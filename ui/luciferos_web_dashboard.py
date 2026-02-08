#!/usr/bin/env python3
"""
LUCIFEROS WEB DASHBOARD
Web-based version of the master dashboard with browser support
"""

from flask import Flask, render_template, request, jsonify, Response
import threading
import requests
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
import time
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import system components
from tools.ai_providers import AIProviderManager
from tools.autonomous_agent import AutonomousAgent
from tools.recon_toolkit import ReconToolkit
from tools.payload_embedder import PayloadEmbedder
from tools.browser_controller import BrowserController
from tools.attack_memory import AttackMemory

class LuciferOSWebDashboard:
    """Web-based dashboard for LUCIFER-OS"""

    def __init__(self):
        self.app = Flask(__name__,
                        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                        static_folder=os.path.join(os.path.dirname(__file__), 'static'))

        # System initialization
        self.backend_url = "http://127.0.0.1:5000"
        self.attack_memory = AttackMemory()
        self.ai_manager = AIProviderManager()
        self.browser_controller = BrowserController()
        self.payload_engineer = PayloadEmbedder()
        self.recon_toolkit = ReconToolkit()

        # UI State
        self.current_attack_mode = None
        self.active_threads = []
        self.attack_progress = {}
        self.system_logs = []
        self.max_logs = 1000

        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/')
        def index():
            return render_template('dashboard.html')

        @self.app.route('/api/system/status')
        def system_status():
            try:
                # Check backend health
                backend_health = False
                try:
                    response = requests.get(f"{self.backend_url}/health", timeout=2)
                    backend_health = response.status_code == 200
                except:
                    backend_health = False

                # Check OpenClaw gateway
                gateway_health = False
                try:
                    response = requests.get("http://127.0.0.1:18789/health", timeout=2)
                    gateway_health = response.status_code == 200
                except:
                    gateway_health = False

                return jsonify({
                    'backend': backend_health,
                    'gateway': gateway_health,
                    'timestamp': datetime.now().isoformat(),
                    'active_threads': len(self.active_threads),
                    'current_mode': self.current_attack_mode
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/logs')
        def get_logs():
            return jsonify({
                'logs': self.system_logs[-100:],  # Last 100 logs
                'total': len(self.system_logs)
            })

        @self.app.route('/api/logs/stream')
        def stream_logs():
            def generate():
                last_index = len(self.system_logs)
                while True:
                    if len(self.system_logs) > last_index:
                        new_logs = self.system_logs[last_index:]
                        last_index = len(self.system_logs)
                        yield f"data: {json.dumps(new_logs)}\n\n"
                    time.sleep(1)
            return Response(generate(), mimetype='text/event-stream')

        @self.app.route('/api/attack/start/<mode>', methods=['POST'])
        def start_attack(mode):
            try:
                data = request.get_json() or {}
                target = data.get('target', '')

                self.log(f"Starting attack mode: {mode} on target: {target}")

                # Start attack in background thread
                thread = threading.Thread(target=self.run_attack_mode, args=(mode, target))
                thread.daemon = True
                thread.start()
                self.active_threads.append(thread)

                return jsonify({'status': 'started', 'mode': mode, 'target': target})
            except Exception as e:
                self.log(f"Error starting attack: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/attack/stop', methods=['POST'])
        def stop_attack():
            try:
                self.current_attack_mode = None
                # Stop all active threads
                for thread in self.active_threads:
                    if thread.is_alive():
                        thread.join(timeout=1)
                self.active_threads.clear()
                self.log("All attacks stopped")
                return jsonify({'status': 'stopped'})
            except Exception as e:
                self.log(f"Error stopping attack: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/ai/query', methods=['POST'])
        def ai_query():
            try:
                data = request.get_json()
                query = data.get('query', '')
                provider = data.get('provider', 'auto')

                self.log(f"AI Query: {query[:50]}...")

                # Use AI manager
                response = self.ai_manager.query(query, provider=provider)

                return jsonify({
                    'response': response,
                    'provider': provider,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                self.log(f"AI query error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/recon/start', methods=['POST'])
        def start_recon():
            try:
                data = request.get_json()
                target = data.get('target', '')
                scan_type = data.get('type', 'basic')

                self.log(f"Starting reconnaissance on {target} (type: {scan_type})")

                # Start recon in background
                thread = threading.Thread(target=self.run_recon, args=(target, scan_type))
                thread.daemon = True
                thread.start()
                self.active_threads.append(thread)

                return jsonify({'status': 'started', 'target': target, 'type': scan_type})
            except Exception as e:
                self.log(f"Recon error: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/browser/control', methods=['POST'])
        def browser_control():
            try:
                data = request.get_json()
                action = data.get('action', '')
                url = data.get('url', '')

                if action == 'navigate':
                    self.browser_controller.navigate(url)
                    self.log(f"Browser navigated to: {url}")
                elif action == 'screenshot':
                    screenshot = self.browser_controller.take_screenshot()
                    self.log("Browser screenshot taken")
                    return jsonify({'screenshot': screenshot})
                elif action == 'inject':
                    script = data.get('script', '')
                    result = self.browser_controller.inject_javascript(script)
                    self.log("JavaScript injected into browser")
                    return jsonify({'result': result})

                return jsonify({'status': 'success', 'action': action})
            except Exception as e:
                self.log(f"Browser control error: {e}")
                return jsonify({'error': str(e)}), 500

    def log(self, message):
        """Add log message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.system_logs.append(log_entry)

        # Keep only max logs
        if len(self.system_logs) > self.max_logs:
            self.system_logs = self.system_logs[-self.max_logs:]

        print(log_entry)

    def run_attack_mode(self, mode, target):
        """Run attack mode in background"""
        try:
            self.current_attack_mode = mode
            self.log(f"Executing {mode} attack on {target}")

            # Simulate attack execution (replace with actual logic)
            for i in range(10):
                if self.current_attack_mode != mode:
                    break  # Stop if mode changed
                time.sleep(1)
                self.log(f"{mode} progress: {i+1}/10")

            self.log(f"{mode} attack completed on {target}")
        except Exception as e:
            self.log(f"Attack error: {e}")
        finally:
            if self.current_attack_mode == mode:
                self.current_attack_mode = None

    def run_recon(self, target, scan_type):
        """Run reconnaissance"""
        try:
            self.log(f"Running {scan_type} reconnaissance on {target}")

            # Use recon toolkit
            results = self.recon_toolkit.scan(target, scan_type)

            self.log(f"Recon completed: {len(results)} findings")
        except Exception as e:
            self.log(f"Recon error: {e}")

    def run(self, host='0.0.0.0', port=8080, debug=False):
        """Run the web dashboard"""
        self.log(f"Starting LuciferOS Web Dashboard on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug, threaded=True)

# Global dashboard instance
dashboard = LuciferOSWebDashboard()

if __name__ == '__main__':
    dashboard.run()</content>
<parameter name="filePath">/workspaces/LUCIFER-OS/ui/luciferos_web_dashboard.py