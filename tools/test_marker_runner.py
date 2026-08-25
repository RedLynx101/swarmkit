import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import marker_runner


class TestMarkerRunner(unittest.TestCase):
    def test_is_due_when_missing_marker(self):
        due = marker_runner.is_due({}, every_seconds=3600, now=dt.datetime(2026, 2, 19, 21, 0, tzinfo=dt.UTC))
        self.assertTrue(due)

    def test_is_due_false_inside_window(self):
        now = dt.datetime(2026, 2, 19, 21, 0, tzinfo=dt.UTC)
        marker = {"last_run_utc": "2026-02-19T20:30:00Z"}
        due = marker_runner.is_due(marker, every_seconds=3600, now=now)
        self.assertFalse(due)

    def test_is_due_true_after_window(self):
        now = dt.datetime(2026, 2, 19, 21, 0, tzinfo=dt.UTC)
        marker = {"last_run_utc": "2026-02-19T19:30:00Z"}
        due = marker_runner.is_due(marker, every_seconds=3600, now=now)
        self.assertTrue(due)

    def test_write_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state" / "x-last-run.json"
            now = dt.datetime(2026, 2, 19, 21, 0, tzinfo=dt.UTC)
            marker_runner.write_marker(path, now, ["python3", "script.py"])

            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["last_run_utc"], "2026-02-19T21:00:00Z")
            self.assertEqual(payload["last_command"], ["python3", "script.py"])
            self.assertEqual(payload["version"], 1)

    def test_main_skips_when_not_due(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "run.json"
            marker.write_text('{"last_run_utc":"2026-02-19T20:45:00Z"}', encoding="utf-8")

            with mock.patch("marker_runner.utc_now", return_value=dt.datetime(2026, 2, 19, 21, 0, tzinfo=dt.UTC)):
                with mock.patch("sys.argv", ["marker_runner.py", "--marker", str(marker), "--every-hours", "1", "--", "echo", "hi"]):
                    rc = marker_runner.main()

            self.assertEqual(rc, 0)

    def test_main_runs_and_updates_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "run.json"
            with mock.patch("marker_runner.utc_now", return_value=dt.datetime(2026, 2, 19, 21, 0, tzinfo=dt.UTC)):
                with mock.patch("marker_runner.run_command", return_value=0) as run_cmd:
                    with mock.patch(
                        "sys.argv",
                        ["marker_runner.py", "--marker", str(marker), "--every-hours", "1", "--", "python3", "-V"],
                    ):
                        rc = marker_runner.main()

            self.assertEqual(rc, 0)
            run_cmd.assert_called_once_with(["python3", "-V"])
            payload = json.loads(marker.read_text(encoding="utf-8"))
            self.assertEqual(payload["last_run_utc"], "2026-02-19T21:00:00Z")


if __name__ == "__main__":
    unittest.main()
