import os, sys, sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
    db_path = os.path.join(os.path.dirname(sys.executable), 'scemas.db')
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'scemas.db')

dist_dir = os.path.join(base_dir, 'dist')
app = Flask(__name__, static_folder=os.path.join(dist_dir, 'assets'), template_folder=dist_dir)
CORS(app)

def init_db():
    with sqlite3.connect(db_path) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS telemetry
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, sensor_type TEXT, value REAL, x REAL, y REAL, zone TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS alerts
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, sensor_type TEXT, value REAL, message TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS thresholds
                        (sensor_type TEXT PRIMARY KEY, min_val REAL, max_val REAL)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS logs
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, event_type TEXT, message TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, role TEXT, is_editable INTEGER)''')
        
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM thresholds")
        if cur.fetchone()[0] == 0:
            defaults = [("TEMPERATURE", -15.0, 35.0), ("NOISE", 0.0, 85.0), ("AIR_QUALITY", 0.0, 50.0)]
            conn.executemany("INSERT INTO thresholds (sensor_type, min_val, max_val) VALUES (?, ?, ?)", defaults)
            
        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            default_users = [("admin", "ADMIN", 0), ("operator", "OPERATOR", 0), ("public", "PUBLIC", 0)]
            conn.executemany("INSERT INTO users (username, role, is_editable) VALUES (?, ?, ?)", default_users)

def calculate_zone(x, y):
    col = min(3, int((x + 1000) // 500))
    row = min(3, int((y + 1000) // 500))
    cols = ['A', 'B', 'C', 'D']
    return f"{cols[col]}{row + 1}"

class LogController:
    @staticmethod
    def log_event(event_type, message):
        timestamp = datetime.now().strftime("%I:%M:%S %p")
        with sqlite3.connect(db_path) as conn:
            conn.execute("INSERT INTO logs (timestamp, event_type, message) VALUES (?, ?, ?)", (timestamp, event_type, message))
        print(f"[{timestamp}] [{event_type}] {message}")

class AlertController:
    @staticmethod
    def trigger_alert(sensor_type, value, zone, message):
        timestamp = datetime.now().strftime("%I:%M:%S %p")
        alert_msg = f"CRITICAL: {sensor_type} Alert in Zone {zone}! {message}"
        with sqlite3.connect(db_path) as conn:
            conn.execute("INSERT INTO alerts (timestamp, sensor_type, value, message) VALUES (?, ?, ?, ?)", 
                         (timestamp, sensor_type, value, alert_msg))
        LogController.log_event("ALERT", alert_msg)

class DataController:
    @staticmethod
    def store_data(sensor_type, value, x, y, zone):
        timestamp = datetime.now().strftime("%I:%M:%S %p")
        with sqlite3.connect(db_path) as conn:
            conn.execute("INSERT INTO telemetry (timestamp, sensor_type, value, x, y, zone) VALUES (?, ?, ?, ?, ?, ?)", 
                         (timestamp, sensor_type, value, x, y, zone))
            cur = conn.cursor()
            cur.execute("SELECT min_val, max_val FROM thresholds WHERE sensor_type = ?", (sensor_type.upper(),))
            row = cur.fetchone()

        LogController.log_event("DATA", f"Stored {sensor_type} data: {value} in {zone}")
        
        if row:
            min_val, max_val = row[0], row[1]
            if value > max_val:
                AlertController.trigger_alert(sensor_type, value, zone, f"Value ({value}) > MAX ({max_val})")
            elif value < min_val:
                AlertController.trigger_alert(sensor_type, value, zone, f"Value ({value}) < MIN ({min_val})")

    @staticmethod
    def get_aggregated_data():
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT zone, sensor_type, value 
                FROM (
                    SELECT zone, sensor_type, value, ROW_NUMBER() OVER (PARTITION BY zone, sensor_type ORDER BY id DESC) as rn 
                    FROM telemetry
                ) WHERE rn <= 5
            """).fetchall()

        zones = [f"{c}{r}" for c in "ABCD" for r in range(1, 5)]
        results = []
        for z in zones:
            z_rows = [r for r in rows if r['zone'] == z]
            if not z_rows: continue
                
            temps = [r['value'] for r in z_rows if r['sensor_type'] == 'TEMPERATURE']
            noises = [r['value'] for r in z_rows if r['sensor_type'] == 'NOISE']
            aqis = [r['value'] for r in z_rows if r['sensor_type'] == 'AIR_QUALITY']
            
            results.append({
                "zone": z,
                "TEMPERATURE": round(sum(temps)/len(temps), 2) if temps else "N/A",
                "NOISE": round(sum(noises)/len(noises), 2) if noises else "N/A",
                "AIR_QUALITY": round(sum(aqis)/len(aqis), 2) if aqis else "N/A"
            })
        return results

class DataValidatorController:
    @staticmethod
    def validate_data(sensor_type, value, x, y):
        try:
            val, px, py = float(value), float(x), float(y)
            if not (-1000 <= px <= 1000) or not (-1000 <= py <= 1000):
                return False, None, "X and Y coordinates must be between -1000 and 1000."
            
            # NEW: Strict Bounds Checking
            if sensor_type == 'AIR_QUALITY' and not (0 <= val <= 500):
                return False, None, "AQI must be between 0 and 500."
            if sensor_type == 'TEMPERATURE' and val < -273:
                return False, None, "Temperature cannot be below absolute zero (-273 °C)."
            if sensor_type == 'NOISE' and val < 0:
                return False, None, "Noise (dB) cannot be less than 0."
                
            return True, (val, px, py), ""
        except ValueError:
            return False, None, "Invalid number format."

# --- API ROUTES ---
@app.route('/api/auth/login', methods=['POST'])
def login():
    username = request.json.get('username', '').lower()
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("SELECT role FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        
    if row:
        LogController.log_event("AUTH", f"User '{username}' logged in.")
        return jsonify({"success": True, "token": f"TOKEN-{username}", "role": row[0]})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/data/public', methods=['GET'])
def get_public_data():
    return jsonify({"aggregated_telemetry": DataController.get_aggregated_data()})

@app.route('/api/data/ingest', methods=['POST'])
def ingest_data():
    data = request.json
    sensor_type = data.get('type', 'UNKNOWN').upper()
    
    # Passing sensor_type into the validator
    is_valid, parsed_data, err_msg = DataValidatorController.validate_data(sensor_type, data.get('value'), data.get('x'), data.get('y'))
    
    if is_valid:
        val, x, y = parsed_data
        zone = calculate_zone(x, y)
        DataController.store_data(sensor_type, val, x, y, zone)
        return jsonify({"success": True, "message": f"Data stored in Zone {zone}."})
    else:
        LogController.log_event("VALIDATION_ERROR", err_msg)
        return jsonify({"success": False, "message": err_msg}), 400

@app.route('/api/alerts/delete', methods=['POST'])
def delete_alert():
    data = request.json
    if data.get('role') not in ['ADMIN', 'OPERATOR']: 
        return jsonify({"success": False}), 403
        
    alert_id = data.get('id')
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
    LogController.log_event("ALERT_CLEARED", f"Alert #{alert_id} resolved by {data.get('username')}.")
    return jsonify({"success": True})

@app.route('/api/thresholds/update', methods=['POST'])
def update_threshold():
    data = request.json
    if data.get('role') != 'ADMIN': return jsonify({"success": False}), 403
    sensor, min_val, max_val = data.get('sensor').upper(), float(data.get('min')), float(data.get('max'))
    with sqlite3.connect(db_path) as conn:
        conn.execute("REPLACE INTO thresholds (sensor_type, min_val, max_val) VALUES (?, ?, ?)", (sensor, min_val, max_val))
    LogController.log_event("THRESHOLD_UPDATE", f"{sensor} updated.")
    return jsonify({"success": True, "message": "Thresholds updated."})

@app.route('/api/system/wipe', methods=['POST'])
def wipe_database():
    if request.json.get('role') != 'ADMIN': return jsonify({"success": False}), 403
    with sqlite3.connect(db_path) as conn:
        for t in ["telemetry", "alerts", "logs", "thresholds"]:
            conn.execute(f"DELETE FROM {t}")
        conn.execute("DELETE FROM sqlite_sequence WHERE name IN ('telemetry', 'alerts', 'logs')")
        conn.executemany("INSERT INTO thresholds (sensor_type, min_val, max_val) VALUES (?, ?, ?)", 
                         [("TEMPERATURE", -15.0, 35.0), ("NOISE", 0.0, 85.0), ("AIR_QUALITY", 0.0, 50.0)])
    LogController.log_event("SYSTEM_WIPE", "Admin wiped database.")
    return jsonify({"success": True, "message": "Database completely wiped."})

@app.route('/api/system/wipe_telemetry', methods=['POST'])
def wipe_telemetry():
    if request.json.get('role') != 'ADMIN': return jsonify({"success": False}), 403
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM telemetry")
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'telemetry'")
    LogController.log_event("DATA_WIPE", "Admin wiped raw sensor telemetry.")
    return jsonify({"success": True, "message": "Raw sensor data wiped."})

@app.route('/api/rbac/users', methods=['GET'])
def get_users():
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        users = conn.execute("SELECT * FROM users ORDER BY id ASC").fetchall()
    return jsonify({"users": [{"id": u["id"], "username": u["username"], "role": u["role"], "is_editable": bool(u["is_editable"])} for u in users]})

@app.route('/api/rbac/add', methods=['POST'])
def add_user():
    data = request.json
    if data.get('admin_role') != 'ADMIN': return jsonify({"success": False}), 403
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("INSERT INTO users (username, role, is_editable) VALUES (?, ?, 1)", (data['username'].lower(), data['role']))
        LogController.log_event("RBAC_ADD", f"Added user '{data['username']}'.")
        return jsonify({"success": True, "message": f"User {data['username']} created!"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Username already exists."})

@app.route('/api/rbac/edit', methods=['POST'])
def edit_user():
    data = request.json
    if data.get('admin_role') != 'ADMIN': return jsonify({"success": False}), 403
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("UPDATE users SET username = ?, role = ? WHERE id = ? AND is_editable = 1", (data['username'].lower(), data['role'], data['id']))
        LogController.log_event("RBAC_EDIT", f"Edited user ID {data['id']}.")
        return jsonify({"success": True, "message": "User updated!"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Username already exists."})

@app.route('/api/rbac/delete', methods=['POST'])
def delete_user():
    data = request.json
    if data.get('admin_role') != 'ADMIN': return jsonify({"success": False}), 403
    with sqlite3.connect(db_path) as conn:
        conn.execute("DELETE FROM users WHERE id = ? AND is_editable = 1", (data['id'],))
    LogController.log_event("RBAC_DELETE", f"Deleted user ID {data['id']}.")
    return jsonify({"success": True, "message": "User deleted!"})

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        logs = conn.execute("SELECT timestamp, event_type, message FROM logs ORDER BY id ASC").fetchall()
        alerts = conn.execute("SELECT id, timestamp, message FROM alerts ORDER BY id ASC").fetchall()
        telemetry = conn.execute("SELECT timestamp, sensor_type, value, x, y, zone FROM telemetry ORDER BY id ASC").fetchall()
        thresholds = conn.execute("SELECT sensor_type, min_val, max_val FROM thresholds").fetchall()

    return jsonify({
        "logs": [f"[{l['timestamp']}] [{l['event_type']}] {l['message']}" for l in logs],
        "alerts": [{"id": a["id"], "text": f"[{a['timestamp']}] {a['message']}"} for a in alerts],
        "raw_telemetry": [{"time": t['timestamp'], "type": t['sensor_type'], "value": t['value'], "x": t['x'], "y": t['y'], "zone": t['zone']} for t in telemetry],
        "thresholds": {t['sensor_type']: {"min": t['min_val'], "max": t['max_val']} for t in thresholds}
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(dist_dir, path)):
        return send_from_directory(dist_dir, path)
    return send_from_directory(dist_dir, 'index.html')

if __name__ == '__main__':
    init_db()
    LogController.log_event("SYSTEM", "SCEMAS Backend Initialized with SQLite.")
    app.run(port=5000, debug=False)