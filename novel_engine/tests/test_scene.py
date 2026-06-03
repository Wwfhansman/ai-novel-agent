import tempfile
import unittest
from pathlib import Path

from novel_engine.contracts import validate_scene_spec
from novel_engine.scene import exemplars, plan
from novel_engine.scene.packet import build_scene_packets
from novel_engine.yamlio import dump_yaml

REPO = Path(__file__).resolve().parents[2]
EXAMPLE = REPO / "projects" / "example-project"


class ExemplarTest(unittest.TestCase):
    def test_retrieve_by_type_then_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            dump_yaml(proj / "style" / "exemplars.yml", {
                "face_slap": ["打脸范例一", "打脸范例二"],
                "_default": ["通用范例"],
            })
            got = exemplars.retrieve(proj, "face_slap", k=3)
            self.assertIn("打脸范例一", got)
            # fills from _default when the type bucket is small
            self.assertIn("通用范例", got)

    def test_alias_maps_chapter_function(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            dump_yaml(proj / "style" / "exemplars.yml", {"domestic": ["种田范例"]})
            got = exemplars.retrieve(proj, "building / relationship", k=2)
            self.assertIn("种田范例", got)

    def test_no_corpus_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(exemplars.retrieve(Path(tmp), "face_slap"), [])


class PlanTest(unittest.TestCase):
    def test_draft_from_rolling_splits_motion_into_scenes(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            dump_yaml(proj / "planning" / "rolling_plan.yml", {"chapters": [{
                "chapter": "ch004",
                "pressure_curve": {"chapter_internal_motion": "抵达→山门→杂役房→系统熟悉"},
                "narrative_weave": {"场景即时质感": ["灰砖墙", "透光被子"]},
                "architecture_role": {"writable_scene_seed": "系统说人多意味着豪意值"},
            }]})
            scenes = plan.draft_from_rolling(proj, "ch004", pov="程默")
            self.assertEqual(len(scenes), 4)
            self.assertEqual(scenes[0]["one_change"], "抵达")
            self.assertEqual(scenes[0]["pov"], "程默")
            # last scene's exit uses the writable scene seed
            self.assertIn("豪意值", scenes[-1]["exit_on"])

    def test_load_plan_validates_scene_specs(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            chdir = proj / "chapters" / "ch004"
            good = {"id": "ch004_s1", "pov": "程默",
                    "emotional_temperature": {"from": "松", "to": "紧"},
                    "sensory_anchor": "灰砖墙", "exit_on": "门被推开"}
            dump_yaml(chdir / "scene_plan.yml", {"chapter": "ch004", "scenes": [good]})
            scenes, errors = plan.load_plan(proj, "ch004")
            self.assertEqual(errors, [])
            self.assertEqual(len(scenes), 1)

    def test_load_plan_reports_bad_scene(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            chdir = proj / "chapters" / "ch004"
            bad = {"id": "ch004_s1", "pov": "程默"}  # missing required experiential fields
            dump_yaml(chdir / "scene_plan.yml", {"chapter": "ch004", "scenes": [bad]})
            _scenes, errors = plan.load_plan(proj, "ch004")
            self.assertTrue(any("SCENE_SPEC" in e for e in errors))


@unittest.skipUnless(EXAMPLE.exists(), "example-project not present")
class PacketTest(unittest.TestCase):
    def test_build_packets_falls_back_to_skeleton(self):
        packets, notes = build_scene_packets(EXAMPLE, "ch002")
        self.assertTrue(packets)
        self.assertTrue(any("skeleton" in n for n in notes))
        p = packets[0]
        self.assertIn("scene", p)
        self.assertIn("entering_state", p)
        self.assertIn("prose_constraints", p)
        self.assertEqual(p["entering_state"]["entering_chapter"], "ch002")


if __name__ == "__main__":
    unittest.main()
