"""Small test for the UTEW221 adapter."""
from pathlib import Path
import json
from homs.integrations.utew221_adapter import convert_utew221_to_rubric


def main():
    sdir = Path(__file__).parent
    sample = sdir / 'sample_utew.json'
    sample_data = {
        'criteria': [
            {'name': 'Correctness', 'weight': 1.0, 'annotations': ['test_0', 'test_1', 'test_6']},
            {'name': 'Style', 'weight': 0.5, 'annotations': ['style_imports']}
        ]
    }
    sample.write_text(json.dumps(sample_data, indent=2), encoding='utf-8')

    out = Path('output') / 'rubrics' / (sample.stem + '.internal.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    rubric = convert_utew221_to_rubric(sample, out)
    print('Converted rubric:')
    print(json.dumps(rubric, indent=2))


if __name__ == '__main__':
    main()
