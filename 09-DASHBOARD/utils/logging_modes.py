#!/usr/bin/env python3
"""
Dashboard Logging Modes Utilities
- Centralize logging mode selection for the dashboard
- Provide a context manager to silence stdout/stderr cleanly
"""
from __future__ import annotations
import os
import sys
import logging
from contextlib import contextmanager
from typing import Iterator, Optional

LOGGING_MODE_ENV = "ICT_LOGGING_MODE"  # values: silent|debug|verbose|dev

@contextmanager
def silence_stdout_stderr(enabled: bool = True) -> Iterator[None]:
    """Temporarily redirect stdout/stderr to devnull when enabled.

    Args:
        enabled: When True, redirect both stdout and stderr to os.devnull
    """
    if not enabled:
        yield
        return
    devnull = open(os.devnull, 'w', encoding='utf-8', buffering=1)
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout = devnull  # type: ignore[assignment]
        sys.stderr = devnull  # type: ignore[assignment]
        yield
    finally:
        try:
            devnull.flush()
            devnull.close()
        except Exception:
            pass
        sys.stdout = old_out  # type: ignore[assignment]
        sys.stderr = old_err  # type: ignore[assignment]


def apply_logging_mode(mode: Optional[str] = None) -> str:
    """Configure Python logging levels based on a simple mode.

    - silent: suppress console handlers; set root level WARNING; disable noisy loggers
    - debug: root INFO; keep console minimal
    - verbose/dev: root DEBUG

    Returns the resolved mode.
    """
    resolved = (mode or os.environ.get(LOGGING_MODE_ENV, "silent")).strip().lower()

    # Root logger baseline
    root = logging.getLogger()
    # Remove any existing console handlers across all loggers if silent
    def _remove_console_handlers_globally():
        try:
            # Root first
            for h in list(root.handlers):
                if isinstance(h, logging.StreamHandler):
                    try:
                        root.removeHandler(h)
                        h.flush()
                        h.close()
                    except Exception:
                        pass
            # Then all known loggers
            for name, logger in logging.Logger.manager.loggerDict.items():
                if isinstance(logger, logging.Logger):
                    for h in list(getattr(logger, 'handlers', [])):
                        if isinstance(h, logging.StreamHandler):
                            try:
                                logger.removeHandler(h)
                                h.flush()
                                h.close()
                            except Exception:
                                pass
        except Exception:
            pass

    if resolved == "silent":
        root.setLevel(logging.WARNING)
        _remove_console_handlers_globally()
        # Silence common noisy namespaces and stop propagation to root
        for name in [
            "matplotlib", "urllib3", "asyncio", "numexpr", "PIL",
            "DashboardIntegrator", "PatternDetector", "MT5Health",
            "OrderBlocksBlackBox", "order_blocks_detection", "order_blocks_validation", "order_blocks_dashboard",
        ]:
            lg = logging.getLogger(name)
            lg.setLevel(logging.ERROR)
            lg.propagate = False
    elif resolved == "debug":
        root.setLevel(logging.INFO)
    else:  # verbose/dev
        root.setLevel(logging.DEBUG)

    return resolved
