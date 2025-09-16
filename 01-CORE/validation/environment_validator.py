"""EnvironmentValidator
Valida el entorno de ejecución para producción:
- Versión de Python
- Directorios críticos
- Permisos de escritura básicos
- Dependencias opcionales clave
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import Dict, Any, List
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

try:
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
except Exception:  # pragma: no cover
    def create_safe_logger(name: str, **_):  # fallback mínimo
        class _Mini:
            def info(self, m: str, c: str): print(f"[INFO][{c}] {m}")
            def warning(self, m: str, c: str): print(f"[WARN][{c}] {m}")
            def error(self, m: str, c: str): print(f"[ERROR][{c}] {m}")
            def debug(self, m: str, c: str): print(f"[DEBUG][{c}] {m}")
        return _Mini()

class EnvironmentValidator:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = get_unified_logger("EnvironmentValidator")
        self._last_result: Dict[str, Any] = {}

    def validate(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'python_version': sys.version.split()[0],
            'status': 'OK',
            'checks': {},
            'warnings': [],
            'errors': []
        }
        checks = result['checks']
        # Python version
        major, minor, *_ = sys.version_info
        py_ok = (major, minor) >= (3, 11)
        checks['python_version>=3.11'] = py_ok
        if not py_ok:
            result['warnings'].append(f"Python {major}.{minor} inferior a 3.11")
        # Critical dirs
        critical = [
            self.project_root / '01-CORE',
            self.project_root / '04-DATA',
            self.project_root / '05-LOGS'
        ]
        for p in critical:
            exists = p.exists()
            checks[f'dir:{p.name}'] = exists
            if not exists:
                result['errors'].append(f"Missing dir {p}")
        # Write test in logs
        try:
            logs_dir = self.project_root / '05-LOGS' / 'system'
            logs_dir.mkdir(parents=True, exist_ok=True)
            test_file = logs_dir / '.env_write_test'
            test_file.write_text('ok')
            test_file.unlink(missing_ok=True)  # type: ignore[arg-type]
            checks['write_permission_logs'] = True
        except Exception as e:  # pragma: no cover
            checks['write_permission_logs'] = False
            result['errors'].append(f"Write perm error: {e}")
        # Optional deps (quick check)
        optional: List[str] = ['pandas', 'numpy']
        for mod in optional:
            try:
                __import__(mod)
                checks[f'dep:{mod}'] = True
            except Exception:
                checks[f'dep:{mod}'] = False
        if result['errors']:
            result['status'] = 'ERROR'
        elif result['warnings']:
            result['status'] = 'WARN'
        self._last_result = result
        self.logger.info(f"Validación entorno status={result['status']}", "env_validator")
        return result

    def last_result(self) -> Dict[str, Any]:
        return dict(self._last_result)

__all__ = ["EnvironmentValidator"]
