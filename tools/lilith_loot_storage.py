#!/usr/bin/env python3
"""
LILITH LOOT STORAGE SYSTEM - Store EVERYTHING in LILITH's Memory
================================================================
Stores: Credentials, Cookies, Session Tokens, Hashes, Keys, Data, Scripts
ALL in MongoDB - NOTHING on your local PC!
"""

import os
import json
import hashlib
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any
from pymongo import MongoClient
from bson import ObjectId
import zlib

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'luciferos')


class LootStorage:
    """
    Secure loot storage in LILITH's memory (MongoDB)
    ALL data stays here - NEVER on local disk!
    """
    
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        
        # Collections for different loot types
        self.credentials = self.db['loot_credentials']
        self.cookies = self.db['loot_cookies']  
        self.sessions = self.db['loot_sessions']
        self.hashes = self.db['loot_hashes']
        self.keys = self.db['loot_keys']
        self.data = self.db['loot_data']
        self.scripts = self.db['loot_scripts']  # Store working scripts here!
        self.attack_results = self.db['attack_results']
        self.telemetry = self.db['attack_telemetry']
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create indexes for fast lookups"""
        self.credentials.create_index([('target', 1), ('username', 1)])
        self.cookies.create_index([('domain', 1)])
        self.scripts.create_index([('name', 1), ('category', 1)])
        self.attack_results.create_index([('attack_id', 1)])
        self.telemetry.create_index([('timestamp', -1)])
    
    def _hash_id(self, data: str) -> str:
        """Generate unique hash ID"""
        return hashlib.sha256(data.encode()).hexdigest()[:24]
    
    # ==================== CREDENTIALS ====================
    
    def store_credential(self, username: str, password: str, target: str,
                        cred_type: str = 'password', source: str = 'harvested',
                        verified: bool = False, metadata: Dict = None) -> Dict:
        """Store harvested credentials in LILITH's memory"""
        doc = {
            'hash_id': self._hash_id(f"{username}:{password}:{target}"),
            'username': username,
            'password': password,  # In real scenario, encrypt this
            'target': target,
            'cred_type': cred_type,  # password, hash, token, api_key
            'source': source,
            'verified': verified,
            'metadata': metadata or {},
            'harvested_at': datetime.utcnow(),
            'last_used': None,
            'use_count': 0
        }
        
        # Upsert - don't duplicate
        result = self.credentials.update_one(
            {'hash_id': doc['hash_id']},
            {'$set': doc, '$inc': {'store_count': 1}},
            upsert=True
        )
        
        return {
            'success': True,
            'stored': True if result.upserted_id else False,
            'updated': True if result.modified_count > 0 else False,
            'credential_id': doc['hash_id'],
            'message': f'🔐 Credential stored for {username}@{target}'
        }
    
    def get_credentials(self, target: str = None, cred_type: str = None,
                       verified_only: bool = False, limit: int = 100) -> List[Dict]:
        """Get all stored credentials"""
        query = {}
        if target:
            query['target'] = {'$regex': target, '$options': 'i'}
        if cred_type:
            query['cred_type'] = cred_type
        if verified_only:
            query['verified'] = True
        
        results = list(self.credentials.find(query).limit(limit))
        for r in results:
            r['_id'] = str(r['_id'])
        return results
    
    # ==================== COOKIES ====================
    
    def store_cookie(self, domain: str, name: str, value: str,
                    path: str = '/', expires: str = None,
                    source: str = 'harvested') -> Dict:
        """Store harvested cookies"""
        doc = {
            'hash_id': self._hash_id(f"{domain}:{name}:{value}"),
            'domain': domain,
            'name': name,
            'value': value,
            'path': path,
            'expires': expires,
            'source': source,
            'harvested_at': datetime.utcnow()
        }
        
        self.cookies.update_one(
            {'hash_id': doc['hash_id']},
            {'$set': doc},
            upsert=True
        )
        
        return {
            'success': True,
            'cookie_id': doc['hash_id'],
            'message': f'🍪 Cookie stored: {name}@{domain}'
        }
    
    def get_cookies(self, domain: str = None, limit: int = 100) -> List[Dict]:
        """Get stored cookies"""
        query = {}
        if domain:
            query['domain'] = {'$regex': domain, '$options': 'i'}
        
        results = list(self.cookies.find(query).limit(limit))
        for r in results:
            r['_id'] = str(r['_id'])
        return results
    
    # ==================== PASSWORD HASHES ====================
    
    def store_hash(self, hash_value: str, hash_type: str, username: str = None,
                  target: str = None, cracked: str = None, source: str = 'dumped') -> Dict:
        """Store password hashes for cracking"""
        doc = {
            'hash_id': self._hash_id(hash_value),
            'hash_value': hash_value,
            'hash_type': hash_type,  # md5, sha1, sha256, ntlm, bcrypt, etc
            'username': username,
            'target': target,
            'cracked': cracked,  # Cracked plaintext if available
            'source': source,
            'stored_at': datetime.utcnow()
        }
        
        self.hashes.update_one(
            {'hash_id': doc['hash_id']},
            {'$set': doc},
            upsert=True
        )
        
        return {
            'success': True,
            'hash_id': doc['hash_id'],
            'message': f'🔑 Hash stored: {hash_type}'
        }
    
    def get_hashes(self, hash_type: str = None, cracked_only: bool = False,
                  uncracked_only: bool = False, limit: int = 100) -> List[Dict]:
        """Get stored hashes"""
        query = {}
        if hash_type:
            query['hash_type'] = hash_type
        if cracked_only:
            query['cracked'] = {'$ne': None}
        if uncracked_only:
            query['cracked'] = None
        
        results = list(self.hashes.find(query).limit(limit))
        for r in results:
            r['_id'] = str(r['_id'])
        return results
    
    # ==================== API KEYS & SECRETS ====================
    
    def store_key(self, key_name: str, key_value: str, key_type: str,
                 target: str = None, permissions: List[str] = None,
                 source: str = 'harvested') -> Dict:
        """Store API keys, SSH keys, secrets"""
        doc = {
            'hash_id': self._hash_id(key_value),
            'key_name': key_name,
            'key_value': key_value,
            'key_type': key_type,  # api_key, ssh_key, aws_key, jwt, etc
            'target': target,
            'permissions': permissions or [],
            'source': source,
            'stored_at': datetime.utcnow()
        }
        
        self.keys.update_one(
            {'hash_id': doc['hash_id']},
            {'$set': doc},
            upsert=True
        )
        
        return {
            'success': True,
            'key_id': doc['hash_id'],
            'message': f'🗝️ Key stored: {key_name}'
        }
    
    def get_keys(self, key_type: str = None, limit: int = 100) -> List[Dict]:
        """Get stored keys"""
        query = {}
        if key_type:
            query['key_type'] = key_type
        
        results = list(self.keys.find(query).limit(limit))
        for r in results:
            r['_id'] = str(r['_id'])
        return results
    
    # ==================== EXFILTRATED DATA ====================
    
    def store_data(self, data_name: str, data_content: Any, data_type: str,
                  target: str = None, compress: bool = True,
                  source: str = 'exfiltrated') -> Dict:
        """Store exfiltrated data (compressed if large)"""
        
        # Serialize and optionally compress
        if isinstance(data_content, (dict, list)):
            serialized = json.dumps(data_content)
        else:
            serialized = str(data_content)
        
        if compress and len(serialized) > 1024:
            compressed = base64.b64encode(zlib.compress(serialized.encode())).decode()
            is_compressed = True
        else:
            compressed = serialized
            is_compressed = False
        
        doc = {
            'hash_id': self._hash_id(data_name + str(datetime.utcnow())),
            'data_name': data_name,
            'data_content': compressed,
            'is_compressed': is_compressed,
            'data_type': data_type,  # file, database, memory_dump, screenshot, etc
            'target': target,
            'size_bytes': len(serialized),
            'source': source,
            'exfiltrated_at': datetime.utcnow()
        }
        
        result = self.data.insert_one(doc)
        
        return {
            'success': True,
            'data_id': str(result.inserted_id),
            'size_bytes': doc['size_bytes'],
            'compressed': is_compressed,
            'message': f'📦 Data stored: {data_name} ({doc["size_bytes"]} bytes)'
        }
    
    def get_data(self, data_type: str = None, target: str = None,
                limit: int = 50) -> List[Dict]:
        """Get exfiltrated data"""
        query = {}
        if data_type:
            query['data_type'] = data_type
        if target:
            query['target'] = {'$regex': target, '$options': 'i'}
        
        results = list(self.data.find(query).limit(limit))
        for r in results:
            r['_id'] = str(r['_id'])
            # Decompress if needed
            if r.get('is_compressed'):
                try:
                    r['data_content'] = zlib.decompress(
                        base64.b64decode(r['data_content'])
                    ).decode()
                except:
                    pass
        return results
    
    # ==================== SCRIPT STORAGE ====================
    # THIS IS THE KEY FEATURE - Store scripts in LILITH's memory!
    
    def store_script(self, name: str, code: str, language: str,
                    category: str = 'general', description: str = None,
                    tags: List[str] = None, tested: bool = False,
                    success_rate: float = 0.0) -> Dict:
        """
        Store a working script/exploit in LILITH's memory!
        NOT on your local PC - stays in the cloud!
        """
        doc = {
            'hash_id': self._hash_id(code),
            'name': name,
            'code': code,
            'language': language,  # python, bash, powershell, javascript, etc
            'category': category,  # exploit, payload, recon, persistence, etc
            'description': description,
            'tags': tags or [],
            'tested': tested,
            'success_rate': success_rate,
            'use_count': 0,
            'created_at': datetime.utcnow(),
            'last_used': None,
            'created_by': 'LILITH'
        }
        
        result = self.scripts.update_one(
            {'hash_id': doc['hash_id']},
            {'$set': doc, '$inc': {'version': 1}},
            upsert=True
        )
        
        return {
            'success': True,
            'script_id': doc['hash_id'],
            'new': result.upserted_id is not None,
            'message': f'📜 Script saved to LILITH memory: {name}'
        }
    
    def get_scripts(self, category: str = None, language: str = None,
                   tags: List[str] = None, search: str = None,
                   tested_only: bool = False, limit: int = 50) -> List[Dict]:
        """Get stored scripts from LILITH's memory"""
        query = {}
        if category:
            query['category'] = category
        if language:
            query['language'] = language
        if tags:
            query['tags'] = {'$in': tags}
        if search:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}},
                {'code': {'$regex': search, '$options': 'i'}}
            ]
        if tested_only:
            query['tested'] = True
        
        results = list(self.scripts.find(query).sort('use_count', -1).limit(limit))
        for r in results:
            r['_id'] = str(r['_id'])
        return results
    
    def get_script_by_name(self, name: str) -> Optional[Dict]:
        """Get a specific script by name"""
        result = self.scripts.find_one({'name': name})
        if result:
            result['_id'] = str(result['_id'])
            # Update use count
            self.scripts.update_one(
                {'name': name},
                {'$inc': {'use_count': 1}, '$set': {'last_used': datetime.utcnow()}}
            )
        return result
    
    def delete_script(self, name: str) -> Dict:
        """Delete a script from memory"""
        result = self.scripts.delete_one({'name': name})
        return {
            'success': result.deleted_count > 0,
            'message': f'Script {name} deleted' if result.deleted_count > 0 else 'Script not found'
        }
    
    # ==================== ATTACK RESULTS ====================
    
    def store_attack_result(self, attack_id: str, attack_type: str,
                           target: str, success: bool, output: str,
                           loot_found: Dict = None, duration: float = 0,
                           commands_executed: List[str] = None) -> Dict:
        """Store the results of an attack"""
        doc = {
            'attack_id': attack_id,
            'attack_type': attack_type,
            'target': target,
            'success': success,
            'output': output[:50000],  # Limit output size
            'loot_found': loot_found or {},
            'duration_seconds': duration,
            'commands_executed': commands_executed or [],
            'executed_at': datetime.utcnow()
        }
        
        result = self.attack_results.insert_one(doc)
        
        return {
            'success': True,
            'result_id': str(result.inserted_id),
            'attack_id': attack_id
        }
    
    def get_attack_results(self, attack_type: str = None, target: str = None,
                          success_only: bool = False, limit: int = 50) -> List[Dict]:
        """Get attack results"""
        query = {}
        if attack_type:
            query['attack_type'] = attack_type
        if target:
            query['target'] = {'$regex': target, '$options': 'i'}
        if success_only:
            query['success'] = True
        
        results = list(self.attack_results.find(query).sort('executed_at', -1).limit(limit))
        for r in results:
            r['_id'] = str(r['_id'])
        return results
    
    # ==================== TELEMETRY ====================
    
    def log_telemetry(self, event_type: str, data: Dict, agent: str = 'LILITH') -> Dict:
        """Log attack telemetry for real-time monitoring"""
        doc = {
            'event_type': event_type,  # command_executed, loot_found, error, etc
            'data': data,
            'agent': agent,
            'timestamp': datetime.utcnow()
        }
        
        result = self.telemetry.insert_one(doc)
        return {'success': True, 'telemetry_id': str(result.inserted_id)}
    
    def get_telemetry(self, event_type: str = None, agent: str = None,
                     since_minutes: int = 60, limit: int = 100) -> List[Dict]:
        """Get recent telemetry"""
        from datetime import timedelta
        
        query = {
            'timestamp': {'$gte': datetime.utcnow() - timedelta(minutes=since_minutes)}
        }
        if event_type:
            query['event_type'] = event_type
        if agent:
            query['agent'] = agent
        
        results = list(self.telemetry.find(query).sort('timestamp', -1).limit(limit))
        for r in results:
            r['_id'] = str(r['_id'])
        return results
    
    # ==================== STATISTICS ====================
    
    def get_loot_stats(self) -> Dict:
        """Get comprehensive loot statistics"""
        return {
            'credentials': self.credentials.count_documents({}),
            'cookies': self.cookies.count_documents({}),
            'hashes': self.hashes.count_documents({}),
            'hashes_cracked': self.hashes.count_documents({'cracked': {'$ne': None}}),
            'keys': self.keys.count_documents({}),
            'data_items': self.data.count_documents({}),
            'scripts_stored': self.scripts.count_documents({}),
            'scripts_tested': self.scripts.count_documents({'tested': True}),
            'attack_results': self.attack_results.count_documents({}),
            'successful_attacks': self.attack_results.count_documents({'success': True}),
            'telemetry_events': self.telemetry.count_documents({})
        }
    
    def get_all_loot_summary(self) -> Dict:
        """Get a summary of all stored loot"""
        return {
            'success': True,
            'stats': self.get_loot_stats(),
            'recent_credentials': self.get_credentials(limit=5),
            'recent_cookies': self.get_cookies(limit=5),
            'recent_keys': self.get_keys(limit=5),
            'top_scripts': self.get_scripts(limit=5),
            'recent_attacks': self.get_attack_results(limit=5)
        }


# Singleton instance
_loot_storage = None

def get_loot_storage() -> LootStorage:
    """Get singleton loot storage instance"""
    global _loot_storage
    if _loot_storage is None:
        _loot_storage = LootStorage()
    return _loot_storage


if __name__ == '__main__':
    print("=== LILITH Loot Storage Test ===")
    storage = get_loot_storage()
    
    # Test credential storage
    result = storage.store_credential(
        username='admin',
        password='SuperSecret123!',
        target='192.168.1.1',
        cred_type='password',
        source='hydra_brute'
    )
    print(f"Credential: {result}")
    
    # Test script storage
    result = storage.store_script(
        name='reverse_shell_python',
        code='python -c "import socket,subprocess..."',
        language='python',
        category='payload',
        description='Python reverse shell one-liner'
    )
    print(f"Script: {result}")
    
    # Get stats
    print(f"Stats: {storage.get_loot_stats()}")
