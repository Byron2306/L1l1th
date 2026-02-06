import zipfile
from pathlib import Path

zpath = Path(r"C:\Users\User\Downloads\Assignment 1 - UTEW221 V 2023_20260130115026.zip")
with zipfile.ZipFile(zpath) as z:
    names = z.namelist()
print("total", len(names))
for n in names[:200]:
    print(n)
