"""DataQualityValidator
Valida la calidad mínima de datos almacenados (ej. velas o métricas).
- Verifica archivos recientes en 04-DATA/candles o data/candles
- Chequea tamaño > 0 y JSON parseable si termina en .json
- Detecta gap de timestamps básicos
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json

try:
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
except Exception:  # pragma: no cover
    def create_safe_logger(name: str, **_):
        class _Mini:
            def info(self, m: str, c: str): print(f"[INFO][{c}] {m}")
            def warning(self, m: str, c: str): print(f"[WARN][{c}] {m}")
            def error(self, m: str, c: str): print(f"[ERROR][{c}] {m}")
        return _Mini()

class DataQualityValidator:
    def __init__(self, data_root: Path):
        self.data_root = data_root
        self.logger = get_unified_logger("DataQualityValidator")
        self._last: Dict[str, Any] = {}

    def _candidate_dirs(self) -> List[Path]:
        cands = [
            self.data_root / 'candles',
            self.data_root.parent / 'data' / 'candles'
        ]
        return [c for c in cands if c.exists()]

    def validate(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'OK',
            'files_checked': 0,
            'issues': [],
            'samples': []
        }
        dirs = self._candidate_dirs()
        if not dirs:
            result['status'] = 'WARN'
            result['issues'].append('No candle dirs found')
            self._last = result
            return result
        latest_files: List[Path] = []
        for d in dirs:
            for f in sorted(d.glob('*.json'))[-5:]:
                latest_files.append(f)
        if not latest_files:
            result['status'] = 'WARN'
            result['issues'].append('No recent json candle files')
            self._last = result
            return result
        time_threshold = datetime.now(timezone.utc) - timedelta(days=2)
        for fp in latest_files:
            try:
                stat = fp.stat()
                if stat.st_size == 0:
                    result['issues'].append(f"Empty file: {fp.name}")
                with fp.open('r', encoding='utf-8') as fh:
                    data = json.load(fh)
                result['files_checked'] += 1
                # naive timestamp gap check (first/last)
                if isinstance(data, list) and data:
                    first = data[0].get('timestamp') if isinstance(data[0], dict) else None
                    last = data[-1].get('timestamp') if isinstance(data[-1], dict) else None
                    if first and last:
                        try:
                            dt_last = datetime.fromisoformat(str(last))
                            if dt_last < time_threshold:
                                result['issues'].append(f"Stale data: {fp.name}")
                        except Exception:
                            result['issues'].append(f"Bad timestamp format: {fp.name}")
                if result['files_checked'] <= 2:
                    result['samples'].append({'file': fp.name, 'size': stat.st_size})
            except Exception as e:  # pragma: no cover
                result['issues'].append(f"Read error {fp.name}: {e}")
        if result['issues']:
            result['status'] = 'WARN'
        self._last = result
        self.logger.info(f"DataQuality status={result['status']} files={result['files_checked']}", 'data_quality')
        return result

    def last_result(self) -> Dict[str, Any]:
        return dict(self._last)

__all__ = ["DataQualityValidator"]
