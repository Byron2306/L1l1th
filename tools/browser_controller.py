"""
Compatibility shim for BrowserController imports.
Provides a stable `BrowserController` symbol for code that expects it.
"""
from .browser_controller_thread import BrowserControllerThread as BrowserController

# Re-export helper
try:
    from .browser_controller_thread import get_browser as get_browser
except Exception:
    def get_browser():
        return BrowserController()

__all__ = ["BrowserController", "get_browser"]
