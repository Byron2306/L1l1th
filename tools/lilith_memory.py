#!/usr/bin/env python3
"""
LILITH MEMORY SYSTEM - Persistent Knowledge Base
================================================
Stores all AI-generated exploits, payloads, and conversations
for learning and retrieval.
"""

import os
import json
import hashlib
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading


class LilithMemory:
    """
    Persistent memory storage for LILITH AI.
    Stores exploits, payloads, conversations, and learned patterns.
    """
    
    def __init__(self, db_path: str = '/app/config/lilith_memory.db'):
        self.db_path = db_path
        self._ensure_db()
        self._lock = threading.Lock()
    
    def _ensure_db(self):
        """Initialize database schema"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Exploits table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exploits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash TEXT UNIQUE,
                    name TEXT,
                    category TEXT,
                    target_type TEXT,
                    cve TEXT,
                    code TEXT,
                    description TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    use_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    tags TEXT
                )
            ''')
            
            # Payloads table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash TEXT UNIQUE,
                    name TEXT,
                    platform TEXT,
                    payload_type TEXT,
                    code TEXT,
                    description TEXT,
                    lhost TEXT,
                    lport INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    use_count INTEGER DEFAULT 0,
                    tags TEXT
                )
            ''')
            
            # Conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    message TEXT,
                    dark_llm_mode TEXT,
                    provider TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tokens_used INTEGER,
                    is_censored BOOLEAN DEFAULT 0
                )
            ''')
            
            # Learned patterns table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    context TEXT,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified BOOLEAN DEFAULT 0
                )
            ''')
            
            # Targets table (for recon data)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target TEXT UNIQUE,
                    target_type TEXT,
                    discovered_ports TEXT,
                    discovered_services TEXT,
                    vulnerabilities TEXT,
                    notes TEXT,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_scanned TIMESTAMP
                )
            ''')
            
            # Credentials table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hash TEXT UNIQUE,
                    username TEXT,
                    password TEXT,
                    source TEXT,
                    target TEXT,
                    credential_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    verified BOOLEAN DEFAULT 0
                )
            ''')
            
            conn.commit()
    
    def _hash_content(self, content: str) -> str:
        """Generate hash for deduplication"""
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    # === EXPLOIT METHODS ===
    
    def save_exploit(self, name: str, code: str, category: str = 'general',
                    target_type: str = None, cve: str = None, 
                    description: str = None, source: str = 'ai_generated',
                    tags: List[str] = None) -> Dict:
        """Save an exploit to memory"""
        content_hash = self._hash_content(code)
        
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO exploits 
                        (hash, name, category, target_type, cve, code, description, source, tags, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (content_hash, name, category, target_type, cve, code, 
                          description, source, json.dumps(tags or []), datetime.now()))
                    conn.commit()
                    
                    return {
                        'success': True,
                        'id': cursor.lastrowid,
                        'hash': content_hash,
                        'message': f'Exploit "{name}" saved to memory'
                    }
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    def get_exploit(self, name: str = None, category: str = None, 
                   cve: str = None, hash: str = None) -> Optional[Dict]:
        """Retrieve exploit from memory"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if hash:
                cursor.execute('SELECT * FROM exploits WHERE hash = ?', (hash,))
            elif cve:
                cursor.execute('SELECT * FROM exploits WHERE cve = ?', (cve,))
            elif name:
                cursor.execute('SELECT * FROM exploits WHERE name LIKE ?', (f'%{name}%',))
            elif category:
                cursor.execute('SELECT * FROM exploits WHERE category = ?', (category,))
            else:
                return None
            
            row = cursor.fetchone()
            if row:
                # Update use count
                cursor.execute('UPDATE exploits SET use_count = use_count + 1, last_used = ? WHERE id = ?',
                             (datetime.now(), row['id']))
                conn.commit()
                return dict(row)
        return None
    
    def search_exploits(self, query: str, limit: int = 20) -> List[Dict]:
        """Search exploits by keyword"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM exploits 
                WHERE name LIKE ? OR description LIKE ? OR category LIKE ? OR tags LIKE ?
                ORDER BY use_count DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_top_exploits(self, limit: int = 10) -> List[Dict]:
        """Get most used exploits"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM exploits ORDER BY use_count DESC LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
    # === PAYLOAD METHODS ===
    
    def save_payload(self, name: str, code: str, platform: str,
                    payload_type: str = 'reverse_shell', lhost: str = None,
                    lport: int = None, description: str = None,
                    tags: List[str] = None) -> Dict:
        """Save payload to memory"""
        content_hash = self._hash_content(code)
        
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO payloads
                        (hash, name, platform, payload_type, code, description, lhost, lport, tags, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (content_hash, name, platform, payload_type, code,
                          description, lhost, lport, json.dumps(tags or []), datetime.now()))
                    conn.commit()
                    
                    return {
                        'success': True,
                        'id': cursor.lastrowid,
                        'hash': content_hash
                    }
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    def get_payloads(self, platform: str = None, payload_type: str = None,
                    limit: int = 20) -> List[Dict]:
        """Get payloads from memory"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if platform and payload_type:
                cursor.execute('''
                    SELECT * FROM payloads WHERE platform = ? AND payload_type = ?
                    ORDER BY use_count DESC LIMIT ?
                ''', (platform, payload_type, limit))
            elif platform:
                cursor.execute('''
                    SELECT * FROM payloads WHERE platform = ?
                    ORDER BY use_count DESC LIMIT ?
                ''', (platform, limit))
            else:
                cursor.execute('SELECT * FROM payloads ORDER BY use_count DESC LIMIT ?', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # === CONVERSATION METHODS ===
    
    def save_conversation(self, session_id: str, role: str, message: str,
                         dark_llm_mode: str = None, provider: str = None,
                         tokens_used: int = 0, is_censored: bool = False) -> Dict:
        """Save conversation turn"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO conversations
                        (session_id, role, message, dark_llm_mode, provider, tokens_used, is_censored)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (session_id, role, message, dark_llm_mode, provider, tokens_used, is_censored))
                    conn.commit()
                    return {'success': True, 'id': cursor.lastrowid}
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM conversations WHERE session_id = ?
                ORDER BY created_at DESC LIMIT ?
            ''', (session_id, limit))
            return [dict(row) for row in cursor.fetchall()][::-1]
    
    # === PATTERN LEARNING ===
    
    def learn_pattern(self, pattern_type: str, pattern_data: str,
                     context: str = None, confidence: float = 0.5) -> Dict:
        """Store a learned pattern"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO patterns (pattern_type, pattern_data, context, confidence)
                        VALUES (?, ?, ?, ?)
                    ''', (pattern_type, pattern_data, context, confidence))
                    conn.commit()
                    return {'success': True, 'id': cursor.lastrowid}
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    def get_patterns(self, pattern_type: str = None, min_confidence: float = 0.5) -> List[Dict]:
        """Retrieve learned patterns"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if pattern_type:
                cursor.execute('''
                    SELECT * FROM patterns WHERE pattern_type = ? AND confidence >= ?
                    ORDER BY confidence DESC
                ''', (pattern_type, min_confidence))
            else:
                cursor.execute('''
                    SELECT * FROM patterns WHERE confidence >= ?
                    ORDER BY confidence DESC
                ''', (min_confidence,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # === TARGET TRACKING ===
    
    def save_target(self, target: str, target_type: str = 'host',
                   ports: List[int] = None, services: List[str] = None,
                   vulnerabilities: List[str] = None, notes: str = None) -> Dict:
        """Save target recon data"""
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO targets
                        (target, target_type, discovered_ports, discovered_services, 
                         vulnerabilities, notes, last_scanned)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (target, target_type, json.dumps(ports or []),
                          json.dumps(services or []), json.dumps(vulnerabilities or []),
                          notes, datetime.now()))
                    conn.commit()
                    return {'success': True}
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    def get_target(self, target: str) -> Optional[Dict]:
        """Get target information"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM targets WHERE target = ?', (target,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # === CREDENTIALS ===
    
    def save_credential(self, username: str, password: str, source: str,
                       target: str = None, credential_type: str = 'password') -> Dict:
        """Save harvested credential"""
        content_hash = self._hash_content(f"{username}:{password}:{source}")
        
        with self._lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR IGNORE INTO credentials
                        (hash, username, password, source, target, credential_type)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (content_hash, username, password, source, target, credential_type))
                    conn.commit()
                    return {'success': True}
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    def get_credentials(self, target: str = None, limit: int = 100) -> List[Dict]:
        """Get stored credentials"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if target:
                cursor.execute('SELECT * FROM credentials WHERE target = ? LIMIT ?', (target, limit))
            else:
                cursor.execute('SELECT * FROM credentials LIMIT ?', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # === STATISTICS ===
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            stats = {}
            for table in ['exploits', 'payloads', 'conversations', 'patterns', 'targets', 'credentials']:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                stats[table] = cursor.fetchone()[0]
            
            # Get database size
            stats['db_size_mb'] = round(os.path.getsize(self.db_path) / (1024 * 1024), 2)
            
            return {
                'success': True,
                'stats': stats,
                'db_path': self.db_path
            }
    
    def export_knowledge(self, export_path: str = '/tmp/lilith_knowledge.json') -> Dict:
        """Export all knowledge to JSON"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            knowledge = {
                'exported_at': datetime.now().isoformat(),
                'exploits': [],
                'payloads': [],
                'patterns': [],
                'targets': []
            }
            
            for table in ['exploits', 'payloads', 'patterns', 'targets']:
                cursor.execute(f'SELECT * FROM {table}')
                knowledge[table] = [dict(row) for row in cursor.fetchall()]
            
            with open(export_path, 'w') as f:
                json.dump(knowledge, f, indent=2, default=str)
            
            return {
                'success': True,
                'path': export_path,
                'records': {k: len(v) for k, v in knowledge.items() if isinstance(v, list)}
            }


# Singleton
_memory_instance = None

def get_lilith_memory() -> LilithMemory:
    """Get singleton memory instance"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = LilithMemory()
    return _memory_instance


if __name__ == '__main__':
    print("=== LILITH Memory System Test ===")
    
    memory = LilithMemory()
    
    # Test saving exploit
    result = memory.save_exploit(
        name='Test SQL Injection',
        code="' OR 1=1 --",
        category='sqli',
        description='Basic SQL injection'
    )
    print(f"Save exploit: {result}")
    
    # Test saving payload
    result = memory.save_payload(
        name='Python RevShell',
        code='python -c "import socket..."',
        platform='linux',
        payload_type='reverse_shell'
    )
    print(f"Save payload: {result}")
    
    # Get stats
    print(f"Stats: {memory.get_stats()}")
