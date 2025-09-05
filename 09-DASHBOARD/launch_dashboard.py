#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 ICT Engine V6.0 Enterprise SIC - Dashboard Launcher
Inicializador principal del dashboard modular

Autor: ICT Engine Development Team
Fecha: 2025-01-25
Version: 6.0.0
"""

import sys
import os
import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Añadir rutas del sistema
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
core_path = project_root / "01-CORE"
utils_path = core_path / "utils"

sys.path.extend([
    str(project_root),
    str(core_path),
    str(utils_path),
    str(script_dir)
])

# Usar central de imports del sistema ICT v6.0 con ruta específica
try:
    # Agregar específicamente la ruta de utils al inicio del path
    if str(utils_path) not in sys.path:
        sys.path.insert(0, str(utils_path))
    
    from import_center import ImportCenter
    _ic = ImportCenter()
    
    # Importar componentes principales via ImportCenter usando safe_import
    pd = _ic.safe_import('pandas')
    np = _ic.safe_import('numpy')
    
    if pd and np:
        print("✅ [SUCCESS] Pandas/Numpy importados via ImportCenter")
    else:
        print("⚠️ [WARNING] Pandas/Numpy no disponibles via ImportCenter")
    
except ImportError as e:
    print(f"⚠️ [WARNING] ImportCenter no disponible: {e}")
    # Continuar con imports directos
    try:
        import pandas as pd
        import numpy as np
        print("✅ [SUCCESS] Pandas/Numpy importados directamente")
    except ImportError:
        pd = None
        np = None
        print("❌ [ERROR] Pandas/Numpy no disponibles")

try:
    # Imports del dashboard
    from widgets.main_interface import MainDashboardInterface
    from core.dashboard_engine import DashboardEngine  
    from data.data_collector_simplified import RealICTDataCollector as DataCollector
    
    print("✅ Imports del dashboard cargados exitosamente")
    
except ImportError as e:
    print(f"❌ Error en imports del dashboard: {e}")
    print("🔧 Intentando imports alternativos...")
    
    # Crear clases dummy para continuar
    class MainDashboardInterface:
        def __init__(self, config): 
            self.config = config
        def run(self, engine, data_collector):
            print("🎯 Dashboard dummy - configuración cargada")
            print(f"📊 Título: {self.config.get('dashboard', {}).get('title', 'ICT Engine')}")
            return True
    
    class DashboardEngine:
        def __init__(self, config): 
            self.config = config
    
    class DataCollector:
        def __init__(self, *args, **kwargs): 
            self.data_history = []
        def start(self): pass
        def stop(self): pass
        def get_latest_data(self): return {}

try:
    # Imports del sistema principal usando ImportCenter si está disponible
    if '_ic' in locals():
        # Usar ImportCenter para componentes del sistema
        try:
            # Intentar cargar FVGMemoryManager via ImportCenter
            from core.analysis.fvg_memory_manager import FVGMemoryManager
            from core.analysis.pattern_detector import PatternDetector
            print("✅ Componentes del sistema cargados via ImportCenter")
        except ImportError as e:
            print(f"⚠️ Componentes del sistema no disponibles: {e}")
            # Crear clases dummy
            class FVGMemoryManager:
                def __init__(self): pass
            class PatternDetector:
                def __init__(self): pass
    else:
        # Fallback sin ImportCenter
        print("🔄 Cargando componentes sin ImportCenter...")
        try:
            from core.analysis.fvg_memory_manager import FVGMemoryManager
            from core.analysis.pattern_detector import PatternDetector
        except ImportError:
            class FVGMemoryManager:
                def __init__(self): pass
            class PatternDetector:
                def __init__(self): pass
    
    print("✅ Todos los imports completados")
    
except ImportError as e:
    print(f"❌ Error en imports del sistema principal: {e}")
    print("🔧 Verificando rutas de sistema...")
    print(f"Script dir: {script_dir}")
    print(f"Project root: {project_root}")
    print("Rutas en sys.path:")
    for path in sys.path:
        print(f"  - {path}")
    # No salir, continuar con clases dummy

class DashboardLauncher:
    """🚀 Lanzador principal del dashboard"""
    
    def __init__(self):
        self.config_file = script_dir / "config" / "dashboard_config.json"
        self.config = self.load_config()
        self.setup_logging()
        
    def load_config(self) -> Dict[str, Any]:
        """Cargar configuración del dashboard"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"✅ Configuración cargada desde: {self.config_file}")
                return config
            else:
                print(f"⚠️ No se encontró config en: {self.config_file}")
                return self.get_default_config()
        except Exception as e:
            print(f"❌ Error cargando config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto"""
        return {
            "dashboard": {
                "title": "ICT Engine V6.0 Enterprise SIC",
                "version": "6.0.0",
                "refresh_interval": 1000,
                "layout_mode": "tabbed",
                "enable_real_time": True
            },
            "display": {
                "theme": "dark",
                "colors": {
                    "primary": "cyan",
                    "secondary": "green",
                    "warning": "yellow",
                    "error": "red"
                }
            }
        }
    
    def setup_logging(self):
        """Configurar logging del dashboard"""
        try:
            log_config = self.config.get('logging', {})
            log_level = getattr(logging, log_config.get('level', 'INFO'))
            
            # Crear directorio de logs si no existe
            log_file = project_root / log_config.get('file', '05-LOGS/application/dashboard.log')
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            logging.basicConfig(
                level=log_level,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
            self.logger = logging.getLogger(__name__)
            self.logger.info("✅ Logging del dashboard configurado")
            
        except Exception as e:
            print(f"⚠️ Error configurando logging: {e}")
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger(__name__)
    
    def initialize_components(self):
        """Inicializar componentes del sistema"""
        try:
            self.logger.info("🔧 Inicializando componentes del sistema...")
            
            # Inicializar componentes principales
            self.fvg_manager = FVGMemoryManager()
            self.pattern_detector = PatternDetector()
            
            # Inicializar dashboard engine
            self.dashboard_engine = DashboardEngine(self.config)
            
            # Inicializar data collector
            self.data_collector = DataCollector(self.config)
            
            # Inicializar interfaz principal
            self.dashboard_interface = MainDashboardInterface(self.config)
            
            self.logger.info("✅ Componentes inicializados exitosamente")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error inicializando componentes: {e}")
            return False
    
    def run(self):
        """Ejecutar dashboard principal"""
        try:
            print("\n🎯 ICT Engine V6.0 Enterprise SIC - Dashboard")
            print("=" * 50)
            print(f"📍 Proyecto: {project_root}")
            print(f"⚙️ Configuración: {self.config_file}")
            print("=" * 50)
            
            # Inicializar componentes
            if not self.initialize_components():
                print("❌ Error en inicialización, abortando...")
                return False
                
            # Iniciar data collector
            self.logger.info("🔄 Iniciando recolección de datos...")
            self.data_collector.start()
            
            # Ejecutar interfaz principal
            self.logger.info("🎯 Iniciando interfaz del dashboard...")
            self.dashboard_interface.run(
                engine=self.dashboard_engine,
                data_collector=self.data_collector
            )
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 Dashboard detenido por el usuario")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error ejecutando dashboard: {e}")
            print(f"❌ Error crítico: {e}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpieza al cerrar"""
        try:
            self.logger.info("Realizando limpieza...")
            if hasattr(self, 'data_collector'):
                self.data_collector.stop()
            print("✅ Limpieza completada")
        except Exception as e:
            print(f"⚠️ Error en limpieza: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando ICT Engine Dashboard Launcher...")
    
    launcher = DashboardLauncher()
    success = launcher.run()
    
    if success:
        print("✅ Dashboard ejecutado exitosamente")
    else:
        print("❌ Dashboard terminó con errores")
        sys.exit(1)

if __name__ == "__main__":
    main()
