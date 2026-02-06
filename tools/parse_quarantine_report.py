import json
from pathlib import Path
qdir = Path(__file__).resolve().parents[1] / 'quarantine'
files = sorted(qdir.glob('quarantine_report.*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
if not files:
    print('No quarantine report found')
    raise SystemExit(1)
fn = str(files[0])
print('report:', fn)
with open(fn, 'r', encoding='utf-8') as fh:
    j = json.load(fh)
print('timestamp:', j.get('timestamp'))
print('suspicious_processes:', sum(1 for p in j.get('processes',[]) if p.get('suspicious')))
print('suspicious_files:', len(j.get('files',[])))
actions = j.get('actions', [])
print('actions:', [list(a.keys())[0] for a in actions])
for a in actions:
    if 'quarantine' in a:
        q = a['quarantine']
        ok = sum(1 for item in q if item.get('quarantined'))
        total = len(q)
        print(f'quarantine: {ok}/{total} files quarantined')
        print('\nsample quarantined paths:')
        for item in q[:10]:
            print(item.get('path'), '->', item.get('dest'))
