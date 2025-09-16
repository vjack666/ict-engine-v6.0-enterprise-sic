#!/usr/bin/env python3
"""
🧩 CONFIG LOADER - ICT ENGINE v6.0 ENTERPRISE
============================================
Carga configuración jerárquica:
1. Defaults embebidos
2. Archivo JSON/YAML (si existe)
3. Overrides variables de entorno (prefijo ICT_*)
Provee acceso seguro y tipado ligero.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import Any, Dict, Optional
from pathlib import Path
import os
import json

try:
    import yaml as _yaml  # opcional
    _YAML = True
except Exception:  # pragma: no cover
    _yaml = None  # type: ignore
    _YAML = False

try:
    from protocols.logging_central_protocols import create_safe_logger, LogLevel  # type: ignore
except Exception:
    def create_safe_logger(name: str, **_):  # type: ignore
        class _L:  # pragma: no cover
            def info(self,m,c=""): print(f"[INFO][{name}][{c}] {m}")
            def warning(self,m,c=""): print(f"[WARN][{name}][{c}] {m}")
            def error(self,m,c=""): print(f"[ERR][{name}][{c}] {m}")
            def debug(self,m,c=""): print(f"[DBG][{name}][{c}] {m}")
        return _L()
    class LogLevel:  # type: ignore
        INFO = "INFO"

class ConfigLoader:
    def __init__(self, 
                 defaults: Optional[Dict[str, Any]] = None, 
                 file_path: Optional[Path] = None,
                 logger=None):
        self.defaults = defaults or {}
        self.file_path = file_path
        
        # Use external logger if provided, otherwise create one
        if logger:
            self.logger = logger
        else:
            self.logger = get_unified_logger("ConfigLoader")
        
        self._config: Dict[str, Any] = {}
        self.reload()

    def _load_file(self) -> Dict[str, Any]:
        if not self.file_path or not self.file_path.exists():
            return {}
        try:
            if self.file_path.suffix.lower() in ('.yaml', '.yml') and _YAML and _yaml is not None:
                return _yaml.safe_load(self.file_path.read_text(encoding='utf-8')) or {}
            if self.file_path.suffix.lower() == '.json':
                return json.loads(self.file_path.read_text(encoding='utf-8'))
        except Exception as e:
            self.logger.error(f"Error cargando config archivo: {e}", "CONFIG")
        return {}

    def _load_env_overrides(self) -> Dict[str, Any]:
        overrides: Dict[str, Any] = {}
        prefix = "ICT_"
        for k, v in os.environ.items():
            if k.startswith(prefix):
                key = k[len(prefix):].lower()
                # intentar parsear numérico o booleano
                if v.isdigit():
                    overrides[key] = int(v)
                else:
                    lv = v.lower()
                    if lv in ("true", "false"):
                        overrides[key] = (lv == "true")
                    else:
                        try:
                            overrides[key] = float(v)
                        except Exception:
                            overrides[key] = v
        return overrides

    def reload(self) -> None:
        file_conf = self._load_file()
        env_conf = self._load_env_overrides()
        merged = {**self.defaults, **file_conf, **env_conf}
        self._config = merged
        self.logger.info(f"Configuración cargada keys={list(merged.keys())}", "CONFIG")

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._config)

__all__ = ["ConfigLoader"]
