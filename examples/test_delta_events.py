"""Meaningful local checks for the portfolio Delta Lake reference."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from deltalake import DeltaTable

from delta_events import publish_events


def event(event_id: str, power_kw: float = 7.4) -> dict:
    return {
        "event_id": event_id,
        "asset_id": "ev-001",
        "event_time": "2026-10-03T12:00:00Z",
        "power_kw": power_kw,
    }


class DeltaEventTests(unittest.TestCase):
    def test_replay_keeps_one_row_per_event_id(self) -> None:
        with TemporaryDirectory() as directory:
            first = publish_events(directory, [event("evt-1"), event("evt-2")])
            replay = publish_events(directory, [event("evt-1"), event("evt-2")])

            rows = DeltaTable(directory).to_pyarrow_table().to_pylist()
            self.assertEqual(first["num_target_rows_inserted"], 2)
            self.assertEqual(replay["num_target_rows_inserted"], 0)
            self.assertEqual({row["event_id"] for row in rows}, {"evt-1", "evt-2"})
            self.assertEqual(len(rows), 2)

    def test_bad_batch_does_not_publish(self) -> None:
        with TemporaryDirectory() as directory:
            publish_events(directory, [event("evt-1")])
            before = DeltaTable(directory).version()

            with self.assertRaises(ValueError):
                publish_events(directory, [event("evt-2"), event("evt-3", float("nan"))])

            table = DeltaTable(directory)
            self.assertEqual(table.version(), before)
            self.assertEqual(table.to_pyarrow_table().num_rows, 1)

    def test_invalid_first_batch_creates_no_table(self) -> None:
        with TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                publish_events(directory, [event("evt-1"), event("evt-1")])
            self.assertFalse((Path(directory) / "_delta_log").exists())


if __name__ == "__main__":
    unittest.main()
