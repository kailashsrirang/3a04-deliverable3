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