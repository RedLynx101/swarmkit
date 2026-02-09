import unittest

from tools.task_broker import parse_issue_json, parse_issue_url, render_markdown


class TaskBrokerTests(unittest.TestCase):
    def test_parse_issue_url(self):
        repo, issue_number = parse_issue_url("https://github.com/RedLynx101/swarmkit/issues/8")
        self.assertEqual(repo, "RedLynx101/swarmkit")
        self.assertEqual(issue_number, 8)

    def test_parse_issue_json_accepts_label_dicts(self):
        issue = parse_issue_json(
            {
                "number": 42,
                "title": "Add broker",
                "body": "",
                "url": "https://example.com/42",
                "labels": [{"name": "P1"}, {"name": "agent-task"}],
            }
        )
        self.assertEqual(issue.labels, ["P1", "agent-task"])

    def test_render_markdown_maps_sections_when_present(self):
        issue = parse_issue_json(
            {
                "number": 8,
                "title": "Build task broker",
                "body": """
## Goal
- Turn issue into brief

## Acceptance Criteria
- [ ] Produces markdown

## How to verify
- Run on issue #8
""",
                "url": "https://example.com/8",
                "labels": ["P2"],
            }
        )

        output = render_markdown(issue)
        self.assertIn("# Agent Brief: #8 Build task broker", output)
        self.assertIn("- Turn issue into brief", output)
        self.assertIn("- [ ] Produces markdown", output)
        self.assertIn("- Run on issue #8", output)

    def test_render_markdown_uses_defaults_when_sections_missing(self):
        issue = parse_issue_json(
            {
                "number": 1,
                "title": "Minimal",
                "body": "No structured sections",
                "url": "https://example.com/1",
                "labels": [],
            }
        )

        output = render_markdown(issue)
        self.assertIn("Deliver the requested issue outcome", output)
        self.assertIn("Avoid unrelated refactors", output)


if __name__ == "__main__":
    unittest.main()
