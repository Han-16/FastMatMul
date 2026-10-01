#!/usr/bin/env python3
"""Batch-only plan checks, progress display and complete-grid validation."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

PROFILE = "server_batch_q1_q10_10reps"
HEAD = "b34d2287c30730a3990d92630185a0a792a2897f"
SCHEMES = {"lamp", "independent_zkmatrix_optimized_bn254"}


def option(command, flag):
    return command[command.index(flag) + 1]


def validate_plan(plan):
    if plan.get("mode") != "plan_only" or plan.get("config") != PROFILE:
        raise ValueError("unexpected experiment plan")
    commands = plan["commands"]
    expected = Counter({("zkmatrix", q): 1 for q in range(1, 11)})
    expected.update({("lamp_batch", q): 10 for q in range(1, 11)})
    actual = Counter()
    for command in commands:
        name = Path(command[0]).name
        if name not in {"zkmatrix", "lamp_batch"} or option(command, "-K") != "7":
            raise ValueError("plan contains a different scheme or matrix size")
        actual[(name, int(option(command, "-batch")))] += 1
        if name == "zkmatrix":
            if option(command, "-repetitions") != "10" or option(command, "-threads") != "32" or option(command, "-variant") != "accelerated":
                raise ValueError("unexpected zkMatrix parameters")
        elif option(command, "-rho") != "1/2" or option(command, "-L") != "309" or "-batch-range=false" not in command:
            raise ValueError("unexpected LAMP parameters")
    if actual != expected or len(commands) != 110 or plan.get("expected_commands") != 110:
        raise ValueError("batch plan does not contain ten repetitions per scheme and batch size")


def make_plan(root, save=None):
    cfg = json.loads((root / "scripts/comparison/configs.json").read_text())[PROFILE]
    if (cfg["log_k"], cfg["repetitions"], cfg["threads"], cfg["rho"], cfg["queries"]) != (7, 10, 32, "1/2", 309):
        raise ValueError("batch configuration differs from the Section 7 profile")
    if cfg.get("include_square") is not False or "log_k_range" in cfg:
        raise ValueError("batch-only profile unexpectedly includes a size sweep")
    plan = json.loads(subprocess.check_output([
        sys.executable, str(root / "scripts/comparison/run.py"),
        "--config", PROFILE, "--scheme", "both", "--plan"
    ], cwd=root, text=True))
    validate_plan(plan)
    if save:
        save.write_text(json.dumps(plan, indent=2) + "\n")
    print("배치 전용 | LAMP·zkMatrix | 128×128 | 배치 1~10 | 각각 10회 | 32 threads", flush=True)
    print("LAMP: rho=1/2, queries=309 | 총 결과 200건", flush=True)
    return plan


def show_progress(output):
    path = output / "manifest.json"
    if not path.exists():
        print("측정 실행 준비 중", flush=True)
        return
    manifest = json.loads(path.read_text())
    commands = manifest.get("commands", [])
    done = sum(c.get("status") == "completed" and c.get("verified_record_count") == c.get("expected_verified_record_count") for c in commands)
    records = sum(c.get("verified_record_count", 0) for c in commands if c.get("status") == "completed")
    elapsed = (manifest.get("finished_unix", time.time()) - manifest["started_unix"]) / 60
    message = f"경과 {elapsed:.1f}분 | 완료 명령 {done}/110 | 검증 성공 결과 {records}/200"
    if manifest.get("run_state") == "building":
        message += " | 컴파일: " + manifest.get("active_build", "")
    elif manifest.get("run_state") == "running_command" and commands:
        c = commands[-1]
        message += f" | 실행 중: {Path(c['argv'][0]).name}, 배치 {option(c['argv'], '-batch')}"
    print(message, flush=True)
    return manifest


def stop_measurement(process):
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGINT)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()


def run_measurement(root, output):
    if output.exists():
        raise ValueError(f"refusing to overwrite: {output}")
    stdout_path = output.parent / "batch-runner.stdout.log"
    stderr_path = output.parent / "batch-runner.stderr.log"
    command = [sys.executable, str(root / "scripts/comparison/run.py"),
               "--config", PROFILE, "--scheme", "both", "--output", str(output)]
    with stdout_path.open("w") as stdout, stderr_path.open("w") as stderr:
        process = subprocess.Popen(command, cwd=root, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            while True:
                try:
                    code = process.wait(timeout=60)
                    break
                except subprocess.TimeoutExpired:
                    manifest = show_progress(output)
                    if manifest and (manifest.get("build_failed") or any(c.get("status") in {"failed", "timeout", "postprocessing_failed", "interrupted"} for c in manifest.get("commands", []))):
                        print("실패한 실행을 발견해 남은 실험을 중단합니다.", file=sys.stderr)
                        stop_measurement(process)
                        return 1
        except KeyboardInterrupt:
            stop_measurement(process)
            return 130
    show_progress(output)
    if code:
        print(f"runner 중단: exit={code}; 로그: {stderr_path}", file=sys.stderr)
        print(stderr_path.read_text()[-4000:], file=sys.stderr)
    return code


def check_results(output):
    m = json.loads((output / "manifest.json").read_text())
    if m.get("config_name") != PROFILE or m.get("completion_status") != "complete" or m.get("run_state") != "finished":
        raise ValueError("batch experiment is incomplete")
    if m.get("source", {}).get("head") != HEAD:
        raise ValueError("unexpected measured source commit")
    commands = m["commands"]
    if len(commands) != 110 or m.get("expected_command_count") != 110:
        raise ValueError("unexpected command count")
    groups = Counter()
    for c in commands:
        if c.get("status") != "completed" or c.get("exit_status") != 0 or c.get("verified_record_count") != c.get("expected_verified_record_count"):
            raise ValueError("failed command or missing verified records")
        # Relative run directory also works after downloading from the VM.
        raw = output / Path(c["stdout"]).parent.name / "lamp_comparison.jsonl"
        rows = [json.loads(line) for line in raw.read_text().splitlines() if line.strip()]
        if len(rows) != c["expected_verified_record_count"]:
            raise ValueError("raw record count differs from the manifest")
        for r in rows:
            if r.get("verification_succeeded") is not True or r.get("protocol_path") != "batch" or r.get("scheme") not in SCHEMES:
                raise ValueError("unverified or non-batch record")
            if r.get("batch_q") != int(option(c["argv"], "-batch")):
                raise ValueError("record batch size differs from its command")
            if r.get("source", {}).get("source_tree_sha256") != m["source"]["source_tree_sha256"] or r.get("source", {}).get("head") != HEAD:
                raise ValueError("record source differs from the manifest")
            groups[(r["scheme"], r["batch_q"])] += 1
    expected = Counter({(scheme, q): 10 for scheme in SCHEMES for q in range(1, 11)})
    if groups != expected:
        raise ValueError("expected 200 records: ten per scheme and batch size")
    print("결과 확인 완료: LAMP 100건 + zkMatrix 100건, 모든 배치 설정 각각 10회", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("plan", "run", "check", "status"))
    parser.add_argument("--checkout", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--save", type=Path)
    args = parser.parse_args()
    if args.mode == "plan":
        make_plan(args.checkout.resolve(), args.save)
    elif args.mode == "run":
        return run_measurement(args.checkout.resolve(), args.output.resolve())
    elif args.mode == "check":
        check_results(args.output.resolve())
    else:
        roots = sorted((args.checkout / "benchmark/comparison").glob("vm_batch_10reps_k7_q1_q10_*"))
        if not roots:
            raise ValueError("배치 10회 실행 폴더가 아직 없습니다.")
        print("결과 폴더:", roots[-1])
        state = roots[-1] / "run-state.json"
        if state.exists():
            print("전체 상태:", json.loads(state.read_text())["state"])
        show_progress(roots[-1] / "batch")
    return 0


def interrupt_handler(signum, frame):
    raise KeyboardInterrupt


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, interrupt_handler)
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as e:
        raise SystemExit(str(e))
