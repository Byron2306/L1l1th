import pybryt
from pathlib import Path
out = Path('scripts/pybryt_inspect.txt')
with open(out, 'w') as f:
    f.write('version: ' + getattr(pybryt, '__version__', 'n/a') + '\n')
    f.write('has ReferenceImplementation: ' + str(hasattr(pybryt, 'ReferenceImplementation')) + '\n')
    f.write('has Value: ' + str(hasattr(pybryt, 'Value')) + '\n')
    f.write('dir snippets:\n')
    names = [n for n in dir(pybryt) if 'Reference' in n or 'Value' in n or 'Student' in n]
    for n in names:
        f.write('  ' + n + '\n')
print('wrote', out)
