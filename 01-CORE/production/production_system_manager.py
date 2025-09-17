#!/usr/bin/env python3
"""
🏭 PRODUCTION SYSTEM MANAGER - ICT Engine v6.0 Enterprise
=========================================================

Central manager for production trading operations. This module coordinates
all production components and provides a unified interface for real trading.

Key Features:
- Unified component management
- Production-ready error handling
- Performance monitoring integration
- Real-time health checks
- Graceful degradation
- Resource management
- Thread-safe operations

Components managed:
- MT5 connection and data management
- Risk management system
- Order execution engine
- Performance monitoring
- Emergency stop system
- Logging and alerting
- Data persistence

Author: ICT Engine v6.0 Enterprise Team
Date: September 2025
"""

import threading
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Set, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sys
import os

# Add project paths
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(current_dir.parent))

# Import logging protocol
try:
    from protocols.logging_protocol import get_central_logger, LogLevel, LogCategory
    logger = get_central_logger("ProductionSystemManager")
    LOGGING_AVAILABLE = True
except ImportError:
    logger = None
    LogCategory = None  # Define fallback
    LOGGING_AVAILABLE = False
    print("⚠️ Advanced logging not available, using fallback")
    
    class FallbackLogger:
        def info(self, msg, component=""): print(f"[INFO] {msg}")
        def error(self, msg, component=""): print(f"[ERROR] {msg}")
        def warning(self, msg, component=""): print(f"[WARNING] {msg}")
        def debug(self, msg, component=""): print(f"[DEBUG] {msg}")
        def critical(self, msg, component=""): print(f"[CRITICAL] {msg}")
    
    logger = FallbackLogger()

def _safe_log(logger_instance, level: str, msg: str, category=None):
    """Safe logging that handles LogCategory availability"""
    if hasattr(logger_instance, level):
        log_func = getattr(logger_instance, level)
        if category and LogCategory and hasattr(LogCategory, 'SYSTEM'):
            try:
                log_func(msg, category)
            except:
                log_func(msg)
        else:
            log_func(msg)


class SystemStatus(Enum):
    """System status levels"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SHUTTING_DOWN = "shutting_down"


class ComponentStatus(Enum):
    """Component status levels"""
    OFFLINE = "offline"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    DEGRADED = "degraded"


@dataclass
class ComponentHealth:
    """Component health information"""
    name: str
    status: ComponentStatus
    last_update: datetime
    error_count: int = 0
    warning_count: int = 0
    performance_metrics: Dict[str, float] = None
    additional_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.additional_info is None:
            self.additional_info = {}


@dataclass
class SystemHealth:
    """Overall system health"""
    overall_status: SystemStatus
    components: Dict[str, ComponentHealth]
    last_update: datetime
    uptime_seconds: float
    total_errors: int
    total_warnings: int
    memory_usage_mb: float
    cpu_usage_percent: float


class ProductionSystemManager:
    """
    Central manager for all production trading operations
    
    This class coordinates all production components and provides
    monitoring, health checks, and unified control.
    """
    
    def __init__(self, config_path_or_dict: Optional[Union[str, Dict[str, Any]]] = None):
        """Initialize production system manager"""
        self.logger = logger or get_central_logger("ProductionManager")
        
        # Handle both config path and config dict
        if isinstance(config_path_or_dict, dict):
            self.config = self._create_config_from_dict(config_path_or_dict)
        else:
            self.config = self._load_config(config_path_or_dict)
        
        # System state
        self.status = SystemStatus.STOPPED
        self.start_time = None
        self.components: Dict[str, Any] = {}
        self.component_health: Dict[str, ComponentHealth] = {}
        
        # Threading
        self._lock = threading.RLock()
        self._monitoring_thread = None
        self._monitoring_active = False
        
        # Performance tracking
        self._performance_history: List[Dict[str, Any]] = []
        self._last_health_check = datetime.now()
        
        _safe_log(self.logger, 'info', "Production System Manager initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "monitoring": {
                "health_check_interval": 30,  # seconds
                "performance_history_limit": 100,
                "auto_recovery": True,
                "critical_error_threshold": 10
            },
            "components": {
                "mt5_manager": {"enabled": True, "retry_attempts": 3},
                "risk_manager": {"enabled": True, "retry_attempts": 2},
                "execution_engine": {"enabled": True, "retry_attempts": 3},
                "emergency_system": {"enabled": True, "retry_attempts": 1},
                "position_manager": {"enabled": True, "retry_attempts": 2},
                "data_persistence": {"enabled": True, "retry_attempts": 2}
            },
            "trading": {
                "max_concurrent_operations": 10,
                "operation_timeout": 30,
                "enable_paper_trading": False,
                "symbols": ["EURUSD", "GBPUSD", "AUDUSD", "USDCAD"]
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    # Merge configurations
                    default_config.update(file_config)
                    self.logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def _create_config_from_dict(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Create configuration from provided dictionary"""
        default_config = {
            "system": {
                "name": "ICT Production System",
                "version": "6.0",
                "environment": "production",
                "max_components": 50,
                "component_timeout": 30
            },
            "monitoring": {
                "health_check_interval": 30,
                "metrics_collection_interval": 10,
                "alert_threshold": 5
            },
            "components": {
                "mt5_manager": True,
                "data_processor": True,
                "risk_manager": True,
                "position_manager": True,
                "alert_system": True
            },
            "trading": {
                "max_concurrent_operations": 10,
                "operation_timeout": 30,
                "enable_paper_trading": False,
                "symbols": ["EURUSD", "GBPUSD", "AUDUSD", "USDCAD"]
            }
        }
        
        # Deep merge the provided config
        if config_dict:
            self._deep_merge_configs(default_config, config_dict)
        
        self.logger.info("Configuration created from dictionary")
        return default_config
    
    def _deep_merge_configs(self, base_config: Dict, update_config: Dict) -> None:
        """Deep merge two configuration dictionaries"""
        for key, value in update_config.items():
            if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                self._deep_merge_configs(base_config[key], value)
            else:
                base_config[key] = value
    
    def initialize_components(self) -> bool:
        """Initialize all production components"""
        _safe_log(self.logger, 'info', "Initializing production components")
        
        with self._lock:
            self.status = SystemStatus.STARTING
            success_count = 0
            total_components = len(self.config["components"])
            
            # Initialize MT5 Manager
            if self._init_mt5_manager():
                success_count += 1
            
            # Initialize Risk Manager  
            if self._init_risk_manager():
                success_count += 1
            
            # Initialize Execution Engine
            if self._init_execution_engine():
                success_count += 1
            
            # Initialize Emergency System
            if self._init_emergency_system():
                success_count += 1
            
            # Initialize Position Manager
            if self._init_position_manager():
                success_count += 1
            
            # Initialize Data Persistence
            if self._init_data_persistence():
                success_count += 1
            
            # Update system status
            if success_count >= total_components * 0.7:  # 70% success rate
                self.status = SystemStatus.RUNNING
                self.logger.info(f"System initialized: {success_count}/{total_components} components ready")
                return True
            else:
                self.status = SystemStatus.ERROR
                self.logger.error(f"System initialization failed: {success_count}/{total_components} components ready")
                return False
    
    def _init_mt5_manager(self) -> bool:
        """Initialize MT5 data manager"""
        try:
            from data_management.mt5_data_manager import MT5DataManager
            
            mt5_manager = MT5DataManager()
            if mt5_manager.connect():
                self.components["mt5_manager"] = mt5_manager
                self._update_component_health("mt5_manager", ComponentStatus.READY)
                self.logger.info("MT5 Manager initialized successfully")
                return True
            else:
                self._update_component_health("mt5_manager", ComponentStatus.ERROR, 
                                            {"error": "Connection failed"})
                self.logger.warning("MT5 Manager failed to connect - continuing with simulation")
                return False
        except Exception as e:
            self._update_component_health("mt5_manager", ComponentStatus.ERROR, 
                                        {"error": str(e)})
            self.logger.warning(f"MT5 Manager initialization failed: {e}")
            return False
    
    def _init_risk_manager(self) -> bool:
        """Initialize risk management system"""
        try:
            from risk_management.risk_manager import RiskManager
            
            risk_manager = RiskManager()
            self.components["risk_manager"] = risk_manager
            self._update_component_health("risk_manager", ComponentStatus.READY)
            self.logger.info("Risk Manager initialized successfully")
            return True
        except Exception as e:
            self._update_component_health("risk_manager", ComponentStatus.ERROR, 
                                        {"error": str(e)})
            self.logger.error(f"Risk Manager initialization failed: {e}")
            return False
    
    def _init_execution_engine(self) -> bool:
        """Initialize execution engine"""
        try:
            from real_trading.execution_engine import ExecutionEngine
            
            execution_engine = ExecutionEngine()
            self.components["execution_engine"] = execution_engine
            self._update_component_health("execution_engine", ComponentStatus.READY)
            self.logger.info("Execution Engine initialized successfully")
            return True
        except Exception as e:
            self._update_component_health("execution_engine", ComponentStatus.ERROR, 
                                        {"error": str(e)})
            self.logger.error(f"Execution Engine initialization failed: {e}")
            return False
    
    def _init_emergency_system(self) -> bool:
        """Initialize emergency stop system"""
        try:
            from real_trading.emergency_stop_system import EmergencyStopSystem
            
            emergency_system = EmergencyStopSystem()
            self.components["emergency_system"] = emergency_system
            self._update_component_health("emergency_system", ComponentStatus.READY)
            self.logger.info("Emergency System initialized successfully")
            return True
        except Exception as e:
            self._update_component_health("emergency_system", ComponentStatus.ERROR, 
                                        {"error": str(e)})
            self.logger.warning(f"Emergency System initialization failed: {e}")
            return False
    
    def _init_position_manager(self) -> bool:
        """Initialize position manager"""
        try:
            from real_trading.position_manager import PositionManager
            
            position_manager = PositionManager()
            self.components["position_manager"] = position_manager
            self._update_component_health("position_manager", ComponentStatus.READY)
            self.logger.info("Position Manager initialized successfully")
            return True
        except Exception as e:
            self._update_component_health("position_manager", ComponentStatus.ERROR, 
                                        {"error": str(e)})
            self.logger.warning(f"Position Manager initialization failed: {e}")
            return False
    
    def _init_data_persistence(self) -> bool:
        """Initialize data persistence system"""
        try:
            from real_trading.state_persistence import StatePersistence
            
            persistence = StatePersistence()
            self.components["data_persistence"] = persistence
            self._update_component_health("data_persistence", ComponentStatus.READY)
            self.logger.info("Data Persistence initialized successfully")
            return True
        except Exception as e:
            self._update_component_health("data_persistence", ComponentStatus.ERROR, 
                                        {"error": str(e)})
            self.logger.warning(f"Data Persistence initialization failed: {e}")
            return False
    
    def _update_component_health(self, component_name: str, status: ComponentStatus, 
                               additional_info: Optional[Dict[str, Any]] = None):
        """Update component health information"""
        if component_name not in self.component_health:
            self.component_health[component_name] = ComponentHealth(
                name=component_name,
                status=status,
                last_update=datetime.now()
            )
        else:
            health = self.component_health[component_name]
            health.status = status
            health.last_update = datetime.now()
            if additional_info:
                health.additional_info.update(additional_info)
                if "error" in additional_info:
                    health.error_count += 1
    
    def start_monitoring(self):
        """Start system monitoring"""
        if self._monitoring_active:
            self.logger.warning("Monitoring already active")
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        self.logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)
        self.logger.info("System monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        interval = self.config["monitoring"]["health_check_interval"]
        
        while self._monitoring_active:
            try:
                self._perform_health_check()
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(interval)
    
    def _perform_health_check(self):
        """Perform comprehensive health check"""
        try:
            # Update component health
            self._check_component_health()
            
            # Check system resources
            self._check_system_resources()
            
            # Check trading operations
            self._check_trading_health()
            
            # Update overall status
            self._update_system_status()
            
            self._last_health_check = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
    
    def _check_component_health(self):
        """Check health of all components"""
        for name, component in self.components.items():
            try:
                if hasattr(component, 'is_healthy'):
                    is_healthy = component.is_healthy()
                    status = ComponentStatus.READY if is_healthy else ComponentStatus.ERROR
                elif hasattr(component, 'is_connected'):
                    is_connected = component.is_connected()
                    status = ComponentStatus.READY if is_connected else ComponentStatus.ERROR
                else:
                    status = ComponentStatus.READY  # Assume healthy if no check method
                
                self._update_component_health(name, status)
                
            except Exception as e:
                self._update_component_health(name, ComponentStatus.ERROR, {"error": str(e)})
    
    def _check_system_resources(self):
        """Check system resource usage"""
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage_mb = memory.used / (1024 * 1024)
            
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Update performance metrics
            for health in self.component_health.values():
                health.performance_metrics.update({
                    "memory_mb": memory_usage_mb,
                    "cpu_percent": cpu_usage
                })
                
        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            self.logger.warning(f"Resource check failed: {e}")
    
    def _check_trading_health(self):
        """Check trading-specific health metrics"""
        try:
            # Check MT5 connection
            if "mt5_manager" in self.components:
                mt5_manager = self.components["mt5_manager"]
                if hasattr(mt5_manager, 'is_connected'):
                    connected = mt5_manager.is_connected()
                    self.logger.debug(f"MT5 connection status: {connected}")
            
            # Check emergency system
            if "emergency_system" in self.components:
                emergency = self.components["emergency_system"]
                if hasattr(emergency, 'is_trading_enabled'):
                    trading_enabled = emergency.is_trading_enabled
                    if not trading_enabled:
                        self.logger.warning("Trading disabled by emergency system")
            
        except Exception as e:
            self.logger.error(f"Trading health check failed: {e}")
    
    def _update_system_status(self):
        """Update overall system status based on component health"""
        error_count = sum(1 for h in self.component_health.values() 
                         if h.status == ComponentStatus.ERROR)
        warning_count = sum(1 for h in self.component_health.values() 
                           if h.status == ComponentStatus.DEGRADED)
        
        if error_count > self.config["monitoring"]["critical_error_threshold"]:
            self.status = SystemStatus.CRITICAL
        elif error_count > 0:
            self.status = SystemStatus.ERROR
        elif warning_count > 0:
            self.status = SystemStatus.WARNING
        else:
            self.status = SystemStatus.RUNNING
    
    def get_system_health(self) -> SystemHealth:
        """Get comprehensive system health information"""
        uptime = 0
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        total_errors = sum(h.error_count for h in self.component_health.values())
        total_warnings = sum(h.warning_count for h in self.component_health.values())
        
        # Get resource usage
        memory_usage = 0
        cpu_usage = 0
        try:
            import psutil
            memory = psutil.virtual_memory()
            memory_usage = memory.used / (1024 * 1024)
            cpu_usage = psutil.cpu_percent()
        except:
            pass
        
        return SystemHealth(
            overall_status=self.status,
            components=self.component_health.copy(),
            last_update=self._last_health_check,
            uptime_seconds=uptime,
            total_errors=total_errors,
            total_warnings=total_warnings,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage
        )
    
    def start_production_system(self) -> bool:
        """Start the complete production system"""
        _safe_log(self.logger, 'info', "Starting ICT Engine Production System")
        
        with self._lock:
            if self.status != SystemStatus.STOPPED:
                self.logger.warning("System is not in stopped state")
                return False
            
            self.start_time = datetime.now()
            
            # Initialize components
            if not self.initialize_components():
                self.logger.error("Component initialization failed")
                return False
            
            # Start monitoring
            self.start_monitoring()
            
            # Final status check
            if self.status in [SystemStatus.RUNNING, SystemStatus.WARNING]:
                _safe_log(self.logger, 'info', "Production system started successfully")
                return True
            else:
                self.logger.error("Production system failed to start")
                return False
    
    def shutdown_production_system(self):
        """Safely shutdown the production system"""
        _safe_log(self.logger, 'info', "Shutting down production system")
        
        with self._lock:
            self.status = SystemStatus.SHUTTING_DOWN
            
            # Stop monitoring
            self.stop_monitoring()
            
            # Shutdown components safely
            for name, component in self.components.items():
                try:
                    if hasattr(component, 'shutdown'):
                        component.shutdown()
                    elif hasattr(component, 'disconnect'):
                        component.disconnect()
                    elif hasattr(component, 'close'):
                        component.close()
                    
                    self.logger.info(f"Component {name} shutdown successfully")
                except Exception as e:
                    self.logger.error(f"Error shutting down {name}: {e}")
            
            self.components.clear()
            self.component_health.clear()
            self.status = SystemStatus.STOPPED
            
            _safe_log(self.logger, 'info', "Production system shutdown complete")
    
    def get_component(self, component_name: str) -> Optional[Any]:
        """Get a specific component by name"""
        return self.components.get(component_name)
    
    def is_production_ready(self) -> bool:
        """Check if system is ready for production trading"""
        if self.status not in [SystemStatus.RUNNING, SystemStatus.WARNING]:
            return False
        
        # Check critical components
        critical_components = ["mt5_manager", "risk_manager", "execution_engine"]
        for comp_name in critical_components:
            if comp_name not in self.component_health:
                return False
            if self.component_health[comp_name].status == ComponentStatus.ERROR:
                return False
        
        return True
    
    def export_system_report(self, file_path: Optional[str] = None) -> str:
        """Export comprehensive system report"""
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"production_system_report_{timestamp}.json"
        
        health = self.get_system_health()
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_health": asdict(health),
            "configuration": self.config,
            "performance_history": self._performance_history[-10:],  # Last 10 entries
            "component_details": {
                name: asdict(health_info) 
                for name, health_info in self.component_health.items()
            }
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"System report exported to {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to export report: {e}")
            return ""


# Global instance
_production_manager: Optional[ProductionSystemManager] = None
_manager_lock = threading.Lock()


def get_production_manager(config_path: Optional[str] = None) -> ProductionSystemManager:
    """Get global production system manager"""
    global _production_manager
    
    with _manager_lock:
        if _production_manager is None:
            _production_manager = ProductionSystemManager(config_path)
        return _production_manager


def start_production_system(config_path: Optional[str] = None) -> bool:
    """Start production system (convenience function)"""
    manager = get_production_manager(config_path)
    return manager.start_production_system()


def shutdown_production_system():
    """Shutdown production system (convenience function)"""
    global _production_manager
    
    if _production_manager:
        _production_manager.shutdown_production_system()
        _production_manager = None


def is_production_ready() -> bool:
    """Check if production system is ready"""
    global _production_manager
    
    if _production_manager:
        return _production_manager.is_production_ready()
    return False


if __name__ == "__main__":
    # Test production system manager
    print("🏭 ICT Engine Production System Manager Test")
    print("=" * 50)
    
    manager = get_production_manager()
    
    if manager.start_production_system():
        print("✅ Production system started successfully")
        
        # Display health info
        health = manager.get_system_health()
        print(f"📊 System Status: {health.overall_status.value}")
        print(f"🔧 Components: {len(health.components)}")
        print(f"⚠️ Errors: {health.total_errors}")
        print(f"🚨 Warnings: {health.total_warnings}")
        
        # Wait a bit for monitoring
        print("\n⏳ Running system check...")
        time.sleep(5)
        
        # Export report
        report_path = manager.export_system_report()
        if report_path:
            print(f"📄 Report exported: {report_path}")
        
        # Shutdown
        print("\n🛑 Shutting down system...")
        manager.shutdown_production_system()
        print("✅ Shutdown complete")
    else:
        print("❌ Failed to start production system")
        manager.shutdown_production_system()