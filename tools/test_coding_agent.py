import json
from lilith_full_backend import run_openclaw_skill

print('CALLING run_openclaw_skill...')
res = run_openclaw_skill('coding-agent', 'print("Hello from Pi test")', timeout=10)
print('RESULT:')
print(json.dumps(res, indent=2))
print('DONE')
