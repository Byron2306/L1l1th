import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SUB_DIR = BASE / 'submissions'
OUT_DIR = BASE / 'output'
OUT_DIR.mkdir(exist_ok=True)

results = []
for f in SUB_DIR.glob('*.py'):
    student_id = f.stem
    timestamp = None
    try:
        ns = {}
        code = f.read_text()
        exec(compile(code, str(f), 'exec'), ns)
        func = ns.get('fibonacci') or ns.get('fib') or ns.get('solve')
        if callable(func):
            tests = [(0,0),(1,1),(6,8)]
            passed = 0
            details = {}
            for inp,exp in tests:
                try:
                    out = func(inp)
                    ok = out == exp
                    details[f'test_{inp}'] = {'input': inp, 'expected': exp, 'output': out, 'passed': ok}
                    if ok:
                        passed += 1
                except Exception as e:
                    details[f'test_{inp}'] = {'input': inp, 'expected': exp, 'output': None, 'passed': False, 'error': str(e)}
            score = (passed/len(tests)) * 100
            res = {
                'student_id': student_id,
                'timestamp': '',
                'status': 'success',
                'annotations': details,
                'total_annotations': len(tests),
                'passed_annotations': passed,
                'final_score': score,
                'submission_path': str(f)
            }
        else:
            res = {'student_id': student_id, 'timestamp': '', 'status': 'error', 'error': 'no callable fibonacci/fib/solve found'}
    except Exception as e:
        res = {'student_id': student_id, 'timestamp': '', 'status': 'error', 'error': str(e)}
    results.append(res)

out_path = OUT_DIR / 'demo_assessment.json'
out_path.write_text(json.dumps(results, indent=2))
print('Wrote', out_path)

html = ['<html><head><meta charset="utf-8"><title>Fallback Report</title></head><body>','<h1>Fallback Assessment Report</h1>','<ul>']
for r in results:
    html.append(f"<li>{r['student_id']}: {r.get('final_score', r.get('error'))}</li>")
html.append('</ul></body></html>')
(OUT_DIR / 'summary_report.html').write_text('\n'.join(html))
print('Wrote', OUT_DIR / 'summary_report.html')
