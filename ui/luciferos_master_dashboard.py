#!/usr/bin/env python3
"""
LUCIFEROS MASTER DASHBOARD
Ultimate Integration - Combines Best of All UIs + Full System Integration
"""

import sys
import threading
import requests
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QPixmap

# Import all system components
from ui.attack_mode_selector import AttackModeSelector
from tools.ai_providers import AIProviderManager
from tools.autonomous_agent import AutonomousAgent
from tools.recon_toolkit import ReconToolkit
from tools.payload_embedder import PayloadEmbedder
from tools.browser_controller import BrowserController
from tools.attack_memory import AttackMemory

class LuciferOSMasterDashboard(QMainWindow):
    """Ultimate integrated dashboard combining all system capabilities"""

    # Thread-safe signals
    log_signal = pyqtSignal(str)
    results_signal = pyqtSignal(str)
    lilith_signal = pyqtSignal(str)
    status_signal = pyqtSignal(dict)
    browser_signal = pyqtSignal(dict)
    progress_signal = pyqtSignal(int, str)
    update_recon_results_signal = pyqtSignal(str, list)

    def __init__(self):
        super().__init__()

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

        self.init_master_ui()
        self.connect_signals()
        self.start_system_monitoring()

    def init_master_ui(self):
        """Initialize the master UI combining all best features"""
        self.setWindowTitle("LUCIFEROS - Ultimate Red Team Command Center")
        self.setGeometry(0, 0, 1920, 1080)

        # Dark theme with LuciferOS styling
        self.apply_luciferos_theme()

        # Main layout with collapsible panels (from streamlined)
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # LEFT SIDEBAR - Control Panel (collapsible sections)
        self.control_panel = self.create_control_panel()
        main_layout.addWidget(self.control_panel, 1)

        # CENTER - Main Content (tabbed interface)
        self.main_tabs = self.create_main_tabs()
        main_layout.addWidget(self.main_tabs, 2)

        # RIGHT - Monitoring & Logs (real-time updates)
        self.monitoring_panel = self.create_monitoring_panel()
        main_layout.addWidget(self.monitoring_panel, 1)

        # Status bar with system health
        self.create_status_bar()

        # Keyboard shortcuts (F1-F12 as mentioned in design)
        self.setup_keyboard_shortcuts()

    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for quick actions"""
        # F1-F5: Quick attack modes
        QShortcut(Qt.Key_F1, self, self.show_help)
        QShortcut(Qt.Key_F2, lambda: self.select_attack_mode("recon", self.start_reconnaissance))
        QShortcut(Qt.Key_F3, lambda: self.select_attack_mode("ai_autonomous", self.start_ai_autonomous))
        QShortcut(Qt.Key_F4, lambda: self.select_attack_mode("browser_hijack", self.start_browser_hijack))
        QShortcut(Qt.Key_F5, lambda: self.select_attack_mode("web_attack", self.start_web_attack))

        # F6-F8: Quick actions
        QShortcut(Qt.Key_F6, self, self.launch_attack)
        QShortcut(Qt.Key_F7, self, self.clear_logs)
        QShortcut(Qt.Key_F8, self, self.show_memory_stats)

        # Other shortcuts
        QShortcut(Qt.CTRL + Qt.Key_L, self, self.focus_target_input)
        QShortcut(Qt.Key_Escape, self, self.clear_inputs)

    def show_help(self):
        """Show keyboard shortcuts help"""
        help_text = """
LUCIFER-OS Keyboard Shortcuts:

F1: Show this help
F2: Reconnaissance mode
F3: AI Autonomous attack
F4: Browser hijack
F5: Web application attack
F6: Launch current attack
F7: Clear logs
F8: Show memory statistics

Ctrl+L: Focus target input
Escape: Clear all inputs
        """
        QMessageBox.information(self, "Keyboard Shortcuts", help_text)

    def focus_target_input(self):
        """Focus the target input field"""
        if hasattr(self, 'target_input'):
            self.target_input.setFocus()

    def clear_inputs(self):
        """Clear all input fields"""
        if hasattr(self, 'target_input'):
            self.target_input.clear()
        if hasattr(self, 'username_input'):
            self.username_input.clear()
        if hasattr(self, 'password_input'):
            self.password_input.clear()

    def clear_logs(self):
        """Clear all log displays"""
        if hasattr(self, 'log_display'):
            self.log_display.clear()
        if hasattr(self, 'progress_display'):
            self.progress_display.clear()

    def show_memory_stats(self):
        """Show attack memory statistics"""
        try:
            response = requests.get(f"{self.backend_url}/agent/memory/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data['stats']
                    stats_text = f"""
Attack Memory Statistics:

Generated Code:
- Total: {stats['generated_code']['total']}
- Avg Success Rate: {stats['generated_code']['avg_success_rate']}%
- Total Usage: {stats['generated_code']['total_usage']}

Attacks:
- Total: {stats['attacks']['total']}
- Success Rate: {stats['attacks']['success_rate']}%
- Unique Targets: {stats['attacks']['unique_targets']}

Loot:
- Total Items: {stats['loot']['total']}
- Types: {stats['loot']['types']}

Credentials:
- Total: {stats['credentials']['total']}
- Valid: {stats['credentials']['valid']}
                    """
                    QMessageBox.information(self, "Memory Statistics", stats_text.strip())
                else:
                    QMessageBox.warning(self, "Error", "Failed to get memory statistics")
            else:
                QMessageBox.warning(self, "Error", f"Backend error: {response.status_code}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not connect to backend: {str(e)}")

    def create_control_panel(self):
        """Control panel with collapsible sections"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Attack Mode Selection
        attack_section = CollapsibleSection("🎯 ATTACK MODES", self.create_attack_modes())
        layout.addWidget(attack_section)

        # AI Integration
        ai_section = CollapsibleSection("🤖 AI SYSTEMS", self.create_ai_panel())
        layout.addWidget(ai_section)

        # OpenClaw Integration
        openclaw_section = CollapsibleSection("🦞 OPENCLAW TOOLS", self.create_openclaw_panel())
        layout.addWidget(openclaw_section)

        # Script Injection
        script_section = CollapsibleSection("💉 SCRIPT INJECTION", self.create_script_injection())
        layout.addWidget(script_section)

        # Target Configuration
        target_section = CollapsibleSection("🎯 TARGET CONFIG", self.create_target_config())
        layout.addWidget(target_section)

        layout.addStretch()
        return panel

    def create_target_config(self):
        """Target configuration panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Target URL/IP input
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target:"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("example.com or 192.168.1.1")
        target_layout.addWidget(self.target_input)
        layout.addLayout(target_layout)

        # Port configuration
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(80)
        port_layout.addWidget(self.port_input)
        layout.addLayout(port_layout)

        # Protocol selection
        protocol_layout = QHBoxLayout()
        protocol_layout.addWidget(QLabel("Protocol:"))
        self.protocol_combo = QComboBox()
        self.protocol_combo.addItems(["http", "https", "tcp", "udp"])
        protocol_layout.addWidget(self.protocol_combo)
        layout.addLayout(protocol_layout)

        # Authentication (optional)
        auth_group = QGroupBox("Authentication (Optional)")
        auth_layout = QVBoxLayout(auth_group)

        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        username_layout.addWidget(self.username_input)
        auth_layout.addLayout(username_layout)

        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)
        auth_layout.addLayout(password_layout)

        layout.addWidget(auth_group)

        return widget

    def create_attack_modes(self):
        """Enhanced attack mode selector with all integrated tools"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Attack mode buttons
        modes = [
            ("🔍 Reconnaissance", "recon_mode", self.start_reconnaissance),
            ("🤖 AI Autonomous", "ai_autonomous", self.start_ai_autonomous),
            ("💣 Payload Engineering", "payload_engineer", self.start_payload_engineering),
            ("🦠 Browser Hijack", "browser_hijack", self.start_browser_hijack),
            ("💀 Local Override", "local_override", self.start_local_override),
            ("🌐 Web Application", "web_attack", self.start_web_attack),
        ]

        for name, mode_id, callback in modes:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, m=mode_id, c=callback: self.select_attack_mode(m, c))
            layout.addWidget(btn)

        # Launch button
        self.launch_btn = QPushButton("🚀 LAUNCH ATTACK")
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff0000;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)
        self.launch_btn.clicked.connect(self.launch_attack)
        layout.addWidget(self.launch_btn)

        return widget

    def create_ai_panel(self):
        """AI system integration panel with metrics"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # AI Provider Status Header
        status_label = QLabel("🤖 AI SYSTEMS STATUS")
        status_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #00ff00;")
        layout.addWidget(status_label)

        # AI Connection Metrics
        metrics_group = QGroupBox("Connection Statistics")
        metrics_layout = QGridLayout(metrics_group)

        # Connected Providers
        self.connected_providers_label = QLabel("✅ Connected: 0")
        self.connected_providers_label.setStyleSheet("color: #00ff00; font-weight: bold;")
        metrics_layout.addWidget(QLabel("AI Providers:"), 0, 0)
        metrics_layout.addWidget(self.connected_providers_label, 0, 1)

        # Failed Providers
        self.failed_providers_label = QLabel("❌ Failed: 0")
        self.failed_providers_label.setStyleSheet("color: #ff4444;")
        metrics_layout.addWidget(QLabel("Failed:"), 1, 0)
        metrics_layout.addWidget(self.failed_providers_label, 1, 1)

        # Token Statistics
        self.tokens_generated_label = QLabel("📈 Generated: 0")
        self.tokens_generated_label.setStyleSheet("color: #00aaff;")
        metrics_layout.addWidget(QLabel("Tokens:"), 2, 0)
        metrics_layout.addWidget(self.tokens_generated_label, 2, 1)

        self.tokens_refused_label = QLabel("🚫 Refused: 0")
        self.tokens_refused_label.setStyleSheet("color: #ffaa00;")
        metrics_layout.addWidget(QLabel("Refused:"), 3, 0)
        metrics_layout.addWidget(self.tokens_refused_label, 3, 1)

        layout.addWidget(metrics_group)

        # Provider List
        provider_group = QGroupBox("Active Providers")
        provider_layout = QVBoxLayout(provider_group)

        self.provider_list = QListWidget()
        self.provider_list.setMaximumHeight(150)
        provider_layout.addWidget(self.provider_list)

        layout.addWidget(provider_group)

        # Control Buttons
        button_layout = QHBoxLayout()

        # Refresh Status
        refresh_btn = QPushButton("🔄 Refresh Status")
        refresh_btn.clicked.connect(self.update_ai_status)
        button_layout.addWidget(refresh_btn)

        # Force Key Generation
        keygen_btn = QPushButton("🔑 Generate Keys")
        keygen_btn.clicked.connect(self.force_key_generation)
        button_layout.addWidget(keygen_btn)

        # AI Attack Planning
        plan_btn = QPushButton("🎯 AI Planning")
        plan_btn.clicked.connect(self.run_ai_planning)
        button_layout.addWidget(plan_btn)

        layout.addLayout(button_layout)

        # Hybrid AI Toggle
        self.hybrid_ai = QCheckBox("Enable Lilith + OpenClaw Hybrid AI")
        self.hybrid_ai.setChecked(True)
        layout.addWidget(self.hybrid_ai)

        # Last Update Timestamp
        self.last_update_label = QLabel("Last Update: Never")
        self.last_update_label.setStyleSheet("color: #888888; font-size: 10px;")
        layout.addWidget(self.last_update_label)

        # Initialize status
        self.update_ai_status()

        return widget

    def create_openclaw_panel(self):
        """OpenClaw CLI integration panel with dynamically loaded red team skills"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # OpenClaw Header
        header_label = QLabel("🦞 OPENCLAW RED TEAM TOOLS")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ff6b35;")
        layout.addWidget(header_label)

        # Status Section
        status_group = QGroupBox("System Status")
        status_layout = QHBoxLayout(status_group)

        self.openclaw_status = QLabel("🔄 Checking...")
        self.openclaw_status.setStyleSheet("color: #888888;")
        status_layout.addWidget(QLabel("OpenClaw:"))
        status_layout.addWidget(self.openclaw_status)

        self.openclaw_version = QLabel("v?.?.?")
        self.openclaw_version.setStyleSheet("color: #00aaff;")
        status_layout.addWidget(QLabel("Version:"))
        status_layout.addWidget(self.openclaw_version)

        layout.addWidget(status_group)

        # Skills will be loaded dynamically
        self.openclaw_skills_layout = QVBoxLayout()
        layout.addLayout(self.openclaw_skills_layout)

        # Control Section
        control_layout = QHBoxLayout()

        # Refresh Status
        refresh_btn = QPushButton("🔄 Check Status")
        refresh_btn.clicked.connect(self.update_openclaw_status)
        control_layout.addWidget(refresh_btn)

        # Custom Command
        self.openclaw_command = QLineEdit()
        self.openclaw_command.setPlaceholderText("Custom OpenClaw command...")
        control_layout.addWidget(self.openclaw_command)

        run_custom_btn = QPushButton("▶️ Run Custom")
        run_custom_btn.clicked.connect(self.run_custom_openclaw_command)
        control_layout.addWidget(run_custom_btn)

        layout.addLayout(control_layout)

        # Output Display
        self.openclaw_output = QTextEdit()
        self.openclaw_output.setReadOnly(True)
        self.openclaw_output.setMaximumHeight(200)
        self.openclaw_output.setPlaceholderText("OpenClaw command output will appear here...")
        layout.addWidget(self.openclaw_output)

        # Initialize status and load skills
        self.update_openclaw_status()

        return widget

    def create_script_injection(self):
        """JavaScript injection panel"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.js_input = QTextEdit()
        self.js_input.setPlaceholderText("Enter JavaScript code to execute...")
        self.js_input.setMaximumHeight(150)
        layout.addWidget(self.js_input)

        inject_btn = QPushButton("Execute JavaScript")
        inject_btn.clicked.connect(self.execute_javascript)
        layout.addWidget(inject_btn)

        return widget

    def create_main_tabs(self):
        """Main content tabs"""
        tabs = QTabWidget()

        # Attack Progress Tab
        self.progress_tab = self.create_progress_tab()
        tabs.addTab(self.progress_tab, "⚡ Attack Progress")

        # Lilith AI Tab
        self.lilith_tab = self.create_lilith_tab()
        tabs.addTab(self.lilith_tab, "🧠 Lilith AI")

        # Browser Control Tab
        self.browser_tab = self.create_browser_tab()
        tabs.addTab(self.browser_tab, "🌐 Browser Control")

        # Recon Results Tab
        self.recon_tab = self.create_recon_tab()
        tabs.addTab(self.recon_tab, "🔍 Reconnaissance")

        # Payload Engineering Tab
        self.payload_tab = self.create_payload_tab()
        tabs.addTab(self.payload_tab, "💣 Payload Engineering")

        return tabs

    def create_progress_tab(self):
        """Attack progress visualization"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.progress_display = QTextEdit()
        self.progress_display.setReadOnly(True)
        layout.addWidget(self.progress_display)

        # Progress bars for different phases
        self.progress_bars = {}
        phases = ["Recon", "Planning", "Execution", "Exfiltration", "Cleanup"]
        for phase in phases:
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            self.progress_bars[phase] = bar
            layout.addWidget(QLabel(f"{phase}:"))
            layout.addWidget(bar)

        return widget

    def create_lilith_tab(self):
        """Lilith AI interaction interface"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.lilith_output = QTextEdit()
        self.lilith_output.setReadOnly(True)
        layout.addWidget(self.lilith_output)

        self.lilith_input = QLineEdit()
        self.lilith_input.setPlaceholderText("Ask Lilith for attack guidance...")
        self.lilith_input.returnPressed.connect(self.query_lilith)
        layout.addWidget(self.lilith_input)

        return widget

    def create_browser_tab(self):
        """Browser control interface"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.url_input = QLineEdit()
        url_layout.addWidget(self.url_input)
        navigate_btn = QPushButton("Navigate")
        navigate_btn.clicked.connect(self.browser_navigate)
        url_layout.addWidget(navigate_btn)
        layout.addLayout(url_layout)

        # Browser controls
        controls_layout = QHBoxLayout()
        screenshot_btn = QPushButton("📸 Screenshot")
        screenshot_btn.clicked.connect(self.browser_screenshot)
        controls_layout.addWidget(screenshot_btn)

        cookies_btn = QPushButton("🍪 Get Cookies")
        cookies_btn.clicked.connect(self.browser_get_cookies)
        controls_layout.addWidget(cookies_btn)

        layout.addLayout(controls_layout)

        # Browser output
        self.browser_output = QTextEdit()
        self.browser_output.setReadOnly(True)
        layout.addWidget(self.browser_output)

        return widget

    def create_recon_tab(self):
        """Reconnaissance results display"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.recon_results = QTreeWidget()
        self.recon_results.setHeaderLabels(["Target", "Type", "Data", "Risk"])
        layout.addWidget(self.recon_results)

        return widget

    def create_payload_tab(self):
        """Payload engineering interface"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Payload type selector
        layout.addWidget(QLabel("🎯 PAYLOAD ENGINEERING"))
        
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Payload Type:"))
        self.payload_type = QComboBox()
        self.payload_type.addItems([
            "tracking_pixel", "js_payload", "phishing_link", 
            "html_smuggling", "malicious_svg", "hta_dropper", 
            "credential_harvester", "macro_document"
        ])
        type_layout.addWidget(self.payload_type)
        layout.addLayout(type_layout)

        # Target input
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target URL:"))
        self.payload_target = QLineEdit()
        self.payload_target.setPlaceholderText("https://target.com")
        target_layout.addWidget(self.payload_target)
        layout.addLayout(target_layout)

        # Generate button
        self.generate_payload_btn = QPushButton("⚡ Generate Payload")
        self.generate_payload_btn.clicked.connect(self.generate_payload)
        layout.addWidget(self.generate_payload_btn)

        # Payload output
        layout.addWidget(QLabel("📄 Generated Payload:"))
        self.payload_output = QTextEdit()
        self.payload_output.setReadOnly(True)
        layout.addWidget(self.payload_output)

        return widget

    def create_monitoring_panel(self):
        """Real-time monitoring panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        layout.addWidget(QLabel("📊 SYSTEM MONITORING"))

        # System health indicators
        self.health_indicators = {}
        systems = ["Backend", "AI Systems", "Browser", "Attack Memory"]
        for system in systems:
            indicator = QLabel(f"{system}: 🔄")
            self.health_indicators[system] = indicator
            layout.addWidget(indicator)

        # Real-time logs
        layout.addWidget(QLabel("📝 ACTIVITY LOGS"))
        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setMaximumHeight(300)
        layout.addWidget(self.activity_log)

        return panel

    def create_status_bar(self):
        """Status bar with system information and loot counter"""
        self.status_bar = self.statusBar()

        # Threat level indicator
        self.threat_indicator = QLabel("THREAT: LOW")
        self.threat_indicator.setStyleSheet("color: green; font-weight: bold;")
        self.status_bar.addWidget(self.threat_indicator)

        # Loot counter (as mentioned in design)
        self.loot_counter = QLabel("🍪 0 | 🔑 0 | 📄 0")
        self.loot_counter.setStyleSheet("color: #00ff00; font-weight: bold; margin-left: 20px;")
        self.status_bar.addWidget(self.loot_counter)

        # Update loot counter periodically
        self.loot_timer = QTimer()
        self.loot_timer.timeout.connect(self.update_loot_counter)
        self.loot_timer.start(5000)  # Update every 5 seconds

        self.status_bar.addPermanentWidget(QLabel("LuciferOS v2026.2.7"))

    def update_loot_counter(self):
        """Update the loot counter in status bar"""
        try:
            # Get loot stats from backend
            response = requests.get(f"{self.backend_url}/agent/memory/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data['stats']
                    cookies = stats['loot']['total']
                    creds = stats['credentials']['total']
                    files = 0  # Could be extended to track files separately
                    
                    self.loot_counter.setText(f"🍪 {cookies} | 🔑 {creds} | 📄 {files}")
        except:
            pass  # Silently fail if backend unavailable

    # ========================================
    # ATTACK MODE IMPLEMENTATIONS
    # ========================================

    def select_attack_mode(self, mode_id, callback):
        """Select attack mode"""
        self.current_attack_mode = mode_id
        self.log(f"Selected attack mode: {mode_id}")
        # Highlight selected button (implementation needed)

    def start_reconnaissance(self):
        """Start reconnaissance using recon_toolkit.py"""
        target = self.get_current_target()
        if not target:
            self.log("❌ No target specified for reconnaissance")
            return

        self.log(f"🔍 Starting reconnaissance on {target}")
        thread = threading.Thread(target=self._recon_thread, args=(target,))
        thread.daemon = True
        thread.start()
        self.active_threads.append(thread)

    def start_ai_autonomous(self):
        """Start AI autonomous attack using autonomous_agent.py"""
        target = self.get_current_target()
        if not target:
            self.log("❌ No target specified for AI autonomous attack")
            return

        self.log(f"🤖 Starting AI autonomous attack on {target}")
        thread = threading.Thread(target=self._ai_autonomous_thread, args=(target,))
        thread.daemon = True
        thread.start()
        self.active_threads.append(thread)

    def start_payload_engineering(self):
        """Start payload engineering using payload_embedder.py"""
        self.log("💣 Opening payload engineering interface")
        # Switch to payload engineering tab
        self.main_tabs.setCurrentWidget(self.payload_tab)

    def start_browser_hijack(self):
        """Start browser hijack attack"""
        self.log("🦠 Starting browser session hijack")
        # Implementation needed

    def start_local_override(self):
        """Start local system override"""
        self.log("💀 Starting local system override")
        # Implementation needed

    def start_web_attack(self):
        """Start web application attack"""
        self.log("🌐 Starting web application attack")
        # Implementation needed

    def launch_attack(self):
        """Launch the selected attack"""
        if not self.current_attack_mode:
            self.log("❌ No attack mode selected")
            return

        self.log(f"🚀 Launching attack: {self.current_attack_mode}")
        # Implementation needed

    # ========================================
    # AI SYSTEM INTEGRATION
    # ========================================

    def run_ai_planning(self):
        """Run AI attack planning using ai_powered_attacks.py"""
        target = self.get_current_target()
        if not target:
            self.log("❌ No target specified for AI planning")
            return

        self.log(f"🎯 Running AI attack planning for {target}")
        thread = threading.Thread(target=self._ai_planning_thread, args=(target,))
        thread.daemon = True
        thread.start()

    def query_lilith(self):
        """Query Lilith AI"""
        query = self.lilith_input.text().strip()
        if not query:
            return

        self.lilith_input.clear()
        self.log(f"🧠 Querying Lilith: {query}")

        thread = threading.Thread(target=self._lilith_query_thread, args=(query,))
        thread.daemon = True
        thread.start()

    # ========================================
    # BROWSER CONTROL
    # ========================================

    def browser_navigate(self):
        """Navigate browser to URL"""
        url = self.url_input.text().strip()
        if not url:
            return

        self.log(f"🌐 Navigating to: {url}")
        try:
            response = requests.post(f"{self.backend_url}/browser/navigate",
                                   json={"url": url})
            if response.status_code == 200:
                self.log("✅ Navigation successful")
            else:
                self.log(f"❌ Navigation failed: {response.text}")
        except Exception as e:
            self.log(f"❌ Browser error: {str(e)}")

    def browser_screenshot(self):
        """Take browser screenshot"""
        self.log("📸 Taking browser screenshot")
        # Implementation needed

    def browser_get_cookies(self):
        """Get browser cookies"""
        self.log("🍪 Getting browser cookies")
        try:
            response = requests.get(f"{self.backend_url}/browser/cookies")
            if response.status_code == 200:
                cookies = response.json()
                self.browser_output.append(f"Cookies: {json.dumps(cookies, indent=2)}")
                self.log("✅ Cookies retrieved")
            else:
                self.log(f"❌ Failed to get cookies: {response.text}")
        except Exception as e:
            self.log(f"❌ Cookie retrieval error: {str(e)}")

    def execute_javascript(self):
        """Execute JavaScript in browser"""
        script = self.js_input.toPlainText().strip()
        if not script:
            return

        self.log("💉 Executing JavaScript in browser")
        try:
            response = requests.post(f"{self.backend_url}/browser/execute_js",
                                   json={"script": script})
            if response.status_code == 200:
                result = response.json()
                self.browser_output.append(f"JS Result: {result}")
                self.log("✅ JavaScript executed successfully")
            else:
                self.log(f"❌ JavaScript execution failed: {response.text}")
        except Exception as e:
            self.log(f"❌ JavaScript error: {str(e)}")

    # ========================================
    # THREAD IMPLEMENTATIONS
    # ========================================

    def _recon_thread(self, target):
        """Reconnaissance thread"""
        try:
            self.progress_signal.emit(10, "Starting reconnaissance")

            # Use recon_toolkit.py
            results = self.recon_toolkit.scan_target(target)

            self.progress_signal.emit(100, "Reconnaissance complete")
            
            # Update UI with results
            self.update_recon_results_signal.emit(target, results)
            self.results_signal.emit(f"Recon Results: {json.dumps(results, indent=2)}")

        except Exception as e:
            self.log(f"❌ Recon error: {str(e)}")

    def _ai_autonomous_thread(self, target):
        """AI autonomous attack thread"""
        try:
            self.progress_signal.emit(10, "Initializing AI autonomous attack")

            # Use autonomous_agent.py
            agent = AutonomousAgent()
            agent.set_target(target)
            results = agent.run_full_chain('web_full')

            self.progress_signal.emit(100, "AI autonomous attack complete")
            self.results_signal.emit(f"AI Attack Results: {json.dumps(results, indent=2)}")

        except Exception as e:
            self.log(f"❌ AI autonomous error: {str(e)}")

    def _ai_planning_thread(self, target):
        """AI planning thread"""
        try:
            # Use ai_powered_attacks.py logic
            plan = self.ai_manager.plan_attack(target)
            self.lilith_signal.emit(f"AI Attack Plan: {json.dumps(plan, indent=2)}")

        except Exception as e:
            self.log(f"❌ AI planning error: {str(e)}")

    def _lilith_query_thread(self, query):
        """Lilith query thread"""
        try:
            response = self.ai_manager.chat(query)
            self.lilith_signal.emit(f"Lilith: {response}")

        except Exception as e:
            self.lilith_signal.emit(f"Error: {str(e)}")

    # ========================================
    # UTILITY METHODS
    # ========================================

    def get_current_target(self):
        """Get current target from UI"""
        target = self.target_input.text().strip()
        if not target:
            return None

        port = self.port_input.value()
        protocol = self.protocol_combo.currentText()

        # Format target with protocol and port
        if protocol in ["http", "https"]:
            if port != (443 if protocol == "https" else 80):
                target = f"{protocol}://{target}:{port}"
            else:
                target = f"{protocol}://{target}"
        else:
            target = f"{target}:{port}"

        return target

    def log(self, message):
        """Add message to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.append(f"[{timestamp}] {message}")

    def apply_luciferos_theme(self):
        """Apply LuciferOS dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
                color: #00ff00;
            }
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #1a1a1a;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                color: #00ff00;
                padding: 10px;
                border: 1px solid #333;
            }
            QTabBar::tab:selected {
                background-color: #ff0000;
                color: white;
            }
            QTextEdit, QLineEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 1px solid #333;
                padding: 5px;
            }
            QPushButton {
                background-color: #2a2a2a;
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #00ff00;
                color: black;
            }
            QLabel {
                color: #00ff00;
            }
        """)

    # ========================================
    # SIGNAL CONNECTIONS
    # ========================================

    def connect_signals(self):
        """Connect all signal handlers"""
        self.log_signal.connect(self.log)
        self.results_signal.connect(self.progress_display.append)
        self.lilith_signal.connect(self.lilith_output.append)
        self.progress_signal.connect(self.update_progress)
        self.update_recon_results_signal.connect(self.update_recon_results)

    def update_progress(self, value, phase):
        """Update progress bar for phase"""
        if phase in self.progress_bars:
            self.progress_bars[phase].setValue(value)

    def update_recon_results(self, target, results):
        """Update reconnaissance results in the UI"""
        self.recon_results.clear()
        
        for result in results:
            item = QTreeWidgetItem(self.recon_results)
            item.setText(0, target)
            item.setText(1, result.get('type', 'unknown'))
            item.setText(2, str(result.get('data', '')))
            item.setText(3, result.get('risk', 'unknown'))
            
            # Color code by risk level
            if result.get('risk') == 'high':
                item.setBackground(0, QColor(255, 100, 100))
                item.setBackground(1, QColor(255, 100, 100))
                item.setBackground(2, QColor(255, 100, 100))
                item.setBackground(3, QColor(255, 100, 100))
            elif result.get('risk') == 'medium':
                item.setBackground(0, QColor(255, 255, 100))
                item.setBackground(1, QColor(255, 255, 100))
                item.setBackground(2, QColor(255, 255, 100))
                item.setBackground(3, QColor(255, 255, 100))

    def generate_payload(self):
        """Generate payload using payload_embedder.py"""
        payload_type = self.payload_type.currentText()
        target = self.payload_target.text().strip()
        
        if not target:
            self.log("❌ No target specified for payload generation")
            return
        
        try:
            embedder = PayloadEmbedder()
            
            if payload_type == "tracking_pixel":
                payload = embedder.embed_tracking_pixel(f"<html><body></body></html>", "test@example.com")
            elif payload_type == "js_payload":
                payload = embedder.embed_js_payload(f"<html><body><h1>{target}</h1></body></html>")
            elif payload_type == "phishing_link":
                payload = embedder.create_phishing_link(target, "https://fake-site.com")
            elif payload_type == "html_smuggling":
                payload = embedder.create_html_smuggling_page(b"malicious content", "evil.exe")
            elif payload_type == "malicious_svg":
                payload = embedder.create_malicious_svg("alert('pwned')")
            elif payload_type == "hta_dropper":
                payload = embedder.create_hta_dropper("calc.exe")
            elif payload_type == "credential_harvester":
                payload = embedder.create_credential_harvester_page(target)
            elif payload_type == "macro_document":
                payload = embedder.create_macro_document_instructions()
            else:
                payload = "Unknown payload type"
            
            self.payload_output.setPlainText(payload)
            self.log(f"✅ Generated {payload_type} payload for {target}")
            
        except Exception as e:
            self.log(f"❌ Payload generation error: {str(e)}")

    def start_system_monitoring(self):
        """Start system health monitoring"""
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.check_system_health)
        self.monitor_timer.start(5000)  # Check every 5 seconds

    def check_system_health(self):
        """Check health of all system components"""
        try:
            # Check backend
            response = requests.get(f"{self.backend_url}/status", timeout=2)
            backend_status = "🟢" if response.status_code == 200 else "🔴"
            self.health_indicators["Backend"].setText(f"Backend: {backend_status}")

            # Check AI systems
            ai_status = "🟢" if self.ai_manager.is_healthy() else "🔴"
            self.health_indicators["AI Systems"].setText(f"AI Systems: {ai_status}")

            # Check browser
            browser_status = "🟢" if self.browser_controller.is_connected() else "🔴"
            self.health_indicators["Browser"].setText(f"Browser: {browser_status}")

            # Check attack memory
            memory_status = "🟢" if self.attack_memory.is_connected() else "🔴"
            self.health_indicators["Attack Memory"].setText(f"Attack Memory: {memory_status}")

        except Exception as e:
            self.log(f"Health check error: {str(e)}")

    def update_ai_status(self):
        """Update AI panel with real-time statistics"""
        try:
            if not hasattr(self, 'ai_manager') or not self.ai_manager:
                return

            # Get provider statistics
            provider_stats = self.ai_manager.get_provider_stats()

            # Update connected/failed counts
            connected_count = sum(1 for p in provider_stats.values() if p.get('connected', False))
            failed_count = len(provider_stats) - connected_count

            self.connected_providers_label.setText(f"✅ Connected: {connected_count}")
            self.failed_providers_label.setText(f"❌ Failed: {failed_count}")

            # Update token statistics
            total_tokens = sum(p.get('tokens_generated', 0) for p in provider_stats.values())
            refused_tokens = sum(p.get('tokens_refused', 0) for p in provider_stats.values())

            self.tokens_generated_label.setText(f"📈 Generated: {total_tokens:,}")
            self.tokens_refused_label.setText(f"🚫 Refused: {refused_tokens:,}")

            # Update provider list
            self.provider_list.clear()
            for provider_name, stats in provider_stats.items():
                status = "🟢" if stats.get('connected', False) else "🔴"
                tokens = stats.get('tokens_generated', 0)
                refused = stats.get('tokens_refused', 0)
                self.provider_list.addItem(f"{status} {provider_name} - Gen: {tokens:,} Ref: {refused:,}")

            # Update last update time
            self.last_update_label.setText(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")

        except Exception as e:
            self.log(f"AI status update error: {str(e)}")

    def force_key_generation(self):
        """Force regeneration of API keys for failed providers"""
        try:
            if not hasattr(self, 'ai_manager') or not self.ai_manager:
                return

            self.log("Forcing API key regeneration...")
            success_count = self.ai_manager.force_key_regeneration()

            self.log(f"Key regeneration completed. {success_count} keys regenerated.")
            self.update_ai_status()  # Refresh the display

        except Exception as e:
            self.log(f"Key regeneration error: {str(e)}")

    def run_ai_planning(self):
        """Run AI planning session for attack optimization"""
        try:
            if not hasattr(self, 'ai_manager') or not self.ai_manager:
                return

            self.log("Starting AI planning session...")

            # Get current targets and attack modes
            targets = getattr(self, 'current_targets', [])
            attack_modes = getattr(self, 'selected_attack_modes', [])

            if not targets:
                self.log("No targets selected for AI planning")
                return

            # Run AI planning
            plan = self.ai_manager.generate_attack_plan(targets, attack_modes)

            if plan:
                self.log("AI planning completed successfully")
                # Could display plan in a dialog or update UI
                self.log(f"Generated plan with {len(plan.get('steps', []))} steps")
            else:
                self.log("AI planning failed - no plan generated")

        except Exception as e:
            self.log(f"AI planning error: {str(e)}")

    def update_openclaw_status(self):
        """Update OpenClaw panel status and load skills"""
        try:
            # Check if OpenClaw is available via backend
            response = requests.get(f"{self.backend_url}/openclaw/status", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                self.openclaw_status.setText("🟢 Connected")
                self.openclaw_status.setStyleSheet("color: #00ff00;")
                self.openclaw_version.setText(status_data.get('version', 'v?.?.?'))
                
                # Load skills after successful status check
                self.load_openclaw_skills()
            else:
                self.openclaw_status.setText("🔴 Disconnected")
                self.openclaw_status.setStyleSheet("color: #ff4444;")
                self.openclaw_version.setText("Unknown")
        except Exception as e:
            self.log(f"OpenClaw status check error: {str(e)}")
            self.openclaw_status.setText("🔴 Error")
            self.openclaw_status.setStyleSheet("color: #ff4444;")
            self.openclaw_version.setText("Unknown")

    def load_openclaw_skills(self):
        """Load and display OpenClaw skills from backend"""
        try:
            response = requests.get(f"{self.backend_url}/openclaw/redteam-skills", timeout=10)
            if response.status_code == 200:
                skills_data = response.json()
                if skills_data.get('success'):
                    self.create_skill_buttons(skills_data['skills'])
                else:
                    self.log("Failed to load OpenClaw skills")
            else:
                self.log(f"Failed to fetch skills: HTTP {response.status_code}")
        except Exception as e:
            self.log(f"Error loading OpenClaw skills: {str(e)}")

    def create_skill_buttons(self, skills_dict):
        """Create skill buttons organized by priority"""
        # Clear existing skills layout
        while self.openclaw_skills_layout.count():
            child = self.openclaw_skills_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Priority colors and labels
        priority_config = {
            'critical': {'color': '#ff4444', 'label': '🔴 CRITICAL SKILLS'},
            'high': {'color': '#ffaa00', 'label': '🟡 HIGH PRIORITY SKILLS'},
            'useful': {'color': '#00aaff', 'label': '🔵 UTILITY SKILLS'}
        }
        
        # Skill icons mapping
        skill_icons = {
            'lilith': '🧠', 'healthcheck': '🛡️', 'coding-agent': '💻', 'github': '🐙',
            'discord': '💬', 'slack': '📱', 'himalaya': '📧', 'model-usage': '📊',
            'session-logs': '📝', 'voice-call': '📞', 'summarize': '📋', 'oracle': '🔮',
            'nano-pdf': '📄', 'openai-whisper': '🎤', 'openai-whisper-api': '🎙️',
            'openai-image-gen': '🎨', 'sherpa-onnx-tts': '🔊', 'camsnap': '📷',
            'peekaboo': '👀', 'tmux': '🖥️', 'trello': '📋', 'notion': '📝',
            'obsidian': '📓', 'blogwatcher': '📰', 'video-frames': '🎬',
            'weather': '🌤️', 'imsg': '💬', 'wacli': '📱', 'bird': '🐦',
            'gemini': '💎', 'skill-creator': '⚙️'
        }
        
        for priority, skills in skills_dict.items():
            if not skills:
                continue
                
            # Create group box for this priority
            group = QGroupBox(priority_config[priority]['label'])
            group.setStyleSheet(f"QGroupBox {{ font-weight: bold; border: 2px solid {priority_config[priority]['color']}; border-radius: 5px; margin-top: 1ex; }} QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }}")
            
            # Calculate grid layout
            cols = 3
            rows = (len(skills) + cols - 1) // cols
            grid_layout = QGridLayout(group)
            
            for i, skill in enumerate(skills):
                row = i // cols
                col = i % cols
                
                icon = skill_icons.get(skill, '🔧')
                btn = QPushButton(f"{icon} {skill.replace('-', ' ').title()}")
                btn.clicked.connect(lambda checked, s=skill: self.run_openclaw_skill(s))
                btn.setToolTip(f"Run {skill} skill")
                btn.setMinimumHeight(35)
                grid_layout.addWidget(btn, row, col)
            
            self.openclaw_skills_layout.addWidget(group)

    def run_openclaw_skill(self, skill_name):
        """Execute an OpenClaw skill via backend"""
        try:
            self.log(f"Running OpenClaw skill: {skill_name}")

            # Show loading state
            self.openclaw_output.clear()
            self.openclaw_output.append(f"🔄 Executing {skill_name} skill...")

            # Call backend OpenClaw endpoint
            response = requests.post(
                f"{self.backend_url}/openclaw/skill/{skill_name}",
                json={"parameters": {}},  # Empty params for now, can be extended
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                self.openclaw_output.clear()
                self.openclaw_output.append(f"✅ {skill_name.upper()} EXECUTED SUCCESSFULLY")
                self.openclaw_output.append("=" * 50)

                # Display results
                if 'output' in result:
                    self.openclaw_output.append("OUTPUT:")
                    self.openclaw_output.append(result['output'])
                if 'data' in result:
                    self.openclaw_output.append("\nDATA:")
                    self.openclaw_output.append(json.dumps(result['data'], indent=2))
                if 'summary' in result:
                    self.openclaw_output.append("\nSUMMARY:")
                    self.openclaw_output.append(result['summary'])

                self.log(f"OpenClaw skill {skill_name} completed successfully")
            else:
                error_msg = f"Failed to execute {skill_name}: HTTP {response.status_code}"
                self.openclaw_output.clear()
                self.openclaw_output.append(f"❌ {error_msg}")
                if response.text:
                    self.openclaw_output.append(f"Response: {response.text}")
                self.log(error_msg)

        except requests.exceptions.Timeout:
            error_msg = f"OpenClaw skill {skill_name} timed out"
            self.openclaw_output.clear()
            self.openclaw_output.append(f"⏰ {error_msg}")
            self.log(error_msg)
        except Exception as e:
            error_msg = f"OpenClaw skill {skill_name} error: {str(e)}"
            self.openclaw_output.clear()
            self.openclaw_output.append(f"❌ {error_msg}")
            self.log(error_msg)

    def run_custom_openclaw_command(self):
        """Execute a custom OpenClaw command"""
        try:
            command = self.openclaw_command.text().strip()
            if not command:
                self.log("No custom command entered")
                return

            self.log(f"Running custom OpenClaw command: {command}")

            # Show loading state
            self.openclaw_output.clear()
            self.openclaw_output.append(f"🔄 Executing custom command: {command}")

            # Call backend custom command endpoint
            response = requests.post(
                f"{self.backend_url}/openclaw/run",
                json={"command": command},
                timeout=60  # Longer timeout for custom commands
            )

            if response.status_code == 200:
                result = response.json()
                self.openclaw_output.clear()
                self.openclaw_output.append(f"✅ CUSTOM COMMAND EXECUTED")
                self.openclaw_output.append("=" * 50)

                # Display results
                if 'output' in result:
                    self.openclaw_output.append("OUTPUT:")
                    self.openclaw_output.append(result['output'])
                if 'error' in result:
                    self.openclaw_output.append("ERROR:")
                    self.openclaw_output.append(result['error'])

                self.log("Custom OpenClaw command completed successfully")
            else:
                error_msg = f"Custom command failed: HTTP {response.status_code}"
                self.openclaw_output.clear()
                self.openclaw_output.append(f"❌ {error_msg}")
                if response.text:
                    self.openclaw_output.append(f"Response: {response.text}")
                self.log(error_msg)

        except requests.exceptions.Timeout:
            error_msg = "Custom OpenClaw command timed out"
            self.openclaw_output.clear()
            self.openclaw_output.append(f"⏰ {error_msg}")
            self.log(error_msg)
        except Exception as e:
            error_msg = f"Custom command error: {str(e)}"
            self.openclaw_output.clear()
            self.openclaw_output.append(f"❌ {error_msg}")
            self.log(error_msg)


class CollapsibleSection(QWidget):
    """Collapsible section widget for modern UI"""

    def __init__(self, title, content_widget, parent=None):
        super().__init__(parent)
        self.content_widget = content_widget
        self.is_collapsed = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header button
        self.header = QPushButton(f"▼ {title}")
        self.header.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: #ff0000;
                border: none;
                padding: 10px;
                text-align: left;
                font-weight: bold;
            }
        """)
        self.header.clicked.connect(self.toggle_collapsed)
        layout.addWidget(self.header)

        # Content area
        self.content_area = QWidget()
        content_layout = QVBoxLayout(self.content_area)
        content_layout.addWidget(content_widget)
        layout.addWidget(self.content_area)

    def toggle_collapsed(self):
        """Toggle section visibility"""
        self.is_collapsed = not self.is_collapsed
        self.content_area.setVisible(not self.is_collapsed)
        self.header.setText(f"{'▶' if self.is_collapsed else '▼'} {self.header.text()[2:]}")


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("LuciferOS Master Dashboard")
    app.setApplicationVersion("2026.2.7")
    app.setOrganizationName("LuciferOS")
    
    # Create and show main window
    window = LuciferOSMasterDashboard()
    window.show()

    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()