#!/usr/bin/env python3
"""Run demo assessment using WorkflowEngine and the demo reference/submission."""
import json
import sys
from pathlib import Path
# Ensure project root is on sys.path when running from scripts/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from homs.core.workflow_engine import WorkflowEngine

BASE = Path(__file__).resolve().parent.parent
REF_DIR = BASE / 'references'
SUB_DIR = BASE / 'submissions'
OUT_DIR = BASE / 'output'
OUT_DIR.mkdir(exist_ok=True)

def run():
    # Load config.json, but fall back to sensible defaults if it's malformed
    try:
        with open('config.json', 'r') as f:
            cfg = json.load(f)
    except Exception:
        cfg = {
            "assessment": {"timeout": 30, "max_memory_mb": 512},
            "moderation": {"low_score_threshold": 40, "high_score_threshold": 95, "std_dev_multiplier": 2.0, "similarity_threshold": 0.85},
            "learning": {"min_samples_for_learning": 10},
            "data": {"data_dir": "./data"},
            "git": {"enabled": False, "repo_path": "."},
            "reporting": {"include_html": True, "include_csv": True},
            "output_dir": "./output"
        }
    engine = WorkflowEngine(cfg)
    # load reference
    ref = REF_DIR / 'fib_ref.pkl'
    engine.assessment_agent.load_reference('fib_ref', ref)

    # Run full workflow to produce reports and saved outputs
    summary = engine.run_complete_workflow(SUB_DIR, 'fib_ref', OUT_DIR)
    summary_path = OUT_DIR / 'workflow_summary.json'
    # Make summary JSON-serializable (convert Path objects)
    def _to_serializable(obj):
        if isinstance(obj, list):
            return [_to_serializable(v) for v in obj]
        if isinstance(obj, dict):
            return {k: _to_serializable(v) for k, v in obj.items()}
        try:
            # Path-like
            from pathlib import Path as _P
            if isinstance(obj, _P):
                return str(obj)
        except Exception:
            pass
        return obj

    serial_summary = _to_serializable(summary)
    with open(summary_path, 'w') as f:
        json.dump(serial_summary, f, indent=2)
    print(f'Workflow complete — summary written to {summary_path}')

if __name__ == '__main__':
    run()
