from abstractions.external_system_model import create_external_system, get_external_systems_by_alert
from abstractions.alert_rule_model import get_all_alert_rules, get_alert_rule_by_id
from abstractions.log_model import log_action

def fetch_alert_rules_for_subscription():
    return get_all_alert_rules()

def register_external_system(form):
    system_name = form["system_name"].strip()
    callback_url = form["callback_url"].strip()
    alert_rule_id = form["alert_rule_id"]

    rule = get_alert_rule_by_id(alert_rule_id)
    if rule is None:
        return False, "Invalid alert selection."

    create_external_system(system_name, callback_url, alert_rule_id)
    log_action(
        "REGISTER_EXTERNAL_SYSTEM",
        f"{system_name} registered for {rule['metric']} alert in {rule['zone']}"
    )
    return True, "External system registered successfully."

def fetch_subscriptions():
    return get_external_systems_by_alert()