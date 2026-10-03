"""Small, local Delta Lake reference for the portfolio (synthetic event data).

This is separate from the Lifepal production platform described on the site.
It demonstrates validation before publish and replay-safe insertion by event ID.
"""

from datetime import datetime, timezone
from math import isfinite
from pathlib import Path

import pyarrow as pa
from deltalake import DeltaTable, write_deltalake


EVENT_SCHEMA = pa.schema(
    [
        pa.field("event_id", pa.string(), nullable=False),
        pa.field("asset_id", pa.string(), nullable=False),
        pa.field("event_time", pa.string(), nullable=False),
        pa.field("power_kw", pa.float64(), nullable=False),
    ]
)


def validate_events(events: list[dict]) -> pa.Table:
    """Reject an entire batch if any event fails its source contract."""
    if not events:
        raise ValueError("A batch needs at least one event")

    seen: set[str] = set()
    rows: list[dict] = []
    for event in events:
        event_id = event.get("event_id")
        asset_id = event.get("asset_id")
        if not isinstance(event_id, str) or not event_id.strip():
            raise ValueError("event_id is required")
        if event_id in seen:
            raise ValueError(f"duplicate event_id in batch: {event_id}")
        if not isinstance(asset_id, str) or not asset_id.strip():
            raise ValueError("asset_id is required")

        try:
            timestamp = datetime.fromisoformat(event["event_time"].replace("Z", "+00:00"))
            power_kw = float(event["power_kw"])
        except (AttributeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid event fields: {event_id}") from exc
        if timestamp.tzinfo is None or not isfinite(power_kw):
            raise ValueError(f"event needs timezone and finite power: {event_id}")

        seen.add(event_id)
        rows.append(
            {
                "event_id": event_id,
                "asset_id": asset_id,
                "event_time": timestamp.astimezone(timezone.utc).isoformat(),
                "power_kw": power_kw,
            }
        )

    return pa.Table.from_pylist(rows, schema=EVENT_SCHEMA)


def publish_events(table_path: str | Path, events: list[dict]) -> dict:
    """Validate, then MERGE unseen event IDs into a local Delta table."""
    source = validate_events(events)  # A bad batch cannot create or change the table.
    table_path = Path(table_path)
    if not (table_path / "_delta_log").exists():
        write_deltalake(str(table_path), pa.Table.from_pylist([], schema=EVENT_SCHEMA))

    table = DeltaTable(str(table_path))
    return (
        table.merge(
            source=source,
            predicate="target.event_id = source.event_id",
            source_alias="source",
            target_alias="target",
        )
        .when_not_matched_insert_all()
        .execute()
    )
