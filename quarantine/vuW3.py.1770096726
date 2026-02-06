#!/usr/bin/env python3
"""
Simple watchdog that ensures `tools/lilith_complete.py` is running and responsive.
- If backend not responding on /status, it will start it using the current Python executable.
- Restarts on crashes with backoff.
- Logs to tools/backend_watchdog.log
"""
import subprocess
import time
import requests
import os
import sys
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), 'backend_watchdog.log')
BACKEND_SCRIPT = os.path.join(os.path.dirname(__file__), 'lilith_complete.py')
CHECK_URL = 'http://127.0.0.1:5000/status'

def log(msg: str):
    t = datetime.utcnow().isoformat()
    line = f"[{t}] {msg}\n"
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(line)
    print(line, end='')


def is_backend_alive() -> bool:
    try:
        r = requests.get(CHECK_URL, timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def start_backend() -> subprocess.Popen:
    python = sys.executable
    log(f"Starting backend with: {python} {BACKEND_SCRIPT}")
    p = subprocess.Popen([python, BACKEND_SCRIPT], cwd=os.path.dirname(BACKEND_SCRIPT))
    log(f"Started backend PID {p.pid}")
    return p


def watchdog_loop():
    p = None
    backoff = 1
    while True:
        try:
            if is_backend_alive():
                # Backend is healthy
                backoff = 1
                time.sleep(3)
                continue

            # Start backend if not running or not healthy
            if p is None or p.poll() is not None:
                p = start_backend()
                # wait a bit for process to initialize
                time.sleep(2)

            # Wait and check for readiness
            for _ in range(20):
                if is_backend_alive():
                    log('Backend responded to health check.')
                    break
                time.sleep(1)

            if not is_backend_alive():
                log('Backend did not respond in time; terminating and retrying with backoff.')
                try:
                    if p and p.poll() is None:
                        p.terminate()
                except Exception as e:
                    log(f'Error terminating: {e}')
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
                continue

        except KeyboardInterrupt:
            log('Watchdog interrupted, exiting.')
            break
        except Exception as e:
            log(f'Watchdog encountered error: {e}')
            time.sleep(5)

if __name__ == '__main__':
    log('Starting backend watchdog...')
    watchdog_loop()