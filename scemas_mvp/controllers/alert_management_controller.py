from abstractions.alert_rule_model import (
    get_all_alert_rules,
    create_alert_rule,
    update_alert_threshold,
    get_matching_alert_rule
)
from abstractions.alert_model import create_alert, clear_alerts, get_all_alerts
from abstractions.log_model import log_action

AVAILABLE_METRICS = ["pm25", "temperature", "humidity", "noise"]
AVAILABLE_ZONES = ["Downtown", "West", "North", "East", "South"]

def fetch_all_rules():
    return get_all_alert_rules()

def fetch_available_metrics():
    return AVAILABLE_METRICS

def fetch_available_zones():
    return AVAILABLE_ZONES

def handle_alert_form(form):
    form_type = form["form_type"]

    if form_type == "create":
        metric = form["metric"].strip()
        zone = form["zone"].strip()
        threshold = form["threshold"]
        create_alert_rule(metric, zone, threshold)
        log_action(
            "CREATE_ALERT_RULE",
            f"Created alert rule: metric={metric}, zone={zone}, threshold={threshold}"
        )

    elif form_type == "update":
        rule_id = form["rule_id"]
        threshold = form["threshold"]
        update_alert_threshold(rule_id, threshold)
        log_action(
            "UPDATE_ALERT_RULE",
            f"Rule {rule_id} updated: threshold={threshold}"
        )

def reset_alerts():
    clear_alerts()

def evaluate_telemetry_item(item):
    rule = get_matching_alert_rule(item["metric"], item["zone"])
    if rule and item["value"] > rule["threshold"]:
        create_alert(
            item["metric"],
            item["zone"],
            item["value"],
            rule["threshold"],
            "active",
            item["timestamp"]
        )

def fetch_alerts():
    return get_all_alerts()