"""Execution Engine (P0)
Orquesta el ciclo de vida de órdenes hacia el broker (MT5 u otros).
Versión inicial mínima productiva.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
import threading
import uuid

from protocols.logging_central_protocols import create_safe_logger

OrderSide = Literal["BUY", "SELL"]
OrderType = Literal["MARKET", "LIMIT", "STOP"]

@dataclass
class OrderSpec:
    symbol: str
    side: OrderSide
    volume: float
    order_type: OrderType = "MARKET"
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    tag: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrackedOrder:
    client_id: str
    broker_id: Optional[int]
    spec: OrderSpec
    status: str
    created_at: datetime
    last_update: datetime
    fills: List[Dict[str, Any]] = field(default_factory=list)

class ExecutionError(Exception): ...
class OrderNotFound(Exception): ...

class ExecutionEngine:
    """Motor de ejecución simplificado con interfaz estable.
    Esta versión no envía aún a broker, se enfoca en tracking + logging estructurado.
    Posteriormente se conectará al `mt5_broker_executor`.
    """
    def __init__(self):
        self.logger = create_safe_logger("ExecutionEngine")
        self._orders: Dict[str, TrackedOrder] = {}
        self._lock = threading.Lock()

    def submit_order(self, spec: OrderSpec) -> str:
        if spec.volume <= 0:
            raise ExecutionError("Volume must be > 0")
        client_id = uuid.uuid4().hex
        now = datetime.utcnow()
        tracked = TrackedOrder(client_id=client_id, broker_id=None, spec=spec, status="PENDING", created_at=now, last_update=now)
        with self._lock:
            self._orders[client_id] = tracked
        self.logger.info(f"📝 Order accepted local tracking {spec.symbol} {spec.side} {spec.volume}", "execution")
        # TODO: integración real broker -> actualizar broker_id y estado
        return client_id

    def cancel_order(self, client_id: str) -> bool:
        with self._lock:
            order = self._orders.get(client_id)
            if not order:
                raise OrderNotFound(client_id)
            if order.status in ("CANCELLED", "FILLED"):
                return False
            order.status = "CANCELLED"
            order.last_update = datetime.utcnow()
        self.logger.warning(f"✋ Order {client_id} cancelled (local)", "execution")
        return True

    def get_order(self, client_id: str) -> Optional[TrackedOrder]:
        return self._orders.get(client_id)

    def list_open_orders(self) -> List[TrackedOrder]:
        return [o for o in self._orders.values() if o.status not in ("CANCELLED", "FILLED")]

    def record_fill(self, client_id: str, price: float, volume: float) -> None:
        with self._lock:
            order = self._orders.get(client_id)
            if not order:
                raise OrderNotFound(client_id)
            fill = {"time": datetime.utcnow(), "price": price, "volume": volume}
            order.fills.append(fill)
            order.status = "FILLED"
            order.last_update = datetime.utcnow()
        self.logger.info(f"✅ Order {client_id} filled @ {price} vol {volume}", "execution")

    def reconcile(self) -> Dict[str, Any]:
        # Placeholder: comparará estados internos vs broker
        snapshot = {"total_tracked": len(self._orders), "open": len(self.list_open_orders())}
        self.logger.debug(f"Reconcile snapshot {snapshot}", "execution")
        return snapshot

__all__ = [
    "ExecutionEngine", "OrderSpec", "TrackedOrder", "ExecutionError", "OrderNotFound"
]
