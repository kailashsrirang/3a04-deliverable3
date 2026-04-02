# abstractions/telemetry_model.py
from abstractions.db import get_db_connection

def clear_telemetry():
    conn = get_db_connection()
    conn.execute("DELETE FROM telemetry")
    conn.commit()
    conn.close()

def insert_telemetry(sensor_id, zone, metric, value, unit, timestamp):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO telemetry (sensor_id, zone, metric, value, unit, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (sensor_id, zone, metric, value, unit, timestamp))
    conn.commit()
    conn.close()

def get_recent_telemetry(limit=20):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT * FROM telemetry
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return rows

def get_public_aggregates():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT zone, metric, AVG(value) AS avg_value, unit
        FROM telemetry
        GROUP BY zone, metric, unit
        ORDER BY zone, metric
    """).fetchall()
    conn.close()
    return rows