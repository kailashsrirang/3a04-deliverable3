from abstractions.db import get_db_connection

def clear_alerts():
    conn = get_db_connection()
    conn.execute("DELETE FROM alerts")
    conn.commit()
    conn.close()

def create_alert(metric, zone, current_value, threshold, status, timestamp):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO alerts (metric, zone, current_value, threshold, status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (metric, zone, current_value, threshold, status, timestamp))
    conn.commit()
    conn.close()

def get_all_alerts():
    conn = get_db_connection()
    alerts = conn.execute("""
        SELECT * FROM alerts
        ORDER BY timestamp DESC
    """).fetchall()
    conn.close()
    return alerts

def active_alert_exists(metric, zone):
    conn = get_db_connection()
    alert = conn.execute("""
        SELECT 1 FROM alerts
        WHERE metric = ? AND zone = ? AND status = 'active'
        LIMIT 1
    """, (metric, zone)).fetchone()
    conn.close()
    return alert is not None

def update_alert_status(alert_id, status):
    conn = get_db_connection()
    conn.execute("""
        UPDATE alerts
        SET status = ?
        WHERE id = ?
    """, (status, alert_id))
    conn.commit()
    conn.close()