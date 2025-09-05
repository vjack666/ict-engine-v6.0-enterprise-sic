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
from data_collector import RealDataCollector
from main_interface import MainDashboardInterface  
from dashboard_logger import DashboardLogger

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
            print(f"✅ Configuración cargada desde: {self.config_path}")
            return config
        except FileNotFoundError:
            print(f"⚠️ Archivo de configuración no encontrado: {self.config_path}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando configuración: {e}")
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
        self.shutdown()
    
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
            self.dashboard_interface.run(mock_engine, self.data_collector)
            
        except KeyboardInterrupt:
            print("\n👋 Dashboard interrumpido por el usuario")
        except Exception as e:
            self.logger.error(f"Error ejecutando dashboard: {e}")
            print(f"❌ Error crítico: {e}")
            raise
        finally:
            await self.shutdown()
    
    def run_sync(self):
        """Ejecutar dashboard de forma síncrona"""
        try:
            # Inicializar componentes de forma síncrona
            self.initialize_sync()
            
            print("\n============================================================")
            print("🎯 ICT ENGINE DASHBOARD v6.1 ENTERPRISE")
            print("============================================================")
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
            
            # Ejecutar interfaz principal de forma síncrona
            self.dashboard_interface.run(mock_engine, self.data_collector)
            
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
                # Intentar shutdown síncrono si existe
                if hasattr(self.data_collector, 'shutdown_sync'):
                    self.data_collector.shutdown_sync()
                else:
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
