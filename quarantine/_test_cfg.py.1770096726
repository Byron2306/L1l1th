import sys, traceback
sys.path.append('.')
from agents.coordinator import SwarmCoordinator
from main import load_config
from agents.ui_agent import UIAgent

cfg = load_config()
coord = SwarmCoordinator(cfg)
ui = UIAgent(coord)
try:
    html = ui._render_config()
    print(html[:200])
except Exception:
    traceback.print_exc()
