#!/usr/bin/env python3
"""
🔧 CONFIGURACIÓN DE IMPORTS - ICT ENGINE v6.0 SIC
================================================

Sistema para manejar imports robustos y resolver problemas de Pylance.
Centraliza todas las configuraciones de imports para el main.py.

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 5 Septiembre 2025
"""

import sys
from pathlib import Path
from typing import Optional, Any

# Configurar rutas del proyecto para imports
PROJECT_ROOT = Path(__file__).parent.absolute()
CORE_PATH = PROJECT_ROOT / "01-CORE"
UTILS_PATH = CORE_PATH / "utils"

# Agregar rutas al PYTHONPATH
sys.path.extend([
    str(PROJECT_ROOT),
    str(CORE_PATH),
    str(UTILS_PATH),
    str(CORE_PATH / "ict_engine"),
    str(CORE_PATH / "smart_money_concepts"),
    str(CORE_PATH / "analysis")
])

class ImportManager:
    """🔧 Gestor centralizado de imports para main.py"""
    
    def __init__(self):
        """Inicializar gestor de imports"""
        self.import_center = None
        self._initialize_import_center()
    
    def _initialize_import_center(self):
        """Inicializar ImportCenter si está disponible"""
        try:
            # Importación dinámica de ImportCenter
            import importlib.util
            import_center_path = UTILS_PATH / "import_center.py"
            
            if import_center_path.exists():
                spec = importlib.util.spec_from_file_location("import_center", import_center_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.import_center = module.ImportCenter()
                    print("✅ ImportCenter inicializado")
                else:
                    raise ImportError("No se pudo crear spec para import_center")
            else:
                raise ImportError(f"No se encontró import_center.py en {import_center_path}")
                
        except ImportError as e:
            print(f"⚠️ ImportCenter no disponible: {e}")
            self.import_center = None
    
    def get_mt5_data_manager(self):
        """Obtener MT5DataManager"""
        try:
            if self.import_center:
                # Usar ImportCenter si está disponible
                module = self.import_center.safe_import('mt5_data_manager')
                if module:
                    return module.MT5DataManager
            
            # Fallback directo con importación dinámica
            import importlib.util
            mt5_path = UTILS_PATH / "mt5_data_manager.py"
            
            if mt5_path.exists():
                spec = importlib.util.spec_from_file_location("mt5_data_manager", mt5_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module.MT5DataManager
                else:
                    raise ImportError("No se pudo crear spec para mt5_data_manager")
            else:
                raise ImportError(f"No se encontró mt5_data_manager.py en {mt5_path}")
            
        except Exception as e:
            print(f"❌ Error cargando MT5DataManager: {e}")
            return None
    
    def get_pattern_detector(self):
        """Obtener ICTPatternDetector"""
        try:
            if self.import_center:
                # Usar ImportCenter si está disponible
                module = self.import_center.safe_import('ict_engine.pattern_detector')
                if module:
                    return module.ICTPatternDetector
            
            # Fallback directo con importación dinámica
            import importlib.util
            pattern_path = CORE_PATH / "ict_engine" / "pattern_detector.py"
            
            if pattern_path.exists():
                spec = importlib.util.spec_from_file_location("pattern_detector", pattern_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module.ICTPatternDetector
                else:
                    raise ImportError("No se pudo crear spec para pattern_detector")
            else:
                raise ImportError(f"No se encontró pattern_detector.py en {pattern_path}")
            
        except Exception as e:
            print(f"❌ Error cargando ICTPatternDetector: {e}")
            return None
    
    def get_order_blocks_detector(self):
        """Obtener OrderBlocksPatternDetector híbrido"""
        try:
            if self.import_center:
                # Usar ImportCenter si está disponible
                module = self.import_center.safe_import('ict_engine.patterns.order_blocks_integration')
                if module:
                    return module.OrderBlocksPatternDetector
            
            # Fallback directo con importación dinámica
            import importlib.util
            order_blocks_path = CORE_PATH / "ict_engine" / "patterns" / "order_blocks_integration.py"
            
            if order_blocks_path.exists():
                spec = importlib.util.spec_from_file_location("order_blocks_integration", order_blocks_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module.OrderBlocksPatternDetector
                else:
                    raise ImportError("No se pudo crear spec para order_blocks_integration")
            else:
                raise ImportError(f"No se encontró order_blocks_integration.py en {order_blocks_path}")
            
        except Exception as e:
            print(f"❌ Error cargando OrderBlocksPatternDetector: {e}")
            return None

    def get_smart_money_analyzer(self):
        """Obtener SmartMoneyAnalyzer"""
        try:
            if self.import_center:
                # Usar ImportCenter si está disponible
                module = self.import_center.safe_import('smart_money_concepts.smart_money_analyzer')
                if module:
                    return module.SmartMoneyAnalyzer
            
            # Fallback directo con importación dinámica
            import importlib.util
            smart_money_path = CORE_PATH / "smart_money_concepts" / "smart_money_analyzer.py"
            
            if smart_money_path.exists():
                spec = importlib.util.spec_from_file_location("smart_money_analyzer", smart_money_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module.SmartMoneyAnalyzer
                else:
                    raise ImportError("No se pudo crear spec para smart_money_analyzer")
            else:
                raise ImportError(f"No se encontró smart_money_analyzer.py en {smart_money_path}")
            
        except Exception as e:
            print(f"❌ Error cargando SmartMoneyAnalyzer: {e}")
            return None
    
    def check_components_availability(self):
        """Verificar disponibilidad de componentes"""
        components = {
            'mt5_data_manager': self.get_mt5_data_manager() is not None,
            'pattern_detector': self.get_pattern_detector() is not None,
            'order_blocks_detector': self.get_order_blocks_detector() is not None,
            'smart_money_analyzer': self.get_smart_money_analyzer() is not None
        }
        
        return components

# Instancia global del gestor
IMPORT_MANAGER = ImportManager()

# Funciones de conveniencia para main.py
def get_mt5_data_manager():
    """Función de conveniencia para obtener MT5DataManager"""
    return IMPORT_MANAGER.get_mt5_data_manager()

def get_pattern_detector():
    """Función de conveniencia para obtener ICTPatternDetector"""
    return IMPORT_MANAGER.get_pattern_detector()

def get_order_blocks_detector():
    """Función de conveniencia para obtener OrderBlocksPatternDetector"""
    return IMPORT_MANAGER.get_order_blocks_detector()

def get_smart_money_analyzer():
    """Función de conveniencia para obtener SmartMoneyAnalyzer"""
    return IMPORT_MANAGER.get_smart_money_analyzer()

def check_components():
    """Función de conveniencia para verificar componentes"""
    return IMPORT_MANAGER.check_components_availability()

if __name__ == "__main__":
    # Test de imports
    print("🔧 TESTING IMPORT MANAGER")
    print("=" * 30)
    
    components = check_components()
    for component, available in components.items():
        status = "✅" if available else "❌"
        print(f"{status} {component}: {available}")
    
    if all(components.values()):
        print("\n✅ Todos los componentes están disponibles")
    else:
        print("\n⚠️ Algunos componentes no están disponibles")
