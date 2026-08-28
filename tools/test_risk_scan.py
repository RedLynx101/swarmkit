import unittest

import risk_scan


class TestRiskScan(unittest.TestCase):
    def test_classify_flags_expected_categories(self):
        paths = [
            ".github/workflows/ci.yml",
            "tools/receipt_lint.py",
            "requirements.txt",
            "scripts/bootstrap.sh",
            "docs/ROADMAP.md",
        ]
        matched = risk_scan.classify(paths)

        self.assertIn("workflows", matched)
        self.assertIn("tooling", matched)
        self.assertIn("dependency-manifests", matched)
        self.assertIn("runtime-scripts", matched)
        self.assertNotIn("docs", matched)

    def test_classify_handles_empty(self):
        self.assertEqual(risk_scan.classify([]), {})


if __name__ == "__main__":
    unittest.main()
