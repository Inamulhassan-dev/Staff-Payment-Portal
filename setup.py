import os
import platform
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
BACKEND_MAIN = ROOT / "backend" / "main.py"
REQUIREMENTS = ROOT / "backend" / "requirements.txt"
APP_URL = "http://localhost:8000/login.html"
DOCS_URL = "http://localhost:8000/docs"


def is_windows() -> bool:
    return platform.system().lower().startswith("win")


def venv_python() -> Path:
    if is_windows():
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, check=True)


def create_venv_if_needed():
    py = venv_python()
    if py.exists():
        return
    print("[1/4] Creating virtual environment...")
    run([sys.executable, "-m", "venv", str(VENV_DIR)])


def install_deps():
    py = str(venv_python())
    print("[2/4] Installing dependencies...")
    run([py, "-m", "pip", "install", "--upgrade", "pip"])
    run([py, "-m", "pip", "install", "-r", str(REQUIREMENTS)])


def is_port_open(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.4)
    try:
        return s.connect_ex(("127.0.0.1", port)) == 0
    finally:
        s.close()


def stop_by_port(port: int = 8000):
    print("Stopping old server on port 8000 (if running)...")
    try:
        if is_windows():
            out = subprocess.check_output(
                ["cmd", "/c", f"netstat -ano | findstr :{port}"],
                stderr=subprocess.STDOUT,
                text=True,
            )
            pids = set()
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 5 and f":{port}" in line:
                    pids.add(parts[-1])
            for pid in pids:
                subprocess.run(["taskkill", "/F", "/PID", pid], check=False)
        else:
            out = subprocess.check_output(["lsof", "-ti", f"tcp:{port}"], text=True)
            for pid in set(out.split()):
                subprocess.run(["kill", "-9", pid], check=False)
    except Exception:
        pass


def start_backend():
    print("[3/4] Starting backend...")
    py = str(venv_python())
    log_file = ROOT / "backend" / "server.log"
    log_handle = open(log_file, "a", encoding="utf-8")

    if is_windows():
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        subprocess.Popen(
            [py, str(BACKEND_MAIN)],
            cwd=str(ROOT),
            stdout=log_handle,
            stderr=log_handle,
            creationflags=flags,
        )
    else:
        subprocess.Popen(
            [py, str(BACKEND_MAIN)],
            cwd=str(ROOT),
            stdout=log_handle,
            stderr=log_handle,
            start_new_session=True,
        )


def wait_until_up(timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(DOCS_URL, timeout=1):
                return True
        except Exception:
            time.sleep(0.5)
    return False


def start():
    print("========================================")
    print("  Staff Payment Portal - Starting")
    print("========================================")

    create_venv_if_needed()
    install_deps()
    stop_by_port(8000)
    start_backend()

    print("[4/4] Waiting for server...")
    if wait_until_up():
        print("Server running: http://localhost:8000")
        print("API docs: http://localhost:8000/docs")
        print("Default login: admin@staff.com / admin123")
        webbrowser.open(APP_URL)
    else:
        print("Server did not start in time. Check backend/server.log")


def stop():
    stop_by_port(8000)
    print("Done.")


if __name__ == "__main__":
    action = "start"
    if len(sys.argv) > 1:
        action = sys.argv[1].strip().lower()

    if action == "stop":
        stop()
    else:
        start()
