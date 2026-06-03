import shutil
import tempfile
import unittest
from pathlib import Path

from novel_engine.kit import build_kit, write_kit
from novel_engine.scene import exemplars

REPO = Path(__file__).resolve().parents[2]
EXAMPLE = REPO / "projects" / "example-project"


@unittest.skipUnless(EXAMPLE.exists(), "example-project not present")
class KitTest(unittest.TestCase):
    def test_build_kit_has_all_pieces(self):
        files, _notes = build_kit(EXAMPLE, "ch002")
        self.assertEqual(
            set(files),
            {"scene_prompts.md", "stitch_prompt.md", "events.template.yml", "PRODUCE.md"},
        )

    def test_scene_prompts_render_entering_state_and_scenes(self):
        files, _ = build_kit(EXAMPLE, "ch002")
        prompts = files["scene_prompts.md"]
        self.assertIn("进入本章时的状态", prompts)
        self.assertIn("场景 1", prompts)
        self.assertIn("出口", prompts)  # exit_on rendered

    def test_events_template_targets_chapter(self):
        files, _ = build_kit(EXAMPLE, "ch002")
        self.assertIn("chapter: ch002", files["events.template.yml"])
        self.assertIn("kind:", files["events.template.yml"])

    def test_produce_lists_check_and_commit(self):
        files, _ = build_kit(EXAMPLE, "ch002")
        self.assertIn("novel_engine check", files["PRODUCE.md"])
        self.assertIn("novel_engine commit", files["PRODUCE.md"])

    def test_write_kit_creates_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "ep"
            shutil.copytree(EXAMPLE, proj)
            out_dir, written, _notes = write_kit(proj, "ch002")
            self.assertTrue((out_dir / "PRODUCE.md").exists())
            self.assertEqual(len(written), 4)


class ExemplarScaffoldTest(unittest.TestCase):
    def test_scaffold_creates_then_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            (proj / "style").mkdir(parents=True)
            (proj / "style" / "samples.md").write_text("> 一段能代表语感的正文。\n", encoding="utf-8")
            path, created = exemplars.scaffold(proj)
            self.assertTrue(created)
            self.assertTrue(path.exists())
            _path, created_again = exemplars.scaffold(proj)
            self.assertFalse(created_again)


if __name__ == "__main__":
    unittest.main()
