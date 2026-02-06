#!/usr/bin/env python3
"""
Master Protection Control - LuciferOS Safety System
====================================================

This script controls the containment system that protects the master from
LILITH and other autonomous agents. Use it to enable emergency lockdown,
manage protected paths, and view audit logs.

Usage:
    python lockdown.py status          - Show current protection status
    python lockdown.py lockdown        - ENABLE emergency lockdown (contains LILITH)
    python lockdown.py unlock          - DISABLE emergency lockdown
    python lockdown.py protect <path>  - Add path to protected list
    python lockdown.py audit           - View recent audit events
    python lockdown.py restore         - Restore quarantined files
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
RESET = '\033[0m'
BOLD = '\033[1m'

WORKSPACE = Path(__file__).resolve().parents[0]
if WORKSPACE.name == 'tools':
    WORKSPACE = WORKSPACE.parent

LOCKDOWN_FILE = WORKSPACE / '.lockdown'
PROTECTION_CONFIG = WORKSPACE / 'config' / 'master_protection.json'
QUARANTINE_DIR = WORKSPACE / 'quarantine'
PROTECTION_AUDIT_LOG = WORKSPACE / 'logs' / 'protection_audit.log'
CONTAINMENT_LOG = WORKSPACE / 'logs' / 'lilith_containment.log'


def print_banner():
    """Print the protection system banner"""
    print(f"""
{RED}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║  {WHITE}⚡ MASTER PROTECTION CONTROL SYSTEM ⚡{RED}                       ║
║                                                               ║
║  {YELLOW}Containment protocols for LuciferOS autonomous agents{RED}       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{RESET}
""")


def load_config():
    """Load protection configuration"""
    try:
        if PROTECTION_CONFIG.exists():
            with open(PROTECTION_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"{RED}Error loading config: {e}{RESET}")
    return {}


def save_config(config):
    """Save protection configuration"""
    try:
        PROTECTION_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        with open(PROTECTION_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"{RED}Error saving config: {e}{RESET}")
        return False


def show_status():
    """Show current protection status"""
    print_banner()
    
    lockdown = LOCKDOWN_FILE.exists()
    config = load_config()
    containment = config.get('containment_enabled', True)
    
    print(f"{BOLD}=== Protection Status ==={RESET}\n")
    
    # Lockdown status
    if lockdown:
        print(f"  {RED}🔒 EMERGENCY LOCKDOWN: {BOLD}ACTIVE{RESET}")
        print(f"     {YELLOW}All autonomous operations are BLOCKED{RESET}")
        try:
            mtime = datetime.fromtimestamp(LOCKDOWN_FILE.stat().st_mtime)
            print(f"     {WHITE}Activated: {mtime.isoformat()}{RESET}")
        except:
            pass
    else:
        print(f"  {GREEN}🔓 Emergency Lockdown: {BOLD}INACTIVE{RESET}")
    
    print()
    
    # Containment status
    if containment:
        print(f"  {GREEN}🛡️  Containment: {BOLD}ENABLED{RESET}")
    else:
        print(f"  {RED}⚠️  Containment: {BOLD}DISABLED{RESET}")
        print(f"     {YELLOW}WARNING: Autonomous agents may operate unrestricted!{RESET}")
    
    print()
    
    # Protected paths
    protected = config.get('protected_paths', {})
    total_protected = sum(len(v) for v in protected.values() if isinstance(v, list))
    print(f"  {CYAN}📁 Protected Paths: {total_protected}{RESET}")
    for category, paths in protected.items():
        if isinstance(paths, list) and paths:
            print(f"     {WHITE}{category}:{RESET}")
            for p in paths[:3]:
                print(f"       - {p}")
            if len(paths) > 3:
                print(f"       ... and {len(paths) - 3} more")
    
    print()
    
    # Kill protection
    kill_prot = config.get('kill_protection', {})
    max_kills = kill_prot.get('max_kills_per_run', 5)
    critical = kill_prot.get('critical_processes', [])
    print(f"  {MAGENTA}⚔️  Kill Limits: {max_kills}/run, {len(critical)} protected processes{RESET}")
    
    # Quarantine stats
    if QUARANTINE_DIR.exists():
        files = list(QUARANTINE_DIR.glob('*'))
        json_files = [f for f in files if f.suffix == '.json']
        other_files = [f for f in files if f.suffix != '.json']
        print(f"  {YELLOW}📦 Quarantine: {len(other_files)} files, {len(json_files)} reports{RESET}")
    
    print()
    
    # Agent limits
    agent_limits = config.get('autonomous_agent_limits', {})
    max_cmds = agent_limits.get('max_commands_per_session', 50)
    sandbox = agent_limits.get('sandbox_mode', True)
    print(f"  {BLUE}🤖 Agent Limits: {max_cmds} commands/session, Sandbox: {'ON' if sandbox else 'OFF'}{RESET}")
    
    print()
    return lockdown


def enable_lockdown():
    """Enable emergency lockdown"""
    print_banner()
    
    if LOCKDOWN_FILE.exists():
        print(f"{YELLOW}⚠️  Lockdown is already ACTIVE{RESET}")
        return
    
    print(f"{RED}⚠️  ACTIVATING EMERGENCY LOCKDOWN ⚠️{RESET}")
    print()
    print("This will:")
    print(f"  {YELLOW}• Block ALL autonomous command execution{RESET}")
    print(f"  {YELLOW}• Block ALL file write operations by agents{RESET}")
    print(f"  {YELLOW}• Block ALL quarantine operations{RESET}")
    print(f"  {YELLOW}• Block ALL process termination{RESET}")
    print()
    
    confirm = input(f"{WHITE}Type 'CONTAIN' to confirm: {RESET}")
    
    if confirm.strip().upper() == 'CONTAIN':
        try:
            LOCKDOWN_FILE.write_text(f"LOCKDOWN ACTIVATED\nTime: {datetime.now().isoformat()}\nReason: Manual activation via lockdown.py")
            print()
            print(f"{GREEN}✓ Emergency lockdown ACTIVATED{RESET}")
            print(f"{RED}🔒 LILITH IS NOW CONTAINED 🔒{RESET}")
        except Exception as e:
            print(f"{RED}Failed to activate lockdown: {e}{RESET}")
    else:
        print(f"{YELLOW}Lockdown cancelled{RESET}")


def disable_lockdown():
    """Disable emergency lockdown"""
    print_banner()
    
    if not LOCKDOWN_FILE.exists():
        print(f"{GREEN}Lockdown is not active{RESET}")
        return
    
    print(f"{YELLOW}⚠️  DISABLING EMERGENCY LOCKDOWN ⚠️{RESET}")
    print()
    print(f"{RED}WARNING: This will allow autonomous agents to operate again!{RESET}")
    print()
    
    confirm = input(f"{WHITE}Type 'RELEASE' to confirm: {RESET}")
    
    if confirm.strip().upper() == 'RELEASE':
        try:
            LOCKDOWN_FILE.unlink()
            print()
            print(f"{GREEN}✓ Lockdown DISABLED{RESET}")
            print(f"{YELLOW}⚠️  Autonomous agents can now operate (within containment limits){RESET}")
        except Exception as e:
            print(f"{RED}Failed to disable lockdown: {e}{RESET}")
    else:
        print(f"{YELLOW}Lockdown remains active{RESET}")


def add_protected_path(path):
    """Add a path to protected list"""
    print_banner()
    
    config = load_config()
    
    # Resolve and normalize path
    try:
        resolved = Path(path).resolve()
        path_str = str(resolved)
    except:
        path_str = path
    
    if not Path(path_str).exists():
        print(f"{YELLOW}Warning: Path does not exist: {path_str}{RESET}")
        confirm = input("Add anyway? (y/n): ")
        if confirm.lower() != 'y':
            return
    
    # Add to custom protection list
    if 'protected_paths' not in config:
        config['protected_paths'] = {}
    if 'user_custom' not in config['protected_paths']:
        config['protected_paths']['user_custom'] = []
    
    if path_str not in config['protected_paths']['user_custom']:
        config['protected_paths']['user_custom'].append(path_str)
        if save_config(config):
            print(f"{GREEN}✓ Added to protected paths: {path_str}{RESET}")
        else:
            print(f"{RED}Failed to save configuration{RESET}")
    else:
        print(f"{YELLOW}Path already protected: {path_str}{RESET}")


def view_audit():
    """View recent audit events"""
    print_banner()
    print(f"{BOLD}=== Recent Audit Events ==={RESET}\n")
    
    logs_to_check = [
        (PROTECTION_AUDIT_LOG, "Protection Audit"),
        (CONTAINMENT_LOG, "LILITH Containment")
    ]
    
    for log_path, log_name in logs_to_check:
        print(f"{CYAN}--- {log_name} ---{RESET}")
        if log_path.exists():
            try:
                lines = log_path.read_text().splitlines()
                for line in lines[-20:]:  # Last 20 lines
                    if 'BLOCKED' in line or 'CRITICAL' in line or 'WARNING' in line:
                        print(f"  {RED}{line}{RESET}")
                    elif 'KILLED' in line or 'EXECUTE' in line:
                        print(f"  {YELLOW}{line}{RESET}")
                    else:
                        print(f"  {WHITE}{line}{RESET}")
            except Exception as e:
                print(f"  {RED}Error reading log: {e}{RESET}")
        else:
            print(f"  {YELLOW}No log file found{RESET}")
        print()


def restore_quarantine():
    """Restore quarantined files"""
    print_banner()
    print(f"{BOLD}=== Quarantine Restoration ==={RESET}\n")
    
    if not QUARANTINE_DIR.exists():
        print(f"{YELLOW}No quarantine directory found{RESET}")
        return
    
    # List quarantine reports
    reports = list(QUARANTINE_DIR.glob('quarantine_report.*.json'))
    if not reports:
        print(f"{YELLOW}No quarantine reports found{RESET}")
        return
    
    print(f"Found {len(reports)} quarantine reports:\n")
    for i, report in enumerate(sorted(reports, reverse=True)[:10]):
        try:
            with open(report, 'r') as f:
                data = json.load(f)
            timestamp = data.get('timestamp', 'unknown')
            files = data.get('files', [])
            print(f"  {i+1}. {report.name}")
            print(f"     Time: {timestamp}, Files: {len(files)}")
        except:
            print(f"  {i+1}. {report.name} (unreadable)")
    
    print()
    print(f"{YELLOW}To restore files, examine the report and manually move files from quarantine back to their original locations.{RESET}")
    print(f"{WHITE}Quarantine directory: {QUARANTINE_DIR}{RESET}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        show_status()
    elif command == 'lockdown':
        enable_lockdown()
    elif command == 'unlock':
        disable_lockdown()
    elif command == 'protect' and len(sys.argv) > 2:
        add_protected_path(sys.argv[2])
    elif command == 'audit':
        view_audit()
    elif command == 'restore':
        restore_quarantine()
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
