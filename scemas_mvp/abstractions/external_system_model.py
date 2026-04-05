from abstractions.db import get_db_connection

def create_external_system(system_name, callback_url, alert_rule_id):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO external_systems (system_name, callback_url, alert_rule_id)
        VALUES (?, ?, ?)
    """, (system_name, callback_url, alert_rule_id))
    conn.commit()
    conn.close()

def get_external_systems_by_alert():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT
            alert_rules.id AS rule_id,
            alert_rules.metric,
            alert_rules.zone,
            alert_rules.threshold,
            external_systems.id AS system_id,
            external_systems.system_name,
            external_systems.callback_url
        FROM alert_rules
        LEFT JOIN external_systems
            ON external_systems.alert_rule_id = alert_rules.id
        ORDER BY alert_rules.zone, alert_rules.metric, external_systems.system_name
    """).fetchall()
    conn.close()
    return rows

def get_external_systems_by_rule_id(rule_id):
    conn = get_db_connection()
    systems = conn.execute("""
        SELECT system_name, callback_url
        FROM external_systems
        WHERE alert_rule_id = ?
    """, (rule_id,)).fetchall()
    conn.close()
    return systems

def delete_external_system(system_id):
    conn = get_db_connection()
    conn.execute("""
        DELETE FROM external_systems
        WHERE id = ?
    """, (system_id,))
    conn.commit()
    conn.close()