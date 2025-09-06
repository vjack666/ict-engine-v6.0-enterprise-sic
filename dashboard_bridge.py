#!/usr/bin/env python3
"""
🔗 DASHBOARD BRIDGE - Puente entre Sistema ICT y Dashboard Enterprise
===================================================================

Conecta el sistema ICT Engine optimizado con el Dashboard Enterprise,
eliminando la necesidad de re-inicializar componentes.

Versión: v6.0.0
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
    str(dashboard_path / "widgets")
])

class DashboardBridge:
    """🔗 Puente entre sistema ICT y Dashboard Enterprise"""
    
    def __init__(self):
        self.components = {}
        self.system_ready = False
    
    def initialize_system_components(self) -> Dict[str, Any]:
        """📊 Inicializar componentes ICT optimizados"""
        try:
            print("🔧 Inicializando componentes del sistema ICT...")
            
            # 1. UnifiedMemorySystem
            from analysis.unified_memory_system import get_unified_memory_system
            memory_system = get_unified_memory_system()
            self.components['memory_system'] = memory_system
            print("✅ UnifiedMemorySystem v6.1 inicializado")
            
            # 2. SmartMoneyAnalyzer optimizado
            from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
            smart_money = SmartMoneyAnalyzer()
            self.components['smart_money'] = smart_money
            print("✅ SmartMoneyAnalyzer optimizado inicializado")
            
            # 3. MT5DataManager
            from data_management.mt5_data_manager import MT5DataManager
            mt5_manager = MT5DataManager()
            self.components['mt5_manager'] = mt5_manager
            print("✅ MT5DataManager inicializado")
            
            # 4. ICTPatternDetector
            from analysis.ict_pattern_detector import ICTPatternDetector
            pattern_detector = ICTPatternDetector()
            self.components['pattern_detector'] = pattern_detector
            print("✅ ICTPatternDetector inicializado")
            
            self.system_ready = True
            return self.components
            
        except Exception as e:
            print(f"❌ Error inicializando componentes: {e}")
            return {}
    
    def launch_dashboard_with_real_data(self, components: Dict[str, Any]) -> bool:
        """🎯 Lanzar dashboard con datos reales"""
        try:
            print("🚀 Lanzando Dashboard Enterprise con datos reales...")
            
            # Importar componentes de dashboard
            from data.data_collector import RealICTDataCollector
            from widgets.main_interface import MainDashboardInterface
            from core.dashboard_engine import DashboardEngine
            
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
            
            # ✅ CONECTAR COMPONENTES REALES
            data_collector.connect_real_components(components)
            
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
