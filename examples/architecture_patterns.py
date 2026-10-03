"""Small source and consumer contracts for the Nexus portfolio diagram.

These functions use synthetic data. They show the shape of boundaries around the
Delta Lake reference; they are not Lifepal or Octopus production integrations.
"""

from datetime import datetime, timezone
from math import isfinite


def partner_record_to_event(record: dict) -> dict:
    """Map a partner file row to the shared event contract."""
    event_id = str(record["partner_event_id"]).strip()
    asset_id = str(record["asset_ref"]).strip()
    power_kw = float(record["power_watts"]) / 1000
    if not event_id or not asset_id or not isfinite(power_kw):
        raise ValueError("partner row has an invalid ID or power value")
    event_time = datetime.fromisoformat(record["observed_at"].replace("Z", "+00:00"))
    if event_time.tzinfo is None:
        raise ValueError("partner timestamp needs a timezone")
    return {"event_id": event_id, "asset_id": asset_id,
            "event_time": event_time.astimezone(timezone.utc).isoformat(),
            "power_kw": power_kw}


def debezium_message_to_event(message: dict) -> dict | None:
    """Read a Debezium value envelope; deletes do not become power readings."""
    payload = message.get("payload") if message is not None else None
    if payload is None:  # Kafka tombstone after a delete.
        return None
    if payload["op"] == "d":
        return None
    row = payload["after"]
    if row is None:
        raise ValueError("change event has no after image")
    return partner_record_to_event({
        "partner_event_id": f"{row['id']}:{row['revision']}",
        "asset_ref": row["asset_id"],
        "power_watts": row["power_watts"],
        "observed_at": row["updated_at"],
    })


def crm_export_row(event: dict) -> dict:
    """Expose a narrow, versionable consumer record instead of raw source data."""
    return {"asset_id": event["asset_id"],
            "observed_at": event["event_time"],
            "latest_power_kw": event["power_kw"]}


APPROVED_METRICS = frozenset({"daily_energy_kwh", "event_count"})


def read_approved_metric(name: str, published_metrics: dict) -> object:
    """Read-only tool boundary for a future agent; no arbitrary query execution."""
    if name not in APPROVED_METRICS:
        raise PermissionError(f"metric is not approved: {name}")
    if name not in published_metrics:
        raise KeyError(name)
    return published_metrics[name]
