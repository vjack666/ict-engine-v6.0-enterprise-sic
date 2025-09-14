#!/usr/bin/env python3
"""
MT5 BROKER EXECUTOR (Stub) - ICT Engine v6.0 Enterprise
======================================================
Ejecutor de órdenes abstracto para MetaTrader 5.

Objetivos:
- Proveer interfaz `send_order` compatible con `ExecutionRouter`.
- Permitir modo simulado cuando MT5 no está disponible.
- Facilitar futura extensión para órdenes reales (market / pending).

La función real de envío debe integrarse con `MetaTrader5` (paquete oficial) cuando
esté instalado y haya conexión a la cuenta. Si no se detecta, opera en modo simulado.
"""
from __future__ import annotations
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import random
import time

try:
    import MetaTrader5 as mt5  # type: ignore
    _MT5_AVAILABLE = True
except Exception:
    mt5 = None  # type: ignore
    _MT5_AVAILABLE = False

try:
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
except ImportError:  # fallback
    from smart_trading_logger import enviar_senal_log as _compat_log  # type: ignore
    class _MiniLogger:
        def info(self,m,c): _compat_log("INFO",m,c)
        def warning(self,m,c): _compat_log("WARNING",m,c)
        def error(self,m,c): _compat_log("ERROR",m,c)
        def debug(self,m,c): _compat_log("DEBUG",m,c)
    def create_safe_logger(component_name: str, **_): return _MiniLogger()  # type: ignore

@dataclass
class MT5ExecutorConfig:
    simulate_if_unavailable: bool = True
    deviation: int = 10  # deslizamiento permitido
    magic_number: int = 777001

class MT5BrokerExecutor:
    def __init__(self, config: Optional[MT5ExecutorConfig] = None):
        self.config = config or MT5ExecutorConfig()
        self.logger = create_safe_logger("MT5BrokerExecutor")
        self.simulated = False
        self.connected = False
        self._init_mt5()
        self._snapshot_cache = None
        self._snapshot_ts = 0.0
        self._snapshot_ttl = 2.0  # segundos

    def _init_mt5(self) -> None:
        if not _MT5_AVAILABLE:
            self.logger.warning("MT5 no disponible - usando simulación", "EXECUTOR")
            self.simulated = True
            return
        try:
            if not mt5.initialize():  # type: ignore
                self.logger.error("Fallo initialize() - simulación activada", "EXECUTOR")
                self.simulated = True
                return
            account_info = mt5.account_info()  # type: ignore
            if account_info is None:
                self.logger.error("account_info() None - simulación activada", "EXECUTOR")
                self.simulated = True
                return
            self.connected = True
            self.logger.info(f"Conectado a MT5 acc={account_info.login}", "EXECUTOR")
        except Exception as e:
            self.logger.error(f"Excepción inicializando MT5: {e}", "EXECUTOR")
            self.simulated = True

    def _simulate_order(self, symbol: str, action: str, volume: float, price: Optional[float], sl: Optional[float], tp: Optional[float]) -> Dict[str, Any]:
        ticket = random.randint(10_000_000, 99_999_999)
        self.logger.info(f"[SIM] {action} {symbol} vol={volume} ticket={ticket}", "EXECUTOR")
        return {
            'success': True,
            'ticket': ticket,
            'mode': 'simulated',
            'symbol': symbol,
            'action': action,
            'requested_price': price,
            'sl': sl,
            'tp': tp,
            'timestamp': datetime.utcnow().isoformat()
        }

    def send_order(self, symbol: str, action: str, volume: float, price: Optional[float], sl: Optional[float], tp: Optional[float]) -> Dict[str, Any]:
        # Validaciones ligeras
        if volume <= 0:
            return {'success': False, 'error': 'invalid_volume'}
        if action not in ("BUY", "SELL"):
            return {'success': False, 'error': 'invalid_action'}

        if self.simulated or not self.connected:
            return self._simulate_order(symbol, action, volume, price, sl, tp)

        # Ruta real (placeholder simplificado)
        try:
            # Selección de tipo de orden market simple (BUY / SELL)
            order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL  # type: ignore
            symbol_info = mt5.symbol_info(symbol)  # type: ignore
            if symbol_info is None:
                return {'success': False, 'error': 'symbol_not_found'}
            if not symbol_info.visible:  # type: ignore
                mt5.symbol_select(symbol, True)  # type: ignore
            # Precio de mercado
            tick = mt5.symbol_info_tick(symbol)  # type: ignore
            if tick is None:
                return {'success': False, 'error': 'tick_unavailable'}
            market_price = tick.ask if action == "BUY" else tick.bid  # type: ignore
            request = {
                'action': mt5.TRADE_ACTION_DEAL,  # type: ignore
                'symbol': symbol,
                'volume': volume,
                'type': order_type,
                'price': market_price,
                'sl': sl,
                'tp': tp,
                'deviation': self.config.deviation,
                'magic': self.config.magic_number,
                'comment': 'ICT-EXEC'
            }
            result = mt5.order_send(request)  # type: ignore
            if result is None:
                return {'success': False, 'error': 'order_send_none'}
            if result.retcode != mt5.TRADE_RETCODE_DONE:  # type: ignore
                return {'success': False, 'error': f'retcode_{result.retcode}'}
            return {
                'success': True,
                'ticket': result.order,  # type: ignore
                'symbol': symbol,
                'action': action,
                'filled_price': result.price,  # type: ignore
                'mode': 'live',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {'success': False, 'error': f'exception:{e}'}

    def get_account_snapshot(self) -> Dict[str, Any]:
        """Retorna snapshot de cuenta con balance / equity reales si MT5 activo; simulados si no."""
        now = time.time()
        if self._snapshot_cache and (now - self._snapshot_ts) < self._snapshot_ttl:
            return self._snapshot_cache
        if self.simulated or not self.connected or not _MT5_AVAILABLE:
            # valores simulados ligeros
            base = 10_000.0
            drift = random.uniform(-50, 50)
            equity = base + drift
            snap = {
                'mode': 'simulated',
                'balance': base,
                'equity': equity,
                'timestamp': datetime.utcnow().isoformat()
            }
            self._snapshot_cache = snap; self._snapshot_ts = now
            return snap
        try:
            info = mt5.account_info()  # type: ignore
            if info is None:
                snap = {'mode': 'unknown', 'error': 'account_info_none'}
                self._snapshot_cache = snap; self._snapshot_ts = now
                return snap
            snap = {
                'mode': 'live',
                'balance': float(getattr(info, 'balance', 0.0)),
                'equity': float(getattr(info, 'equity', 0.0)),
                'login': getattr(info, 'login', None),
                'currency': getattr(info, 'currency', None),
                'timestamp': datetime.utcnow().isoformat()
            }
            self._snapshot_cache = snap; self._snapshot_ts = now
            return snap
        except Exception as e:
            snap = {'mode': 'error', 'error': str(e)}
            self._snapshot_cache = snap; self._snapshot_ts = now
            return snap

__all__ = ['MT5BrokerExecutor', 'MT5ExecutorConfig']
