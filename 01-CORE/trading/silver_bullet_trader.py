#!/usr/bin/env python3
"""
🔫 SILVER BULLET AUTO TRADER - ICT ENGINE v6.0 ENTERPRISE
========================================================

Ejecutor automático de patrones Silver Bullet integrado con main.py
Detecta kill zones activas y ejecuta trades basados en Silver Bullet patterns.

Integra: SilverBulletDetectorEnterprise + TradeExecutor + RealTradingSystem

Ubicación: 01-CORE/trading/silver_bullet_trader.py
Integración: main.py -> opción "Silver Bullet Auto Trading"
"""

from protocols.unified_logging import get_unified_logger
import sys
import os
from pathlib import Path
from datetime import datetime, time, timedelta
import asyncio
from typing import Optional, Dict, List, Any
import time as time_module

# Setup paths - desde 01-CORE/trading/
CURRENT_DIR = Path(__file__).resolve().parent
CORE_PATH = CURRENT_DIR.parent
SYSTEM_ROOT = CORE_PATH.parent
sys.path.insert(0, str(CORE_PATH))

class SilverBulletAutoTrader:
    """🔫 Clase principal para trading automático Silver Bullet"""
    
    def __init__(self):
        self.active = False
        self.detector = None
        self.trade_executor = None
        self.trading_system = None
        self.data_downloader = None
        
    def initialize_components(self):
        """🔧 Inicializar todos los componentes necesarios"""
        try:
            print("🔧 Inicializando componentes Silver Bullet...")
            
            # Import componentes necesarios
            from ict_engine.advanced_patterns.silver_bullet_enterprise import SilverBulletDetectorEnterprise
            from trading.trade_executor import TradeExecutor
            from trading.real_trading_system import RealTradingSystem
            from data_management.advanced_candle_downloader import AdvancedCandleDownloader
            
            # Inicializar componentes
            self.detector = SilverBulletDetectorEnterprise()
            self.trade_executor = TradeExecutor()
            self.trading_system = RealTradingSystem()
            self.data_downloader = AdvancedCandleDownloader()
            
            print("✅ Componentes Silver Bullet inicializados")
            return True
            
        except Exception as e:
            print(f"❌ Error inicializando componentes: {e}")
            return False
    
    def check_killzone_status(self) -> Dict[str, Any]:
        """⏰ Verificar estado actual de kill zones"""
        if not self.detector:
            return {'active': False, 'message': 'Detector no inicializado'}
            
        current_killzone = self.detector.get_current_killzone()
        now = datetime.now()
        current_hour = now.hour
        
        killzone_info = {
            'current_zone': current_killzone,
            'hour': current_hour,
            'active': False,
            'message': '',
            'next_killzone': '',
            'time_until_next': ''
        }
        
        # Kill zones principales para trading Silver Bullet
        if current_killzone in ['london', 'new_york', 'overlap']:
            killzone_info['active'] = True
            killzone_info['message'] = f"🟢 {current_killzone.upper()} KILLZONE ACTIVA"
        else:
            killzone_info['active'] = False
            killzone_info['message'] = f"🔴 {current_killzone.upper()} - Fuera de kill zones principales"
            
            # Calcular próxima kill zone
            next_zones = {
                3: 'London (3-5 AM EST)',
                10: 'NY/London Close (10-11 AM EST)',
                20: 'Asian (8-10 PM EST)'
            }
            
            for hour, zone_name in next_zones.items():
                if current_hour < hour:
                    hours_until = hour - current_hour
                    killzone_info['next_killzone'] = zone_name
                    killzone_info['time_until_next'] = f"{hours_until} hora(s)"
                    break
            else:
                # Si es después de las 20h, la próxima es London a las 3h del día siguiente
                hours_until = (24 - current_hour) + 3
                killzone_info['next_killzone'] = 'London (3-5 AM EST)'
                killzone_info['time_until_next'] = f"{hours_until} hora(s)"
        
        return killzone_info
    
    def scan_silver_bullet_signals(self, symbols: Optional[List[str]] = None, timeframes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """🎯 Escanear señales Silver Bullet en múltiples símbolos"""
        if not self.detector or not self.data_downloader:
            return []
            
        symbols = symbols or ['EURUSD', 'GBPUSD', 'USDCAD', 'USDJPY']
        timeframes = timeframes or ['M5', 'M15']
        detected_signals = []
        
        print("\n📊 ESCANEANDO SEÑALES SILVER BULLET...")
        print("-" * 50)
        
        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    print(f"🔍 Analizando {symbol} {timeframe}...")
                    
                    # Obtener datos actuales usando download_candles
                    data = None
                    try:
                        data = self.data_downloader.download_candles(symbol, timeframe, bars_count=100)
                    except Exception as data_error:
                        print(f"   ⚠️  Error obteniendo datos {symbol} {timeframe}: {data_error}")
                        continue
                    
                    if data is not None and len(data) > 20:
                        current_price = float(data['close'].iloc[-1])
                        
                        # Detectar Silver Bullet patterns
                        signals = self.detector.detect_silver_bullet_patterns(
                            data=data,
                            symbol=symbol,
                            timeframe=timeframe,
                            current_price=current_price
                        )
                        
                        # Procesar señales válidas
                        for signal in signals:
                            if signal.confidence > 70.0:  # Solo confianza alta
                                signal_data = {
                                    'symbol': symbol,
                                    'timeframe': timeframe,
                                    'signal_type': signal.signal_type.value,
                                    'confidence': signal.confidence,
                                    'direction': signal.direction.value,
                                    'entry_price': signal.entry_price,
                                    'stop_loss': signal.stop_loss,
                                    'take_profit_1': signal.take_profit_1,
                                    'take_profit_2': signal.take_profit_2,
                                    'killzone_timing': signal.killzone_timing,
                                    'structure_confluence': signal.structure_confluence,
                                    'order_block_present': signal.order_block_present,
                                    'narrative': signal.narrative,
                                    'timestamp': datetime.now()
                                }
                                detected_signals.append(signal_data)
                                
                                print(f"🎯 SEÑAL DETECTADA:")
                                print(f"   {symbol} {timeframe} - {signal.signal_type.value}")
                                print(f"   Confianza: {signal.confidence:.1f}%")
                                print(f"   Dirección: {signal.direction.value}")
                                print(f"   Entry: {signal.entry_price:.5f}")
                        
                        if not signals:
                            print(f"   ⚪ Sin señales en {symbol} {timeframe}")
                            
                except Exception as e:
                    print(f"   ❌ Error analizando {symbol} {timeframe}: {e}")
        
        print(f"\n📈 RESUMEN: {len(detected_signals)} señales detectadas")
        return detected_signals
    
    def execute_signal(self, signal_data: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """💰 Ejecutar señal Silver Bullet (real o simulado)"""
        try:
            if dry_run:
                print(f"🧪 SIMULANDO TRADE: {signal_data['symbol']} {signal_data['direction']}")
                return {
                    'success': True,
                    'trade_id': f"SIM_{int(datetime.now().timestamp())}",
                    'message': 'Trade simulado exitosamente',
                    'dry_run': True
                }
            
            if not self.trade_executor:
                return {
                    'success': False,
                    'error': 'Trade executor no inicializado',
                    'dry_run': False
                }
            
            # Preparar señal para ejecutor
            trade_signal = {
                'symbol': signal_data['symbol'],
                'direction': signal_data['direction'],
                'entry_price': signal_data['entry_price'],
                'stop_loss': signal_data['stop_loss'],
                'take_profit_1': signal_data['take_profit_1'],
                'take_profit_2': signal_data['take_profit_2'],
                'confidence': signal_data['confidence'],
                'pattern_type': 'silver_bullet',
                'killzone': signal_data['signal_type']
            }
            
            # EJECUTAR TRADE REAL
            result = self.trade_executor.execute_silver_bullet_trade(trade_signal)
            
            if result.success:
                trade_id = getattr(result, 'ticket', f"SB_{int(datetime.now().timestamp())}")
                print(f"✅ TRADE EJECUTADO: {trade_id}")
                print(f"   Símbolo: {signal_data['symbol']}")
                print(f"   Dirección: {signal_data['direction']}")
                print(f"   Tamaño: {getattr(result, 'volume', 'N/A')}")
                print(f"   Precio: {getattr(result, 'execution_price', signal_data['entry_price'])}")
                
                return {
                    'success': True,
                    'trade_id': trade_id,
                    'message': 'Trade ejecutado exitosamente',
                    'dry_run': False
                }
            else:
                print(f"❌ TRADE FALLÓ: {getattr(result, 'error_message', 'Error desconocido')}")
                return {
                    'success': False,
                    'error': getattr(result, 'error_message', 'Error desconocido'),
                    'dry_run': False
                }
                
        except Exception as e:
            print(f"❌ Error ejecutando señal: {e}")
            return {
                'success': False,
                'error': str(e),
                'dry_run': dry_run
            }
    
    def run_continuous_scan(self, interval_minutes: int = 5, max_duration_hours: int = 8):
        """🔄 Ejecutar escaneo continuo durante kill zones activas"""
        print(f"\n🔄 INICIANDO ESCANEO CONTINUO")
        print(f"   Intervalo: {interval_minutes} minutos")
        print(f"   Duración máxima: {max_duration_hours} horas")
        print("   Presiona CTRL+C para detener\n")
        
        start_time = datetime.now()
        max_end_time = start_time + timedelta(hours=max_duration_hours)
        
        try:
            while datetime.now() < max_end_time:
                # Verificar si seguimos en kill zone activa
                killzone_status = self.check_killzone_status()
                
                if not killzone_status['active']:
                    print(f"⏰ Fuera de kill zone activa: {killzone_status['message']}")
                    print(f"   Próxima: {killzone_status.get('next_killzone', 'N/A')}")
                    break
                
                print(f"\n🔍 Escaneo: {datetime.now().strftime('%H:%M:%S')} - {killzone_status['current_zone']}")
                
                # Escanear señales
                signals = self.scan_silver_bullet_signals()
                
                # Mostrar señales encontradas (sin ejecutar automáticamente)
                if signals:
                    print(f"🎯 {len(signals)} señales encontradas:")
                    for i, signal in enumerate(signals, 1):
                        print(f"   {i}. {signal['symbol']} {signal['direction']} - {signal['confidence']:.1f}%")
                        
                    # Aquí podrías agregar lógica de auto-ejecución
                    # Por ahora solo muestra las señales
                    
                else:
                    print("   ⚪ Sin señales válidas en este escaneo")
                
                # Esperar intervalo
                print(f"⏱️  Esperando {interval_minutes} minutos hasta próximo escaneo...")
                time_module.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 ESCANEO DETENIDO POR USUARIO")
        except Exception as e:
            print(f"\n❌ Error en escaneo continuo: {e}")
        
        print(f"\n✅ Escaneo continuo finalizado. Duración: {datetime.now() - start_time}")


# =============================================================================
# 🎮 FUNCIONES PARA INTEGRACIÓN CON MAIN.PY
# =============================================================================

def silver_bullet_menu():
    """🎮 Menú interactivo Silver Bullet para main.py"""
    trader = SilverBulletAutoTrader()
    
    while True:
        print("\n🔫 SILVER BULLET AUTO TRADER v6.0")
        print("=" * 40)
        print("1. 🔧 Inicializar componentes")
        print("2. ⏰ Ver estado kill zones")
        print("3. 🎯 Escanear señales (una vez)")
        print("4. 🔄 Escaneo continuo")
        print("5. 💰 Ejecutar señal manual")
        print("6. 🏠 Volver al menú principal")
        print("=" * 40)
        
        choice = input("Selecciona opción (1-6): ").strip()
        
        if choice == "1":
            success = trader.initialize_components()
            if success:
                print("✅ Componentes inicializados correctamente")
            else:
                print("❌ Error inicializando componentes")
            input("\nPresiona ENTER para continuar...")
            
        elif choice == "2":
            status = trader.check_killzone_status()
            print(f"\n⏰ ESTADO KILL ZONES")
            print(f"   {status['message']}")
            print(f"   Hora actual: {status['hour']}:00")
            if not status['active']:
                print(f"   Próxima kill zone: {status.get('next_killzone', 'N/A')}")
                print(f"   Tiempo restante: {status.get('time_until_next', 'N/A')}")
            input("\nPresiona ENTER para continuar...")
            
        elif choice == "3":
            if not trader.detector:
                print("❌ Primero inicializa los componentes (opción 1)")
            else:
                signals = trader.scan_silver_bullet_signals()
                if signals:
                    print(f"\n📊 {len(signals)} señales encontradas")
                    for i, signal in enumerate(signals, 1):
                        print(f"{i}. {signal['symbol']} {signal['timeframe']} - {signal['confidence']:.1f}%")
                else:
                    print("\n⚪ No se encontraron señales válidas")
            input("\nPresiona ENTER para continuar...")
            
        elif choice == "4":
            if not trader.detector:
                print("❌ Primero inicializa los componentes (opción 1)")
            else:
                try:
                    interval = int(input("Intervalo en minutos (default 5): ") or "5")
                    duration = int(input("Duración máxima en horas (default 8): ") or "8")
                    trader.run_continuous_scan(interval, duration)
                except ValueError:
                    print("❌ Valores inválidos, usando defaults (5 min, 8h)")
                    trader.run_continuous_scan(5, 8)
            
        elif choice == "5":
            print("🚧 Función de ejecución manual en desarrollo")
            input("\nPresiona ENTER para continuar...")
            
        elif choice == "6":
            break
            
        else:
            print("❌ Opción inválida")
            input("\nPresiona ENTER para continuar...")


def run_silver_bullet_trader():
    """🚀 Función principal para llamar desde main.py"""
    try:
        silver_bullet_menu()
    except KeyboardInterrupt:
        print("\n\n🛑 Silver Bullet Auto Trader interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error en Silver Bullet Auto Trader: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_silver_bullet_trader()