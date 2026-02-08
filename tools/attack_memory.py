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
        
        # Generated attack code storage
        c.execute('''CREATE TABLE IF NOT EXISTS generated_code (
            id INTEGER PRIMARY KEY,
            code_type TEXT,
            target_type TEXT,
            code_content TEXT,
            language TEXT,
            success_rate REAL DEFAULT 0.0,
            times_used INTEGER DEFAULT 0,
            times_successful INTEGER DEFAULT 0,
            last_used TEXT,
            created_at TEXT,
            notes TEXT,
            syntax_valid INTEGER DEFAULT 1,
            tested_targets TEXT
        )''')
        
        # Code generation learning patterns
        c.execute('''CREATE TABLE IF NOT EXISTS code_patterns (
            id INTEGER PRIMARY KEY,
            pattern_type TEXT,
            target_fingerprint TEXT,
            successful_code_id INTEGER,
            failure_reasons TEXT,
            improvements_made TEXT,
            learned_at TEXT,
            FOREIGN KEY (successful_code_id) REFERENCES generated_code(id)
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

    def learn_from_ai_response(self, prompt: str, response: str, 
                              success: bool, provider: str, model: str,
                              execution_time: float = None, tokens_used: int = None):
        """Learn from AI responses to improve future prompts"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create ai_learning table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS ai_learning (
            id INTEGER PRIMARY KEY,
            prompt_hash TEXT UNIQUE,
            prompt TEXT,
            response TEXT,
            success INTEGER,
            provider TEXT,
            model TEXT,
            execution_time REAL,
            tokens_used INTEGER,
            timestamp TEXT,
            lessons_learned TEXT
        )''')
        
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        
        c.execute('''INSERT OR REPLACE INTO ai_learning 
                    (prompt_hash, prompt, response, success, provider, model, 
                     execution_time, tokens_used, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (prompt_hash, prompt[:2000], response[:5000], 
                  1 if success else 0, provider, model, execution_time, 
                  tokens_used, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_similar_prompts(self, prompt: str, limit: int = 5) -> List[Dict]:
        """Find similar prompts and their outcomes"""
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Simple similarity based on keywords (could be improved with embeddings)
        keywords = set(prompt.lower().split()[:10])  # First 10 words
        
        c.execute("SELECT * FROM ai_learning ORDER BY timestamp DESC LIMIT 100")
        rows = c.fetchall()
        
        similar = []
        for row in rows:
            row_dict = dict(zip([d[0] for d in c.description], row))
            stored_keywords = set(row_dict['prompt'].lower().split()[:10])
            similarity = len(keywords.intersection(stored_keywords)) / len(keywords.union(stored_keywords))
            
            if similarity > 0.3:  # 30% keyword overlap
                row_dict['similarity'] = similarity
                similar.append(row_dict)
        
        conn.close()
        return sorted(similar, key=lambda x: x['similarity'], reverse=True)[:limit]
    
    def adapt_prompt(self, original_prompt: str, failed_attempts: List[str] = None) -> str:
        """Adapt a prompt based on learning from similar prompts"""
        similar = self.get_similar_prompts(original_prompt)
        
        if not similar:
            return original_prompt
        
        # Analyze successful vs failed patterns
        successful = [s for s in similar if s['success']]
        failed = [s for s in similar if not s['success']]
        
        adaptations = []
        
        if successful:
            # Learn from successful prompts
            avg_tokens = sum(s['tokens_used'] for s in successful if s['tokens_used']) / len([s for s in successful if s['tokens_used']])
            adaptations.append(f"Based on {len(successful)} successful similar prompts, aim for ~{int(avg_tokens)} tokens")
        
        if failed:
            # Avoid patterns that led to failure
            failed_providers = set(s['provider'] for s in failed)
            if len(failed_providers) > 0:
                adaptations.append(f"Avoid providers: {', '.join(failed_providers)}")
        
        if adaptations:
            adapted_prompt = original_prompt + "\n\nLEARNING ADAPTATIONS:\n" + "\n".join(adaptations)
            return adapted_prompt
        
        return original_prompt
    
    def get_provider_performance(self) -> Dict[str, Dict]:
        """Get performance statistics for each AI provider"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""SELECT provider, 
                            COUNT(*) as total_calls,
                            AVG(success) as success_rate,
                            AVG(execution_time) as avg_time,
                            AVG(tokens_used) as avg_tokens
                     FROM ai_learning 
                     GROUP BY provider
                     ORDER BY success_rate DESC""")
        
        results = {}
        for row in c.fetchall():
            results[row[0]] = {
                'total_calls': row[1],
                'success_rate': row[2],
                'avg_time': row[3],
                'avg_tokens': row[4]
            }
        
        conn.close()
        return results
    
    def get_attack_success_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in successful vs failed attacks"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        patterns = {
            'successful_vectors': [],
            'failed_vectors': [],
            'best_attack_types': [],
            'worst_attack_types': []
        }
        
        # Successful attack vectors
        c.execute("""SELECT attack_vector, COUNT(*) as count
                     FROM attacks WHERE success = 1
                     GROUP BY attack_vector
                     ORDER BY count DESC LIMIT 10""")
        patterns['successful_vectors'] = [{'vector': r[0], 'count': r[1]} for r in c.fetchall()]
        
        # Failed attack vectors
        c.execute("""SELECT attack_vector, COUNT(*) as count
                     FROM attacks WHERE success = 0
                     GROUP BY attack_vector
                     ORDER BY count DESC LIMIT 10""")
        patterns['failed_vectors'] = [{'vector': r[0], 'count': r[1]} for r in c.fetchall()]
        
        # Best attack types
        c.execute("""SELECT attack_type, AVG(impact_score) as avg_impact, COUNT(*) as count
                     FROM attacks WHERE success = 1
                     GROUP BY attack_type
                     HAVING count > 2
                     ORDER BY avg_impact DESC LIMIT 5""")
        patterns['best_attack_types'] = [{'type': r[0], 'avg_impact': r[1], 'count': r[2]} for r in c.fetchall()]
        
        # Worst attack types
        c.execute("""SELECT attack_type, COUNT(*) as failures
                     FROM attacks WHERE success = 0
                     GROUP BY attack_type
                     ORDER BY failures DESC LIMIT 5""")
        patterns['worst_attack_types'] = [{'type': r[0], 'failures': r[1]} for r in c.fetchall()]
        
        conn.close()
        return patterns
    
    def generate_strategy_adaptation(self, target_info: Dict) -> str:
        """Generate adaptive strategy based on learned patterns"""
        patterns = self.get_attack_success_patterns()
        provider_perf = self.get_provider_performance()
        
        strategy = "ADAPTIVE ATTACK STRATEGY:\n\n"
        
        # Provider recommendations
        if provider_perf:
            best_provider = max(provider_perf.items(), key=lambda x: x[1]['success_rate'])
            strategy += f"🤖 Use {best_provider[0]} (success rate: {best_provider[1]['success_rate']:.1%})\n"
        
        # Attack vector recommendations
        if patterns['successful_vectors']:
            top_vector = patterns['successful_vectors'][0]
            strategy += f"🎯 Prioritize: {top_vector['vector']} (worked {top_vector['count']} times)\n"
        
        # Avoid failed vectors
        if patterns['failed_vectors']:
            avoid_vectors = [v['vector'] for v in patterns['failed_vectors'][:3]]
            strategy += f"❌ Avoid: {', '.join(avoid_vectors)}\n"
        
        # Target-specific learning
        if target_info.get('cms'):
            cms_suggestions = self.suggest_attack(cms=target_info['cms'])
            if cms_suggestions['confidence'] > 0.5:
                strategy += f"🎪 CMS-specific: {cms_suggestions['suggestion']}\n"
        
        strategy += "\nLEARNED LESSONS:\n"
        strategy += "- Always test small before scaling attacks\n"
        strategy += "- Combine reconnaissance with exploitation\n"
        strategy += "- Use multiple vectors for redundancy\n"
        strategy += "- Document everything for future reference\n"
        
        return strategy
    
    def store_generated_code(self, code_type: str, target_type: str, 
                           code_content: str, language: str = "python",
                           syntax_valid: bool = True, notes: str = None) -> int:
        """Store generated attack code for learning and reuse"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO generated_code 
                    (code_type, target_type, code_content, language, 
                     syntax_valid, created_at, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (code_type, target_type, code_content, language,
                  1 if syntax_valid else 0, datetime.now().isoformat(), notes))
        
        code_id = c.lastrowid
        conn.commit()
        conn.close()
        return code_id
    
    def record_code_usage(self, code_id: int, success: bool, target_fingerprint: str = None):
        """Record when generated code is used and its success"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Update usage statistics
        success_increment = 1 if success else 0
        c.execute('''UPDATE generated_code 
                    SET times_used = times_used + 1,
                        times_successful = times_successful + ?,
                        last_used = ?,
                        success_rate = CAST((times_successful + ?) AS REAL) / (times_used + 1)
                    WHERE id = ?''',
                 (success_increment, datetime.now().isoformat(), success_increment, code_id))
        
        # Add target to tested targets if provided
        if target_fingerprint:
            c.execute('''UPDATE generated_code 
                        SET tested_targets = CASE 
                            WHEN tested_targets IS NULL THEN ?
                            WHEN instr(tested_targets, ?) = 0 THEN tested_targets || ',' || ?
                            ELSE tested_targets
                        END
                        WHERE id = ?''',
                     (target_fingerprint, target_fingerprint, target_fingerprint, code_id))
        
        conn.commit()
        conn.close()
    
    def get_best_code_for_target(self, code_type: str, target_type: str, 
                               min_success_rate: float = 0.5) -> Optional[Dict]:
        """Get the best performing code for a specific target type"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT id, code_content, language, success_rate, times_used, notes
                    FROM generated_code 
                    WHERE code_type = ? AND target_type = ? AND success_rate >= ?
                    ORDER BY success_rate DESC, times_used DESC
                    LIMIT 1''',
                 (code_type, target_type, min_success_rate))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'code': result[1],
                'language': result[2],
                'success_rate': result[3],
                'times_used': result[4],
                'notes': result[5]
            }
        return None
    
    def get_all_generated_code(self, code_type: str = None, target_type: str = None,
                              language: str = None, min_success_rate: float = 0.0) -> List[Dict]:
        """Get all generated code matching criteria"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = '''SELECT id, code_type, target_type, code_content, language, 
                          success_rate, times_used, times_successful, last_used, 
                          created_at, notes, syntax_valid, tested_targets
                   FROM generated_code WHERE 1=1'''
        params = []
        
        if code_type:
            query += ' AND code_type = ?'
            params.append(code_type)
        
        if target_type:
            query += ' AND target_type = ?'
            params.append(target_type)
        
        if language:
            query += ' AND language = ?'
            params.append(language)
        
        query += ' AND success_rate >= ?'
        params.append(min_success_rate)
        
        query += ' ORDER BY created_at DESC'
        
        c.execute(query, params)
        results = c.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'code_type': row[1],
            'target_type': row[2],
            'code_content': row[3],
            'language': row[4],
            'success_rate': row[5],
            'times_used': row[6],
            'times_successful': row[7],
            'last_used': row[8],
            'created_at': row[9],
            'notes': row[10],
            'syntax_valid': bool(row[11]),
            'tested_targets': row[12]
        } for row in results]
    
    def learn_from_code_generation(self, code_type: str, target_fingerprint: str,
                                 successful_code: str, failure_reasons: List[str] = None,
                                 improvements: List[str] = None):
        """Learn from code generation attempts"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Store successful code if provided
        code_id = None
        if successful_code:
            code_id = self.store_generated_code(
                code_type=code_type,
                target_type=self._extract_target_type(target_fingerprint),
                code_content=successful_code,
                language=self._detect_language(successful_code)
            )
        
        # Record learning pattern
        if failure_reasons or improvements:
            c.execute('''INSERT INTO code_patterns 
                        (pattern_type, target_fingerprint, successful_code_id,
                         failure_reasons, improvements_made, learned_at)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (code_type, target_fingerprint, code_id,
                      json.dumps(failure_reasons) if failure_reasons else None,
                      json.dumps(improvements) if improvements else None,
                      datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def _extract_target_type(self, target_fingerprint: str) -> str:
        """Extract target type from fingerprint (simplified)"""
        # This would be enhanced to actually analyze the target
        return "web"  # Default assumption
    
    def _detect_language(self, code: str) -> str:
        """Detect programming language from code content"""
        code_lower = code.lower()
        if "import " in code_lower or "def " in code_lower or "class " in code_lower:
            return "python"
        elif "function" in code_lower or "var " in code_lower or "const " in code_lower:
            return "javascript"
        elif "<?php" in code_lower or "echo " in code_lower:
            return "php"
        elif "#include" in code_lower or "int main" in code_lower:
            return "c/cpp"
        elif "public class" in code_lower or "import java" in code_lower:
            return "java"
        else:
            return "unknown"


# Global instance
_memory_instance = None

def get_memory() -> AttackMemory:
    """Get the global attack memory instance"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = AttackMemory()
    return _memory_instance
