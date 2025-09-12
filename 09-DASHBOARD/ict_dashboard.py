#!/usr/bin/env python3
"""
🎯 ICT ENGINE v6.1 ENTERPRISE - DASHBOARD PRINCIPAL
==================================================

Dashboard modular principal que integra todos los componentes del sistema ICT.
Basado en los tests existentes progress_dashboard.py y progress_dashboard_blackbox.py.

Características:
- ✅ Interfaz modular y escalable
- ✅ Datos en tiempo real del sistema FVG
- ✅ Análisis de coherencia integrado
- ✅ Monitoreo de patrones ICT
- ✅ Gestión de memoria persistente
- ✅ Sistema de alertas inteligente

Versión: v6.1.0-enterprise-dashboard
Fecha: 4 de Septiembre 2025
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Configurar paths del dashboard
dashboard_root = Path(__file__).parent
project_root = dashboard_root.parent
sys.path.insert(0, str(project_root / "01-CORE"))
sys.path.insert(0, str(dashboard_root))

# Imports del dashboard modular
from core.dashboard_engine import DashboardEngine
from data.data_collector import RealICTDataCollector
from widgets.main_interface import TextualDashboardApp

class ICTDashboard:
    """🎯 Dashboard principal del ICT Engine v6.1"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializar dashboard principal
        
        Args:
            config: Configuración personalizada del dashboard
        """
        self.config = config or self._get_default_config()
        self.engine = DashboardEngine(self.config)
        self.data_collector = RealICTDataCollector(self.config)
        self.interface = TextualDashboardApp(self.config)
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto del dashboard"""
        return {
            'update_interval': 1.0,  # segundos
            'symbols': ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY'],
            'timeframes': ['M15', 'H1', 'H4'],
            'theme': 'dark',
            'enable_alerts': True,
            'auto_refresh': True,
            'show_debug': False,
            'data_source': 'live',  # 'live' o 'mock'
            'layout_mode': 'tabbed'  # 'tabbed' o 'grid'
        }
    
    def start(self):
        """🚀 Iniciar dashboard"""
        try:
            print("🎯 Iniciando ICT Dashboard v6.1 Enterprise...")
            
            # Inicializar componentes
            self.engine.initialize()
            self.data_collector.start()
            
            # Mostrar interfaz
            self.interface.run(self.engine, self.data_collector)
            
        except KeyboardInterrupt:
            print("\n⏹️ Dashboard detenido por usuario")
        except Exception as e:
            print(f"❌ Error en dashboard: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """⏹️ Detener dashboard"""
        try:
            if hasattr(self, 'data_collector'):
                self.data_collector.stop()
            if hasattr(self, 'engine'):
                self.engine.cleanup()
            print("✅ Dashboard detenido correctamente")
        except Exception as e:
            print(f"⚠️ Error deteniendo dashboard: {e}")

def main():
    """Función principal"""
    # Configuración personalizada si es necesario
    custom_config = {
        'symbols': ['EURUSD', 'GBPUSD', 'XAUUSD'],
        'update_interval': 2.0,
        'theme': 'professional',
        'show_debug': True
    }
    
    # Crear y ejecutar dashboard
    dashboard = ICTDashboard(custom_config)
    dashboard.start()

if __name__ == "__main__":
    main()
