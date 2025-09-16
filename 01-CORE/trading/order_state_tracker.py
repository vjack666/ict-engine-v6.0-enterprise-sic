"""OrderStateTracker
Seguimiento ligero de órdenes / posiciones para exposición y PnL agregado.
Se integra sin depender aún de un broker executor completo.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from threading import RLock

try:
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
except Exception:  # pragma: no cover
    def create_safe_logger(name: str, **_):  # fallback
        class _Mini:
            def info(self, m: str, c: str): print(f"[INFO][{c}] {m}")
            def warning(self, m: str, c: str): print(f"[WARN][{c}] {m}")
            def error(self, m: str, c: str): print(f"[ERROR][{c}] {m}")
            def debug(self, m: str, c: str): print(f"[DEBUG][{c}] {m}")
        return _Mini()

class OrderStateTracker:
    def __init__(self):
        self.logger = get_unified_logger("OrderStateTracker")
        self._lock = RLock()
        self._positions: Dict[str, Dict[str, Any]] = {}
        self._closed: List[Dict[str, Any]] = []

    def upsert_position(self, symbol: str, lots: float, entry_price: float, direction: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        with self._lock:
            pos = self._positions.get(symbol, {
                'symbol': symbol,
                'lots': 0.0,
                'avg_price': entry_price,
                'direction': direction,
                'opened_at': datetime.now(timezone.utc).isoformat(),
                'metadata': metadata or {}
            })
            # Simple averaging (no FIFO for ahora)
            total_lots = pos['lots'] + lots
            if total_lots > 0:
                pos['avg_price'] = round((pos['avg_price'] * pos['lots'] + entry_price * lots) / total_lots, 5)
            pos['lots'] = round(total_lots, 2)
            pos['direction'] = direction
            self._positions[symbol] = pos
            self.logger.debug(f"Upsert {symbol} lots={pos['lots']} avg={pos['avg_price']}", 'order_tracker')

    def close_position(self, symbol: str, exit_price: float) -> None:
        with self._lock:
            pos = self._positions.pop(symbol, None)
            if not pos:
                return
            pnl = (exit_price - pos['avg_price']) * pos['lots'] * (1 if pos['direction'].lower() == 'buy' else -1)
            rec = {
                **pos,
                'closed_at': datetime.now(timezone.utc).isoformat(),
                'exit_price': exit_price,
                'pnl': round(pnl, 2)
            }
            self._closed.append(rec)
            self.logger.info(f"Closed {symbol} pnl={rec['pnl']}", 'order_tracker')

    def exposure_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            total_lots = sum(p['lots'] for p in self._positions.values())
            symbols = list(self._positions.keys())
            unrealized = 0.0  # Placeholder sin feed de precios actualizados
            return {
                'open_positions': len(self._positions),
                'total_lots': round(total_lots, 2),
                'symbols': symbols,
                'unrealized_pnl': unrealized,
            }

    def recent_closed(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._closed[-limit:])

__all__ = ["OrderStateTracker"]
