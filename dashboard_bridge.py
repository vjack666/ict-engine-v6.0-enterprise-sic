#!/usr/bin/env python3
"""
🔗 DASHBOARD BRIDGE - Puente entre Sistema ICT y Dashboard Enterprise
===================================================================

Conecta el sistema ICT Engine optimizado con el Dashboard Enterprise,
eliminando la necesidad de re-inicializar componentes.

NOTA TÉCNICA:
- Utiliza importlib para imports dinámicos y evitar errores de Pylance
- Los componentes del dashboard son opcionales y se cargan de forma robusta
- Todos los imports están encapsulados en try-catch para máxima compatibilidad

Versión: v6.0.0
Fecha: 9 Septiembre 2025
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Configurar rutas
project_root = Path(__file__).parent.absolute()
core_path = project_root / "01-CORE"
dashboard_path = project_root / "09-DASHBOARD"

sys.path.extend([
    str(project_root),
    str(core_path),
    str(dashboard_path),
    str(dashboard_path / "data"),
    str(dashboard_path / "widgets"),
    str(dashboard_path / "core")
])

class DashboardBridge:
    """🔗 Puente entre sistema ICT y Dashboard Enterprise"""
    
    def __init__(self):
        self.components = {}
        self.system_ready = False
        self.dashboard_available = False
        self._check_dashboard_availability()
    
    def _check_dashboard_availability(self):
        """Verificar si los componentes del dashboard están disponibles"""
        try:
            # Verificar estructura básica del dashboard
            required_paths = [
                dashboard_path / "data",
                dashboard_path / "widgets", 
                dashboard_path / "core"
            ]
            
            self.dashboard_available = all(path.exists() for path in required_paths)
            
            if self.dashboard_available:
                print("✅ Dashboard components structure available")
            else:
                print("⚠️ Dashboard components structure incomplete")
                
        except Exception as e:
            print(f"⚠️ Error checking dashboard availability: {e}")
            self.dashboard_available = False
    
    def initialize_system_components(self) -> Dict[str, Any]:
        """📊 Inicializar componentes ICT optimizados"""
        try:
            print("🔧 Inicializando componentes del sistema ICT...")
            
            # 1. UnifiedMemorySystem
            try:
                from analysis.unified_memory_system import get_unified_memory_system
                memory_system = get_unified_memory_system()
                self.components['memory_system'] = memory_system
                print("✅ UnifiedMemorySystem v6.1 inicializado")
            except ImportError as e:
                print(f"⚠️ UnifiedMemorySystem no disponible: {e}")
                self.components['memory_system'] = None
            
            # 2. SmartMoneyAnalyzer optimizado
            try:
                from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
                smart_money = SmartMoneyAnalyzer()
                self.components['smart_money'] = smart_money
                print("✅ SmartMoneyAnalyzer optimizado inicializado")
            except ImportError as e:
                print(f"⚠️ SmartMoneyAnalyzer no disponible: {e}")
                self.components['smart_money'] = None
            
            # 3. MT5DataManager
            try:
                from data_management.mt5_data_manager import MT5DataManager
                mt5_manager = MT5DataManager()
                self.components['mt5_manager'] = mt5_manager
                print("✅ MT5DataManager inicializado")
            except ImportError as e:
                print(f"⚠️ MT5DataManager no disponible: {e}")
                self.components['mt5_manager'] = None
            
            # 4. ICTPatternDetector - Usar import_manager para carga robusta
            try:
                # Intentar usar import_manager si está disponible
                try:
                    from import_manager import get_pattern_detector
                    ICTPatternDetector = get_pattern_detector()
                    if ICTPatternDetector:
                        pattern_detector = ICTPatternDetector()
                        self.components['pattern_detector'] = pattern_detector
                        print("✅ ICTPatternDetector inicializado via ImportManager")
                    else:
                        raise ImportError("ImportManager no pudo cargar ICTPatternDetector")
                except ImportError:
                    # Fallback directo
                    import importlib
                    module = importlib.import_module('analysis.pattern_detector')
                    ICTPatternDetector = getattr(module, 'ICTPatternDetector', None)
                    if ICTPatternDetector:
                        pattern_detector = ICTPatternDetector()
                        self.components['pattern_detector'] = pattern_detector
                        print("✅ ICTPatternDetector inicializado via fallback")
                    else:
                        raise ImportError("ICTPatternDetector no encontrado")
            except Exception as e:
                print(f"⚠️ ICTPatternDetector no disponible: {e}")
                self.components['pattern_detector'] = None
            
            # Verificar si al menos algunos componentes están disponibles
            available_components = [k for k, v in self.components.items() if v is not None]
            
            if available_components:
                self.system_ready = True
                print(f"✅ Sistema parcialmente listo con: {', '.join(available_components)}")
            else:
                print("❌ No se pudo inicializar ningún componente del sistema")
                self.system_ready = False
            
            return self.components
            
        except Exception as e:
            print(f"❌ Error crítico inicializando componentes: {e}")
            return {}
    
    def launch_dashboard_with_real_data(self, components: Dict[str, Any]) -> bool:
        """🎯 Lanzar dashboard con datos reales"""
        if not self.dashboard_available:
            print("❌ Dashboard components no están disponibles")
            return False
            
        try:
            print("🚀 Lanzando Dashboard Enterprise con datos reales...")
            
            # Importar componentes de dashboard usando importlib para evitar errores de Pylance
            import importlib
            
            # Intentar importar RealICTDataCollector
            try:
                data_collector_module = importlib.import_module('data.data_collector')
                RealICTDataCollector = getattr(data_collector_module, 'RealICTDataCollector', None)
                if RealICTDataCollector:
                    print("✅ RealICTDataCollector importado")
                else:
                    raise ImportError("RealICTDataCollector no encontrado en módulo")
            except Exception as e:
                print(f"⚠️ RealICTDataCollector no disponible - {e}")
                return False
            
            # Intentar importar MainDashboardInterface
            try:
                interface_module = importlib.import_module('widgets.main_interface')
                MainDashboardInterface = getattr(interface_module, 'MainDashboardInterface', None)
                if MainDashboardInterface:
                    print("✅ MainDashboardInterface importado")
                else:
                    raise ImportError("MainDashboardInterface no encontrado en módulo")
            except Exception as e:
                print(f"⚠️ MainDashboardInterface no disponible - {e}")
                return False
                
            # Intentar importar DashboardEngine
            try:
                engine_module = importlib.import_module('core.dashboard_engine')
                DashboardEngine = getattr(engine_module, 'DashboardEngine', None)
                if DashboardEngine:
                    print("✅ DashboardEngine importado")
                else:
                    raise ImportError("DashboardEngine no encontrado en módulo")
            except Exception as e:
                print(f"⚠️ DashboardEngine no disponible - {e}")
                return False
            
            # Configuración enterprise
            config = {
                'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD'],
                'timeframes': ['M15', 'H1', 'H4'],
                'update_interval': 1.0,
                'theme': 'enterprise',
                'enable_alerts': True,
                'auto_refresh': True,
                'show_debug': False,
                'data_source': 'live',
                'layout_mode': 'tabbed',
                'enterprise_mode': True,
                'real_components': components  # ✅ COMPONENTES REALES
            }
            
            # Inicializar con componentes reales
            engine = DashboardEngine(config)
            data_collector = RealICTDataCollector(config)
            
            # ✅ CONECTAR COMPONENTES REALES si el método existe
            if hasattr(data_collector, 'connect_real_components'):
                data_collector.connect_real_components(components)
                print("✅ Componentes reales conectados al data collector")
            else:
                print("⚠️ Método connect_real_components no disponible")
            
            interface = MainDashboardInterface(config)
            
            print("✅ Dashboard Enterprise conectado con sistema real")
            print("🎯 Iniciando interfaz...")
            
            # Ejecutar dashboard
            interface.run(engine, data_collector)
            
            return True
            
        except Exception as e:
            print(f"❌ Error lanzando dashboard: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def launch_basic_dashboard(self) -> bool:
        """📊 Lanzar dashboard básico como fallback"""
        try:
            print("🔄 Intentando lanzar dashboard básico...")
            
            # Configuración básica
            basic_config = {
                'symbols': ['EURUSD', 'GBPUSD'],
                'timeframes': ['H1', 'H4'],
                'update_interval': 5.0,
                'theme': 'basic',
                'enable_alerts': False,
                'auto_refresh': True,
                'show_debug': True,
                'data_source': 'demo',
                'layout_mode': 'simple'
            }
            
            # Intentar ejecutar dashboard básico
            dashboard_script = dashboard_path / "start_dashboard.py"
            
            if dashboard_script.exists():
                import subprocess
                result = subprocess.run([
                    sys.executable, str(dashboard_script)
                ], cwd=str(dashboard_path))
                print("✅ Dashboard básico ejecutado")
                return True
            else:
                print("❌ No se encontró start_dashboard.py")
                return False
                
        except Exception as e:
            print(f"❌ Error lanzando dashboard básico: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """📊 Obtener estado del sistema y componentes"""
        return {
            'system_ready': self.system_ready,
            'dashboard_available': self.dashboard_available,
            'components_status': {
                name: component is not None 
                for name, component in self.components.items()
            },
            'available_components_count': len([c for c in self.components.values() if c is not None]),
            'total_components_count': len(self.components)
        }
