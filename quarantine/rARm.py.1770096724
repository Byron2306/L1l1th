from pathlib import Path
import sys
from pathlib import Path as P
# ensure project root on sys.path
ROOT = P(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from homs.core.workflow_engine import WorkflowEngine
import homs.core.assessment_agent as _aa
import inspect
print('assessment_agent module file:', getattr(_aa, '__file__', None))
print('assessment_agent source snippet:')
print('\n'.join(inspect.getsource(_aa).splitlines()[:40]))
import json

cfg = {
    "assessment": {"timeout": 30, "max_memory_mb": 512},
    "git": {"enabled": False}
}
engine = WorkflowEngine(cfg)
engine.assessment_agent.load_reference('fib_ref', Path('references/fib_ref.pkl'))
res = engine.assessment_agent.assess_submission(Path('submissions/student_001.py'), 'fib_ref', 'student_001')
print('RESULT:')
print(json.dumps(res, indent=2))
