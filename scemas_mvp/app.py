import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

from utils.resource_helper import resource_path
from abstractions.db import ensure_db
from controllers.authentication_controller import login_user
from controllers.data_management_controller import ingest_telemetry, fetch_public_data, fetch_operator_telemetry
from controllers.alert_management_controller import (
    fetch_alerts,
    fetch_all_rules,
    fetch_available_metrics,
    fetch_available_zones,
    handle_alert_form
)
from controllers.subscription_management_controller import (
    fetch_alert_rules_for_subscription,
    register_external_system,
    fetch_subscriptions
)
from controllers.role_management_controller import fetch_all_users, change_user_role
from controllers.log_management_controller import fetch_logs

app = Flask(
    __name__,
    template_folder=resource_path("templates"),
    static_folder=resource_path("static")
)

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = login_user(request.form["username"])
        if not user:
            return render_template("login.html", error="Invalid username")

        if user["role"] == "public":
            return redirect(url_for("public_dashboard"))
        elif user["role"] == "operator":
            return redirect(url_for("operator_dashboard"))
        elif user["role"] == "admin":
            return redirect(url_for("admin_dashboard"))

    return render_template("login.html")

@app.route("/public")
def public_dashboard():
    rows = fetch_public_data()
    return render_template(
        "public_dashboard.html",
        rows=rows,
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.route("/public/register", methods=["GET", "POST"])
def external_register():
    success = None
    error = None

    if request.method == "POST":
        ok, message = register_external_system(request.form)
        if ok:
            success = message
        else:
            error = message

    alert_rules = fetch_alert_rules_for_subscription()
    return render_template(
        "external_register.html",
        alert_rules=alert_rules,
        success=success,
        error=error
    )

@app.route("/operator")
def operator_dashboard():
    telemetry = fetch_operator_telemetry()
    alerts = fetch_alerts()
    return render_template(
        "operator_dashboard.html",
        telemetry=telemetry,
        alerts=alerts,
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