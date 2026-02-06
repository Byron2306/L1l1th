"""Feedback packaging utilities.

Create per-student feedback files and efundi-compatible zip for upload.
"""
from __future__ import annotations
from pathlib import Path
import json
import zipfile
import csv
import io
import re
from typing import Dict, Any, List, Iterable, Tuple, Optional


def write_feedback_files(results: List[Dict[str, Any]], out_dir: Path) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for r in results:
        sid = r.get('student_id', 'unknown')
        p = out_dir / f"{sid}_feedback.json"
        p.write_text(json.dumps(r, indent=2), encoding='utf-8')
        files.append(p)
    return files


def zip_feedback(files: List[Path], zip_path: Path) -> Path:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, arcname=f.name)
    return zip_path


# --- eFundi/Sakai packaging helpers ---
_STUDENT_ID_RE = re.compile(r"\((\d{5,})\)")


def extract_student_id(folder_name: str) -> Optional[str]:
    """Extract student id from a folder name like 'SURNAME, NAME(12345678)'."""
    m = _STUDENT_ID_RE.search(folder_name)
    return m.group(1) if m else None


def update_grades_csv(csv_bytes: bytes, grades_map: Dict[str, Any]) -> bytes:
    """Update grades.csv content with new grades keyed by student id.

    Preserves the leading two metadata lines and rewrites the data rows.
    """
    text = csv_bytes.decode("utf-8-sig", errors="replace")
    lines = text.splitlines()
    if len(lines) < 3:
        return csv_bytes

    prefix = lines[:2]
    header = lines[2]
    data_lines = lines[3:]

    reader = csv.DictReader([header] + data_lines)
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=reader.fieldnames, lineterminator="\r\n")
    writer.writeheader()
    for row in reader:
        sid = (row.get("ID") or row.get("Display ID") or "").strip()
        if sid in grades_map:
            row["grade"] = str(grades_map[sid])
        writer.writerow(row)

    updated = "\r\n".join(prefix) + "\r\n" + out.getvalue().rstrip("\r\n") + "\r\n"
    return updated.encode("utf-8-sig")


def repackage_efundi_zip(
    download_zip: Path,
    output_zip: Path,
    grades_map: Dict[str, Any],
    feedback_files: Dict[str, Iterable[Path]] | None = None,
    comments_map: Dict[str, str] | None = None,
) -> Path:
    """Repackage a downloaded eFundi assignment zip for Upload All.

    - Preserves the original structure
    - Updates grades.csv at the root
    - Injects feedback files into each student's 'Feedback Attachment(s)' folder
    - Writes comments.txt per student when provided
    """
    feedback_files = feedback_files or {}
    comments_map = comments_map or {}

    download_zip = Path(download_zip)
    output_zip = Path(output_zip)
    output_zip.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(download_zip, 'r') as zin, zipfile.ZipFile(
        output_zip, 'w', compression=zipfile.ZIP_DEFLATED
    ) as zout:
        names = zin.namelist()
        # Root folder is the first segment of any entry
        root = names[0].split('/')[0] if names else ""

        for name in names:
            data = zin.read(name)
            # Update grades.csv
            if name.endswith("/grades.csv"):
                data = update_grades_csv(data, grades_map)
                zout.writestr(name, data)
                continue
            # Skip comments.txt if we will write a new one later
            if name.endswith("/comments.txt"):
                folder = name.rsplit("/", 1)[0]
                student_folder = folder.split("/")[-1]
                sid = extract_student_id(student_folder)
                if sid and sid in comments_map:
                    continue
            # Otherwise preserve original file
            zout.writestr(name, data)

        # Add/replace comments.txt and feedback attachments
        for student_folder, files in feedback_files.items():
            sid = extract_student_id(student_folder)
            if not sid:
                continue
            base = f"{root}/{student_folder}"
            fb_dir = f"{base}/Feedback Attachment(s)"
            # ensure directory entry
            zout.writestr(fb_dir + "/", b"")
            for f in files:
                f = Path(f)
                if f.exists():
                    zout.write(f, arcname=f"{fb_dir}/{f.name}")

        for sid, comment in comments_map.items():
            # find student folder name by id in existing zip
            student_folder = None
            for name in names:
                if name.startswith(root + "/"):
                    parts = name[len(root) + 1 :].split("/")
                    if parts and parts[0]:
                        if extract_student_id(parts[0]) == sid:
                            student_folder = parts[0]
                            break
            if student_folder:
                path = f"{root}/{student_folder}/comments.txt"
                zout.writestr(path, comment)

    return output_zip
