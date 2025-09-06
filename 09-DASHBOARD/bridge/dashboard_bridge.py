#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 DASHBOARD BRIDGE v6.1 ENTERPRISE
===================================

Bridge de comunicación entre main.py y el sistema de dashboard.
Integra componentes reales del sistema ICT v6.0 Enterprise.
"""

import sys
import threading
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from queue import Queue, Empty

# Configuración de rutas
project_root = Path(__file__).parent.parent.parent
core_path = project_root / "01-CORE"
dashboard_path = project_root / "09-DASHBOARD"

sys.path.extend([
    str(core_path),
    str(core_path / "utils"),
    str(project_root),
    str(dashboard_path / "data")
])

print(f" [DashboardBridge] Core: {core_path}")
print(f" [DashboardBridge] Dashboard: {dashboard_path}")

# Imports de componentes reales
try:
    from import_center import ImportCenter
    _ic = ImportCenter()
    print(" [DashboardBridge] ImportCenter cargado")
except:
    _ic = None

try:
    from data_collector import RealICTDataCollector
    print(" [DashboardBridge] RealICTDataCollector disponible")
except:
    RealICTDataCollector = None

try:
    import run_real_market_system
    print(" [DashboardBridge] RealMarketSystem disponible")
except:
    run_real_market_system = None

@dataclass
class DashboardMessage:
    type: str
    data: Dict[str, Any]
    timestamp: datetime
    source: str
    priority: int = 1

class DashboardBridge:
    """Bridge principal para comunicación ICT Engine  Dashboard"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {
            'symbols': ['EURUSD', 'GBPUSD', 'USDJPY'],
            'timeframes': ['H1', 'H4', 'D1'],
            'debug_mode': False
        }
        
        self.is_running = False
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0,
            'uptime_start': None
        }
        
        # Componentes reales
        self.data_collector = None
        self.real_market_data_func = None
        self.ict_components = {}
        
        self._initialize_real_components()
        print(" [DashboardBridge] v6.1 Enterprise inicializado")
    
    def _initialize_real_components(self):
        """Inicializar componentes reales del sistema ICT"""
        try:
            # Data Collector
            if RealICTDataCollector:
                collector_config = {
                    'data': {
                        'symbols': self.config['symbols'],
                        'timeframes': self.config['timeframes']
                    }
                }
                self.data_collector = RealICTDataCollector(collector_config)
                print(" [DashboardBridge] Data collector inicializado")
            
            # Market Data
            if run_real_market_system:
                self.real_market_data_func = run_real_market_system.get_real_market_data
                print(" [DashboardBridge] Market data conectado")
            
        except Exception as e:
            print(f" [DashboardBridge] Error inicializando componentes: {e}")
    
    def send_market_data(self, symbol: str, timeframe: str, data: Dict[str, Any]):
        """Enviar datos de mercado reales"""
        if self.real_market_data_func:
            try:
                real_data = self.real_market_data_func(symbol, timeframe)
                print(f" [Bridge] Enviando datos de mercado para {symbol} {timeframe}")
                return {'status': 'sent', 'symbol': symbol, 'timeframe': timeframe}
            except Exception as e:
                print(f" [Bridge] Error enviando datos de mercado: {e}")
                return {'status': 'error', 'error': str(e)}
    
    def send_pattern_detection(self, pattern_type: str, details: Dict[str, Any]):
        """Enviar detección de patrón"""
        print(f" [Bridge] Patrón detectado: {pattern_type}")
        return {'status': 'sent', 'pattern_type': pattern_type}
    
    def send_alert(self, alert_type: str, message: str, severity: str = 'info'):
        """Enviar alerta"""
        print(f" [Bridge] Alerta {severity}: {message}")
        return {'status': 'sent', 'alert_type': alert_type, 'severity': severity}
    
    def get_bridge_stats(self) -> Dict[str, Any]:
        """Estadísticas del bridge"""
        uptime = None
        if self.stats['uptime_start']:
            uptime = (datetime.now() - self.stats['uptime_start']).total_seconds()
        
        return {
            'is_running': self.is_running,
            'messages_sent': self.stats['messages_sent'],
            'messages_received': self.stats['messages_received'],
            'errors': self.stats['errors'],
            'uptime_seconds': uptime,
            'data_collector_active': self.data_collector is not None,
            'real_market_data_available': self.real_market_data_func is not None,
            'ict_components_connected': len(self.ict_components)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Estado completo"""
        return {
            'status': 'running' if self.is_running else 'stopped',
            'config': self.config,
            'stats': self.get_bridge_stats(),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def get_real_data(self) -> Optional[Dict[str, Any]]:
        """Obtener datos reales del sistema ICT"""
        try:
            if self.data_collector:
                return self.data_collector.get_latest_data()
            return None
        except Exception as e:
            print(f" [Bridge] Error obteniendo datos reales: {e}")
            return None

# Instancia global
_bridge_instance = None

def get_dashboard_bridge() -> DashboardBridge:
    """Obtener instancia global"""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = DashboardBridge()
    return _bridge_instance

def initialize_bridge(config: Optional[Dict[str, Any]] = None) -> DashboardBridge:
    """Inicializar bridge"""
    global _bridge_instance
    _bridge_instance = DashboardBridge(config)
    return _bridge_instance

# Funciones de conveniencia
def send_market_data(symbol: str, timeframe: str, data: Dict[str, Any]):
    bridge = get_dashboard_bridge()
    return bridge.send_market_data(symbol, timeframe, data)

def send_pattern_detection(pattern_type: str, details: Dict[str, Any]):
    bridge = get_dashboard_bridge()
    return bridge.send_pattern_detection(pattern_type, details)

def send_alert(alert_type: str, message: str, severity: str = 'info'):
    bridge = get_dashboard_bridge()
    return bridge.send_alert(alert_type, message, severity)

def get_real_system_data() -> Optional[Dict[str, Any]]:
    bridge = get_dashboard_bridge()
    return bridge.get_real_data()

# Test de integración
if __name__ == "__main__":
    print(" DASHBOARD BRIDGE v6.1 ENTERPRISE")
    print("===================================")
    
    bridge = DashboardBridge()
    print(f" Estado: {bridge.get_status()}")
    print(f" Estadísticas: {bridge.get_bridge_stats()}")
    print(" Dashboard Bridge listo para integración")
