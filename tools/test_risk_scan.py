import re
import unittest

from tools.risk_scan import CONTENT_PATTERNS


class RiskScanPatternTests(unittest.TestCase):
    def _matches_kind(self, line: str):
        for kind, pattern in CONTENT_PATTERNS:
            if pattern.search(line):
                return kind
        return None

    def test_detects_network_calls(self):
        self.assertEqual(self._matches_kind("requests.get('https://example.com')"), "network-call")
        self.assertEqual(self._matches_kind("curl https://example.com"), "network-call")

    def test_detects_process_execution(self):
        self.assertEqual(self._matches_kind("subprocess.run(['ls'])"), "process-exec")
        self.assertEqual(self._matches_kind("os.system('rm -rf /')"), "process-exec")

    def test_detects_shell_injections(self):
        self.assertEqual(self._matches_kind("bash -c 'echo hi'"), "shell-script")
        self.assertEqual(self._matches_kind("powershell.exe -Command Get-ChildItem"), "shell-script")

    def test_ignores_benign_lines(self):
        self.assertIsNone(self._matches_kind("print('hello world')"))
        self.assertIsNone(self._matches_kind("def parse_config(path):"))


if __name__ == "__main__":
    unittest.main()
