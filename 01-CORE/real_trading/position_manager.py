#!/usr/bin/env python3
"""
📌 POSITION MANAGER - ICT ENGINE v6.0 ENTERPRISE
================================================

Responsabilidad:
- Mantener snapshot ligero de posiciones abiertas
- Calcular exposición neta por símbolo y global
- Validar límites rápidos antes de enviar orden (hook ExecutionRouter)
- Complementar RiskGuard (no duplicar reglas avanzadas)

Notas:
- Thread-safe mediante lock
- No depende de MT5 directamente (se puede sincronizar externamente)
- Optimizado para consultas frecuentes en tiempo real
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple, Any
from threading import Lock
from datetime import datetime, timezone

try:
    from protocols.logging_central_protocols import create_safe_logger, LogLevel  # type: ignore
    _LOG_OK = True
except Exception:
    _LOG_OK = False
    def create_safe_logger(name: str, **_):  # type: ignore
        class _L:  # pragma: no cover
            def info(self,m,c=""): print(f"[INFO][{name}][{c}] {m}")
            def warning(self,m,c=""): print(f"[WARN][{name}][{c}] {m}")
            def error(self,m,c=""): print(f"[ERR][{name}][{c}] {m}")
            def debug(self,m,c=""): print(f"[DBG][{name}][{c}] {m}")
        return _L()
    class LogLevel:  # type: ignore
        INFO = "INFO"

@dataclass(frozen=True)
class Position:
    symbol: str
    direction: str  # 'buy' / 'sell'
    volume: float
    entry_price: float
    ticket: Optional[int]
    opened_at: datetime

class PositionManagerConfig:
    def __init__(self,
                 max_positions_global: int = 20,
                 max_positions_per_symbol: int = 8,
                 max_volume_per_symbol: float = 10.0,
                 max_total_volume: float = 50.0):
        self.max_positions_global = max_positions_global
        self.max_positions_per_symbol = max_positions_per_symbol
        self.max_volume_per_symbol = max_volume_per_symbol
        self.max_total_volume = max_total_volume

class PositionManager:
    def __init__(self, 
                 config: Optional[PositionManagerConfig] = None,
                 logger=None,
                 max_positions: int = 100,
                 max_exposure_per_symbol: float = 150000.0):
        self.config = config or PositionManagerConfig(
            max_positions_global=max_positions,
            max_volume_per_symbol=max_exposure_per_symbol
        )
        self._positions: Dict[int, Position] = {}
        self._lock = Lock()
        
        # Use external logger if provided, otherwise create one
        if logger:
            self.logger = logger
        else:
            self.logger = get_unified_logger("PositionManager")
        
        # Compatibility properties
        self.max_exposure_per_symbol = max_exposure_per_symbol
        self._exposure = {}  # Symbol -> current exposure

    def get_symbol_exposure(self, symbol: str) -> float:
        """Get current exposure for a symbol"""
        with self._lock:
            return self._exposure.get(symbol, 0.0)
    
    def update_symbol_exposure(self, symbol: str, volume: float, direction: str) -> None:
        """Update exposure when position is added/removed"""
        with self._lock:
            current = self._exposure.get(symbol, 0.0)
            if direction.lower() == 'buy':
                self._exposure[symbol] = current + volume
            else:  # sell
                self._exposure[symbol] = current - volume

    # ---------------- Core Ops ----------------
    def add_position(self, ticket: int, symbol: str, direction: str, volume: float, entry_price: float) -> None:
        if volume <= 0:
            self.logger.warning(f"Ignorando add_position volumen<=0 ticket={ticket}", "POSITION")
            return
        pos = Position(symbol=symbol, direction=direction.lower(), volume=volume, entry_price=entry_price,
                       ticket=ticket, opened_at=datetime.now(timezone.utc))
        with self._lock:
            self._positions[ticket] = pos
            
        # Update exposure tracking
        self.update_symbol_exposure(symbol, volume, direction)
        self.logger.debug(f"Añadida posición ticket={ticket} {symbol} {direction} {volume}", "POSITION")

    def remove_position(self, ticket: int) -> None:
        with self._lock:
            if ticket in self._positions:
                pos = self._positions.pop(ticket, None)
                if pos:
                    # Update exposure tracking (reverse direction)
                    opposite_direction = 'sell' if pos.direction == 'buy' else 'buy'
                    self.update_symbol_exposure(pos.symbol, pos.volume, opposite_direction)
                self.logger.debug(f"Removida posición ticket={ticket}", "POSITION")

    def snapshot(self) -> List[Position]:
        with self._lock:
            return list(self._positions.values())

    # ---------------- Exposure Metrics ----------------
    def exposure_per_symbol(self) -> Dict[str, float]:
        exp: Dict[str, float] = {}
        with self._lock:
            for p in self._positions.values():
                exp[p.symbol] = exp.get(p.symbol, 0.0) + p.volume
        return exp

    def total_volume(self) -> float:
        with self._lock:
            return sum(p.volume for p in self._positions.values())

    def counts(self) -> Tuple[int, Dict[str, int]]:
        per_symbol: Dict[str, int] = {}
        with self._lock:
            for p in self._positions.values():
                per_symbol[p.symbol] = per_symbol.get(p.symbol, 0) + 1
            return len(self._positions), per_symbol

    # ---------------- Validation ----------------
    def validate_new_order(self, symbol: str, volume: float) -> Tuple[bool, str]:
        if volume <= 0:
            return False, "invalid_volume"
        with self._lock:
            current_positions = len(self._positions)
            if current_positions >= self.config.max_positions_global:
                return False, "max_positions_global"
            per_symbol_count = sum(1 for p in self._positions.values() if p.symbol == symbol)
            if per_symbol_count >= self.config.max_positions_per_symbol:
                return False, "max_positions_symbol"
            exp_symbol = sum(p.volume for p in self._positions.values() if p.symbol == symbol)
            if (exp_symbol + volume) > self.config.max_volume_per_symbol:
                return False, "max_volume_symbol"
            total_vol = sum(p.volume for p in self._positions.values())
            if (total_vol + volume) > self.config.max_total_volume:
                return False, "max_volume_total"
        return True, "ok"

    # ---------------- CRITICAL PRODUCTION METHODS ----------------
    
    def get_open_positions(self) -> List[Dict[str, Any]]:
        """Get all open positions in a format compatible with trading systems"""
        positions_list = []
        with self._lock:
            for ticket, pos in self._positions.items():
                position_dict = {
                    "ticket": ticket,
                    "symbol": pos.symbol,
                    "direction": pos.direction,
                    "volume": pos.volume,
                    "entry_price": pos.entry_price,
                    "opened_at": pos.opened_at.isoformat(),
                    "current_price": 0.0,  # Would be updated by sync_with_broker
                    "pnl": 0.0,  # Would be calculated by get_pnl
                    "unrealized_pnl": 0.0
                }
                positions_list.append(position_dict)
        
        self.logger.debug(f"Retrieved {len(positions_list)} open positions", "POSITION")
        return positions_list
    
    def close_position(self, ticket: int, close_price: Optional[float] = None) -> bool:
        """Close a specific position by ticket"""
        try:
            with self._lock:
                if ticket not in self._positions:
                    self.logger.warning(f"Position ticket {ticket} not found for closing", "POSITION")
                    return False
                
                pos = self._positions[ticket]
                self.logger.info(f"Closing position ticket={ticket} {pos.symbol} {pos.direction} {pos.volume}", "POSITION")
                
                # Remove from tracking
                self.remove_position(ticket)
                
                # Log closure
                self.logger.info(f"Position {ticket} closed successfully", "POSITION")
                return True
                
        except Exception as e:
            self.logger.error(f"Error closing position {ticket}: {e}", "POSITION")
            return False
    
    def get_total_exposure(self) -> Dict[str, float]:
        """Get total exposure breakdown by symbol and direction"""
        exposure_breakdown = {}
        
        with self._lock:
            for pos in self._positions.values():
                if pos.symbol not in exposure_breakdown:
                    exposure_breakdown[pos.symbol] = {
                        "buy_volume": 0.0,
                        "sell_volume": 0.0,
                        "net_volume": 0.0,
                        "total_positions": 0
                    }
                
                if pos.direction == "buy":
                    exposure_breakdown[pos.symbol]["buy_volume"] += pos.volume
                else:
                    exposure_breakdown[pos.symbol]["sell_volume"] += pos.volume
                
                exposure_breakdown[pos.symbol]["total_positions"] += 1
            
            # Calculate net exposure
            for symbol_data in exposure_breakdown.values():
                symbol_data["net_volume"] = symbol_data["buy_volume"] - symbol_data["sell_volume"]
        
        return exposure_breakdown
    
    def get_pnl(self, current_prices: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """Calculate P&L for all positions
        
        Args:
            current_prices: Dict of symbol -> current_price for P&L calculation
            
        Returns:
            Dict with 'total_pnl', 'realized_pnl', 'unrealized_pnl', and per-symbol breakdown
        """
        if current_prices is None:
            current_prices = {}
        
        pnl_breakdown = {
            "total_pnl": 0.0,
            "realized_pnl": 0.0,  # Would need trade history for this
            "unrealized_pnl": 0.0,
            "positions": {}
        }
        
        with self._lock:
            for ticket, pos in self._positions.items():
                current_price = current_prices.get(pos.symbol, pos.entry_price)
                
                # Calculate unrealized P&L
                if pos.direction == "buy":
                    position_pnl = (current_price - pos.entry_price) * pos.volume
                else:  # sell
                    position_pnl = (pos.entry_price - current_price) * pos.volume
                
                pnl_breakdown["positions"][ticket] = {
                    "symbol": pos.symbol,
                    "direction": pos.direction,
                    "volume": pos.volume,
                    "entry_price": pos.entry_price,
                    "current_price": current_price,
                    "unrealized_pnl": position_pnl
                }
                
                pnl_breakdown["unrealized_pnl"] += position_pnl
        
        pnl_breakdown["total_pnl"] = pnl_breakdown["realized_pnl"] + pnl_breakdown["unrealized_pnl"]
        
        return pnl_breakdown
    
    def sync_with_broker(self, broker_positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synchronize internal positions with broker positions
        
        Args:
            broker_positions: List of position dicts from broker (MT5, etc.)
            
        Returns:
            Sync report with discrepancies and actions taken
        """
        sync_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "internal_positions": len(self._positions),
            "broker_positions": len(broker_positions),
            "discrepancies_found": [],
            "positions_added": [],
            "positions_removed": [],
            "positions_updated": [],
            "sync_successful": False
        }
        
        try:
            broker_tickets = set()
            
            # Process broker positions
            for broker_pos in broker_positions:
                ticket = broker_pos.get("ticket")
                symbol = broker_pos.get("symbol") 
                direction = broker_pos.get("type", "").lower()
                volume = broker_pos.get("volume", 0.0)
                entry_price = broker_pos.get("price_open", 0.0)
                
                if ticket is None:
                    continue
                
                broker_tickets.add(ticket)
                
                # Check if position exists internally
                with self._lock:
                    if ticket not in self._positions:
                        # Add missing position (ensure symbol is valid)
                        safe_symbol = symbol or "UNKNOWN"
                        self.add_position(ticket, safe_symbol, direction, volume, entry_price)
                        sync_report["positions_added"].append(ticket)
                        self.logger.info(f"Added missing position from broker: {ticket}", "SYNC")
                    else:
                        # Verify position details
                        internal_pos = self._positions[ticket]
                        if (internal_pos.symbol != symbol or 
                            internal_pos.direction != direction or 
                            abs(internal_pos.volume - volume) > 0.01):
                            
                            sync_report["discrepancies_found"].append({
                                "ticket": ticket,
                                "internal": {
                                    "symbol": internal_pos.symbol,
                                    "direction": internal_pos.direction, 
                                    "volume": internal_pos.volume
                                },
                                "broker": {
                                    "symbol": symbol,
                                    "direction": direction,
                                    "volume": volume
                                }
                            })
            
            # Find positions to remove (exist internally but not in broker)
            with self._lock:
                internal_tickets = set(self._positions.keys())
                for ticket in internal_tickets - broker_tickets:
                    self.remove_position(ticket)
                    sync_report["positions_removed"].append(ticket)
                    self.logger.warning(f"Removed orphaned position: {ticket}", "SYNC")
            
            sync_report["sync_successful"] = True
            self.logger.info(f"Position sync completed: {len(sync_report['positions_added'])} added, "
                           f"{len(sync_report['positions_removed'])} removed, "
                           f"{len(sync_report['discrepancies_found'])} discrepancies", "SYNC")
            
        except Exception as e:
            sync_report["sync_successful"] = False
            sync_report["error"] = str(e)
            self.logger.error(f"Position sync failed: {e}", "SYNC")
        
        return sync_report
    
    # ---------------- HEALTH MONITORING ----------------
    
    def is_healthy(self) -> bool:
        """Check if Position Manager is in healthy state"""
        try:
            with self._lock:
                # Basic health checks
                position_count = len(self._positions)
                total_volume = sum(p.volume for p in self._positions.values())
                
                # Check limits
                if position_count > self.config.max_positions_global:
                    self.logger.warning(f"Position count {position_count} exceeds limit {self.config.max_positions_global}", "HEALTH")
                    return False
                
                if total_volume > self.config.max_total_volume:
                    self.logger.warning(f"Total volume {total_volume} exceeds limit {self.config.max_total_volume}", "HEALTH")
                    return False
                
                # Check for data integrity
                for ticket, pos in self._positions.items():
                    if pos.volume <= 0 or pos.entry_price <= 0:
                        self.logger.warning(f"Invalid position data for ticket {ticket}", "HEALTH")
                        return False
                
                return True
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", "HEALTH")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status information for monitoring"""
        try:
            with self._lock:
                exposure = self.get_total_exposure()
                pnl_data = self.get_pnl()
                position_count, per_symbol_count = self.counts()
                
                status = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "healthy": self.is_healthy(),
                    "positions": {
                        "total_count": position_count,
                        "per_symbol_count": per_symbol_count,
                        "total_volume": self.total_volume()
                    },
                    "exposure": exposure,
                    "pnl": {
                        "total": pnl_data["total_pnl"],
                        "unrealized": pnl_data["unrealized_pnl"]
                    },
                    "limits": {
                        "max_positions": self.config.max_positions_global,
                        "max_volume_per_symbol": self.config.max_volume_per_symbol,
                        "max_total_volume": self.config.max_total_volume
                    },
                    "utilization": {
                        "position_utilization": f"{(position_count / self.config.max_positions_global * 100):.1f}%",
                        "volume_utilization": f"{(self.total_volume() / self.config.max_total_volume * 100):.1f}%"
                    }
                }
                
                return status
                
        except Exception as e:
            self.logger.error(f"Status retrieval failed: {e}", "STATUS")
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "healthy": False,
                "error": str(e)
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring"""
        return {
            "position_count": len(self._positions),
            "total_volume": self.total_volume(),
            "symbol_count": len(self.exposure_per_symbol()),
            "health_status": "healthy" if self.is_healthy() else "unhealthy",
            "last_update": datetime.now(timezone.utc).isoformat()
        }

__all__ = ["PositionManager", "PositionManagerConfig", "Position"]
