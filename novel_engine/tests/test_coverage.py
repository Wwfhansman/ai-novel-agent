import tempfile
import unittest
from pathlib import Path

from novel_engine.coverage import coverage_warnings
from novel_engine.events import Event
from novel_engine.profile import load_profile, resolve_project_profile
from novel_engine.projection import project
from novel_engine.yamlio import dump_yaml

PROFILE = load_profile()


def ev(kind, chapter, **data):
    data["kind"] = kind
    data["chapter"] = chapter
    return Event(kind=kind, chapter=chapter, data=data, source="t")


def _two_chars():
    return [
        ev("character_introduced", "bootstrap", id="a", name="陈默"),
        ev("character_introduced", "bootstrap", id="b", name="林冲"),
    ]


class CoverageTest(unittest.TestCase):
    def _project(self, tmp, final_text, ch001_events):
        proj = Path(tmp) / "p"
        (proj / "chapters" / "ch001").mkdir(parents=True)
        (proj / "chapters" / "ch001" / "final.txt").write_text(final_text, encoding="utf-8")
        events = _two_chars() + ch001_events
        return proj, events

    def test_flags_unrecorded_relationship(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj, events = self._project(
                tmp, "第一章\n\n那天之后，陈默和林冲结盟了，一起对付仇人。\n", []
            )
            warns = coverage_warnings(proj, events, project(events), PROFILE)
            self.assertTrue(any("COVERAGE_RELATIONSHIP_UNRECORDED" in w and "陈默" in w and "林冲" in w for w in warns))

    def test_no_warning_when_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj, events = self._project(
                tmp, "第一章\n\n那天之后，陈默和林冲结盟了。\n",
                [ev("relationship_changed", "ch001", a="a", b="b", to="盟友")],
            )
            warns = coverage_warnings(proj, events, project(events), PROFILE)
            self.assertEqual(warns, [])

    def test_no_trigger_no_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj, events = self._project(tmp, "第一章\n\n陈默和林冲一起吃了顿饭。\n", [])
            warns = coverage_warnings(proj, events, project(events), PROFILE)
            self.assertEqual(warns, [])

    def test_single_character_no_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj, events = self._project(tmp, "第一章\n\n陈默决定结盟天下豪杰。\n", [])
            warns = coverage_warnings(proj, events, project(events), PROFILE)
            self.assertEqual(warns, [])


class ProfileOverrideTest(unittest.TestCase):
    def test_project_override_bans_not_but(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "p"
            proj.mkdir()
            dump_yaml(proj / "project.yml", {
                "project": {"id": "p"},
                "profile_overrides": {"banned_patterns": {"max_not_but_per_chapter": 0}},
            })
            prof = resolve_project_profile(proj)
            self.assertEqual(prof["banned_patterns"]["max_not_but_per_chapter"], 0)
            # base profile still intact elsewhere
            self.assertIn("contrast_negation", prof["banned_patterns"])

    def test_no_override_keeps_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp) / "p"
            proj.mkdir()
            prof = resolve_project_profile(proj)
            self.assertEqual(prof["banned_patterns"]["max_not_but_per_chapter"], 1)


if __name__ == "__main__":
    unittest.main()
