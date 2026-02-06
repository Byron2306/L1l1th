"""Extract eFundi Download All zip into output/sample_submissions.

Copies each student's 'Submission attachment(s)' folder into output/sample_submissions/<Student Folder>/.
"""
from __future__ import annotations
from pathlib import Path
import zipfile
import shutil

ZIP_PATH = Path(r"C:\Users\User\Downloads\Assignment 1 - UTEW221 V 2023_20260130115026.zip")
BASE = Path(__file__).resolve().parents[1]
OUT_ROOT = BASE / "output" / "sample_submissions"


def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    if not ZIP_PATH.exists():
        raise SystemExit(f"Zip not found: {ZIP_PATH}")

    with zipfile.ZipFile(ZIP_PATH) as z:
        names = z.namelist()
        # find root folder
        root = names[0].split("/")[0] if names else ""
        for name in names:
            # only submission attachments
            if "/Submission attachment(s)/" not in name:
                continue
            # skip directory entries
            if name.endswith("/"):
                continue
            # name: <root>/<student_folder>/Submission attachment(s)/<file>
            parts = name.split("/")
            if len(parts) < 4:
                continue
            student_folder = parts[1]
            rel_path = Path(*parts[2:])  # Submission attachment(s)/file
            target_dir = OUT_ROOT / student_folder
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / rel_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with z.open(name) as src, open(target_path, "wb") as dst:
                shutil.copyfileobj(src, dst)

    print(f"Extracted submissions to: {OUT_ROOT}")


if __name__ == "__main__":
    main()
