# Staff Payment Portal

Production-ready payroll management system with FastAPI + SQLite + responsive frontend.

## Works on Windows, Linux, and macOS

After cloning from GitHub, setup is automatic using one cross-platform script.

## Quick Start

1. Install Python 3.10+ and Git
2. Clone repo
3. Run setup:

Windows:

```bat
start.bat
```

Linux/macOS:

```bash
python3 setup.py start
```

macOS double-click option:

- Double-click `setup.command`

Stop server:

Windows:

```bat
stop.bat
```

Linux/macOS:

```bash
python3 setup.py stop
```

## Optional: Docker (all platforms)

If Docker Desktop/Engine is installed:

```bash
docker compose up -d
```

Stop:

```bash
docker compose down
```

## What setup does automatically

- create virtual environment (`.venv`)
- install dependencies from `backend/requirements.txt`
- stop old process on port 8000 (if running)
- start FastAPI backend
- auto-create SQLite DB (`backend/staff_payment.db`) on first run
- auto-create default admin on first run
- open browser to login page

## URLs

- App login: `http://localhost:8000/login.html`
- API docs: `http://localhost:8000/docs`

## Default login

- Email: `admin@staff.com`
- Password: `admin123`

## Project structure

```
staff-payment-portal/
├── backend/
│   ├── auth.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── requirements.txt
├── frontend/
├── start.bat
├── stop.bat
├── setup.py
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Notes

- `backend/staff_payment.db` is ignored in Git to keep repository clean.
- New laptop gets a fresh local DB automatically.
