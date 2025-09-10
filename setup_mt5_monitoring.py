"""
MT5 Health Monitoring Setup Script v6.0 Enterprise
Configuración completa del sistema de monitoreo con Black Box Logging

Este script configura e inicia el sistema completo de monitoreo de salud MT5:
- MT5ConnectionManager con imports corregidos
- MT5HealthMonitor con alertas automáticas
- MT5BlackBoxLogger para análisis tipo caja negra
- Logging estructurado para análisis posterior
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Resolver imports
def _resolve_imports():
    """Resolver imports con path absoluto"""
    current_dir = Path(__file__).parent
    core_dir = current_dir / "01-CORE"
    data_mgmt_dir = core_dir / "data_management"
    
    paths_to_add = [str(current_dir), str(core_dir), str(data_mgmt_dir)]
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)

_resolve_imports()

# Imports principales
try:
    from mt5_connection_manager import MT5ConnectionManager
    from mt5_health_monitor import MT5HealthMonitor, HealthStatus
    from mt5_black_box_logger import MT5BlackBoxLogger
    print("✅ Todos los módulos importados correctamente")
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    MODULES_AVAILABLE = False

class MT5MonitoringSystem:
    """
    Sistema completo de monitoreo MT5 con logging tipo caja negra
    """
    
    def __init__(self):
        """Inicializar el sistema de monitoreo"""
        self.mt5_manager = None
        self.health_monitor = None
        self.black_box_logger = None
        self.system_active = False
        
        print("🔧 Inicializando MT5 Monitoring System...")
        
    def setup_system(self, check_interval: int = 30, max_failed_checks: int = 3) -> bool:
        """
        Configurar todos los componentes del sistema
        
        Args:
            check_interval: Intervalo entre checks de salud (segundos)
            max_failed_checks: Máximo de checks fallidos antes de alerta crítica
            
        Returns:
            bool: True si la configuración fue exitosa
        """
        if not MODULES_AVAILABLE:
            print("❌ Módulos no disponibles - no se puede configurar el sistema")
            return False
            
        try:
            print("🔧 Configurando componentes...")
            
            # 1. Configurar MT5ConnectionManager
            print("   📡 Configurando MT5ConnectionManager...")
            self.mt5_manager = MT5ConnectionManager()
            print("   ✅ MT5ConnectionManager configurado")
            
            # 2. Configurar Black Box Logger
            print("   📝 Configurando Black Box Logger...")
            self.black_box_logger = MT5BlackBoxLogger()
            print("   ✅ Black Box Logger configurado")
            
            # 3. Configurar Health Monitor
            print("   🔍 Configurando Health Monitor...")
            self.health_monitor = MT5HealthMonitor(
                mt5_manager=self.mt5_manager,
                check_interval=check_interval,
                max_failed_checks=max_failed_checks
            )
            print("   ✅ Health Monitor configurado")
            
            # 4. Configurar callbacks de alerta
            self._setup_alert_callbacks()
            
            print("✅ Sistema configurado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando sistema: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def _setup_alert_callbacks(self):
        """Configurar callbacks para alertas"""
        def critical_alert_callback(metrics):
            """Callback para alertas críticas"""
            if metrics.status in [HealthStatus.CRITICAL, HealthStatus.DISCONNECTED]:
                print(f"🚨 CRITICAL ALERT: {metrics.error_message}")
                print(f"   Failed checks: {metrics.failed_checks_count}")
                print(f"   Last successful check: {metrics.last_successful_check}")
                
                # Aquí se pueden agregar acciones adicionales:
                # - Enviar emails
                # - Notificaciones push
                # - Alertas SMS
                # - Integración con sistemas de monitoreo externos
                
        def performance_alert_callback(metrics):
            """Callback para alertas de performance"""
            if metrics.response_time_ms > 10000:  # > 10 segundos
                print(f"⚠️ PERFORMANCE ALERT: Response time {metrics.response_time_ms:.1f}ms")
                
        # Agregar callbacks al monitor
        if self.health_monitor:
            self.health_monitor.add_alert_callback(critical_alert_callback)
            self.health_monitor.add_alert_callback(performance_alert_callback)
            print("   📞 Callbacks de alerta configurados")
            
    def start_monitoring(self) -> bool:
        """
        Iniciar el sistema de monitoreo
        
        Returns:
            bool: True si el monitoreo se inició correctamente
        """
        if not self.health_monitor:
            print("❌ Sistema no configurado - ejecutar setup_system() primero")
            return False
            
        try:
            print("🚀 Iniciando sistema de monitoreo...")
            
            # Iniciar health monitoring
            if self.health_monitor.start_monitoring():
                self.system_active = True
                print("✅ Health Monitoring activo")
                
                # Ejecutar check inicial
                initial_metrics = self.health_monitor.force_health_check()
                print(f"📊 Check inicial: {initial_metrics.status.value}")
                print(f"   Conexión: {'✅' if initial_metrics.connection_active else '❌'}")
                print(f"   Tiempo de respuesta: {initial_metrics.response_time_ms:.1f}ms")
                
                # Mostrar rutas de logs
                if self.black_box_logger:
                    print(f"📁 Logs guardándose en: {self.black_box_logger.base_log_dir}")
                    print(f"   📅 Daily logs: {self.black_box_logger.daily_dir}")
                    print(f"   🚨 Alerts: {self.black_box_logger.alerts_dir}")
                    print(f"   📊 Performance: {self.black_box_logger.performance_dir}")
                    print(f"   🔗 Connections: {self.black_box_logger.connections_dir}")
                
                return True
            else:
                print("❌ Error iniciando health monitoring")
                return False
                
        except Exception as e:
            print(f"❌ Error iniciando monitoreo: {e}")
            return False
            
    def stop_monitoring(self) -> None:
        """Detener el sistema de monitoreo"""
        if self.health_monitor and self.system_active:
            print("🛑 Deteniendo sistema de monitoreo...")
            self.health_monitor.stop_monitoring()
            self.system_active = False
            print("✅ Sistema detenido")
            
    def get_system_status(self) -> dict:
        """Obtener estado completo del sistema"""
        if not self.health_monitor:
            return {'status': 'NOT_CONFIGURED'}
            
        health_summary = self.health_monitor.get_health_summary()
        
        if self.black_box_logger:
            logging_stats = self.black_box_logger.get_logging_statistics()
        else:
            logging_stats = {'status': 'NOT_AVAILABLE'}
            
        return {
            'system_active': self.system_active,
            'health_monitoring': health_summary,
            'black_box_logging': logging_stats,
            'timestamp': datetime.now().isoformat()
        }
        
    def run_continuous_monitoring(self, duration_hours: float = 24.0):
        """
        Ejecutar monitoreo continuo por un período específico
        
        Args:
            duration_hours: Duración del monitoreo en horas
        """
        if not self.start_monitoring():
            print("❌ No se pudo iniciar el monitoreo")
            return
            
        print(f"🔄 Ejecutando monitoreo continuo por {duration_hours} horas...")
        print("   Presiona Ctrl+C para detener el monitoreo")
        
        try:
            # Mostrar estado cada 5 minutos
            status_interval = 300  # 5 minutos
            end_time = time.time() + (duration_hours * 3600)
            last_status_time = 0
            
            while time.time() < end_time and self.system_active:
                current_time = time.time()
                
                # Mostrar estado cada 5 minutos
                if current_time - last_status_time >= status_interval:
                    status = self.get_system_status()
                    health_status = status['health_monitoring']['current_status']
                    response_time = status['health_monitoring']['response_time_ms']
                    
                    print(f"📊 Status: {health_status} | Response: {response_time:.1f}ms | Time: {datetime.now().strftime('%H:%M:%S')}")
                    last_status_time = current_time
                
                time.sleep(10)  # Check cada 10 segundos
                
        except KeyboardInterrupt:
            print("\\n🛑 Monitoreo interrumpido por usuario")
        finally:
            self.stop_monitoring()
            
            # Mostrar resumen final
            if self.black_box_logger:
                final_stats = self.black_box_logger.get_logging_statistics()
                print("\\n📊 RESUMEN FINAL:")
                print(f"   Health checks: {final_stats['health_checks_logged']}")
                print(f"   Alertas: {final_stats['alerts_logged']}")
                print(f"   Entries performance: {final_stats['performance_entries']}")
                print(f"   Eventos conexión: {final_stats['connection_events']}")
                print(f"   Tiempo activo: {final_stats['uptime']}")

def main():
    """Función principal para ejecutar el sistema"""
    print("🚀 MT5 Health Monitoring System v6.0 Enterprise")
    print("=" * 60)
    
    # Crear e inicializar sistema
    monitoring_system = MT5MonitoringSystem()
    
    if not monitoring_system.setup_system(check_interval=30, max_failed_checks=3):
        print("❌ Error configurando sistema - abortando")
        return
    
    # Ejecutar monitoreo continuo
    try:
        monitoring_system.run_continuous_monitoring(duration_hours=1.0)  # 1 hora por defecto
    except Exception as e:
        print(f"❌ Error en monitoreo: {e}")
    finally:
        monitoring_system.stop_monitoring()
        
    print("\\n✅ Sistema de monitoreo finalizado")

if __name__ == "__main__":
    main()
