"""Backtest Persistence Utilities
===============================

Funciones ligeras para persistir resultados de backtests de forma
homogénea (JSON) en `04-DATA/reports/backtests/` con timestamp.

El objetivo es mantener la capa de persistencia separada del motor
para permitir futuras extensiones (parquet, DB, etc.).
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger

from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import json

BASE_DIR = Path('04-DATA') / 'reports' / 'backtests'


def persist_backtest_result(result: Dict[str, Any], prefix: str = 'ict') -> Optional[Path]:
    try:
        BASE_DIR.mkdir(parents=True, exist_ok=True)
        symbol = result.get('symbol', 'UNKNOWN')
        timeframe = result.get('timeframe', 'NA')
        ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        fname = f"{prefix}_{symbol}_{timeframe}_{ts}.json".replace('/', '_')
        out_path = BASE_DIR / fname
        payload = {
            'saved_at': datetime.now(timezone.utc).isoformat(),
            'result': result
        }
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2, default=str)
        return out_path
    except Exception:
        return None

__all__ = ["persist_backtest_result"]
