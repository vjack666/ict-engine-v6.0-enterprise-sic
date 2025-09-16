#!/usr/bin/env python3
"""Enterprise Tabs Manager (minimal implementation)

Provides a lightweight manager for dashboard tabs so other
modules (stress tests, dashboards) can import without failure.
Designed to be forward-compatible: methods are defensive and
safe even if full enterprise dashboard stack is not loaded.
"""
from __future__ import annotations

from typing import Dict, Any, List, Optional, Callable
import time

try:
    from smart_trading_logger import SmartTradingLogger  # type: ignore
except Exception:  # Fallback simple logger
    class SmartTradingLogger:  # type: ignore
        def __init__(self, name: str = "EnterpriseTabs"):
            self._name = name
        def info(self, msg: str): print(f"[INFO][{self._name}] {msg}")
        def warning(self, msg: str): print(f"[WARN][{self._name}] {msg}")
        def error(self, msg: str): print(f"[ERROR][{self._name}] {msg}")
        def debug(self, msg: str): pass


# Fallback helpers defined once to avoid redefinition warnings
class _FallbackDashboardApp:  # minimal shape
    def __init__(self):
        self.started = False
    def run(self, *_, **__):
        self.started = True


class _FallbackICTDashboard:
    def __init__(self, *_, **__):
        self.config = {"fallback": True}
    def start(self):
        return False

def setup_logging(level: str = "INFO"):
    """Return a SmartTradingLogger configured for dashboard usage.

    This is a lightweight facade so tests and other modules can
    obtain a working logger without importing deep internals.
    """
    logger = SmartTradingLogger("dashboard")  # type: ignore[name-defined]
    # SmartTradingLogger already handles level mapping internally via constructor;
    # keep it simple and rely on its defaults for now.
    return logger


def create_dashboard_app():
    """Create and return a minimal dashboard app instance.

    Tries to load the enterprise dashboard app; falls back to a simple
    placeholder object if dependencies aren't available. This keeps
    tests and light integrations working.
    """
    try:
        # Prefer local package import
        from .dashboard import ICTDashboardApp  # type: ignore
    except Exception:
        try:
            from dashboard import ICTDashboardApp  # type: ignore
        except Exception:
            return _FallbackDashboardApp()
    try:
        return ICTDashboardApp()  # type: ignore[name-defined]
    except Exception:
        # Final fallback if constructor fails
        return _FallbackDashboardApp()


def create_ict_dashboard():
    """Create and return the main ICTDashboard object if available.

    Provides a resilient import path so that tests can import this
    function even if the full dashboard stack isn't installed.
    """
    try:
        from .ict_dashboard import ICTDashboard  # type: ignore
    except Exception:
        try:
            from ict_dashboard import ICTDashboard  # type: ignore
        except Exception:
            return _FallbackICTDashboard()
    try:
        return ICTDashboard()  # type: ignore[name-defined]
    except Exception:
        return _FallbackICTDashboard()


class EnterpriseTabsManager:
    """Minimal enterprise tabs manager.

    Responsibilities:
    - Maintain registry of available tabs
    - Provide lazy creation of tab structures
    - Offer metadata for stress tests & dashboards
    """

    def __init__(self, logger: Optional[SmartTradingLogger] = None):  # type: ignore[name-defined]
        self.logger = logger or SmartTradingLogger("EnterpriseTabs")
        self._tabs: Dict[str, Dict[str, Any]] = {}
        self._creation_hooks: Dict[str, Callable[[], Dict[str, Any]]] = {}
        self._initialized = False

    # ---------------------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------------------
    def initialize_all_tabs(self) -> None:
        if self._initialized:
            return
        baseline = [
            ("main", lambda: {"id": "main", "title": "Main Overview", "content": "System Overview", "created_at": time.time()}),
            ("patterns", lambda: {"id": "patterns", "title": "Patterns", "content": "ICT Patterns Analysis", "created_at": time.time()}),
            ("performance", lambda: {"id": "performance", "title": "Performance", "content": "Performance Metrics", "created_at": time.time()}),
        ]
        for name, hook in baseline:
            self._creation_hooks[name] = hook
        # Eager create baseline
        for name in self._creation_hooks:
            self.create_tab(name)
        self._initialized = True
        self.logger.info(f"Initialized {len(self._tabs)} tabs (minimal implementation)")

    # ---------------------------------------------------------------------
    # Tab Operations
    # ---------------------------------------------------------------------
    def get_available_tabs(self) -> List[str]:
        return list(self._tabs.keys()) if self._tabs else list(self._creation_hooks.keys())

    def create_tab(self, tab_name: str) -> Dict[str, Any]:
        if tab_name in self._tabs:
            return self._tabs[tab_name]
        hook = self._creation_hooks.get(tab_name)
        if hook:
            try:
                tab = hook()
            except Exception as e:  # pragma: no cover
                self.logger.error(f"Failed to create tab '{tab_name}': {e}")
                tab = {"id": tab_name, "title": tab_name.title(), "content": "Error creating tab"}
        else:
            tab = {"id": tab_name, "title": tab_name.title(), "content": "Dynamic Tab"}
        self._tabs[tab_name] = tab
        return tab

    def get_tab(self, tab_name: str) -> Optional[Dict[str, Any]]:
        return self._tabs.get(tab_name)

    # ---------------------------------------------------------------------
    # Metadata & Diagnostics
    # ---------------------------------------------------------------------
    def get_tabs_metadata(self) -> Dict[str, Any]:
        return {
            "count": len(self._tabs),
            "initialized": self._initialized,
            "tabs": list(self._tabs.keys()),
        }

    def refresh(self) -> None:
        # Placeholder for future dynamic refresh logic
        pass

__all__ = [
    "EnterpriseTabsManager",
    "setup_logging",
    "create_dashboard_app",
    "create_ict_dashboard",
]
