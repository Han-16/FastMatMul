"""Small orchestration checks; no Go binary or performance workload is executed."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import run_epyc_zkmap as helper

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent / "tmp/zkmap/fastmatmul-implementation-checkout"


@unittest.skipUnless((ROOT / "scripts/comparison/run_zkmap.py").exists(), "local pinned checkout required")
class EPYCSetupTests(unittest.TestCase):
    def test_square_profile_is_plan_only_and_exact_grid(self):
        argv = ["runner", "--checkout", str(ROOT), "--profile", "square", "--plan"]
        out = io.StringIO()
        with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(out), mock.patch.object(helper, "measured_call") as call:
            self.assertEqual(helper.main(), 0)
        call.assert_not_called()
        plan = json.loads(out.getvalue())
        self.assertEqual([x["n"] for x in plan["commands"]], [128, 256, 512, 1024, 2048])
        self.assertEqual(len(plan["commands"]), 5)
        self.assertFalse(plan["comparison_eligible_as_published_zkmap"])

    def test_failure_preflight_stops_all_large_conditions(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "zkmap"
            binary.touch()
            output = Path(tmp) / "results"
            argv = ["runner", "--checkout", str(ROOT), "--profile", "square", "--execute",
                    "--binary", str(binary), "--output", str(output)]
            with mock.patch.object(sys, "argv", argv), mock.patch("os.cpu_count", return_value=32), mock.patch.object(helper, "measured_call", return_value=2) as call:
                self.assertEqual(helper.main(), 2)
            self.assertEqual(call.call_count, 1)
            state = json.loads((output / "progress.json").read_text())
            self.assertEqual(state["run_state"], "failed")
            self.assertEqual(state["commands"], [])

    def test_failure_first_condition_stops_remaining_grid(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "zkmap"
            binary.touch()
            output = Path(tmp) / "results"
            argv = ["runner", "--checkout", str(ROOT), "--profile", "square", "--execute",
                    "--binary", str(binary), "--output", str(output)]
            with mock.patch.object(sys, "argv", argv), mock.patch("os.cpu_count", return_value=32), mock.patch.object(helper, "measured_call", side_effect=[0, 2]) as call:
                self.assertEqual(helper.main(), 1)
            self.assertEqual(call.call_count, 2)
            state = json.loads((output / "progress.json").read_text())
            self.assertEqual(state["run_state"], "failed")
            self.assertEqual(len(state["commands"]), 1)

    def test_missing_records_and_timeout_are_failures(self):
        runner = helper.load_runner(ROOT, HERE / "zkmap_10reps.json")
        command = ["not-executed", "-K", "2", "-repetitions", "10"]
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "missing"
            directory.mkdir()
            with mock.patch.object(helper.subprocess, "run", return_value=subprocess.CompletedProcess(command, 0)):
                self.assertEqual(helper.measured_call(runner, command, directory, 60), 1)
            self.assertTrue((directory / "validation_error.txt").exists())
            directory = Path(tmp) / "timeout"
            directory.mkdir()
            with mock.patch.object(helper.subprocess, "run", side_effect=subprocess.TimeoutExpired(command, 60)):
                self.assertEqual(helper.measured_call(runner, command, directory, 60), 124)


if __name__ == "__main__":
    unittest.main()
