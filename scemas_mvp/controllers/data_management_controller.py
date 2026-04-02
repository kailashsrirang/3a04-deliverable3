import json
from abstractions.telemetry_model import (
    clear_telemetry,
    insert_telemetry,
    get_recent_telemetry,
    get_public_aggregates
)
from abstractions.log_model import log_action
from controllers.alert_management_controller import reset_alerts, evaluate_telemetry_item
from utils.resource_helper import resource_path

def ingest_telemetry():
    with open(resource_path("telemetry.json"), "r") as f:
        data = json.load(f)

    clear_telemetry()
    reset_alerts()

    for item in data:
        insert_telemetry(
            item["sensor_id"],
            item["zone"],
            item["metric"],
            item["value"],
            item["unit"],
            item["timestamp"]
        )
        evaluate_telemetry_item(item)

    log_action("INGEST_TELEMETRY", "Telemetry and alerts refreshed from telemetry.json")

def fetch_public_data():
    return get_public_aggregates()

def fetch_operator_telemetry():
    return get_recent_telemetry()