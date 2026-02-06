import time
import threading
import logging
import argparse


class OpenClawAgent:
    """Minimal local OpenClaw agent for integration and testing.

    - Accepts a `coordinator` reference (optional) so it can publish status
      to the coordinator's `data_cache` or use existing IPC channels.
    - Implements a simple heartbeat loop and graceful stop.
    """

    def __init__(self, coordinator=None, cfg=None):
        self.coordinator = coordinator
        self.cfg = cfg or {}
        self._stop = threading.Event()
        self.thread = None

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self.run, name="OpenClawAgent", daemon=True)
        self.thread.start()

    def run(self):
        logging.info("OpenClawAgent starting")
        try:
            while not self._stop.is_set():
                # Heartbeat: publish to coordinator data cache if available
                try:
                    if self.coordinator and hasattr(self.coordinator, 'data_cache'):
                        now_ms = int(time.time() * 1000)
                        self.coordinator.data_cache['openclaw.heartbeat'] = {'ts': now_ms, 'status': 'ok'}
                except Exception:
                    logging.exception("OpenClawAgent failed to publish heartbeat")
                # TODO: replace with real agent work (network calls, strategy, etc.)
                time.sleep(float(self.cfg.get('heartbeat_sec', 5)))
        except Exception:
            logging.exception("OpenClawAgent encountered an error")
        logging.info("OpenClawAgent stopped")

    def stop(self):
        self._stop.set()
        if self.thread:
            self.thread.join(timeout=2)


def main():
    parser = argparse.ArgumentParser(description="Run OpenClawAgent standalone")
    parser.add_argument('--heartbeat', type=float, default=5.0, help='seconds between heartbeats')
    parser.add_argument('--once', action='store_true', help='run one heartbeat then exit')
    args = parser.parse_args()

    agent = OpenClawAgent(cfg={'heartbeat_sec': args.heartbeat})
    if args.once:
        try:
            # single iteration for health checks
            if hasattr(agent, 'coordinator') and agent.coordinator and hasattr(agent.coordinator, 'data_cache'):
                agent.coordinator.data_cache['openclaw.heartbeat'] = {'ts': int(time.time() * 1000), 'status': 'ok'}
            print('OpenClawAgent single heartbeat emitted')
        except Exception:
            print('OpenClawAgent single heartbeat failed')
        return

    try:
        agent.run()
    except KeyboardInterrupt:
        agent.stop()


if __name__ == '__main__':
    main()
