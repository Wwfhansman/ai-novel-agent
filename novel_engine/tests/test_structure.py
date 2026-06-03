import unittest
from pathlib import Path

from novel_engine.events import Event
from novel_engine.profile import load_profile
from novel_engine.structure.analyze import analyze
from novel_engine.structure.chapter_meta import ChapterMeta, validate_record
from novel_engine.structure.legacy_structure import from_rolling_plan

PROFILE = load_profile()
REPO = Path(__file__).resolve().parents[2]
EXAMPLE = REPO / "projects" / "example-project"


def meta(ch, **kw):
    return ChapterMeta(chapter=ch, **kw)


class AnalyzeTest(unittest.TestCase):
    def test_clean_varied_plan_has_no_warnings(self):
        records = [
            meta("ch001", pacing_mode="pressure", chapter_function="investigation",
                 position_in_flow="rising_early", world_expansion=True, offscreen_pressure=True),
            meta("ch002", pacing_mode="mystery", chapter_function="reveal",
                 position_in_flow="rising_middle", world_expansion=True, offscreen_pressure=True),
            meta("ch003", pacing_mode="relationship", chapter_function="social_conflict",
                 position_in_flow="peak", world_expansion=True, offscreen_pressure=True),
        ]
        self.assertEqual(analyze(records, PROFILE)["warnings"], [])

    def test_pacing_loop_flagged(self):
        records = [meta(f"ch00{i}", pacing_mode="pressure", world_expansion=True, offscreen_pressure=True)
                   for i in range(1, 4)]
        warnings = analyze(records, PROFILE)["warnings"]
        self.assertTrue(any("PACING_LOOP" in w for w in warnings))

    def test_world_expansion_drought_flagged(self):
        records = [meta(f"ch00{i}", pacing_mode=m, world_expansion=False, offscreen_pressure=True)
                   for i, m in enumerate(["a", "b", "c"], start=1)]
        warnings = analyze(records, PROFILE)["warnings"]
        self.assertTrue(any("WORLD_EXPANSION_DROUGHT" in w for w in warnings))

    def test_tension_flatline_flagged(self):
        records = [meta(f"ch00{i}", pacing_mode=m, position_in_flow="aftermath_trough",
                        world_expansion=True, offscreen_pressure=True)
                   for i, m in enumerate(["a", "b", "c"], start=1)]
        warnings = analyze(records, PROFILE)["warnings"]
        self.assertTrue(any("TENSION_FLATLINE" in w for w in warnings))

    def test_growth_too_dense_flagged(self):
        records = [meta(f"ch00{i}", pacing_mode=m, world_expansion=True, offscreen_pressure=True,
                        protagonist_growth=True)
                   for i, m in enumerate(["a", "b", "c", "d", "e"], start=1)]
        warnings = analyze(records, PROFILE)["warnings"]
        self.assertTrue(any("GROWTH_TOO_DENSE" in w for w in warnings))

    def test_arc_stall_from_events(self):
        records = [meta(f"ch{i:03d}", pacing_mode=m, world_expansion=True, offscreen_pressure=True)
                   for i, m in zip(range(1, 13), "abcabcabcabc")]
        events = [
            Event("character_introduced", "ch001", {"id": "hero", "name": "H", "role": "protagonist"}, "t"),
            Event("character_changed", "ch002", {"id": "hero", "change": "x"}, "t"),
        ]
        warnings = analyze(records, PROFILE, events=events)["warnings"]
        self.assertTrue(any("ARC_STALL" in w and "hero" in w for w in warnings))


class SchemaTest(unittest.TestCase):
    def test_record_requires_chapter(self):
        self.assertEqual(validate_record({"chapter": "ch001", "pacing_mode": "pressure"}), [])
        self.assertTrue(validate_record({"pacing_mode": "pressure"}))

    def test_bad_type_rejected(self):
        self.assertTrue(validate_record({"chapter": "ch001", "world_expansion": "yes"}))


@unittest.skipUnless(EXAMPLE.exists(), "example-project not present")
class LegacyStructureTest(unittest.TestCase):
    def test_extracts_records_from_rolling_plan(self):
        records = from_rolling_plan(EXAMPLE, PROFILE)
        self.assertGreaterEqual(len(records), 5)
        # The example plan varies pacing and keeps world_expansion on every chapter.
        self.assertTrue(all(r.pacing_mode for r in records))
        self.assertTrue(all(r.world_expansion for r in records))
        # And it declares no power growth.
        self.assertTrue(all(not r.protagonist_growth for r in records))

    def test_example_plan_is_structurally_clean(self):
        records = from_rolling_plan(EXAMPLE, PROFILE)
        report = analyze(records, PROFILE)
        self.assertEqual(report["warnings"], [])


if __name__ == "__main__":
    unittest.main()
