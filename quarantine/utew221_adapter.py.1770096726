"""UTEW221 Rubric Adapter

Converts UTEW221-style rubric files into the internal rubric format
used by `AssessmentAgent`. The internal format is a dict of criteria:

{
  "criterion_name": {
      "weight": 1.0,
      "annotations": ["ann_1", "ann_2"]
  },
  ...
}

This adapter supports simple JSON or CSV rubrics. If input is CSV, it
expects columns: criterion, annotation, weight (optional).
"""

from pathlib import Path
import json
import csv
from typing import Dict, Any


def convert_utew221_to_rubric(input_path: Path, output_path: Path) -> Dict[str, Any]:
    """Read a UTEW221 rubric (JSON or CSV) and write internal rubric JSON.

    Returns the internal rubric dict.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    rubric = {}

    if input_path.suffix.lower() == '.json':
        data = json.loads(input_path.read_text(encoding='utf-8'))
        # Best-effort mapping: look for top-level list of criteria or mapping
        if isinstance(data, dict):
            # If structure matches internal format already, return it
            if all(isinstance(v, dict) for v in data.values()):
                rubric = data
            else:
                # Try common shapes: {'criteria': [...]} or {'rubric': {...}}
                if 'criteria' in data and isinstance(data['criteria'], list):
                    for c in data['criteria']:
                        name = c.get('name') or c.get('criterion')
                        if not name:
                            continue
                        weight = float(c.get('weight', 1.0))
                        annotations = c.get('annotations') or c.get('annotation_ids') or []
                        rubric[name] = {'weight': weight, 'annotations': annotations}
                elif 'rubric' in data and isinstance(data['rubric'], dict):
                    rubric = data['rubric']
                else:
                    # Fallback: flatten recognized entries
                    for k, v in data.items():
                        if isinstance(v, dict) and 'annotations' in v:
                            rubric[k] = {'weight': float(v.get('weight', 1.0)), 'annotations': v.get('annotations', [])}
        elif isinstance(data, list):
            for c in data:
                name = c.get('name') or c.get('criterion')
                if not name:
                    continue
                weight = float(c.get('weight', 1.0))
                annotations = c.get('annotations') or []
                rubric[name] = {'weight': weight, 'annotations': annotations}

    elif input_path.suffix.lower() == '.csv':
        with input_path.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                crit = row.get('criterion') or row.get('criterion_name') or row.get('criterion_id')
                ann = row.get('annotation') or row.get('annotation_id') or row.get('annotation_name')
                weight = row.get('weight')
                if not crit:
                    continue
                if crit not in rubric:
                    rubric[crit] = {'weight': float(weight) if weight else 1.0, 'annotations': []}
                if ann and ann not in rubric[crit]['annotations']:
                    rubric[crit]['annotations'].append(ann)

    else:
        raise ValueError('Unsupported rubric format: ' + str(input_path.suffix))

    # Ensure weight and annotations are normalized
    for crit, details in list(rubric.items()):
        if not isinstance(details, dict):
            # try to coerce simple list -> annotations
            if isinstance(details, list):
                rubric[crit] = {'weight': 1.0, 'annotations': details}
            else:
                rubric[crit] = {'weight': 1.0, 'annotations': []}
        else:
            rubric[crit]['weight'] = float(details.get('weight', 1.0))
            rubric[crit]['annotations'] = list(details.get('annotations', []))

    # write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(rubric, indent=2), encoding='utf-8')
    return rubric


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Convert UTEW221 rubric to internal format')
    p.add_argument('input', help='Input rubric file (JSON or CSV)')
    p.add_argument('output', help='Output JSON rubric path')
    args = p.parse_args()
    r = convert_utew221_to_rubric(Path(args.input), Path(args.output))
    print('Wrote rubric to', args.output)
