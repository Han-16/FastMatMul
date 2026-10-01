"""Preparation tests only: plans and synthetic records, no Go/server workload."""
import contextlib
from copy import deepcopy
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

import epyc_batch_tools as batch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent / "tmp/zkmap/fastmatmul-implementation-checkout"


class BatchSetupTests(unittest.TestCase):
    @unittest.skipUnless((ROOT / "scripts/comparison/run.py").exists(), "pinned local checkout required")
    def test_actual_shell_plan_does_not_execute_go_or_create_results(self):
        before = set((ROOT / "benchmark/comparison").glob("vm_batch_10reps_*"))
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "go-called"
            go = Path(tmp) / "go"
            go.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 73\n")
            go.chmod(0o755)
            env = {**os.environ, "PATH": tmp + os.pathsep + os.environ["PATH"]}
            p = subprocess.run(["bash", str(HERE / "run_epyc_batch_10reps.sh"),
                                "--plan", "--checkout", str(ROOT)], env=env, text=True, capture_output=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("총 결과 200건", p.stdout)
            self.assertFalse(marker.exists())
        self.assertEqual(before, set((ROOT / "benchmark/comparison").glob("vm_batch_10reps_*")))

    @unittest.skipUnless((ROOT / "scripts/comparison/run.py").exists(), "pinned local checkout required")
    def test_plan_rejects_missing_batch_and_square_or_different_parameters(self):
        with contextlib.redirect_stdout(io.StringIO()):
            plan = batch.make_plan(ROOT)
        missing = deepcopy(plan)
        missing["commands"].pop()
        with self.assertRaises(ValueError):
            batch.validate_plan(missing)
        square = deepcopy(plan)
        square["commands"][0][0] = "<binary-dir>/lamp"
        with self.assertRaises(ValueError):
            batch.validate_plan(square)
        wrong_threads = deepcopy(plan)
        c = wrong_threads["commands"][0]
        c[c.index("-threads") + 1] = "16"
        with self.assertRaises(ValueError):
            batch.validate_plan(wrong_threads)

    def fixture(self, output):
        output.mkdir()
        source = {"head": batch.HEAD, "source_tree_sha256": "synthetic-fixture"}
        commands = []
        for scheme in sorted(batch.SCHEMES):
            for q in range(1, 11):
                is_lamp = scheme == "lamp"
                for _ in range(10 if is_lamp else 1):
                    count = 1 if is_lamp else 10
                    name = f"run_{len(commands)+1:02d}"
                    run = output / name
                    run.mkdir()
                    row = {"scheme": scheme, "batch_q": q, "verification_succeeded": True,
                           "protocol_path": "batch", "source": source}
                    (run / "lamp_comparison.jsonl").write_text((json.dumps(row) + "\n") * count)
                    commands.append({"argv": ["lamp_batch" if is_lamp else "zkmatrix", "-batch", str(q)],
                                     "stdout": f"/server/results/{name}/stdout.txt", "status": "completed",
                                     "exit_status": 0, "verified_record_count": count,
                                     "expected_verified_record_count": count})
        manifest = {"config_name": batch.PROFILE, "completion_status": "complete", "run_state": "finished",
                    "source": source, "commands": commands, "expected_command_count": 110}
        (output / "manifest.json").write_text(json.dumps(manifest))
        return manifest

    def test_downloaded_paths_validate_200_records_and_reject_missing_or_unverified(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "batch"
            self.fixture(output)
            with contextlib.redirect_stdout(io.StringIO()):
                batch.check_results(output)
            raw = output / "run_01/lamp_comparison.jsonl"
            original = raw.read_text()
            raw.write_text("\n".join(original.splitlines()[1:]) + "\n")
            with self.assertRaisesRegex(ValueError, "raw record count"):
                batch.check_results(output)
            rows = [json.loads(line) for line in original.splitlines()]
            rows[0]["verification_succeeded"] = False
            raw.write_text("".join(json.dumps(row) + "\n" for row in rows))
            with self.assertRaisesRegex(ValueError, "unverified"):
                batch.check_results(output)

    def test_incomplete_manifest_cannot_be_reported_as_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "batch"
            manifest = self.fixture(output)
            manifest["completion_status"] = "incomplete"
            (output / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "incomplete"):
                batch.check_results(output)

    def test_runner_failure_is_returned_and_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "scripts/comparison/run.py"
            script.parent.mkdir(parents=True)
            script.write_text("import sys\nprint('fixture failure', file=sys.stderr)\nsys.exit(7)\n")
            output = root / "batch"
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(batch.run_measurement(root, output), 7)
            self.assertIn("fixture failure", (root / "batch-runner.stderr.log").read_text())
            output.mkdir()
            sentinel = output / "keep.txt"
            sentinel.write_text("previous data")
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                batch.run_measurement(root, output)
            self.assertEqual(sentinel.read_text(), "previous data")

    def test_detected_failure_stops_remaining_measurements(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "batch"
            process = mock.Mock()
            process.wait.side_effect = subprocess.TimeoutExpired("runner", 60)
            failed = {"commands": [{"status": "postprocessing_failed"}]}
            with mock.patch.object(batch.subprocess, "Popen", return_value=process), \
                 mock.patch.object(batch, "show_progress", return_value=failed), \
                 mock.patch.object(batch, "stop_measurement") as stop, \
                 contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(batch.run_measurement(root, output), 1)
            stop.assert_called_once_with(process)


if __name__ == "__main__":
    unittest.main()
