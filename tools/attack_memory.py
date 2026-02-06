#!/usr/bin/env python3
"""
LuciferOS Attack Memory System
Learns from every attack - remembers what works, avoids what fails
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

class AttackMemory:
    """
    Persistent attack memory - LILITH learns and never forgets
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path.home() / ".lucifera" / "attack_memory.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize the attack memory database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Targets we've seen
        c.execute('''CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY,
            fingerprint TEXT UNIQUE,
            domain TEXT,
            ip TEXT,
            technologies TEXT,
            ports TEXT,
            cms TEXT,
            server TEXT,
            first_seen TEXT,
            last_seen TEXT,
            times_attacked INTEGER DEFAULT 0
        )''')
        
        # Attack attempts and results
        c.execute('''CREATE TABLE IF NOT EXISTS attacks (
            id INTEGER PRIMARY KEY,
            target_fingerprint TEXT,
            attack_type TEXT,
            attack_vector TEXT,
            payload TEXT,
            success INTEGER,
            impact_score REAL,
            response_code INTEGER,
            response_snippet TEXT,
            execution_time REAL,
            timestamp TEXT,
            notes TEXT,
            FOREIGN KEY (target_fingerprint) REFERENCES targets(fingerprint)
        )''')
        
        # Captured loot
        c.execute('''CREATE TABLE IF NOT EXISTS loot (
            id INTEGER PRIMARY KEY,
            target_fingerprint TEXT,
            loot_type TEXT,
            data TEXT,
            source TEXT,
            timestamp TEXT,
            used INTEGER DEFAULT 0,
            FOREIGN KEY (target_fingerprint) REFERENCES targets(fingerprint)
        )''')
        
        # Successful attack chains (playbooks)
        c.execute('''CREATE TABLE IF NOT EXISTS playbooks (
            id INTEGER PRIMARY KEY,
            name TEXT,
            target_type TEXT,
            attack_chain TEXT,
            success_rate REAL,
            avg_time REAL,
            times_used INTEGER DEFAULT 0,
            last_used TEXT
        )''')
        
        # Credentials
        c.execute('''CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY,
            target_fingerprint TEXT,
            username TEXT,
            password TEXT,
            hash TEXT,
            cred_type TEXT,
            source TEXT,
            tested INTEGER DEFAULT 0,
            valid INTEGER DEFAULT 0,
            timestamp TEXT
        )''')
        
        conn.commit()
        conn.close()
    
    def fingerprint_target(self, domain: str = None, ip: str = None, 
                          technologies: List[str] = None, ports: List[int] = None,
                          cms: str = None, server: str = None) -> str:
        """Generate a unique fingerprint for a target"""
        data = {
            'domain': domain,
            'ip': ip,
            'tech': sorted(technologies or []),
            'ports': sorted(ports or []),
            'cms': cms,
            'server': server
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]
    
    def remember_target(self, domain: str = None, ip: str = None,
                       technologies: List[str] = None, ports: List[int] = None,
                       cms: str = None, server: str = None) -> str:
        """Store target information, return fingerprint"""
        fingerprint = self.fingerprint_target(domain, ip, technologies, ports, cms, server)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        now = datetime.now().isoformat()
        
        c.execute('''INSERT INTO targets 
                    (fingerprint, domain, ip, technologies, ports, cms, server, first_seen, last_seen, times_attacked)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    ON CONFLICT(fingerprint) DO UPDATE SET
                    last_seen = ?, times_attacked = times_attacked + 1''',
                 (fingerprint, domain, ip, json.dumps(technologies), json.dumps(ports),
                  cms, server, now, now, now))
        
        conn.commit()
        conn.close()
        return fingerprint
    
    def record_attack(self, target_fingerprint: str, attack_type: str,
                     attack_vector: str, payload: str, success: bool,
                     impact_score: float = 0.0, response_code: int = None,
                     response_snippet: str = None, execution_time: float = None,
                     notes: str = None):
        """Record an attack attempt and its result"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO attacks 
                    (target_fingerprint, attack_type, attack_vector, payload, success,
                     impact_score, response_code, response_snippet, execution_time, timestamp, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (target_fingerprint, attack_type, attack_vector, payload, 
                  1 if success else 0, impact_score, response_code,
                  response_snippet[:500] if response_snippet else None,
                  execution_time, datetime.now().isoformat(), notes))
        
        conn.commit()
        conn.close()
    
    def store_loot(self, target_fingerprint: str, loot_type: str, 
                  data: Any, source: str = None) -> int:
        """Store captured loot (cookies, tokens, files, etc.)"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO loot (target_fingerprint, loot_type, data, source, timestamp)
                    VALUES (?, ?, ?, ?, ?)''',
                 (target_fingerprint, loot_type, json.dumps(data), source, 
                  datetime.now().isoformat()))
        
        loot_id = c.lastrowid
        conn.commit()
        conn.close()
        return loot_id
    
    def store_credential(self, target_fingerprint: str, username: str = None,
                        password: str = None, hash: str = None,
                        cred_type: str = "password", source: str = None):
        """Store captured credentials"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO credentials 
                    (target_fingerprint, username, password, hash, cred_type, source, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (target_fingerprint, username, password, hash, cred_type, source,
                  datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_working_attacks(self, target_fingerprint: str = None, 
                           attack_type: str = None, limit: int = 10) -> List[Dict]:
        """Get attacks that worked on similar targets"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = "SELECT * FROM attacks WHERE success = 1"
        params = []
        
        if target_fingerprint:
            query += " AND target_fingerprint = ?"
            params.append(target_fingerprint)
        if attack_type:
            query += " AND attack_type = ?"
            params.append(attack_type)
        
        query += " ORDER BY impact_score DESC, timestamp DESC LIMIT ?"
        params.append(limit)
        
        c.execute(query, params)
        columns = [d[0] for d in c.description]
        results = [dict(zip(columns, row)) for row in c.fetchall()]
        
        conn.close()
        return results
    
    def get_failed_attacks(self, target_fingerprint: str = None, limit: int = 20) -> List[Dict]:
        """Get attacks that failed - so we don't repeat them"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if target_fingerprint:
            c.execute("""SELECT attack_type, attack_vector, COUNT(*) as failures
                        FROM attacks WHERE success = 0 AND target_fingerprint = ?
                        GROUP BY attack_type, attack_vector
                        ORDER BY failures DESC LIMIT ?""", (target_fingerprint, limit))
        else:
            c.execute("""SELECT attack_type, attack_vector, COUNT(*) as failures
                        FROM attacks WHERE success = 0
                        GROUP BY attack_type, attack_vector
                        ORDER BY failures DESC LIMIT ?""", (limit,))
        
        return [{'attack_type': r[0], 'attack_vector': r[1], 'failures': r[2]} 
                for r in c.fetchall()]
    
    def find_similar_targets(self, technologies: List[str] = None, 
                            cms: str = None, server: str = None) -> List[Dict]:
        """Find similar targets we've attacked before"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        conditions = []
        params = []
        
        if cms:
            conditions.append("cms = ?")
            params.append(cms)
        if server:
            conditions.append("server LIKE ?")
            params.append(f"%{server}%")
        
        if conditions:
            query = f"SELECT * FROM targets WHERE {' OR '.join(conditions)}"
            c.execute(query, params)
        else:
            c.execute("SELECT * FROM targets ORDER BY times_attacked DESC LIMIT 20")
        
        columns = [d[0] for d in c.description]
        results = [dict(zip(columns, row)) for row in c.fetchall()]
        
        conn.close()
        return results
    
    def suggest_attack(self, domain: str = None, cms: str = None, 
                      server: str = None, technologies: List[str] = None) -> Dict:
        """Suggest the best attack based on what worked before"""
        # Find similar targets
        similar = self.find_similar_targets(technologies, cms, server)
        
        if not similar:
            return {
                'suggestion': 'No similar targets in memory. Run full recon first.',
                'confidence': 0.0,
                'attacks': []
            }
        
        # Get successful attacks on similar targets
        fingerprints = [t['fingerprint'] for t in similar]
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        placeholders = ','.join('?' * len(fingerprints))
        c.execute(f"""SELECT attack_type, attack_vector, payload, 
                            AVG(impact_score) as avg_impact,
                            COUNT(*) as successes
                     FROM attacks 
                     WHERE success = 1 AND target_fingerprint IN ({placeholders})
                     GROUP BY attack_type, attack_vector
                     ORDER BY avg_impact DESC, successes DESC
                     LIMIT 5""", fingerprints)
        
        attacks = [{'type': r[0], 'vector': r[1], 'payload': r[2],
                   'avg_impact': r[3], 'successes': r[4]} for r in c.fetchall()]
        
        conn.close()
        
        if attacks:
            best = attacks[0]
            return {
                'suggestion': f"Use {best['type']} via {best['vector']} - worked {best['successes']} times on similar targets",
                'confidence': min(best['avg_impact'] / 10, 1.0),
                'attacks': attacks
            }
        
        return {
            'suggestion': 'Similar targets found but no successful attacks recorded. Try standard vectors.',
            'confidence': 0.3,
            'attacks': []
        }
    
    def get_unused_credentials(self, limit: int = 50) -> List[Dict]:
        """Get credentials that haven't been tested yet"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""SELECT c.*, t.domain, t.ip FROM credentials c
                    LEFT JOIN targets t ON c.target_fingerprint = t.fingerprint
                    WHERE c.tested = 0
                    ORDER BY c.timestamp DESC LIMIT ?""", (limit,))
        
        columns = [d[0] for d in c.description]
        results = [dict(zip(columns, row)) for row in c.fetchall()]
        
        conn.close()
        return results
    
    def get_all_loot(self, loot_type: str = None) -> List[Dict]:
        """Get all captured loot"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if loot_type:
            c.execute("SELECT * FROM loot WHERE loot_type = ? ORDER BY timestamp DESC", (loot_type,))
        else:
            c.execute("SELECT * FROM loot ORDER BY timestamp DESC")
        
        columns = [d[0] for d in c.description]
        results = [dict(zip(columns, row)) for row in c.fetchall()]
        
        conn.close()
        return results
    
    def save_playbook(self, name: str, target_type: str, attack_chain: List[Dict],
                     success_rate: float = 1.0):
        """Save a successful attack chain as a reusable playbook"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO playbooks (name, target_type, attack_chain, success_rate, last_used)
                    VALUES (?, ?, ?, ?, ?)''',
                 (name, target_type, json.dumps(attack_chain), success_rate,
                  datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_playbook(self, target_type: str = None) -> Optional[Dict]:
        """Get the best playbook for a target type"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if target_type:
            c.execute("""SELECT * FROM playbooks WHERE target_type = ?
                        ORDER BY success_rate DESC, times_used DESC LIMIT 1""", (target_type,))
        else:
            c.execute("""SELECT * FROM playbooks 
                        ORDER BY success_rate DESC, times_used DESC LIMIT 1""")
        
        row = c.fetchone()
        if row:
            columns = [d[0] for d in c.description]
            result = dict(zip(columns, row))
            result['attack_chain'] = json.loads(result['attack_chain'])
            conn.close()
            return result
        
        conn.close()
        return None
    
    def get_stats(self) -> Dict:
        """Get attack statistics"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        stats = {}
        
        c.execute("SELECT COUNT(*) FROM targets")
        stats['total_targets'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM attacks")
        stats['total_attacks'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM attacks WHERE success = 1")
        stats['successful_attacks'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM credentials")
        stats['credentials_captured'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM loot")
        stats['loot_items'] = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM playbooks")
        stats['playbooks'] = c.fetchone()[0]
        
        if stats['total_attacks'] > 0:
            stats['success_rate'] = stats['successful_attacks'] / stats['total_attacks']
        else:
            stats['success_rate'] = 0.0
        
        conn.close()
        return stats
    
    def export_memory(self) -> Dict:
        """Export all memory for backup or transfer"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        data = {}
        for table in ['targets', 'attacks', 'loot', 'playbooks', 'credentials']:
            c.execute(f"SELECT * FROM {table}")
            columns = [d[0] for d in c.description]
            data[table] = [dict(zip(columns, row)) for row in c.fetchall()]
        
        conn.close()
        return data


# Global instance
_memory = None

def get_memory() -> AttackMemory:
    """Get the global attack memory instance"""
    global _memory
    if _memory is None:
        _memory = AttackMemory()
    return _memory


if __name__ == "__main__":
    # Test the memory system
    mem = AttackMemory()
    
    # Simulate learning
    fp = mem.remember_target(
        domain="example.com",
        technologies=["PHP", "MySQL"],
        cms="WordPress",
        ports=[80, 443, 22]
    )
    
    mem.record_attack(fp, "sqli", "/search?q=", "' OR 1=1--", True, 8.5)
    mem.store_credential(fp, "admin", "password123", source="login_bruteforce")
    mem.store_loot(fp, "cookies", [{"name": "session", "value": "abc123"}])
    
    print("Stats:", mem.get_stats())
    print("Suggestion:", mem.suggest_attack(cms="WordPress"))
