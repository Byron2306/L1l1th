import sys
sys.path.append('.')
from agents.ui_agent import UIAgent

class DummyCfg: pass
class DummyCoordinator:
    def __init__(self):
        self.cfg = DummyCfg()
        self.cfg.feed_buffer_trades = 500
        self.cfg.feed_buffer_logs = 1000
        self.agents = {}

if __name__ == '__main__':
    dc = DummyCoordinator()
    ui = UIAgent(coordinator=dc, host='127.0.0.1', port=5000)
    print('Starting Flask UI (simple runner) on http://127.0.0.1:5000')
    ui.app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
