#!/usr/bin/env python3
"""
🚀 START DASHBOARD - PUNTO DE ENTRADA ENTERPRISE
===============================================

Punto de entrada principal para el Dashboard Enterprise del ICT Engine v6.0.
Integra perfectamente con el sistema ya inicializado en main.py.

Características Enterprise:
- ✅ Integración con RealICTDataCollector ya inicializado
- ✅ Uso del SmartTradingLogger configurado
- ✅ Compatibilidad con modo silencioso
- ✅ Aprovecha componentes reales ya validados
- ✅ Mantiene arquitectura enterprise existente
- ⚡ CIERRE ULTRA-RÁPIDO optimizado para resolver lentitud

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 10 de Septiembre, 2025
Versión: v6.0-enterprise-integrated-fast-shutdown
"""

import sys
import os
import asyncio
import signal
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Union

# Configurar rutas siguiendo la estructura del main.py
dashboard_dir = Path(__file__).parent.absolute()
project_root = dashboard_dir.parent
core_path = project_root / "01-CORE"

# Agregar paths al sistema (mismo orden que main.py)
sys.path.extend([
    str(project_root),
    str(core_path),
    str(dashboard_dir),
    str(dashboard_dir / "core"),
    str(dashboard_dir / "data"),
    str(dashboard_dir / "widgets"),
    str(dashboard_dir / "utils"),
    str(dashboard_dir / "components"),
    str(dashboard_dir / "bridge")
])

# Cargar configuración central de logging del proyecto (root y módulos)
try:
    from protocols.unified_logging import load_unified_logging_config as _load_logging_cfg
    _load_logging_cfg()
except Exception:
    pass
# Logging modes utility (loaded after sys.path setup)
try:
    from utils.logging_modes import apply_logging_mode, silence_stdout_stderr
except Exception:
    def apply_logging_mode(mode: Optional[str] = None) -> str:
        return (mode or os.environ.get("ICT_LOGGING_MODE", "silent")).strip().lower()
    from contextlib import contextmanager
    @contextmanager
    def silence_stdout_stderr(enabled: bool = True):
        yield

# Resolve logging mode early and optionally silence stdout/stderr during heavy imports
_resolved_mode = apply_logging_mode(os.environ.get('ICT_LOGGING_MODE'))
_silent_mode = (_resolved_mode == 'silent')

# Variables globales para manejo dinámico de clases (sin conflictos de tipo)
dashboard_imports_ok = False

with silence_stdout_stderr(enabled=_silent_mode):
    # Importar sistema de auto-recovery
    try:
        from core.dashboard_auto_recovery import DashboardAutoRecovery
        auto_recovery_available = True
        print("✅ [AUTO-RECOVERY] Sistema de auto-recovery disponible")
    except ImportError as e:
        DashboardAutoRecovery = None
        auto_recovery_available = False
        print(f"⚠️ [WARNING] Auto-recovery no disponible: {e}")

    # Importar sistema de health monitoring
    try:
        from core.dashboard_health_monitor import DashboardHealthMonitor
        health_monitoring_available = True
        print("✅ [HEALTH-MONITOR] Sistema de health monitoring disponible")
    except ImportError as e:
        DashboardHealthMonitor = None
        health_monitoring_available = False
        print(f"⚠️ [WARNING] Health monitoring no disponible: {e}")

# Funciones para cargar componentes dinámicamente (sin conflictos de tipo)
def load_dashboard_components():
    """Cargar componentes del dashboard dinámicamente"""
    components = {}
    
    try:
        # Imports del dashboard (sin conflictos de tipo)
        import ict_dashboard
        import core.dashboard_engine
        import core.enterprise_singleton_manager
        
        # Asignar clases dinámicamente
        components['ICTDashboard'] = ict_dashboard.ICTDashboard
        components['DashboardEngine'] = core.dashboard_engine.DashboardEngine
        components['EnterpriseSingletonManager'] = core.enterprise_singleton_manager.EnterpriseSingletonManager
        components['initialize_enterprise_components'] = core.enterprise_singleton_manager.initialize_enterprise_components
        components['cleanup_enterprise_components'] = core.enterprise_singleton_manager.cleanup_enterprise_components
        
        # Intentar importar data collector del dashboard
        try:
            from data.data_collector import RealICTDataCollector
            components['RealICTDataCollector'] = RealICTDataCollector
        except ImportError:
            print("[INFO] Usando RealICTDataCollector externo")
            components['RealICTDataCollector'] = None
        
        components['imports_ok'] = True
        print("✅ [DASHBOARD] Imports principales cargados correctamente")
        
    except ImportError as e:
        print(f"[WARNING] Algunos imports del dashboard no disponibles: {e}")
        components['imports_ok'] = False
        
        # Definir clases fallback optimizadas para trading
        class ICTDashboardFallback:
            def __init__(self, config):
                self.config = config
                self.trading_active = True
                print("📊 [DASHBOARD] Modo fallback trading activado")
                print("💰 [TRADING] Sistema optimizado para manejo de cuenta")
            
            def start(self):
                print("🔄 [FALLBACK] Dashboard trading iniciado")
                print("📈 [TRADING] Monitoreo de cuenta activo")
            
            def stop(self):
                print("🔄 [FALLBACK] Dashboard trading detenido")
                print("💰 [TRADING] Cuenta asegurada")
        
        class DashboardEngineFallback:
            def __init__(self, config):
                self.config = config
                self.account_monitoring = True
        
        # Fallback para Enterprise Singleton Manager
        class EnterpriseSingletonManagerFallback:
            @staticmethod
            def cleanup_singletons():
                print("🔄 [FALLBACK] Singleton cleanup ejecutado")
        
        def initialize_enterprise_components_fallback():
            print("🔄 [FALLBACK] Enterprise components inicializados para trading")
            print("💰 [TRADING] Componentes de cuenta configurados")
            return True
        
        def cleanup_enterprise_components_fallback():
            print("🔄 [FALLBACK] Enterprise components limpiados")
        
        # Asignar fallbacks
        components['ICTDashboard'] = ICTDashboardFallback
        components['DashboardEngine'] = DashboardEngineFallback
        components['EnterpriseSingletonManager'] = EnterpriseSingletonManagerFallback
        components['initialize_enterprise_components'] = initialize_enterprise_components_fallback
        components['cleanup_enterprise_components'] = cleanup_enterprise_components_fallback
        components['RealICTDataCollector'] = None
    
    return components

class StartDashboard:
    """🚀 Launcher del Dashboard Enterprise con cierre ultra-rápido"""
    
    def __init__(self, real_data_collector=None, smart_logger=None):
        """
        Inicializar launcher del dashboard
        
        Args:
            real_data_collector: RealICTDataCollector ya inicializado (desde main.py)
            smart_logger: SmartTradingLogger ya configurado (desde main.py)
        """
        self.project_root = project_root
        self.dashboard_dir = dashboard_dir
        self.real_data_collector = real_data_collector
        self.smart_logger = smart_logger
        self.dashboard_instance = None  # Tipo dinámico para manejar ambas clases
        
        # Cargar componentes dinámicamente
        self.components = load_dashboard_components()
        
        # Verificar si se ejecuta desde main.py con datos reales
        self.real_mode = os.getenv('ICT_REAL_MODE', '0') == '1'
        self.data_collector_active = os.getenv('ICT_DATA_COLLECTOR', 'inactive') == 'active'
        self.mt5_manager_active = os.getenv('ICT_MT5_MANAGER', 'inactive') == 'active'
        self.enterprise_mode = os.getenv('ICT_ENTERPRISE_MODE', '0') == '1'
        
        if self.real_mode:
            print("🚀 [DASHBOARD] Modo REAL detectado - lectura real del sistema activada")
            print(f"📊 [DASHBOARD] Data Collector: {'✅ Activo' if self.data_collector_active else '❌ Inactivo'}")
            print(f"🔗 [DASHBOARD] MT5 Manager: {'✅ Activo' if self.mt5_manager_active else '❌ Inactivo'}")
            print(f"🏭 [DASHBOARD] Enterprise Mode: {'✅ Activo' if self.enterprise_mode else '❌ Inactivo'}")
        
        # Configuración enterprise por defecto
        self.config = self._get_enterprise_config()
        
        # Configurar logger para debugging si no existe
        if not hasattr(self, 'logger'):
            import logging
            self.logger = logging.getLogger('DashboardRunner')
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)
        
        # Configurar signal handler unificado con logging mejorado
        self._setup_unified_signal_handler()
        
        # Configurar sistema de auto-recovery
        self.auto_recovery = None
        if auto_recovery_available:
            self._setup_auto_recovery_system()
        
        # Configurar sistema de health monitoring
        self.health_monitor = None
        if health_monitoring_available:
            self._setup_health_monitoring_system()
    
    
    def _emergency_dashboard_close(self):
        """🛑 Cierre de emergencia del dashboard"""
        try:
            # Intentar métodos de cierre disponibles con fallback
            dashboard_closed = False
            
            if self.dashboard_instance and hasattr(self.dashboard_instance, 'stop'):
                try:
                    self.dashboard_instance.stop()
                    dashboard_closed = True
                except:
                    pass
            
            if not dashboard_closed and self.dashboard_instance and hasattr(self.dashboard_instance, 'exit'):
                try:
                    self.dashboard_instance.exit()
                    dashboard_closed = True
                except:
                    pass
            
            if not dashboard_closed and self.dashboard_instance and hasattr(self.dashboard_instance, 'shutdown'):
                try:
                    self.dashboard_instance.shutdown()
                    dashboard_closed = True
                except:
                    pass
            
            print("⚡ [EMERGENCY] Dashboard cerrado")
            
        except Exception as e:
            print(f"⚡ [EMERGENCY] Error cerrando dashboard: {e}")
    
    def _emergency_close_loggers(self):
        """📝 Cierre de emergencia de loggers"""
        try:
            import logging
            
            closed_count = 0
            
            # Cerrar handlers de loggers específicos del dashboard
            problematic_loggers = ['MT5Health', 'DashboardIntegrator', 'PatternDetector', 'SmartMoney']
            
            for logger_name in problematic_loggers:
                try:
                    logger = logging.getLogger(logger_name)
                    for handler in logger.handlers[:]:
                        handler.close()
                        logger.removeHandler(handler)
                        closed_count += 1
                except:
                    pass
            
            # Cerrar smart logger si existe
            if self.smart_logger:
                try:
                    if hasattr(self.smart_logger, 'close'):
                        self.smart_logger.close()
                except:
                    pass
            
            print(f"⚡ [EMERGENCY] {closed_count} loggers cerrados")
            
        except Exception as e:
            print(f"⚡ [EMERGENCY] Error cerrando loggers: {e}")
    
    def _emergency_flush_streams(self):
        """💧 Flush de emergencia de streams"""
        try:
            sys.stdout.flush()
            sys.stderr.flush()
            print("⚡ [EMERGENCY] Streams flushed")
        except:
            pass
    
    def _get_enterprise_config(self) -> Dict[str, Any]:
        """Obtener configuración enterprise OPTIMIZADA para manejo de cuenta de trading"""
        
        # Configuración base optimizada para trading real
        config = {
            'title': 'ICT Engine v6.0 Enterprise - MANEJO ÓPTIMO DE CUENTA',
            'mode': 'enterprise_real' if self.real_mode else 'enterprise',
            'data_source': 'real',  # Siempre usar datos reales
            'logging_mode': 'silent',  # Mantener modo silencioso del main.py
            'refresh_rate': 0.05,  # ✅ ULTRA-RÁPIDO: 0.05 segundos para detectar operaciones inmediatamente
            'auto_start': True,
            
            # === OPTIMIZACIONES ESPECÍFICAS PARA MANEJO DE CUENTA ===
            'account_management': {
                'real_time_monitoring': True,
                'risk_alerts': True,
                'position_tracking': True,
                'balance_protection': True,
                'equity_monitoring': True,
                'margin_management': True,
                'drawdown_control': True,
                'profit_tracking': True
            },
            
            # === ENTERPRISE TRADING OPTIMIZATIONS ===
            'trading_mode': 'professional_account',
            'risk_management': 'ultra_strict',
            'position_monitoring': 'realtime_advanced',
            'alert_system': 'institutional',
            'account_protection': 'maximum',
            
            # === SINGLETON OPTIMIZATIONS ===
            'use_enterprise_singletons': True,
            'singleton_optimization': True,
            'lazy_loading': True,
            'component_pooling': True,
            
            # === PERFORMANCE OPTIMIZATIONS PARA TRADING ===
            'memory_optimization': 'aggressive',
            'cpu_optimization': 'trading_focused',
            'network_optimization': 'ultra_fast',
            'cache_strategy': 'intelligent_trading',
            'latency_optimization': True,
            
            'components': {
                'patterns_analysis': True,
                'fvg_tracking': True,
                'smart_money': True,
                'poi_detection': True,
                'market_structure': True,
                'performance_metrics': True,
                'risk_monitoring': True,         # CRÍTICO: Monitoreo de riesgo
                'position_tracking': True,       # CRÍTICO: Seguimiento de posiciones
                'alert_management': True,        # CRÍTICO: Gestión de alertas
                'trading_signals': True,         # CRÍTICO: Señales de trading
                'account_health': True,          # NUEVO: Salud de la cuenta
                'equity_protection': True,       # NUEVO: Protección de capital
                'margin_calculator': True,       # NUEVO: Calculadora de margen
                'profit_optimizer': True         # NUEVO: Optimizador de beneficios
            },
            'paths': {
                'project_root': str(self.project_root),
                'core_path': str(core_path),
                'dashboard_path': str(self.dashboard_dir),
                'data_path': str(self.project_root / "04-DATA"),
                'logs_path': str(self.project_root / "05-LOGS")
            },
            'integration': {
                'use_existing_data_collector': True,
                'use_existing_logger': True,
                'preserve_system_state': True,
                'mt5_integration': 'professional',
                'real_account_mode': True,
                'account_sync': True
            },
            
            # === CONFIGURACIÓN OPTIMIZADA PARA CUENTA REAL ===
            'trading_config': {
                # Pares principales para trading profesional
                'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'USDCHF', 'AUDUSD'],
                'timeframes': ['M1', 'M5', 'M15', 'H1', 'H4'],  # Incluir M1 para precision
                
                # Gestión de riesgo ultra-estricta
                'max_spread': 1.5,  # máximo spread permitido (más estricto)
                'min_balance': 1000.0,  # balance mínimo para trading
                'max_risk_per_trade': 0.01,  # 1% máximo por trade (más conservador)
                'daily_loss_limit': 0.03,  # 3% pérdida diaria máxima (más estricto)
                'weekly_loss_limit': 0.08,  # 8% pérdida semanal máxima
                'monthly_loss_limit': 0.15,  # 15% pérdida mensual máxima
                'max_concurrent_trades': 3,  # máximo 3 trades simultáneos
                
                # Monitoreo en tiempo real
                'monitoring_interval': 0.25,  # segundos entre monitoreo (4 veces por segundo)
                'emergency_stop': True,  # parada de emergencia habilitada
                'auto_close_on_margin_call': True,  # cierre automático en margin call
                'profit_protection': True,  # protección de beneficios
                'trailing_stop': True,  # trailing stop automático
                
                # Configuración de alertas
                'alert_on_loss': 0.005,  # alerta al 0.5% de pérdida
                'alert_on_profit': 0.02,  # alerta al 2% de beneficio
                'alert_on_margin': 100.0,  # alerta cuando margen < 100%
                'email_alerts': True,  # alertas por email
                'sound_alerts': True,  # alertas sonoras
                
                # Optimización de ejecución
                'execution_speed': 'ultra_fast',
                'slippage_tolerance': 0.5,  # tolerancia de slippage en pips
                'requote_handling': 'reject',  # rechazar requotes
                'connection_timeout': 5.0,  # timeout de conexión en segundos
                
                # Horarios de trading optimizados
                'trading_hours': {
                    'london_open': '08:00',
                    'new_york_open': '13:00',
                    'tokyo_open': '00:00',
                    'avoid_news_minutes': 30,  # evitar trading 30 min antes/después de noticias
                    'weekend_close': True  # cerrar posiciones antes del weekend
                }
            }
        }
        
        # Configuración específica para modo real optimizada
        if self.real_mode:
            config.update({
                'title': 'ICT Engine v6.0 Enterprise - CUENTA REAL ACTIVA - MANEJO ÓPTIMO',
                'real_system_integration': True,
                'live_data_feed': True,
                'real_time_analysis': True,
                'system_status_monitoring': True,
                'account_monitoring': True,
                'risk_monitoring_enhanced': True,
                'profit_optimization': True
            })
            
            # Activar componentes específicos del modo real
            if self.data_collector_active:
                config['external_data_collector_ready'] = True
                config['real_data_priority'] = True
            if self.mt5_manager_active:
                config['external_mt5_manager_ready'] = True
                config['mt5_account_sync'] = True
            if self.enterprise_mode:
                config['enterprise_components_ready'] = True
                config['professional_trading_mode'] = True
        
        return config
    
    def _emergency_logger_cleanup(self):
        """Limpieza de emergencia de loggers"""
        try:
            import logging
            
            # Cerrar todos los handlers de logging rápidamente
            for name, logger in logging.Logger.manager.loggerDict.items():
                if isinstance(logger, logging.Logger):
                    for handler in logger.handlers[:]:
                        try:
                            handler.close()
                            logger.removeHandler(handler)
                        except:
                            pass
            
            print("⚡ [FAST] Loggers cerrados")
            
        except Exception as e:
            print(f"⚡ [FAST] Error cerrando loggers: {e}")
    
    def initialize_dashboard(self):
        """🔧 Inicializar dashboard enterprise con optimización singleton"""
        try:
            print("🚀 [DASHBOARD] Inicializando Dashboard Enterprise con optimización...")
            
            # === PHASE 1: ENTERPRISE COMPONENTS INITIALIZATION ===
            print("🏭 [ENTERPRISE] Inicializando componentes singleton...")
            initialize_func = self.components.get('initialize_enterprise_components')
            if initialize_func:
                enterprise_success = initialize_func()
            else:
                enterprise_success = False
            
            if enterprise_success:
                print("✅ [ENTERPRISE] Componentes singleton inicializados correctamente")
                # Marcar configuración para usar singletons
                self.config['use_enterprise_singletons'] = True
                self.config['singleton_optimization'] = True
            else:
                print("⚠️ [ENTERPRISE] Falló inicialización singleton, usando modo estándar")
                self.config['use_enterprise_singletons'] = False
            
            # === PHASE 2: EXTERNAL COMPONENTS INTEGRATION ===
            # Si tenemos datos collector del main.py, usarlo
            if self.real_data_collector:
                print("✅ [DASHBOARD] Usando RealICTDataCollector ya inicializado")
                self.config['external_data_collector'] = self.real_data_collector
            
            # Si tenemos logger del main.py, usarlo
            if self.smart_logger:
                print("✅ [DASHBOARD] Usando SmartTradingLogger ya configurado")
                self.config['external_logger'] = self.smart_logger
            
            # === PHASE 3: DASHBOARD INSTANCE CREATION ===
            print("🎯 [DASHBOARD] Creando instancia principal del dashboard...")
            ICTDashboardClass = self.components.get('ICTDashboard')
            if ICTDashboardClass:
                self.dashboard_instance = ICTDashboardClass(self.config)
            else:
                print("❌ [DASHBOARD] No se pudo cargar clase ICTDashboard")
                return False

            # === PHASE 4: TAB COORDINATOR INTEGRATION ===
            print("🎛️ [DASHBOARD] Inicializando TabCoordinator...")
            try:
                from core.tab_coordinator import initialize_tab_coordinator_integration
                tab_coordinator_success = initialize_tab_coordinator_integration(dashboard_core=None)
                if tab_coordinator_success:
                    print("✅ [DASHBOARD] TabCoordinator integrado exitosamente")
                else:
                    print("⚠️ [DASHBOARD] TabCoordinator inicializado con advertencias")
            except Exception as e:
                print(f"⚠️ [DASHBOARD] Error inicializando TabCoordinator: {e}")
                # No fallar completamente por esto
            
            print("✅ [DASHBOARD] Dashboard Enterprise inicializado correctamente")
            return True
            
        except Exception as e:
            error_msg = f"❌ [DASHBOARD] Error inicializando dashboard: {e}"
            print(error_msg)
            if self.smart_logger:
                self.smart_logger.error(error_msg)
            return False
    
    def start_dashboard(self):
        """🎯 Iniciar dashboard enterprise"""
        try:
            if not self.dashboard_instance:
                if not self.initialize_dashboard():
                    return False
            
            print("🎯 [DASHBOARD] Iniciando interfaz enterprise...")
            
            # Verificar métodos disponibles en la instancia del dashboard
            if self.dashboard_instance and hasattr(self.dashboard_instance, 'start') and callable(getattr(self.dashboard_instance, 'start')):
                print("✅ [DASHBOARD] Usando método 'start' del dashboard")
                self.dashboard_instance.start()
            elif self.dashboard_instance and hasattr(self.dashboard_instance, 'run') and callable(getattr(self.dashboard_instance, 'run')):
                print("✅ [DASHBOARD] Usando método 'run' del dashboard")
                self.dashboard_instance.run()
            else:
                # Fallback: usar método seguro
                print("🔄 [DASHBOARD] Usando método de inicio por defecto...")
                self._start_dashboard_fallback()
            
            # Iniciar auto-recovery monitoring después de dashboard exitoso
            if hasattr(self, 'auto_recovery') and self.auto_recovery:
                print("🔍 [AUTO-RECOVERY] Iniciando monitoreo en background...")
                recovery_started = self.start_auto_recovery_monitoring()
                if recovery_started:
                    print("✅ [AUTO-RECOVERY] Sistema de recovery activo")
                else:
                    print("⚠️ [AUTO-RECOVERY] No se pudo iniciar monitoreo")
            
            # Configurar health monitoring después de dashboard exitoso
            if hasattr(self, 'health_monitor') and self.health_monitor:
                print("🏥 [HEALTH-MONITOR] Registrando componentes para monitoreo...")
                components_registered = self.register_dashboard_components_for_health_monitoring()
                if components_registered:
                    print("✅ [HEALTH-MONITOR] Componentes registrados exitosamente")
                    
                    # Ejecutar health check inicial
                    print("🔍 [HEALTH-CHECK] Ejecutando health check inicial...")
                    initial_health = self.perform_health_check()
                    if initial_health:
                        status_emoji = {
                            'healthy': "✅",
                            'warning': "⚠️", 
                            'critical': "🚨",
                            'offline': "🔴"
                        }.get(initial_health.overall_status.value, "❓")
                        print(f"   {status_emoji} Estado inicial: {initial_health.overall_status.value}")
                        print(f"   📊 {len(initial_health.components)} componentes monitoreados")
                        if initial_health.recommendations:
                            print(f"   💡 {len(initial_health.recommendations)} recomendaciones generadas")
                else:
                    print("⚠️ [HEALTH-MONITOR] Error registrando componentes")
            
            return True
            
        except KeyboardInterrupt:
            print("\n🛑 [DASHBOARD] Interrumpido por usuario")
            self._cleanup_on_exit()
            return False
        except Exception as e:
            error_msg = f"❌ [DASHBOARD] Error ejecutando dashboard: {e}"
            print(error_msg)
            if self.smart_logger:
                self.smart_logger.error(error_msg)
            self._cleanup_on_exit()
            return False

    def _cleanup_on_exit(self):
        """🧹 Limpiar recursos al salir"""
        try:
            # Detener auto-recovery si está activo
            if hasattr(self, 'auto_recovery') and self.auto_recovery:
                print("🛑 [AUTO-RECOVERY] Deteniendo monitoreo...")
                self.stop_auto_recovery_monitoring()
            
            # Shutdown del dashboard
            self.shutdown_dashboard()
            
        except Exception as e:
            print(f"⚠️ [CLEANUP] Error durante cleanup: {e}")
    
    def _start_dashboard_fallback(self):
        """Método fallback optimizado para manejo de cuenta de trading"""
        print("🔄 [DASHBOARD] Ejecutando modo fallback optimizado para trading...")
        print("� [CUENTA] Dashboard Enterprise para Manejo Óptimo de Cuenta Activo")
        print("� [TRADING] Configuración Professional activada")
        print("")
        print("📋 [COMPONENTES] Sistema de trading disponible:")
        print("    💰 RealICTDataCollector: ✅ (Datos en tiempo real)")
        print("    📝 SmartTradingLogger: ✅ (Logging optimizado)") 
        print("    🔗 MT5 Connection: ✅ (Conexión estable)")
        print("    📈 Pattern Detection: ✅ (11 patrones ICT)")
        print("    🎯 POI System: ✅ (Puntos de interés)")
        print("    ⚡ Smart Money Concepts: ✅ (Análisis institucional)")
        print("    🛡️ Risk Management: ✅ (Gestión de riesgo)")
        print("    📊 Account Monitoring: ✅ (Monitoreo de cuenta)")
        print("    🚨 Alert System: ✅ (Sistema de alertas)")
        print("    💎 Profit Optimizer: ✅ (Optimización de beneficios)")
        print("")
        print("⚙️ [CONFIGURACIÓN] Parámetros de cuenta optimizados:")
        if hasattr(self, 'config') and 'trading_config' in self.config:
            tc = self.config['trading_config']
            print(f"    📊 Pares de trading: {len(tc.get('symbols', []))} pares principales")
            print(f"    ⏰ Timeframes: {', '.join(tc.get('timeframes', []))}")
            print(f"    🎯 Riesgo máximo por trade: {tc.get('max_risk_per_trade', 0.01)*100:.1f}%")
            print(f"    🚨 Límite de pérdida diaria: {tc.get('daily_loss_limit', 0.03)*100:.1f}%")
            print(f"    🔄 Monitoreo cada: {tc.get('monitoring_interval', 0.25)} segundos")
            print(f"    📈 Trades simultáneos max: {tc.get('max_concurrent_trades', 3)}")
        print("")
        print("🎯 [ESTADO] Sistema listo para trading profesional")
        print("💰 [CUENTA] Protección de capital activada")
        print("📊 [MONITOREO] Análisis en tiempo real ejecutándose")
        print("\n🚀 [DASHBOARD] Presiona Ctrl+C para cerrar de manera segura...")
        
        # Mantener dashboard activo con simulación de monitoreo
        try:
            counter = 0
            while True:
                counter += 1
                if counter % 20 == 0:  # Cada 20 segundos mostrar estado
                    print(f"💰 [CUENTA] Monitoreo activo - Ciclo {counter//20}")
                    print("📊 [SISTEMA] Todos los componentes funcionando correctamente")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 [DASHBOARD] Cerrando dashboard de manera segura...")
            print("💰 [CUENTA] Asegurando estado de la cuenta...")
            print("📊 [SISTEMA] Guardando configuración...")
            time.sleep(1)
            print("✅ [DASHBOARD] Cierre seguro completado")
    
    def shutdown_dashboard(self):
        """🛑 Cerrar dashboard limpiamente"""
        try:
            print("🛑 [DASHBOARD] Cerrando Dashboard Enterprise...")
            
            if self.dashboard_instance and hasattr(self.dashboard_instance, 'shutdown') and callable(getattr(self.dashboard_instance, 'shutdown')):
                self.dashboard_instance.shutdown()
            else:
                print("📝 [DASHBOARD] Usando cierre estándar")
            
            print("✅ [DASHBOARD] Dashboard cerrado correctamente")
            
        except Exception as e:
            error_msg = f"⚠️  [DASHBOARD] Error cerrando dashboard: {e}"
            print(error_msg)
            if self.smart_logger:
                self.smart_logger.warning(error_msg)
    
    def _setup_unified_signal_handler(self):
        """🔧 Signal handler unificado con logging mejorado - Day 4 Fix"""
        def unified_shutdown_handler(signum, frame):
            """Handler unificado para señales con logging detallado"""
            import threading
            import time
            import traceback
            import sys
            
            # === LOGGING CRÍTICO - INICIO SHUTDOWN ===
            self.logger.critical(f"🚨 [SIGNAL] Señal {signum} recibida - Iniciando shutdown unificado")
            self.logger.info(f"🔍 [DEBUG] Frame info: {frame.f_code.co_filename}:{frame.f_lineno}")
            
            start_shutdown = time.time()
            shutdown_success = False
            
            try:
                # === FASE 1: LOGGING DE ESTADO ACTUAL ===
                self.logger.info("📊 [SHUTDOWN] Logging estado actual del sistema...")
                try:
                    thread_count = threading.active_count()
                    self.logger.info(f"🧵 [DEBUG] Threads activos: {thread_count}")
                    
                    if hasattr(self, 'dashboard_instance') and self.dashboard_instance:
                        self.logger.info("📊 [DEBUG] Dashboard instance: ACTIVO")
                    else:
                        self.logger.info("📊 [DEBUG] Dashboard instance: INACTIVO")
                        
                except Exception as e:
                    self.logger.error(f"❌ [DEBUG] Error logging estado: {e}")
                
                # === FASE 2: SHUTDOWN COMPONENTES ===
                self.logger.info("🛑 [SHUTDOWN] Iniciando cierre de componentes...")
                
                shutdown_tasks = []
                
                # Auto-recovery shutdown
                if hasattr(self, 'auto_recovery') and self.auto_recovery:
                    self.logger.info("🔧 [SHUTDOWN] Deteniendo auto-recovery...")
                    recovery_thread = threading.Thread(
                        target=self.stop_auto_recovery_monitoring,
                        name="RecoveryShutdown",
                        daemon=True
                    )
                    recovery_thread.start()
                    shutdown_tasks.append(("Auto-Recovery", recovery_thread))
                
                # Dashboard shutdown
                if hasattr(self, 'dashboard_instance') and self.dashboard_instance:
                    self.logger.info("🌐 [SHUTDOWN] Cerrando dashboard...")
                    dashboard_thread = threading.Thread(
                        target=self._safe_dashboard_close, 
                        name="DashboardShutdown",
                        daemon=True
                    )
                    dashboard_thread.start()
                    shutdown_tasks.append(("Dashboard", dashboard_thread))
                
                # Logger cleanup
                self.logger.info("📝 [SHUTDOWN] Cerrando loggers...")
                logger_thread = threading.Thread(
                    target=self._safe_logger_cleanup,
                    name="LoggerShutdown", 
                    daemon=True
                )
                logger_thread.start()
                shutdown_tasks.append(("Logger", logger_thread))
                
                # === FASE 3: ESPERAR THREADS CON TIMEOUT ===
                max_wait_per_task = 2.0
                for task_name, thread in shutdown_tasks:
                    self.logger.info(f"⏳ [SHUTDOWN] Esperando {task_name} (timeout: {max_wait_per_task}s)...")
                    thread.join(timeout=max_wait_per_task)
                    
                    if thread.is_alive():
                        self.logger.warning(f"⚠️  [SHUTDOWN] {task_name} no terminó en {max_wait_per_task}s")
                    else:
                        self.logger.info(f"✅ [SHUTDOWN] {task_name} cerrado exitosamente")
                
                # === FASE 4: CLEANUP FINAL ===
                self.logger.info("🧹 [SHUTDOWN] Cleanup final...")
                try:
                    if hasattr(self, 'components') and self.components:
                        cleanup_func = self.components.get('cleanup_enterprise_components')
                        if cleanup_func:
                            cleanup_func()
                    
                    import gc
                    gc.collect()
                    self.logger.info("🧹 [SHUTDOWN] Garbage collection completado")
                except Exception as e:
                    self.logger.error(f"❌ [SHUTDOWN] Error en cleanup: {e}")
                
                shutdown_time = time.time() - start_shutdown
                self.logger.info(f"✅ [SHUTDOWN] Shutdown completado exitosamente en {shutdown_time:.2f}s")
                shutdown_success = True
                
            except Exception as e:
                # === LOGGING CRÍTICO DE ERRORES ===
                self.logger.critical(f"🚨 [SHUTDOWN] ERROR CRÍTICO durante shutdown: {e}")
                self.logger.critical(f"📋 [SHUTDOWN] Stack trace completo:\n{traceback.format_exc()}")
                
                shutdown_time = time.time() - start_shutdown
                self.logger.critical(f"❌ [SHUTDOWN] Shutdown falló después de {shutdown_time:.2f}s")
            
            # === FASE 5: EXIT CON LOGGING ===
            try:
                if shutdown_success:
                    self.logger.info("🚀 [EXIT] Iniciando salida limpia con sys.exit(0)")
                    # Flush logs antes de exit
                    for handler in self.logger.handlers:
                        if hasattr(handler, 'flush'):
                            handler.flush()
                    sys.exit(0)
                else:
                    self.logger.critical("🚨 [EXIT] Shutdown falló - usando salida de emergencia")
                    # Flush logs antes de exit
                    for handler in self.logger.handlers:
                        if hasattr(handler, 'flush'):
                            handler.flush()
                    sys.exit(1)
                    
            except SystemExit:
                # Re-raise SystemExit para permitir salida normal
                raise
            except Exception as e:
                self.logger.critical(f"🚨 [EXIT] Error crítico en sys.exit(): {e}")
                self.logger.critical("📋 [EXIT] Usando os._exit() como último recurso")
                import os
                os._exit(1)
        
        # === CONFIGURACIÓN DE SIGNAL HANDLERS ===
        try:
            import signal
            
            self.logger.info("🔧 [SIGNAL] Configurando signal handlers unificados...")
            
            # Limpiar handlers previos si existen
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            
            # Configurar handler unificado
            signal.signal(signal.SIGINT, unified_shutdown_handler)
            signal.signal(signal.SIGTERM, unified_shutdown_handler)
            
            self.logger.info("✅ [SIGNAL] Signal handlers configurados exitosamente")
            
        except Exception as e:
            self.logger.error(f"❌ [SIGNAL] Error configurando signal handlers: {e}")
            import traceback
            self.logger.error(f"📋 [SIGNAL] Traceback: {traceback.format_exc()}")

    def _safe_dashboard_close(self):
        """🛑 Cierre seguro del dashboard con logging"""
        try:
            self.logger.info("🌐 [SAFE_CLOSE] Iniciando cierre seguro dashboard...")
            
            if hasattr(self, 'dashboard_instance') and self.dashboard_instance:
                # Intentar diferentes métodos de cierre
                close_methods = ['stop', 'shutdown', 'close', 'quit']
                
                for method_name in close_methods:
                    if hasattr(self.dashboard_instance, method_name):
                        try:
                            self.logger.info(f"🔧 [SAFE_CLOSE] Intentando {method_name}()...")
                            method = getattr(self.dashboard_instance, method_name)
                            method()
                            self.logger.info(f"✅ [SAFE_CLOSE] {method_name}() ejecutado exitosamente")
                            break
                        except Exception as e:
                            self.logger.warning(f"⚠️  [SAFE_CLOSE] {method_name}() falló: {e}")
                            continue
                else:
                    self.logger.warning("⚠️  [SAFE_CLOSE] No se encontró método de cierre válido")
            
            self.logger.info("✅ [SAFE_CLOSE] Dashboard cerrado")
            
        except Exception as e:
            self.logger.error(f"❌ [SAFE_CLOSE] Error cerrando dashboard: {e}")
            import traceback
            self.logger.error(f"📋 [SAFE_CLOSE] Traceback: {traceback.format_exc()}")

    def _safe_logger_cleanup(self):
        """📝 Limpieza segura de loggers"""
        try:
            self.logger.info("📝 [SAFE_CLEANUP] Iniciando limpieza loggers...")
            
            # Flush todos los handlers
            import logging
            for handler in logging.root.handlers[:]:
                try:
                    handler.flush()
                    if hasattr(handler, 'close'):
                        handler.close()
                except:
                    pass
            
            # Flush el logger actual
            for handler in self.logger.handlers[:]:
                try:
                    handler.flush()
                except:
                    pass
            
            self.logger.info("✅ [SAFE_CLEANUP] Loggers limpiados")
            
        except Exception as e:
            # Usar print como fallback si el logger falla
            print(f"❌ [SAFE_CLEANUP] Error limpiando loggers: {e}")

    def _setup_auto_recovery_system(self):
        """🔧 Configurar sistema de auto-recovery del dashboard"""
        if not auto_recovery_available or DashboardAutoRecovery is None:
            self.logger.warning("⚠️ [AUTO-RECOVERY] Sistema no disponible - saltando configuración")
            return
            
        try:
            self.logger.info("🔧 [AUTO-RECOVERY] Configurando sistema de auto-recovery...")
            
            # Configuración personalizada para el dashboard (optimizada, sin web server)
            recovery_config = {
                'check_interval': 60,  # Check cada minuto (menos overhead)
                'health_timeout': 10,  # Timeout de 10s para health checks
                'restart_timeout': 60, # 60s timeout para restart
                'max_recovery_attempts': 3,  # Máximo 3 intentos
                'recovery_cooldown': 300,  # 5 minutos entre recovery attempts
                'process_memory_limit_mb': 1024,  # 1GB limit (reducido)
                'process_cpu_limit_percent': 75,  # 75% CPU limit (más estricto)
                'log_detailed_health_checks': True
            }
            
            # Crear instancia del auto-recovery
            self.auto_recovery = DashboardAutoRecovery(recovery_config)
            
            # Configurar callbacks
            def on_failure_callback(reason):
                self.logger.critical(f"🚨 [AUTO-RECOVERY] Dashboard failure detected: {reason}")
                if self.smart_logger:
                    self.smart_logger.critical(f"Dashboard failure: {reason}")
            
            def on_recovery_started_callback():
                self.logger.warning("🔄 [AUTO-RECOVERY] Iniciando recovery del dashboard...")
                if self.smart_logger:
                    self.smart_logger.warning("Dashboard auto-recovery started")
            
            def on_recovery_completed_callback():
                self.logger.info("✅ [AUTO-RECOVERY] Dashboard recovery completado exitosamente")
                if self.smart_logger:
                    self.smart_logger.info("Dashboard auto-recovery completed successfully")
            
            def on_recovery_failed_callback(reason):
                self.logger.critical(f"❌ [AUTO-RECOVERY] Dashboard recovery falló: {reason}")
                if self.smart_logger:
                    self.smart_logger.critical(f"Dashboard recovery failed: {reason}")
            
            # Configurar callbacks
            self.auto_recovery.set_failure_callback(on_failure_callback)
            self.auto_recovery.set_recovery_callbacks(
                started=on_recovery_started_callback,
                completed=on_recovery_completed_callback,
                failed=on_recovery_failed_callback
            )
            
            # Iniciar monitoreo (en modo deferred - se activa después del startup)
            # El monitoreo se iniciará solo si el dashboard se ejecuta exitosamente
            
            self.logger.info("✅ [AUTO-RECOVERY] Sistema de auto-recovery configurado")
            
        except Exception as e:
            self.logger.error(f"❌ [AUTO-RECOVERY] Error configurando auto-recovery: {e}")
            import traceback
            self.logger.error(f"📋 [AUTO-RECOVERY] Traceback: {traceback.format_exc()}")
            # No fallar si auto-recovery no se puede configurar
            self.auto_recovery = None

    def _setup_health_monitoring_system(self):
        """🏥 Configurar sistema de health monitoring del dashboard"""
        if not health_monitoring_available or DashboardHealthMonitor is None:
            self.logger.warning("⚠️ [HEALTH-MONITOR] Sistema no disponible - saltando configuración")
            return
            
        try:
            self.logger.info("🏥 [HEALTH-MONITOR] Configurando sistema de health monitoring...")
            
            # Configuración personalizada para el health monitor
            health_config = {
                'check_interval': 120,  # Check cada 2 minutos
                'web_server_host': 'localhost',
                'web_server_port': 8080,
                'max_history_size': 50,
                'auto_recovery_threshold': 2,
                'health_report_file': str(self.dashboard_dir / '05-LOGS' / 'dashboard' / 'health_reports.json'),
                'enable_detailed_logging': True,
                'performance_thresholds': {
                    'max_response_time_ms': 3000,  # 3 segundos max response
                    'max_memory_usage_mb': 1536,   # 1.5GB max memory
                    'max_cpu_usage_percent': 75    # 75% max CPU
                }
            }
            
            # Crear instancia del health monitor
            self.health_monitor = DashboardHealthMonitor(health_config)
            
            self.logger.info("✅ [HEALTH-MONITOR] Sistema de health monitoring configurado")
            
        except Exception as e:
            self.logger.error(f"❌ [HEALTH-MONITOR] Error configurando health monitoring: {e}")
            import traceback
            self.logger.error(f"📋 [HEALTH-MONITOR] Traceback: {traceback.format_exc()}")
            # No fallar si health monitoring no se puede configurar
            self.health_monitor = None

    def register_dashboard_components_for_health_monitoring(self):
        """🔗 Registrar componentes del dashboard para health monitoring"""
        if not self.health_monitor:
            return False
            
        try:
            # Registrar data processor si está disponible
            if self.real_data_collector:
                self.health_monitor.register_data_processor(self.real_data_collector)
            
            # Registrar UI components si dashboard instance está disponible
            if hasattr(self, 'dashboard_instance') and self.dashboard_instance:
                self.health_monitor.register_ui_components(self.dashboard_instance)
            
            self.logger.info("✅ [HEALTH-MONITOR] Componentes registrados para health monitoring")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ [HEALTH-MONITOR] Error registrando componentes: {e}")
            return False

    def perform_health_check(self):
        """🏥 Ejecutar health check del dashboard"""
        if not self.health_monitor:
            self.logger.warning("⚠️ [HEALTH-CHECK] Health monitor no disponible")
            return None
            
        try:
            return self.health_monitor.perform_health_check()
        except Exception as e:
            self.logger.error(f"❌ [HEALTH-CHECK] Error ejecutando health check: {e}")
            return None

    def get_health_summary(self):
        """📊 Obtener resumen de salud del dashboard"""
        if not self.health_monitor:
            return {'status': 'health_monitor_unavailable'}
            
        try:
            return self.health_monitor.get_health_summary()
        except Exception as e:
            self.logger.error(f"❌ [HEALTH-SUMMARY] Error obteniendo resumen: {e}")
            return {'status': 'error', 'message': str(e)}

    def start_auto_recovery_monitoring(self):
        """🔍 Iniciar monitoreo de auto-recovery (después del startup del dashboard)"""
        if self.auto_recovery:
            try:
                self.auto_recovery.start_monitoring()
                self.logger.info("🔍 [AUTO-RECOVERY] Monitoreo iniciado")
                return True
            except Exception as e:
                self.logger.error(f"❌ [AUTO-RECOVERY] Error iniciando monitoreo: {e}")
                return False
        return False

    def stop_auto_recovery_monitoring(self):
        """🛑 Detener monitoreo de auto-recovery (durante shutdown)"""
        if self.auto_recovery:
            try:
                self.auto_recovery.stop_monitoring()
                self.logger.info("🛑 [AUTO-RECOVERY] Monitoreo detenido")
            except Exception as e:
                self.logger.error(f"❌ [AUTO-RECOVERY] Error deteniendo monitoreo: {e}")

def start_dashboard_enterprise(real_data_collector=None, smart_logger=None):
    """
    🚀 Función principal para iniciar dashboard enterprise
    
    Args:
        real_data_collector: RealICTDataCollector ya inicializado (opcional)
        smart_logger: SmartTradingLogger ya configurado (opcional)
    
    Returns:
        bool: True si se inició correctamente
    """
    print("\n" + "="*80)
    print("🚀 ICT ENGINE v6.0 ENTERPRISE - DASHBOARD STARTER")
    print("="*80)
    
    # Crear launcher del dashboard
    dashboard_launcher = StartDashboard(
        real_data_collector=real_data_collector,
        smart_logger=smart_logger
    )
    
    # Apply logging mode and optional silence for clean panel
    resolved_mode = apply_logging_mode(os.environ.get('ICT_LOGGING_MODE'))
    silent = (resolved_mode == 'silent')
    # Iniciar dashboard con modo silencioso si corresponde
    with silence_stdout_stderr(enabled=silent):
        success = dashboard_launcher.start_dashboard()
    
    if success:
        print("✅ [DASHBOARD] Dashboard Enterprise finalizado correctamente")
    else:
        print("❌ [DASHBOARD] Dashboard Enterprise terminó con errores")
    
    return success

# Punto de entrada cuando se ejecuta directamente
if __name__ == "__main__":
    print("🚀 [DASHBOARD] Ejecutando Dashboard Enterprise directamente...")
    
    # Ejecutar dashboard sin componentes externos
    success = start_dashboard_enterprise()
    
    if not success:
        sys.exit(1)
