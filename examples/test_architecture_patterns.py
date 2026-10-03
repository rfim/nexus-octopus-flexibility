"""Checks for source normalization and the read-only consumer boundary."""

import unittest

from architecture_patterns import (
    crm_export_row,
    debezium_message_to_event,
    partner_record_to_event,
    read_approved_metric,
)


class ArchitecturePatternTests(unittest.TestCase):
    def test_partner_and_cdc_paths_share_contract(self) -> None:
        row = {"partner_event_id": "42:2", "asset_ref": "ev-9",
               "power_watts": 7400, "observed_at": "2026-10-03T12:00:00Z"}
        partner = partner_record_to_event(row)
        cdc = debezium_message_to_event({"payload": {"op": "u", "after": {
            "id": 42, "revision": 2, "asset_id": "ev-9", "power_watts": 7400,
            "updated_at": "2026-10-03T12:00:00Z"}}})
        self.assertEqual(partner, cdc)
        self.assertEqual(partner["power_kw"], 7.4)
        self.assertEqual(partner["event_time"], "2026-10-03T12:00:00+00:00")

    def test_delete_and_bad_source_values_do_not_become_readings(self) -> None:
        self.assertIsNone(debezium_message_to_event({"payload": {"op": "d", "after": None}}))
        self.assertIsNone(debezium_message_to_event({"payload": None}))
        with self.assertRaises(ValueError):
            partner_record_to_event({"partner_event_id": "x", "asset_ref": "ev-9",
                                     "power_watts": float("nan"),
                                     "observed_at": "2026-10-03T12:00:00Z"})

    def test_consumer_projection_and_metric_allowlist(self) -> None:
        event = {"asset_id": "ev-9", "event_time": "2026-10-03T12:00:00Z",
                 "power_kw": 7.4, "source_secret": "must not publish"}
        self.assertEqual(set(crm_export_row(event)),
                         {"asset_id", "observed_at", "latest_power_kw"})
        self.assertEqual(read_approved_metric("event_count", {"event_count": 7}), 7)
        with self.assertRaises(PermissionError):
            read_approved_metric("raw_customer_records", {"raw_customer_records": []})


if __name__ == "__main__":
    unittest.main()
