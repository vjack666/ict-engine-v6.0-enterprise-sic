"""
MT5 Connection Manager v6.0 Enterprise
Gestor de conexiones robustas a MetaTrader5 con FTMO Global Markets

Dependencias:
- MetaTrader5
- utils.smart_trading_logger
"""

import MetaTrader5 as mt5
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any
from utils.smart_trading_logger import SmartTradingLogger

class MT5ConnectionManager:
    """
    Gestor de conexiones MT5 enterprise con reconexión automática
    y validación de cuenta FTMO Global Markets
    """
    
    def __init__(self):
        """Inicializar el gestor de conexiones MT5"""
        self.logger = SmartTradingLogger()
        self.is_connected = False
        self.connection_attempts = 0
        self.max_attempts = 3
        self.reconnect_delay = 5
        self.account_info = None
        self._lock = threading.Lock()
        
    def connect(self, path: Optional[str] = None, login: Optional[int] = None, 
                password: Optional[str] = None, server: Optional[str] = None) -> bool:
        """
        Establecer conexión con MetaTrader5
        
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
                # Intentar conexión
                if login and password and server:
                    success = mt5.initialize(path=path, login=login, password=password, server=server)
                else:
                    success = mt5.initialize(path=path)
                
                if success:
                    self.account_info = mt5.account_info()
                    if self.account_info:
                        self.is_connected = True
                        self.connection_attempts = 0
                        
                        # Validar que es una cuenta FTMO Global Markets
                        if self._validate_ftmo_account():
                            self.logger.info(f"✅ Conectado a FTMO Global Markets - Cuenta: {self.account_info.login}")
                            return True
                        else:
                            self.logger.warning("⚠️ Cuenta no validada como FTMO Global Markets")
                            return False
                    else:
                        self.logger.error("❌ No se pudo obtener información de la cuenta")
                        return False
                else:
                    error = mt5.last_error()
                    self.logger.error(f"❌ Error de conexión MT5: {error}")
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
            
        # Validaciones específicas de FTMO Global Markets
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
        """Cerrar conexión MT5"""
        with self._lock:
            try:
                mt5.shutdown()
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
            
        # Verificar si la conexión sigue activa
        try:
            account = mt5.account_info()
            if account is None:
                self.is_connected = False
                return self.reconnect()
            return True
        except Exception as e:
            self.logger.error(f"❌ Error verificando conexión: {e}")
            self.is_connected = False
            return self.reconnect()
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Obtener información de la cuenta
        
        Returns:
            dict: Información de la cuenta o None
        """
        if not self.ensure_connection():
            return None
            
        try:
            info = mt5.account_info()
            if info:
                return {
                    'login': info.login,
                    'server': info.server,
                    'company': info.company,
                    'balance': info.balance,
                    'equity': info.equity,
                    'currency': info.currency,
                    'leverage': info.leverage,
                    'margin': info.margin,
                    'margin_free': info.margin_free,
                    'margin_level': info.margin_level,
                    'name': info.name
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
            'account_login': self.account_info.login if self.account_info else None,
            'server': self.account_info.server if self.account_info else None,
            'last_check': datetime.now().isoformat()
        }

# Instancia singleton
_connection_manager = None

def get_mt5_connection() -> MT5ConnectionManager:
    """Obtener instancia singleton del gestor de conexiones"""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = MT5ConnectionManager()
    return _connection_manager
