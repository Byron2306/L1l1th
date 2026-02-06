#!/usr/bin/env python3
"""
LuciferOS - Attack Mode Selector
Initial configuration dialog for selecting attack vectors
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QTextEdit, QGroupBox, QRadioButton,
    QButtonGroup, QComboBox, QCheckBox, QStackedWidget,
    QWidget, QGridLayout, QSpinBox, QScrollArea, QDesktopWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap


class AttackModeSelector(QDialog):
    """Initial attack mode selection dialog"""
    
    mode_selected = pyqtSignal(dict)  # Emits configuration dict
    
    MODES = {
        'remote_unauth': {
            'name': 'Remote Reconnaissance',
            'description': 'Unauthenticated web reconnaissance and analysis.\nNo credentials required.',
            'icon': '🌐',
            'capabilities': [
                'Subdomain enumeration',
                'Technology fingerprinting',
                'Form & input discovery',
                'Cookie analysis',
                'JavaScript extraction',
                'Link harvesting',
                'XSS/SQLi surface mapping'
            ]
        },
        'remote_auth': {
            'name': 'Authenticated Attack',
            'description': 'Attack with stolen/provided credentials.\nSession hijacking, privilege escalation.',
            'icon': '🔐',
            'capabilities': [
                'Session hijacking',
                'Cookie injection',
                'Credential stuffing',
                'Authenticated API abuse',
                'Privilege escalation',
                'Data exfiltration',
                'Account takeover'
            ]
        },
        'browser_hijack': {
            'name': 'Browser Session Hijack',
            'description': 'Attach to existing authenticated session.\nExtract cookies from logged-in browser.',
            'icon': '🦠',
            'capabilities': [
                'Live session attachment',
                'Cookie extraction',
                'Token harvesting',
                'Session cloning',
                'Real-time manipulation',
                'Form auto-fill',
                'Screenshot capture'
            ]
        },
        'local_override': {
            'name': 'Local System Override',
            'description': 'KALI-like local attack mode.\nDirect system access and privilege escalation.',
            'icon': '💀',
            'capabilities': [
                'Privilege escalation',
                'Rootkit deployment',
                'Persistence installation',
                'Credential harvesting',
                'Memory extraction',
                'Keylogging',
                'Network pivoting'
            ]
        }
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LuciferOS - Attack Vector Selection")
        self.setModal(True)
        
        # Fullscreen for current resolution
        screen = QDesktopWidget().availableGeometry()
        self.setGeometry(screen)
        self.setMinimumSize(1000, 800)
        
        self.selected_mode = None
        self.config = {}
        
        self._apply_style()
        self._init_ui()
    
    def _apply_style(self):
        # Get the path to the background image
        import os
        bg_path = os.path.join(os.path.dirname(__file__), 'luciferos_bg.png').replace('\\', '/')
        
        self.setStyleSheet(f"""
            QDialog {{
                background-image: url('{bg_path}');
                background-repeat: no-repeat;
                background-position: center;
                background-color: #0a0a0a;
                color: #00ff00;
            }}
            QLabel {{
                color: #00ff00;
                background-color: rgba(0, 0, 0, 0.7);
            }}
            QGroupBox {{
                border: 2px solid #ff0000;
                margin-top: 10px;
                padding-top: 10px;
                color: #ff0000;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0.8);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QPushButton {{
                background-color: rgba(26, 26, 26, 0.9);
                color: #00ff00;
                border: 2px solid #00ff00;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 34, 0, 0.9);
                border-color: #00ff00;
            }}
            QPushButton:checked, QPushButton:pressed {{
                background-color: #ff0000;
                color: #ffffff;
                border-color: #ff0000;
            }}
            QPushButton#launch_btn {{
                background-color: #ff0000;
                color: #ffffff;
                border: none;
                font-size: 18px;
                padding: 20px;
            }}
            QPushButton#launch_btn:hover {{
                background-color: #ff3333;
            }}
            QLineEdit {{
                background-color: rgba(26, 26, 26, 0.9);
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 8px;
                font-family: 'Courier New';
            }}
            QTextEdit {{
                background-color: rgba(10, 10, 10, 0.9);
                color: #00ff00;
                border: 1px solid #333;
                font-family: 'Courier New';
            }}
            QComboBox {{
                background-color: rgba(26, 26, 26, 0.9);
                color: #00ff00;
                border: 1px solid #00ff00;
                padding: 5px;
            }}
            QRadioButton {{
                color: #00ff00;
            }}
            QRadioButton::indicator:checked {{
                background-color: #ff0000;
                border: 2px solid #ff0000;
            }}
            QCheckBox {{
                color: #00ff00;
                background-color: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: #ff0000;
            }}
        """)
    
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Make the entire dialog scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(25)  # More spacing between sections
        layout.setContentsMargins(40, 40, 40, 40)  # More margins
        
        # Header
        header = QLabel("🔥 LUCIFERA ATTACK VECTOR SELECTION 🔥")
        header.setFont(QFont("Courier New", 28, QFont.Bold))  # Larger font
        header.setStyleSheet("color: #ff0000;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        subtitle = QLabel("Select your attack mode and configure the target parameters")
        subtitle.setFont(QFont("Courier New", 14))  # Larger subtitle
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #ff0000;")
        sep.setMinimumHeight(2)
        layout.addWidget(sep)
        
        layout.addSpacing(10)
        
        # Mode selection buttons
        mode_group = QGroupBox("ATTACK MODE")
        mode_layout = QGridLayout(mode_group)
        mode_layout.setSpacing(20)  # More spacing between buttons
        mode_layout.setContentsMargins(20, 25, 20, 20)
        
        self.mode_buttons = {}
        self.mode_button_group = QButtonGroup(self)
        
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for i, (mode_id, mode_info) in enumerate(self.MODES.items()):
            btn = QPushButton(f"{mode_info['icon']}  {mode_info['name']}")
            btn.setCheckable(True)
            btn.setMinimumHeight(100)  # Taller buttons
            btn.setMinimumWidth(350)   # Wider buttons
            btn.setFont(QFont("Courier New", 14))  # Larger font
            btn.setProperty('mode_id', mode_id)
            btn.clicked.connect(lambda checked, m=mode_id: self._select_mode(m))
            
            row, col = positions[i]
            mode_layout.addWidget(btn, row, col)
            self.mode_buttons[mode_id] = btn
            self.mode_button_group.addButton(btn)
        
        layout.addWidget(mode_group)
        
        # Stacked widget for mode-specific config
        self.config_stack = QStackedWidget()
        
        # Empty placeholder
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_label = QLabel("← Select an attack mode to configure")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("color: #666;")
        empty_layout.addWidget(empty_label)
        self.config_stack.addWidget(empty_widget)
        
        # Remote Unauth config
        self.config_stack.addWidget(self._create_remote_unauth_config())
        
        # Remote Auth config
        self.config_stack.addWidget(self._create_remote_auth_config())
        
        # Browser Hijack config
        self.config_stack.addWidget(self._create_browser_hijack_config())
        
        # Local Override config
        self.config_stack.addWidget(self._create_local_override_config())
        
        layout.addWidget(self.config_stack)
        
        layout.addSpacing(10)
        
        # Mode description
        self.mode_description = QTextEdit()
        self.mode_description.setReadOnly(True)
        self.mode_description.setMinimumHeight(150)  # Taller description area
        self.mode_description.setMaximumHeight(200)
        self.mode_description.setFont(QFont("Courier New", 11))
        self.mode_description.setPlaceholderText("Mode capabilities will be shown here...")
        layout.addWidget(self.mode_description)
        
        layout.addSpacing(15)
        
        # Launch button
        launch_btn = QPushButton("🚀 LAUNCH ATTACK INTERFACE")
        launch_btn.setObjectName("launch_btn")
        launch_btn.setMinimumHeight(70)  # Taller launch button
        launch_btn.setFont(QFont("Courier New", 18, QFont.Bold))
        launch_btn.clicked.connect(self._launch)
        layout.addWidget(launch_btn)
        
        layout.addStretch()
        
        # Finalize scroll area
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
    
    def _create_remote_unauth_config(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        group = QGroupBox("REMOTE RECONNAISSANCE CONFIG")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)
        group_layout.setContentsMargins(15, 20, 15, 15)
        
        # Target URL
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target URL:"))
        self.remote_target = QLineEdit()
        self.remote_target.setPlaceholderText("https://target.com")
        self.remote_target.setMinimumWidth(400)
        self.remote_target.setMinimumHeight(35)
        target_layout.addWidget(self.remote_target)
        group_layout.addLayout(target_layout)
        
        group_layout.addSpacing(10)
        
        # Options
        options_layout = QHBoxLayout()
        options_layout.setSpacing(25)  # More space between checkboxes
        self.opt_screenshot = QCheckBox("Auto Screenshot")
        self.opt_screenshot.setChecked(True)
        options_layout.addWidget(self.opt_screenshot)
        
        self.opt_cookies = QCheckBox("Extract Cookies")
        self.opt_cookies.setChecked(True)
        options_layout.addWidget(self.opt_cookies)
        
        self.opt_forms = QCheckBox("Analyze Forms")
        self.opt_forms.setChecked(True)
        options_layout.addWidget(self.opt_forms)
        
        self.opt_subdomains = QCheckBox("Enumerate Subdomains")
        self.opt_subdomains.setChecked(True)
        options_layout.addWidget(self.opt_subdomains)
        options_layout.addStretch()
        
        group_layout.addLayout(options_layout)
        
        group_layout.addSpacing(10)
        
        # Browser mode
        browser_layout = QHBoxLayout()
        browser_layout.addWidget(QLabel("Browser Mode:"))
        self.browser_mode = QComboBox()
        self.browser_mode.addItems(["Visible (Debug)", "Headless (Stealth)"])
        self.browser_mode.setMinimumWidth(200)
        self.browser_mode.setMinimumHeight(30)
        browser_layout.addWidget(self.browser_mode)
        browser_layout.addStretch()
        group_layout.addLayout(browser_layout)
        
        layout.addWidget(group)
        layout.addStretch()
        return widget
    
    def _create_remote_auth_config(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        group = QGroupBox("AUTHENTICATED ATTACK CONFIG")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)
        group_layout.setContentsMargins(15, 20, 15, 15)
        
        # Target
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target URL:"))
        self.auth_target = QLineEdit()
        self.auth_target.setPlaceholderText("https://target.com/login")
        self.auth_target.setMinimumWidth(400)
        self.auth_target.setMinimumHeight(35)
        target_layout.addWidget(self.auth_target)
        group_layout.addLayout(target_layout)
        
        group_layout.addSpacing(10)
        
        # Credentials
        cred_group = QGroupBox("Credentials")
        cred_layout = QGridLayout(cred_group)
        cred_layout.setSpacing(10)
        cred_layout.setContentsMargins(15, 20, 15, 15)
        
        cred_layout.addWidget(QLabel("Username:"), 0, 0)
        self.auth_username = QLineEdit()
        self.auth_username.setPlaceholderText("user@target.com")
        self.auth_username.setMinimumWidth(350)
        self.auth_username.setMinimumHeight(35)
        cred_layout.addWidget(self.auth_username, 0, 1)
        
        cred_layout.addWidget(QLabel("Password:"), 1, 0)
        self.auth_password = QLineEdit()
        self.auth_password.setEchoMode(QLineEdit.Password)
        self.auth_password.setPlaceholderText("password or token")
        self.auth_password.setMinimumWidth(350)
        self.auth_password.setMinimumHeight(35)
        cred_layout.addWidget(self.auth_password, 1, 1)
        
        group_layout.addWidget(cred_group)
        
        group_layout.addSpacing(10)
        
        # Attack type
        attack_layout = QHBoxLayout()
        attack_layout.addWidget(QLabel("Attack Type:"))
        self.auth_attack_type = QComboBox()
        self.auth_attack_type.addItems([
            "Credential Stuffing",
            "Session Hijacking",
            "Privilege Escalation",
            "Data Exfiltration",
            "API Abuse"
        ])
        self.auth_attack_type.setMinimumWidth(200)
        self.auth_attack_type.setMinimumHeight(30)
        attack_layout.addWidget(self.auth_attack_type)
        attack_layout.addStretch()
        group_layout.addLayout(attack_layout)
        
        layout.addWidget(group)
        layout.addStretch()
        return widget
    
    def _create_browser_hijack_config(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        group = QGroupBox("BROWSER SESSION HIJACK CONFIG")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)
        group_layout.setContentsMargins(15, 20, 15, 15)
        
        # Info
        info = QLabel("⚠️ This mode attaches to an existing browser session.\n"
                     "The browser will open with your saved cookies and sessions.")
        info.setStyleSheet("color: #ffaa00; padding: 10px;")
        info.setFont(QFont("Courier New", 11))
        group_layout.addWidget(info)
        
        group_layout.addSpacing(10)
        
        # Target to navigate to
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Navigate To:"))
        self.hijack_target = QLineEdit()
        self.hijack_target.setPlaceholderText("https://target.com/dashboard (after auth)")
        self.hijack_target.setMinimumWidth(400)
        self.hijack_target.setMinimumHeight(35)
        target_layout.addWidget(self.hijack_target)
        group_layout.addLayout(target_layout)
        
        group_layout.addSpacing(10)
        
        # Options
        options_layout = QVBoxLayout()
        options_layout.setSpacing(8)
        
        self.hijack_extract_all = QCheckBox("Extract all cookies on load")
        self.hijack_extract_all.setChecked(True)
        options_layout.addWidget(self.hijack_extract_all)
        
        self.hijack_extract_storage = QCheckBox("Extract localStorage/sessionStorage")
        self.hijack_extract_storage.setChecked(True)
        options_layout.addWidget(self.hijack_extract_storage)
        
        self.hijack_monitor = QCheckBox("Monitor network requests")
        self.hijack_monitor.setChecked(False)
        options_layout.addWidget(self.hijack_monitor)
        
        self.hijack_screenshot = QCheckBox("Screenshot on page load")
        self.hijack_screenshot.setChecked(True)
        options_layout.addWidget(self.hijack_screenshot)
        
        group_layout.addLayout(options_layout)
        
        layout.addWidget(group)
        layout.addStretch()
        return widget
    
    def _create_local_override_config(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        group = QGroupBox("LOCAL SYSTEM OVERRIDE CONFIG")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)
        group_layout.setContentsMargins(15, 20, 15, 15)
        
        # Warning
        warning = QLabel("💀 WARNING: This mode executes commands on the LOCAL system.\n"
                        "Ensure you have proper authorization.")
        warning.setStyleSheet("color: #ff0000; font-weight: bold; padding: 10px;")
        warning.setFont(QFont("Courier New", 11))
        group_layout.addWidget(warning)
        
        group_layout.addSpacing(10)
        
        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Override Mode:"))
        self.local_mode = QComboBox()
        self.local_mode.addItems([
            "Privilege Escalation",
            "Persistence Installation",
            "Credential Harvesting",
            "Network Pivot",
            "Full System Compromise"
        ])
        self.local_mode.setMinimumWidth(250)
        self.local_mode.setMinimumHeight(30)
        mode_layout.addWidget(self.local_mode)
        mode_layout.addStretch()
        group_layout.addLayout(mode_layout)
        
        group_layout.addSpacing(10)
        
        # Target network
        network_layout = QHBoxLayout()
        network_layout.addWidget(QLabel("Target Network:"))
        self.local_network = QLineEdit()
        self.local_network.setPlaceholderText("192.168.1.0/24 (optional)")
        self.local_network.setMinimumWidth(300)
        self.local_network.setMinimumHeight(35)
        network_layout.addWidget(self.local_network)
        network_layout.addStretch()
        group_layout.addLayout(network_layout)
        
        group_layout.addSpacing(10)
        
        # Options
        self.local_stealth = QCheckBox("Stealth Mode (minimize traces)")
        self.local_stealth.setChecked(True)
        group_layout.addWidget(self.local_stealth)
        
        self.local_persist = QCheckBox("Install persistence")
        self.local_persist.setChecked(False)
        group_layout.addWidget(self.local_persist)
        
        layout.addWidget(group)
        layout.addStretch()
        return widget
    
    def _select_mode(self, mode_id):
        self.selected_mode = mode_id
        
        # Update button states
        for mid, btn in self.mode_buttons.items():
            btn.setChecked(mid == mode_id)
        
        # Show appropriate config
        mode_index = list(self.MODES.keys()).index(mode_id) + 1
        self.config_stack.setCurrentIndex(mode_index)
        
        # Update description
        mode_info = self.MODES[mode_id]
        capabilities = "\n".join(f"  • {cap}" for cap in mode_info['capabilities'])
        self.mode_description.setText(
            f"{mode_info['icon']} {mode_info['name']}\n"
            f"{mode_info['description']}\n\n"
            f"Capabilities:\n{capabilities}"
        )
    
    def _launch(self):
        if not self.selected_mode:
            self.mode_description.setText("⚠️ Please select an attack mode first!")
            return
        
        # Build config based on mode
        self.config = {
            'mode': self.selected_mode,
            'mode_name': self.MODES[self.selected_mode]['name']
        }
        
        if self.selected_mode == 'remote_unauth':
            target = self.remote_target.text().strip()
            # Validate URL
            if target and not target.startswith(('http://', 'https://')):
                target = 'https://' + target
            self.config.update({
                'target': target,
                'screenshot': self.opt_screenshot.isChecked(),
                'cookies': self.opt_cookies.isChecked(),
                'forms': self.opt_forms.isChecked(),
                'subdomains': self.opt_subdomains.isChecked(),
                'headless': self.browser_mode.currentIndex() == 1
            })
        
        elif self.selected_mode == 'remote_auth':
            target = self.auth_target.text().strip()
            if target and not target.startswith(('http://', 'https://')):
                target = 'https://' + target
            self.config.update({
                'target': target,
                'username': self.auth_username.text(),
                'password': self.auth_password.text(),
                'attack_type': self.auth_attack_type.currentText(),
                'headless': False
            })
        
        elif self.selected_mode == 'browser_hijack':
            target = self.hijack_target.text().strip()
            if target and not target.startswith(('http://', 'https://')):
                target = 'https://' + target
            self.config.update({
                'target': target,
                'extract_cookies': self.hijack_extract_all.isChecked(),
                'extract_storage': self.hijack_extract_storage.isChecked(),
                'monitor_network': self.hijack_monitor.isChecked(),
                'screenshot': self.hijack_screenshot.isChecked(),
                'headless': False
            })
        
        elif self.selected_mode == 'local_override':
            self.config.update({
                'local_mode': self.local_mode.currentText(),
                'target_network': self.local_network.text(),
                'stealth': self.local_stealth.isChecked(),
                'persist': self.local_persist.isChecked()
            })
        
        self.mode_selected.emit(self.config)
        self.accept()
    
    def get_config(self):
        return self.config


class QuickTargetDialog(QDialog):
    """Quick target input for rapid attacks"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quick Target")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.setStyleSheet("""
            QDialog { background-color: #0a0a0a; }
            QLabel { color: #00ff00; }
            QLineEdit { 
                background-color: #1a1a1a; 
                color: #00ff00; 
                border: 1px solid #00ff00; 
                padding: 10px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #ff0000;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Enter target URL:"))
        
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("https://target.com")
        self.target_input.setMinimumWidth(400)  # Prevent URL truncation
        self.target_input.returnPressed.connect(self.accept)
        layout.addWidget(self.target_input)
        
        btn_layout = QHBoxLayout()
        
        go_btn = QPushButton("GO")
        go_btn.clicked.connect(self.accept)
        btn_layout.addWidget(go_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #333;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def get_target(self):
        return self.target_input.text()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = AttackModeSelector()
    
    if dialog.exec_() == QDialog.Accepted:
        print("Selected config:", dialog.get_config())
    
    sys.exit()
