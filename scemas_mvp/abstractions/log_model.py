from datetime import datetime
from abstractions.db import get_db_connection

def log_action(action, details):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO logs (action, details, timestamp) VALUES (?, ?, ?)",
        (action, details, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_all_logs():
    conn = get_db_connection()
    logs = conn.execute("""
        SELECT * FROM logs
        ORDER BY id DESC
    """).fetchall()
    conn.close()
    return logs