import unittest

from novel_engine.events import Event
from novel_engine.integrity import check_integrity


def ev(kind, chapter="ch001", **data):
    data["kind"] = kind
    data["chapter"] = chapter
    return Event(kind=kind, chapter=chapter, data=data, source="test")


class IntegrityTest(unittest.TestCase):
    def test_clean_log_has_no_errors(self):
        events = [
            ev("character_introduced", id="char_a", name="甲"),
            ev("character_changed", chapter="ch002", id="char_a", change="变了"),
            ev("debt_opened", id="d1", description="x"),
            ev("debt_paid", chapter="ch003", id="d1"),
        ]
        errors, warnings = check_integrity(events)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_change_before_introduction_is_error(self):
        events = [ev("character_changed", id="ghost", change="x")]
        errors, _ = check_integrity(events)
        self.assertTrue(any("UNKNOWN_CHARACTER" in e for e in errors))

    def test_seed_allows_bootstrap_character(self):
        events = [ev("character_changed", id="boot", change="x")]
        errors, _ = check_integrity(events, known_characters={"boot"})
        self.assertEqual(errors, [])

    def test_pay_debt_never_opened_is_error(self):
        events = [ev("debt_paid", id="nope")]
        errors, _ = check_integrity(events)
        self.assertTrue(any("UNKNOWN_DEBT" in e for e in errors))

    def test_double_pay_is_warning(self):
        events = [
            ev("debt_opened", id="d1", description="x"),
            ev("debt_paid", chapter="ch002", id="d1"),
            ev("debt_paid", chapter="ch003", id="d1"),
        ]
        errors, warnings = check_integrity(events)
        self.assertEqual(errors, [])
        self.assertTrue(any("DEBT_TOUCHED_AFTER_PAID" in w for w in warnings))

    def test_unknown_knowledge_holder_is_error(self):
        events = [ev("knowledge_changed", topic="t", holder="stranger", level="knows")]
        errors, _ = check_integrity(events)
        self.assertTrue(any("UNKNOWN_KNOWLEDGE_HOLDER" in e for e in errors))

    def test_reader_is_valid_knowledge_holder(self):
        events = [ev("knowledge_changed", topic="t", holder="reader", level="hinted")]
        errors, _ = check_integrity(events)
        self.assertEqual(errors, [])

    def test_foreshadow_paid_without_plant_is_error(self):
        events = [ev("foreshadow_paid", id="f9")]
        errors, _ = check_integrity(events)
        self.assertTrue(any("UNKNOWN_FORESHADOW" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
