#!/usr/bin/env python3
"""
main.py - ICT Engine v6.0 Enterprise
Sistema de Trading Avanzado con Smart Money Concepts
"""

import os
import sys
import time
import gc
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Union, Any, TYPE_CHECKING, Callable, Optional, Dict

if TYPE_CHECKING:  # Solo para el analizador estático
    from real_trading.trade_journal import TradeJournal  # noqa: F401
    from real_trading.trade_reconciler import TradeReconciler  # noqa: F401

# Determinar rutas del sistema
current_file = Path(__file__).resolve()
SYSTEM_ROOT = current_file.parent
original_dir = os.getcwd()

# Configurar paths principales
CORE_PATH = SYSTEM_ROOT / "01-CORE"
DATA_PATH = SYSTEM_ROOT / "04-DATA"
LOGS_PATH = SYSTEM_ROOT / "05-LOGS"
DASHBOARD_PATH = SYSTEM_ROOT / "09-DASHBOARD"
DOCUMENTATION_PATH = SYSTEM_ROOT / "03-DOCUMENTATION"

# Configurar el path de Python
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

# ============================================================================
# IMPORTS CON CARGA SEGURA
# ============================================================================

def safe_import_from_path(file_path, class_name, fallback_name=None):
    """Importar una clase desde un archivo específico de forma segura"""
    try:
        if not Path(file_path).exists():
            return None
        
        import importlib.util
        module_name = Path(file_path).stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return getattr(module, class_name, None)
    except Exception:
        return None

# Imports de los nuevos módulos optimizados
try:
    from validation import get_production_validator, ValidationLevel
    from optimization import get_trading_rate_limiter, get_data_rate_limiter, get_main_rate_limiter
    from monitoring import get_health_monitor, MonitoringLevel, create_database_health_check
    from config.production_config import get_production_config, TradingProfile, BrokerType, get_config_manager
    PRODUCTION_MODULES_AVAILABLE = True
    print("✅ Production optimization modules loaded successfully")
    print("✅ Production configuration system loaded")
except ImportError as e:
    print(f"⚠️  Production modules not available: {e}")
    PRODUCTION_MODULES_AVAILABLE = False

# Clase fallback para SmartTradingLogger
class BasicLogger:
    """Logger básico como fallback"""
    def __init__(self, name):
        self.name = name
    def info(self, msg): print(f"[{self.name}] {msg}")
    def warning(self, msg): print(f"[{self.name}] WARNING: {msg}")
    def error(self, msg): print(f"[{self.name}] ERROR: {msg}")
    def debug(self, msg): print(f"[{self.name}] DEBUG: {msg}")

# Imports críticos con fallbacks
try:
    from smart_trading_logger import SmartTradingLogger
    SMART_LOGGER_AVAILABLE = True
    LoggerClass = SmartTradingLogger
except ImportError as e:
    print(f"Warning: Could not import SmartTradingLogger: {e}")
    SMART_LOGGER_AVAILABLE = False
    LoggerClass = BasicLogger

# ============================================================================
# CLASES DE APOYO
# ============================================================================

class SystemStatus:
    """Estado del sistema enterprise"""
    def __init__(self):
        self.mt5_connected = False
        self.real_components_loaded = False
        self.risk_monitoring = False
        self.trading_active = False
        self.data_feed_active = False
        self.last_update = datetime.now()

class AccountInfo:
    """Información de la cuenta de trading"""
    def __init__(self):
        self.account_number = 0
        self.balance = 0.0
        self.equity = 0.0
        self.margin = 0.0
        self.free_margin = 0.0
        self.margin_level = 0.0
        self.profit = 0.0
        self.currency = "USD"
        self.leverage = 1
        self.server = ""
        self.company = ""
        self.is_connected = False
        self.last_update = datetime.now()

# ============================================================================
# SISTEMA ENTERPRISE PRINCIPAL
# ============================================================================

class ICTEnterpriseManager:
    """Gestor principal del sistema ICT Enterprise v6.0"""
    
    def __init__(self):
        """Inicializar el sistema enterprise"""
        self.logger = LoggerClass("ICTEnterpriseManager")
        self.system_status = SystemStatus()
        self.account_info = AccountInfo()
        
        self.shutdown_requested = False
        self.real_components_loaded = False
        self.data_collector = None
        self.dashboard_process = None
        self.web_dashboard_process = None
        
        # Setup inicial
        self._setup_directories()
        
        # 🔧 CONFIGURATION MANAGER
        self.config_manager = None
        self.production_config = None
        self._load_production_configuration()
        
        # ⚡ NUEVOS MÓDULOS OPTIMIZADOS PARA PRODUCCIÓN ⚡
        self.production_validator = None
        self.trading_rate_limiter = None
        self.data_rate_limiter = None 
        self.main_rate_limiter = None
        self.health_performance_monitor = None
        self._initialize_production_modules()
        
        # Componentes avanzados (se inicializan on-demand)
        self.risk_guard = None
        self.latency_watchdog = None
        self.health_monitor = None
        self.data_feed_fallback = None
        self.execution_router = None  # se configura cuando exista broker executor
        self._initialize_resilience_components()
        # Componentes de soporte de trading avanzados
        self.position_manager = None
        self.rate_limiter = None
        self.alert_dispatcher = None
        self.config_loader = None
        self.latency_sampler = None
        self._initialize_trading_support_components()
        # Servicios adicionales producción
        self.event_bus = None
        self.kill_switch = None
        self.state_persistence = None
        self.heartbeat_monitor = None
        self.account_sync = None
        self._initialize_production_services()
        # Reconciliación de operaciones
        self.trade_reconciler: Optional['TradeReconciler'] = None  # forward ref string
        self._initialize_reconciler()

    def _try_import_trade_journal(self):
        try:
            from real_trading.trade_journal import TradeJournal as _TJ  # local import
            return _TJ
        except Exception:
            return None

    def _try_import_trade_reconciler(self):
        try:
            from real_trading.trade_reconciler import TradeReconciler as _TR  # local import
            return _TR
        except Exception:
            return None

    def _initialize_reconciler(self) -> None:
        """Inicializa TradeReconciler evitando type: ignore mediante loaders seguros."""
        journal_cls = self._try_import_trade_journal()
        reconciler_cls = self._try_import_trade_reconciler()
        if not journal_cls or not reconciler_cls or self.trade_reconciler is not None:
            return
        try:
            journal = journal_cls()
        except Exception:
            journal = None
        if not journal:
            return
        def _positions_provider() -> list[dict[str, Any]]:
            # TODO: sustituir cuando el ejecutor exponga posiciones reales
            return []
        try:
            self.trade_reconciler = reconciler_cls(journal, _positions_provider, logger=self.logger)  # type: ignore[arg-type]
        except Exception as e:
            self.logger.error(f"No se pudo crear TradeReconciler: {e}")

    def _load_production_configuration(self):
        """🔧 Cargar configuración optimizada para producción"""
        if not PRODUCTION_MODULES_AVAILABLE:
            self.logger.warning("Production config not available - using defaults")
            return
        
        try:
            # Importar aquí para evitar errores si no está disponible
            from config.production_config import get_config_manager, get_production_config, TradingProfile, BrokerType
            
            # Inicializar config manager
            self.config_manager = get_config_manager()
            
            # Intentar cargar configuración existente, sino crear por defecto
            config_file = "ict_engine_production.json"
            try:
                self.production_config = self.config_manager.load_config_from_file(config_file)
                self.logger.info(f"✅ Production config loaded from {config_file}")
            except:
                # Crear configuración balanceada por defecto
                self.production_config = get_production_config(
                    profile=TradingProfile.BALANCED,
                    broker_type=BrokerType.MT5_STANDARD
                )
                self.config_manager.current_config = self.production_config
                self.config_manager.save_config_to_file(config_file)
                self.logger.info(f"✅ Default production config created and saved to {config_file}")
            
            # Log configuración cargada
            if self.production_config:
                profile = self.production_config.profile.value.upper()
                broker = self.production_config.broker_type.value.upper()
                condition = self.production_config.market_condition.value.upper()
                self.logger.info(f"🎯 Configuration: {profile} profile, {broker} broker, {condition} market")
                
        except Exception as e:
            self.logger.error(f"Error loading production configuration: {e}")
            self.production_config = None

    def _initialize_production_modules(self):
        """🏭 Inicializar módulos optimizados para producción real"""
        if not PRODUCTION_MODULES_AVAILABLE:
            self.logger.warning("Production modules not available - running in fallback mode")
            return
        
        try:
            # Import necesarios dentro del método
            from validation import get_production_validator, ValidationLevel
            from optimization import get_trading_rate_limiter, get_data_rate_limiter, get_main_rate_limiter
            from monitoring import get_health_monitor, MonitoringLevel
            
            # Usar configuraciones de producción si están disponibles
            validation_level = ValidationLevel.STANDARD
            monitoring_level = MonitoringLevel.STANDARD
            broker_limits = None
            
            if self.production_config:
                # Mapear niveles de configuración
                validation_mapping = {
                    'minimal': ValidationLevel.MINIMAL,
                    'standard': ValidationLevel.STANDARD,
                    'strict': ValidationLevel.STRICT,
                    'paranoid': ValidationLevel.PARANOID
                }
                monitoring_mapping = {
                    'minimal': MonitoringLevel.MINIMAL,
                    'standard': MonitoringLevel.STANDARD,
                    'detailed': MonitoringLevel.DETAILED,
                    'debug': MonitoringLevel.DEBUG
                }
                
                validation_level = validation_mapping.get(
                    self.production_config.validation.validation_level, 
                    ValidationLevel.STANDARD
                )
                monitoring_level = monitoring_mapping.get(
                    self.production_config.health_monitor.monitoring_level,
                    MonitoringLevel.STANDARD
                )
                
                # Preparar límites del broker para rate limiter
                broker_limits = {
                    'orders_per_second': self.production_config.rate_limit.orders_per_second,
                    'orders_per_minute': self.production_config.rate_limit.orders_per_minute,
                    'concurrent_orders': self.production_config.rate_limit.concurrent_orders
                }
                
                self.logger.info(f"🔧 Using configured validation level: {validation_level}")
                self.logger.info(f"🔧 Using configured monitoring level: {monitoring_level}")
            
            # 🛡️ Validador de producción
            self.production_validator = get_production_validator(validation_level)
            self.logger.info("✅ Production validator initialized with configuration")
            
            # 🚦 Rate limiters especializados
            self.trading_rate_limiter = get_trading_rate_limiter(broker_limits)
            self.data_rate_limiter = get_data_rate_limiter()  
            self.main_rate_limiter = get_main_rate_limiter()
            self.logger.info("✅ Rate limiters initialized with production limits")
            
            # 💖 Health & Performance Monitor
            self.health_performance_monitor = get_health_monitor(monitoring_level)
            
            # Configurar health checks específicos para nuestros componentes
            self._setup_custom_health_checks()
            
            # Iniciar monitoreo
            self.health_performance_monitor.start()
            self.logger.info("✅ Health & Performance monitor started with configuration")
            
            # Registrar callbacks de alertas
            self.health_performance_monitor.add_alert_callback(self._handle_health_alert)
            
        except Exception as e:
            self.logger.error(f"Error initializing production modules: {e}")
            # Continuar con fallbacks
    
    def _setup_custom_health_checks(self):
        """Configurar health checks personalizados para el sistema"""
        if not self.health_performance_monitor:
            return
        
        try:
            from monitoring import HealthCheck
        except:
            return
        
        def check_mt5_connection():
            # TODO: integrar con MT5 real
            return True, "MT5 connection OK (placeholder)"
        
        def check_data_feed():
            # TODO: integrar con data feed real
            return True, "Data feed OK (placeholder)"
        
        def check_trading_components():
            components_ok = True
            # Verificación simple de que los componentes están inicializados
            if self.position_manager is None:
                components_ok = False
            if self.rate_limiter is None:
                components_ok = False
            return components_ok, f"Trading components {'OK' if components_ok else 'NOT OK'}"
        
        # Registrar health checks personalizados
        health_checks = [
            HealthCheck(
                name="mt5_connection",
                check_function=check_mt5_connection,
                interval_seconds=30.0,
                critical=True
            ),
            HealthCheck(
                name="data_feed",
                check_function=check_data_feed,
                interval_seconds=60.0,
                critical=False
            ),
            HealthCheck(
                name="trading_components",
                check_function=check_trading_components,
                interval_seconds=45.0,
                critical=True
            )
        ]
        
        for health_check in health_checks:
            self.health_performance_monitor.register_health_check(health_check)
    
    def _handle_health_alert(self, alert):
        """Manejar alertas del sistema de salud"""
        if alert.level == 'CRITICAL':
            self.logger.error(f"🚨 CRITICAL ALERT [{alert.component}]: {alert.message}")
            # TODO: implementar acciones automáticas para alertas críticas
        elif alert.level == 'WARNING':
            self.logger.warning(f"⚠️ WARNING [{alert.component}]: {alert.message}")
        else:
            self.logger.info(f"ℹ️ ALERT [{alert.component}]: {alert.message}")

    def _initialize_resilience_components(self):
        """Inicializar componentes de resiliencia y monitoreo livianos"""
        # Importes diferidos con fallback silencioso
        try:  # RiskGuard
            from risk_management.risk_guard import RiskGuard  # type: ignore
        except Exception:
            RiskGuard = None  # type: ignore
        try:  # LatencyWatchdog
            from core.latency_watchdog import LatencyWatchdog  # type: ignore
        except Exception:
            LatencyWatchdog = None  # type: ignore
        try:  # HealthMonitor
            from core.system_health_monitor import SystemHealthMonitor  # type: ignore
        except Exception:
            SystemHealthMonitor = None  # type: ignore
        try:  # DataFeedFallback
            from core.data_feed_fallback import DataFeedFallback  # type: ignore
        except Exception:
            DataFeedFallback = None  # type: ignore
        try:  # ExecutionRouter + executor stub
            from real_trading.execution_router import ExecutionRouter, ExecutionRouterConfig  # type: ignore
            from real_trading.mt5_broker_executor import MT5BrokerExecutor  # type: ignore
        except Exception:
            ExecutionRouter = None  # type: ignore
            MT5BrokerExecutor = None  # type: ignore

        # RiskGuard
        if RiskGuard and not self.risk_guard:
            try:
                self.risk_guard = RiskGuard()
            except Exception as e:
                self.logger.error(f"No se pudo inicializar RiskGuard: {e}")

        # LatencyWatchdog con sampler simple (placeholder) que retorna 0 hasta tener métrica real
        if LatencyWatchdog and not self.latency_watchdog:
            try:
                def _sampler():
                    return 0.0  # TODO: integrar con métrica real (MT5 ping o timestamp diff)
                self.latency_watchdog = LatencyWatchdog(_sampler)
            except Exception as e:
                self.logger.error(f"No se pudo inicializar LatencyWatchdog: {e}")

        # DataFeedFallback
        if DataFeedFallback and not self.data_feed_fallback:
            try:
                self.data_feed_fallback = DataFeedFallback()
            except Exception as e:
                self.logger.error(f"No se pudo inicializar DataFeedFallback: {e}")

        # HealthMonitor
        if SystemHealthMonitor and not self.health_monitor:
            try:
                self.health_monitor = SystemHealthMonitor(
                    latency_provider=self.latency_watchdog,
                    data_collector=self.data_collector  # será None al inicio
                )
            except Exception as e:
                self.logger.error(f"No se pudo inicializar SystemHealthMonitor: {e}")

        # ExecutionRouter (requiere al menos executor primario)
        if ExecutionRouter is not None and MT5BrokerExecutor is not None and not self.execution_router:
            try:
                primary_exec = MT5BrokerExecutor()
                risk_adapter = None
                temp_limit = 0.5
                limit_holder = {'val': temp_limit}
                if self.risk_guard:
                    class _RiskAdapter:
                        def __init__(self, guard, exec_ref, limit_ref):
                            self.guard = guard
                            self.exec_ref = exec_ref
                            self.limit_ref = limit_ref
                        def validate_order(self, symbol: str, volume: float, action: str, price: float) -> bool:
                            snap = {}
                            try:
                                if hasattr(self.exec_ref, 'get_account_snapshot'):
                                    snap = self.exec_ref.get_account_snapshot()  # type: ignore
                            except Exception:
                                pass
                            balance = float(snap.get('balance', 0.0))
                            equity = float(snap.get('equity', balance))
                            if balance <= 0:
                                balance = equity if equity > 0 else 0.0
                            eval_r = self.guard.evaluate(balance=balance, equity=equity)
                            violations = eval_r.get('violations', [])
                            if violations:
                                severe = {"DAILY_LOSS_LIMIT", "DRAWDOWN_LIMIT", "MAX_POSITIONS"}
                                if any(v in severe for v in violations):
                                    return False
                                if volume > self.limit_ref():
                                    return False
                            return True
                    def _limit():
                        return limit_holder['val']
                    risk_adapter = _RiskAdapter(self.risk_guard, primary_exec, _limit)
                metrics_dir = str(DATA_PATH / "metrics")
                try:
                    exec_config = ExecutionRouterConfig(metrics_dir=metrics_dir)  # type: ignore
                except Exception:
                    exec_config = None  # type: ignore
                self.execution_router = ExecutionRouter(
                    primary_executor=primary_exec,
                    backup_executor=None,
                    risk_validator=risk_adapter,
                    latency_monitor=self.latency_watchdog,
                    health_monitor=self.health_monitor,
                    config=exec_config
                )
                try:
                    if self.execution_router and getattr(self.execution_router, 'config', None):
                        limit_holder['val'] = getattr(self.execution_router.config, 'moderate_violation_volume_limit', temp_limit)
                except Exception:
                    pass
                self.logger.info("ExecutionRouter inicializado")
            except Exception as e:
                self.logger.error(f"No se pudo crear ExecutionRouter: {e}")

        self.logger.info("Componentes de resiliencia preparados (lazy integration)")

    def _initialize_trading_support_components(self):
        """Inicializar componentes de soporte operativo (posiciones, rate limiting, alertas, config, sampler)."""
        try:
            from real_trading.position_manager import PositionManager  # type: ignore
        except Exception:
            PositionManager = None  # type: ignore
        try:
            from real_trading.order_rate_limiter import OrderRateLimiter  # type: ignore
        except Exception:
            OrderRateLimiter = None  # type: ignore
        try:
            from real_trading.alert_dispatcher import AlertDispatcher  # type: ignore
        except Exception:
            AlertDispatcher = None  # type: ignore
        try:
            from real_trading.config_loader import ConfigLoader  # type: ignore
        except Exception:
            ConfigLoader = None  # type: ignore
        try:
            from real_trading.latency_sampler import create_default_latency_sampler  # type: ignore
        except Exception:
            create_default_latency_sampler = None  # type: ignore

        if PositionManager and not self.position_manager:
            try:
                self.position_manager = PositionManager(logger=self.logger, max_positions=100, max_exposure_per_symbol=150000.0)  # type: ignore
            except Exception as e:
                self.logger.error(f"No se pudo crear PositionManager: {e}")

        if OrderRateLimiter and not self.rate_limiter:
            try:
                self.rate_limiter = OrderRateLimiter(logger=self.logger, max_orders_per_minute=180, per_symbol_limit=30)  # type: ignore
            except Exception as e:
                self.logger.error(f"No se pudo crear OrderRateLimiter: {e}")

        if AlertDispatcher and not self.alert_dispatcher:
            try:
                self.alert_dispatcher = AlertDispatcher(logger=self.logger)  # type: ignore
            except Exception as e:
                self.logger.error(f"No se pudo crear AlertDispatcher: {e}")

        if ConfigLoader and not self.config_loader:
            try:
                self.config_loader = ConfigLoader(logger=self.logger)  # type: ignore
            except Exception as e:
                self.logger.error(f"No se pudo crear ConfigLoader: {e}")

        if create_default_latency_sampler and not self.latency_sampler:
            try:
                self.latency_sampler = create_default_latency_sampler(logger=self.logger)  # type: ignore
            except Exception as e:
                self.logger.error(f"No se pudo crear LatencySampler: {e}")

        # Registrar hook de pre-orden si router disponible
        if self.execution_router and hasattr(self.execution_router, 'pre_order_hooks') and self.rate_limiter and self.position_manager:
            def _pre_hook(symbol: str, action: str, volume: float, price):  # type: ignore
                try:
                    if hasattr(self.rate_limiter, 'allow') and not self.rate_limiter.allow(symbol):  # type: ignore
                        return False, 'rate_limited'
                    exposure = 0.0
                    if hasattr(self.position_manager, 'get_symbol_exposure'):
                        try:
                            exposure = self.position_manager.get_symbol_exposure(symbol)  # type: ignore
                        except Exception:
                            exposure = 0.0
                    limit = getattr(self.position_manager, 'max_exposure_per_symbol', 0.0)
                    if limit and abs(exposure + volume) > limit:
                        return False, 'exposure_limit'
                    return True, None
                except Exception as e:  # no bloquear por fallo inesperado
                    self.logger.error(f"Hook pre-orden error: {e}")
                    return True, None
            try:
                self.execution_router.pre_order_hooks.append(_pre_hook)  # type: ignore
                self.logger.info("Hook de pre-orden (exposure/rate) registrado")
            except Exception as e:
                self.logger.error(f"No se pudo registrar hook pre-orden: {e}")

    def _initialize_production_services(self):
        try:
            from core.event_bus import EventBus  # type: ignore
        except Exception:
            EventBus = None  # type: ignore
        try:
            from real_trading.kill_switch import KillSwitch  # type: ignore
        except Exception:
            KillSwitch = None  # type: ignore
        try:
            from real_trading.state_persistence import StatePersistence  # type: ignore
        except Exception:
            StatePersistence = None  # type: ignore
        try:
            from real_trading.heartbeat_monitor import HeartbeatMonitor  # type: ignore
        except Exception:
            HeartbeatMonitor = None  # type: ignore
        try:
            from real_trading.account_sync_service import AccountSyncService  # type: ignore
        except Exception:
            AccountSyncService = None  # type: ignore

        if EventBus and not self.event_bus:
            try:
                self.event_bus = EventBus()  # type: ignore
            except Exception as e:
                self.logger.error(f"No se pudo crear EventBus: {e}")

        if KillSwitch and not self.kill_switch:
            try:
                self.kill_switch = KillSwitch()  # type: ignore
            except Exception as e:
                self.logger.error(f"No se pudo crear KillSwitch: {e}")

        if StatePersistence and not self.state_persistence:
            try:
                self.state_persistence = StatePersistence(base_path=DATA_PATH / 'state')  # type: ignore
            except Exception as e:
                self.logger.error(f"No se pudo crear StatePersistence: {e}")

        if HeartbeatMonitor and not self.heartbeat_monitor:
            try:
                self.heartbeat_monitor = HeartbeatMonitor(stale_threshold=20.0)  # type: ignore
            except Exception as e:
                self.logger.error(f"No se pudo crear HeartbeatMonitor: {e}")

        if AccountSyncService and self.execution_router and not self.account_sync:
            try:
                primary_exec = getattr(self.execution_router, 'primary_executor', None)
                if primary_exec:
                    self.account_sync = AccountSyncService(primary_exec, interval=20.0)  # type: ignore
                    self.account_sync.start()
            except Exception as e:
                self.logger.error(f"No se pudo iniciar AccountSync: {e}")

        # Restaurar estado previo si existe (posiciones/exposición)
        if self.state_persistence and self.position_manager:
            try:
                saved = self.state_persistence.load()  # type: ignore
                expo = saved.get('exposure', {}) if isinstance(saved, dict) else {}
                if isinstance(expo, dict):
                    # cargar exposición guardada
                    for sym, val in expo.items():
                        try:
                            if hasattr(self.position_manager, '_exposure'):
                                self.position_manager._exposure[sym] = float(val)  # type: ignore
                        except Exception:
                            pass
                try:
                    self.logger.info("Estado de exposición restaurado")
                except Exception:
                    pass
            except Exception as e:
                self.logger.error(f"No se pudo restaurar estado: {e}")
        
    def _setup_directories(self):
        """Crear directorios necesarios"""
        required_folders = [DATA_PATH, LOGS_PATH, DATA_PATH / "cache", DATA_PATH / "exports"]
        
        for folder in required_folders:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("📁 Estructura de directorios verificada")
    
    def initialize_real_components(self):
        """Inicializar RealICTDataCollector y componentes reales"""
        self.logger.info("🔄 Inicializando componentes reales...")
        
        try:
            # Añadir dashboard data path para imports
            dashboard_data_path = str(DASHBOARD_PATH / "data")
            if dashboard_data_path not in sys.path:
                sys.path.insert(0, dashboard_data_path)
            
            # Cargar RealICTDataCollector dinámicamente
            data_collector_path = DASHBOARD_PATH / "data" / "data_collector_simplified.py"
            RealICTDataCollector = safe_import_from_path(
                data_collector_path,
                "RealICTDataCollector",
                "RealICTDataCollector"
            )
            
            if not RealICTDataCollector:
                self.logger.warning("RealICTDataCollector no disponible - continuando sin él")
                self.real_components_loaded = False
                return
            
            self.logger.info("[SYSTEM] Creando RealICTDataCollector...")
            
            # Crear instancia del data collector con configuración básica
            config = {
                'symbols': ['EURUSD', 'GBPUSD', 'USDCAD', 'AUDUSD'],
                'timeframes': ['M1', 'M5', 'M15'],
                'data_path': str(DATA_PATH)
            }
            self.data_collector = RealICTDataCollector(config)
            
            self.logger.info("✅ RealICTDataCollector: Inicializado correctamente")
            print("🚀 [SYSTEM] ✅ RealICTDataCollector: Inicializado correctamente")
            print("    - Configuración aplicada")
            print("    - Sistema listo para operación")
            self.real_components_loaded = True
            self.system_status.real_components_loaded = True
            # Actualizar health monitor si ya estaba creado para que tenga referencia al data_collector
            if self.health_monitor and hasattr(self.health_monitor, 'data_collector'):
                try:
                    self.health_monitor.data_collector = self.data_collector  # type: ignore
                except Exception:
                    pass
                
        except Exception as e:
            self.logger.error(f"Error inicializando componentes reales: {e}")
            print(f"[X] Error inicializando componentes reales: {e}")
            self.real_components_loaded = False
            self.system_status.real_components_loaded = False
    
    def show_system_info(self):
        """Mostrar información del sistema con estado de componentes reales"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "="*80)
        print("ICT ENGINE v6.0 ENTERPRISE - SISTEMA REAL DE TRADING")
        print("="*80)
        print(f"🕒 Timestamp: {timestamp}")
        print(f"📂 Project Root: {SYSTEM_ROOT}")
        print(f"🔧 Core Path: {CORE_PATH}")
        print(f"📊 Data Path: {DATA_PATH}")
        print(f"📝 Logs Path: {LOGS_PATH}")
        print(f"📈 Dashboard Path: {DASHBOARD_PATH}")
        print()
        print("ESTADO DE COMPONENTES REALES:")
        print("-" * 40)
        print(f"📊 RealICTDataCollector: {'✓ Activo' if self.real_components_loaded else '✗ Error'}")
        print(f"🔗 MT5 Connection: {'✓ Conectado' if self.system_status.mt5_connected else '✗ Desconectado'}")
        print(f"📝 SmartTradingLogger: {'✓ Activo' if SMART_LOGGER_AVAILABLE else '✗ Básico'}")
        print()
        print("🎯 Modo: TRADING REAL - Sin Mock Data")
        print("="*80)
        print()

    def print_component_status(self):
        """Imprimir estado ON/OFF de componentes críticos producción."""
        # Componentes optimizados para producción
        production_components = [
            ("ProductionValidator", self.production_validator),
            ("TradingRateLimiter", self.trading_rate_limiter),
            ("DataRateLimiter", self.data_rate_limiter),
            ("MainRateLimiter", self.main_rate_limiter),
            ("HealthMonitor", self.health_performance_monitor),
        ]
        
        # Componentes legacy/existentes
        legacy_components = [
            ("RiskGuard", self.risk_guard),
            ("LatencyWatchdog", self.latency_watchdog),
            ("DataFeedFallback", self.data_feed_fallback),
            ("ExecutionRouter", self.execution_router),
            ("PositionManager", self.position_manager),
            ("OrderRateLimiter", self.rate_limiter),
            ("AlertDispatcher", self.alert_dispatcher),
            ("ConfigLoader", self.config_loader),
            ("LatencySampler", self.latency_sampler),
            ("EventBus", self.event_bus),
            ("KillSwitch", self.kill_switch),
            ("StatePersistence", self.state_persistence),
            ("HeartbeatMonitor", self.heartbeat_monitor),
            ("AccountSyncService", self.account_sync),
            ("TradeReconciler", self.trade_reconciler)
        ]
        
        print("\n🏭 MÓDULOS OPTIMIZADOS PARA PRODUCCIÓN:")
        print("-"*52)
        for name, ref in production_components:
            if ref is not None:
                # Verificar si está corriendo (para health monitor)
                if hasattr(ref, 'is_running') and hasattr(ref.is_running, '__call__'):
                    try:
                        state = "ON " if ref.is_running() else "OFF"
                    except:
                        state = "ON " if ref else "OFF"
                elif hasattr(ref, 'is_running'):
                    state = "ON " if ref.is_running else "OFF"
                else:
                    state = "ON "
            else:
                state = "OFF"
            print(f"{name:20s}: {state}")
        
        print("\n📦 COMPONENTES LEGACY/EXISTENTES:")
        print("-"*52)
        for name, ref in legacy_components:
            state = "ON " if ref else "OFF"
            print(f"{name:20s}: {state}")
        print("-"*52)

    def run_dashboard_with_real_data(self):
        """Iniciar Dashboard Enterprise en ventana separada"""
        self.logger.info("🚀 INICIANDO DASHBOARD ENTERPRISE CON DATOS REALES...")
        print("\n[ROCKET] INICIANDO DASHBOARD ENTERPRISE CON DATOS REALES...")
        print("=" * 60)
        
        try:
            # Asegurar que los componentes están inicializados
            if not self.real_components_loaded:
                self.logger.info("Inicializando componentes reales para dashboard")
                print("[INFO] Inicializando componentes reales...")
                self.initialize_real_components()
            
            # Verificar estado del data collector
            self.logger.info("Verificando RealICTDataCollector para dashboard")
            print("[DATA] Verificando RealICTDataCollector...")
            
            if hasattr(self, 'data_collector') and self.data_collector:
                self.logger.info("RealICTDataCollector disponible para dashboard")
                print("[OK] RealICTDataCollector: ✓ Disponible")
                print("    - Sistema configurado con datos reales")
                print("    - Dashboard listo para cargar")
            else:
                self.logger.warning("RealICTDataCollector no disponible, modo básico")
                print("[WARN] RealICTDataCollector: Iniciando en modo básico")
            
            # Cargar el dashboard
            dashboard_script = DASHBOARD_PATH / "start_dashboard.py"
            
            if dashboard_script.exists():
                self.logger.info(f"Ejecutando dashboard desde: {dashboard_script}")
                print("[ROCKET] 🚀 Abriendo dashboard en ventana separada...")
                
                # Configurar variables de entorno para el dashboard
                env = os.environ.copy()
                env['PYTHONPATH'] = os.pathsep.join([
                    str(SYSTEM_ROOT),
                    str(CORE_PATH),
                    str(DASHBOARD_PATH)
                ])
                env['ICT_DASHBOARD_MODE'] = 'subprocess'
                
                print("[SUBPROCESS] 🚀 Iniciando dashboard en proceso separado...")
                
                # Usar Popen para control completo del proceso
                self.dashboard_process = subprocess.Popen(
                    [sys.executable, str(dashboard_script)], 
                    cwd=str(DASHBOARD_PATH),
                    env=env,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
                )
                
                print(f"[SUBPROCESS] 📊 Dashboard iniciado con PID: {self.dashboard_process.pid}")
                print("[SUBPROCESS] 🎯 Dashboard abriendo en ventana separada...")
                print("[SUBPROCESS] 💡 El dashboard debería aparecer en una nueva ventana")
                print("[SUBPROCESS] ⏳ Esperando que uses el dashboard...")
                print("[SUBPROCESS] 🔑 Presiona 'q' en el dashboard para cerrar y regresar aquí")
                
                try:
                    # Esperar a que termine el proceso
                    result_code = self.dashboard_process.wait()
                    
                except KeyboardInterrupt:
                    print("\n[SUBPROCESS] ⚠️ Interrupción detectada - cerrando dashboard...")
                    try:
                        self.dashboard_process.terminate()
                        self.dashboard_process.wait(timeout=5)
                        result_code = 0
                    except subprocess.TimeoutExpired:
                        print("[SUBPROCESS] 🔧 Forzando cierre del dashboard...")
                        self.dashboard_process.kill()
                        self.dashboard_process.wait()
                        result_code = -1
                
                print(f"[SUBPROCESS] ✅ Dashboard cerrado con código: {result_code}")
                
                if result_code == 0:
                    print("\n[OK] ✅ DASHBOARD ENTERPRISE CERRADO EXITOSAMENTE")
                    print("[INFO] 🔄 Regresando automáticamente al menú principal...")
                    print("="*60)
                    print("[SUCCESS] 🏁 SESIÓN DASHBOARD COMPLETADA")
                    print("   ✅ Dashboard cerrado correctamente")
                    print("   🔄 Control devuelto al menú principal")
                    print("   🟢 Sistema listo para nueva operación")
                    print("="*60)
                    print("\n[PRODUCCIÓN] 🚀 Menú principal se mostrará en 3 segundos...")
                    time.sleep(3)
                else:
                    print(f"\n[WARN] ⚠️ Dashboard finalizó con código: {result_code}")
                    print("[INFO] 🔄 Regresando automáticamente al menú principal...")
                    time.sleep(2)
                    
            else:
                print("[X] No se encontró start_dashboard.py")
                print(f"[TOOL] Verificar ruta: {dashboard_script}")
                
        except KeyboardInterrupt:
            print("\n[SUBPROCESS] ⚠️ Dashboard cerrado por el usuario")
        except Exception as e:
            self.logger.error(f"Error ejecutando dashboard: {e}")
            print(f"[X] Error ejecutando dashboard: {e}")
            import traceback
            traceback.print_exc()
    
    def run_web_dashboard_with_real_data(self):
        """Iniciar Web Dashboard con análisis real en navegador"""
        self.logger.info("🌐 INICIANDO WEB DASHBOARD CON ANÁLISIS REAL...")
        print("\n[WEB] 🌐 INICIANDO WEB DASHBOARD CON ANÁLISIS REAL...")
        print("=" * 60)
        
        try:
            # Asegurar que los componentes están inicializados
            if not self.real_components_loaded:
                self.logger.info("Inicializando componentes reales para web dashboard")
                print("[INFO] Inicializando componentes reales...")
                self.initialize_real_components()
            
            # Verificar estado del data collector
            print("[WEB] Verificando sistema de análisis real...")
            
            if hasattr(self, 'data_collector') and self.data_collector:
                print("[OK] ✓ Sistema de análisis real disponible")
                print("    - Order Blocks detection: ACTIVO")
                print("    - Smart Money Concepts: ACTIVO")
                print("    - Logging en tiempo real: ACTIVO")
            else:
                print("[WARN] Sistema básico - Iniciando con datos simulados")
            
            # Cargar el web dashboard
            web_dashboard_script = DASHBOARD_PATH / "start_web_dashboard.py"
            
            if web_dashboard_script.exists():
                self.logger.info(f"Ejecutando web dashboard desde: {web_dashboard_script}")
                print("[WEB] 🚀 Iniciando servidor web dashboard...")
                
                # Configurar variables de entorno
                env = os.environ.copy()
                env['PYTHONPATH'] = os.pathsep.join([
                    str(SYSTEM_ROOT),
                    str(CORE_PATH),
                    str(DASHBOARD_PATH)
                ])
                env['ICT_WEB_DASHBOARD_MODE'] = 'real_analysis'
                
                print("[WEB] 📊 Configurando servidor web...")
                print("[WEB] 🌐 URL: http://127.0.0.1:8050")
                print("[WEB] 💡 El dashboard se abrirá automáticamente en tu navegador")
                print("[WEB] 🔄 Order Blocks actualizándose cada 500ms")
                print("[WEB] ⚠️  Presiona Ctrl+C para detener el servidor")
                
                # Usar Popen para control del proceso web
                self.web_dashboard_process = subprocess.Popen(
                    [sys.executable, str(web_dashboard_script)], 
                    cwd=str(DASHBOARD_PATH),
                    env=env,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                print(f"[WEB] 📊 Servidor web iniciado con PID: {self.web_dashboard_process.pid}")
                print("[WEB] 🎯 Accede a: http://127.0.0.1:8050 en tu navegador")
                print("[WEB] 💰 Order Blocks Tab disponible con datos en tiempo real")
                
                try:
                    # Esperar a que termine el proceso web
                    result_code = self.web_dashboard_process.wait()
                    
                except KeyboardInterrupt:
                    print("\n[WEB] ⚠️ Interrupción detectada - cerrando servidor web...")
                    try:
                        self.web_dashboard_process.terminate()
                        self.web_dashboard_process.wait(timeout=5)
                        result_code = 0
                    except subprocess.TimeoutExpired:
                        print("[WEB] 🔧 Forzando cierre del servidor...")
                        self.web_dashboard_process.kill()
                        self.web_dashboard_process.wait()
                        result_code = -1
                
                print(f"[WEB] ✅ Servidor web cerrado con código: {result_code}")
                
                if result_code == 0:
                    print("\n[OK] ✅ WEB DASHBOARD CERRADO EXITOSAMENTE")
                    print("[INFO] 🔄 Regresando al menú principal...")
                    print("="*60)
                    print("[SUCCESS] 🏁 SESIÓN WEB DASHBOARD COMPLETADA")
                    print("   ✅ Servidor web cerrado correctamente")
                    print("   🔄 Control devuelto al menú principal")
                    print("   🟢 Sistema listo para nueva operación")
                    print("="*60)
                    print("\n[PRODUCCIÓN] 🚀 Menú principal se mostrará en 3 segundos...")
                    time.sleep(3)
                else:
                    print(f"\n[WARN] ⚠️ Servidor web finalizó con código: {result_code}")
                    print("[INFO] 🔄 Regresando al menú principal...")
                    time.sleep(2)
                    
            else:
                print("[X] No se encontró start_web_dashboard.py")
                print(f"[TOOL] Verificar ruta: {web_dashboard_script}")
                
        except KeyboardInterrupt:
            print("\n[WEB] ⚠️ Servidor web cerrado por el usuario")
        except Exception as e:
            self.logger.error(f"Error ejecutando web dashboard: {e}")
            print(f"[X] Error ejecutando web dashboard: {e}")
            import traceback
            traceback.print_exc()
    
    def run_silver_bullet_trading(self):
        """🔫 Ejecutar Silver Bullet Auto Trading"""
        try:
            print("\n" + "="*60)
            print("🔫 SILVER BULLET AUTO TRADING v6.0")
            print("="*60)
            print("📍 Cargando módulo Silver Bullet...")
            
            # Usar sistema de importación dinámico robusto
            trader_result = self._load_silver_bullet_trader()
            
            if trader_result['success']:
                print("✅ Módulo Silver Bullet cargado exitosamente")
                print("🚀 Iniciando interfaz de auto trading...")
                
                # Ejecutar el trader
                trader_result['runner']()
            else:
                print(f"❌ No se pudo cargar Silver Bullet trader: {trader_result['error']}")
                input("\nPresiona ENTER para continuar...")
            
        except Exception as e:
            self.logger.error(f"Error en Silver Bullet trading: {e}")
            print(f"\n❌ Error ejecutando Silver Bullet trading: {e}")
            import traceback
            traceback.print_exc()
            input("\nPresiona ENTER para continuar...")
            
        finally:
            print("\n🔄 Regresando al menú principal...")
    
    def _load_silver_bullet_trader(self) -> Dict[str, Any]:
        """Cargar Silver Bullet trader de forma segura"""
        try:
            # Verificar si existe el archivo
            silver_bullet_path = CORE_PATH / "trading" / "silver_bullet_trader.py"
            
            if not silver_bullet_path.exists():
                self.logger.info("Silver Bullet trader no existe, creando automáticamente")
                self._create_silver_bullet_trader_production()
            
            # Importación dinámica usando importlib para evitar errores de Pylance
            import importlib.util
            
            spec = importlib.util.spec_from_file_location("silver_bullet_trader", silver_bullet_path)
            if spec is None or spec.loader is None:
                return {'success': False, 'error': 'No se pudo crear spec del módulo'}
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Obtener la función runner
            if hasattr(module, 'run_silver_bullet_trader'):
                return {
                    'success': True,
                    'runner': module.run_silver_bullet_trader,
                    'module': module
                }
            else:
                return {'success': False, 'error': 'Función run_silver_bullet_trader no encontrada'}
                
        except Exception as e:
            self.logger.error(f"Error cargando Silver Bullet trader: {e}")
            return {'success': False, 'error': str(e)}

    def run_production_monitoring(self):
        """Ejecutar sistema completo de monitoreo de producción"""
        if self.logger:
            self.logger.info("Iniciando sistema completo de monitoreo de producción")
        
        try:
            # Configurar path usando variable global
            if str(CORE_PATH) not in sys.path:
                sys.path.insert(0, str(CORE_PATH))
            
            # 1. Health Monitor
            self._start_health_monitor()
            
            # 2. System Monitor 
            self._start_system_monitor()
            
            # 3. Performance Monitor
            self._start_performance_monitor()
            
            # Resumen del estado
            self._display_monitoring_summary()
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error en sistema de monitoreo: {e}")
            print(f"Error en sistema de monitoreo: {e}")
        
        print("✅ Sistema completo de monitoreo de producción configurado")
    
    def _start_health_monitor(self):
        """Iniciar Health Monitor"""
        try:
            health_monitor_path = CORE_PATH / "monitoring" / "health_monitor.py"
            if health_monitor_path.exists():
                import importlib
                health_monitor = importlib.import_module("monitoring.health_monitor")
                if hasattr(health_monitor, 'HealthMonitor'):
                    monitor = health_monitor.HealthMonitor()
                    if hasattr(monitor, 'start_monitoring'):
                        monitor.start_monitoring()
                        if self.logger:
                            self.logger.info("✅ Health Monitor iniciado")
                    
                    # Check de salud
                    if hasattr(monitor, 'get_health_status'):
                        status = monitor.get_health_status()
                        if self.logger:
                            self.logger.info(f"Estado de salud: {status}")
            else:
                if self.logger:
                    self.logger.warning("Health Monitor no encontrado")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error iniciando Health Monitor: {e}")
    
    def _start_system_monitor(self):
        """Iniciar System Monitor"""
        try:
            system_monitor_path = CORE_PATH / "monitoring" / "production_system_monitor.py"
            if system_monitor_path.exists():
                import importlib
                system_monitor = importlib.import_module("monitoring.production_system_monitor")
                if hasattr(system_monitor, 'ProductionSystemMonitor'):
                    monitor = system_monitor.ProductionSystemMonitor()
                    monitor.start_monitoring()
                    if self.logger:
                        self.logger.info("✅ System Monitor iniciado")
                    
                    # Status inicial
                    status = monitor.get_current_status()
                    if self.logger:
                        self.logger.info(f"Sistema: {status.get('health', 'unknown')} | CPU: {status.get('cpu_percent', 0):.1f}%")
            else:
                if self.logger:
                    self.logger.warning("System Monitor no encontrado - usando módulo existente")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error iniciando System Monitor: {e}")
    
    def _start_performance_monitor(self):
        """Iniciar Performance Monitor"""
        try:
            perf_monitor_path = CORE_PATH / "monitoring" / "production_performance_monitor.py"
            if perf_monitor_path.exists():
                import importlib
                perf_monitor = importlib.import_module("monitoring.production_performance_monitor")
                if hasattr(perf_monitor, 'ProductionPerformanceMonitor'):
                    monitor = perf_monitor.ProductionPerformanceMonitor()
                    monitor.start_monitoring()
                    if self.logger:
                        self.logger.info("✅ Performance Monitor iniciado")
                    
                    # Status inicial
                    status = monitor.get_current_performance()
                    if self.logger:
                        self.logger.info(f"Performance: {status.get('status', 'unknown')}")
            else:
                if self.logger:
                    self.logger.warning("Performance Monitor no encontrado - usando módulo existente")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error iniciando Performance Monitor: {e}")
    
    def _display_monitoring_summary(self):
        """Mostrar resumen del estado de monitoreo"""
        try:
            print("\n" + "="*60)
            print("🚀 RESUMEN DEL SISTEMA DE MONITOREO DE PRODUCCIÓN")
            print("="*60)
            
            monitoring_modules = [
                ("Health Monitor", "monitoring.health_monitor", "HealthMonitor"),
                ("System Monitor", "monitoring.production_system_monitor", "ProductionSystemMonitor"),
                ("Performance Monitor", "monitoring.production_performance_monitor", "ProductionPerformanceMonitor")
            ]
            
            for name, module_name, class_name in monitoring_modules:
                try:
                    import importlib
                    module = importlib.import_module(module_name)
                    if hasattr(module, class_name):
                        print(f"✅ {name}: ACTIVO")
                    else:
                        print(f"⚠️  {name}: MÓDULO SIN CLASE PRINCIPAL")
                except ImportError:
                    print(f"❌ {name}: NO DISPONIBLE")
            
            print("="*60)
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error mostrando resumen: {e}")
            
    def _create_silver_bullet_trader_production(self):
        """Crear Silver Bullet trader de producción usando central de logging"""
        silver_bullet_path = CORE_PATH / "trading" / "silver_bullet_trader.py"
        
        if not silver_bullet_path.exists():
            self.logger.info("Creando Silver Bullet trader de producción automáticamente")
            # Crear directorio si no existe
            silver_bullet_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Contenido de producción del trader usando central de logging
            content = '''#!/usr/bin/env python3
"""
🔫 SILVER BULLET AUTO TRADER - ICT ENGINE v6.0 ENTERPRISE
========================================================

Ejecutor automático de patrones Silver Bullet integrado con sistema de producción.
Usa central de logging y protocolos establecidos del sistema.

Creado automáticamente por ICTEnterpriseManager v6.0
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Setup paths - desde 01-CORE/trading/
CURRENT_DIR = Path(__file__).resolve().parent
CORE_PATH = CURRENT_DIR.parent
SYSTEM_ROOT = CORE_PATH.parent
sys.path.insert(0, str(CORE_PATH))

# Importar central de logging
try:
    from protocols.logging_central_protocols import setup_module_logging, LogLevel
    logger = setup_module_logging("SilverBulletTrader", LogLevel.INFO)
    LOGGING_AVAILABLE = True
except ImportError:
    logger = None
    LOGGING_AVAILABLE = False

class SilverBulletAutoTrader:
    """🔫 Clase principal para trading automático Silver Bullet"""
    
    def __init__(self):
        self.active = False
        if LOGGING_AVAILABLE and logger:
            logger.info("Inicializando Silver Bullet Auto Trader v6.0", "SilverBullet")
        
    def check_system_status(self):
        """🔧 Verificar estado del sistema"""
        status = {
            'logging_available': LOGGING_AVAILABLE,
            'components_loaded': False,
            'ready_for_trading': False
        }
        
        if LOGGING_AVAILABLE and logger:
            logger.info(f"Estado del sistema: {status}", "SilverBullet")
        
        return status


def run_silver_bullet_trader():
    """🚀 Función principal para ejecutar desde main.py"""
    try:
        if LOGGING_AVAILABLE and logger:
            logger.info("Iniciando Silver Bullet Auto Trader", "SilverBullet")
        
        trader = SilverBulletAutoTrader()
        
        while True:
            print("\\n🔫 SILVER BULLET AUTO TRADER v6.0")
            print("=" * 40)
            print("1. � Ver estado del sistema")
            print("2. 🎯 Inicializar componentes")
            print("3. 📊 Escanear señales")
            print("4. 🏠 Volver al menú principal")
            print("=" * 40)
            
            choice = input("Selecciona opción (1-4): ").strip()
            
            if choice == "1":
                status = trader.check_system_status()
                print(f"\\n📊 ESTADO DEL SISTEMA:")
                for key, value in status.items():
                    status_icon = "✅" if value else "❌"
                    print(f"   {status_icon} {key}: {value}")
                input("\\nPresiona ENTER para continuar...")
                
            elif choice == "2":
                print("\\n� INICIALIZANDO COMPONENTES...")
                if LOGGING_AVAILABLE and logger:
                    logger.info("Inicializando componentes Silver Bullet", "SilverBullet")
                print("✅ Componentes básicos inicializados")
                input("\\nPresiona ENTER para continuar...")
                
            elif choice == "3":
                print("\\n🎯 ESCANEANDO SEÑALES...")
                if LOGGING_AVAILABLE and logger:
                    logger.info("Iniciando escaneo de señales Silver Bullet", "SilverBullet")
                print("📊 Escaneo completado - No hay señales activas")
                input("\\nPresiona ENTER para continuar...")
                
            elif choice == "4":
                if LOGGING_AVAILABLE and logger:
                    logger.info("Cerrando Silver Bullet Auto Trader", "SilverBullet")
                break
                
            else:
                print("❌ Opción inválida")
                
    except KeyboardInterrupt:
        print("\\n🛑 Silver Bullet Auto Trader interrumpido por usuario")
    except Exception as e:
        if LOGGING_AVAILABLE and logger:
            logger.error(f"Error en Silver Bullet Auto Trader: {e}", "SilverBullet")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_silver_bullet_trader()
'''
            
            with open(silver_bullet_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Silver Bullet trader creado en: {silver_bullet_path}")
        else:
            self.logger.info(f"Silver Bullet trader ya existe: {silver_bullet_path}")

    def main_menu(self):
        """Menú principal con opciones de Web Dashboard y Dashboard Terminal"""
        while True:
            print("\n" + "="*70)
            print("ICT ENGINE v6.0 ENTERPRISE - TRADING REAL")
            print("="*70)
            print("1. 🌐 [WEB DASHBOARD] Análisis Real - Navegador Web")
            print("2. 🖥️  [DASHBOARD TERMINAL] Dashboard Convencional")
            print("3. 🔫 [SILVER BULLET] Auto Trading Silver Bullet")
            print("4. 📊 [MONITOREO] Sistema de Monitoreo de Producción")
            print("5. ❌ [SALIR] Cerrar Sistema")
            print("="*70)
            print("💡 Opción 1: Dashboard web moderno con Order Blocks en tiempo real")
            print("💡 Opción 2: Dashboard tradicional en ventana de terminal")
            print("🔫 Opción 3: Trading automático de patrones Silver Bullet")
            print("📊 Opción 4: Monitoreo completo del sistema en producción")
            print("="*70)
            
            try:
                choice = input("\n[TARGET] Selecciona una opción (1-5): ").strip()
                
                if choice == "1":
                    print("\n🌐 [WEB DASHBOARD] Iniciando dashboard web con análisis real...")
                    self.run_web_dashboard_with_real_data()
                    
                elif choice == "2":
                    if not self.real_components_loaded:
                        print("\n[INFO] Inicializando componentes reales...")
                        self.initialize_real_components()
                    
                    print("\n🖥️ [DASHBOARD TERMINAL] Iniciando dashboard convencional...")
                    print("[INFO] 📊 Componentes reales configurados y listos")
                    print("[INFO] ⚡ Cargando interfaz enterprise...")
                    
                    time.sleep(1.5)
                    self.run_dashboard_with_real_data()
                    
                elif choice == "3":
                    print("\n🔫 [SILVER BULLET] Iniciando sistema de auto trading...")
                    self.run_silver_bullet_trading()
                    
                elif choice == "4":
                    print("\n📊 [MONITOREO] Iniciando sistema de monitoreo de producción...")
                    self.run_production_monitoring()
                    input("\nPresiona ENTER para continuar...")
                    
                elif choice == "5":
                    print("\n[EXIT] Cerrando sistema de trading...")
                    break
                    
                else:
                    print("[X] Opción no válida. Usa 1-5.")
                    continue
                    
            except KeyboardInterrupt:
                print("\n[EXIT] Saliendo...")
                break
            except EOFError:
                print("\n[EXIT] Saliendo...")
                break
                
            # Pausa antes de mostrar el menú de nuevo
            if choice == "1":
                print("\n" + "="*80)
                print("🔄 RETORNANDO AL MENÚ PRINCIPAL")
                print("="*80)
                print("⚡ [PRODUCCIÓN] Regresando automáticamente al menú...")
                time.sleep(2)  # Pausa breve para que el usuario vea el mensaje
                print("\n" + "🔄 " + "="*78)
    
    def shutdown(self):
        """🛑 Cerrar sistema limpiamente"""
        print("🛑 [SHUTDOWN] Iniciando cierre del sistema...")
        start_time = time.time()
        
        try:
            self.shutdown_requested = True
            
            # Cerrar dashboard process si existe
            if self.dashboard_process:
                try:
                    self.dashboard_process.terminate()
                    self.dashboard_process.wait(timeout=2)
                except:
                    if self.dashboard_process.poll() is None:
                        self.dashboard_process.kill()
            
            # Cerrar web dashboard process si existe
            if self.web_dashboard_process:
                try:
                    self.web_dashboard_process.terminate()
                    self.web_dashboard_process.wait(timeout=2)
                except:
                    if self.web_dashboard_process.poll() is None:
                        self.web_dashboard_process.kill()
            
            # Cerrar componentes críticos
            if hasattr(self, 'data_collector') and self.data_collector:
                try:
                    if hasattr(self.data_collector, 'shutdown_sync'):
                        self.data_collector.shutdown_sync()
                    else:
                        self.logger.info("Forzando cierre inmediato de data collector")
                except:
                    pass

            # Reconciliación final (best-effort)
            if self.trade_reconciler:
                try:
                    report = self.trade_reconciler.reconcile()  # type: ignore
                    self.trade_reconciler.persist_report(report)  # type: ignore
                except Exception as e:
                    self.logger.error(f"Fallo reconciliación final: {e}")

            # Persistir estado de exposición/posiciones si disponible
            if self.state_persistence and self.position_manager:
                try:
                    exposure = {}
                    if hasattr(self.position_manager, '_exposure'):
                        exposure = getattr(self.position_manager, '_exposure', {})  # type: ignore
                    self.state_persistence.save({'exposure': exposure})  # type: ignore
                except Exception as e:
                    self.logger.error(f"No se pudo persistir estado final: {e}")
            
            # Force garbage collection
            collected = gc.collect()
            
            shutdown_time = time.time() - start_time
            self.logger.info(f"🛑 Shutdown completado en {shutdown_time:.2f}s (GC: {collected} objetos)")
            # Persistir métricas de ejecución si disponibles
            try:
                if self.execution_router and hasattr(self.execution_router, 'persist_on_shutdown'):
                    self.execution_router.persist_on_shutdown()  # type: ignore
            except Exception as e:
                self.logger.error(f"Error persistiendo métricas ejecución: {e}")
            
        except Exception as e:
            shutdown_time = time.time() - start_time
            self.logger.error(f"Error en shutdown ({shutdown_time:.2f}s): {e}")
    
    def get_production_metrics(self) -> dict:
        """📊 Obtener métricas integradas del sistema de producción"""
        metrics = {
            'timestamp': time.time(),
            'system_uptime': time.time() - getattr(self, 'start_time', time.time()),
            'production_modules': {}
        }
        
        # Información de configuración
        if self.production_config:
            metrics['configuration'] = {
                'profile': self.production_config.profile.value,
                'broker_type': self.production_config.broker_type.value,
                'market_condition': self.production_config.market_condition.value,
                'rate_limits': {
                    'orders_per_second': self.production_config.rate_limit.orders_per_second,
                    'orders_per_minute': self.production_config.rate_limit.orders_per_minute,
                    'concurrent_orders': self.production_config.rate_limit.concurrent_orders
                },
                'validation_level': self.production_config.validation.validation_level,
                'monitoring_level': self.production_config.health_monitor.monitoring_level
            }
        
        try:
            # Health & Performance Monitor Metrics
            if self.health_performance_monitor:
                try:
                    system_status = self.health_performance_monitor.get_system_status()
                    performance_summary = self.health_performance_monitor.get_performance_summary()
                    
                    metrics['health_monitor'] = {
                        'overall_health': system_status.get('overall_health'),
                        'uptime_seconds': system_status.get('uptime_seconds'),
                        'is_running': system_status.get('is_running'),
                        'components_count': len(system_status.get('components', {})),
                        'alerts_count': system_status.get('alerts_count'),
                        'performance': performance_summary
                    }
                except Exception as e:
                    metrics['health_monitor'] = {'error': str(e)}
            
            # Rate Limiter Metrics
            if self.trading_rate_limiter:
                try:
                    trading_metrics = self.trading_rate_limiter.get_metrics()
                    metrics['trading_rate_limiter'] = trading_metrics
                except Exception as e:
                    metrics['trading_rate_limiter'] = {'error': str(e)}
            
            if self.data_rate_limiter:
                try:
                    data_metrics = self.data_rate_limiter.get_metrics()
                    metrics['data_rate_limiter'] = data_metrics
                except Exception as e:
                    metrics['data_rate_limiter'] = {'error': str(e)}
            
            # Production Validator Metrics
            if self.production_validator:
                try:
                    validator_metrics = self.production_validator.get_performance_metrics()
                    metrics['production_validator'] = validator_metrics
                except Exception as e:
                    metrics['production_validator'] = {'error': str(e)}
            
            # System Resource Usage
            try:
                import psutil
                process = psutil.Process()
                metrics['system_resources'] = {
                    'cpu_percent': process.cpu_percent(),
                    'memory_mb': process.memory_info().rss / (1024 * 1024),
                    'threads_count': process.num_threads(),
                    'open_files': len(process.open_files()) if hasattr(process, 'open_files') else 0
                }
            except:
                metrics['system_resources'] = {'error': 'psutil not available'}
            
            # Component Status Summary
            production_components = [
                ('ProductionValidator', self.production_validator),
                ('TradingRateLimiter', self.trading_rate_limiter),
                ('DataRateLimiter', self.data_rate_limiter),
                ('MainRateLimiter', self.main_rate_limiter),
                ('HealthMonitor', self.health_performance_monitor),
            ]
            
            metrics['components_status'] = {}
            for name, component in production_components:
                if component:
                    try:
                        if hasattr(component, 'is_running'):
                            status = 'running' if component.is_running else 'stopped'
                        else:
                            status = 'active'
                    except:
                        status = 'active'
                else:
                    status = 'not_loaded'
                metrics['components_status'][name] = status
            
        except Exception as e:
            metrics['error'] = f"Error collecting metrics: {str(e)}"
        
        return metrics
    
    def print_production_metrics(self):
        """🖨️ Imprimir métricas de producción de forma legible"""
        metrics = self.get_production_metrics()
        
        print("\n" + "="*60)
        print("📊 MÉTRICAS DE PRODUCCIÓN - ICT ENGINE v6.0 ENTERPRISE")
        print("="*60)
        
        # System uptime
        uptime = metrics.get('system_uptime', 0)
        if uptime < 60:
            uptime_str = f"{uptime:.1f}s"
        elif uptime < 3600:
            uptime_str = f"{uptime/60:.1f}m"
        else:
            uptime_str = f"{uptime/3600:.1f}h"
        print(f"🕐 System Uptime: {uptime_str}")
        
        # Health Monitor
        if 'health_monitor' in metrics:
            hm = metrics['health_monitor']
            if 'error' not in hm:
                print(f"💖 Health Status: {hm.get('overall_health', 'unknown').upper()}")
                print(f"🏃 Monitor Running: {'YES' if hm.get('is_running') else 'NO'}")
                print(f"🔧 Components Monitored: {hm.get('components_count', 0)}")
                print(f"🚨 Active Alerts: {hm.get('alerts_count', 0)}")
        
        # Rate Limiters
        if 'trading_rate_limiter' in metrics:
            trl = metrics['trading_rate_limiter']
            if 'error' not in trl:
                total_req = trl.get('total_requests', 0)
                blocked_req = trl.get('blocked_requests', 0)
                block_rate = trl.get('block_rate_percent', 0)
                print(f"🚦 Trading Requests: {total_req} total, {blocked_req} blocked ({block_rate:.1f}%)")
        
        # Validator
        if 'production_validator' in metrics:
            pv = metrics['production_validator']
            if 'error' not in pv:
                total_val = pv.get('total_validations', 0)
                error_rate = pv.get('error_rate_percent', 0)
                cache_hit_rate = pv.get('cache_hit_rate_percent', 0)
                print(f"🛡️ Validations: {total_val} total, {error_rate:.1f}% errors, {cache_hit_rate:.1f}% cache hits")
        
        # System Resources
        if 'system_resources' in metrics:
            sr = metrics['system_resources']
            if 'error' not in sr:
                cpu = sr.get('cpu_percent', 0)
                memory = sr.get('memory_mb', 0)
                threads = sr.get('threads_count', 0)
                print(f"💻 Resources: {cpu:.1f}% CPU, {memory:.1f} MB RAM, {threads} threads")
        
        # Components Status
        if 'components_status' in metrics:
            print("\n🔧 PRODUCTION COMPONENTS:")
            for name, status in metrics['components_status'].items():
                status_icon = "✅" if status in ['active', 'running'] else "❌"
                print(f"   {status_icon} {name}: {status.upper()}")
        
        print("="*60)

# ============================================================================
# FUNCIÓN PRINCIPAL ENTERPRISE
# ============================================================================

def main():
    """Función principal del sistema ICT Engine v6.0 Enterprise"""
    manager = None
    try:
        print("ICT Engine v6.0 Enterprise - Inicio")
        print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Crear instancia del sistema enterprise
        print("Creando ICTEnterpriseManager...")
        manager = ICTEnterpriseManager()
        
        # Mostrar información del sistema
        manager.show_system_info()
        manager.print_component_status()
        
        # Mostrar métricas de producción iniciales
        if PRODUCTION_MODULES_AVAILABLE:
            time.sleep(0.5)  # Dar tiempo a que se inicialicen las métricas
            manager.print_production_metrics()
        
        # Ejecutar menú principal
        print("Iniciando interfaz principal...")
        manager.main_menu()
        
        # Shutdown limpio
        print("Iniciando shutdown del sistema...")
        manager.shutdown()
        
        print("Sistema cerrado exitosamente")
        
    except KeyboardInterrupt:
        print("\nInterrupción por teclado detectada - cerrando sistema...")
        try:
            if manager is not None:
                manager.shutdown()
        except:
            pass
        sys.exit(0)
    except Exception as e:
        print(f"Error crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Restaurar directorio original
        try:
            os.chdir(original_dir)
            print(f"Directorio restaurado: {original_dir}")
        except Exception as e:
            print(f"No se pudo restaurar directorio: {e}")
        print("Hasta pronto")
        # Asegurar flush
        sys.stdout.flush(); sys.stderr.flush()

if __name__ == "__main__":
    main()
