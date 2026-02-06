import json
from sterilize import Sterilizer
s = Sterilizer()
report = {'processes': s.scan_processes(), 'files': s.scan_files()}
print(json.dumps(report, indent=2))
