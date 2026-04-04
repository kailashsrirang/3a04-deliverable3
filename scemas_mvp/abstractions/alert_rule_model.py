from abstractions.db import get_db_connection

def get_all_alert_rules():
    conn = get_db_connection()
    rules = conn.execute("""
        SELECT * FROM alert_rules
        ORDER BY zone, metric
    """).fetchall()
    conn.close()
    return rules

def get_alert_rule_by_id(rule_id):
    conn = get_db_connection()
    rule = conn.execute("""
        SELECT * FROM alert_rules
        WHERE id = ?
    """, (rule_id,)).fetchone()
    conn.close()
    return rule

def get_matching_alert_rule(metric, zone):
    conn = get_db_connection()
    rule = conn.execute("""
        SELECT * FROM alert_rules
        WHERE metric = ? AND zone = ? AND enabled = 1
    """, (metric, zone)).fetchone()
    conn.close()
    return rule

def create_alert_rule(metric, zone, threshold):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO alert_rules (metric, zone, threshold, enabled)
        VALUES (?, ?, ?, 1)
    """, (metric, zone, threshold))
    conn.commit()
    conn.close()

def update_alert_threshold(rule_id, threshold):
    conn = get_db_connection()
    conn.execute("""
        UPDATE alert_rules
        SET threshold = ?
        WHERE id = ?
    """, (threshold, rule_id))
    conn.commit()
    conn.close()