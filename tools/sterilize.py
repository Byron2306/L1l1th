#!/usr/bin/env python3
"""
Sterilize utility for LuciferOS
- Scans for suspicious processes and files (based on path heuristics)
- Provides dry-run reporting
- Optionally quarantines files and terminates processes when explicitly confirmed

Safety rules:
- Default mode is dry-run (no destructive actions)
- Destructive actions require explicit confirm=True and admin privileges
- Whitelist system dirs (Windows Program Files, Windows, Python venv, workspace)
- Quarantine moves files to workspace/quarantine
- MASTER PROTECTION: Critical user paths are always protected
"""

import os
import sys
import shutil
import json
import time
import fnmatch
import logging
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

WORKSPACE = Path(__file__).resolve().parents[1]
QUARANTINE_DIR = WORKSPACE / 'quarantine'
QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

# Master protection configuration
MASTER_PROTECTION_CONFIG = WORKSPACE / 'config' / 'master_protection.json'
LOCKDOWN_FILE = WORKSPACE / '.lockdown'
AUDIT_LOG = WORKSPACE / 'logs' / 'protection_audit.log'

# Ensure logs directory exists
(WORKSPACE / 'logs').mkdir(parents=True, exist_ok=True)

def setup_audit_logger():
    """Setup audit logging for protection events"""
    logger = logging.getLogger('master_protection')
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = logging.FileHandler(str(AUDIT_LOG), encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
    return logger

audit_log = setup_audit_logger()

def load_master_protection():
    """Load master protection configuration"""
    default_config = {
        'containment_enabled': True,
        'protected_paths': {'desktop_projects': [], 'user_documents': [], 'system_critical': [], 'workspace': []},
        'protected_extensions': {'high_value': [], 'code': [], 'config': []},
        'kill_protection': {'critical_processes': [], 'max_kills_per_run': 5, 'require_confirmation_above': 3},
        'quarantine_protection': {'max_files_per_run': 50, 'max_total_size_mb': 500, 'never_quarantine_patterns': []},
        'emergency_lockdown': {'enabled': False}
    }
    try:
        if MASTER_PROTECTION_CONFIG.exists():
            with open(MASTER_PROTECTION_CONFIG, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
    except Exception as e:
        audit_log.error(f"Failed to load master protection config: {e}")
    return default_config

def is_lockdown_active():
    """Check if emergency lockdown is active"""
    return LOCKDOWN_FILE.exists()

def is_path_protected(path: str, protection_config: dict) -> tuple:
    """Check if a path is protected by master protection
    Returns: (is_protected: bool, reason: str)
    """
    if not path:
        return False, ''
    
    path_lower = str(path).lower().replace('/', '\\')
    
    # Check all protected path categories
    for category, paths in protection_config.get('protected_paths', {}).items():
        if isinstance(paths, list):
            for protected in paths:
                protected_lower = str(protected).lower().replace('/', '\\')
                if path_lower.startswith(protected_lower) or protected_lower.startswith(path_lower):
                    return True, f'master_protected:{category}'
    
    # Check never-quarantine patterns
    patterns = protection_config.get('quarantine_protection', {}).get('never_quarantine_patterns', [])
    for pattern in patterns:
        if fnmatch.fnmatch(path_lower, pattern.lower()) or fnmatch.fnmatch(Path(path).name.lower(), pattern.lower()):
            return True, f'pattern_protected:{pattern}'
    
    return False, ''

WORKSPACE = Path(__file__).resolve().parents[1]
QUARANTINE_DIR = WORKSPACE / 'quarantine'
QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

# Default whitelist paths - do not quarantine or kill processes from these
DEFAULT_WHITELIST = [
    str(Path(os.environ.get('SystemRoot', 'C:/Windows'))).lower(),
    str(Path(os.environ.get('ProgramFiles', 'C:/Program Files'))).lower(),
    str(Path(os.environ.get('ProgramFiles(x86)', 'C:/Program Files (x86)'))).lower(),
    str(sys.exec_prefix).lower(),
    str(WORKSPACE.resolve()).lower()
]

# Default process name whitelist (common user / developer apps we should not terminate automatically)
DEFAULT_PROCESS_WHITELIST = [
    'explorer.exe', 'taskmgr.exe', 'wininit.exe', 'csrss.exe', 'svchost.exe', 'lsass.exe', 'services.exe',
    'code.exe', 'comet.exe', 'taskhostw.exe', 'onedrive.exe', 'teams.exe'
]

# Whitelist configuration file (workspace-level)
WHITELIST_CONFIG = WORKSPACE / 'config' / 'sterilize_whitelist.json'

class Sterilizer:
    def __init__(self, quarantine_dir: Path = QUARANTINE_DIR, whitelist=None):
        self.quarantine_dir = quarantine_dir
        self.whitelist = set([p.rstrip('\\/') for p in (whitelist or DEFAULT_WHITELIST)])
        # Load process name whitelist (can be extended via config file)
        self.process_whitelist = set([n.lower() for n in DEFAULT_PROCESS_WHITELIST])
        self._load_whitelist_config()
        self.now = datetime.now()
        
        # MASTER PROTECTION SYSTEM
        self.master_protection = load_master_protection()
        self.containment_enabled = self.master_protection.get('containment_enabled', True)
        self.lockdown_active = is_lockdown_active()
        
        # Add master-protected processes to whitelist
        for proc in self.master_protection.get('kill_protection', {}).get('critical_processes', []):
            self.process_whitelist.add(proc.lower())
        
        # Counters for limits
        self.kills_this_run = 0
        self.quarantines_this_run = 0
        self.total_quarantine_size = 0
        
        if self.lockdown_active:
            audit_log.warning("EMERGENCY LOCKDOWN ACTIVE - All destructive operations blocked")
        elif self.containment_enabled:
            audit_log.info("Master protection containment ENABLED")

    def _load_whitelist_config(self):
        """Load optional whitelist config from workspace/config/sterilize_whitelist.json
        Format:
        {
          "paths": ["C:/Users/..."],
          "names": ["code.exe"]
        }
        If file does not exist, create a template for the user to customize.
        """
        try:
            cfg_dir = WHITELIST_CONFIG.parent
            cfg_dir.mkdir(parents=True, exist_ok=True)
            if WHITELIST_CONFIG.exists():
                try:
                    with open(WHITELIST_CONFIG, 'r', encoding='utf-8') as fh:
                        j = json.load(fh)
                        for p in j.get('paths', []):
                            self.whitelist.add(str(p).lower())
                        for n in j.get('names', []):
                            self.process_whitelist.add(str(n).lower())
                except Exception:
                    # If config parse fails, keep defaults and proceed
                    pass
            else:
                # Create a sample file so users can customize whitelists
                sample = {'paths': [], 'names': []}
                try:
                    with open(WHITELIST_CONFIG, 'w', encoding='utf-8') as fh:
                        json.dump(sample, fh, indent=2)
                except Exception:
                    pass
        except Exception:
            pass

    def _is_whitelisted(self, path: str) -> bool:
        if not path:
            return False
        p = path.lower()
        for w in self.whitelist:
            if p.startswith(w):
                return True
        return False

    def _is_process_whitelisted(self, name: str, exe: str) -> bool:
        """Return True if process name or exe path matches whitelist"""
        if name and name.lower() in self.process_whitelist:
            return True
        if exe and self._is_whitelisted(exe):
            return True
        return False

    def scan_processes(self):
        """Return list of processes with basic info and suspicious flag"""
        procs = []
        # Prefer psutil if available
        try:
            import psutil
            for p in psutil.process_iter(['pid','name','exe','cmdline']):
                try:
                    info = p.info
                    exe = info.get('exe') or ''
                    cmd = ' '.join(info.get('cmdline') or [])
                    suspicious = False
                    reason = []
                    if not exe:
                        suspicious = True
                        reason.append('no_executable_path')
                    else:
                        if self._is_whitelisted(exe):
                            suspicious = False
                        else:
                            # suspicious if under temp or downloads or user profile
                            low = exe.lower()
                            if any(seg in low for seg in ['\\temp\\', '\\downloads\\', '\\appdata\\', '\\local\\temp\\']):
                                suspicious = True
                                reason.append('in_temp_or_downloads')
                    procs.append({'pid': info.get('pid'), 'name': info.get('name'), 'exe': exe, 'cmdline': cmd, 'suspicious': suspicious, 'reason': reason})
                except Exception:
                    continue
            return procs
        except Exception:
            # Fallback to PowerShell (Windows) or ps output (POSIX)
            if sys.platform == 'win32':
                try:
                    ps_cmd = 'powershell -NoProfile -Command "Get-CimInstance Win32_Process | Select-Object ProcessId,Name,ExecutablePath,CommandLine | ConvertTo-Json -Depth 2"'
                    res = subprocess.run(ps_cmd, shell=True, capture_output=True, text=True, timeout=15)
                    out = res.stdout.strip()
                    if out:
                        items = json.loads(out)
                        if isinstance(items, dict):
                            items = [items]
                        for it in items:
                            pid = it.get('ProcessId')
                            name = it.get('Name')
                            exe = it.get('ExecutablePath') or ''
                            cmd = it.get('CommandLine') or ''
                            suspicious = False
                            reason = []
                            if not exe:
                                suspicious = True
                                reason.append('no_executable_path')
                            else:
                                if self._is_whitelisted(exe):
                                    suspicious = False
                                else:
                                    low = exe.lower()
                                    if any(seg in low for seg in ['\\\\temp\\', '\\downloads\\', '\\appdata\\']):
                                        suspicious = True
                                        reason.append('in_temp_or_downloads')
                            procs.append({'pid': pid, 'name': name, 'exe': exe, 'cmdline': cmd, 'suspicious': suspicious, 'reason': reason})
                except Exception:
                    pass
            else:
                try:
                    # Simple ps aux parsing
                    res = subprocess.run(['ps','-eo','pid,comm,args'], capture_output=True, text=True, timeout=10)
                    lines = res.stdout.splitlines()[1:]
                    for ln in lines:
                        parts = ln.strip().split(None,2)
                        if len(parts) >= 3:
                            pid = int(parts[0]); name = parts[1]; cmd = parts[2]
                            exe = name
                            suspicious = False
                            reason = []
                            if not self._is_whitelisted(exe):
                                if any(seg in cmd.lower() for seg in ['tmp','/var/tmp','/home/']) :
                                    suspicious = True; reason.append('in_tmp_or_home')
                            procs.append({'pid': pid, 'name': name, 'exe': exe, 'cmdline': cmd, 'suspicious': suspicious, 'reason': reason})
                except Exception:
                    pass
            return procs

    def scan_files(self, look_back_days=7):
        """Scan common user directories for suspicious executable files modified recently
        MASTER PROTECTION: Skip protected paths entirely"""
        suspicious_files = []
        dirs = []
        # Common dirs
        user = Path.home()
        dirs.extend([user / 'Downloads', Path(os.environ.get('TMP', user / 'AppData/Local/Temp')), user / 'Desktop'])
        cutoff = self.now - timedelta(days=look_back_days)
        exts = ['.exe','.ps1','.bat','.cmd','.scr','.vbs','.py','.dll']
        for d in dirs:
            try:
                if not d or not d.exists():
                    continue
                for f in d.rglob('*'):
                    try:
                        if not f.is_file():
                            continue
                        
                        # MASTER PROTECTION: Skip protected paths
                        p = str(f.resolve())
                        is_protected, reason = is_path_protected(p, self.master_protection)
                        if is_protected:
                            continue
                        
                        if f.suffix.lower() in exts and datetime.fromtimestamp(f.stat().st_mtime) > cutoff:
                            if not self._is_whitelisted(p):
                                suspicious_files.append({'path': p, 'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat(), 'size': f.stat().st_size})
                    except Exception:
                        continue
            except Exception:
                continue
        return suspicious_files

    def quarantine_file(self, filepath: str):
        p = Path(filepath)
        
        # MASTER PROTECTION CHECK
        if self.lockdown_active:
            audit_log.warning(f"LOCKDOWN: Blocked quarantine of {filepath}")
            return False, 'lockdown_active'
        
        is_protected, reason = is_path_protected(filepath, self.master_protection)
        if is_protected:
            audit_log.warning(f"PROTECTED: Blocked quarantine of {filepath} - {reason}")
            return False, f'protected:{reason}'
        
        # Check quarantine limits
        qp = self.master_protection.get('quarantine_protection', {})
        max_files = qp.get('max_files_per_run', 50)
        max_size_mb = qp.get('max_total_size_mb', 500)
        
        if self.quarantines_this_run >= max_files:
            audit_log.warning(f"LIMIT: Quarantine file limit reached ({max_files})")
            return False, f'limit_reached:max_files={max_files}'
        
        if p.exists():
            file_size = p.stat().st_size
            if (self.total_quarantine_size + file_size) > (max_size_mb * 1024 * 1024):
                audit_log.warning(f"LIMIT: Quarantine size limit reached ({max_size_mb}MB)")
                return False, f'limit_reached:max_size={max_size_mb}MB'
        
        if not p.exists():
            # Possibly already moved in a previous run
            # Try to find a matching file in quarantine by basename
            matches = list(self.quarantine_dir.glob(p.name + '.*'))
            if matches:
                return True, str(matches[0])
            return False, 'not_found'
        dest = self.quarantine_dir / (p.name + '.' + str(int(time.time())))

        # Try fast rename first (same filesystem)
        try:
            os.replace(str(p), str(dest))
            return True, str(dest)
        except Exception:
            # Fall back to careful copy-then-delete with retries and interruption-safe behavior
            try:
                # Copy in chunks to avoid large memory usage and support interruption cleanup
                buffer_size = 64 * 1024
                with open(str(p), 'rb') as src, open(str(dest), 'wb') as dst:
                    while True:
                        chunk = src.read(buffer_size)
                        if not chunk:
                            break
                        dst.write(chunk)
                        dst.flush()
                        os.fsync(dst.fileno())
                # Preserve metadata
                try:
                    shutil.copystat(str(p), str(dest))
                except Exception:
                    pass
                # Remove original
                try:
                    p.unlink()
                except Exception:
                    # If we cannot remove original, leave it and report copy success
                    return True, str(dest)
                return True, str(dest)
            except KeyboardInterrupt:
                # Clean up partial destination if present
                try:
                    if dest.exists():
                        dest.unlink()
                except Exception:
                    pass
                return False, 'interrupted'
            except Exception as e2:
                # Final fallback: try shutil.copy2 then leave original if copy fails
                try:
                    shutil.copy2(str(p), str(dest))
                    return True, str(dest)
                except Exception as e3:
                    # Cleanup partial destination
                    try:
                        if dest.exists():
                            dest.unlink()
                    except Exception:
                        pass
                    return False, str(e3)

    def kill_process(self, pid: int, name: str = None, exe: str = None):
        # MASTER PROTECTION CHECK
        if self.lockdown_active:
            audit_log.warning(f"LOCKDOWN: Blocked kill of PID {pid} ({name})")
            return False, 'lockdown_active'
        
        # Check kill limits
        kp = self.master_protection.get('kill_protection', {})
        max_kills = kp.get('max_kills_per_run', 5)
        
        if self.kills_this_run >= max_kills:
            audit_log.warning(f"LIMIT: Kill limit reached ({max_kills})")
            return False, f'limit_reached:max_kills={max_kills}'
        
        # Check if process is protected
        critical_procs = [p.lower() for p in kp.get('critical_processes', [])]
        if name and name.lower() in critical_procs:
            audit_log.warning(f"PROTECTED: Blocked kill of protected process {name} (PID {pid})")
            return False, f'protected:critical_process:{name}'
        
        try:
            if sys.platform == 'win32':
                res = subprocess.run(f'taskkill /PID {pid} /F', shell=True, capture_output=True, text=True, timeout=10)
                if res.returncode == 0:
                    self.kills_this_run += 1
                    audit_log.info(f"KILLED: PID {pid} ({name})")
                return res.returncode == 0, res.stdout + res.stderr
            else:
                os.kill(pid, 9)
                self.kills_this_run += 1
                audit_log.info(f"KILLED: PID {pid} ({name})")
                return True, 'killed'
        except Exception as e:
            return False, str(e)

    def preview_kills(self, suspicious_procs):
        """Return dict with 'to_kill' and 'skipped' lists with reasons (does not perform kills)"""
        to_kill = []
        skipped = []
        for p in suspicious_procs:
            pid = p.get('pid')
            name = (p.get('name') or '')
            exe = (p.get('exe') or '')
            # Skip obvious system processes
            if not pid or pid <= 4:
                skipped.append({'pid': pid, 'name': name, 'exe': exe, 'reason': 'system_or_protected_pid'})
                continue
            # Skip whitelisted processes
            if self._is_process_whitelisted(name, exe):
                skipped.append({'pid': pid, 'name': name, 'exe': exe, 'reason': 'whitelisted_process'})
                continue
            # Skip processes with no executable path unless force is used (handled upstream)
            if not exe:
                skipped.append({'pid': pid, 'name': name, 'exe': exe, 'reason': 'no_executable_path'})
                continue
            # Default: include in kill list
            to_kill.append({'pid': pid, 'name': name, 'exe': exe})
        return {'to_kill': to_kill, 'skipped': skipped}

    def _write_report(self, report: dict) -> str:
        """Write the report JSON to quarantine directory and return the path"""
        fn = self.quarantine_dir / (f'quarantine_report.{int(time.time())}.json')
        try:
            with open(fn, 'w', encoding='utf-8') as fh:
                json.dump(report, fh, indent=2)
            return str(fn)
        except Exception:
            return ''

    def _quarantine_files_archive(self, suspicious_files, archive_name=None):
        """Create a compressed archive of suspicious files in quarantine directory.
        Returns (ok_count, total_count, archive_path, errors_list)
        """
        from zipfile import ZipFile, ZIP_DEFLATED
        files = [Path(f.get('path')) for f in suspicious_files if f.get('path')]
        total = len(files)
        errors = []
        if not files:
            return 0, 0, '', ['no_files']

        ts = int(time.time())
        archive_name = archive_name or f'quarantine_archive.{ts}.zip'
        archive_path = self.quarantine_dir / archive_name

        # Estimate required space (sum sizes * 0.6 heuristic)
        try:
            total_size = sum((f.stat().st_size for f in files if f.exists()))
        except Exception:
            total_size = 0
        try:
            usage = shutil.disk_usage(str(self.quarantine_dir))
            free = usage.free
            # heuristic: compressed will be about half size; require at least 25% buffer
            required = int(total_size * 0.6) if total_size else 0
            if required and free < required + (required // 4):
                return 0, total, '', [f'low_disk_space: required~{required}, free~{free}']
        except Exception:
            pass

        ok = 0
        try:
            with ZipFile(str(archive_path), 'w', compression=ZIP_DEFLATED) as zf:
                for f in files:
                    try:
                        if not f.exists():
                            errors.append({'path': str(f), 'error': 'not_found'})
                            continue
                        # Compute arcname: relative to user's home or drive root
                        try:
                            arcname = os.path.relpath(str(f), str(Path.home()))
                        except Exception:
                            arcname = f.name
                        zf.write(str(f), arcname)
                        ok += 1
                    except Exception as e:
                        errors.append({'path': str(f), 'error': str(e)})
            # After successful archive, attempt to remove originals for storage saving
            for f in files:
                try:
                    if f.exists():
                        f.unlink()
                except Exception:
                    # If we can't remove, just continue
                    continue
            return ok, total, str(archive_path), errors
        except KeyboardInterrupt:
            # Clean up partial archive
            try:
                if archive_path.exists():
                    archive_path.unlink()
            except Exception:
                pass
            return ok, total, '', errors + [{'error': 'interrupted'}]
        except Exception as e:
            # Clean up on failure
            try:
                if archive_path.exists():
                    archive_path.unlink()
            except Exception:
                pass
            return ok, total, '', errors + [{'error': str(e)}]

    def run(self, dry_run=True, confirm=False, kill=False, quarantine=False, compress=False, force=False):
        """Main sterilize runner
        - dry_run: if True, only report
        - confirm: must be True to allow destructive actions
        - kill: terminate suspicious processes
        - quarantine: move suspicious files to quarantine
        - compress: if True and quarantine=True, create a compressed archive to save space
        - force: bypass safety thresholds for high-risk operations
        """
        report = {'timestamp': datetime.now().isoformat(), 'processes': [], 'files': [], 'actions': []}
        
        # MASTER PROTECTION: Check lockdown status
        if self.lockdown_active:
            report['error'] = 'EMERGENCY LOCKDOWN ACTIVE - All destructive operations blocked'
            report['lockdown'] = True
            audit_log.critical("Attempted operation during lockdown - BLOCKED")
            return report
        
        report['containment_enabled'] = self.containment_enabled
        
        try:
            procs = self.scan_processes()
            files = self.scan_files()
            report['processes'] = procs
            report['files'] = files

            suspicious_procs = [p for p in procs if p.get('suspicious')]
            suspicious_files = files

            report['counts'] = {'suspicious_processes': len(suspicious_procs), 'suspicious_files': len(suspicious_files)}

            if dry_run or not (kill or quarantine):
                report['note'] = 'Dry run: no actions performed' if dry_run else 'No actions requested'
                return report

            if not confirm:
                report['error'] = 'Destructive actions require confirm=True'
                return report

            # Execute actions
            if kill:
                # Compute a safe preview of what would be killed and what will be skipped
                preview = self.preview_kills(suspicious_procs)
                report['actions'].append({'kill_preview': preview})

                to_kill = preview.get('to_kill', [])
                skipped = preview.get('skipped', [])

                # If many processes would be killed, require explicit force to proceed
                FORCE_THRESHOLD = 10
                if len(to_kill) > FORCE_THRESHOLD and not force:
                    report['need_force'] = True
                    report['note'] = f"{len(to_kill)} processes would be killed; re-run with force=True to proceed"
                    # Do not perform kills automatically without force
                    report['actions'].append({'kill': [], 'skipped': skipped})
                else:
                    actions = []
                    for p in to_kill:
                        pid = p.get('pid')
                        ok, out = self.kill_process(pid, name=p.get('name'), exe=p.get('exe'))
                        actions.append({'pid': pid, 'name': p.get('name'), 'exe': p.get('exe'), 'killed': ok, 'output': out})
                    report['actions'].append({'kill': actions, 'skipped': skipped})


            if quarantine:
                if compress:
                    ok, total, archive_path, errors = self._quarantine_files_archive(suspicious_files)
                    report['actions'].append({'quarantine_archive': {'quarantined': ok, 'total': total, 'archive': archive_path, 'errors': errors}})
                else:
                    q_actions = []
                    for f in suspicious_files:
                        path = f.get('path')
                        ok, info = self.quarantine_file(path)
                        q_actions.append({'path': path, 'quarantined': ok, 'dest': info})
                    report['actions'].append({'quarantine': q_actions})

            return report
        except KeyboardInterrupt:
            report.setdefault('error', 'Interrupted by user')
            return report
        finally:
            # Always attempt to write report (best-effort)
            report['written_at'] = datetime.now().isoformat()
            out_path = self._write_report(report)
            if out_path:
                report['report_path'] = out_path
            # Note: return value from finally doesn't change returned value above


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Sterilize environment (scan/quarantine/kill)')
    parser.add_argument('--run', action='store_true', help='Perform actions (requires --confirm)')
    parser.add_argument('--confirm', action='store_true', help='Confirm destructive actions')
    parser.add_argument('--kill', action='store_true', help='Kill suspicious processes')
    parser.add_argument('--quarantine', action='store_true', help='Quarantine suspicious files')
    parser.add_argument('--compress', action='store_true', help='Compress quarantined files into an archive to save storage')
    parser.add_argument('--dry-run', action='store_true', default=False, help='Perform dry run')
    parser.add_argument('--force', action='store_true', default=False, help='Force high-risk kills (bypass safety threshold and proceed)')
    args = parser.parse_args()

    s = Sterilizer()
    report = s.run(dry_run=args.dry_run or not args.run, confirm=args.confirm, kill=args.kill, quarantine=args.quarantine, compress=args.compress, force=args.force)
    print(json.dumps(report, indent=2))
