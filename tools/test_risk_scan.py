import unittest
from unittest.mock import patch

import risk_scan


class RiskScanTests(unittest.TestCase):
    def test_scan_paths_flags_workflows(self):
        findings = risk_scan.scan_paths([".github/workflows/ci.yml"])
        self.assertTrue(any(f.reason == "CI/workflow pipeline changed" for f in findings))

    def test_scan_paths_flags_dependency_files(self):
        findings = risk_scan.scan_paths(["package-lock.json", "pyproject.toml"])
        reasons = {f.reason for f in findings}
        self.assertIn("Dependency lock/manifest changed", reasons)

    def test_format_finding_includes_line_and_snippet(self):
        finding = risk_scan.Finding(
            file="tools/risk_scan.py",
            line=10,
            severity="high",
            reason="Shell command execution added",
            snippet="subprocess.run(['echo', 'x'])",
        )
        rendered = risk_scan.format_finding(finding)
        self.assertIn("tools/risk_scan.py:10", rendered)
        self.assertIn("Shell command execution added", rendered)
        self.assertIn("subprocess.run", rendered)

    @patch("risk_scan.run_git")
    def test_changed_files_parses_git_output(self, mock_run_git):
        mock_run_git.return_value = "tools/a.py\nREADME.md\n"
        files = risk_scan.changed_files("base", "head")
        self.assertEqual(files, ["tools/a.py", "README.md"])
        mock_run_git.assert_called_once_with(["diff", "--name-only", "base..head"])

    def test_excluded_path_matches_regex(self):
        patterns = [risk_scan.re.compile(r"^tools/test_.*\.py$")]
        self.assertTrue(risk_scan.is_excluded("tools/test_risk_scan.py", patterns))
        self.assertFalse(risk_scan.is_excluded("tools/risk_scan.py", patterns))


if __name__ == "__main__":
    unittest.main()
