import json
from sterilize import Sterilizer

s = Sterilizer()
print('Running sterilizer: quarantine (confirm=True)')
report = s.run(dry_run=False, confirm=True, kill=False, quarantine=True)
with open('quarantine_report.json','w', encoding='utf-8') as f:
    f.write(json.dumps(report, indent=2))
print('Report written to quarantine_report.json')
