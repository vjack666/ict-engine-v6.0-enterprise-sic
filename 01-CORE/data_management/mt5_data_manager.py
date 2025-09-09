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

    def connect(self) -> bool:
        """
        Conecta a MetaTrader 5 de forma robusta
        """
        if not _lazy_import_mt5() or mt5 is None:
            self._log_error("MT5 no está disponible")
            return False
            
        self._connection_attempts += 1
        
        try:
            # Intentar conexión
            if not mt5.initialize():  # type: ignore
                error_code = mt5.last_error()  # type: ignore
                self._log_error(f"Fallo al inicializar MT5. Error: {error_code}")
                return False
                
            # Verificar conexión
            account_info = mt5.account_info()  # type: ignore
            if account_info is None:
                self._log_error("No se pudo obtener información de la cuenta")
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
                
            self._log_info(f"✅ Conectado exitosamente - Cuenta: {account_info.login} | Servidor: {account_info.server}")
            return True
            
        except Exception as e:
            self._log_error("Error durante la conexión", e)
            return False

    def connect_mt5(self) -> bool:
        """Alias público para connect()"""
        return self.connect()

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
            
            # Convertir timestamp a datetime
            df['time'] = pd.to_datetime(df['time'], unit='s')  # type: ignore
            df.set_index('time', inplace=True)  # type: ignore
            
            # Renombrar columnas para consistencia
            df.columns = ['open', 'high', 'low', 'close', 'tick_volume', 'spread', 'real_volume']  # type: ignore
            
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
