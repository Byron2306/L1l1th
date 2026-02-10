#!/usr/bin/env python3
"""
LILITH ATTACK HISTORY LOGGER v1.0
=================================
Logs all autonomous attacks and operations to MongoDB.
Provides replay, analysis, and reporting capabilities.
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib

# MongoDB
try:
    from pymongo import MongoClient
    from bson import ObjectId
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False


class AttackType(Enum):
    """Types of attacks logged"""
    HACKINGBUDDY = "hackingbuddy"
    CREWAI = "crewai"
    AUTOGPT = "autogpt"
    GARAK = "garak"
    KAWAII = "kawaii"
    NMAP = "nmap"
    SQLMAP = "sqlmap"
    MANUAL = "manual"
    PAYLOAD = "payload"
    FULL_ATTACK = "full_attack"


class AttackStatus(Enum):
    """Status of an attack"""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class AttackLog:
    """Single attack log entry"""
    attack_id: str
    attack_type: str
    target: str
    objective: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    rounds: List[Dict] = None
    results: Dict = None
    commands_executed: List[str] = None
    vulnerabilities_found: List[str] = None
    data_exfiltrated: List[str] = None
    success_rate: float = 0.0
    notes: str = ""
    agent_used: str = ""
    
    def __post_init__(self):
        if self.rounds is None:
            self.rounds = []
        if self.results is None:
            self.results = {}
        if self.commands_executed is None:
            self.commands_executed = []
        if self.vulnerabilities_found is None:
            self.vulnerabilities_found = []
        if self.data_exfiltrated is None:
            self.data_exfiltrated = []
    
    def to_dict(self) -> Dict:
        return {
            'attack_id': self.attack_id,
            'attack_type': self.attack_type,
            'target': self.target,
            'objective': self.objective,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': self.duration_seconds,
            'rounds': self.rounds,
            'results': self.results,
            'commands_executed': self.commands_executed,
            'vulnerabilities_found': self.vulnerabilities_found,
            'data_exfiltrated': self.data_exfiltrated,
            'success_rate': self.success_rate,
            'notes': self.notes,
            'agent_used': self.agent_used
        }


class AttackHistoryLogger:
    """
    MongoDB-backed attack history logger.
    Records all autonomous attacks for analysis and replay.
    """
    
    COLLECTION_NAME = "attack_history"
    
    def __init__(self, mongo_url: str = None, db_name: str = None):
        self.mongo_url = mongo_url or os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = db_name or os.environ.get('DB_NAME', 'luciferos')
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB"""
        if not MONGO_AVAILABLE:
            print("[ATTACK LOG] MongoDB not available - using file-based logging")
            return
        
        try:
            self.client = MongoClient(self.mongo_url)
            self.db = self.client[self.db_name]
            self.collection = self.db[self.COLLECTION_NAME]
            
            # Create indexes
            self.collection.create_index("attack_id", unique=True)
            self.collection.create_index("target")
            self.collection.create_index("attack_type")
            self.collection.create_index("started_at")
            self.collection.create_index("status")
            
            print(f"[ATTACK LOG] Connected to MongoDB: {self.db_name}")
        except Exception as e:
            print(f"[ATTACK LOG] MongoDB connection error: {e}")
            self.collection = None
    
    def _generate_attack_id(self, attack_type: str, target: str) -> str:
        """Generate unique attack ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{attack_type}_{target}_{timestamp}"
        short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"{attack_type}_{short_hash}_{timestamp}"
    
    def start_attack(
        self,
        attack_type: str,
        target: str,
        objective: str,
        agent_used: str = ""
    ) -> str:
        """
        Log the start of an attack. Returns attack_id.
        """
        attack_id = self._generate_attack_id(attack_type, target)
        
        log_entry = AttackLog(
            attack_id=attack_id,
            attack_type=attack_type,
            target=target,
            objective=objective,
            status=AttackStatus.STARTED.value,
            started_at=datetime.now(),
            agent_used=agent_used
        )
        
        if self.collection:
            try:
                self.collection.insert_one(log_entry.to_dict())
            except Exception as e:
                print(f"[ATTACK LOG] Error logging attack start: {e}")
        
        return attack_id
    
    def log_round(
        self,
        attack_id: str,
        round_number: int,
        command: str,
        output: str,
        success: bool,
        thought: str = "",
        action: str = ""
    ):
        """Log a single round of an attack"""
        round_data = {
            'round': round_number,
            'command': command,
            'output': output[:2000],  # Truncate long outputs
            'success': success,
            'thought': thought[:500],
            'action': action[:200],
            'timestamp': datetime.now().isoformat()
        }
        
        if self.collection:
            try:
                self.collection.update_one(
                    {'attack_id': attack_id},
                    {
                        '$push': {'rounds': round_data},
                        '$addToSet': {'commands_executed': command},
                        '$set': {'status': AttackStatus.IN_PROGRESS.value}
                    }
                )
            except Exception as e:
                print(f"[ATTACK LOG] Error logging round: {e}")
    
    def log_vulnerability(self, attack_id: str, vulnerability: str):
        """Log a discovered vulnerability"""
        if self.collection:
            try:
                self.collection.update_one(
                    {'attack_id': attack_id},
                    {'$addToSet': {'vulnerabilities_found': vulnerability}}
                )
            except Exception as e:
                print(f"[ATTACK LOG] Error logging vulnerability: {e}")
    
    def log_exfiltration(self, attack_id: str, data_type: str, description: str):
        """Log exfiltrated data"""
        entry = f"{data_type}: {description}"
        if self.collection:
            try:
                self.collection.update_one(
                    {'attack_id': attack_id},
                    {'$addToSet': {'data_exfiltrated': entry}}
                )
            except Exception as e:
                print(f"[ATTACK LOG] Error logging exfiltration: {e}")
    
    def complete_attack(
        self,
        attack_id: str,
        success: bool,
        results: Dict = None,
        notes: str = ""
    ):
        """Mark attack as completed"""
        status = AttackStatus.COMPLETED.value if success else AttackStatus.FAILED.value
        
        # Get start time to calculate duration
        if self.collection:
            try:
                attack = self.collection.find_one({'attack_id': attack_id})
                started_at = datetime.fromisoformat(attack['started_at']) if attack else datetime.now()
                duration = (datetime.now() - started_at).total_seconds()
                
                # Calculate success rate from rounds
                rounds = attack.get('rounds', []) if attack else []
                success_rate = sum(1 for r in rounds if r.get('success')) / len(rounds) if rounds else 0.0
                
                self.collection.update_one(
                    {'attack_id': attack_id},
                    {
                        '$set': {
                            'status': status,
                            'completed_at': datetime.now().isoformat(),
                            'duration_seconds': duration,
                            'results': results or {},
                            'notes': notes,
                            'success_rate': success_rate
                        }
                    }
                )
            except Exception as e:
                print(f"[ATTACK LOG] Error completing attack: {e}")
    
    def get_attack(self, attack_id: str) -> Optional[Dict]:
        """Get a specific attack log"""
        if self.collection:
            try:
                attack = self.collection.find_one(
                    {'attack_id': attack_id},
                    {'_id': 0}
                )
                return attack
            except Exception as e:
                print(f"[ATTACK LOG] Error getting attack: {e}")
        return None
    
    def get_attacks_by_target(self, target: str, limit: int = 50) -> List[Dict]:
        """Get all attacks against a specific target"""
        if self.collection:
            try:
                attacks = list(self.collection.find(
                    {'target': {'$regex': target, '$options': 'i'}},
                    {'_id': 0}
                ).sort('started_at', -1).limit(limit))
                return attacks
            except Exception as e:
                print(f"[ATTACK LOG] Error getting attacks by target: {e}")
        return []
    
    def get_recent_attacks(self, limit: int = 20) -> List[Dict]:
        """Get most recent attacks"""
        if self.collection:
            try:
                attacks = list(self.collection.find(
                    {},
                    {'_id': 0}
                ).sort('started_at', -1).limit(limit))
                return attacks
            except Exception as e:
                print(f"[ATTACK LOG] Error getting recent attacks: {e}")
        return []
    
    def get_attacks_by_type(self, attack_type: str, limit: int = 50) -> List[Dict]:
        """Get attacks of a specific type"""
        if self.collection:
            try:
                attacks = list(self.collection.find(
                    {'attack_type': attack_type},
                    {'_id': 0}
                ).sort('started_at', -1).limit(limit))
                return attacks
            except Exception as e:
                print(f"[ATTACK LOG] Error getting attacks by type: {e}")
        return []
    
    def get_successful_attacks(self, limit: int = 50) -> List[Dict]:
        """Get only successful attacks"""
        if self.collection:
            try:
                attacks = list(self.collection.find(
                    {'status': 'completed', 'success_rate': {'$gt': 0.5}},
                    {'_id': 0}
                ).sort('started_at', -1).limit(limit))
                return attacks
            except Exception as e:
                print(f"[ATTACK LOG] Error getting successful attacks: {e}")
        return []
    
    def get_statistics(self) -> Dict:
        """Get attack statistics"""
        stats = {
            'total_attacks': 0,
            'successful_attacks': 0,
            'failed_attacks': 0,
            'attacks_by_type': {},
            'unique_targets': 0,
            'total_rounds': 0,
            'total_vulnerabilities': 0,
            'avg_success_rate': 0.0
        }
        
        if self.collection:
            try:
                # Total attacks
                stats['total_attacks'] = self.collection.count_documents({})
                
                # Successful attacks
                stats['successful_attacks'] = self.collection.count_documents({
                    'status': 'completed',
                    'success_rate': {'$gt': 0.5}
                })
                
                # Failed attacks
                stats['failed_attacks'] = self.collection.count_documents({
                    'status': 'failed'
                })
                
                # Attacks by type
                pipeline = [
                    {'$group': {'_id': '$attack_type', 'count': {'$sum': 1}}}
                ]
                for result in self.collection.aggregate(pipeline):
                    stats['attacks_by_type'][result['_id']] = result['count']
                
                # Unique targets
                stats['unique_targets'] = len(self.collection.distinct('target'))
                
                # Total rounds
                pipeline = [
                    {'$project': {'rounds_count': {'$size': {'$ifNull': ['$rounds', []]}}}},
                    {'$group': {'_id': None, 'total': {'$sum': '$rounds_count'}}}
                ]
                result = list(self.collection.aggregate(pipeline))
                if result:
                    stats['total_rounds'] = result[0].get('total', 0)
                
                # Total vulnerabilities
                pipeline = [
                    {'$project': {'vulns_count': {'$size': {'$ifNull': ['$vulnerabilities_found', []]}}}},
                    {'$group': {'_id': None, 'total': {'$sum': '$vulns_count'}}}
                ]
                result = list(self.collection.aggregate(pipeline))
                if result:
                    stats['total_vulnerabilities'] = result[0].get('total', 0)
                
                # Average success rate
                pipeline = [
                    {'$match': {'success_rate': {'$exists': True}}},
                    {'$group': {'_id': None, 'avg': {'$avg': '$success_rate'}}}
                ]
                result = list(self.collection.aggregate(pipeline))
                if result:
                    stats['avg_success_rate'] = round(result[0].get('avg', 0) * 100, 1)
                
            except Exception as e:
                print(f"[ATTACK LOG] Error getting statistics: {e}")
        
        return stats
    
    def delete_attack(self, attack_id: str) -> bool:
        """Delete an attack log"""
        if self.collection:
            try:
                result = self.collection.delete_one({'attack_id': attack_id})
                return result.deleted_count > 0
            except Exception as e:
                print(f"[ATTACK LOG] Error deleting attack: {e}")
        return False
    
    def clear_all(self) -> int:
        """Clear all attack logs (dangerous!)"""
        if self.collection:
            try:
                result = self.collection.delete_many({})
                return result.deleted_count
            except Exception as e:
                print(f"[ATTACK LOG] Error clearing logs: {e}")
        return 0


# Singleton
_attack_logger = None

def get_attack_logger() -> AttackHistoryLogger:
    """Get singleton attack logger"""
    global _attack_logger
    if _attack_logger is None:
        _attack_logger = AttackHistoryLogger()
    return _attack_logger


# Quick test
if __name__ == '__main__':
    print("=" * 60)
    print("ATTACK HISTORY LOGGER TEST")
    print("=" * 60)
    
    logger = get_attack_logger()
    
    # Test logging
    attack_id = logger.start_attack(
        attack_type="hackingbuddy",
        target="testhost.local",
        objective="Test attack",
        agent_used="HackingBuddyAgent"
    )
    print(f"Started attack: {attack_id}")
    
    # Log rounds
    logger.log_round(attack_id, 1, "id && whoami", "uid=1000(test)", True, "Checking user", "enumeration")
    logger.log_round(attack_id, 2, "sudo -l", "No sudo", False, "Checking sudo", "privesc")
    
    # Log vulnerability
    logger.log_vulnerability(attack_id, "Outdated kernel 5.4.0")
    
    # Complete attack
    logger.complete_attack(attack_id, True, {'goal_achieved': False}, 'Test completed')
    
    # Get stats
    stats = logger.get_statistics()
    print(f"Statistics: {stats}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
