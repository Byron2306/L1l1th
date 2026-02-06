import inspect
import pybryt
from pathlib import Path
out = Path('scripts/studentimpl_source.txt')
try:
    src = inspect.getsource(pybryt.StudentImplementation)
except Exception as e:
    src = f'error getting source: {e}'
out.write_text(src)
print('wrote', out)
