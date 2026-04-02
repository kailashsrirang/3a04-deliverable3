# abstractions/db.py
import sqlite3
from utils.resource_helper import get_db_name

DB_NAME = get_db_name()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT NOT NULL,
            zone TEXT NOT NULL,
            metric TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric TEXT NOT NULL,
            zone TEXT NOT NULL,
            threshold REAL NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric TEXT NOT NULL,
            zone TEXT NOT NULL,
            current_value REAL NOT NULL,
            threshold REAL NOT NULL,
            status TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS external_systems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system_name TEXT NOT NULL,
            callback_url TEXT NOT NULL,
            alert_rule_id INTEGER NOT NULL,
            FOREIGN KEY (alert_rule_id) REFERENCES alert_rules(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES (?, ?)", ("public", "public"))
    cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES (?, ?)", ("operator", "operator"))
    cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES (?, ?)", ("admin", "admin"))

    cursor.execute("""
        INSERT OR IGNORE INTO alert_rules (id, metric, zone, threshold, enabled)
        VALUES (1, 'pm25', 'Downtown', 100, 1)
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO alert_rules (id, metric, zone, threshold, enabled)
        VALUES (2, 'temperature', 'West', 30, 1)
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO alert_rules (id, metric, zone, threshold, enabled)
        VALUES (3, 'noise', 'Downtown', 70, 1)
    """)

    conn.commit()
    conn.close()