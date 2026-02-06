"""Rubric parsing utilities for HOMS.

Supports simple DOCX (docx text extraction) and PDF (best-effort).
Produces internal rubric dict format used by AssessmentAgent.
"""
from __future__ import annotations
from pathlib import Path
import re
import zipfile
from typing import Dict, Any, List, Tuple


def _extract_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml').decode('utf-8', errors='ignore')
    text = re.sub(r'<w:tab/>', '\t', xml)
    text = re.sub(r'</w:p>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text


def _parse_simple_rubric_blocks(text: str) -> List[Tuple[str, float]]:
    """Parse lines like 'Introduction and context [15]' into (name, weight)."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    out = []
    for l in lines:
        m = re.match(r'^(.*)\[(\d+)\]$', l)
        if m:
            name = m.group(1).strip()
            weight = float(m.group(2))
            out.append((name, weight))
    return out


def rubric_from_docx(path: Path) -> Dict[str, Any]:
    text = _extract_docx_text(path)
    items = _parse_simple_rubric_blocks(text)
    rubric: Dict[str, Any] = {}
    for name, weight in items:
        rubric[name] = {"weight": weight, "annotations": []}
    return rubric


def rubric_from_assignment1_docx(path: Path) -> Dict[str, Any]:
    """Handles the detailed rubric layout in Individual Assignment 1 doc.
    Extracts major criteria + weights from the 'Marks will be awarded as follows' list.
    """
    text = _extract_docx_text(path)
    rubric: Dict[str, Any] = {}
    # Find the marks list block
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # Example: "1 Biographical issues (Harvard style) 6 marks"
    for l in lines:
        m = re.match(r'^\d+\s+(.+?)\s+(\d+)\s+marks?$', l, re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            weight = float(m.group(2))
            rubric[name] = {"weight": weight, "annotations": []}
    return rubric


def save_rubric(rubric: Dict[str, Any], out_path: Path) -> Path:
    import json
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rubric, indent=2), encoding='utf-8')
    return out_path
