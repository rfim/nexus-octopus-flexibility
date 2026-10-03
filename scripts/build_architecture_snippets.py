"""Generate the site's inspectable architecture excerpts from repo source files."""

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://github.com/rfim/nexus-octopus-flexibility/blob/main/"

SAMPLES = {
    "postgres": ("examples/source_events.sql", None, "SQL", "PostgreSQL source contract",
                 "Illustrative PostgreSQL schema with a source key, revision and timestamp.", "Illustrative schema; no database is deployed here."),
    "partner": ("examples/architecture_patterns.py", "partner_record_to_event", "PYTHON", "APIs & partner files",
                "A tested adapter converts a partner row to the event contract and rejects invalid values.", "Tested local source adapter; synthetic records."),
    "kafka": ("examples/architecture_patterns.py", "debezium_message_to_event", "PYTHON", "Kafka + Debezium",
              "A tested Debezium value-envelope adapter preserves identity and ignores deletes as readings.", "Tested envelope parser; Kafka is not running in this demo."),
    "airflow": ("examples/airflow_partner_dag.py", None, "PYTHON", "Airflow + Python",
                "An hourly DAG sketch reads a local partner file, applies the shared adapter and publishes to Delta.", "Illustrative DAG; requires an Airflow environment."),
    "databricks": ("examples/gold_daily_flexibility.sql", None, "SQL", "Databricks SQL",
                   "A Databricks SQL view sketch exposes a curated daily product from a validated Delta Silver table.", "Illustrative SQL; no Databricks workspace is connected."),
    "spark": ("examples/spark_silver.py", "build_silver_events", "PYTHON", "Apache Spark",
              "A Spark Silver transform rejects invalid rows and keeps the latest ingested version of each event ID.", "Illustrative transform; requires a Spark runtime."),
    "delta": ("examples/delta_events.py", "publish_events", "PYTHON", "Delta Lake",
              "The runnable local reference uses Delta MERGE so repeated event IDs do not create duplicate visible rows.", "Runnable local Delta Lake reference; synthetic events."),
    "bronze": ("examples/delta_events.py", "publish_events", "PYTHON", "Bronze · durable write",
               "The runnable reference validates then MERGEs unseen IDs to one Delta table. A full Bronze/Silver/Gold deployment is not included.", "Runnable local Delta Lake reference; synthetic events."),
    "silver": ("examples/delta_events.py", "validate_events", "PYTHON", "Silver · quality gate",
               "The source contract rejects a whole batch before a Delta write when IDs, timestamps or power values fail checks.", "Runnable local Delta Lake reference; synthetic events."),
    "gold": ("examples/gold_daily_flexibility.sql", None, "SQL", "Gold · curated model",
             "An illustrative Databricks SQL view publishes daily event counts and average power from validated Silver rows.", "Illustrative SQL; the view is not deployed."),
    "analytics": ("examples/analytics_product.sql", None, "SQL", "Analytics & BI",
                  "A consumer query reads the curated Gold view so the model owns the shared definition.", "Illustrative SQL; no BI system is connected."),
    "crm": ("examples/architecture_patterns.py", "crm_export_row", "PYTHON", "CRM & data science",
            "A tested projection publishes only approved fields from an event, omitting unrelated source data.", "Tested local projection; no CRM is connected."),
    "mcp": ("examples/architecture_patterns.py", "read_approved_metric", "PYTHON", "MCP agents & RAG",
            "A tested read-only boundary allows named metrics and rejects arbitrary data requests.", "Tested boundary function; no MCP or RAG server is deployed."),
    "trust": ("examples/test_delta_events.py", "test_bad_batch_does_not_publish", "PYTHON", "Trust across the flow",
              "The test proves a failed batch leaves the Delta transaction version and visible row count unchanged.", "Runnable local test for validation before publish."),
    "foundation": ("examples/requirements.txt", None, "TEXT", "Platform foundation",
                   "The local Delta reference pins its Python dependencies. AWS and Databricks are shown in the architecture, not deployed by this demo.", "Dependency manifest for the local runnable reference."),
}


def extract(path: Path, symbol: str | None) -> tuple[str, int, int]:
    source = path.read_text().splitlines()
    if symbol is None:
        return "\n".join(source), 1, len(source)
    tree = ast.parse("\n".join(source))
    matches = [node for node in ast.walk(tree)
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
               and node.name == symbol]
    if len(matches) != 1:
        raise ValueError(f"Expected one definition of {symbol} in {path}")
    node = matches[0]
    return "\n".join(source[node.lineno - 1:node.end_lineno]), node.lineno, node.end_lineno


def main() -> None:
    snippets = {}
    for key, (filename, symbol, language, title, description, scope) in SAMPLES.items():
        code, first, last = extract(ROOT / filename, symbol)
        snippets[key] = {
            "title": title, "description": description, "scope": scope,
            "filename": filename, "language": language, "code": code,
            "link": f"{BASE}{filename}#L{first}-L{last}",
        }
    output = ROOT / "assets/architecture-snippets.json"
    output.write_text(json.dumps(snippets, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
