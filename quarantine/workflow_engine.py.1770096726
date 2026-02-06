"""
Workflow Engine - Orchestrates the complete assessment workflow
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from .assessment_agent import AssessmentAgent
from .moderation_agent import ModerationAgent
from .learning_agent import LearningAgent
from ..utils.data_manager import DataManager
from ..utils.git_integration import GitIntegration
from ..utils.report_generator import ReportGenerator
from ..utils.feedback_packager import repackage_efundi_zip, extract_student_id

class WorkflowEngine:
    def __init__(self, config_path: Path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.assessment_agent = AssessmentAgent(self.config.get('assessment', {}))
        self.moderation_agent = ModerationAgent(self.config.get('moderation', {}))
        self.learning_agent = LearningAgent(self.config.get('learning', {}))
        self.data_manager = DataManager(self.config.get('data', {}))
        self.git_integration = GitIntegration(self.config.get('git', {}))
        self.report_generator = ReportGenerator(self.config.get('reporting', {}))
        print("[WorkflowEngine] Initialized successfully")

    def run_complete_workflow(self, submissions_dir: Path, 
                             reference_name: str, 
                             output_dir: Path) -> Dict[str, Any]:
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n{'='*60}")
        print(f"[WorkflowEngine] Starting workflow: {workflow_id}")
        print(f"{'='*60}\n")
        workflow_summary = {
            'workflow_id': workflow_id,
            'start_time': datetime.now().isoformat(),
            'steps': []
        }
        try:
            print("[WorkflowEngine] Step 1: Creating Git branch...")
            branch_name = f"assessment_{workflow_id}"
            self.git_integration.create_branch(branch_name)
            workflow_summary['steps'].append({'step': 'git_branch', 'status': 'success'})

            print("\n[WorkflowEngine] Step 2: Running assessments...")
            assessments = self.assessment_agent.batch_assess(submissions_dir, reference_name)
            workflow_summary['steps'].append({'step': 'assessment', 'status': 'success', 'count': len(assessments)})

            print("\n[WorkflowEngine] Step 3: Moderating assessments...")
            moderations = self.moderation_agent.batch_moderate(assessments)
            plagiarism_cases = self.moderation_agent.detect_plagiarism(assessments)
            workflow_summary['steps'].append({
                'step': 'moderation',
                'status': 'success',
                'flagged': len([m for m in moderations if m.get('requires_human_review')]),
                'plagiarism_cases': len(plagiarism_cases)
            })

            print("\n[WorkflowEngine] Step 4: Learning from assessment patterns...")
            self.learning_agent.learn_from_assessments(assessments, moderations)
            insights = self.learning_agent.get_insights()
            workflow_summary['steps'].append({'step': 'learning', 'status': 'success'})

            print("\n[WorkflowEngine] Step 5: Generating reports...")
            report_data = {
                'assessments': assessments,
                'moderations': moderations,
                'plagiarism': plagiarism_cases,
                'insights': insights,
                'statistics': self.assessment_agent.get_statistics(),
                'moderation_report': self.moderation_agent.get_moderation_report()
            }
            report_paths = self.report_generator.generate_all_reports(report_data, output_dir)
            workflow_summary['steps'].append({'step': 'reporting', 'status': 'success', 'reports': report_paths})

            print("\n[WorkflowEngine] Step 6: Saving data...")
            self.data_manager.save_workflow_data(workflow_id, report_data)
            kb_path = output_dir / "knowledge_base.pkl"
            self.learning_agent.save_knowledge_base(kb_path)
            workflow_summary['steps'].append({'step': 'data_save', 'status': 'success'})

            print("\n[WorkflowEngine] Step 7: Committing to Git...")
            commit_msg = f"Assessment workflow {workflow_id} - {len(assessments)} submissions"
            self.git_integration.commit_and_push(commit_msg)
            workflow_summary['steps'].append({'step': 'git_commit', 'status': 'success'})

            workflow_summary['end_time'] = datetime.now().isoformat()
            workflow_summary['status'] = 'success'
            print(f"\n{'='*60}")
            print(f"[WorkflowEngine] Workflow completed successfully")
            print(f"{'='*60}\n")
            return workflow_summary
        except Exception as e:
            print(f"\n[WorkflowEngine] ERROR: {str(e)}")
            workflow_summary['end_time'] = datetime.now().isoformat()
            workflow_summary['status'] = 'failed'
            workflow_summary['error'] = str(e)
            return workflow_summary

    def run_assessment_only(self, submissions_dir: Path, 
                           reference_name: str) -> List[Dict[str, Any]]:
        print("[WorkflowEngine] Running assessment-only workflow...")
        return self.assessment_agent.batch_assess(submissions_dir, reference_name)

    def reprocess_with_learning(self, previous_workflow_id: str):
        print(f"[WorkflowEngine] Reprocessing workflow: {previous_workflow_id}")
        previous_data = self.data_manager.load_workflow_data(previous_workflow_id)
        self.learning_agent.learn_from_assessments(previous_data['assessments'], previous_data.get('moderations', []))
        insights = self.learning_agent.get_insights()
        print("[WorkflowEngine] Updated insights:")
        print(json.dumps(insights, indent=2))
        return insights
"""
Workflow Engine - Orchestrates the complete assessment workflow
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from .assessment_agent import AssessmentAgent
from .moderation_agent import ModerationAgent
from .learning_agent import LearningAgent
from ..utils.data_manager import DataManager
from ..utils.git_integration import GitIntegration
from ..utils.report_generator import ReportGenerator

class WorkflowEngine:
    def __init__(self, config):
        # Accept either a path to a JSON config or a dict
        if isinstance(config, (str, Path)):
            with open(config, 'r') as f:
                self.config = json.load(f)
        elif isinstance(config, dict):
            self.config = config
        else:
            raise TypeError('config must be a path or a dict')

        self.assessment_agent = AssessmentAgent(self.config.get('assessment', {}))
        self.moderation_agent = ModerationAgent(self.config.get('moderation', {}))
        self.learning_agent = LearningAgent(self.config.get('learning', {}))
        self.data_manager = DataManager(self.config.get('data', {}))
        self.git_integration = GitIntegration(self.config.get('git', {}))
        self.report_generator = ReportGenerator(self.config.get('reporting', {}))
        print("[WorkflowEngine] Initialized successfully")

    def run_complete_workflow(self, submissions_dir: Path, reference_name: str, output_dir: Path) -> Dict[str, Any]:
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n{'='*60}")
        print(f"[WorkflowEngine] Starting workflow: {workflow_id}")
        print(f"{'='*60}\n")

        workflow_summary = {'workflow_id': workflow_id, 'start_time': datetime.now().isoformat(), 'steps': []}
        try:
            # Step 1: Create Git branch
            branch_name = f"assessment_{workflow_id}"
            self.git_integration.create_branch(branch_name)
            workflow_summary['steps'].append({'step': 'git_branch', 'status': 'success'})

            # Pre-step: load rubric if available (support explicit path or common locations)
            rubric_loaded = False
            rp = None
            if isinstance(self.config.get('rubric_path'), (str, Path)):
                rp = Path(self.config.get('rubric_path'))
            else:
                # common locations
                for p in [Path('rubrics'), Path('output') / 'rubrics']:
                    if p.exists():
                        cands = list(p.glob('*.json'))
                        if cands:
                            rp = cands[0]
                            break

            if rp is not None and rp.exists():
                try:
                    self.assessment_agent.load_rubric(rp)
                    rubric_loaded = True
                except Exception as e:
                    print(f"[WorkflowEngine] Warning: failed to load rubric {rp}: {e}")

            # Step 2: Load rubric (if configured)
            try:
                from homs.utils.rubric_parser import rubric_from_docx, rubric_from_assignment1_docx
                from homs.utils.rubric_parser import save_rubric
                rp = None
                if self.rubric_path:
                    rp = Path(self.rubric_path)
                elif self.assignment1_doc:
                    rp = Path(self.assignment1_doc)
                if rp and rp.exists():
                    if self.assignment1_doc:
                        rubric = rubric_from_assignment1_docx(rp)
                    else:
                        rubric = rubric_from_docx(rp)
                    out = save_rubric(rubric, Path('output') / 'rubrics' / (rp.stem + '.json'))
                    self.assessment_agent.load_rubric(out)
            except Exception as e:
                print(f"[WorkflowEngine] Warning: rubric parse/load failed: {e}")

            # Step 3: Run assessments
            assessments = self.assessment_agent.batch_assess(submissions_dir, reference_name)
            workflow_summary['steps'].append({'step': 'assessment', 'status': 'success', 'count': len(assessments)})

            # Step 3: Moderate results
            moderations = self.moderation_agent.batch_moderate(assessments)
            plagiarism_cases = self.moderation_agent.detect_plagiarism(assessments)
            workflow_summary['steps'].append({'step': 'moderation', 'status': 'success', 'flagged': len([m for m in moderations if m.get('requires_human_review')]), 'plagiarism_cases': len(plagiarism_cases)})

            # Step 4: Learning
            self.learning_agent.learn_from_assessments(assessments, moderations)
            insights = self.learning_agent.get_insights()
            workflow_summary['steps'].append({'step': 'learning', 'status': 'success'})

            # Step 5: Reporting
            report_data = {
                'assessments': assessments,
                'moderations': moderations,
                'plagiarism': plagiarism_cases,
                'insights': insights,
                'statistics': self.assessment_agent.get_statistics(),
                'moderation_report': self.moderation_agent.get_moderation_report()
            }
            report_paths = self.report_generator.generate_all_reports(report_data, output_dir)
            workflow_summary['steps'].append({'step': 'reporting', 'status': 'success', 'reports': report_paths})

            # Step 5b: eFundi packaging (optional)
            ef_cfg = self.config.get('efundi', {}) or {}
            if ef_cfg.get('package', False):
                try:
                    download_zip = Path(ef_cfg['download_zip'])
                    output_zip = Path(ef_cfg.get('output_zip') or (Path(output_dir) / 'efundi_upload.zip'))
                    feedback_dir = Path(ef_cfg.get('feedback_dir') or '')
                    comments_json = Path(ef_cfg.get('comments_json') or '')
                    id_map = ef_cfg.get('student_id_map') or {}

                    grades_map = {}
                    for a in assessments:
                        sid = str(a.get('student_id', '')).strip()
                        if not sid:
                            continue
                        score = a.get('final_score', a.get('rubric_score', a.get('basic_score')))
                        if score is not None:
                            grades_map[sid] = score

                    # Apply explicit id mapping (local -> efundi)
                    for local_id, efundi_id in id_map.items():
                        if local_id in grades_map:
                            grades_map[str(efundi_id)] = grades_map[local_id]

                    feedback_files = _collect_feedback_files(feedback_dir)
                    comments_map = _collect_comments_map(feedback_dir, comments_json)

                    repackage_efundi_zip(
                        download_zip=download_zip,
                        output_zip=output_zip,
                        grades_map=grades_map,
                        feedback_files=feedback_files,
                        comments_map=comments_map,
                    )
                    workflow_summary['steps'].append({'step': 'efundi_package', 'status': 'success', 'output_zip': str(output_zip)})
                except Exception as e:
                    workflow_summary['steps'].append({'step': 'efundi_package', 'status': 'failed', 'error': str(e)})

            # Step 6: Save data
            self.data_manager.save_workflow_data(workflow_id, report_data)
            kb_path = output_dir / "knowledge_base.pkl"
            self.learning_agent.save_knowledge_base(kb_path)
            workflow_summary['steps'].append({'step': 'data_save', 'status': 'success'})

            # Step 7: Commit to Git
            commit_msg = f"Assessment workflow {workflow_id} - {len(assessments)} submissions"
            self.git_integration.commit_and_push(commit_msg)
            workflow_summary['steps'].append({'step': 'git_commit', 'status': 'success'})

            workflow_summary['end_time'] = datetime.now().isoformat()
            workflow_summary['status'] = 'success'
            print(f"\n{'='*60}")
            print(f"[WorkflowEngine] Workflow completed successfully")
            print(f"{'='*60}\n")
            return workflow_summary

        except Exception as e:
            print(f"\n[WorkflowEngine] ERROR: {str(e)}")
            workflow_summary['end_time'] = datetime.now().isoformat()
            workflow_summary['status'] = 'failed'
            workflow_summary['error'] = str(e)
            return workflow_summary

    def run_assessment_only(self, submissions_dir: Path, reference_name: str) -> List[Dict[str, Any]]:
        print("[WorkflowEngine] Running assessment-only workflow...")
        return self.assessment_agent.batch_assess(submissions_dir, reference_name)


def _find_efundi_root(path: Path) -> Path:
    """Detect root folder that contains student folders."""
    if not path or not path.exists():
        return path
    # If there's exactly one child directory, treat it as root
    dirs = [p for p in path.iterdir() if p.is_dir()]
    if len(dirs) == 1:
        return dirs[0]
    return path


def _collect_feedback_files(feedback_dir: Path) -> Dict[str, List[Path]]:
    """Collect feedback files per student folder.

    Expected layout (either):
      feedback_dir/<root>/<Student Name(id)>/Feedback Attachment(s)/*
      feedback_dir/<Student Name(id)>/*
    """
    feedback_files: Dict[str, List[Path]] = {}
    if not feedback_dir or not feedback_dir.exists():
        return feedback_files

    root = _find_efundi_root(feedback_dir)
    for student_folder in root.iterdir():
        if not student_folder.is_dir():
            continue
        sid = extract_student_id(student_folder.name)
        if not sid:
            continue

        files: List[Path] = []
        fb_dir = student_folder / 'Feedback Attachment(s)'
        if fb_dir.exists():
            files.extend([p for p in fb_dir.rglob('*') if p.is_file()])
        else:
            # use any files directly under student folder (excluding comments/submission)
            for p in student_folder.rglob('*'):
                if not p.is_file():
                    continue
                if p.name.lower() == 'comments.txt':
                    continue
                if 'submission attachment' in str(p.parent).lower():
                    continue
                files.append(p)

        if files:
            feedback_files[student_folder.name] = files
    return feedback_files


def _collect_comments_map(feedback_dir: Path, comments_json: Path) -> Dict[str, str]:
    comments: Dict[str, str] = {}
    if comments_json and comments_json.exists():
        try:
            with open(comments_json, 'r', encoding='utf-8') as f:
                raw = json.load(f)
                if isinstance(raw, dict):
                    comments.update({str(k): str(v) for k, v in raw.items()})
        except Exception:
            pass

    if feedback_dir and feedback_dir.exists():
        root = _find_efundi_root(feedback_dir)
        for student_folder in root.iterdir():
            if not student_folder.is_dir():
                continue
            sid = extract_student_id(student_folder.name)
            if not sid:
                continue
            c = student_folder / 'comments.txt'
            if c.exists():
                comments[sid] = c.read_text(encoding='utf-8', errors='ignore')

    return comments
