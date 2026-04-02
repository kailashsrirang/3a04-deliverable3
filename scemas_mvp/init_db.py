import sqlite3

DB_NAME = "scemas.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Telemetry table
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

    # Alert rules table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alert_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric TEXT NOT NULL,
            zone TEXT NOT NULL,
            threshold REAL NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Alerts table
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

    # External systems table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS external_systems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system_name TEXT NOT NULL,
            callback_url TEXT NOT NULL,
            alert_rule_id INTEGER NOT NULL,
            FOREIGN KEY (alert_rule_id) REFERENCES alert_rules(id)
        )
    """)

    # Logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # Seed users
    cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES (?, ?)", ("public", "public"))
    cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES (?, ?)", ("operator", "operator"))
    cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES (?, ?)", ("admin", "admin"))

    # Seed alert rules
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
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()