import pybryt
import json
from pathlib import Path

out = Path('scripts/pybryt_probe.json')
data = {
    'version': getattr(pybryt, '__version__', 'n/a'),
    'has_StudentImplementation': hasattr(pybryt, 'StudentImplementation'),
    'has_StudentCode': hasattr(pybryt, 'StudentCode'),
    'names': [n for n in dir(pybryt) if 'Student' in n or 'Reference' in n or 'Value' in n]
}
out.write_text(json.dumps(data, indent=2))
print('wrote', out)
