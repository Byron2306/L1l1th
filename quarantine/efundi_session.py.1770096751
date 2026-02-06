"""Create or refresh an efundi session (storage state) for Playwright."""
from pathlib import Path
import json
from homs.integrations.efundi import EfundiClient

CONFIG_PATH = Path("config.json")

if CONFIG_PATH.exists():
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        cfg = {}
else:
    cfg = {}

base_url = cfg.get("efundi", {}).get("base_url", "https://efundi.nwu.ac.za")
storage_state = cfg.get("efundi", {}).get("storage_state", "./data/efundi_state.json")

client = EfundiClient(base_url=base_url, storage_state_path=Path(storage_state), headless=False)
client.interactive_login_and_save()
