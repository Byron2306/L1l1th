"""
Assessment Agent - Core auto-assessment module using PyBryt
"""

import json
import traceback
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    import pybryt
except Exception:
    pybryt = None

# Optional UTEW221 adapter
try:
    from homs.integrations.utew221_adapter import convert_utew221_to_rubric
except Exception:
    try:
        from ..integrations.utew221_adapter import convert_utew221_to_rubric
    except Exception:
        convert_utew221_to_rubric = None


class AssessmentAgent:
    """
    Automated assessment agent that evaluates student submissions
    using PyBryt reference implementations and custom rubrics.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.reference_implementations = {}
        self.rubrics = {}
        self.assessment_history = []

    def load_reference(self, name: str, reference_path: Path):
        if pybryt is None:
            print(f"[AssessmentAgent] pybryt not available; skipping load for {name}")
            return
        try:
            ref = pybryt.ReferenceImplementation.load(str(reference_path))
            self.reference_implementations[name] = ref
            print(f"[AssessmentAgent] Loaded reference: {name}")
        except Exception as e:
            print(f"[AssessmentAgent] Error loading reference {name}: {e}")

    def load_rubric(self, rubric_path: Path):
        rubric_path = Path(rubric_path)
        # If the UTEW221 adapter is available, try to normalize the rubric
        if convert_utew221_to_rubric is not None:
            try:
                # Quick probe: if JSON/YAML already matches internal format, load it
                with open(rubric_path, 'r', encoding='utf-8') as f:
                    if rubric_path.suffix.lower() == '.json':
                        data = json.load(f)
                    else:
                        import yaml
                        data = yaml.safe_load(f)

                if isinstance(data, dict) and all(isinstance(v, dict) for v in data.values()):
                    self.rubrics = data
                    print(f"[AssessmentAgent] Loaded internal-format rubric from {rubric_path}")
                    return
            except Exception:
                # fall through to conversion attempt
                pass

            # Convert using adapter and load the converted JSON
            out_dir = Path('output') / 'rubrics'
            out_path = out_dir / (rubric_path.stem + '.internal.json')
            rubric = convert_utew221_to_rubric(rubric_path, out_path)
            self.rubrics = rubric
            print(f"[AssessmentAgent] Converted and loaded UTEW221 rubric from {rubric_path} -> {out_path}")
            return

        # Fallback behavior when adapter isn't available
        with open(rubric_path, 'r', encoding='utf-8') as f:
            if rubric_path.suffix.lower() == '.json':
                self.rubrics = json.load(f)
            else:
                import yaml
                self.rubrics = yaml.safe_load(f)
        print(f"[AssessmentAgent] Loaded rubric from {rubric_path}")

    def assess_submission(self, submission_path: Path, reference_name: str, student_id: str) -> Dict[str, Any]:
        timestamp = datetime.now().isoformat()

        if pybryt is None or reference_name not in self.reference_implementations:
            assessment = {
                'student_id': student_id,
                'timestamp': timestamp,
                'status': 'success',
                'reference_used': reference_name,
                'annotations': {},
                'total_annotations': 0,
                'passed_annotations': 0,
                'basic_score': 0,
                'rubric_score': None,
                'final_score': 0,
                'submission_path': str(submission_path)
            }
            self.assessment_history.append(assessment)
            return assessment

        try:
            # If submission is a notebook, prefer pybryt; for .py fallback to simple functional tests
            if submission_path.suffix == '.ipynb' and pybryt is not None:
                pybryt_dir = [n for n in dir(pybryt)]
                if hasattr(pybryt, 'StudentImplementation'):
                    student_trace = pybryt.StudentImplementation(str(submission_path))
                elif hasattr(pybryt, 'StudentCode'):
                    student_trace = pybryt.StudentCode(str(submission_path))
                else:
                    raise AttributeError("pybryt missing StudentImplementation/StudentCode")

                reference = self.reference_implementations[reference_name]

                # Try common evaluation method names used across pybryt versions.
                if hasattr(student_trace, 'check'):
                    results = student_trace.check(reference)
                elif hasattr(reference, 'check'):
                    results = reference.check(student_trace)
                elif hasattr(reference, 'evaluate'):
                    results = reference.evaluate(student_trace)
                else:
                    raise RuntimeError('No compatible evaluation method found on pybryt objects')
            else:
                # Non-notebook submission: first try converting the .py -> .ipynb and run PyBryt
                results = None
                if pybryt is not None:
                    try:
                        import nbformat
                        import tempfile
                        import os
                        import shutil

                        code = submission_path.read_text()
                        nb = nbformat.v4.new_notebook()
                        nb['cells'] = [nbformat.v4.new_code_cell(code)]

                        td = tempfile.mkdtemp(prefix='homs_py2nb_')
                        nb_path = os.path.join(td, submission_path.stem + '.ipynb')
                        nbformat.write(nb, nb_path)

                        timeout = None
                        # config may be nested or direct
                        timeout = (self.config.get('assessment', {}) or {}).get('timeout') or self.config.get('timeout')
                        # create student implementation from notebook
                        if hasattr(pybryt, 'StudentImplementation'):
                            if timeout is not None:
                                student_impl = pybryt.StudentImplementation(nb_path, timeout=timeout)
                            else:
                                student_impl = pybryt.StudentImplementation(nb_path)
                            reference = self.reference_implementations[reference_name]
                            if hasattr(student_impl, 'check'):
                                results = student_impl.check(reference)
                            elif hasattr(reference, 'check'):
                                results = reference.check(student_impl)
                            elif hasattr(reference, 'evaluate'):
                                results = reference.evaluate(student_impl)
                        shutil.rmtree(td, ignore_errors=True)
                    except Exception:
                        results = None

                # If conversion/evaluation via pybryt didn't work, fall back to simple functional tests
                if results is None:
                    ns = {}
                    with open(submission_path, 'r') as f:
                        code = f.read()
                    exec(compile(code, str(submission_path), 'exec'), ns)
                    func = ns.get('fibonacci') or ns.get('fib') or ns.get('solve')
                    if callable(func):
                        tests = [(0, 0), (1, 1), (6, 8)]
                        results = {}
                        passed = 0
                        for inp, exp in tests:
                            try:
                                out = func(inp)
                                ok = out == exp
                                results[f'test_{inp}'] = {'input': inp, 'expected': exp, 'output': out, 'passed': ok}
                                if ok:
                                    passed += 1
                            except Exception as e2:
                                results[f'test_{inp}'] = {'input': inp, 'expected': exp, 'output': None, 'passed': False, 'error': str(e2)}
                        score = (passed / len(tests)) * 100
                    else:
                        raise RuntimeError('No callable fibonacci/fib/solve found in submission')

            annotation_results = {}
            # results may be pybryt ReferenceResult objects or our fallback dicts
            for annotation_name, result in results.items():
                if isinstance(result, dict):
                    satisfied = bool(result.get('passed') or result.get('satisfied'))
                    value = result.get('output') or result.get('value')
                else:
                    satisfied = getattr(result, 'satisfied', False)
                    value = getattr(result, 'value', None)
                annotation_results[annotation_name] = {
                    'satisfied': satisfied,
                    'value': str(value) if value is not None else None
                }

            total_annotations = len(annotation_results)
            passed_annotations = sum(1 for r in annotation_results.values() if r['satisfied'])
            score = (passed_annotations / total_annotations * 100) if total_annotations > 0 else 0

            rubric_score = self._apply_rubric(annotation_results)

            assessment = {
                'student_id': student_id,
                'timestamp': timestamp,
                'status': 'success',
                'reference_used': reference_name,
                'annotations': annotation_results,
                'total_annotations': total_annotations,
                'passed_annotations': passed_annotations,
                'basic_score': score,
                'rubric_score': rubric_score,
                'final_score': rubric_score if rubric_score is not None else score,
                'submission_path': str(submission_path)
            }

            self.assessment_history.append(assessment)
            return assessment

        except Exception as e:
            # If pybryt integration fails (common across versions), fall back
            # to a lightweight functional grader for simple demo tasks.
            err_str = str(e)
            tb = traceback.format_exc()
            fallback = None
            try:
                # simple fallback: execute submission and test common fib function
                ns = {}
                with open(submission_path, 'r') as f:
                    code = f.read()
                exec(compile(code, str(submission_path), 'exec'), ns)
                func = ns.get('fibonacci') or ns.get('fib') or ns.get('solve')
                if callable(func):
                    tests = [(0, 0), (1, 1), (6, 8)]
                    results = {}
                    passed = 0
                    for inp, exp in tests:
                        try:
                            out = func(inp)
                            ok = out == exp
                            results[f'test_{inp}'] = {'input': inp, 'expected': exp, 'output': out, 'passed': ok}
                            if ok:
                                passed += 1
                        except Exception as e2:
                            results[f'test_{inp}'] = {'input': inp, 'expected': exp, 'output': None, 'passed': False, 'error': str(e2)}
                    score = (passed / len(tests)) * 100
                    assessment = {
                        'student_id': student_id,
                        'timestamp': timestamp,
                        'status': 'success',
                        'reference_used': reference_name,
                        'annotations': results,
                        'total_annotations': len(tests),
                        'passed_annotations': passed,
                        'basic_score': score,
                        'rubric_score': None,
                        'final_score': score,
                        'submission_path': str(submission_path),
                        'note': 'fallback functional grading used due to pybryt integration error',
                        'pybryt_error': err_str,
                        'pybryt_traceback': tb,
                        'pybryt_dir': pybryt_dir if 'pybryt_dir' in locals() else None
                    }
                    self.assessment_history.append(assessment)
                    return assessment
            except Exception:
                fallback = None

            details = {
                'student_id': student_id,
                'timestamp': timestamp,
                'status': 'error',
                'error': err_str,
                'traceback': tb,
                'pybryt_dir': pybryt_dir if 'pybryt_dir' in locals() else None,
                'fallback_used': False
            }
            return details

    def _apply_rubric(self, annotation_results: Dict) -> Optional[float]:
        if not self.rubrics:
            return None

        total_score = 0
        total_weight = 0
        for criterion, details in self.rubrics.items():
            weight = details.get('weight', 1.0)
            annotations = details.get('annotations', [])
            satisfied = sum(1 for ann in annotations if ann in annotation_results and annotation_results[ann]['satisfied'])
            criterion_score = (satisfied / len(annotations)) * weight if annotations else 0
            total_score += criterion_score
            total_weight += weight

        return (total_score / total_weight * 100) if total_weight > 0 else 0

    def batch_assess(self, submissions_dir: Path, reference_name: str) -> List[Dict[str, Any]]:
        results = []
        submission_files = list(submissions_dir.glob('*.py'))
        print(f"[AssessmentAgent] Assessing {len(submission_files)} submissions...")
        for submission_file in submission_files:
            student_id = submission_file.stem
            result = self.assess_submission(submission_file, reference_name, student_id)
            results.append(result)
        print(f"[AssessmentAgent] Batch assessment complete")
        return results

    def get_statistics(self) -> Dict[str, Any]:
        if not self.assessment_history:
            return {}
        successful = [a for a in self.assessment_history if a['status'] == 'success']
        scores = [a['final_score'] for a in successful]
        return {
            'total_assessments': len(self.assessment_history),
            'successful': len(successful),
            'failed': len(self.assessment_history) - len(successful),
            'mean_score': np.mean(scores) if scores else 0,
            'median_score': np.median(scores) if scores else 0,
            'std_score': np.std(scores) if scores else 0,
            'min_score': np.min(scores) if scores else 0,
            'max_score': np.max(scores) if scores else 0
        }
