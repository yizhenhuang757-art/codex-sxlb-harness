import shutil
import tempfile
import unittest
from pathlib import Path

from learning_ledger import add_entry, mark_stale, query_entries


class LearningLedgerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="sxlb-learning-ledger-"))
        self.ledger = self.temp_dir / "learning-ledger.jsonl"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_add_and_query_entry(self) -> None:
        add_entry(
            self.ledger,
            {
                "type": "pattern",
                "scope": "project",
                "source": "observed",
                "confidence": 7,
                "summary": "Use approval ledger for dangerous branches",
                "promote_to": "none",
                "stale_when": "guard protocol changes",
            },
        )
        rows = query_entries(self.ledger, learning_type="pattern")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "active")

    def test_mark_stale_updates_status(self) -> None:
        add_entry(
            self.ledger,
            {
                "type": "operational",
                "scope": "case",
                "source": "observed",
                "confidence": 6,
                "summary": "Case-level workaround",
                "promote_to": "none",
                "stale_when": "next release",
            },
        )
        changed = mark_stale(self.ledger, scope="case", reason="superseded")
        self.assertEqual(changed, 1)
        stale = query_entries(self.ledger, status="stale")
        self.assertEqual(len(stale), 1)
        self.assertEqual(stale[0]["stale_reason"], "superseded")

    def test_add_rejects_invalid_scope(self) -> None:
        with self.assertRaises(ValueError):
            add_entry(
                self.ledger,
                {
                    "type": "pattern",
                    "scope": "global",
                    "source": "observed",
                    "confidence": 7,
                    "summary": "invalid",
                    "promote_to": "none",
                    "stale_when": "never",
                },
            )


if __name__ == "__main__":
    unittest.main()
