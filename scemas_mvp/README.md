# SCEMAS MVP

A minimal proof-of-concept for the **Smart City Environmental Monitoring & Alert System (SCEMAS)**.

This application is a lightweight Flask-based MVP that demonstrates the main system flows using:
- Flask
- SQLite
- HTML/CSS
- mock telemetry data from JSON

The app reads fake telemetry from a JSON file, stores it in the database, generates alerts from threshold rules, and provides separate public, operator, and admin views.

---

# Features

## Public
- View aggregated environmental data
- Register an external system for alert subscriptions

## Operator
- View recent telemetry
- View triggered alerts

## Admin
- Create new alert rules
- Update alert thresholds
- View which external systems are subscribed to each alert
- Manage RBAC roles
- View system logs

---

# Tech Stack

- **Backend:** Flask
- **Database:** SQLite
- **Frontend:** Jinja templates + HTML/CSS
- **Mock data source:** JSON
- **Packaging:** PyInstaller

---


# 1. Developer Environment Setup

## Step 1: Clone the repository

```bash
git clone <your-repo-url>
cd scemas_mvp
```

## Step 2: Create a virtual environment

### macOS / Linux
```bash
python3 -m venv venv
```

### Windows
```bash
python -m venv venv
```

## Step 3: Activate the virtual environment

### macOS / Linux
```bash
source venv/bin/activate
```

### Windows
```bash
venv\Scripts\activate
```

After activation, the terminal should show `(venv)`.

## Step 4: Upgrade pip

```bash
pip install --upgrade pip
```

## Step 5: Install dependencies

```bash
pip install -r requirements.txt
```

## Step 6: Install PyInstaller for packaging

```bash
pip install pyinstaller
```

If desired, add it to `requirements.txt` too:

```txt
Flask==3.0.3
pyinstaller==6.10.0
```

Then run:

```bash
pip install -r requirements.txt
```

---

# 2. Initialize the Database

Before running the app for the first time, initialize the SQLite database.

```bash
python init_db.py
```

This creates the database file `scemas.db` and seeds:
- demo users
- initial alert rules
- required tables

---

# 3. Run the App Locally

Start the Flask app with:

```bash
python app.py
```

Then open this in the browser:

```text
http://localhost:8000/login
```

---

# 4. Demo Login Accounts

Use these usernames on the login page:

- `public`
- `operator`
- `admin`

These are demo accounts stored in the seeded database.

---

# 5. Typical Local Development Workflow

Each time a developer wants to work on the app:

## Step 1
Open terminal in the project folder:

```bash
cd scemas_mvp
```

## Step 2
Activate the virtual environment:

### macOS / Linux
```bash
source venv/bin/activate
```

### Windows
```bash
venv\Scripts\activate
```

## Step 3
Run the app:

```bash
python app.py
```

## Step 4
Open the browser:

```text
http://localhost:8000/login
```

---

# 6. Reset the Database

If the database becomes messy during testing, delete and recreate it.

### macOS / Linux
```bash
rm scemas.db
python init_db.py
```

### Windows
```bash
del scemas.db
python init_db.py
```

Then run the app again:

```bash
python app.py
```

---

# 7. How the App Works

## Telemetry
The app reads from `telemetry.json` and inserts telemetry into SQLite on startup.

## Alert Generation
When telemetry is ingested, each telemetry value is checked against alert rules in the database. If the threshold is exceeded, an alert record is created.

## External System Registration
External systems can register through the public page and subscribe to a selected alert rule from a database-populated dropdown.

## Role Management
Admin users can update user roles through the RBAC page.

## Logs
System actions such as ingestion, role updates, alert rule updates, and external registrations are stored in the logs table.

---

# 8. Packaging the App into an Executable

This project can be packaged into a standalone executable using **PyInstaller**.

## Important note
The current app is a Flask web app. Packaging it into an executable means:
- the executable starts the Flask server locally
- the user still opens the app in a browser
- the browser points to the local server address

This is acceptable for a proof-of-concept desktop-distributed demo.

---

# 9. Create the Executable

## Step 1: Make sure PyInstaller is installed

```bash
pip install pyinstaller
```

## Step 2: Build the executable

Run this from the project root:

### macOS / Linux
```bash
pyinstaller --onefile --add-data "templates:templates" --add-data "static:static" --add-data "telemetry.json:." app.py
```

### Windows
```bash
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" --add-data "telemetry.json;." app.py
```

## What this does
It creates:
- a `build/` folder
- a `dist/` folder
- a packaged executable inside `dist/`

---

# 10. Running the Packaged Executable

After packaging, go into the `dist` folder.

### macOS / Linux
```bash
cd dist
./app
```

### Windows
```bash
cd dist
app.exe
```

After running it, open:

```text
http://localhost:8000/login
```

If the executable launches successfully, the Flask app will be served locally and the browser can connect to it.

---


# 15. Recommended Commands Summary

## First-time setup

```bash
git clone <your-repo-url>
cd scemas_mvp
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
python init_db.py
python app.py
```

Open:

```text
http://localhost:8000/login
```

## Daily development run

```bash
cd scemas_mvp
source venv/bin/activate
python app.py
```

## Reset DB

```bash
rm scemas.db
python init_db.py
```

## Build executable

### macOS / Linux
```bash
pyinstaller --onefile --add-data "templates:templates" --add-data "static:static" --add-data "telemetry.json:." app.py
```

### Windows
```bash
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" --add-data "telemetry.json;." app.py
```

## Run executable

### macOS / Linux
```bash
cd dist
./app
```

### Windows
```bash
cd dist
app.exe
```

Then open:

```text
http://localhost:8000/login
```

---
