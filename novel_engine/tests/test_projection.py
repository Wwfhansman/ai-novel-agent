import unittest
from pathlib import Path

from novel_engine.events import load_project_events
from novel_engine.projection import project

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "good_project"


class ProjectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        events, errors = load_project_events(FIXTURE)
        assert not errors, f"fixture should load cleanly: {errors}"
        cls.events = events
        cls.state = project(events)

    def test_character_fields_fold_forward(self):
        char_a = self.state.characters["char_a"]
        self.assertEqual(char_a["current_goal"], "查清自己的来历")  # set in ch002 overrides ch001
        self.assertEqual(char_a["current_stance"], "不再躲避乙")
        self.assertEqual(char_a["role"], "protagonist")
        self.assertEqual(char_a["last_updated"], "ch002")

    def test_change_history_accumulates(self):
        history = self.state.characters["char_a"]["change_history"]
        self.assertEqual([h["chapter"] for h in history], ["ch002"])
        self.assertEqual(self.state.characters["char_b"]["change_history"][0]["chapter"], "ch003")

    def test_relationship_is_symmetric(self):
        self.assertEqual(self.state.characters["char_a"]["relationships"]["char_b"], "敌对")
        self.assertEqual(self.state.characters["char_b"]["relationships"]["char_a"], "敌对")

    def test_debt_lifecycle(self):
        debt = self.state.debts["debt_001"]
        self.assertEqual(debt["status"], "paid")
        self.assertEqual([h["action"] for h in debt["history"]], ["opened", "advanced", "paid"])
        self.assertEqual(debt["opened_in"], "ch001")

    def test_foreshadow_lifecycle(self):
        self.assertEqual(self.state.foreshadowing["f_001"]["status"], "paid")

    def test_knowledge_visibility(self):
        secret = self.state.knowledge["k_secret"]
        self.assertEqual(secret["reader"], "hinted")
        self.assertEqual(secret["char_a"], "suspects")

    def test_note_attaches_to_scope(self):
        notes = self.state.characters["char_a"].get("notes", [])
        self.assertEqual(len(notes), 1)
        self.assertIn("松动", notes[0]["text"])

    def test_projection_is_deterministic(self):
        again = project(self.events)
        self.assertEqual(again.to_dict(), self.state.to_dict())


if __name__ == "__main__":
    unittest.main()
