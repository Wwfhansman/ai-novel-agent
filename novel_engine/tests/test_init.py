import tempfile
import unittest
from pathlib import Path

from novel_engine.events import load_project_events
from novel_engine.migrate import seed_bootstrap
from novel_engine.yamlio import dump_yaml


class SeedBootstrapTest(unittest.TestCase):
    def _project_with_entities(self, tmp: str) -> Path:
        proj = Path(tmp) / "new-novel"
        dump_yaml(proj / "entities" / "characters.yml", {"characters": [
            {"id": "char_hero", "name": "阿岩", "role": "protagonist", "current_goal": "活下去"},
        ]})
        dump_yaml(proj / "ledgers" / "narrative_debts.yml", {"debts": [
            {"id": "debt_001", "created_in": "bootstrap", "description": "阿岩为何被流放", "urgency": "high"},
        ]})
        dump_yaml(proj / "ledgers" / "foreshadowing.yml", {"foreshadowing": [
            {"id": "f_001", "created_in": "bootstrap", "content": "袖中半枚旧印"},
        ]})
        return proj

    def test_seeds_bootstrap_from_initial_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = self._project_with_entities(tmp)
            path, count = seed_bootstrap(proj)
            self.assertTrue(path.exists())
            self.assertGreaterEqual(count, 3)  # character + debt + foreshadow
            events, errors = load_project_events(proj)
            self.assertEqual(errors, [])
            kinds = {e.kind for e in events}
            self.assertIn("character_introduced", kinds)
            self.assertIn("debt_opened", kinds)
            self.assertIn("foreshadow_planted", kinds)

    def test_empty_project_yields_zero_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "empty"
            proj.mkdir(parents=True)
            _path, count = seed_bootstrap(proj)
            self.assertEqual(count, 0)

    def test_refuses_to_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = self._project_with_entities(tmp)
            seed_bootstrap(proj)
            with self.assertRaises(FileExistsError):
                seed_bootstrap(proj)
            seed_bootstrap(proj, force=True)  # ok with force


if __name__ == "__main__":
    unittest.main()
