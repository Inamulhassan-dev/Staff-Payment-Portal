# Staff Payment Portal

Production-ready payroll management system with FastAPI + SQLite and responsive frontend pages.

## Clone and Run (Recommended)

### Prerequisites

1. Python 3.10+
2. Git
3. Internet connection for first-time dependency install

### 1) Clone

```bash
git clone https://github.com/Inamulhassan-dev/Staff-Payment-Portal.git
cd Staff-Payment-Portal
```

### 2) Configure environment (optional)

Copy the example env file and edit values if needed:

```bash
cp .env.example .env
```

> **Important for production**: open `.env` and replace `SECRET_KEY` with a
> strong random string. You can generate one with:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

The app works out-of-the-box with the defaults (SQLite DB, auto-created on
first run), so this step is optional for local development.

### 3) Start

Windows (first-time setup):

```bat
setup.bat
```

Windows (normal start after first setup):

```bat
start.bat
```

Linux/macOS:

```bash
python3 setup.py start
```

macOS double-click option:

1. Double-click `setup.command`

### 4) Stop

Windows:

```bat
stop.bat
```

Linux/macOS:

```bash
python3 setup.py stop
```


## What Setup Does Automatically

1. Creates virtual environment `.venv` (if missing)
2. Upgrades `pip`
3. Installs packages from `backend/requirements-lock.txt` (or `requirements.txt` as fallback)
4. Stops old process on port `8000` (if any)
5. Starts FastAPI backend
6. Auto-creates SQLite DB on first run
7. Auto-creates default admin on first run
8. Opens login page in browser

## App URLs

1. Login: `http://localhost:8000/login.html`
2. API docs: `http://localhost:8000/docs`

## Default Admin Login

1. Email: `admin@staff.com`
2. Password: `admin123`

## Optional: Docker

Start:

```bash
docker compose up -d
```

Stop:

```bash
docker compose down
```

## Troubleshooting

### Python not found

1. Install Python 3.10+ from python.org.
2. During install, enable "Add Python to PATH".
3. Reopen terminal and run setup again.

### Port 8000 already in use

1. Run `stop.bat`.
2. Run `start.bat` again.

### Dependencies fail to install

1. Check internet connection.
2. Run `setup.bat` again.

### Fresh reset of local app data

Delete local files and run setup again:

1. `.venv/`
2. `staff_payment.db`
3. `backend/staff_payment.db` (if present)

## Notes

1. Runtime files (DB/logs/venv) are not meant for Git commits.
2. New machines get fresh local DB automatically at first run.
