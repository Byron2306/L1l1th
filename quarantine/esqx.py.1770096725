import sys
sys.path.append('.')
from agents.ui_agent import UIAgent
# prevent starting background feed worker in constructor for test
UIAgent._feed_worker = lambda self: None
# instantiate UIAgent without coordinator
# create minimal dummy coordinator with cfg and agents so UIAgent init doesn't fail
class DummyCfg: pass
class DummyCoordinator:
    def __init__(self):
        self.cfg = DummyCfg()
        # sensible defaults used by UIAgent
        self.cfg.feed_buffer_trades = 500
        self.cfg.feed_buffer_logs = 1000
        self.agents = {}

dc = DummyCoordinator()
ui = UIAgent(coordinator=dc)
# populate buffers with sample entries
ui._trade_buffer.clear()
ui._log_buffer.clear()
for i in range(5):
    ui._trade_buffer.append({'timestamp': 1000+i, 'symbol':'ETH/USDT','side':'SELL','quantity':0.1*i,'price':2000+i})
for i in range(3):
    ui._log_buffer.append({'ts': 2000+i, 'level':'INFO','msg':f'test log {i}','agent':'test'})
# use Flask test client
c = ui.app.test_client()
r = c.get('/debug/export_buffers?limit=10')
print(r.status_code)
print(r.get_data(as_text=True))
