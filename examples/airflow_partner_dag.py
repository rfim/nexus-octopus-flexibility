"""Illustrative local-file DAG; needs Airflow and the Delta dependencies to run."""

import json
from datetime import datetime
from pathlib import Path

from airflow.decorators import dag, task

from architecture_patterns import partner_record_to_event
from delta_events import publish_events


@dag(schedule="@hourly", start_date=datetime(2026, 1, 1), catchup=False)
def nexus_partner_ingest():
    @task
    def load_partner_batch() -> dict:
        source = Path("/opt/airflow/data/partner-events.jsonl")
        rows = [json.loads(line) for line in source.read_text().splitlines() if line]
        events = [partner_record_to_event(row) for row in rows]
        return publish_events("/opt/airflow/data/nexus-delta", events)

    load_partner_batch()


nexus_partner_ingest()
