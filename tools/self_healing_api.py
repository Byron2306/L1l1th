#!/usr/bin/env python3
"""
LILITH Self-Healing API System
================================
Automatically detects when API providers fail and autonomously
harvests new API keys to maintain operational capability.

This is LILITH's self-sustaining mechanism.
"""

import os
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

class SelfHealingAPISystem:
    """
    Monitors API health and autonomously harvests new keys when needed.
    """
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.failure_threshold = 5  # Failures before auto-harvest
        self.failure_counts = {}
        self.last_harvest_attempt = {}
        self.harvest_cooldown = 3600  # 1 hour between harvest attempts
    
    def start_monitoring(self):
        """Start monitoring API health"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("[SELF-HEAL] API monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("[SELF-HEAL] API monitoring stopped")
    
    def record_failure(self, provider: str):
        """Record API failure"""
        if provider not in self.failure_counts:
            self.failure_counts[provider] = 0
        
        self.failure_counts[provider] += 1
        
        print(f"[SELF-HEAL] {provider} failure #{self.failure_counts[provider]}")
        
        # Check if we need to harvest new key
        if self.failure_counts[provider] >= self.failure_threshold:
            self._trigger_harvest(provider)
    
    def record_success(self, provider: str):
        """Record API success - reset failure count"""
        if provider in self.failure_counts:
            self.failure_counts[provider] = 0
    
    def _trigger_harvest(self, provider: str):
        """Trigger autonomous key harvesting"""
        # Check cooldown
        if provider in self.last_harvest_attempt:
            elapsed = time.time() - self.last_harvest_attempt[provider]
            if elapsed < self.harvest_cooldown:
                print(f"[SELF-HEAL] {provider} harvest on cooldown ({int(self.harvest_cooldown - elapsed)}s remaining)")
                return
        
        print(f"\n{'='*60}")
        print(f"[SELF-HEAL] 🚨 {provider} CRITICAL FAILURE THRESHOLD REACHED")
        print(f"[SELF-HEAL] 🤖 Initiating autonomous API key harvesting...")
        print(f"{'='*60}\n")
        
        self.last_harvest_attempt[provider] = time.time()
        
        # Run harvester in background
        harvest_thread = threading.Thread(
            target=self._run_harvester,
            args=(provider,),
            daemon=True
        )
        harvest_thread.start()
    
    def _run_harvester(self, provider: str):
        """Run the key harvester"""
        try:
            from api_key_harvester import APIKeyHarvester
            
            harvester = APIKeyHarvester()
            
            # Run harvest for specific provider
            if provider == 'groq':
                key = harvester.harvest_groq_key()
            elif provider == 'huggingface':
                key = harvester.harvest_huggingface_key()
            else:
                print(f"[SELF-HEAL] No harvester available for {provider}")
                return
            
            if key:
                print(f"[SELF-HEAL] ✓ Successfully harvested new {provider} key!")
                print(f"[SELF-HEAL] 🔄 Restarting backend to apply new key...")
                
                # Reset failure count
                self.failure_counts[provider] = 0
                
                # Signal backend to reload configuration
                self._reload_backend_config()
            else:
                print(f"[SELF-HEAL] ✗ Failed to harvest {provider} key")
        
        except Exception as e:
            print(f"[SELF-HEAL] Error during harvesting: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            if hasattr(harvester, 'close_browser'):
                harvester.close_browser()
    
    def _reload_backend_config(self):
        """Reload backend configuration with new keys"""
        try:
            # Import and reinitialize AI providers
            from ai_providers import get_ai_manager
            
            manager = get_ai_manager()
            manager._reload_providers()
            
            print("[SELF-HEAL] ✓ Backend configuration reloaded")
        except Exception as e:
            print(f"[SELF-HEAL] Error reloading config: {e}")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                # Check API health periodically
                self._check_all_providers()
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"[SELF-HEAL] Monitor error: {e}")
                time.sleep(60)
    
    def _check_all_providers(self):
        """Check health of all providers"""
        try:
            from guaranteed_endpoint import get_key_manager
            
            manager = get_key_manager()
            status = manager.get_status()
            
            # Check for unhealthy providers
            for provider_info in status['providers']:
                if not provider_info['is_valid']:
                    provider = provider_info['provider']
                    print(f"[SELF-HEAL] {provider} is unhealthy")
                    self.record_failure(provider)
        
        except Exception as e:
            print(f"[SELF-HEAL] Error checking providers: {e}")
    
    def get_status(self) -> Dict:
        """Get self-healing system status"""
        return {
            'monitoring': self.monitoring,
            'failure_counts': self.failure_counts,
            'last_harvest_attempts': {
                k: datetime.fromtimestamp(v).isoformat()
                for k, v in self.last_harvest_attempt.items()
            }
        }


# Global instance
_self_healing_system: Optional[SelfHealingAPISystem] = None

def get_self_healing_system() -> SelfHealingAPISystem:
    """Get or create the global self-healing system"""
    global _self_healing_system
    if _self_healing_system is None:
        _self_healing_system = SelfHealingAPISystem()
        _self_healing_system.start_monitoring()
    return _self_healing_system


if __name__ == '__main__':
    # Test the system
    system = get_self_healing_system()
    
    print("Self-Healing API System - Test Mode")
    print("="*60)
    
    # Simulate failures
    for i in range(6):
        system.record_failure('groq')
        time.sleep(2)
    
    # Keep running
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        system.stop_monitoring()
        print("\nStopped")
