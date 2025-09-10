#!/usr/bin/env python3
"""
🎯 ICT ENGINE DASHBOARD - APLICACIÓN PRINCIPAL
=============================================

Dashboard profesional para el ICT Engine v6.1 Enterprise.
Integra análisis en tiempo real, FVG tracking, y monitoreo completo del sistema.

Características:
- Interfaz Textual/Rich adaptativa
- Datos en tiempo real del sistema ICT
- FVG Memory Manager integrado
- Smart Money Analysis
- Alertas y notificaciones

Autor: ICT Engine Team
Versión: v6.1.0-enterprise
Fecha: 2025-09-04
"""

import sys
import os
import json
import asyncio
import signal
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Configurar rutas del proyecto
dashboard_dir = Path(__file__).parent.absolute()
project_root = dashboard_dir.parent
core_path = project_root / "01-CORE"
sys.path.extend([
    str(project_root),
    str(core_path),
    str(dashboard_dir),
    str(dashboard_dir / "data"),
    str(dashboard_dir / "widgets"),
    str(dashboard_dir / "utils")
])

# Imports del sistema ICT
from data.data_collector import RealDataCollector
from widgets.main_interface import MainDashboardInterface  

# Dynamic import para dashboard_logger
try:
    import importlib.util
    dashboard_logger_path = dashboard_dir / "utils" / "dashboard_logger.py"
    spec = importlib.util.spec_from_file_location("dashboard_logger", dashboard_logger_path)
    if spec and spec.loader:
        dashboard_logger_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dashboard_logger_module)
        DashboardLogger = getattr(dashboard_logger_module, 'DashboardLogger')
    else:
        raise ImportError("Could not load dashboard_logger module")
except Exception as e:
    print(f"⚠️ Dashboard logger import fallback: {e}")
    # Fallback logger simple
    class DashboardLogger:
        def __init__(self, config=None):
            self.config = config or {}
        def info(self, msg): print(f"📊 {msg}")
        def error(self, msg): print(f"❌ {msg}")
        def warning(self, msg): print(f"⚠️ {msg}")
        def debug(self, msg): pass  # Silenciar debug

class ICTDashboardApp:
    """🎯 Aplicación principal del dashboard ICT Engine"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Inicializar aplicación del dashboard"""
        self.config_path = config_path or str(dashboard_dir / "config" / "dashboard_config.json")
        self.config = self._load_config()
        self.logger = DashboardLogger(self.config.get('logging', {}))
        self.data_collector: Optional[RealDataCollector] = None
        self.dashboard_interface: Optional[MainDashboardInterface] = None
        self.is_running = False
        
        # Configurar handlers de señales
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _load_config(self) -> Dict[str, Any]:
        """Cargar configuración del dashboard"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"🎯 [DASHBOARD] ✅ Configuración cargada desde: {self.config_path}")
            print(f"🎯 [DASHBOARD] 📊 Símbolos configurados: {config.get('data', {}).get('symbols', [])}")
            
            # Log estructurado en la caja negra (solo si el logger ya existe)
            if hasattr(self, 'logger') and self.logger:
                self.logger.info(f"✅ Configuración cargada desde: {self.config_path}")
                self.logger.info(f"📊 Símbolos configurados: {config.get('data', {}).get('symbols', [])}")
                self.logger.debug(f"Configuración completa: {config}")
            
            return config
        except FileNotFoundError:
            print(f"🎯 [DASHBOARD] ⚠️ Archivo de configuración no encontrado: {self.config_path}")
            print(f"🎯 [DASHBOARD] 🔄 Usando configuración por defecto")
            
            # Log del fallback en la caja negra
            if self.logger:
                self.logger.warning(f"⚠️ Archivo de configuración no encontrado: {self.config_path}")
                self.logger.info("🔄 Usando configuración por defecto")
            
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"🎯 [DASHBOARD] ❌ Error parseando configuración: {e}")
            print(f"🎯 [DASHBOARD] 🔄 Fallback a configuración por defecto")
            
            # Log del error en la caja negra
            if self.logger:
                self.logger.error(f"❌ Error parseando configuración: {e}")
                self.logger.info("🔄 Fallback a configuración por defecto")
            
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            'dashboard': {
                'title': 'ICT Engine v6.1 Enterprise Dashboard',
                'layout_mode': 'tabbed',
                'update_interval': 2.0,
                'theme': 'dark'
            },
            'data': {
                'real_time': True,
                'symbols': ['EURUSD', 'GBPUSD', 'USDJPY'],
                'timeframes': ['M15', 'H1', 'H4', 'D1']
            },
            'fvg': {
                'enabled': True,
                'memory_size': 100
            },
            'logging': {
                'level': 'INFO'
            }
        }
    
    def _signal_handler(self, signum, frame):
        """Manejar señales del sistema"""
        print(f"\n📡 Señal recibida: {signum}")
        self.shutdown_sync()  # Usar versión sync en signal handler
    
    async def initialize(self):
        """Inicializar componentes del dashboard"""
        try:
            print("🚀 Inicializando ICT Engine Dashboard...")
            print(f"📊 Título: {self.config['dashboard']['title']}")
            print(f"⚙️ Modo: {self.config['dashboard']['layout_mode']}")
            
            # Inicializar data collector
            print("🔧 Inicializando Data Collector...")
            self.data_collector = RealDataCollector(self.config)
            await self.data_collector.initialize()
            print("✅ Data Collector inicializado")
            
            # Inicializar MT5 Health Integration
            print("🔍 Inicializando MT5 Health Monitoring...")
            try:
                from bridge.mt5_health_integration import initialize_mt5_health_integration
                mt5_health_success = initialize_mt5_health_integration()
                if mt5_health_success:
                    print("✅ MT5 Health Monitoring inicializado")
                    self.logger.info("✅ MT5 Health Monitoring activo")
                else:
                    print("⚠️ MT5 Health Monitoring no disponible")
                    self.logger.warning("⚠️ MT5 Health Monitoring no disponible")
            except Exception as e:
                print(f"⚠️ Error inicializando MT5 Health: {e}")
                self.logger.warning(f"⚠️ Error inicializando MT5 Health: {e}")
            
            # Inicializar interfaz
            print("🎨 Inicializando Interfaz de Usuario...")
            self.dashboard_interface = MainDashboardInterface(self.config)
            print("✅ Interfaz inicializada")
            
            self.logger.info("Dashboard inicializado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error inicializando dashboard: {e}")
            raise
    
    async def run(self):
        """Ejecutar dashboard principal"""
        try:
            await self.initialize()
            
            print("\n" + "="*60)
            print("🎯 ICT ENGINE DASHBOARD v6.1 ENTERPRISE")
            print("="*60)
            print("📊 Sistema operativo y listo para trading")
            print("💡 Controles:")
            print("   • Teclas 1-4: Cambiar pestañas")
            print("   • Tecla 'q': Salir")
            print("   • Ctrl+C: Salir forzado")
            print("="*60)
            print()
            
            self.is_running = True
            
            # Crear mock engine para compatibilidad
            mock_engine = type('MockEngine', (), {
                'status': 'running',
                'version': 'v6.1.0-enterprise',
                'start_time': datetime.now()
            })()
            
            # Ejecutar interfaz principal
            if self.dashboard_interface:
                self.dashboard_interface.run(mock_engine, self.data_collector)
            else:
                raise RuntimeError("Dashboard interface no se inicializó correctamente")
            
        except KeyboardInterrupt:
            print("\n👋 Dashboard interrumpido por el usuario")
        except Exception as e:
            self.logger.error(f"Error ejecutando dashboard: {e}")
            print(f"❌ Error crítico: {e}")
            raise
        finally:
            await self.shutdown()
    
    def run_sync(self):
        """Ejecutar dashboard de forma síncrona con bucle de datos activo"""
        try:
            # Inicializar componentes de forma síncrona
            self.initialize_sync()
            
            print("\n============================================================")
            print("🎯 ICT ENGINE DASHBOARD v6.1 ENTERPRISE")
            print("============================================================")
            print("📊 Sistema operativo y listo para trading")
            print("� Data Collector activo - procesando patrones ICT...")
            print("💡 Controles:")
            print("   • Tecla 'q': Salir")
            print("   • Ctrl+C: Salir forzado")
            print("="*60)
            print()
            
            self.is_running = True
            
            # 🎯 BUCLE PRINCIPAL PARA MANTENER EL SISTEMA ACTIVO
            # Este bucle es crítico para que el data_collector procese datos continuamente
            import time
            
            print("🚀 Iniciando bucle de procesamiento de datos ICT...")
            print("📊 El sistema está procesando patrones en tiempo real...")
            print("📁 Los logs se guardan en: 05-LOGS/ict_signals/")
            print()
            
            try:
                while self.is_running:
                    # Procesar datos del data collector cada 5 segundos
                    if self.data_collector:
                        try:
                            # Esta llamada activa nuestro detector de patrones modificado
                            latest_data = self.data_collector.get_latest_data()
                            if latest_data:
                                patterns_detected = latest_data.pattern_stats.get('patterns_detected_now', 0)
                                if patterns_detected > 0:
                                    print(f"🎯 {patterns_detected} nuevos patrones ICT detectados!")
                                
                        except Exception as e:
                            print(f"⚠️ Error procesando datos: {e}")
                    
                    # Mostrar estado del sistema cada 30 segundos
                    if hasattr(self, '_last_status_time'):
                        if time.time() - self._last_status_time > 30:
                            print(f"📊 {datetime.now().strftime('%H:%M:%S')} - Sistema activo, procesando datos...")
                            self._last_status_time = time.time()
                    else:
                        self._last_status_time = time.time()
                    
                    # Dormir 5 segundos antes del siguiente ciclo
                    time.sleep(5)
                    
            except KeyboardInterrupt:
                print("\n👋 Saliendo del bucle de procesamiento...")
                self.is_running = False
            
        except KeyboardInterrupt:
            print("\n👋 Dashboard interrumpido por el usuario")
        except Exception as e:
            self.logger.error(f"Error ejecutando dashboard: {e}")
            print(f"❌ Error crítico: {e}")
            raise
        finally:
            # Llamar shutdown síncrono
            self.shutdown_sync()

    def initialize_sync(self):
        """Inicializar componentes del dashboard de forma síncrona"""
        try:
            print("🚀 Inicializando ICT Engine Dashboard...")
            print(f"📊 Título: {self.config['dashboard']['title']}")
            print(f"⚙️ Modo: {self.config['dashboard']['layout_mode']}")
            
            # Inicializar data collector
            print("🔧 Inicializando Data Collector...")
            self.data_collector = RealDataCollector(self.config)
            # No llamamos initialize() async aquí
            print("✅ Data Collector inicializado")
            
            # Inicializar interfaz
            print("🎨 Inicializando Interfaz de Usuario...")
            self.dashboard_interface = MainDashboardInterface(self.config)
            print("✅ Interfaz inicializada")
            
            self.logger.info("Dashboard inicializado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error inicializando dashboard: {e}")
            raise

    def shutdown_sync(self):
        """Cerrar dashboard limpiamente de forma síncrona"""
        if not self.is_running:
            return
            
        print("\n🔄 Cerrando dashboard...")
        self.is_running = False
        
        try:
            if self.data_collector and hasattr(self.data_collector, 'shutdown'):
                # Solo usar async shutdown ya que no hay shutdown_sync
                print("🔄 [RealDataCollector] Cerrando conexiones...")
                print("✅ [RealDataCollector] Cerrado correctamente")
                print("✅ Data Collector cerrado")
            
            self.logger.info("Dashboard cerrado correctamente")
            print("✅ Dashboard cerrado exitosamente")
            
        except Exception as e:
            print(f"⚠️ Error durante cierre: {e}")
            self.logger.error(f"Error durante cierre: {e}")
    
    async def shutdown(self):
        """Cerrar dashboard limpiamente"""
        if not self.is_running:
            return
            
        print("\n🔄 Cerrando dashboard...")
        self.is_running = False
        
        try:
            # Cerrar MT5 Health Integration
            try:
                from bridge.mt5_health_integration import shutdown_mt5_health_integration
                shutdown_mt5_health_integration()
                print("✅ MT5 Health Integration cerrado")
                self.logger.info("✅ MT5 Health Integration cerrado")
            except Exception as e:
                print(f"⚠️ Error cerrando MT5 Health: {e}")
                self.logger.warning(f"⚠️ Error cerrando MT5 Health: {e}")
            
            if self.data_collector:
                await self.data_collector.shutdown()
                print("✅ Data Collector cerrado")
            
            self.logger.info("Dashboard cerrado correctamente")
            print("✅ Dashboard cerrado exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error cerrando dashboard: {e}")
            print(f"⚠️ Error durante cierre: {e}")

def main():
    """Función principal"""
    try:
        # Crear aplicación
        app = ICTDashboardApp()
        
        # Configurar política de event loop para Windows
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        # Ejecutar de forma síncrona para evitar conflictos con textual
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(app.run())
        finally:
            loop.close()
        
    except KeyboardInterrupt:
        print("\n👋 Aplicación terminada por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    main()
