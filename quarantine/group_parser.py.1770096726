"""Group member parsing utilities.

Extracts student names and numbers from the Assignment 2 template header.
"""
from __future__ import annotations
from pathlib import Path
import re
import zipfile
from typing import List, Dict


def _extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
    text = re.sub(r'<w:tab/>', '\t', xml)
    text = re.sub(r'</w:p>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text


def parse_group_header_from_docx(path: Path) -> Dict[str, List[str]]:
    text = _extract_docx_text(path)
    # Simple extraction by labels
    def find_after(label: str) -> List[str]:
        pattern = re.compile(re.escape(label) + r'\s*:\s*(.+)', re.IGNORECASE)
        for line in text.splitlines():
            m = pattern.search(line)
            if m:
                # split by commas or semicolons
                vals = [v.strip() for v in re.split(r'[;,]', m.group(1)) if v.strip()]
                return vals
        return []

    names = find_after('Name(s)')
    numbers = find_after('Student Number(s)')
    group_size = find_after('Group Size (Individual / Pair)')

    return {"names": names, "numbers": numbers, "group_size": group_size}
