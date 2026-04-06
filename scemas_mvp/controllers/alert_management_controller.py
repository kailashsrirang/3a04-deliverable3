from abstractions.alert_rule_model import (
    get_all_alert_rules,
    create_alert_rule,
    update_alert_threshold,
    get_matching_alert_rule
)
from abstractions.external_system_model import get_external_systems_by_rule_id
from abstractions.alert_model import create_alert, clear_alerts, get_all_alerts, active_alert_exists, update_alert_status
from abstractions.log_model import log_action
from datetime import datetime

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
            f"Updated alert rule {rule_id} with threshold {threshold}"
        )

def get_effective_threshold(rule):
    if rule["metric"] == "noise":
        now = datetime.now()
        hour = now.hour
        if 7 <= hour < 22:  # daytime 7:00 to 21:59
            return rule["threshold"]
        else:  # night
            return rule["threshold"] - 20
    else:
        return rule["threshold"]

def evaluate_telemetry_item(item):
    rule = get_matching_alert_rule(item["metric"], item["zone"])
    if rule:
        effective_threshold = get_effective_threshold(rule)
        if item["value"] > effective_threshold and not active_alert_exists(item["metric"], item["zone"]):
            create_alert(
                item["metric"],
                item["zone"],
                item["value"],
                effective_threshold,
                "active",
                item["timestamp"]
            )
            # log triggered alert
            log_action(
                "ALERT_TRIGGERED",
                (
                    f"Triggered alert for metric={item['metric']}, "
                    f"zone={item['zone']}, "
                    f"value={item['value']}, "
                    f"threshold={effective_threshold}, "
                    f"timestamp={item['timestamp']}"
                )
            )

            # notify subscribed external systems
            systems = get_external_systems_by_rule_id(rule["id"])
            for system in systems:
                log_action(
                    "NOTIFY_EXTERNAL_SYSTEM",
                    f"System '{system['system_name']}' notified for {rule['metric']} alert in {rule['zone']}"
                )

def fetch_alerts():
    return get_all_alerts()

def acknowledge_alert(alert_id):
    update_alert_status(alert_id, "acknowledged")
    log_action("ALERT_ACKNOWLEDGED", f"Alert {alert_id} acknowledged")

def resolve_alert(alert_id):
    update_alert_status(alert_id, "resolved")
    log_action("ALERT_RESOLVED", f"Alert {alert_id} resolved")