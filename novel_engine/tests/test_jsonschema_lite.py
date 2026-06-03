import unittest

from novel_engine import jsonschema_lite
from novel_engine.events import event_schema, validate_event


class JsonSchemaLiteTest(unittest.TestCase):
    def test_type_and_required(self):
        schema = {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}}
        self.assertEqual(jsonschema_lite.validate({"a": "x"}, schema), [])
        self.assertTrue(jsonschema_lite.validate({}, schema))
        self.assertTrue(jsonschema_lite.validate({"a": 1}, schema))

    def test_enum_and_const(self):
        self.assertEqual(jsonschema_lite.validate("open", {"enum": ["open", "paid"]}), [])
        self.assertTrue(jsonschema_lite.validate("nope", {"enum": ["open", "paid"]}))
        self.assertEqual(jsonschema_lite.validate("x", {"const": "x"}), [])
        self.assertTrue(jsonschema_lite.validate("y", {"const": "x"}))

    def test_one_of_discriminates_by_const(self):
        schema = {
            "oneOf": [
                {"properties": {"kind": {"const": "a"}, "x": {"type": "string"}}, "required": ["kind", "x"]},
                {"properties": {"kind": {"const": "b"}, "y": {"type": "integer"}}, "required": ["kind", "y"]},
            ]
        }
        self.assertEqual(jsonschema_lite.validate({"kind": "a", "x": "hi"}, schema), [])
        self.assertEqual(jsonschema_lite.validate({"kind": "b", "y": 3}, schema), [])
        self.assertTrue(jsonschema_lite.validate({"kind": "a"}, schema))  # missing x

    def test_array_items_and_min_items(self):
        schema = {"type": "array", "minItems": 1, "items": {"type": "string"}}
        self.assertEqual(jsonschema_lite.validate(["a"], schema), [])
        self.assertTrue(jsonschema_lite.validate([], schema))
        self.assertTrue(jsonschema_lite.validate([1], schema))


class EventSchemaTest(unittest.TestCase):
    def test_schema_loads(self):
        self.assertIn("oneOf", event_schema())

    def test_valid_events(self):
        self.assertEqual(validate_event({"kind": "fact_added", "text": "x"}), [])
        self.assertEqual(validate_event({"kind": "debt_opened", "id": "d1", "description": "x"}), [])
        self.assertEqual(
            validate_event({"kind": "knowledge_changed", "topic": "t", "holder": "reader", "level": "hinted"}), []
        )

    def test_invalid_events(self):
        self.assertTrue(validate_event({"kind": "fact_added"}))  # missing text
        self.assertTrue(validate_event({"kind": "debt_opened", "id": "d1"}))  # missing description
        self.assertTrue(validate_event({"kind": "not_a_kind", "text": "x"}))  # bad enum
        self.assertTrue(
            validate_event({"kind": "knowledge_changed", "topic": "t", "holder": "r", "level": "omniscient"})
        )  # bad level enum


if __name__ == "__main__":
    unittest.main()
