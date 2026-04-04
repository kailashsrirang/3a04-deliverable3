import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_limiter import Limiter

from utils.resource_helper import resource_path
from abstractions.db import ensure_db
from controllers.authentication_controller import login_user
from controllers.data_management_controller import ingest_telemetry, fetch_public_data, fetch_operator_telemetry
from controllers.alert_management_controller import (
    fetch_alerts,
    fetch_all_rules,
    fetch_available_metrics,
    fetch_available_zones,
    handle_alert_form,
    acknowledge_alert,
    resolve_alert
)
from controllers.subscription_management_controller import (
    fetch_alert_rules_for_subscription,
    register_external_system,
    fetch_subscriptions,
    delete_external_subscription
)
from controllers.role_management_controller import fetch_all_users, change_user_role
from controllers.log_management_controller import fetch_logs

app = Flask(
    __name__,
    template_folder=resource_path("templates"),
    static_folder=resource_path("static")
)

limiter = Limiter(app=app)

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = login_user(request.form["username"], request.form["access_code"])
        if not user:
            return render_template("login.html", error="Invalid enterprise ID or access code")

        if user["role"] == "public":
            return redirect(url_for("public_dashboard"))
        elif user["role"] == "operator":
            return redirect(url_for("operator_dashboard"))
        elif user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))

    return render_template("login.html")
@limiter.limit("30 per minute")

@app.route("/public")
def public_dashboard():
    rows, summaries = fetch_public_data()
    return render_template(
        "public_dashboard.html",
        rows=rows,
        summaries=summaries,
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@limiter.limit("10 per minute")
@app.route("/public/register", methods=["GET", "POST"])
def external_register():
    success = None
    error = None

    if request.method == "POST":
        if "system_name" in request.form:  # Registration
            ok, message = register_external_system(request.form)
            if ok:
                success = message
            else:
                error = message
        elif "delete_system_id" in request.form:  # Deletion
            ok, message = delete_external_subscription(int(request.form["delete_system_id"]))
            if ok:
                success = message
            else:
                error = message

    alert_rules = fetch_alert_rules_for_subscription()
    subscriptions = fetch_subscriptions()
    return render_template(
        "external_register.html",
        alert_rules=alert_rules,
        subscriptions=subscriptions,
        success=success,
        error=error
    )

@app.route("/operator")
def operator_dashboard():
    telemetry = fetch_operator_telemetry()
    alerts = fetch_alerts()
    subscriptions = fetch_subscriptions()
    active_alerts_count = len([a for a in alerts if a['status'] == 'active'])
    total_telemetry = len(telemetry)
    latest_timestamp = max((t['timestamp'] for t in telemetry), default=None)
    total_subscriptions = len([s for s in subscriptions if s.get('system_id')])
    # For chart: counts of alerts by status
    status_counts = {}
    for a in alerts:
        status = a['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    return render_template(
        "operator_dashboard.html",
        telemetry=telemetry,
        alerts=alerts,
        subscriptions=subscriptions,
        active_alerts_count=active_alerts_count,
        total_telemetry=total_telemetry,
        latest_timestamp=latest_timestamp,
        total_subscriptions=total_subscriptions,
        status_counts=status_counts,
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.route("/admin")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@app.route("/admin/alerts", methods=["GET", "POST"])
def admin_alert_settings():
    if request.method == "POST":
        handle_alert_form(request.form)

    return render_template(
        "alert_settings.html",
        rules=fetch_all_rules(),
        subscriptions=fetch_subscriptions(),
        available_metrics=fetch_available_metrics(),
        available_zones=fetch_available_zones()
    )

@app.route("/admin/rbac", methods=["GET", "POST"])
def admin_rbac():
    if request.method == "POST":
        change_user_role(request.form["user_id"], request.form["role"])

    return render_template("rbac.html", users=fetch_all_users())

@app.route("/admin/logs")
def admin_logs():
    return render_template("logs.html", logs=fetch_logs())

if __name__ == "__main__":
    ensure_db()
    ingest_telemetry()
    app.run(host="0.0.0.0", port=8000, debug=True)