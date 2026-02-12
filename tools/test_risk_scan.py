import unittest

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


if __name__ == "__main__":
    unittest.main()
