#!/usr/bin/env python3
"""
Sistema de Datos de Mercado Real
Proveedor de datos reales desde MetaTrader5
"""

import os
import sys
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import pandas as pd

# Configurar paths
script_dir = os.path.dirname(os.path.abspath(__file__))
core_path = os.path.join(script_dir, "01-CORE")

if core_path not in sys.path:
    sys.path.insert(0, core_path)

print(f"[RealMarketSystem] Script: {script_dir}")
print(f"[RealMarketSystem] Core: {core_path}")

# Importar validador de datos crítico
try:
    sys.path.insert(0, os.path.join(core_path, "data_management"))
    from data_validator_real_trading import RealTradingDataValidator
    VALIDATOR_AVAILABLE = True
    print("[RealMarketSystem] ✅ Validador de datos crítico cargado")
except ImportError as e:
    print(f"[RealMarketSystem] ⚠️ Validador no disponible: {e}")
    RealTradingDataValidator = None
    VALIDATOR_AVAILABLE = False

class RealMarketDataProvider:
    """Proveedor de datos de mercado real usando MetaTrader5"""
    
    def __init__(self):
        self.is_connected = False
        self.data_cache = {}
        self.mt5_initialized = False
        
        # Inicializar validador de datos crítico
        if VALIDATOR_AVAILABLE and RealTradingDataValidator is not None:
            try:
                self.data_validator = RealTradingDataValidator()
                print("[RealMarketDataProvider] ✅ Validador de datos inicializado")
            except Exception as e:
                print(f"[RealMarketDataProvider] ⚠️ Error inicializando validador: {e}")
                self.data_validator = None
        else:
            self.data_validator = None
            
        print("[RealMarketDataProvider] Inicializado")
        # Intentar conectar inmediatamente
        self.connect()
    
    def connect(self):
        """Conectar a MetaTrader5"""
        try:
            import MetaTrader5 as mt5
            
            if not self.mt5_initialized:
                if mt5.initialize():
                    self.mt5_initialized = True
                    account_info = mt5.account_info()
                    if account_info:
                        self.is_connected = True
                        print(f"[RealMarketDataProvider] ✅ Conectado a MT5 - Cuenta: {account_info.login}")
                        print(f"[RealMarketDataProvider] Servidor: {account_info.server}")
                        print(f"[RealMarketDataProvider] Balance: {account_info.balance}")
                    else:
                        print("[RealMarketDataProvider] ❌ Info de cuenta no disponible")
                else:
                    print("[RealMarketDataProvider] ❌ No se pudo inicializar MT5")
            else:
                self.is_connected = True
                print("[RealMarketDataProvider] ✅ MT5 ya inicializado")
                
        except ImportError:
            print("[RealMarketDataProvider] ❌ MetaTrader5 no está instalado")
        except Exception as e:
            print(f"[RealMarketDataProvider] ❌ Error conectando: {e}")
    
    def get_market_data(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        """Obtener datos de mercado reales desde MT5"""
        try:
            if not self.is_connected:
                print(f"[RealMarketDataProvider] Reconectando para {symbol}...")
                self.connect()
            
            if not self.is_connected:
                return None
            
            import MetaTrader5 as mt5
            
            # Mapear timeframes
            timeframe_map = {
                'M1': mt5.TIMEFRAME_M1,
                'M5': mt5.TIMEFRAME_M5,
                'M15': mt5.TIMEFRAME_M15,
                'M30': mt5.TIMEFRAME_M30,
                'H1': mt5.TIMEFRAME_H1,
                'H4': mt5.TIMEFRAME_H4,
                'D1': mt5.TIMEFRAME_D1
            }
            
            mt5_timeframe = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
            
            # Obtener datos recientes
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, 500)
            
            if rates is not None and len(rates) > 0:
                # Convertir a DataFrame
                df = pd.DataFrame(rates)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                df.set_index('time', inplace=True)
                
                current_time = datetime.now(timezone.utc)
                last_candle_time = df.index[-1].tz_localize('UTC') if df.index[-1].tz is None else df.index[-1]
                
                # Verificar si los datos son frescos (menos de 1 hora)
                data_age_minutes = (current_time - last_candle_time.replace(tzinfo=timezone.utc)).total_seconds() / 60
                
                market_data = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'timestamp': current_time.isoformat(),
                    'data': df,
                    'last_price': float(df['close'].iloc[-1]),
                    'data_age_minutes': data_age_minutes,
                    'candles_count': len(df),
                    'data_source': 'MT5_Real',
                    'is_fresh': data_age_minutes < 60  # Datos frescos si son menos de 1 hora
                }
                
                # Cache los datos
                cache_key = f"{symbol}_{timeframe}"
                self.data_cache[cache_key] = {
                    'data': market_data,
                    'timestamp': current_time
                }
                
                # 🔒 VALIDAR DATOS ANTES DE DEVOLVERLOS
                if self.data_validator is not None:
                    try:
                        validated_df = self.data_validator.validate_price_data(df)
                        market_data['data'] = validated_df
                        market_data['validation_status'] = 'VALIDATED'
                        print(f"[RealMarketDataProvider] ✅ Datos validados para {symbol} {timeframe}")
                    except Exception as validation_error:
                        print(f"[RealMarketDataProvider] ⚠️ Error en validación: {validation_error}")
                        market_data['validation_status'] = 'FAILED'
                        market_data['validation_error'] = str(validation_error)
                else:
                    market_data['validation_status'] = 'SKIPPED'
                    print(f"[RealMarketDataProvider] ⚠️ Datos no validados - validador no disponible")
                
                print(f"[RealMarketDataProvider] ✅ Datos obtenidos {symbol} {timeframe}: {len(df)} velas, último precio: {market_data['last_price']:.5f}")
                return market_data
            else:
                print(f"[RealMarketDataProvider] ❌ No se obtuvieron datos para {symbol} {timeframe}")
                return None
                
        except Exception as e:
            print(f"[RealMarketDataProvider] ❌ Error obteniendo datos: {e}")
            return None
    
    def get_cached_data(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        """Obtener datos desde cache si están disponibles y frescos"""
        cache_key = f"{symbol}_{timeframe}"
        if cache_key in self.data_cache:
            cached = self.data_cache[cache_key]
            # Verificar si los datos cached son frescos (menos de 5 minutos)
            current_time = datetime.now(timezone.utc)
            cache_age = (current_time - cached['timestamp']).total_seconds() / 60
            
            if cache_age < 5:  # Datos frescos
                print(f"[RealMarketDataProvider] 📋 Usando datos cached para {symbol} {timeframe} (edad: {cache_age:.1f}min)")
                return cached['data']
        
        return None
    
    def disconnect(self):
        """Desconectar de MT5"""
        try:
            if self.mt5_initialized:
                import MetaTrader5 as mt5
                mt5.shutdown()
                self.mt5_initialized = False
                self.is_connected = False
                print("[RealMarketDataProvider] 🔌 Desconectado de MT5")
        except Exception as e:
            print(f"[RealMarketDataProvider] Error desconectando: {e}")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Obtener estado de conexión"""
        try:
            if self.is_connected:
                import MetaTrader5 as mt5
                account_info = mt5.account_info()
                terminal_info = mt5.terminal_info()
                
                return {
                    'connected': True,
                    'account': account_info.login if account_info else None,
                    'server': account_info.server if account_info else None,
                    'balance': account_info.balance if account_info else None,
                    'terminal_connected': terminal_info.connected if terminal_info else False,
                    'cached_symbols': list(set([key.split('_')[0] for key in self.data_cache.keys()]))
                }
            else:
                return {
                    'connected': False,
                    'error': 'No conectado a MT5'
                }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }

# Instancia global del proveedor de datos reales
_real_data_provider = None

def get_real_data_provider() -> RealMarketDataProvider:
    """Obtener la instancia global del proveedor de datos reales"""
    global _real_data_provider
    if _real_data_provider is None:
        _real_data_provider = RealMarketDataProvider()
    return _real_data_provider

def get_real_market_data(symbol: str = "EURUSD", timeframe: str = "H1") -> Optional[Dict[str, Any]]:
    """Función global para obtener datos de mercado reales"""
    provider = get_real_data_provider()
    return provider.get_market_data(symbol, timeframe)

def get_market_status() -> Dict[str, Any]:
    """Obtener estado del mercado y conexión"""
    provider = get_real_data_provider()
    status = provider.get_connection_status()
    
    # Agregar información adicional
    status.update({
        'provider': 'MetaTrader5',
        'cache_size': len(provider.data_cache),
        'last_check': datetime.now(timezone.utc).isoformat()
    })
    
    return status

def test_real_data_connection():
    """Probar la conexión de datos reales"""
    print("\n=== TEST CONEXIÓN DATOS REALES ===")
    
    provider = get_real_data_provider()
    
    # Test status
    status = provider.get_connection_status()
    print(f"Estado de conexión: {status}")
    
    # Test data retrieval
    symbols = ["EURUSD", "GBPUSD", "USDJPY"]
    timeframes = ["H1", "M15"]
    
    for symbol in symbols:
        for tf in timeframes:
            print(f"\n--- Probando {symbol} {tf} ---")
            data = provider.get_market_data(symbol, tf)
            if data:
                print(f"✅ Datos obtenidos: {data['candles_count']} velas")
                print(f"   Último precio: {data['last_price']}")
                print(f"   Fuente: {data['data_source']}")
                print(f"   Fresco: {data['is_fresh']}")
            else:
                print("❌ No se obtuvieron datos")

if __name__ == "__main__":
    test_real_data_connection()
