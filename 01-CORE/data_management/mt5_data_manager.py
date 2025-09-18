#!/usr/bin/env python3
"""
📡 MT5 DATA MANAGER v6.0 ENTERPRISE - ICT ENGINE (OPTIMIZED)
===========================================================

Gestor centralizado para MetaTrader 5 con máxima eficiencia y limpieza.
Solo incluye funcionalidades esenciales y en uso.

Características:
- Conexión robusta a MT5
- Descarga de datos históricos
- Manejo de errores optimizado
- Interfaz simple y eficiente

Autor: ICT Engine v6.1.0 Enterprise Team
Versión: v6.1.0-enterprise-clean
"""

from protocols.unified_logging import get_unified_logger
import sys
import os
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

# Lazy import de MT5
MT5_AVAILABLE = False
mt5: Any = None

def _lazy_import_mt5() -> bool:
    """Importa MT5 de forma lazy y segura"""
    global mt5, MT5_AVAILABLE
    if not MT5_AVAILABLE:
        try:
            import MetaTrader5 as mt5_module
            mt5 = mt5_module
            MT5_AVAILABLE = True
            return True
        except ImportError:
            print("⚠️ MetaTrader 5 no disponible - funcionando en modo fallback")
            return False
    return MT5_AVAILABLE

# Lazy import de pandas
pd: Any = None

def _lazy_import_pandas() -> bool:
    """Importa pandas de forma lazy y segura"""
    global pd
    if pd is None:
        try:
            import pandas as pandas_module
            pd = pandas_module
            return True
        except ImportError:
            print("⚠️ pandas no disponible")
            return False
    return pd is not None

# ===============================
# CONFIGURACIÓN DE CUENTA FTMO
# ===============================

# 🏦 CONFIGURACIÓN CUENTA FTMO DEMO
FTMO_ACCOUNT_CONFIG = {
    'login': 1511525932,
    'password': '6U*ss5@D2RLa',
    'server': 'FTMO-Demo',
    'path': r"C:\Program Files\FTMO Global Markets MT5 Terminal\terminal64.exe",
    'timeout': 60000,  # 60 segundos
    'portable': False
}

# Configuración por defecto
DEFAULT_MT5_CONFIG = FTMO_ACCOUNT_CONFIG.copy()

# ===============================
# TIPOS DE DATOS ESENCIALES
# ===============================

class AccountType(Enum):
    DEMO = "demo"
    REAL = "real"
    CONTEST = "contest"

@dataclass
class MT5ConnectionInfo:
    """Información básica de conexión MT5"""
    connected: bool = False
    account: Optional[int] = None
    server: Optional[str] = None
    company: Optional[str] = None
    account_type: Optional[AccountType] = None
    balance: Optional[float] = None
    equity: Optional[float] = None
    margin: Optional[float] = None
    free_margin: Optional[float] = None
    margin_level: Optional[float] = None
    last_connection: Optional[datetime] = None

# ===============================
# GESTOR MT5 OPTIMIZADO
# ===============================

class MT5DataManager:
    """
    Gestor optimizado de datos MT5 - Solo funcionalidades esenciales
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Inicializa el gestor de datos MT5"""
        self.connection_info = MT5ConnectionInfo()
        self._last_error = None
        self._connection_attempts = 0
        self._max_connection_attempts = 3
        self.config = config or {}
        
    def _log_info(self, message: str):
        """Log simple para información"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ℹ️ MT5: {message}")
        
    def _log_error(self, message: str, error: Optional[Exception] = None):
        """Log simple para errores"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        error_detail = f" - {str(error)}" if error else ""
        print(f"[{timestamp}] ❌ MT5 ERROR: {message}{error_detail}")
        self._last_error = message
        
    def _log_warning(self, message: str):
        """Log simple para advertencias"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] ⚠️ MT5 WARNING: {message}")

    def initialize(self) -> bool:
        """
        Inicializa y conecta a MetaTrader 5
        
        Returns:
            bool: True si la conexión fue exitosa
        """
        return self.connect()
    
    def connect(self, login: Optional[int] = None, password: Optional[str] = None, server: Optional[str] = None) -> bool:
        """
        Conecta a MetaTrader 5 de forma robusta usando configuración FTMO
        
        Args:
            login: Login de cuenta (por defecto usa FTMO_ACCOUNT_CONFIG)
            password: Contraseña (por defecto usa FTMO_ACCOUNT_CONFIG)
            server: Servidor (por defecto usa FTMO_ACCOUNT_CONFIG)
        """
        if not _lazy_import_mt5() or mt5 is None:
            self._log_error("MT5 no está disponible")
            return False
            
        self._connection_attempts += 1
        
        # Usar configuración FTMO por defecto
        account_login = login or FTMO_ACCOUNT_CONFIG['login']
        account_password = password or FTMO_ACCOUNT_CONFIG['password']
        account_server = server or FTMO_ACCOUNT_CONFIG['server']
        
        try:
            # Intentar conexión con credenciales específicas y ruta del terminal
            terminal_path = FTMO_ACCOUNT_CONFIG.get('path')
            
            if terminal_path:
                authorized = mt5.initialize(  # type: ignore
                    path=terminal_path,
                    login=account_login,
                    password=account_password,
                    server=account_server,
                    timeout=FTMO_ACCOUNT_CONFIG.get('timeout', 60000),
                    portable=FTMO_ACCOUNT_CONFIG.get('portable', False)
                )
            else:
                authorized = mt5.initialize(  # type: ignore
                    login=account_login,
                    password=account_password,
                    server=account_server,
                    timeout=FTMO_ACCOUNT_CONFIG.get('timeout', 60000),
                    portable=FTMO_ACCOUNT_CONFIG.get('portable', False)
                )
            
            if not authorized:
                error_code = mt5.last_error()  # type: ignore
                self._log_error(f"Fallo al inicializar MT5 con cuenta FTMO {account_login}. Error: {error_code}")
                return False
                
            # Verificar conexión
            account_info = mt5.account_info()  # type: ignore
            if account_info is None:
                self._log_error("No se pudo obtener información de la cuenta FTMO")
                mt5.shutdown()  # type: ignore
                return False
                
            # Verificar que es la cuenta correcta
            if account_info.login != account_login:
                self._log_error(f"Cuenta incorrecta: esperada {account_login}, obtenida {account_info.login}")
                mt5.shutdown()  # type: ignore
                return False
                
            # Actualizar información de conexión
            self.connection_info.connected = True
            self.connection_info.account = account_info.login
            self.connection_info.server = account_info.server
            self.connection_info.company = account_info.company
            self.connection_info.balance = account_info.balance
            self.connection_info.equity = account_info.equity
            self.connection_info.margin = account_info.margin
            self.connection_info.free_margin = account_info.margin_free
            self.connection_info.margin_level = account_info.margin_level
            self.connection_info.last_connection = datetime.now()
            
            # Determinar tipo de cuenta
            if "demo" in account_info.server.lower():
                self.connection_info.account_type = AccountType.DEMO
            elif "contest" in account_info.server.lower():
                self.connection_info.account_type = AccountType.CONTEST
            else:
                self.connection_info.account_type = AccountType.REAL
                
            self._log_info(f"✅ Conectado exitosamente a FTMO - Cuenta: {account_info.login} | Servidor: {account_info.server} | Balance: ${account_info.balance:.2f}")
            return True
            
        except Exception as e:
            self._log_error("Error durante la conexión a FTMO", e)
            return False

    def connect_mt5(self) -> bool:
        """Alias público para connect()"""
        return self.connect()
        
    def connect_ftmo_only(self) -> bool:
        """
        Conecta ÚNICAMENTE a la cuenta FTMO configurada
        Valida que sea exactamente la cuenta correcta
        """
        expected_login = FTMO_ACCOUNT_CONFIG['login']
        expected_server = FTMO_ACCOUNT_CONFIG['server']
        
        self._log_info(f"🏦 Intentando conexión exclusiva a FTMO - Cuenta: {expected_login} | Servidor: {expected_server}")
        
        success = self.connect()
        
        if success:
            # Validar que es exactamente la cuenta FTMO esperada
            if (self.connection_info.account == expected_login and 
                self.connection_info.server == expected_server):
                self._log_info("✅ Conexión FTMO validada correctamente")
                return True
            else:
                self._log_error(f"❌ Cuenta incorrecta: esperada {expected_login}@{expected_server}, " +
                              f"obtenida {self.connection_info.account}@{self.connection_info.server}")
                self.disconnect()
                return False
        else:
            self._log_error("❌ Fallo en conexión FTMO")
            return False
            
    def validate_ftmo_account(self) -> bool:
        """
        Valida que la cuenta actual sea la FTMO configurada
        """
        if not self.is_connected():
            return False
            
        expected_login = FTMO_ACCOUNT_CONFIG['login']
        expected_server = FTMO_ACCOUNT_CONFIG['server']
        
        is_valid = (self.connection_info.account == expected_login and 
                   self.connection_info.server == expected_server)
                   
        if is_valid:
            self._log_info(f"✅ Cuenta FTMO validada: {expected_login}@{expected_server}")
        else:
            self._log_warning(f"⚠️ Cuenta no es FTMO esperada: actual {self.connection_info.account}@{self.connection_info.server}")
            
        return is_valid
        
    def check_ftmo_terminal_installation(self) -> bool:
        """
        Verifica que el terminal FTMO esté instalado en la ruta configurada
        """
        terminal_path = FTMO_ACCOUNT_CONFIG.get('path')
        if not terminal_path:
            self._log_warning("⚠️ Ruta del terminal FTMO no configurada")
            return False
            
        import os
        if os.path.exists(terminal_path):
            self._log_info(f"✅ Terminal FTMO encontrado: {terminal_path}")
            return True
        else:
            self._log_error(f"❌ Terminal FTMO no encontrado: {terminal_path}")
            return False
            
    def get_ftmo_config(self) -> Dict[str, Any]:
        """
        Retorna la configuración completa de FTMO (sin contraseña por seguridad)
        """
        config = FTMO_ACCOUNT_CONFIG.copy()
        config['password'] = '***OCULTA***'  # No mostrar contraseña en logs
        return config
        
    def start_ftmo_terminal(self) -> bool:
        """
        Inicia el terminal FTMO si no está ejecutándose
        """
        terminal_path = FTMO_ACCOUNT_CONFIG.get('path')
        if not terminal_path:
            self._log_error("❌ Ruta del terminal FTMO no configurada")
            return False
            
        if not self.check_ftmo_terminal_installation():
            return False
            
        try:
            import subprocess
            import time
            
            self._log_info("🚀 Iniciando terminal FTMO...")
            subprocess.Popen([terminal_path], shell=True)
            
            # Esperar un poco para que inicie
            time.sleep(3)
            
            self._log_info("✅ Terminal FTMO iniciado")
            return True
            
        except Exception as e:
            self._log_error(f"❌ Error iniciando terminal FTMO: {e}")
            return False

    def disconnect(self):
        """Desconecta de MT5 de forma segura"""
        try:
            if MT5_AVAILABLE and mt5:
                mt5.shutdown()  # type: ignore
            self.connection_info.connected = False
            self._log_info("Desconectado de MT5")
        except Exception as e:
            self._log_error("Error al desconectar", e)

    def is_connected(self) -> bool:
        """Verifica si está conectado a MT5"""
        if not MT5_AVAILABLE or not mt5:
            return False
            
        try:
            # Verificar que MT5 esté realmente conectado
            terminal_info = mt5.terminal_info()  # type: ignore
            return terminal_info is not None and self.connection_info.connected
        except:
            return False

    def get_broker_info(self) -> str:
        """Obtiene información básica del broker"""
        if not self.is_connected():
            return "No conectado"
            
        try:
            account_info = mt5.account_info()  # type: ignore
            if account_info:
                return f"{account_info.company} - {account_info.server}"
            return "Información no disponible"
        except:
            return "Error al obtener información"

    def get_historical_data(self, symbol: str, timeframe: str, count: int = 500):
        """
        Obtiene datos históricos - alias para get_direct_market_data para compatibilidad
        """
        return self.get_direct_market_data(symbol, timeframe, count)

    def get_direct_market_data(self, symbol: str, timeframe: str, count: int = 500):
        """
        Obtiene datos de mercado directamente de MT5 con manejo robusto de errores
        """
        if not self.is_connected():
            self._log_error("No hay conexión a MT5")
            return None
            
        if not _lazy_import_pandas() or pd is None:
            self._log_error("pandas no está disponible")
            return None
            
        try:
            # Mapear timeframes
            timeframe_map = {
                'M1': getattr(mt5, 'TIMEFRAME_M1', 1),
                'M5': getattr(mt5, 'TIMEFRAME_M5', 5),
                'M15': getattr(mt5, 'TIMEFRAME_M15', 15),
                'M30': getattr(mt5, 'TIMEFRAME_M30', 30),
                'H1': getattr(mt5, 'TIMEFRAME_H1', 60),
                'H4': getattr(mt5, 'TIMEFRAME_H4', 240),
                'D1': getattr(mt5, 'TIMEFRAME_D1', 1440)
            }
            
            mt5_timeframe = timeframe_map.get(timeframe)
            if mt5_timeframe is None:
                self._log_error(f"Timeframe '{timeframe}' no soportado")
                return None
                
            # Obtener datos históricos
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)  # type: ignore
            
            if rates is None or len(rates) == 0:
                error_code = mt5.last_error()  # type: ignore
                self._log_error(f"No se pudieron obtener datos para {symbol}. Error: {error_code}")
                return None
                
            # Convertir a DataFrame
            df = pd.DataFrame(rates)  # type: ignore
            
            # Convertir timestamp a datetime pero MANTENER como columna
            df['time'] = pd.to_datetime(df['time'], unit='s')  # type: ignore
            # NO establecer como índice - los algoritmos ICT necesitan 'time' como columna
            # df.set_index('time', inplace=True)  # ← COMENTADO para reparar pipeline
            
            # Renombrar tick_volume a volume para compatibilidad
            if 'tick_volume' in df.columns:
                df['volume'] = df['tick_volume']
            
            # NO forzar nombres de columnas - mantener estructura original + time + volume
            # df.columns = ['open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume']  # COMENTADO
            
            self._log_info(f"✅ Datos obtenidos: {symbol} {timeframe} ({len(df)} velas)")
            return df
            
        except Exception as e:
            self._log_error(f"Error obteniendo datos de {symbol}", e)
            return None
    
    def get_candles(self, symbol: str, timeframe: str, count: int = 500):
        """
        📊 Obtener velas de MT5 - Método estándar para compatibilidad
        
        Args:
            symbol: Símbolo del instrumento
            timeframe: Marco temporal
            count: Número de velas
            
        Returns:
            DataFrame con datos OHLCV o None
        """
        return self.get_direct_market_data(symbol, timeframe, count)

    def get_current_data(self, symbol: str, timeframe: str, count: int = 500):
        """
        📊 Alias para get_candles - compatibilidad con ICTDataManager
        
        Args:
            symbol: Símbolo del instrumento
            timeframe: Marco temporal
            count: Número de velas
            
        Returns:
            DataFrame con datos OHLCV o None
        """
        return self.get_candles(symbol, timeframe, count)

    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtiene información básica de un símbolo"""
        if not self.is_connected():
            return None
            
        try:
            symbol_info = mt5.symbol_info(symbol)  # type: ignore
            if symbol_info is None:
                return None
                
            return {
                'name': symbol_info.name,
                'description': symbol_info.description,
                'point': symbol_info.point,
                'digits': symbol_info.digits,
                'spread': symbol_info.spread,
                'volume_min': symbol_info.volume_min,
                'volume_max': symbol_info.volume_max,
                'trade_mode': symbol_info.trade_mode
            }
        except Exception as e:
            self._log_error(f"Error obteniendo info de {symbol}", e)
            return None

    def get_current_spread(self, symbol: str) -> float:
        """Obtiene el spread actual de un símbolo"""
        if not self.is_connected():
            return 1.5  # Spread estimado por defecto
            
        try:
            tick = mt5.symbol_info_tick(symbol)  # type: ignore
            if tick and hasattr(tick, 'ask') and hasattr(tick, 'bid'):
                spread_points = tick.ask - tick.bid
                symbol_info = mt5.symbol_info(symbol)  # type: ignore
                if symbol_info and hasattr(symbol_info, 'point'):
                    spread_pips = spread_points / symbol_info.point / 10
                    return spread_pips
            return 1.5  # Fallback
        except Exception as e:
            self._log_error(f"Error obteniendo spread de {symbol}", e)
            return 1.5  # Fallback

    def get_connection_status(self) -> Dict[str, Any]:
        """Retorna el estado completo de la conexión"""
        return {
            'connected': self.connection_info.connected,
            'account': self.connection_info.account,
            'server': self.connection_info.server,
            'company': self.connection_info.company,
            'account_type': self.connection_info.account_type.value if self.connection_info.account_type else None,
            'balance': self.connection_info.balance,
            'equity': self.connection_info.equity,
            'margin_level': self.connection_info.margin_level,
            'last_connection': self.connection_info.last_connection.isoformat() if self.connection_info.last_connection else None,
            'mt5_available': MT5_AVAILABLE,
            'last_error': self._last_error,
            'connection_attempts': self._connection_attempts
        }

    # ===============================
    # ORDENES DE TRADING (BÁSICAS)
    # ===============================
    def _ensure_symbol_selected(self, symbol: str) -> bool:
        """Asegura que el símbolo esté seleccionado en MT5"""
        try:
            if not MT5_AVAILABLE or not mt5:
                return False
            info = mt5.symbol_info(symbol)  # type: ignore
            if info is None:
                return False
            if not info.visible:
                return bool(mt5.symbol_select(symbol, True))  # type: ignore
            return True
        except Exception as e:
            self._log_error(f"Error seleccionando símbolo {symbol}", e)
            return False

    def place_market_order(self, symbol: str, side: str, volume: float, price: Optional[float] = None,
                           sl: Optional[float] = None, tp: Optional[float] = None,
                           comment: str = "ICT") -> Dict[str, Any]:
        """Ejecuta una orden de mercado básica BUY/SELL via MT5."""
        result: Dict[str, Any] = {"success": False, "ticket": None, "price": None, "message": ""}
        if not self.is_connected():
            result["message"] = "MT5 no conectado"
            return result
        if not self._ensure_symbol_selected(symbol):
            result["message"] = f"Símbolo no disponible: {symbol}"
            return result
        try:
            import MetaTrader5 as _mt5  # local import para tipos
            # Obtener precio actual si no se especifica
            if price is None:
                tick = mt5.symbol_info_tick(symbol)  # type: ignore
                if not tick:
                    result["message"] = "Tick no disponible"
                    return result
                price = float(tick.ask) if side.upper() == "BUY" else float(tick.bid)

            order_type = mt5.ORDER_TYPE_BUY if side.upper() == "BUY" else mt5.ORDER_TYPE_SELL  # type: ignore
            request = {
                "action": mt5.TRADE_ACTION_DEAL,  # type: ignore
                "symbol": symbol,
                "volume": float(volume),
                "type": order_type,
                "price": float(price),
                "deviation": 20,
                "magic": 12345,
                "comment": comment,
            }
            if sl is not None:
                request["sl"] = float(sl)
            if tp is not None:
                request["tp"] = float(tp)

            send_result = mt5.order_send(request)  # type: ignore
            # Éxito si retcode DONE o PLACED
            done_codes = {
                getattr(mt5, "TRADE_RETCODE_DONE", 10009),
                getattr(mt5, "TRADE_RETCODE_PLACED", 10008),
            }
            success = hasattr(send_result, "retcode") and send_result.retcode in done_codes
            result["success"] = bool(success)
            result["ticket"] = getattr(send_result, "order", None) or getattr(send_result, "deal", None)
            result["price"] = float(price)
            result["message"] = getattr(send_result, "comment", "") or getattr(send_result, "retcode_external", "")
            return result
        except Exception as e:
            self._log_error("Error enviando orden de mercado", e)
            result["message"] = str(e)
            return result

    def place_buy_order(self, symbol: str, volume: float, price: Optional[float] = None,
                        sl: Optional[float] = None, tp: Optional[float] = None,
                        comment: str = "ICT") -> Dict[str, Any]:
        """Helper para BUY market."""
        return self.place_market_order(symbol, "BUY", volume, price, sl, tp, comment)

    def place_sell_order(self, symbol: str, volume: float, price: Optional[float] = None,
                         sl: Optional[float] = None, tp: Optional[float] = None,
                         comment: str = "ICT") -> Dict[str, Any]:
        """Helper para SELL market."""
        return self.place_market_order(symbol, "SELL", volume, price, sl, tp, comment)

    def __del__(self):
        """Limpieza automática al destruir el objeto"""
        try:
            self.disconnect()
        except:
            pass

# ===============================
# FUNCIONES DE CONVENIENCIA
# ===============================

# Instancia global del gestor
_mt5_manager = None

def get_mt5_manager() -> MT5DataManager:
    """Obtiene la instancia global del gestor MT5"""
    global _mt5_manager
    if _mt5_manager is None:
        _mt5_manager = MT5DataManager()
    return _mt5_manager

def connect_mt5() -> bool:
    """Función de conveniencia para conectar a MT5"""
    manager = get_mt5_manager()
    return manager.connect()

def get_market_data(symbol: str, timeframe: str, count: int = 500):
    """Función de conveniencia para obtener datos de mercado"""
    manager = get_mt5_manager()
    return manager.get_direct_market_data(symbol, timeframe, count)

def is_mt5_connected() -> bool:
    """Verifica si MT5 está conectado"""
    manager = get_mt5_manager()
    return manager.is_connected()

if __name__ == "__main__":
    # Test básico
    print("🧪 Test del MT5DataManager optimizado")
    
    manager = get_mt5_manager()
    
    if manager.connect():
        print("✅ Conexión exitosa")
        status = manager.get_connection_status()
        print(f"📊 Estado: {status}")
        
        # Test de datos
        data = manager.get_direct_market_data("EURUSD", "M15", 10)
        if data is not None:
            print(f"✅ Datos obtenidos: {len(data)} velas")
        else:
            print("❌ No se pudieron obtener datos")
            
        manager.disconnect()
    else:
        print("❌ Fallo en la conexión")
