import json
import sqlite3
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

class DataManager:
    def __init__(self, config: Dict[str, Any]):
        self.data_dir = Path(config.get('data_dir', './data'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / 'homs.db'
        self._init_database()

    def _init_database(self):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                workflow_id TEXT PRIMARY KEY,
                timestamp TEXT,
                status TEXT,
                data_path TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_workflow_data(self, workflow_id: str, data: Dict[str, Any]):
        json_path = self.data_dir / f"{workflow_id}.json"
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO workflows VALUES (?, ?, ?, ?)
        ''', (workflow_id, datetime.now().isoformat(), 'completed', str(json_path)))
        conn.commit()
        conn.close()

    def load_workflow_data(self, workflow_id: str) -> Dict[str, Any]:
        json_path = self.data_dir / f"{workflow_id}.json"
        with open(json_path, 'r') as f:
            return json.load(f)
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

class DataManager:
    def __init__(self, config: Dict[str, Any] = None):
        cfg = config or {}
        self.data_dir = Path(cfg.get('data_dir', './data'))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / 'homs.db'
        self._init_database()

    def _init_database(self):
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                workflow_id TEXT PRIMARY KEY,
                timestamp TEXT,
                status TEXT,
                data_path TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_workflow_data(self, workflow_id: str, data: Dict[str, Any]):
        json_path = self.data_dir / f"{workflow_id}.json"
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO workflows VALUES (?, ?, ?, ?)
        ''', (workflow_id, datetime.now().isoformat(), 'completed', str(json_path)))
        conn.commit()
        conn.close()

    def load_workflow_data(self, workflow_id: str) -> Dict[str, Any]:
        json_path = self.data_dir / f"{workflow_id}.json"
        with open(json_path, 'r') as f:
            return json.load(f)
