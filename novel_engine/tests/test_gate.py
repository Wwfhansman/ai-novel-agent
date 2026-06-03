import shutil
import tempfile
import unittest
from pathlib import Path

from novel_engine.events import load_project_events
from novel_engine.gate import run_gate
from novel_engine.materialize import write_materialized
from novel_engine.migrate import migrate
from novel_engine.projection import project
from novel_engine.yamlio import load_yaml

REPO = Path(__file__).resolve().parents[2]
EXAMPLE = REPO / "projects" / "example-project"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "good_project"


class GateTest(unittest.TestCase):
    def test_clean_fixture_passes(self):
        result = run_gate(FIXTURE)
        self.assertTrue(result.ok, result.errors)
        self.assertEqual(result.sections["event_count"], 15)

    def test_broken_events_fail_the_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "p"
            (proj / "events").mkdir(parents=True)
            # debt_paid for a debt that was never opened -> integrity error.
            (proj / "events" / "ch001.yml").write_text(
                "chapter: ch001\nevents:\n  - {kind: debt_paid, id: ghost}\n", encoding="utf-8"
            )
            result = run_gate(proj)
            self.assertFalse(result.ok)
            self.assertTrue(any("UNKNOWN_DEBT" in e for e in result.errors))

    def test_schema_violation_fails_the_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "p"
            (proj / "events").mkdir(parents=True)
            (proj / "events" / "ch001.yml").write_text(
                "chapter: ch001\nevents:\n  - {kind: fact_added}\n", encoding="utf-8"  # missing text
            )
            result = run_gate(proj)
            self.assertFalse(result.ok)
            self.assertTrue(any("EVENT_SCHEMA" in e for e in result.errors))


@unittest.skipUnless(EXAMPLE.exists(), "example-project not present")
class CommitRoundTripTest(unittest.TestCase):
    def test_migrate_then_gate_then_materialize_in_place(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "example-project"
            shutil.copytree(EXAMPLE, proj)
            shutil.rmtree(proj / "events", ignore_errors=True)

            migrate(proj)
            result = run_gate(proj)
            self.assertTrue(result.ok, result.errors)

            # commit == gate passes -> materialize in place; entities become derived.
            events, _ = load_project_events(proj)
            write_materialized(project(events), proj, in_place=True)

            derived = load_yaml(proj / "ledgers" / "foreshadowing.yml")
            fore_ids = {f["id"] for f in derived["foreshadowing"]}
            self.assertIn("f_002", fore_ids)  # the previously-dropped foreshadow is now present


if __name__ == "__main__":
    unittest.main()
