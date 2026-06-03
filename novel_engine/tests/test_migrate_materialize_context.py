import shutil
import tempfile
import unittest
from pathlib import Path

from novel_engine.context import entering_state
from novel_engine.events import load_project_events
from novel_engine.integrity import check_integrity
from novel_engine.materialize import materialize
from novel_engine.migrate import migrate
from novel_engine.projection import project

REPO = Path(__file__).resolve().parents[2]
EXAMPLE = REPO / "projects" / "example-project"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "good_project"


class ContextTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events, errors = load_project_events(FIXTURE)
        assert not errors, errors

    def test_entering_ch002_sees_ch001_state(self):
        pack = entering_state(self.events, "ch002")
        # char_a goal is still the ch001 value (ch002 change not yet applied).
        self.assertEqual(pack["characters"]["char_a"]["current_goal"], "在城里活下去")
        debt_ids = {d["id"] for d in pack["open_debts"]}
        self.assertIn("debt_001", debt_ids)
        self.assertTrue(any(f["id"] == "f_001" for f in pack["live_foreshadowing"]))

    def test_entering_ch003_sees_ch002_changes(self):
        pack = entering_state(self.events, "ch003")
        self.assertEqual(pack["characters"]["char_a"]["current_goal"], "查清自己的来历")

    def test_entering_after_payoff_drops_resolved_debt(self):
        # Entering ch004: debt_001 was paid in ch003, so it should not be open.
        pack = entering_state(self.events, "ch004")
        self.assertNotIn("debt_001", {d["id"] for d in pack["open_debts"]})


class MaterializeTest(unittest.TestCase):
    def test_materialize_shapes(self):
        events, _ = load_project_events(FIXTURE)
        files = materialize(project(events))
        self.assertEqual(
            set(files),
            {"entities/characters.yml", "ledgers/narrative_debts.yml",
             "ledgers/foreshadowing.yml", "ledgers/knowledge_state.yml"},
        )
        char_ids = {c["id"] for c in files["entities/characters.yml"]["characters"]}
        self.assertEqual(char_ids, {"char_a", "char_b"})
        debt = files["ledgers/narrative_debts.yml"]["debts"][0]
        self.assertEqual(debt["status"], "paid")


@unittest.skipUnless(EXAMPLE.exists(), "example-project not present")
class MigrateRoundTripTest(unittest.TestCase):
    def test_migrate_then_validate_project_materialize(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "example-project"
            shutil.copytree(EXAMPLE, proj)
            shutil.rmtree(proj / "events", ignore_errors=True)  # migrate a clean legacy snapshot

            events_dir, written = migrate(proj)
            self.assertIn("bootstrap.yml", written)
            self.assertIn("ch001.yml", written)

            # The migrated log validates: schema-clean and integrity-clean
            # (bootstrap introduces every character before any change).
            events, load_errors = load_project_events(proj)
            self.assertEqual(load_errors, [])
            int_errors, _warnings = check_integrity(events)
            self.assertEqual(int_errors, [])

            # The drift the shadow tool found (f_002 planted but never in the
            # ledger) is gone once foreshadowing is *derived*: materialized
            # state contains f_002.
            files = materialize(project(events))
            fore_ids = {f["id"] for f in files["ledgers/foreshadowing.yml"]["foreshadowing"]}
            self.assertIn("f_001", fore_ids)
            self.assertIn("f_002", fore_ids)

    def test_migrate_refuses_to_clobber(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "example-project"
            shutil.copytree(EXAMPLE, proj)
            shutil.rmtree(proj / "events", ignore_errors=True)
            migrate(proj)
            with self.assertRaises(FileExistsError):
                migrate(proj)
            # force overwrites
            migrate(proj, force=True)


if __name__ == "__main__":
    unittest.main()
