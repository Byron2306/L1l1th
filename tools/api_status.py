#!/usr/bin/env python3
"""
API Status Dashboard Module
==========================
Provides health monitoring and status endpoints for the API system.
Integrates with Flask for web dashboard access.
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from flask import Blueprint, jsonify, request

# Status directory
STATUS_DIR = Path.home() / ".lucifera" / "api_status"
STATUS_DIR.mkdir(parents=True, exist_ok=True)

# Create blueprint for Flask integration
api_status_bp = Blueprint('api_status', __name__)


class APIStatusMonitor:
    """
    Monitors API health and provides status endpoints.
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_latency = 0.0
        self._lock = threading.Lock()
        self._key_manager = None
        self._last_cleanup = datetime.now()
    
    def set_key_manager(self, key_manager):
        """Set the key manager for status monitoring"""
        self._key_manager = key_manager
    
    def record_request(self, success: bool, latency: float):
        """Record a request for statistics"""
        with self._lock:
            self.request_count += 1
            self.total_latency += latency
            if success:
                self.success_count += 1
            else:
                self.failure_count += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        with self._lock:
            uptime = (datetime.now() - self.start_time).total_seconds()
            avg_latency = self.total_latency / max(1, self.request_count)
            success_rate = (self.success_count / max(1, self.request_count)) * 100
            
            return {
                'uptime_seconds': uptime,
                'uptime_formatted': self._format_uptime(uptime),
                'total_requests': self.request_count,
                'success_count': self.success_count,
                'failure_count': self.failure_count,
                'success_rate': round(success_rate, 2),
                'average_latency_ms': round(avg_latency * 1000, 2)
            }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime as human-readable string"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        elif seconds < 86400:
            return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"
        else:
            return f"{int(seconds // 86400)}d {int((seconds % 86400) // 3600)}h"
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed status including key manager info"""
        stats = self.get_stats()
        
        # Get key manager status if available
        key_status = {}
        if self._key_manager:
            try:
                key_status = self._key_manager.get_status()
            except Exception as e:
                key_status = {'error': str(e)}
        
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime': stats,
            'key_manager': key_status,
            'system': self._get_system_info()
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        import os
        try:
            import psutil
            process = psutil.Process()
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'process_memory_mb': round(process.memory_info().rss / 1024 / 1024, 2)
            }
        except ImportError:
            return {'note': 'psutil not installed'}
        except Exception as e:
            return {'error': str(e)}
    
    def cleanup_old_files(self):
        """Clean up old status files"""
        try:
            max_age = 24 * 60 * 60  # 24 hours
            for f in STATUS_DIR.glob('*.json'):
                if f.stat().st_mtime < (time.time() - max_age):
                    f.unlink()
            self._last_cleanup = datetime.now()
        except Exception as e:
            print(f"[STATUS] Cleanup error: {e}")


# Global monitor instance
_status_monitor = APIStatusMonitor()


def get_status_monitor() -> APIStatusMonitor:
    """Get the global status monitor"""
    return _status_monitor


# Flask routes for status endpoints
@api_status_bp.route('/api/status', methods=['GET'])
def get_status():
    """Get basic status"""
    monitor = get_status_monitor()
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        **monitor.get_stats()
    })


@api_status_bp.route('/api/status/detailed', methods=['GET'])
def get_detailed_status():
    """Get detailed status with key manager info"""
    monitor = get_status_monitor()
    return jsonify(monitor.get_detailed_status())


@api_status_bp.route('/api/status/providers', methods=['GET'])
def get_provider_status():
    """Get status of all providers"""
    try:
        from guaranteed_endpoint import get_key_manager
        manager = get_key_manager()
        return jsonify(manager.get_status())
    except ImportError:
        return jsonify({'error': 'guaranteed_endpoint not available'})
    except Exception as e:
        return jsonify({'error': str(e)})


@api_status_bp.route('/api/status/health', methods=['GET'])
def get_health():
    """Health check endpoint - returns 200 if system is healthy"""
    try:
        from guaranteed_endpoint import get_key_manager
        manager = get_key_manager()
        status = manager.get_status()
        
        # Check if any provider is available
        if status['healthy_count'] > 0:
            return jsonify({
                'status': 'healthy',
                'healthy_providers': status['healthy_count'],
                'total_providers': status['total_count'],
                'best_provider': status['best_provider']
            }), 200
        else:
            return jsonify({
                'status': 'unhealthy',
                'message': 'No healthy providers available'
            }), 503
    except ImportError:
        return jsonify({
            'status': 'degraded',
            'message': 'guaranteed_endpoint not available'
        }), 200


@api_status_bp.route('/api/status/refresh', methods=['POST'])
def refresh_health():
    """Force refresh health check"""
    try:
        from guaranteed_endpoint import get_key_manager
        manager = get_key_manager()
        manager.run_health_check()
        return jsonify({
            'success': True,
            'status': manager.get_status()
        })
    except ImportError:
        return jsonify({'error': 'guaranteed_endpoint not available'})
    except Exception as e:
        return jsonify({'error': str(e)})


@api_status_bp.route('/api/stats', methods=['GET'])
def get_stats():
    """Get request statistics"""
    monitor = get_status_monitor()
    return jsonify(monitor.get_stats())


# Helper function to integrate with existing Flask apps
def register_status_routes(app):
    """Register status routes with a Flask app"""
    app.register_blueprint(api_status_bp)


# Convenience function for external use
def record_api_call(success: bool, latency: float):
    """Record an API call from anywhere"""
    monitor = get_status_monitor()
    monitor.record_request(success, latency)


if __name__ == "__main__":
    # Test the status module
    print("=" * 60)
    print("API STATUS MONITOR - TEST")
    print("=" * 60)
    
    # Simulate some requests
    monitor = get_status_monitor()
    
    # Record some test requests
    for i in range(5):
        monitor.record_request(success=True, latency=0.5)
    
    for i in range(2):
        monitor.record_request(success=False, latency=1.2)
    
    # Get stats
    print("\nBasic Stats:")
    stats = monitor.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")
    
    print("\nDetailed Status:")
    detailed = monitor.get_detailed_status()
    print(f"  timestamp: {detailed['timestamp']}")
    print(f"  uptime: {detailed['uptime']}")
    print(f"  key_manager: {'available' if detailed.get('key_manager') else 'not set'}")

