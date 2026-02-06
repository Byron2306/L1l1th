"""Analyze PDF submissions against rubric + reference corpus (best-effort, text-based).

Outputs:
- output/pdf_analysis/report_refs.csv
- output/pdf_analysis/report_refs.md
"""
from pathlib import Path
import csv
import re
import sys
from typing import Dict, Any, List, Tuple

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


def extract_text_from_refs(ref_dir: Path) -> str:
    texts = []
    for p in ref_dir.rglob('*'):
        if not p.is_file():
            continue
        if p.suffix.lower() == '.pdf':
            texts.append(extract_pdf_text(p))
        elif p.suffix.lower() in {'.txt', '.md'}:
            try:
                texts.append(p.read_text(encoding='utf-8', errors='ignore'))
            except Exception:
                pass
    return "\n".join(texts)


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z]{3,}", text.lower())


def keywords_for_criterion(name: str) -> List[str]:
    words = re.findall(r"[A-Za-z]{4,}", name.lower())
    stop = {"and", "with", "from", "that", "this", "will", "marks", "have", "your", "into", "over", "then"}
    return [w for w in words if w not in stop]


def sentence_snippets(text: str, keywords: List[str], max_snips: int = 3) -> List[str]:
    if not keywords:
        return []
    # crude sentence split
    sentences = re.split(r"(?<=[.!?])\s+", text)
    hits = []
    for s in sentences:
        s_l = s.lower()
        if any(k in s_l for k in keywords):
            hits.append(s.strip())
        if len(hits) >= max_snips:
            break
    return hits


def jaccard_similarity(a: List[str], b: List[str]) -> float:
    set_a, set_b = set(a), set(b)
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def score_text_against_rubric(text: str, rubric: Dict[str, Any]) -> Dict[str, Any]:
    text_lc = text.lower()
    results = {}
    for crit, meta in rubric.items():
        kws = keywords_for_criterion(crit)
        hits = sum(text_lc.count(k) for k in kws) if kws else 0
        present = sum(1 for k in kws if k in text_lc) if kws else 0
        coverage = present / max(len(kws), 1)
        results[crit] = {
            "weight": meta.get("weight", 0),
            "keywords": kws,
            "hits": hits,
            "coverage": coverage,
            "snippets": sentence_snippets(text, kws),
        }
    return results


def main():
    base = BASE
    rubric_path = base / "Individual Assignment 1.docx"
    submissions_dir = base / "output" / "sample_submissions"
    ref_dir = base / "references"
    out_dir = base / "output" / "pdf_analysis"
    out_dir.mkdir(parents=True, exist_ok=True)

    rubric = rubric_from_assignment1_docx(rubric_path)
    ref_text = extract_text_from_refs(ref_dir)
    ref_tokens = tokenize(ref_text)

    rows = []
    md_lines = ["# PDF Analysis Report (with references)\n"]

    for student_dir in sorted(p for p in submissions_dir.iterdir() if p.is_dir()):
        pdfs = list(student_dir.rglob("*.pdf"))
        if not pdfs:
            continue
        text = "\n".join(extract_pdf_text(p) for p in pdfs)
        text_len = len(text)
        rubric_scores = score_text_against_rubric(text, rubric)

        total_weight = sum(v["weight"] for v in rubric_scores.values()) or 1
        weighted = sum(v["coverage"] * v["weight"] for v in rubric_scores.values())
        rubric_score = (weighted / total_weight) * 100

        student_tokens = tokenize(text)
        ref_sim = jaccard_similarity(student_tokens, ref_tokens)
        heuristic_score = (0.7 * rubric_score) + (0.3 * (ref_sim * 100))

        needs_ocr = text_len < 200

        rows.append({
            "student_folder": student_dir.name,
            "pdf_count": len(pdfs),
            "text_length": text_len,
            "rubric_score": round(rubric_score, 2),
            "ref_similarity": round(ref_sim, 4),
            "heuristic_score": round(heuristic_score, 2),
            "needs_ocr": needs_ocr,
        })

        md_lines.append(f"## {student_dir.name}\n")
        md_lines.append(f"PDFs: {len(pdfs)}  |  Text length: {text_len}  |  Ref similarity: {ref_sim:.4f}  |  Rubric score: {rubric_score:.2f}  |  Heuristic score: {heuristic_score:.2f}\n")
        if needs_ocr:
            md_lines.append("**⚠ Likely scanned/empty text. OCR recommended.**\n")
        md_lines.append("| Criterion | Weight | Coverage | Snippets |\n|---|---:|---:|---|\n")
        for crit, data in rubric_scores.items():
            snips = " / ".join(data['snippets'][:2])
            md_lines.append(f"| {crit} | {data['weight']} | {data['coverage']:.2f} | {snips} |\n")
        md_lines.append("\n")

    # write CSV
    with open(out_dir / "report_refs.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["student_folder", "pdf_count", "text_length", "rubric_score", "ref_similarity", "heuristic_score", "needs_ocr"])
        writer.writeheader()
        writer.writerows(rows)

    # write MD
    (out_dir / "report_refs.md").write_text("".join(md_lines), encoding="utf-8")
    print("Wrote:", out_dir / "report_refs.csv")
    print("Wrote:", out_dir / "report_refs.md")


if __name__ == "__main__":
    main()
