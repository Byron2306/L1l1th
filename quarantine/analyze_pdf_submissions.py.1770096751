"""Analyze PDF submissions against a rubric (best-effort, text-based).

Outputs:
- output/pdf_analysis/report.csv
- output/pdf_analysis/report.md
"""
from pathlib import Path
import csv
import re
from typing import Dict, Any, List
import sys

import PyPDF2

# ensure repo root on path
BASE = Path(__file__).resolve().parents[1]
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from homs.utils.rubric_parser import rubric_from_assignment1_docx


def extract_pdf_text(path: Path) -> str:
    reader = PyPDF2.PdfReader(str(path))
    parts = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            parts.append("")
    return "\n".join(parts)


def keywords_for_criterion(name: str) -> List[str]:
    words = re.findall(r"[A-Za-z]{4,}", name.lower())
    # remove ultra-generic words
    stop = {"and", "with", "from", "that", "this", "will", "marks", "have", "your", "into", "over", "then"}
    return [w for w in words if w not in stop]


def score_text_against_rubric(text: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
    text_lc = text.lower()
    results = {}
    for crit, meta in rubric.items():
        kws = keywords_for_criterion(crit)
        hits = sum(text_lc.count(k) for k in kws) if kws else 0
        # coverage = fraction of keywords present at least once (0..1)
        present = sum(1 for k in kws if k in text_lc) if kws else 0
        coverage = present / max(len(kws), 1)
        results[crit] = {
            "weight": meta.get("weight", 0),
            "keywords": kws,
            "hits": hits,
            "coverage": coverage,
        }
    return results


def main():
    base = Path(__file__).resolve().parents[1]
    rubric_path = base / "Individual Assignment 1.docx"
    submissions_dir = base / "output" / "sample_submissions"
    out_dir = base / "output" / "pdf_analysis"
    out_dir.mkdir(parents=True, exist_ok=True)

    rubric = rubric_from_assignment1_docx(rubric_path)

    rows = []
    md_lines = ["# PDF Analysis Report\n"]

    for student_dir in sorted(p for p in submissions_dir.iterdir() if p.is_dir()):
        pdfs = list(student_dir.rglob("*.pdf"))
        if not pdfs:
            continue
        # concatenate all PDFs per student
        text = "\n".join(extract_pdf_text(p) for p in pdfs)
        text_len = len(text)
        rubric_scores = score_text_against_rubric(text, rubric)

        # overall heuristic: weighted coverage
        total_weight = sum(v["weight"] for v in rubric_scores.values()) or 1
        weighted = sum(v["coverage"] * v["weight"] for v in rubric_scores.values())
        heuristic_score = (weighted / total_weight) * 100

        rows.append({
            "student_folder": student_dir.name,
            "pdf_count": len(pdfs),
            "text_length": text_len,
            "heuristic_score": round(heuristic_score, 2),
        })

        md_lines.append(f"## {student_dir.name}\n")
        md_lines.append(f"PDFs: {len(pdfs)}  |  Text length: {text_len}  |  Heuristic score: {heuristic_score:.2f}\n")
        md_lines.append("| Criterion | Weight | Keyword hits | Coverage |\n|---|---:|---:|---:|\n")
        for crit, data in rubric_scores.items():
            md_lines.append(f"| {crit} | {data['weight']} | {data['hits']} | {data['coverage']:.2f} |\n")
        md_lines.append("\n")

    # write CSV
    with open(out_dir / "report.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["student_folder", "pdf_count", "text_length", "heuristic_score"])
        writer.writeheader()
        writer.writerows(rows)

    # write MD
    (out_dir / "report.md").write_text("".join(md_lines), encoding="utf-8")
    print("Wrote:", out_dir / "report.csv")
    print("Wrote:", out_dir / "report.md")


if __name__ == "__main__":
    main()
