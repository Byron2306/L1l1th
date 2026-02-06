import os
import sys
import time
import subprocess
import signal
from datetime import datetime


LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
LOG_DIR = os.path.abspath(LOG_DIR)
UI_SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'run_ui_server.py')


def ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def log(msg: str):
    ensure_log_dir()
    ts = datetime.utcnow().isoformat() + 'Z'
    line = f"[{ts}] {msg}\n"
    with open(os.path.join(LOG_DIR, 'ui_supervisor.log'), 'a', encoding='utf8') as f:
        f.write(line)
    print(line, end='')


def start_child():
    ensure_log_dir()
    child_out = open(os.path.join(LOG_DIR, 'ui_child.log'), 'a', encoding='utf8')
    cmd = [sys.executable, UI_SCRIPT]
    log(f"Starting UI child: {cmd}")
    p = subprocess.Popen(cmd, stdout=child_out, stderr=subprocess.STDOUT)
    return p


def main():
    backoff = 1
    max_backoff = 30
    child = None

    def handle_term(signum, frame):
        log(f"Supervisor received signal {signum}, shutting down")
        if child and child.poll() is None:
            try:
                child.terminate()
            except Exception:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_term)
    try:
        signal.signal(signal.SIGTERM, handle_term)
    except Exception:
        pass

    while True:
        try:
            child = start_child()
            # wait for process to exit
            rc = child.wait()
            log(f"UI child exited with code {rc}")
            if rc == 0:
                log("UI child exited cleanly (0). Not restarting.")
                break
            # non-zero -> restart with backoff
            log(f"Restarting UI child after {backoff}s backoff")
            time.sleep(backoff)
            backoff = min(max_backoff, backoff * 2)
        except KeyboardInterrupt:
            log("Supervisor interrupted by user (KeyboardInterrupt), shutting down")
            if child and child.poll() is None:
                try:
                    child.terminate()
                except Exception:
                    pass
            break
        except Exception as e:
            log(f"Supervisor encountered exception: {e}")
            time.sleep(min(max_backoff, backoff))
            backoff = min(max_backoff, backoff * 2)


if __name__ == '__main__':
    main()
