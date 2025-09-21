#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Black Box File Logger Utility
- Simple JSONL logger writing to 05-LOGS/<subfolder>/
- Propagate=False; safe serialization; UTF-8
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# Safe JSON default similar to order blocks
import json

def _json_default(o: object):
    try:
        import numpy as _np  # type: ignore
        if isinstance(o, (_np.generic,)):
            return o.item()
        if isinstance(o, (_np.ndarray,)):
            return o.tolist()
    except Exception:
        pass
    iso = getattr(o, 'isoformat', None)
    if callable(iso):
        try:
            return iso()
        except Exception:
            return str(o)
    if isinstance(o, (bool, int, float, str)):
        return o
    return str(o)

class BlackBoxLogger:
    def __init__(self, component: str, subfolder: str):
        self.component = component
        # Resolve project root as two parents up from this file (01-CORE/utils -> repo root)
        project_root = Path(__file__).resolve().parent.parent.parent
        self.log_dir = project_root / '05-LOGS' / subfolder
        self.log_dir.mkdir(parents=True, exist_ok=True)
        date = datetime.now().strftime('%Y-%m-%d')
        self.log_path = self.log_dir / f"{component.lower()}_{date}.log"
        self.logger = logging.getLogger(f"bb.{subfolder}.{component}")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        # Avoid duplicate handlers
        if not self.logger.handlers:
            fh = logging.FileHandler(self.log_path, encoding='utf-8')
            fh.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(message)s')
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    def _emit(self, level: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        payload: Dict[str, Any] = {
            'ts': datetime.now(timezone.utc).isoformat(),
            'level': level.upper(),
            'component': self.component,
            'message': message,
        }
        if data:
            payload['data'] = data
        try:
            self.logger.info(json.dumps(payload, ensure_ascii=False, default=_json_default))
        except Exception:
            # Fallback flat
            self.logger.info(json.dumps({'ts': payload['ts'], 'level': level, 'component': self.component, 'message': str(message)}, ensure_ascii=False))

    def info(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        self._emit('info', message, data)

    def warning(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        self._emit('warning', message, data)

    def error(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        self._emit('error', message, data)

    def debug(self, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        self._emit('debug', message, data)


# Factory/cache
_instances: Dict[str, BlackBoxLogger] = {}

def get_black_box_logger(component: str, subfolder: str) -> BlackBoxLogger:
    key = f"{subfolder}:{component}"
    inst = _instances.get(key)
    if inst is None:
        inst = BlackBoxLogger(component=component, subfolder=subfolder)
        _instances[key] = inst
    return inst
