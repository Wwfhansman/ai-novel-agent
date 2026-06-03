import json
import shutil
import tempfile
import unittest
from pathlib import Path

from novel_engine.experiment import build_experiment, write_experiment

REPO = Path(__file__).resolve().parents[2]
EXAMPLE = REPO / "projects" / "example-project"


@unittest.skipUnless(EXAMPLE.exists(), "example-project not present")
class ExperimentTest(unittest.TestCase):
    def test_build_contains_all_pieces(self):
        files = build_experiment(EXAMPLE, "ch002")
        self.assertEqual(
            set(files),
            {"entering_state.json", "scene_plan.template.yml", "prompt_A_chapter_level.md",
             "prompt_B_scene_level.md", "evaluate.md", "README.md"},
        )

    def test_entering_state_is_valid_json_and_resolved(self):
        files = build_experiment(EXAMPLE, "ch002")
        es = json.loads(files["entering_state.json"])
        self.assertEqual(es["entering_chapter"], "ch002")
        # ch001 state is resolved: the protagonist and the open debt are present.
        self.assertIn("char_lin_qi", es["characters"])
        self.assertTrue(es["open_debts"])

    def test_prompts_share_the_same_beat(self):
        files = build_experiment(EXAMPLE, "ch002")
        # Fair test: both prompts target the same chapter handoff.
        self.assertIn("ch002", files["prompt_A_chapter_level.md"])
        self.assertIn("ch002", files["prompt_B_scene_level.md"])
        self.assertIn("场景", files["prompt_B_scene_level.md"])
        self.assertNotIn("场景", files["prompt_A_chapter_level.md"].split("梗概")[0][:50])

    def test_write_creates_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "ep"
            shutil.copytree(EXAMPLE, proj)
            out_dir, written = write_experiment(proj, "ch002")
            self.assertTrue((out_dir / "README.md").exists())
            self.assertEqual(len(written), 6)


if __name__ == "__main__":
    unittest.main()
