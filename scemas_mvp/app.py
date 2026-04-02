from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import json
from datetime import datetime
import os
import sys
import shutil


def resource_path(relative_path):
    """Path to bundled read-only files (works in dev and PyInstaller)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


def writable_path(filename):
    """Path to user-writable app files."""
    base_dir = os.path.join(os.path.expanduser("~"), ".scemas_mvp")
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, filename)


def find_data_file(filename):
    """
    Prefer a user-editable copy in the writable folder.
    Fall back to the bundled copy.
    """
    writable_file = writable_path(filename)
    if os.path.exists(writable_file):
        return writable_file
    return resource_path(filename)


app = Flask(
    __name__,
    template_folder=resource_path("templates"),
    static_folder=resource_path("static")
)

DB_NAME = writable_path("scemas.db")
SEED_DB = resource_path("scemas.db")


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """
    Ensure the runtime database exists and has the required schema.
    If a bundled seed database exists, copy it on first run.
    """
    if not os.path.exists(DB_NAME):
        if os.path.exists(SEED_DB):
            shutil.copy2(SEED_DB, DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cur.execute("""
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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS alert_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric TEXT NOT NULL,
            zone TEXT NOT NULL,
            threshold REAL NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1
        )
    """)

    cur.execute("""
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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS external_systems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            system_name TEXT NOT NULL,
            callback_url TEXT NOT NULL,
            alert_rule_id INTEGER NOT NULL,
            FOREIGN KEY (alert_rule_id) REFERENCES alert_rules (id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            details TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # Seed default users if missing
    user_count = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        cur.executemany("""
            INSERT INTO users (username, role)
            VALUES (?, ?)
        """, [
            ("public", "public"),
            ("operator", "operator"),
            ("admin", "admin")
        ])

    # Seed default alert rules if missing
    rules_count = cur.execute("SELECT COUNT(*) FROM alert_rules").fetchone()[0]
    if rules_count == 0:
        cur.executemany("""
            INSERT INTO alert_rules (metric, zone, threshold, enabled)
            VALUES (?, ?, ?, ?)
        """, [
            ("pm25", "Downtown", 35, 1),
            ("temperature", "West", 30, 1),
            ("humidity", "North", 75, 1),
            ("noise", "East", 80, 1)
        ])

    conn.commit()
    conn.close()


def log_action(action, details):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO logs (action, details, timestamp) VALUES (?, ?, ?)",
        (action, details, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def ingest_telemetry():
    telemetry_file = find_data_file("telemetry.json")

    if not os.path.exists(telemetry_file):
        raise FileNotFoundError(
            f"Could not find telemetry.json. Looked for: {telemetry_file}"
        )

    with open(telemetry_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    conn = get_db_connection()

    # Clean old telemetry and alerts for a simple MVP demo
    conn.execute("DELETE FROM telemetry")
    conn.execute("DELETE FROM alerts")

    for item in data:
        conn.execute("""
            INSERT INTO telemetry (sensor_id, zone, metric, value, unit, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            item["sensor_id"],
            item["zone"],
            item["metric"],
            item["value"],
            item["unit"],
            item["timestamp"]
        ))

        rule = conn.execute("""
            SELECT * FROM alert_rules
            WHERE metric = ? AND zone = ? AND enabled = 1
        """, (
            item["metric"],
            item["zone"]
        )).fetchone()

        if rule and item["value"] > rule["threshold"]:
            conn.execute("""
                INSERT INTO alerts (metric, zone, current_value, threshold, status, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                item["metric"],
                item["zone"],
                item["value"],
                rule["threshold"],
                "active",
                item["timestamp"]
            ))

    conn.commit()
    conn.close()

    log_action("INGEST_TELEMETRY", "Telemetry and alerts refreshed from telemetry.json")


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip().lower()

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if not user:
            return render_template("login.html", error="Invalid username")

        log_action("LOGIN", f"{username} logged in")

        if user["role"] == "public":
            return redirect(url_for("public_dashboard"))
        elif user["role"] == "operator":
            return redirect(url_for("operator_dashboard"))
        elif user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))

    return render_template("login.html")


@app.route("/public")
def public_dashboard():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT zone, metric, AVG(value) AS avg_value, unit
        FROM telemetry
        GROUP BY zone, metric, unit
        ORDER BY zone, metric
    """).fetchall()
    conn.close()

    return render_template(
        "public_dashboard.html",
        rows=rows,
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@app.route("/operator")
def operator_dashboard():
    conn = get_db_connection()
    telemetry = conn.execute("""
        SELECT * FROM telemetry
        ORDER BY timestamp DESC
        LIMIT 20
    """).fetchall()

    alerts = conn.execute("""
        SELECT * FROM alerts
        ORDER BY timestamp DESC
    """).fetchall()

    conn.close()

    return render_template(
        "operator_dashboard.html",
        telemetry=telemetry,
        alerts=alerts,
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )


@app.route("/admin")
def admin_dashboard():
    return render_template("admin_dashboard.html")


@app.route("/public/register", methods=["GET", "POST"])
def external_register():
    conn = get_db_connection()
    alert_rules = conn.execute("""
        SELECT * FROM alert_rules
        WHERE enabled = 1
        ORDER BY zone, metric
    """).fetchall()

    success = None
    error = None

    if request.method == "POST":
        system_name = request.form["system_name"].strip()
        callback_url = request.form["callback_url"].strip()
        alert_rule_id = request.form["alert_rule_id"]

        selected_rule = conn.execute("""
            SELECT * FROM alert_rules
            WHERE id = ? AND enabled = 1
        """, (alert_rule_id,)).fetchone()

        if selected_rule is None:
            error = "Invalid alert selection."
        else:
            conn.execute("""
                INSERT INTO external_systems (system_name, callback_url, alert_rule_id)
                VALUES (?, ?, ?)
            """, (system_name, callback_url, alert_rule_id))
            conn.commit()

            log_action(
                "REGISTER_EXTERNAL_SYSTEM",
                f"{system_name} registered for {selected_rule['metric']} alert in {selected_rule['zone']}"
            )

            success = "External system registered successfully."

            # Refresh rules/subscriptions view after insert
            alert_rules = conn.execute("""
                SELECT * FROM alert_rules
                WHERE enabled = 1
                ORDER BY zone, metric
            """).fetchall()

    conn.close()

    return render_template(
        "external_register.html",
        success=success,
        error=error,
        alert_rules=alert_rules
    )


@app.route("/admin/alerts", methods=["GET", "POST"])
def admin_alert_settings():
    conn = get_db_connection()

    if request.method == "POST":
        form_type = request.form["form_type"]

        if form_type == "update":
            rule_id = request.form["rule_id"]
            threshold = request.form["threshold"]

            conn.execute("""
                UPDATE alert_rules
                SET threshold = ?
                WHERE id = ?
            """, (threshold, rule_id))
            conn.commit()

            log_action(
                "UPDATE_ALERT_RULE",
                f"Rule {rule_id} updated: threshold={threshold}"
            )

        elif form_type == "create":
            metric = request.form["metric"].strip()
            zone = request.form["zone"].strip()
            threshold = request.form["threshold"]

            conn.execute("""
                INSERT INTO alert_rules (metric, zone, threshold, enabled)
                VALUES (?, ?, ?, 1)
            """, (metric, zone, threshold))
            conn.commit()

            log_action(
                "CREATE_ALERT_RULE",
                f"Created alert rule: metric={metric}, zone={zone}, threshold={threshold}"
            )

    rules = conn.execute("""
        SELECT * FROM alert_rules
        ORDER BY zone, metric
    """).fetchall()

    subscriptions = conn.execute("""
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

    available_metrics = ["pm25", "temperature", "humidity", "noise"]
    available_zones = ["Downtown", "West", "North", "East", "South"]

    return render_template(
        "alert_settings.html",
        rules=rules,
        subscriptions=subscriptions,
        available_metrics=available_metrics,
        available_zones=available_zones
    )


@app.route("/admin/rbac", methods=["GET", "POST"])
def admin_rbac():
    conn = get_db_connection()

    if request.method == "POST":
        user_id = request.form["user_id"]
        new_role = request.form["role"]

        conn.execute("""
            UPDATE users
            SET role = ?
            WHERE id = ?
        """, (new_role, user_id))
        conn.commit()

        log_action(
            "UPDATE_ROLE",
            f"User ID {user_id} role changed to {new_role}"
        )

    users = conn.execute("""
        SELECT * FROM users
        ORDER BY id
    """).fetchall()

    conn.close()

    return render_template("rbac.html", users=users)


@app.route("/admin/logs")
def admin_logs():
    conn = get_db_connection()

    logs = conn.execute("""
        SELECT * FROM logs
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template("logs.html", logs=logs)


if __name__ == "__main__":
    initialize_database()
    ingest_telemetry()
    app.run(host="127.0.0.1", port=8000, debug=False, use_reloader=False)