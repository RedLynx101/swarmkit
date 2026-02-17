import unittest

import task_broker


class TestTaskBroker(unittest.TestCase):
    def test_parse_issue_ref_supports_multiple_formats(self):
        repo, number = task_broker.parse_issue_ref("8", None)
        self.assertIsNone(repo)
        self.assertEqual(number, 8)

        repo, number = task_broker.parse_issue_ref("#9", "acme/swarmkit")
        self.assertEqual(repo, "acme/swarmkit")
        self.assertEqual(number, 9)

        repo, number = task_broker.parse_issue_ref(
            "https://github.com/RedLynx101/swarmkit/issues/10", None
        )
        self.assertEqual(repo, "RedLynx101/swarmkit")
        self.assertEqual(number, 10)

    def test_parse_issue_ref_rejects_invalid_values(self):
        with self.assertRaises(RuntimeError):
            task_broker.parse_issue_ref("", None)

        with self.assertRaises(RuntimeError):
            task_broker.parse_issue_ref("not-an-issue", None)

        with self.assertRaises(RuntimeError):
            task_broker.parse_issue_ref("https://example.com/acme/swarmkit/issues/8", None)

        with self.assertRaises(RuntimeError):
            task_broker.parse_issue_ref(
                "https://github.com/RedLynx101/swarmkit/issues/8", "acme/swarmkit"
            )

    def test_parse_sections_extracts_markdown_headings(self):
        body = """
## Goal
Ship a script.

## Acceptance criteria
- Has tests
- Has docs
""".strip()
        sections = task_broker.parse_sections(body)

        self.assertEqual(sections["goal"], "Ship a script.")
        self.assertIn("- Has tests", sections["acceptance criteria"])

    def test_parse_sections_extracts_informal_template_headings(self):
        body = """
**Goal**
Ship a script.

Non-goals:
- Don't ship a daemon.

**Acceptance criteria:**
- Has tests
""".strip()
        sections = task_broker.parse_sections(body)

        self.assertEqual(sections["goal"], "Ship a script.")
        self.assertIn("- Don't ship a daemon.", sections["non-goals"])
        self.assertIn("- Has tests", sections["acceptance criteria"])

    def test_parse_sections_ignores_non_required_plain_colon_lines(self):
        body = """
## Goal
Implement parser

Note:
This should stay inside the goal section.
""".strip()
        sections = task_broker.parse_sections(body)

        self.assertIn("Note:", sections["goal"])

    def test_build_brief_fills_missing_sections_with_todo(self):
        issue = {
            "number": 8,
            "title": "Build task-broker script",
            "html_url": "https://github.com/acme/swarmkit/issues/8",
            "labels": [{"name": "P2"}, {"name": "agent-task"}],
            "body": "## Goal\nGenerate brief from issue",
        }

        brief = task_broker.build_brief(issue)

        self.assertIn("# Agent Brief: Issue #8", brief)
        self.assertIn("## Goal\nGenerate brief from issue", brief)
        self.assertIn("## Non-goals\n- TODO", brief)
        self.assertIn("Labels: P2, agent-task", brief)
        self.assertIn("Missing required sections in source issue:", brief)

    def test_missing_required_sections_returns_headings(self):
        issue = {
            "body": "## Goal\nImplement parser\n\n## How to verify\nRun tests"
        }
        missing = task_broker.missing_required_sections(issue)
        self.assertIn("Non-goals", missing)
        self.assertIn("Acceptance criteria", missing)
        self.assertNotIn("Goal", missing)
        self.assertNotIn("How to verify", missing)


if __name__ == "__main__":
    unittest.main()
