import unittest

import task_broker


class TestTaskBroker(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
