"""
MT5 Connection Manager v6.0 Enterprise
Gestor de conexiones robustas a MetaTrader5 con FTMO Global Markets

Dependencias:
- mt5_data_manager (archivo dedicado a MT5)
- smart_trading_logger
"""

import time
import threading
import logging
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from mt5_data_manager import MT5DataManager
from pathlib import Path

# Fix imports with absolute path resolution
def _resolve_imports():
    """Resolver imports con path absoluto para evitar errores relativos"""
    current_dir = Path(__file__).parent
    core_dir = current_dir.parent
    project_root = core_dir.parent
    
    # Agregar paths al sys.path si no están
    paths_to_add = [str(project_root), str(core_dir), str(current_dir)]
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)

# Resolver imports antes de cualquier import relativo
_resolve_imports()

# Ahora usar imports absolutos
try:
    from mt5_data_manager import get_mt5_manager, _lazy_import_mt5  # type: ignore
    MT5_MANAGER_AVAILABLE = True
except ImportError:
    # Fallback para imports relativos
    try:
        from .mt5_data_manager import get_mt5_manager, _lazy_import_mt5  # type: ignore
        MT5_MANAGER_AVAILABLE = True
    except ImportError:
        # Fallback absoluto con path manual
        MT5_MANAGER_AVAILABLE = False
        try:
            import importlib.util
            current_dir = Path(__file__).parent
            mt5_manager_path = current_dir / "mt5_data_manager.py"
            
            if mt5_manager_path.exists():
                spec = importlib.util.spec_from_file_location("mt5_data_manager", mt5_manager_path)
                if spec and spec.loader:
                    mt5_data_manager_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mt5_data_manager_module)
                    get_mt5_manager = mt5_data_manager_module.get_mt5_manager  # type: ignore
                    _lazy_import_mt5 = mt5_data_manager_module._lazy_import_mt5  # type: ignore
                    MT5_MANAGER_AVAILABLE = True
                else:
                    raise ImportError("Could not create module spec")
            else:
                raise ImportError("mt5_data_manager.py not found")
        except Exception:
            # Último fallback - definir funciones dummy con tipos correctos
            def get_mt5_manager() -> Optional['MT5DataManager']:  # type: ignore
                return None
            def _lazy_import_mt5() -> bool:  # type: ignore
                return False
            MT5_MANAGER_AVAILABLE = False

# Verificar disponibilidad de MT5 a través del manager dedicado
MT5_AVAILABLE = _lazy_import_mt5()

# Import directo de MT5 para trading (cuando esté disponible)
if MT5_AVAILABLE:
    try:
        import MetaTrader5 as mt5
    except ImportError:
        MT5_AVAILABLE = False
        mt5 = None
else:
    mt5 = None

# Constantes MT5 seguras para evitar errores Pylance
class MT5Constants:
    """Constantes MT5 con valores reales para fallback cuando MT5 no está disponible"""
    # Trading Actions
    TRADE_ACTION_DEAL = 1
    TRADE_ACTION_SLTP = 2
    
    # Order Types  
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1
    ORDER_TYPE_BUY_LIMIT = 2
    ORDER_TYPE_SELL_LIMIT = 3
    
    # Time Types
    ORDER_TIME_GTC = 0
    
    # Filling Types
    ORDER_FILLING_IOC = 1
    
    # Return Codes
    TRADE_RETCODE_DONE = 10009

def get_mt5_constants():
    """Obtener constantes MT5 de forma segura"""
    if MT5_AVAILABLE and mt5:
        return mt5
    return MT5Constants()

class MT5Wrapper:
    """
    🛡️ Wrapper seguro para métodos de MT5 con fallback
    """
    
    def __init__(self):
        self._mt5_available = MT5_AVAILABLE and mt5 is not None
        self._mt5 = mt5 if self._mt5_available else None
    
    def order_send(self, request: dict) -> Any:
        """Enviar orden con fallback seguro"""
        if not self._mt5_available or not self._mt5:
            return None
        try:
            # Usar getattr para evitar errores de Pylance
            order_send_func = getattr(self._mt5, 'order_send', None)
            if order_send_func:
                return order_send_func(request)
            return None
        except Exception:
            return None
    
    def positions_get(self, ticket: Optional[int] = None, symbol: Optional[str] = None) -> Any:
        """Obtener posiciones con fallback seguro"""
        if not self._mt5_available or not self._mt5:
            return None
        try:
            positions_get_func = getattr(self._mt5, 'positions_get', None)
            if not positions_get_func:
                return None
            
            if ticket:
                return positions_get_func(ticket=ticket)
            elif symbol:
                return positions_get_func(symbol=symbol)
            else:
                return positions_get_func()
        except Exception:
            return None
    
    def orders_get(self, ticket: Optional[int] = None, symbol: Optional[str] = None) -> Any:
        """Obtener órdenes con fallback seguro"""
        if not self._mt5_available or not self._mt5:
            return None
        try:
            orders_get_func = getattr(self._mt5, 'orders_get', None)
            if not orders_get_func:
                return None
                
            if ticket:
                return orders_get_func(ticket=ticket)
            elif symbol:
                return orders_get_func(symbol=symbol)
            else:
                return orders_get_func()
        except Exception:
            return None
    
    def last_error(self) -> int:
        """Obtener último error con fallback seguro"""
        if not self._mt5_available or not self._mt5:
            return -1
        try:
            last_error_func = getattr(self._mt5, 'last_error', None)
            if last_error_func:
                return last_error_func()
            return -1
        except Exception:
            return -1

# Obtener constantes para uso en el código
mt5_const = get_mt5_constants()
mt5_wrapper = MT5Wrapper()

# Import logging system
try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from smart_trading_logger import get_smart_logger
    logger = get_smart_logger("MT5Manager")
except ImportError:
    logger = logging.getLogger(__name__)

class MT5ConnectionManager:
    """
    Gestor de conexiones MT5 enterprise con reconexión automática
    y validación de cuenta FTMO Global Markets
    """
    
    def __init__(self):
        """Inicializar el gestor de conexiones MT5"""
        self.logger = logger
        self.is_connected = False
        self.connection_attempts = 0
        self.max_attempts = 3
        self.reconnect_delay = 5
        self.account_info = None
        self._lock = threading.Lock()
        
        # Usar el manager dedicado para conexiones básicas (con validación de None)
        if MT5_MANAGER_AVAILABLE:
            self.mt5_data_manager = get_mt5_manager()
        else:
            self.mt5_data_manager = None
            self.logger.warning("⚠️ MT5DataManager no disponible - funcionalidad limitada")
        
    def _ensure_mt5_available(self) -> bool:
        """Verificar que MT5 esté disponible para trading"""
        if not MT5_AVAILABLE or not mt5:
            self.logger.error("❌ MT5 no está disponible para operaciones de trading")
            return False
        return True
        
    def _ensure_mt5_manager_available(self) -> bool:
        """Verificar que MT5DataManager esté disponible"""
        if not self.mt5_data_manager:
            self.logger.error("❌ MT5DataManager no está disponible")
            return False
        return True
        
    def connect(self, path: Optional[str] = None, login: Optional[int] = None, 
                password: Optional[str] = None, server: Optional[str] = None) -> bool:
        """
        Establecer conexión con MetaTrader5 usando el manager dedicado
        
        Args:
            path: Ruta al terminal MT5
            login: Número de cuenta
            password: Contraseña
            server: Servidor
            
        Returns:
            bool: True si la conexión es exitosa
        """
        with self._lock:
            try:
                # Verificar que el manager esté disponible
                if not self._ensure_mt5_manager_available():
                    self.logger.error("❌ MT5DataManager no disponible para conexión")
                    return False
                
                # Type assertion para TypeChecker - ya validamos que no es None
                assert self.mt5_data_manager is not None
                
                # Usar el manager dedicado para la conexión
                if self.mt5_data_manager.connect():
                    self.is_connected = True
                    self.connection_attempts = 0
                    
                    # Obtener información de cuenta del manager
                    connection_info = self.mt5_data_manager.connection_info
                    self.account_info = connection_info
                    
                    # Validar que es una cuenta FTMO Global Markets
                    if self._validate_ftmo_account():
                        self.logger.info(f"✅ Conectado a FTMO Global Markets - Cuenta: {connection_info.account}")
                        return True
                    else:
                        self.logger.warning("⚠️ Cuenta no validada como FTMO Global Markets")
                        return False
                else:
                    self.logger.error("❌ Error de conexión MT5 a través del data manager")
                    return False
                    
            except Exception as e:
                self.logger.error(f"❌ Excepción en conexión MT5: {e}")
                return False
    
    def _validate_ftmo_account(self) -> bool:
        """
        Validar que la cuenta conectada es de FTMO Global Markets
        
        Returns:
            bool: True si es cuenta FTMO Global Markets válida
        """
        if not self.account_info:
            return False
            
        # Validaciones específicas de FTMO Global Markets usando MT5ConnectionInfo
        server_name = self.account_info.server.lower() if self.account_info.server else ""
        company_name = self.account_info.company.lower() if self.account_info.company else ""
        
        ftmo_indicators = [
            "ftmo" in server_name,
            "ftmo" in company_name,
            "fn-" in server_name,
            "funded" in server_name
        ]
        
        is_valid = any(ftmo_indicators)
        
        if is_valid:
            self.logger.info(f"✅ Cuenta FTMO Global Markets validada: {self.account_info.server}")
        else:
            self.logger.warning(f"⚠️ Cuenta no identificada como FTMO Global Markets: {self.account_info.server}")
            
        return is_valid
    
    def disconnect(self) -> None:
        """Cerrar conexión MT5 usando el manager dedicado"""
        with self._lock:
            try:
                if self._ensure_mt5_manager_available():
                    assert self.mt5_data_manager is not None
                    self.mt5_data_manager.disconnect()
                    
                self.is_connected = False
                self.account_info = None
                self.logger.info("🔌 Desconectado de MT5")
            except Exception as e:
                self.logger.error(f"❌ Error al desconectar: {e}")
    
    def reconnect(self) -> bool:
        """
        Intentar reconexión automática
        
        Returns:
            bool: True si la reconexión es exitosa
        """
        self.logger.info("🔄 Intentando reconexión...")
        self.disconnect()
        time.sleep(self.reconnect_delay)
        return self.connect()
    
    def ensure_connection(self) -> bool:
        """
        Asegurar que hay conexión activa, reconectar si es necesario
        
        Returns:
            bool: True si hay conexión activa
        """
        if not self.is_connected:
            return self.reconnect()
            
        # Verificar si la conexión sigue activa usando el manager
        try:
            if self._ensure_mt5_manager_available():
                assert self.mt5_data_manager is not None
                if self.mt5_data_manager.is_connected():
                    return True
                else:
                    self.is_connected = False
                    return self.reconnect()
            else:
                self.is_connected = False
                return self.reconnect()
        except Exception as e:
            self.logger.error(f"❌ Error verificando conexión: {e}")
            self.is_connected = False
            return self.reconnect()
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Obtener información de la cuenta usando el manager dedicado
        
        Returns:
            dict: Información de la cuenta o None
        """
        if not self.ensure_connection():
            return None
            
        try:
            if not self._ensure_mt5_manager_available():
                return None
                
            assert self.mt5_data_manager is not None
            connection_info = self.mt5_data_manager.connection_info
            if connection_info and connection_info.connected:
                return {
                    'login': connection_info.account,
                    'server': connection_info.server,
                    'company': connection_info.company,
                    'balance': connection_info.balance,
                    'equity': connection_info.equity,
                    'currency': 'USD',  # Default, puede ser configurado
                    'leverage': 100,    # Default, puede ser configurado
                    'margin': connection_info.margin,
                    'margin_free': connection_info.free_margin,
                    'margin_level': connection_info.margin_level,
                    'name': f"Account_{connection_info.account}"
                }
            return None
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo info de cuenta: {e}")
            return None
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Obtener estado de la conexión
        
        Returns:
            dict: Estado de la conexión
        """
        return {
            'connected': self.is_connected,
            'attempts': self.connection_attempts,
            'account_login': self.account_info.account if self.account_info else None,
            'server': self.account_info.server if self.account_info else None,
            'last_check': datetime.now().isoformat()
        }
    
    # ================== MÉTODOS DE TRADING REAL ==================
    
    def place_buy_order(self, symbol: str, volume: float, price: Optional[float] = None, 
                       sl: Optional[float] = None, tp: Optional[float] = None, comment: str = "ICT_BUY") -> Dict[str, Any]:
        """
        🚀 MÉTODO CRÍTICO: Colocar orden de compra real en MT5
        
        Args:
            symbol: Símbolo a operar (ej: EURUSD)
            volume: Volumen en lotes (ej: 0.01)
            price: Precio de entrada (None para market order)
            sl: Stop Loss
            tp: Take Profit  
            comment: Comentario de la orden
            
        Returns:
            Dict con resultado: {'success': bool, 'ticket': int, 'message': str, 'price': float, 'error_code': int}
        """
        try:
            if not self.ensure_connection():
                return {
                    'success': False,
                    'ticket': None,
                    'message': 'No hay conexión con MT5',
                    'price': None,
                    'error_code': -1
                }
            
            if not self._ensure_mt5_available():
                return {
                    'success': False,
                    'ticket': None,
                    'message': 'MT5 no disponible para trading',
                    'price': None,
                    'error_code': -1
                }
            
            # Preparar request de orden BUY real
            request = {
                "action": mt5_const.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5_const.ORDER_TYPE_BUY,
                "deviation": 20,
                "magic": 12345,  # ICT Engine magic number
                "comment": comment,
                "type_time": mt5_const.ORDER_TIME_GTC,
                "type_filling": mt5_const.ORDER_FILLING_IOC,
            }
            
            # Agregar precio si es orden limitada
            if price is not None:
                request["price"] = price
                request["type"] = mt5_const.ORDER_TYPE_BUY_LIMIT
            
            # Agregar SL y TP si están especificados
            if sl is not None:
                request["sl"] = sl
            if tp is not None:
                request["tp"] = tp
            
            # Enviar orden real a MT5
            result = mt5_wrapper.order_send(request)
            
            if result is None:
                return {
                    'success': False,
                    'ticket': None,
                    'message': 'MT5 order_send retornó None',
                    'price': None,
                    'error_code': -2
                }
            
            # Verificar resultado de MT5 - BUY ORDER
            if result.retcode != mt5_const.TRADE_RETCODE_DONE:
                return {
                    'success': False,
                    'ticket': result.order,
                    'message': result.comment,
                    'price': result.price,
                    'error_code': result.retcode
                }
            
            # Orden exitosa en MT5 real
            self.logger.info(f"✅ BUY order executed: {symbol} {volume} lots at {result.price}")
            return {
                'success': True,
                'ticket': result.order,
                'message': f'BUY order executed successfully',
                'price': result.price,
                'error_code': 0
            }
            
        except Exception as e:
            error_msg = f"Error placing BUY order: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'ticket': None,
                'message': error_msg,
                'price': None,
                'error_code': -3
            }
    
    def place_sell_order(self, symbol: str, volume: float, price: Optional[float] = None,
                        sl: Optional[float] = None, tp: Optional[float] = None, comment: str = "ICT_SELL") -> Dict[str, Any]:
        """
        🚀 MÉTODO CRÍTICO: Colocar orden de venta real en MT5
        
        Args:
            symbol: Símbolo a operar (ej: EURUSD)
            volume: Volumen en lotes (ej: 0.01)
            price: Precio de entrada (None para market order)
            sl: Stop Loss
            tp: Take Profit
            comment: Comentario de la orden
            
        Returns:
            Dict con resultado: {'success': bool, 'ticket': int, 'message': str, 'price': float, 'error_code': int}
        """
        try:
            if not self.ensure_connection():
                return {
                    'success': False,
                    'ticket': None,
                    'message': 'No hay conexión con MT5',
                    'price': None,
                    'error_code': -1
                }
            
            # Preparar request de orden SELL real
            request = {
                "action": mt5_const.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5_const.ORDER_TYPE_SELL,
                "deviation": 20,
                "magic": 12345,  # ICT Engine magic number
                "comment": comment,
                "type_time": mt5_const.ORDER_TIME_GTC,
                "type_filling": mt5_const.ORDER_FILLING_IOC,
            }
            
            # Agregar precio si es orden limitada
            if price is not None:
                request["price"] = price
                request["type"] = mt5_const.ORDER_TYPE_SELL_LIMIT
            
            # Agregar SL y TP si están especificados
            if sl is not None:
                request["sl"] = sl
            if tp is not None:
                request["tp"] = tp
            
            # Enviar orden real a MT5
            result = mt5_wrapper.order_send(request)
            
            if result is None:
                return {
                    'success': False,
                    'ticket': None,
                    'message': 'MT5 order_send retornó None',
                    'price': None,
                    'error_code': -2
                }
            
            # Verificar resultado de MT5 - SELL ORDER
            if result.retcode != mt5_const.TRADE_RETCODE_DONE:
                return {
                    'success': False,
                    'ticket': result.order,
                    'message': result.comment,
                    'price': result.price,
                    'error_code': result.retcode
                }
            
            # Orden exitosa en MT5 real
            self.logger.info(f"✅ SELL order executed: {symbol} {volume} lots at {result.price}")
            return {
                'success': True,
                'ticket': result.order,
                'message': f'SELL order executed successfully',
                'price': result.price,
                'error_code': 0
            }
            
        except Exception as e:
            error_msg = f"Error placing SELL order: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'ticket': None,
                'message': error_msg,
                'price': None,
                'error_code': -3
            }
    
    def close_position(self, ticket: int, volume: Optional[float] = None) -> Dict[str, Any]:
        """
        🚀 MÉTODO CRÍTICO: Cerrar posición específica por ticket
        
        Args:
            ticket: Ticket de la posición a cerrar
            volume: Volumen a cerrar (None para cerrar completamente)
            
        Returns:
            Dict con resultado: {'success': bool, 'ticket': int, 'message': str, 'price': float, 'error_code': int}
        """
        try:
            if not self.ensure_connection():
                return {
                    'success': False,
                    'ticket': None,
                    'message': 'No hay conexión con MT5',
                    'price': None,
                    'error_code': -1
                }
            
            # Obtener información de la posición real
            positions = mt5_wrapper.positions_get(ticket=ticket)
            if not positions or len(positions) == 0:
                return {
                    'success': False,
                    'ticket': ticket,
                    'message': f'Posición {ticket} no encontrada',
                    'price': None,
                    'error_code': -2
                }
            
            position = positions[0]
            
            # Determinar tipo de orden de cierre real
            close_type = mt5_const.ORDER_TYPE_SELL if position.type == mt5_const.ORDER_TYPE_BUY else mt5_const.ORDER_TYPE_BUY
            
            # Volumen a cerrar (completo si no se especifica)
            close_volume = volume if volume is not None else position.volume
            
            # Preparar request de cierre real
            request = {
                "action": mt5_const.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": close_volume,
                "type": close_type,
                "position": ticket,
                "deviation": 20,
                "magic": 12345,
                "comment": f"Close_{ticket}",
                "type_time": mt5_const.ORDER_TIME_GTC,
                "type_filling": mt5_const.ORDER_FILLING_IOC,
            }
            
            # Enviar orden de cierre real a MT5
            result = mt5_wrapper.order_send(request)
            
            if result is None:
                return {
                    'success': False,
                    'ticket': ticket,
                    'message': 'MT5 order_send para cierre retornó None',
                    'price': None,
                    'error_code': -3
                }
            
            # Verificar resultado real de MT5 - CLOSE POSITION
            if result.retcode != mt5_const.TRADE_RETCODE_DONE:
                return {
                    'success': False,
                    'ticket': ticket,
                    'message': result.comment,
                    'price': result.price,
                    'error_code': result.retcode
                }
            
            # Cierre exitoso en MT5 real
            self.logger.info(f"✅ Position {ticket} closed at {result.price}")
            return {
                'success': True,
                'ticket': result.order,
                'message': f'Position {ticket} closed successfully',
                'price': result.price,
                'error_code': 0
            }
            
        except Exception as e:
            error_msg = f"Error closing position {ticket}: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'ticket': ticket,
                'message': error_msg,
                'price': None,
                'error_code': -4
            }
    
    def modify_position(self, ticket: int, sl: Optional[float] = None, tp: Optional[float] = None) -> Dict[str, Any]:
        """
        🚀 MÉTODO CRÍTICO: Modificar SL/TP de posición existente
        
        Args:
            ticket: Ticket de la posición a modificar
            sl: Nuevo Stop Loss (None para mantener actual)
            tp: Nuevo Take Profit (None para mantener actual)
            
        Returns:
            Dict con resultado: {'success': bool, 'ticket': int, 'message': str, 'error_code': int}
        """
        try:
            if not self.ensure_connection():
                return {
                    'success': False,
                    'ticket': ticket,
                    'message': 'No hay conexión con MT5',
                    'error_code': -1
                }
            
            # Obtener información de la posición real
            positions = mt5_wrapper.positions_get(ticket=ticket)
            if not positions or len(positions) == 0:
                return {
                    'success': False,
                    'ticket': ticket,
                    'message': f'Posición {ticket} no encontrada',
                    'error_code': -2
                }
            
            position = positions[0]
            
            # Usar valores actuales si no se especifican nuevos
            current_sl = position.sl
            current_tp = position.tp
            new_sl = sl if sl is not None else current_sl
            new_tp = tp if tp is not None else current_tp
            
            # Preparar request de modificación real
            request = {
                "action": mt5_const.TRADE_ACTION_SLTP,
                "symbol": position.symbol,
                "position": ticket,
                "sl": new_sl,
                "tp": new_tp,
            }
            
            # Enviar modificación real a MT5
            result = mt5_wrapper.order_send(request)
            
            if result is None:
                return {
                    'success': False,
                    'ticket': ticket,
                    'message': 'MT5 order_send para modificación retornó None',
                    'error_code': -3
                }
            
            # Verificar resultado real de MT5 - CLOSE ALL
            if result.retcode != mt5_const.TRADE_RETCODE_DONE:
                return {
                    'success': False,
                    'ticket': ticket,
                    'message': result.comment,
                    'error_code': result.retcode
                }
            
            # Modificación exitosa en MT5 real
            self.logger.info(f"✅ Position {ticket} modified - SL: {new_sl}, TP: {new_tp}")
            return {
                'success': True,
                'ticket': ticket,
                'message': f'Position {ticket} modified successfully',
                'error_code': 0
            }
            
        except Exception as e:
            error_msg = f"Error modifying position {ticket}: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'ticket': ticket,
                'message': error_msg,
                'error_code': -4
            }
    
    def get_open_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        🚀 MÉTODO CRÍTICO: Obtener todas las posiciones abiertas
        
        Args:
            symbol: Filtrar por símbolo específico (None para todas)
            
        Returns:
            Lista de posiciones con datos completos
        """
        try:
            if not self.ensure_connection():
                self.logger.error("No hay conexión con MT5 para obtener posiciones")
                return []
            
            # Obtener posiciones reales de MT5
            if symbol:
                positions = mt5_wrapper.positions_get(symbol=symbol)
            else:
                positions = mt5_wrapper.positions_get()
            
            if positions is None:
                return []
            
            # Convertir a lista de diccionarios con datos reales
            position_list = []
            for pos in positions:
                position_data = {
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'buy' if pos.type == mt5_const.ORDER_TYPE_BUY else 'sell',
                    'volume': pos.volume,
                    'open_price': pos.price_open,
                    'current_price': pos.price_current,
                    'stop_loss': pos.sl,
                    'take_profit': pos.tp,
                    'profit': pos.profit,
                    'swap': pos.swap,
                    'commission': pos.commission,
                    'comment': pos.comment,
                    'magic': pos.magic,
                    'open_time': datetime.fromtimestamp(pos.time) if pos.time > 0 else datetime.now()
                }
                position_list.append(position_data)
            
            self.logger.info(f"✅ Retrieved {len(position_list)} real open positions")
            return position_list
            
        except Exception as e:
            error_msg = f"Error getting open positions: {str(e)}"
            self.logger.error(error_msg)
            return []
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        🚀 MÉTODO CRÍTICO: Alias para get_open_positions (compatibilidad)
        
        Args:
            symbol: Filtrar por símbolo específico (None para todas)
            
        Returns:
            Lista de posiciones con datos completos
        """
        return self.get_open_positions(symbol)

# Instancia singleton
_connection_manager = None

def get_mt5_connection() -> MT5ConnectionManager:
    """Obtener instancia singleton del gestor de conexiones"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = MT5ConnectionManager()
    return _connection_manager
