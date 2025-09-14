#!/usr/bin/env python3
"""
🏭 PRODUCTION CONFIGURATION - ICT ENGINE v6.0 ENTERPRISE
======================================================

Configuración optimizada para trading en cuenta real.
Define parámetros, límites y thresholds específicos para ambiente de producción,
ajustados para máxima estabilidad, rendimiento y protección de capital.

Características principales:
✅ Configuración por niveles de agresividad (Conservative, Balanced, Aggressive)
✅ Parámetros optimizados para diferentes brokers
✅ Rate limits ajustados a condiciones reales de mercado  
✅ Health monitoring thresholds para alertas críticas
✅ Risk parameters calibrados para cuenta real
✅ Performance baselines y SLA targets
✅ Configuración dinámica según condiciones del mercado

Optimizaciones específicas:
- Latencia targets < 50ms para operaciones críticas
- Rate limits sincronizados con límites del broker
- Memory limits < 512MB para estabilidad 24/7
- CPU usage < 25% en condiciones normales
- Error rates < 2% como máximo aceptable

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 14 Septiembre 2025
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json
import os
import time
from pathlib import Path

# ============================================================================
# PRODUCTION ENVIRONMENT TYPES
# ============================================================================

class TradingProfile(Enum):
    """Perfiles de trading para diferentes estilos"""
    CONSERVATIVE = "conservative"    # Máxima estabilidad, mínimo riesgo
    BALANCED = "balanced"           # Balance entre performance y estabilidad  
    AGGRESSIVE = "aggressive"       # Máxima performance, mayor riesgo

class BrokerType(Enum):
    """Tipos de broker soportados"""
    MT5_STANDARD = "mt5_standard"   # MetaTrader 5 estándar
    MT5_ECN = "mt5_ecn"            # MetaTrader 5 ECN
    MT5_PRO = "mt5_pro"            # MetaTrader 5 Professional
    CUSTOM = "custom"              # Broker personalizado

class MarketCondition(Enum):
    """Condiciones del mercado"""
    NORMAL = "normal"              # Condiciones normales
    HIGH_VOLATILITY = "high_volatility"  # Alta volatilidad
    LOW_LIQUIDITY = "low_liquidity"      # Baja liquidez
    NEWS_EVENT = "news_event"            # Evento de noticias

# ============================================================================
# CONFIGURATION DATACLASSES
# ============================================================================

@dataclass
class RateLimitConfig:
    """Configuración de rate limiting"""
    orders_per_second: int = 5
    orders_per_minute: int = 100
    requests_per_second: int = 20
    data_requests_per_minute: int = 1000
    api_calls_per_hour: int = 5000
    concurrent_orders: int = 50
    burst_allowance_percent: float = 20.0  # 20% extra para bursts

@dataclass
class ValidationConfig:
    """Configuración del validador de producción"""
    enable_caching: bool = True
    cache_size: int = 1000
    validation_level: str = "standard"  # minimal, standard, strict, paranoid
    enable_sanitization: bool = True
    enable_batch_validation: bool = True
    max_batch_size: int = 100

@dataclass
class HealthMonitorConfig:
    """Configuración del monitor de salud"""
    monitoring_level: str = "standard"  # minimal, standard, detailed, debug
    health_check_interval: float = 30.0
    performance_sample_interval: float = 1.0
    enable_auto_recovery: bool = True
    circuit_breaker_enabled: bool = True
    max_concurrent_checks: int = 10
    
    # Thresholds críticos
    cpu_warning_threshold: float = 80.0
    cpu_critical_threshold: float = 95.0
    memory_warning_threshold: float = 85.0
    memory_critical_threshold: float = 95.0
    latency_warning_threshold: float = 100.0  # ms
    latency_critical_threshold: float = 500.0  # ms
    error_rate_warning_threshold: float = 5.0  # %
    error_rate_critical_threshold: float = 15.0  # %

@dataclass
class TradingConfig:
    """Configuración específica de trading"""
    max_position_size: float = 10.0  # Lotes
    max_daily_trades: int = 100
    max_drawdown_percent: float = 5.0
    stop_trading_on_daily_loss: bool = True
    daily_loss_threshold: float = 1000.0  # USD
    enable_position_sizing: bool = True
    risk_per_trade_percent: float = 1.0
    
    # Order Block específico
    min_order_block_strength: float = 7.0
    max_order_blocks_per_symbol: int = 5
    order_block_invalidation_pips: float = 10.0
    
    # Smart Money Concepts
    liquidity_grab_confirmation: bool = True
    structural_break_confirmation: bool = True
    fair_value_gap_min_size: float = 5.0  # pips

@dataclass
class SystemConfig:
    """Configuración general del sistema"""
    enable_production_mode: bool = True
    max_memory_usage_mb: float = 512.0
    max_cpu_usage_percent: float = 25.0
    enable_detailed_logging: bool = True
    log_rotation_enabled: bool = True
    max_log_file_size_mb: int = 100
    keep_log_files_days: int = 30
    
    # Paths y directorios
    data_directory: str = "04-DATA"
    logs_directory: str = "05-LOGS"
    exports_directory: str = "exports"
    backup_enabled: bool = True
    backup_interval_hours: int = 6

# ============================================================================
# PRODUCTION CONFIGURATION PROFILES  
# ============================================================================

class ProductionConfig:
    """
    🏭 Configuración principal para ambiente de producción
    
    Proporciona configuraciones optimizadas para diferentes perfiles
    de trading y condiciones del mercado.
    """
    
    def __init__(self, 
                 profile: TradingProfile = TradingProfile.BALANCED,
                 broker_type: BrokerType = BrokerType.MT5_STANDARD,
                 market_condition: MarketCondition = MarketCondition.NORMAL):
        
        self.profile = profile
        self.broker_type = broker_type
        self.market_condition = market_condition
        
        # Configuraciones específicas
        self.rate_limit = self._get_rate_limit_config()
        self.validation = self._get_validation_config()
        self.health_monitor = self._get_health_monitor_config()
        self.trading = self._get_trading_config()
        self.system = self._get_system_config()
        
    def _get_rate_limit_config(self) -> RateLimitConfig:
        """Obtener configuración de rate limiting según perfil"""
        
        base_configs = {
            TradingProfile.CONSERVATIVE: RateLimitConfig(
                orders_per_second=3,
                orders_per_minute=50,
                requests_per_second=15,
                data_requests_per_minute=800,
                api_calls_per_hour=3000,
                concurrent_orders=25,
                burst_allowance_percent=10.0
            ),
            TradingProfile.BALANCED: RateLimitConfig(
                orders_per_second=5,
                orders_per_minute=100,
                requests_per_second=20,
                data_requests_per_minute=1200,
                api_calls_per_hour=5000,
                concurrent_orders=50,
                burst_allowance_percent=20.0
            ),
            TradingProfile.AGGRESSIVE: RateLimitConfig(
                orders_per_second=8,
                orders_per_minute=150,
                requests_per_second=30,
                data_requests_per_minute=1500,
                api_calls_per_hour=7000,
                concurrent_orders=75,
                burst_allowance_percent=30.0
            )
        }
        
        config = base_configs[self.profile]
        
        # Ajustes por broker
        if self.broker_type == BrokerType.MT5_ECN:
            config.orders_per_second = int(config.orders_per_second * 1.2)
            config.requests_per_second = int(config.requests_per_second * 1.1)
        elif self.broker_type == BrokerType.MT5_PRO:
            config.orders_per_second = int(config.orders_per_second * 1.5)
            config.requests_per_second = int(config.requests_per_second * 1.3)
        
        # Ajustes por condiciones de mercado
        if self.market_condition == MarketCondition.HIGH_VOLATILITY:
            config.orders_per_second = int(config.orders_per_second * 0.8)
            config.burst_allowance_percent *= 0.5
        elif self.market_condition == MarketCondition.LOW_LIQUIDITY:
            config.orders_per_second = int(config.orders_per_second * 0.6)
            config.concurrent_orders = int(config.concurrent_orders * 0.7)
        
        return config
    
    def _get_validation_config(self) -> ValidationConfig:
        """Obtener configuración de validación según perfil"""
        
        base_configs = {
            TradingProfile.CONSERVATIVE: ValidationConfig(
                enable_caching=True,
                cache_size=2000,
                validation_level="strict",
                enable_sanitization=True,
                enable_batch_validation=True,
                max_batch_size=50
            ),
            TradingProfile.BALANCED: ValidationConfig(
                enable_caching=True,
                cache_size=1000,
                validation_level="standard",
                enable_sanitization=True,
                enable_batch_validation=True,
                max_batch_size=100
            ),
            TradingProfile.AGGRESSIVE: ValidationConfig(
                enable_caching=True,
                cache_size=500,
                validation_level="minimal",
                enable_sanitization=False,
                enable_batch_validation=True,
                max_batch_size=200
            )
        }
        
        return base_configs[self.profile]
    
    def _get_health_monitor_config(self) -> HealthMonitorConfig:
        """Obtener configuración de health monitoring según perfil"""
        
        base_configs = {
            TradingProfile.CONSERVATIVE: HealthMonitorConfig(
                monitoring_level="detailed",
                health_check_interval=15.0,
                performance_sample_interval=0.5,
                enable_auto_recovery=True,
                circuit_breaker_enabled=True,
                max_concurrent_checks=15,
                cpu_warning_threshold=60.0,
                cpu_critical_threshold=80.0,
                memory_warning_threshold=70.0,
                memory_critical_threshold=85.0,
                latency_warning_threshold=50.0,
                latency_critical_threshold=200.0,
                error_rate_warning_threshold=2.0,
                error_rate_critical_threshold=5.0
            ),
            TradingProfile.BALANCED: HealthMonitorConfig(
                monitoring_level="standard",
                health_check_interval=30.0,
                performance_sample_interval=1.0,
                enable_auto_recovery=True,
                circuit_breaker_enabled=True,
                max_concurrent_checks=10,
                cpu_warning_threshold=80.0,
                cpu_critical_threshold=95.0,
                memory_warning_threshold=85.0,
                memory_critical_threshold=95.0,
                latency_warning_threshold=100.0,
                latency_critical_threshold=500.0,
                error_rate_warning_threshold=5.0,
                error_rate_critical_threshold=15.0
            ),
            TradingProfile.AGGRESSIVE: HealthMonitorConfig(
                monitoring_level="minimal",
                health_check_interval=60.0,
                performance_sample_interval=2.0,
                enable_auto_recovery=False,
                circuit_breaker_enabled=False,
                max_concurrent_checks=5,
                cpu_warning_threshold=90.0,
                cpu_critical_threshold=98.0,
                memory_warning_threshold=90.0,
                memory_critical_threshold=98.0,
                latency_warning_threshold=200.0,
                latency_critical_threshold=1000.0,
                error_rate_warning_threshold=10.0,
                error_rate_critical_threshold=25.0
            )
        }
        
        return base_configs[self.profile]
    
    def _get_trading_config(self) -> TradingConfig:
        """Obtener configuración de trading según perfil"""
        
        base_configs = {
            TradingProfile.CONSERVATIVE: TradingConfig(
                max_position_size=5.0,
                max_daily_trades=50,
                max_drawdown_percent=3.0,
                stop_trading_on_daily_loss=True,
                daily_loss_threshold=500.0,
                enable_position_sizing=True,
                risk_per_trade_percent=0.5,
                min_order_block_strength=8.0,
                max_order_blocks_per_symbol=3,
                order_block_invalidation_pips=8.0,
                liquidity_grab_confirmation=True,
                structural_break_confirmation=True,
                fair_value_gap_min_size=8.0
            ),
            TradingProfile.BALANCED: TradingConfig(
                max_position_size=10.0,
                max_daily_trades=100,
                max_drawdown_percent=5.0,
                stop_trading_on_daily_loss=True,
                daily_loss_threshold=1000.0,
                enable_position_sizing=True,
                risk_per_trade_percent=1.0,
                min_order_block_strength=7.0,
                max_order_blocks_per_symbol=5,
                order_block_invalidation_pips=10.0,
                liquidity_grab_confirmation=True,
                structural_break_confirmation=True,
                fair_value_gap_min_size=5.0
            ),
            TradingProfile.AGGRESSIVE: TradingConfig(
                max_position_size=20.0,
                max_daily_trades=200,
                max_drawdown_percent=8.0,
                stop_trading_on_daily_loss=False,
                daily_loss_threshold=2000.0,
                enable_position_sizing=True,
                risk_per_trade_percent=2.0,
                min_order_block_strength=6.0,
                max_order_blocks_per_symbol=8,
                order_block_invalidation_pips=15.0,
                liquidity_grab_confirmation=False,
                structural_break_confirmation=False,
                fair_value_gap_min_size=3.0
            )
        }
        
        return base_configs[self.profile]
    
    def _get_system_config(self) -> SystemConfig:
        """Obtener configuración del sistema según perfil"""
        
        base_configs = {
            TradingProfile.CONSERVATIVE: SystemConfig(
                enable_production_mode=True,
                max_memory_usage_mb=256.0,
                max_cpu_usage_percent=15.0,
                enable_detailed_logging=True,
                log_rotation_enabled=True,
                max_log_file_size_mb=50,
                keep_log_files_days=60,
                backup_enabled=True,
                backup_interval_hours=3
            ),
            TradingProfile.BALANCED: SystemConfig(
                enable_production_mode=True,
                max_memory_usage_mb=512.0,
                max_cpu_usage_percent=25.0,
                enable_detailed_logging=True,
                log_rotation_enabled=True,
                max_log_file_size_mb=100,
                keep_log_files_days=30,
                backup_enabled=True,
                backup_interval_hours=6
            ),
            TradingProfile.AGGRESSIVE: SystemConfig(
                enable_production_mode=True,
                max_memory_usage_mb=1024.0,
                max_cpu_usage_percent=40.0,
                enable_detailed_logging=False,
                log_rotation_enabled=True,
                max_log_file_size_mb=200,
                keep_log_files_days=15,
                backup_enabled=True,
                backup_interval_hours=12
            )
        }
        
        return base_configs[self.profile]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir configuración a diccionario"""
        return {
            'profile': self.profile.value,
            'broker_type': self.broker_type.value,
            'market_condition': self.market_condition.value,
            'rate_limit': {
                'orders_per_second': self.rate_limit.orders_per_second,
                'orders_per_minute': self.rate_limit.orders_per_minute,
                'requests_per_second': self.rate_limit.requests_per_second,
                'data_requests_per_minute': self.rate_limit.data_requests_per_minute,
                'api_calls_per_hour': self.rate_limit.api_calls_per_hour,
                'concurrent_orders': self.rate_limit.concurrent_orders,
                'burst_allowance_percent': self.rate_limit.burst_allowance_percent
            },
            'validation': {
                'enable_caching': self.validation.enable_caching,
                'cache_size': self.validation.cache_size,
                'validation_level': self.validation.validation_level,
                'enable_sanitization': self.validation.enable_sanitization,
                'enable_batch_validation': self.validation.enable_batch_validation,
                'max_batch_size': self.validation.max_batch_size
            },
            'health_monitor': {
                'monitoring_level': self.health_monitor.monitoring_level,
                'health_check_interval': self.health_monitor.health_check_interval,
                'performance_sample_interval': self.health_monitor.performance_sample_interval,
                'enable_auto_recovery': self.health_monitor.enable_auto_recovery,
                'circuit_breaker_enabled': self.health_monitor.circuit_breaker_enabled,
                'max_concurrent_checks': self.health_monitor.max_concurrent_checks,
                'thresholds': {
                    'cpu_warning': self.health_monitor.cpu_warning_threshold,
                    'cpu_critical': self.health_monitor.cpu_critical_threshold,
                    'memory_warning': self.health_monitor.memory_warning_threshold,
                    'memory_critical': self.health_monitor.memory_critical_threshold,
                    'latency_warning': self.health_monitor.latency_warning_threshold,
                    'latency_critical': self.health_monitor.latency_critical_threshold,
                    'error_rate_warning': self.health_monitor.error_rate_warning_threshold,
                    'error_rate_critical': self.health_monitor.error_rate_critical_threshold
                }
            },
            'trading': {
                'max_position_size': self.trading.max_position_size,
                'max_daily_trades': self.trading.max_daily_trades,
                'max_drawdown_percent': self.trading.max_drawdown_percent,
                'stop_trading_on_daily_loss': self.trading.stop_trading_on_daily_loss,
                'daily_loss_threshold': self.trading.daily_loss_threshold,
                'enable_position_sizing': self.trading.enable_position_sizing,
                'risk_per_trade_percent': self.trading.risk_per_trade_percent,
                'order_blocks': {
                    'min_strength': self.trading.min_order_block_strength,
                    'max_per_symbol': self.trading.max_order_blocks_per_symbol,
                    'invalidation_pips': self.trading.order_block_invalidation_pips
                },
                'smart_money': {
                    'liquidity_grab_confirmation': self.trading.liquidity_grab_confirmation,
                    'structural_break_confirmation': self.trading.structural_break_confirmation,
                    'fvg_min_size': self.trading.fair_value_gap_min_size
                }
            },
            'system': {
                'enable_production_mode': self.system.enable_production_mode,
                'max_memory_usage_mb': self.system.max_memory_usage_mb,
                'max_cpu_usage_percent': self.system.max_cpu_usage_percent,
                'enable_detailed_logging': self.system.enable_detailed_logging,
                'log_rotation_enabled': self.system.log_rotation_enabled,
                'max_log_file_size_mb': self.system.max_log_file_size_mb,
                'keep_log_files_days': self.system.keep_log_files_days,
                'backup_enabled': self.system.backup_enabled,
                'backup_interval_hours': self.system.backup_interval_hours
            }
        }
    
    def save_to_file(self, filepath: str):
        """Guardar configuración a archivo JSON"""
        config_dict = self.to_dict()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'ProductionConfig':
        """Cargar configuración desde archivo JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        
        # Crear instancia con valores del archivo
        profile = TradingProfile(config_dict.get('profile', 'balanced'))
        broker_type = BrokerType(config_dict.get('broker_type', 'mt5_standard'))
        market_condition = MarketCondition(config_dict.get('market_condition', 'normal'))
        
        return cls(profile=profile, broker_type=broker_type, market_condition=market_condition)

# ============================================================================
# CONFIGURATION FACTORY FUNCTIONS
# ============================================================================

def get_conservative_config(broker_type: BrokerType = BrokerType.MT5_STANDARD) -> ProductionConfig:
    """Obtener configuración conservadora para máxima estabilidad"""
    return ProductionConfig(
        profile=TradingProfile.CONSERVATIVE,
        broker_type=broker_type,
        market_condition=MarketCondition.NORMAL
    )

def get_balanced_config(broker_type: BrokerType = BrokerType.MT5_STANDARD) -> ProductionConfig:
    """Obtener configuración balanceada para uso general"""
    return ProductionConfig(
        profile=TradingProfile.BALANCED,
        broker_type=broker_type,
        market_condition=MarketCondition.NORMAL
    )

def get_aggressive_config(broker_type: BrokerType = BrokerType.MT5_STANDARD) -> ProductionConfig:
    """Obtener configuración agresiva para máximo rendimiento"""
    return ProductionConfig(
        profile=TradingProfile.AGGRESSIVE,
        broker_type=broker_type,
        market_condition=MarketCondition.NORMAL
    )

def get_config_for_market_condition(condition: MarketCondition, 
                                    base_profile: TradingProfile = TradingProfile.BALANCED) -> ProductionConfig:
    """Obtener configuración optimizada para condición específica del mercado"""
    return ProductionConfig(
        profile=base_profile,
        broker_type=BrokerType.MT5_STANDARD,
        market_condition=condition
    )

# ============================================================================
# CONFIGURATION MANAGER
# ============================================================================

class ConfigurationManager:
    """
    🔧 Gestor de configuraciones para el sistema de producción
    
    Maneja múltiples configuraciones, cambios dinámicos y
    persistencia de configuraciones personalizadas.
    """
    
    def __init__(self, config_directory: str = "01-CORE/config"):
        self.config_directory = Path(config_directory)
        self.config_directory.mkdir(parents=True, exist_ok=True)
        
        self.current_config: Optional[ProductionConfig] = None
        self.config_history: List[Dict[str, Any]] = []
        
    def load_default_config(self, profile: TradingProfile = TradingProfile.BALANCED) -> ProductionConfig:
        """Cargar configuración por defecto"""
        self.current_config = ProductionConfig(profile=profile)
        return self.current_config
    
    def load_config_from_file(self, filename: str) -> ProductionConfig:
        """Cargar configuración desde archivo"""
        filepath = self.config_directory / filename
        if filepath.exists():
            self.current_config = ProductionConfig.load_from_file(str(filepath))
        else:
            # Si no existe, crear con valores por defecto
            self.current_config = ProductionConfig()
            self.save_config_to_file(filename)
        
        return self.current_config
    
    def save_config_to_file(self, filename: str):
        """Guardar configuración actual a archivo"""
        if self.current_config:
            filepath = self.config_directory / filename
            self.current_config.save_to_file(str(filepath))
    
    def update_market_condition(self, condition: MarketCondition):
        """Actualizar condición del mercado dinámicamente"""
        if self.current_config:
            # Guardar configuración actual en historial
            self.config_history.append({
                'timestamp': time.time(),
                'config': self.current_config.to_dict()
            })
            
            # Crear nueva configuración con condición actualizada
            self.current_config = ProductionConfig(
                profile=self.current_config.profile,
                broker_type=self.current_config.broker_type,
                market_condition=condition
            )
    
    def get_current_config(self) -> Optional[ProductionConfig]:
        """Obtener configuración actual"""
        return self.current_config
    
    def list_saved_configs(self) -> List[str]:
        """Listar configuraciones guardadas"""
        if self.config_directory.exists():
            return [f.name for f in self.config_directory.glob("*.json")]
        return []

# ============================================================================
# GLOBAL CONFIGURATION INSTANCE
# ============================================================================

# Instancia global del gestor de configuraciones
_global_config_manager = None

def get_config_manager() -> ConfigurationManager:
    """Obtener instancia global del gestor de configuraciones"""
    global _global_config_manager
    
    if _global_config_manager is None:
        _global_config_manager = ConfigurationManager()
    
    return _global_config_manager

def get_production_config(profile: TradingProfile = TradingProfile.BALANCED,
                         broker_type: BrokerType = BrokerType.MT5_STANDARD) -> ProductionConfig:
    """Obtener configuración de producción optimizada"""
    return ProductionConfig(profile=profile, broker_type=broker_type)

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'TradingProfile',
    'BrokerType', 
    'MarketCondition',
    'RateLimitConfig',
    'ValidationConfig',
    'HealthMonitorConfig',
    'TradingConfig',
    'SystemConfig',
    'ProductionConfig',
    'ConfigurationManager',
    'get_conservative_config',
    'get_balanced_config',
    'get_aggressive_config',
    'get_config_for_market_condition',
    'get_config_manager',
    'get_production_config'
]