#!/usr/bin/env python3
"""Create a simple PyBryt reference and a sample student submission."""
import pybryt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
REF_DIR = BASE / 'references'
SUB_DIR = BASE / 'submissions'
REF_DIR.mkdir(exist_ok=True)
SUB_DIR.mkdir(exist_ok=True)

def make_reference():
    # simple fibonacci reference
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)

    # Newer pybryt versions require a name and annotations list on init
    # Construct ReferenceImplementation with annotations list (pybryt>=0.7 API)
    ann = pybryt.Value(fibonacci(6), name="fib_6")
    ref = pybryt.ReferenceImplementation('fib_ref', [ann])
    target = REF_DIR / 'fib_ref.pkl'
    # dump to file
    ref.dump(str(target))
    print(f"Saved reference to {target}")

def make_student_submission(correct=True):
    code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(6)
print(result)
"""
    if not correct:
        # introduce a bug: incorrect base case
        code = code.replace('if n <= 1:', 'if n == 0:')

    sub_path = SUB_DIR / 'student_001.py'
    with open(sub_path, 'w') as f:
        f.write(code)
    print(f"Wrote student submission to {sub_path}")

if __name__ == '__main__':
    make_reference()
    make_student_submission(correct=True)
