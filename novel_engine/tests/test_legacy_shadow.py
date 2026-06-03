import unittest
from pathlib import Path

from novel_engine import diff
from novel_engine.legacy import adapt_project
from novel_engine.projection import project

REPO = Path(__file__).resolve().parents[2]
EXAMPLE = REPO / "projects" / "example-project"


@unittest.skipUnless(EXAMPLE.exists(), "example-project not present")
class LegacyShadowTest(unittest.TestCase):
    def test_adapter_emits_typed_events(self):
        events, seeds = adapt_project(EXAMPLE)
        kinds = {e.kind for e in events}
        # ch001 canon_delta has facts, a character change, a debt, foreshadowing.
        self.assertIn("fact_added", kinds)
        self.assertIn("debt_opened", kinds)
        self.assertIn("char_lin_qi", seeds["characters"])

    def test_adapted_events_project_without_crashing(self):
        events, _ = adapt_project(EXAMPLE)
        state = project(events)
        self.assertIn("debt_001", state.debts)

    def test_shadow_report_shape(self):
        report = diff.shadow_report(EXAMPLE)
        self.assertEqual(set(report["summary"]), {"drift", "unmerged", "informational"})
        self.assertGreater(report["event_count"], 0)
        # Report must be renderable.
        self.assertIn("Shadow diff", diff.format_report(report))


if __name__ == "__main__":
    unittest.main()
