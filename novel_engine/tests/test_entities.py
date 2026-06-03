import unittest

from novel_engine.events import Event, validate_event
from novel_engine.integrity import check_integrity
from novel_engine.materialize import materialize
from novel_engine.projection import project


def ev(kind, chapter="bootstrap", **data):
    data["kind"] = kind
    data["chapter"] = chapter
    return Event(kind=kind, chapter=chapter, data=data, source="t")


class EntityEventSchemaTest(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_event({"kind": "faction_introduced", "id": "f1", "name": "破云宗"}), [])
        self.assertEqual(validate_event({"kind": "location_introduced", "id": "l1", "name": "后山"}), [])
        self.assertEqual(validate_event({"kind": "faction_changed", "id": "f1", "change": "扩张"}), [])
        self.assertEqual(validate_event({"kind": "power_introduced", "id": "p1", "name": "炼气"}), [])

    def test_invalid(self):
        self.assertTrue(validate_event({"kind": "faction_introduced", "id": "f1"}))  # missing name
        self.assertTrue(validate_event({"kind": "faction_changed", "id": "f1"}))  # missing change


class EntityProjectionTest(unittest.TestCase):
    def test_faction_introduce_then_change(self):
        events = [
            ev("faction_introduced", id="f1", name="破云宗", scale="小宗"),
            ev("faction_changed", "ch001", id="f1", change="开始回收", set={"current_action": "清理"}),
            ev("location_introduced", id="l1", name="后山禁地"),
        ]
        state = project(events)
        self.assertEqual(state.factions["f1"]["name"], "破云宗")
        self.assertEqual(state.factions["f1"]["current_action"], "清理")
        self.assertEqual(len(state.factions["f1"]["change_history"]), 1)
        self.assertIn("l1", state.locations)

    def test_materialize_writes_faction_location_files(self):
        events = [ev("faction_introduced", id="f1", name="破云宗"), ev("location_introduced", id="l1", name="后山")]
        files = materialize(project(events))
        self.assertEqual(files["entities/factions.yml"]["factions"][0]["name"], "破云宗")
        self.assertEqual(files["entities/locations.yml"]["locations"][0]["id"], "l1")

    def test_change_before_introduce_is_error(self):
        errors, _ = check_integrity([ev("faction_changed", "ch001", id="ghost", change="x")])
        self.assertTrue(any("UNKNOWN_FACTION" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
