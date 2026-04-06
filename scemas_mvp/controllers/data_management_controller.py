import json
from abstractions.telemetry_model import (
    clear_telemetry,
    insert_telemetry,
    get_recent_telemetry,
    get_public_aggregates
)
from abstractions.log_model import log_action
from controllers.alert_management_controller import evaluate_telemetry_item
from utils.resource_helper import resource_path

SUPPORTED_ZONES = [
    "Downtown",
    "West",
    "North",
    "East",
    "South"
]
VALID_METRICS = {
    "temperature": (-50.0, 60.0),
    "humidity": (0.0, 100.0),
    "noise": (0.0, 200.0),
    "pm25": (0.0, 1000.0)
}


def validate_telemetry_item(item):
    required_fields = (
        "sensor_id",
        "zone",
        "metric",
        "value",
        "unit",
        "timestamp"
    )
    for field in required_fields:
        if field not in item:
            return False, f"Missing required field '{field}'."

    metric = str(item["metric"]).strip().lower()
    if metric not in VALID_METRICS:
        return False, f"Metric '{item['metric']}' is not supported."

    zone = str(item["zone"]).strip()
    zone_map = {supported.lower(): supported for supported in SUPPORTED_ZONES}
    if zone.lower() not in zone_map:
        return False, f"Zone '{item['zone']}' is not supported."

    try:
        value = float(item["value"])
    except (TypeError, ValueError):
        return False, f"Value '{item['value']}' is not numeric."

    min_val, max_val = VALID_METRICS[metric]
    if not (min_val <= value <= max_val):
        return False, (
            f"Value {value} for metric '{metric}' is outside plausible range "
            f"[{min_val}, {max_val}]."
        )

    item["metric"] = metric
    item["zone"] = zone_map[zone.lower()]
    return True, value


def ingest_telemetry():
    with open(resource_path("telemetry.json"), "r") as f:
        data = json.load(f)

    clear_telemetry()
    # Removed reset_alerts() to preserve alert history

    for item in data:
        is_valid, validation_result = validate_telemetry_item(item)
        if not is_valid:
            log_action("INVALID_TELEMETRY", validation_result)
            continue

        insert_telemetry(
            item["sensor_id"],
            item["zone"],
            item["metric"],
            validation_result,
            item["unit"],
            item["timestamp"]
        )
        evaluate_telemetry_item(item)

    log_action("INGEST_TELEMETRY", "Telemetry and alerts refreshed from telemetry.json")

def fetch_public_data():
    aggregates = get_public_aggregates()
    # Compute summary cards: overall average per metric
    summaries = {}
    for row in aggregates:
        metric = row["metric"]
        if metric not in summaries:
            summaries[metric] = {"total": 0, "count": 0, "unit": row["unit"]}
        summaries[metric]["total"] += row["avg_value"]
        summaries[metric]["count"] += 1
    for metric in summaries:
        summaries[metric]["avg"] = summaries[metric]["total"] / summaries[metric]["count"]
    return aggregates, summaries

def fetch_operator_telemetry():
    return get_recent_telemetry()