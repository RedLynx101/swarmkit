from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import security_checklist


class SecurityChecklistTests(unittest.TestCase):
    def test_required_files_report_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            missing = security_checklist.check_required_files(root)
            self.assertIn("SECURITY.md", missing)

    def test_permissions_check_detects_missing_block(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (workflows / "ci.yml").write_text("name: CI\non: push\n", encoding="utf-8")

            missing = security_checklist.find_workflows_missing_permissions(root)
            self.assertEqual(missing, [".github/workflows/ci.yml"])

    def test_permissions_check_passes_with_block(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workflows = root / ".github" / "workflows"
            workflows.mkdir(parents=True)
            (workflows / "ci.yml").write_text(
                "name: CI\npermissions:\n  contents: read\n", encoding="utf-8"
            )

            missing = security_checklist.find_workflows_missing_permissions(root)
            self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
