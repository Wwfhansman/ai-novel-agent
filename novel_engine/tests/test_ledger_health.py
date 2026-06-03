import unittest

from novel_engine.ledger_health import check_ledger_health
from novel_engine.projection import State


class LedgerHealthTest(unittest.TestCase):
    def test_overdue_debt_flagged(self):
        state = State(debts={
            "d1": {"id": "d1", "status": "open", "payoff_window": "ch002-ch004", "urgency": "high", "description": "x"},
        })
        warnings = check_ledger_health(state, current_chapter_no=9)
        self.assertTrue(any("DEBT_OVERDUE" in w and "d1" in w for w in warnings))

    def test_debt_within_window_not_flagged(self):
        state = State(debts={
            "d1": {"id": "d1", "status": "open", "payoff_window": "ch002-ch004", "description": "x"},
        })
        self.assertEqual(check_ledger_health(state, current_chapter_no=3), [])

    def test_paid_debt_never_flagged(self):
        state = State(debts={
            "d1": {"id": "d1", "status": "paid", "payoff_window": "ch002-ch004", "description": "x"},
        })
        self.assertEqual(check_ledger_health(state, current_chapter_no=99), [])

    def test_non_numeric_window_skipped(self):
        state = State(debts={
            "d1": {"id": "d1", "status": "open", "payoff_window": "volume_001_mid", "description": "x"},
        })
        self.assertEqual(check_ledger_health(state, current_chapter_no=50), [])

    def test_stale_foreshadow_flagged(self):
        state = State(foreshadowing={
            "f1": {"id": "f1", "status": "planted", "last_touched": "ch002", "content": "x"},
        })
        warnings = check_ledger_health(state, current_chapter_no=20, foreshadow_stale_after=12)
        self.assertTrue(any("FORESHADOW_STALE" in w and "f1" in w for w in warnings))

    def test_recent_foreshadow_not_flagged(self):
        state = State(foreshadowing={
            "f1": {"id": "f1", "status": "planted", "last_touched": "ch018", "content": "x"},
        })
        self.assertEqual(check_ledger_health(state, current_chapter_no=20, foreshadow_stale_after=12), [])


if __name__ == "__main__":
    unittest.main()
