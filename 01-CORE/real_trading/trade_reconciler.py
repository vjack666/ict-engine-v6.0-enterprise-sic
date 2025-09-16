#!/usr/bin/env python3
"""
Trade Reconciler - ICT Engine v6.0 Enterprise
===========================================

Objetivo:
  Reconciliar operaciones registradas en TradeJournal con las posiciones/órdenes
  reales del broker (o simuladas) para detectar discrepancias.

Alcance inicial (ligero, extensible):
  - Comparar símbolos y volúmenes abiertos vs journal
  - Detectar entradas en journal sin posición abierta (posible cierre faltante)
  - Detectar posiciones abiertas sin entrada en journal (posible omisión de log)
  - Generar reporte en estructura dict y opción de persistir JSON

Dependencias suaves: TradeJournal y ejecutor con método opcional get_account_positions()
 (aún no implementado en MT5BrokerExecutor stub). Se permite inyectar un callable
 que retorne lista de posiciones para facilitar pruebas.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timezone
import json
from pathlib import Path

try:
    from real_trading.trade_journal import TradeJournal, JournalEntry  # type: ignore
except Exception:  # fallback blando
    TradeJournal = None  # type: ignore
    JournalEntry = None  # type: ignore

class TradeReconciler:
    def __init__(self,
                 journal: Optional[TradeJournal],  # type: ignore
                 positions_provider: Optional[Callable[[], List[Dict[str, Any]]]] = None,
                 base_path: Optional[Path] = None,
                 logger: Optional[Any] = None) -> None:
        self.journal = journal
        self.positions_provider = positions_provider
        self.base_path = base_path or Path('05-LOGS') / 'trading' / 'reconciliation'
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.logger = logger

    def _log(self, level: str, msg: str) -> None:
        if self.logger and hasattr(self.logger, level):
            try:
                getattr(self.logger, level)(f"[Reconciler] {msg}")
            except Exception:
                pass
        else:
            print(f"[Reconciler:{level.upper()}] {msg}")

    def reconcile(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        result: Dict[str, Any] = {
            'timestamp': now,
            'status': 'ok',
            'journal_available': bool(self.journal),
            'positions_available': bool(self.positions_provider),
            'discrepancies': [],
            'summary': {
                'journal_open_count': 0,
                'broker_position_count': 0,
                'missing_in_journal': 0,
                'missing_in_broker': 0
            }
        }
        if not self.journal or not self.positions_provider:
            result['status'] = 'incomplete'
            return result
        try:
            journal_open = []
            try:
                journal_open = self.journal.get_open_positions()  # type: ignore
            except Exception:
                journal_open = []
            broker_positions = []
            try:
                broker_positions = self.positions_provider() or []
            except Exception:
                broker_positions = []
            # Normalizar diccionarios {symbol: total_volume}
            def aggregate(entries):
                agg: Dict[str, float] = {}
                for e in entries:
                    try:
                        symbol = getattr(e, 'symbol', None)
                        vol = float(getattr(e, 'volume', 0.0))
                        if not symbol:
                            continue
                        agg[symbol] = agg.get(symbol, 0.0) + vol
                    except Exception:
                        continue
                return agg
            def aggregate_positions(positions):
                agg: Dict[str, float] = {}
                for p in positions:
                    try:
                        symbol = p.get('symbol')
                        vol = float(p.get('volume', 0.0))
                        if not symbol:
                            continue
                        agg[symbol] = agg.get(symbol, 0.0) + vol
                    except Exception:
                        continue
                return agg
            journal_agg = aggregate(journal_open)
            broker_agg = aggregate_positions(broker_positions)
            result['summary']['journal_open_count'] = len(journal_open)
            result['summary']['broker_position_count'] = len(broker_positions)
            # Detectar símbolos en broker sin journal
            for sym, vol in broker_agg.items():
                jvol = journal_agg.get(sym, 0.0)
                if jvol == 0.0:
                    result['discrepancies'].append({'type': 'missing_in_journal', 'symbol': sym, 'volume': vol})
            # Detectar símbolos en journal sin broker
            for sym, vol in journal_agg.items():
                bvol = broker_agg.get(sym, 0.0)
                if bvol == 0.0:
                    result['discrepancies'].append({'type': 'missing_in_broker', 'symbol': sym, 'volume': vol})
            # Contadores
            result['summary']['missing_in_journal'] = sum(1 for d in result['discrepancies'] if d['type'] == 'missing_in_journal')
            result['summary']['missing_in_broker'] = sum(1 for d in result['discrepancies'] if d['type'] == 'missing_in_broker')
            return result
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            return result

    def persist_report(self, report: Dict[str, Any]) -> Optional[Path]:
        try:
            filename = f"reconciliation_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
            path = self.base_path / filename
            path.write_text(json.dumps(report, indent=2), encoding='utf-8')
            self._log('info', f"Reporte persistido en {path}")
            return path
        except Exception as e:
            self._log('error', f"No se pudo persistir reporte: {e}")
            return None

__all__ = ['TradeReconciler']
