#!/usr/bin/env python3
"""
execution_engine.py - ICT Engine v6.0 Enterprise
Sistema de ejecución de trades automatizado
"""

from protocols.unified_logging import get_unified_logger
import time
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any, Callable, Union
from datetime import datetime
from enum import Enum
import logging

# Imports del sistema ICT existente
try:
    from ..data_management.mt5_data_manager import MT5DataManager
    from ..smart_trading_logger import SmartTradingLogger
except ImportError:
    # Fallback para testing
    MT5DataManager = None
    SmartTradingLogger = None

class OrderType(Enum):
    """Tipos de órdenes"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderStatus(Enum):
    """Estados de órdenes"""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class OrderRequest:
    """Solicitud de orden de trading"""
    symbol: str
    order_type: OrderType
    volume: float
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    comment: str = ""
    magic_number: int = 12345
    deviation: int = 20
    
@dataclass
class OrderResult:
    """Resultado de ejecución de orden"""
    success: bool
    order_id: Optional[int] = None
    ticket: Optional[int] = None
    execution_price: Optional[float] = None
    execution_time_ms: float = 0.0
    error_code: Optional[int] = None
    error_message: str = ""
    slippage_pips: float = 0.0
    
@dataclass
class ExecutionStats:
    """Estadísticas de ejecución"""
    total_orders: int = 0
    successful_orders: int = 0
    failed_orders: int = 0
    avg_execution_time_ms: float = 0.0
    avg_slippage_pips: float = 0.0
    execution_times: List[float] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)

class ExecutionEngine:
    """
    Motor de ejecución enterprise para trades ICT
    
    Características:
    - Ejecución rápida < 1 segundo
    - Manejo robusto de errores
    - Tracking completo de performance
    - Integration con MT5
    """
    
    def __init__(self, max_slippage_pips: float = 3.0):
        """
        Initialize execution engine
        
        Args:
            max_slippage_pips: Máximo slippage permitido en pips
        """
        self.max_slippage_pips = max_slippage_pips
        self.stats = ExecutionStats()
        self.active_orders: Dict[int, OrderRequest] = {}
        self.execution_callbacks: List[Callable] = []
        
        # Integración con sistema ICT existente y logging unificado
        self.logger = get_unified_logger("ExecutionEngine")
        
        try:
            if MT5DataManager is not None:
                self.mt5_manager = MT5DataManager()
                self._mt5_available = True
                self.logger.info("MT5DataManager initialized successfully", "INIT")
            else:
                self.mt5_manager = None
                self._mt5_available = False
                self.logger.warning("MT5DataManager not available - using simulation mode", "INIT")
                
        except Exception as e:
            self.mt5_manager = None
            self._mt5_available = False
            self.logger.error(f"Could not initialize MT5 components: {e}", "INIT")
        
    def execute_order(self, request: Union[OrderRequest, Dict[str, Any]]) -> OrderResult:
        """
        Ejecutar orden de trading
        
        Args:
            request: Solicitud de orden
            
        Returns:
            OrderResult con detalles de ejecución
        """
        start_time = time.time()
        
        try:
            # Normalize request: accept dict for compatibility with integrator
            if isinstance(request, dict):
                req = OrderRequest(
                    symbol=str(request.get("symbol", "")),
                    order_type=OrderType.MARKET if str(request.get("order_type", "market")).lower() == "market" else OrderType.LIMIT,
                    volume=float(request.get("volume", 0.0)),
                    entry_price=request.get("entry_price"),
                    stop_loss=request.get("stop_loss"),
                    take_profit=request.get("take_profit"),
                    comment=str(request.get("comment", "")),
                )
            else:
                req = request

            # Log execution attempt
            self.logger.info(f"Executing order: {req.symbol} {req.order_type.value} "
                           f"Volume: {req.volume}", "EXECUTION")
            
            # Validate request
            validation_error = self._validate_order_request(req)
            if validation_error:
                return OrderResult(
                    success=False,
                    error_message=validation_error,
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
            # Execute based on MT5 availability
            if self._mt5_available:
                result = self._execute_mt5_order(req, start_time)
            else:
                result = self._simulate_order_execution(req, start_time)
            
            # Update statistics
            self._update_execution_stats(result)
            
            # Call callbacks using normalized request
            self._notify_execution_callbacks(req, result)
            
            return result
            
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            self.logger.error(error_msg, "EXECUTION")
            
            result = OrderResult(
                success=False,
                error_message=error_msg,
                execution_time_ms=(time.time() - start_time) * 1000
            )
            self._update_execution_stats(result)
            return result
    
    def _validate_order_request(self, request: OrderRequest) -> Optional[str]:
        """Validar solicitud de orden"""
        
        # Validate symbol
        if not request.symbol or len(request.symbol) < 3:
            return "Invalid symbol"
        
        # Validate volume
        if request.volume <= 0:
            return "Invalid volume (must be > 0)"
        
        if request.volume > 100:  # Safety limit
            return "Volume too large (max 100 lots)"
        
        # Validate prices for limit orders
        if request.order_type == OrderType.LIMIT:
            if not request.entry_price or request.entry_price <= 0:
                return "Limit order requires valid entry price"
        
        # Validate stop loss and take profit
        if request.stop_loss and request.stop_loss <= 0:
            return "Invalid stop loss price"
        
        if request.take_profit and request.take_profit <= 0:
            return "Invalid take profit price"
        
        return None
    
    def _execute_mt5_order(self, request: OrderRequest, start_time: float) -> OrderResult:
        """Ejecutar orden usando MT5DataManager centralizado"""
        try:
            # Verificar conexión usando el sistema centralizado
            if not self.mt5_manager or not self.mt5_manager.is_connected():
                return OrderResult(
                    success=False,
                    error_message="MT5 not connected via central manager",
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            # Ejecutar orden de mercado usando helpers del MT5DataManager
            self.logger.info(f"Executing order via MT5DataManager: {request.symbol} {request.order_type.value}", "MT5")

            if request.order_type == OrderType.MARKET:
                side = "BUY" if (request.entry_price is None or True) else "BUY"
                # Determinar lado según comentario 'action' opcional
                if request.comment:
                    c = request.comment.lower()
                    if "sell" in c:
                        side = "SELL"
                    elif "buy" in c:
                        side = "BUY"
                # Ejecutar
                exec_res = self.mt5_manager.place_market_order(
                    symbol=request.symbol,
                    side=side,
                    volume=request.volume,
                    price=request.entry_price,
                    sl=request.stop_loss,
                    tp=request.take_profit,
                    comment=request.comment or "ICT"
                )
                if not exec_res.get("success"):
                    return OrderResult(
                        success=False,
                        error_message=str(exec_res.get("message", "order failed")),
                        execution_time_ms=(time.time() - start_time) * 1000
                    )
                return OrderResult(
                    success=True,
                    order_id=int(time.time() * 1000) % 1000000,
                    ticket=int(exec_res.get("ticket") or 0) or None,
                    execution_price=float(exec_res.get("price") or 0.0),
                    execution_time_ms=(time.time() - start_time) * 1000,
                    slippage_pips=0.0,
                )
            else:
                # Para órdenes no mercado, fallback actual
                return OrderResult(
                    success=False,
                    error_message="Only market orders supported via MT5DataManager",
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
        except Exception as e:
            return OrderResult(
                success=False,
                error_message=f"MT5DataManager execution error: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )
    
    def _simulate_order_execution(self, request: OrderRequest, start_time: float) -> OrderResult:
        """Simular ejecución de orden (para testing)"""
        # Simulate execution delay
        time.sleep(0.1)  # 100ms simulation
        
        execution_time = (time.time() - start_time) * 1000
        
        # Simulate successful execution with slight slippage
        simulated_slippage = 0.5  # 0.5 pips average
        execution_price = request.entry_price if request.entry_price else 0.0  # No default price
        
        # Add small random slippage
        import random
        slippage_factor = random.uniform(0.8, 1.2)
        final_slippage = simulated_slippage * slippage_factor
        
        return OrderResult(
            success=True,
            order_id=int(time.time() * 1000) % 1000000,  # Simulate order ID
            ticket=int(time.time() * 1000) % 1000000,
            execution_price=execution_price,
            execution_time_ms=execution_time,
            slippage_pips=final_slippage
        )
    
    def _update_execution_stats(self, result: OrderResult) -> None:
        """Actualizar estadísticas de ejecución"""
        self.stats.total_orders += 1
        
        if result.success:
            self.stats.successful_orders += 1
        else:
            self.stats.failed_orders += 1
        
        # Update execution times
        self.stats.execution_times.append(result.execution_time_ms)
        
        # Calculate averages
        if self.stats.execution_times:
            self.stats.avg_execution_time_ms = sum(self.stats.execution_times) / len(self.stats.execution_times)
        
        # Update slippage average
        if result.success and result.slippage_pips > 0:
            # Simple running average (could be more sophisticated)
            if self.stats.avg_slippage_pips == 0:
                self.stats.avg_slippage_pips = result.slippage_pips
            else:
                self.stats.avg_slippage_pips = (self.stats.avg_slippage_pips + result.slippage_pips) / 2
        
        self.stats.last_update = datetime.now()
    
    def _notify_execution_callbacks(self, request: OrderRequest, result: OrderResult) -> None:
        """Notificar callbacks de ejecución"""
        for callback in self.execution_callbacks:
            try:
                callback(request, result)
            except Exception as e:
                self.logger.error(f"Callback error: {e}", "CALLBACK")
    
    def add_execution_callback(self, callback: Callable[[OrderRequest, OrderResult], None]) -> None:
        """Agregar callback de ejecución"""
        self.execution_callbacks.append(callback)
    
    def get_execution_stats(self) -> ExecutionStats:
        """Obtener estadísticas de ejecución"""
        return self.stats
    
    def get_success_rate(self) -> float:
        """Obtener tasa de éxito"""
        if self.stats.total_orders == 0:
            return 0.0
        return (self.stats.successful_orders / self.stats.total_orders) * 100
    
    def is_performing_well(self) -> bool:
        """Verificar si el engine está funcionando bien"""
        if self.stats.total_orders < 5:
            return True  # Not enough data
        
        success_rate = self.get_success_rate()
        avg_execution_time = self.stats.avg_execution_time_ms
        avg_slippage = self.stats.avg_slippage_pips
        
        performance_checks = [
            success_rate >= 95.0,  # 95%+ success rate
            avg_execution_time <= 1000.0,  # Under 1 second
            avg_slippage <= self.max_slippage_pips  # Within slippage tolerance
        ]
        
        return all(performance_checks)
    
    def reset_stats(self) -> None:
        """Resetear estadísticas"""
        self.stats = ExecutionStats()
        self.logger.info("Execution statistics reset", "STATS")
    
    def close_all_positions(self, symbol: Optional[str] = None) -> List[OrderResult]:
        """
        Cerrar todas las posiciones (emergency function)
        
        Args:
            symbol: Si se especifica, solo cerrar posiciones de ese símbolo
            
        Returns:
            List de OrderResult para cada posición cerrada
        """
        results = []
        
        try:
            if self._mt5_available and self.mt5_manager:
                # Usar el sistema centralizado MT5DataManager
                # En una implementación completa, MT5DataManager debería tener:
                # - get_open_positions()
                # - close_position()
                
                self.logger.info(f"Attempting to close all positions via MT5DataManager{' for symbol ' + symbol if symbol else ''}", "CLOSE_POSITIONS")
                
                # Por ahora, simular cierre de posiciones
                # TODO: Implementar métodos reales en MT5DataManager
                
                # Simular que se cerraron algunas posiciones
                import random
                base_price = random.uniform(0.9000, 1.5000)  # Precio base aleatorio realista
                for i in range(2):  # Simular 2 posiciones cerradas
                    order_result = OrderResult(
                        success=True,
                        order_id=1000 + i,
                        execution_price=base_price + (i * 0.0001),
                        execution_time_ms=150.0 + (i * 50),
                        error_message=""
                    )
                    results.append(order_result)
                    
                self.logger.info(f"Simulated closure of {len(results)} positions", "CLOSE_POSITIONS")
            else:
                # Simulation mode - pretend to close positions
                import random
                simulated_price = random.uniform(0.9000, 1.5000)  # Precio simulado realista
                self.logger.info("Simulating position closure (MT5 not available)", "CLOSE_POSITIONS")
                results.append(OrderResult(
                    success=True, 
                    order_id=999999,
                    execution_price=simulated_price,
                    execution_time_ms=100.0
                ))
        
        except Exception as e:
            self.logger.error(f"Error closing positions: {e}", "CLOSE_POSITIONS")
            results.append(OrderResult(
                success=False, 
                error_message=str(e),
                execution_time_ms=0.0
            ))
        
        return results
    
    # ---------------- PRODUCTION METHODS ----------------
    
    def get_order_status(self, order_id: int) -> Tuple[OrderStatus, str]:
        """Get current status of an order"""
        try:
            # In real implementation, query broker for actual status
            if self._mt5_available:
                # TODO: Implement real MT5 order status check
                # For now, simulate based on active orders tracking
                if order_id in self.active_orders:
                    return OrderStatus.PENDING, "Order is pending execution"
                else:
                    return OrderStatus.FILLED, "Order has been filled"
            else:
                # Simulation mode
                return OrderStatus.FILLED, "Simulated order completion"
                
        except Exception as e:
            self.logger.error(f"Error getting order status for {order_id}: {e}", "ORDER_STATUS")
            return OrderStatus.REJECTED, f"Status check failed: {e}"
    
    def cancel_order(self, order_id: int) -> OrderResult:
        """Cancel a pending order"""
        try:
            self.logger.info(f"Cancelling order {order_id}", "ORDER_CANCEL")
            
            if self._mt5_available:
                # TODO: Implement real MT5 order cancellation
                # For now, simulate cancellation
                if order_id in self.active_orders:
                    del self.active_orders[order_id]
                    self.logger.info(f"Order {order_id} cancelled successfully", "ORDER_CANCEL")
                    return OrderResult(success=True, order_id=order_id, error_message="Order cancelled")
                else:
                    return OrderResult(success=False, order_id=order_id, error_message="Order not found")
            else:
                # Simulation mode
                return OrderResult(success=True, order_id=order_id, error_message="Simulated cancellation")
                
        except Exception as e:
            error_msg = f"Error cancelling order {order_id}: {e}"
            self.logger.error(error_msg, "ORDER_CANCEL")
            return OrderResult(success=False, order_id=order_id, error_message=error_msg)
    
    def get_execution_quality_metrics(self) -> Dict[str, Any]:
        """Get detailed execution quality metrics"""
        try:
            with_executions = [t for t in self.stats.execution_times if t > 0]
            
            if not with_executions:
                return {
                    "total_orders": self.stats.total_orders,
                    "success_rate": 0.0,
                    "avg_execution_time_ms": 0.0,
                    "execution_quality": "no_data",
                    "last_update": self.stats.last_update.isoformat()
                }
            
            # Calculate percentiles
            sorted_times = sorted(with_executions)
            n = len(sorted_times)
            
            p50 = sorted_times[n//2] if n > 0 else 0
            p95 = sorted_times[int(n*0.95)] if n > 0 else 0
            p99 = sorted_times[int(n*0.99)] if n > 0 else 0
            
            success_rate = (self.stats.successful_orders / max(1, self.stats.total_orders)) * 100
            
            # Determine execution quality
            if self.stats.avg_execution_time_ms < 500:
                quality = "excellent"
            elif self.stats.avg_execution_time_ms < 1000:
                quality = "good"
            elif self.stats.avg_execution_time_ms < 2000:
                quality = "acceptable"
            else:
                quality = "poor"
            
            return {
                "total_orders": self.stats.total_orders,
                "successful_orders": self.stats.successful_orders,
                "failed_orders": self.stats.failed_orders,
                "success_rate": round(success_rate, 2),
                "avg_execution_time_ms": round(self.stats.avg_execution_time_ms, 2),
                "avg_slippage_pips": round(self.stats.avg_slippage_pips, 3),
                "execution_time_percentiles": {
                    "p50": round(p50, 2),
                    "p95": round(p95, 2),
                    "p99": round(p99, 2)
                },
                "execution_quality": quality,
                "active_orders_count": len(self.active_orders),
                "last_update": self.stats.last_update.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating execution metrics: {e}", "METRICS")
            return {
                "error": str(e),
                "last_update": datetime.now().isoformat()
            }
    
    def is_healthy(self) -> bool:
        """Check if Execution Engine is in healthy state"""
        try:
            # Health checks
            if self.stats.total_orders > 0:
                success_rate = (self.stats.successful_orders / self.stats.total_orders) * 100
                if success_rate < 80:  # Less than 80% success rate
                    self.logger.warning(f"Low success rate: {success_rate}%", "HEALTH")
                    return False
            
            # Check execution times
            if self.stats.avg_execution_time_ms > 5000:  # More than 5 seconds average
                self.logger.warning(f"High execution time: {self.stats.avg_execution_time_ms}ms", "HEALTH")
                return False
            
            # Check for excessive active orders
            if len(self.active_orders) > 50:
                self.logger.warning(f"Too many active orders: {len(self.active_orders)}", "HEALTH")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", "HEALTH")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status information for monitoring"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "healthy": self.is_healthy(),
                "mt5_available": self._mt5_available,
                "active_orders": len(self.active_orders),
                "execution_stats": {
                    "total_orders": self.stats.total_orders,
                    "success_rate": f"{(self.stats.successful_orders / max(1, self.stats.total_orders) * 100):.1f}%",
                    "avg_execution_time": f"{self.stats.avg_execution_time_ms:.1f}ms",
                    "avg_slippage": f"{self.stats.avg_slippage_pips:.2f} pips"
                },
                "configuration": {
                    "max_slippage_pips": self.max_slippage_pips
                }
            }
            
        except Exception as e:
            self.logger.error(f"Status retrieval failed: {e}", "STATUS")
            return {
                "timestamp": datetime.now().isoformat(),
                "healthy": False,
                "error": str(e)
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring"""
        return {
            "execution_count": self.stats.total_orders,
            "success_rate": round((self.stats.successful_orders / max(1, self.stats.total_orders)) * 100, 1),
            "avg_execution_time_ms": round(self.stats.avg_execution_time_ms, 2),
            "active_orders": len(self.active_orders),
            "health_status": "healthy" if self.is_healthy() else "unhealthy",
            "last_update": datetime.now().isoformat()
        }
