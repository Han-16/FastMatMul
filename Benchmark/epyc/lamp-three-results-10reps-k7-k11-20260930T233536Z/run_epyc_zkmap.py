#!/usr/bin/env python3
"""Pinned zkMaP variant runner with a separate profile, progress and record checks.

Imports the repository runner without changing its source or default profiles.
This measures completeness-roots-v1, not a sound implementation of published zkMaP.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def load_runner(checkout, profiles):
    path = checkout / "scripts/comparison/run_zkmap.py"
    spec = importlib.util.spec_from_file_location("epyc_zkmap_runner", path)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.ROOT = checkout
    runner.PROFILE = profiles
    return runner


def save_progress(path, state):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n")
    temporary.replace(path)


def measured_call(runner, command, directory, timeout):
    code = 1
    with (directory / "stdout.txt").open("x") as out, (directory / "stderr.txt").open("x") as err:
        try:
            code = subprocess.run(command, cwd=runner.ROOT, stdout=out, stderr=err,
                                  timeout=timeout, env={**os.environ, "GOMAXPROCS": "32"}).returncode
        except subprocess.TimeoutExpired:
            err.write(f"Timed out after {timeout} seconds\n")
            code = 124
    if code == 0:
        try:
            runner.validate_records(directory / "attempts.jsonl", command)
        except (OSError, ValueError, KeyError, TypeError) as error:
            (directory / "validation_error.txt").write_text(str(error) + "\n")
            code = 1
    return code


def main():
    parser = argparse.ArgumentParser(description=__doc__, add_help=False, allow_abbrev=False)
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--profiles", type=Path, default=Path(__file__).with_name("zkmap_10reps.json"))
    args, remaining = parser.parse_known_args()
    checkout = args.checkout.resolve()
    profiles = args.profiles.resolve()
    config = json.loads(profiles.read_text())
    if (config["square_log_k"] != [7, 8, 9, 10, 11] or config["repetitions"] != 10
            or config["threads"] != 32 or config["variant"] != "completeness-roots-v1"
            or config["batch_log_k"] != 7 or config["batch_q"] != list(range(1, 11))
            or config["security_certified"] is not False):
        parser.error("unexpected profile: require n=128..2048, 10 repetitions, 32 threads and declared variant")
    runner = load_runner(checkout, profiles)
    # Plans never invoke a binary or allocate full-size inputs.
    if "--execute" not in remaining:
        sys.argv = [str(runner.__file__)] + remaining
        return runner.main()
    if "--allow-failed-attempts" in remaining:
        parser.error("failed attempts must not enter this comparison grid")
    if "--output" not in remaining:
        parser.error("--execute requires --output")
    output = Path(remaining[remaining.index("--output") + 1]).resolve()
    if output.exists():
        parser.error("refusing to overwrite an existing results directory")
    stage = remaining[remaining.index("--profile") + 1] if "--profile" in remaining else "both"
    count = {"square": 5, "batch": 10, "both": 15}.get(stage)
    if count is None:
        parser.error("only square or independent batch workloads are supported")
    state = {"variant": config["variant"], "security_certified": False,
             "comparison_eligible_as_published_zkmap": False, "run_state": "preparing",
             "expected_command_count": count, "expected_record_count": count * 10,
             "commands": [], "started_unix": time.time()}

    def monitored(command, directory):
        preflight = directory.name == "preflight"
        entry = {"name": directory.name, "argv": command, "started_unix": time.time()}
        state["active_command"] = entry
        state["run_state"] = "preflight" if preflight else "running_command"
        save_progress(output / "progress.json", state)
        print("zkMaP variant:", directory.name, "시작", flush=True)
        code = measured_call(runner, command, directory, config["timeout_seconds"])
        entry.update(exit_code=code, finished_unix=time.time(), status="completed" if code == 0 else "failed")
        if not preflight:
            state["commands"].append(entry)
        else:
            state["preflight_exit_code"] = code
        state.pop("active_command", None)
        state["run_state"] = "between_commands" if code == 0 else "failed"
        save_progress(output / "progress.json", state)
        # Stop the grid after the first failed full-size condition.
        return 1 if code != 0 and not preflight else code

    runner.call = monitored
    sys.argv = [str(runner.__file__)] + remaining
    try:
        code = runner.main()
        if code == 0 and len(state["commands"]) != count:
            code = 1
        state["run_state"] = "complete" if code == 0 else "failed"
        state["exit_code"] = code
        state["finished_unix"] = time.time()
        if output.exists():
            save_progress(output / "progress.json", state)
        return code
    except BaseException:
        state["run_state"] = "interrupted_or_error"
        if output.exists():
            save_progress(output / "progress.json", state)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
