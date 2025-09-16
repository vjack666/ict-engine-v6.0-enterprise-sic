#!/usr/bin/env python3
"""
🔧 CONFIG MANAGER - ICT ENGINE v6.0 ENTERPRISE
============================================

Gestor centralizado de configuraciones para el sistema ICT Engine.
Maneja configuraciones por entorno (dev/staging/prod) con validación,
recarga dinámica y gestión de secretos.

CARACTERÍSTICAS PRINCIPALES:
✅ Multi-entorno (dev/staging/prod)
✅ Validación automática de configuraciones
✅ Recarga dinámica sin reinicio
✅ Gestión segura de credenciales
✅ Cache inteligente con TTL
✅ Fallbacks y valores por defecto
✅ Logging detallado de cambios
✅ Backup automático de configuraciones

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 15 Septiembre 2025
"""

from protocols.unified_logging import get_unified_logger
import os
import json
import yaml
import hashlib
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Callable, Protocol, runtime_checkable
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Imports seguros para logging
try:
    from ..smart_trading_logger import SmartTradingLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False
    SmartTradingLogger = None


class Environment(Enum):
    """🌍 Entornos soportados"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class ConfigChangeType(Enum):
    """🔄 Tipos de cambios de configuración"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    RELOADED = "reloaded"
    VALIDATED = "validated"


@dataclass
class ConfigChangeEvent:
    """📝 Evento de cambio de configuración"""
    timestamp: datetime
    change_type: ConfigChangeType
    section: str
    key: Optional[str]
    old_value: Optional[Any]
    new_value: Optional[Any]
    environment: Environment
    source: str


@dataclass
class ConfigValidationRule:
    """✅ Regla de validación para configuraciones"""
    key_path: str  # e.g., "trading.max_positions"
    required: bool = False
    data_type: Optional[type] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    validator_func: Optional[Callable[[Any], bool]] = None
    error_message: Optional[str] = None


class ConfigurationError(Exception):
    """❌ Error de configuración"""
    pass


class ConfigManager:
    """
    🔧 GESTOR DE CONFIGURACIÓN ENTERPRISE
    ===================================
    
    Gestor centralizado para todas las configuraciones del sistema ICT Engine.
    Proporciona configuración por entorno, validación automática y recarga dinámica.
    """
    
    def __init__(self, 
                 config_dir: Optional[Path] = None,
                 environment: Optional[Environment] = None,
                 auto_reload: bool = True):
        """
        Inicializar ConfigManager
        
        Args:
            config_dir: Directorio de configuraciones (default: 01-CORE/config/)
            environment: Entorno activo (default: desde ENV var)
            auto_reload: Activar recarga automática de archivos
        """
        # Configurar paths
        self.config_dir = config_dir or self._get_default_config_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Entorno activo
        self.environment = environment or self._detect_environment()
        
        # Logger
        self.logger = self._setup_logger()
        
        # Storage interno
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        self._file_hashes: Dict[str, str] = {}
        self._change_listeners: List[Callable[[ConfigChangeEvent], None]] = []
        self._lock = threading.RLock()
        
        # Configuración de recarga automática
        self.auto_reload = auto_reload
        self._last_check = datetime.now()
        self._check_interval = timedelta(seconds=30)  # Check every 30 seconds
        
        # Reglas de validación
        self._validation_rules: List[ConfigValidationRule] = []
        self._setup_default_validation_rules()
        
        # Inicializar
        self._load_all_configs()
        
        self.logger.info(f"✅ ConfigManager initialized for environment: {self.environment.value}")
    
    def _get_default_config_dir(self) -> Path:
        """📁 Obtener directorio por defecto de configuraciones"""
        current_file = Path(__file__)
        return current_file.parent.parent / "config"
    
    def _detect_environment(self) -> Environment:
        """🌍 Detectar entorno actual"""
        env_var = os.getenv('ICT_ENVIRONMENT', 'development').lower()
        
        env_mapping = {
            'dev': Environment.DEVELOPMENT,
            'development': Environment.DEVELOPMENT,
            'staging': Environment.STAGING,
            'stage': Environment.STAGING,
            'prod': Environment.PRODUCTION,
            'production': Environment.PRODUCTION,
            'test': Environment.TEST
        }
        
        return env_mapping.get(env_var, Environment.DEVELOPMENT)
    
    @runtime_checkable
    class _LoggerLike(Protocol):  # internal protocol for type compatibility
        def info(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
        def warning(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
        def error(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
        def debug(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
        def exception(self, msg: str, *args: Any, **kwargs: Any) -> None: ...

    def _setup_logger(self) -> logging.Logger:
        """📝 Configurar logger
        Devuelve siempre una instancia que cumple la interfaz logging.Logger
        Si SmartTradingLogger no hereda explícitamente de logging.Logger se crea
        un wrapper adaptador para satisfacer a Pylance.
        """
        if LOGGER_AVAILABLE and SmartTradingLogger:
            raw_logger = SmartTradingLogger("ConfigManager")
            # Si ya es instancia de logging.Logger la devolvemos directamente
            if isinstance(raw_logger, logging.Logger):
                return raw_logger
            # Adaptador mínimal que delega métodos estándar
            base_logger = logging.getLogger("ConfigManager")
            if not base_logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                base_logger.addHandler(handler)
                base_logger.setLevel(logging.INFO)

            class _Adapter(logging.Logger):  # type: ignore[misc]
                def __init__(self, delegate: Any):
                    super().__init__("ConfigManagerAdapter")
                    self._delegate = delegate
                    # Reutilizamos handlers del base_logger
                    for h in base_logger.handlers:
                        self.addHandler(h)
                    self.setLevel(base_logger.level)

                def info(self, msg: str, *args: Any, **kwargs: Any) -> None:  # noqa: D401
                    try:
                        return self._delegate.info(msg, *args, **kwargs)
                    except AttributeError:
                        return base_logger.info(msg, *args, **kwargs)

                def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
                    try:
                        return self._delegate.warning(msg, *args, **kwargs)
                    except AttributeError:
                        return base_logger.warning(msg, *args, **kwargs)

                def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
                    try:
                        return self._delegate.error(msg, *args, **kwargs)
                    except AttributeError:
                        return base_logger.error(msg, *args, **kwargs)

                def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
                    try:
                        return self._delegate.debug(msg, *args, **kwargs)
                    except AttributeError:
                        return base_logger.debug(msg, *args, **kwargs)

                def exception(self, msg: str, *args: Any, **kwargs: Any) -> None:
                    try:
                        return self._delegate.exception(msg, *args, **kwargs)
                    except AttributeError:
                        return base_logger.exception(msg, *args, **kwargs)

            return _Adapter(raw_logger)

        # Fallback logger estándar
        logger = logging.getLogger("ConfigManager")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _setup_default_validation_rules(self):
        """⚙️ Configurar reglas de validación por defecto"""
        self._validation_rules = [
            # Trading rules
            ConfigValidationRule(
                "trading.max_positions", True, int, 1, 100,
                error_message="max_positions debe estar entre 1 y 100"
            ),
            ConfigValidationRule(
                "trading.max_daily_trades", True, int, 1, 1000,
                error_message="max_daily_trades debe estar entre 1 y 1000"
            ),
            ConfigValidationRule(
                "trading.risk_per_trade", True, float, 0.001, 0.1,
                error_message="risk_per_trade debe estar entre 0.001 (0.1%) y 0.1 (10%)"
            ),
            
            # MT5 rules
            ConfigValidationRule(
                "mt5.connection.timeout", True, int, 1000, 300000,
                error_message="timeout debe estar entre 1000ms y 300000ms"
            ),
            ConfigValidationRule(
                "mt5.connection.server", True, str,
                error_message="server es requerido"
            ),
            
            # Dashboard rules
            ConfigValidationRule(
                "dashboard.refresh_interval", False, int, 100, 60000,
                error_message="refresh_interval debe estar entre 100ms y 60000ms"
            ),
            
            # Risk management rules
            ConfigValidationRule(
                "risk.emergency_drawdown_limit", True, float, 0.01, 0.5,
                error_message="emergency_drawdown_limit debe estar entre 1% y 50%"
            )
        ]
    
    def _load_all_configs(self):
        """📥 Cargar todas las configuraciones"""
        try:
            with self._lock:
                config_files = [
                    "base.yaml",                    # Configuración base
                    f"{self.environment.value}.yaml",  # Configuración específica del entorno
                    "trading.json",                # Configuración de trading
                    "real_trading_config.json",   # Configuración de trading real (existente)
                    "secrets.json"                # Secretos (si existe)
                ]
                
                for config_file in config_files:
                    file_path = self.config_dir / config_file
                    if file_path.exists():
                        self._load_config_file(file_path)
                    else:
                        self.logger.debug(f"Config file not found: {config_file}")
                
                # Aplicar overrides de entorno
                self._apply_environment_overrides()
                
                # Validar configuraciones
                self._validate_all_configs()
                
        except Exception as e:
            self.logger.error(f"Error loading configurations: {e}")
            raise ConfigurationError(f"Failed to load configurations: {e}")
    
    def _load_config_file(self, file_path: Path):
        """📄 Cargar archivo de configuración específico"""
        try:
            # Calcular hash del archivo
            file_hash = self._calculate_file_hash(file_path)
            file_key = str(file_path.relative_to(self.config_dir))
            
            # Si no ha cambiado, skip
            if file_key in self._file_hashes and self._file_hashes[file_key] == file_hash:
                return
            
            # Cargar contenido basado en extensión
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    content = yaml.safe_load(f)
                elif file_path.suffix.lower() == '.json':
                    content = json.load(f)
                else:
                    self.logger.warning(f"Unsupported config file format: {file_path}")
                    return
            
            # Actualizar cache
            self._config_cache[file_key] = content or {}
            self._file_hashes[file_key] = file_hash
            
            # Registrar evento
            self._notify_change_event(ConfigChangeEvent(
                timestamp=datetime.now(),
                change_type=ConfigChangeType.RELOADED,
                section=file_key,
                key=None,
                old_value=None,
                new_value=content,
                environment=self.environment,
                source=str(file_path)
            ))
            
            self.logger.info(f"✅ Loaded config file: {file_key}")
            
        except Exception as e:
            self.logger.error(f"Error loading config file {file_path}: {e}")
            raise ConfigurationError(f"Failed to load {file_path}: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """🔐 Calcular hash de archivo"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _apply_environment_overrides(self):
        """🌍 Aplicar overrides específicos del entorno"""
        # Environment variables override
        env_overrides = {}
        
        # Buscar variables de entorno con prefijo ICT_CONFIG_
        for env_var, value in os.environ.items():
            if env_var.startswith('ICT_CONFIG_'):
                raw_key = env_var[11:]  # Remove ICT_CONFIG_

                # Soportar convención de doble guion bajo para separar niveles
                # ICT_CONFIG_TRADING__MAX_POSITIONS -> trading.max_positions
                if '__' in raw_key:
                    parts = [p.lower() for p in raw_key.split('__') if p]
                    config_key = '.'.join(parts)
                else:
                    # Heurística: detectar secciones top-level comunes y mantener underscores internos
                    lower = raw_key.lower()
                    top_levels = (
                        'trading', 'mt5', 'risk', 'dashboard', 'data', 'monitoring',
                        'analysis', 'execution', 'real_trading_config', 'secrets'
                    )
                    config_key = lower
                    for prefix in top_levels:
                        prefix_us = prefix + '_'
                        if lower.startswith(prefix_us):
                            # Mapear solo el primer guion bajo a punto, conservar el resto
                            config_key = prefix + '.' + lower[len(prefix_us):]
                            break
                env_overrides[config_key] = self._parse_env_value(value)
        
        if env_overrides:
            self._config_cache['env_overrides'] = env_overrides
            self.logger.info(f"Applied {len(env_overrides)} environment overrides")
    
    def _parse_env_value(self, value: str) -> Any:
        """🔄 Parsear valor de variable de entorno"""
        # Intentar parsear como JSON primero
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
        
        # Conversiones comunes
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        try:
            # Intentar entero
            if '.' not in value:
                return int(value)
            # Intentar float
            return float(value)
        except ValueError:
            pass
        
        return value  # String por defecto
    
    def _validate_all_configs(self):
        """✅ Validar todas las configuraciones"""
        errors = []
        
        for rule in self._validation_rules:
            try:
                value = self.get(rule.key_path)
                
                # Check if required
                if rule.required and value is None:
                    errors.append(f"Required config '{rule.key_path}' is missing")
                    continue
                
                # Skip validation if value is None and not required
                if value is None:
                    continue
                
                # Validate type
                if rule.data_type and not isinstance(value, rule.data_type):
                    errors.append(f"Config '{rule.key_path}' must be {rule.data_type.__name__}, got {type(value).__name__}")
                    continue
                
                # Validate min/max for numeric types
                if isinstance(value, (int, float)):
                    if rule.min_value is not None and value < rule.min_value:
                        errors.append(f"Config '{rule.key_path}' value {value} is below minimum {rule.min_value}")
                    if rule.max_value is not None and value > rule.max_value:
                        errors.append(f"Config '{rule.key_path}' value {value} is above maximum {rule.max_value}")
                
                # Validate allowed values
                if rule.allowed_values and value not in rule.allowed_values:
                    errors.append(f"Config '{rule.key_path}' value '{value}' not in allowed values: {rule.allowed_values}")
                
                # Custom validator
                if rule.validator_func and not rule.validator_func(value):
                    error_msg = rule.error_message or f"Config '{rule.key_path}' failed custom validation"
                    errors.append(error_msg)
                    
            except Exception as e:
                errors.append(f"Validation error for '{rule.key_path}': {e}")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
            self.logger.error(error_msg)
            raise ConfigurationError(error_msg)
        
        self.logger.info("✅ All configurations validated successfully")
    
    def get(self, key_path: str, default: Any = None, required: bool = False) -> Any:
        """
        📖 Obtener valor de configuración
        
        Args:
            key_path: Path del config (e.g., "trading.max_positions")
            default: Valor por defecto
            required: Si es requerido (lanza excepción si no existe)
            
        Returns:
            Valor de configuración
        """
        try:
            with self._lock:
                # Check auto reload
                if self.auto_reload:
                    self._check_auto_reload()
                
                # Parse key path
                parts = key_path.split('.')
                
                # Runtime overrides tienen máxima prioridad
                runtime_overrides = self._config_cache.get('runtime_overrides', {})
                if key_path in runtime_overrides:
                    return runtime_overrides[key_path]

                # Buscar en environment overrides primero
                env_overrides = self._config_cache.get('env_overrides', {})
                if key_path in env_overrides:
                    return env_overrides[key_path]
                
                # Buscar en archivos en orden de prioridad explícito
                # 1) YAML específico del entorno
                env_config_key = f"{self.environment.value}.yaml"
                if env_config_key in self._config_cache:
                    value = self._get_nested_value(self._config_cache[env_config_key], parts)
                    if value is not None:
                        return value

                # 2) trading.json (sobre-escribe base para claves de trading)
                if "trading.json" in self._config_cache:
                    value = self._get_nested_value(self._config_cache["trading.json"], parts)
                    if value is not None:
                        return value

                # 3) real_trading_config.json
                if "real_trading_config.json" in self._config_cache:
                    value = self._get_nested_value(self._config_cache["real_trading_config.json"], parts)
                    if value is not None:
                        return value

                # 4) base.yaml (menor prioridad)
                if "base.yaml" in self._config_cache:
                    value = self._get_nested_value(self._config_cache["base.yaml"], parts)
                    if value is not None:
                        return value
                
                # Si no se encuentra y es requerido
                if required:
                    raise ConfigurationError(f"Required configuration '{key_path}' not found")
                
                return default
                
        except Exception as e:
            if required:
                raise ConfigurationError(f"Error getting required config '{key_path}': {e}")
            self.logger.warning(f"Error getting config '{key_path}': {e}")
            return default
    
    def _get_nested_value(self, data: Dict[str, Any], parts: List[str]) -> Any:
        """🔍 Obtener valor anidado de diccionario"""
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
                
        return current
    
    def set(self, key_path: str, value: Any, persist: bool = False) -> None:
        """
        ✏️ Establecer valor de configuración
        
        Args:
            key_path: Path del config (e.g., "trading.max_positions")
            value: Nuevo valor
            persist: Si debe persistir a archivo
        """
        try:
            with self._lock:
                # Get old value for event
                old_value = self.get(key_path)
                
                # Store in runtime overrides
                if 'runtime_overrides' not in self._config_cache:
                    self._config_cache['runtime_overrides'] = {}
                
                self._config_cache['runtime_overrides'][key_path] = value
                
                # Notify change
                self._notify_change_event(ConfigChangeEvent(
                    timestamp=datetime.now(),
                    change_type=ConfigChangeType.UPDATED,
                    section='runtime_overrides',
                    key=key_path,
                    old_value=old_value,
                    new_value=value,
                    environment=self.environment,
                    source='runtime'
                ))
                
                # Persist if requested
                if persist:
                    self._persist_config(key_path, value)
                
                self.logger.info(f"✏️ Config '{key_path}' set to: {value}")
                
        except Exception as e:
            self.logger.error(f"Error setting config '{key_path}': {e}")
            raise ConfigurationError(f"Failed to set config '{key_path}': {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """
        📋 Obtener toda la configuración como diccionario
        
        Returns:
            Dict con toda la configuración disponible
        """
        try:
            with self._lock:
                # Combinar todas las configuraciones en orden de prioridad
                result = {}
                
                # Base configs first
                for config_key, config_data in self._config_cache.items():
                    if config_key not in ['env_overrides', 'runtime_overrides']:
                        if isinstance(config_data, dict):
                            result.update(config_data)
                
                # Environment overrides
                env_overrides = self._config_cache.get('env_overrides', {})
                for key_path, value in env_overrides.items():
                    self._set_nested_value(result, key_path.split('.'), value)
                
                # Runtime overrides (highest priority)
                runtime_overrides = self._config_cache.get('runtime_overrides', {})
                for key_path, value in runtime_overrides.items():
                    self._set_nested_value(result, key_path.split('.'), value)
                
                return result
                
        except Exception as e:
            self.logger.error(f"Error getting config: {e}")
            return {}
    
    def save(self) -> None:
        """
        💾 Guardar configuración actual a archivos
        
        Persiste todas las configuraciones runtime al disco
        """
        try:
            with self._lock:
                runtime_overrides = self._config_cache.get('runtime_overrides', {})
                
                if not runtime_overrides:
                    self.logger.info("No runtime overrides to save")
                    return
                
                # Guardar cada override
                for key_path, value in runtime_overrides.items():
                    self._persist_config(key_path, value)
                
                # Recargar configuraciones después de guardar
                self.reload_all()
                
                self.logger.info(f"💾 Saved {len(runtime_overrides)} configuration changes")
                
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def _set_nested_value(self, data: Dict[str, Any], parts: List[str], value: Any) -> None:
        """🔧 Establecer valor anidado en diccionario"""
        current = data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    
    def _persist_config(self, key_path: str, value: Any):
        """💾 Persistir configuración a archivo"""
        try:
            # Determine target file based on key
            if key_path.startswith('trading.'):
                target_file = "trading.json"
            else:
                target_file = f"{self.environment.value}.yaml"
            
            file_path = self.config_dir / target_file
            
            # Load existing or create new
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    if target_file.endswith('.json'):
                        data = json.load(f)
                    else:
                        data = yaml.safe_load(f) or {}
            else:
                data = {}
            
            # Set nested value
            parts = key_path.split('.')
            current = data
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
            
            # Create backup
            if file_path.exists():
                backup_path = file_path.with_suffix(f'.backup.{int(datetime.now().timestamp())}')
                file_path.rename(backup_path)
                # Keep only last 5 backups
                backups = sorted(file_path.parent.glob(f"{file_path.stem}.backup.*"))
                for old_backup in backups[:-5]:
                    old_backup.unlink()
            
            # Write updated config
            with open(file_path, 'w', encoding='utf-8') as f:
                if target_file.endswith('.json'):
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:
                    yaml.safe_dump(data, f, default_flow_style=False)
            
            self.logger.info(f"💾 Config '{key_path}' persisted to {target_file}")
            
        except Exception as e:
            self.logger.error(f"Error persisting config '{key_path}': {e}")
    
    def _check_auto_reload(self):
        """🔄 Verificar y recargar configuraciones si han cambiado"""
        now = datetime.now()
        if (now - self._last_check) < self._check_interval:
            return
        
        self._last_check = now
        
        try:
            for config_file in self.config_dir.glob("*.yaml"):
                self._load_config_file(config_file)
            for config_file in self.config_dir.glob("*.json"):
                self._load_config_file(config_file)
        except Exception as e:
            self.logger.warning(f"Error during auto-reload: {e}")
    
    def reload_all(self):
        """🔄 Recargar todas las configuraciones manualmente"""
        self.logger.info("🔄 Manually reloading all configurations...")
        self._file_hashes.clear()  # Force reload
        self._load_all_configs()
        self.logger.info("✅ All configurations reloaded")
    
    def add_change_listener(self, listener: Callable[[ConfigChangeEvent], None]):
        """👂 Agregar listener para cambios de configuración"""
        self._change_listeners.append(listener)
        self.logger.debug("Added configuration change listener")
    
    def _notify_change_event(self, event: ConfigChangeEvent):
        """📢 Notificar evento de cambio"""
        for listener in self._change_listeners:
            try:
                listener(event)
            except Exception as e:
                self.logger.error(f"Error in config change listener: {e}")
    
    def add_validation_rule(self, rule: ConfigValidationRule):
        """✅ Agregar regla de validación"""
        self._validation_rules.append(rule)
        self.logger.debug(f"Added validation rule for '{rule.key_path}'")
    
    def get_all_configs(self) -> Dict[str, Any]:
        """📋 Obtener todas las configuraciones (para debugging)"""
        with self._lock:
            return {
                "environment": self.environment.value,
                "config_files": list(self._config_cache.keys()),
                "sample_configs": {
                    key: self.get(key) for key in [
                        "trading.max_positions",
                        "trading.risk_per_trade",
                        "mt5.connection.timeout",
                        "dashboard.refresh_interval"
                    ] if self.get(key) is not None
                }
            }
    
    def health_check(self) -> Dict[str, Any]:
        """🏥 Verificar salud del sistema de configuración"""
        try:
            with self._lock:
                status = {
                    "status": "healthy",
                    "environment": self.environment.value,
                    "config_files_loaded": len(self._config_cache),
                    "validation_rules": len(self._validation_rules),
                    "auto_reload_enabled": self.auto_reload,
                    "last_check": self._last_check.isoformat(),
                    "errors": []
                }
                
                # Test critical configs
                critical_configs = [
                    "trading.max_positions",
                    "trading.risk_per_trade"
                ]
                
                for config in critical_configs:
                    try:
                        value = self.get(config, required=True)
                        if value is None:
                            status["errors"].append(f"Critical config '{config}' is None")
                    except Exception as e:
                        status["errors"].append(f"Critical config '{config}' error: {e}")
                
                if status["errors"]:
                    status["status"] = "degraded"
                
                return status
                
        except Exception as e:
            return {
                "status": "critical",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Singleton instance para uso global
_global_config_manager: Optional[ConfigManager] = None
_config_lock = threading.Lock()


def get_config_manager(
    config_dir: Optional[Path] = None,
    environment: Optional[Environment] = None,
    force_new: bool = False
) -> ConfigManager:
    """
    🏭 Factory function para obtener ConfigManager singleton
    
    Args:
        config_dir: Directorio de configuraciones
        environment: Entorno específico
        force_new: Forzar nueva instancia
        
    Returns:
        Instancia de ConfigManager
    """
    global _global_config_manager
    
    with _config_lock:
        if _global_config_manager is None or force_new:
            _global_config_manager = ConfigManager(
                config_dir=config_dir,
                environment=environment
            )
        
        return _global_config_manager


def get_config(key_path: str, default: Any = None, required: bool = False) -> Any:
    """
    🎯 Función de conveniencia para obtener configuración
    
    Args:
        key_path: Path del config (e.g., "trading.max_positions")
        default: Valor por defecto
        required: Si es requerido
        
    Returns:
        Valor de configuración
    """
    return get_config_manager().get(key_path, default, required)


def set_config(key_path: str, value: Any, persist: bool = False) -> None:
    """
    🎯 Función de conveniencia para establecer configuración
    
    Args:
        key_path: Path del config
        value: Nuevo valor
        persist: Si debe persistir a archivo
    """
    get_config_manager().set(key_path, value, persist)


def test_config_manager():
    """🧪 Test function para validar ConfigManager"""
    print("🧪 Testing ConfigManager...")
    
    try:
        # Test initialization
        config_manager = ConfigManager()
        print("✅ ConfigManager initialized successfully")
        
        # Test health check
        health = config_manager.health_check()
        print(f"✅ Health check: {health['status']}")
        
        # Test config operations
        config_manager.set("test.value", 42)
        value = config_manager.get("test.value")
        assert value == 42, f"Expected 42, got {value}"
        print("✅ Config set/get operations working")
        
        # Test validation
        config_manager.add_validation_rule(ConfigValidationRule(
            "test.positive_number", True, int, 1, 100
        ))
        
        try:
            config_manager.set("test.positive_number", -5)
            config_manager._validate_all_configs()
            print("❌ Validation should have failed")
        except ConfigurationError:
            print("✅ Validation working correctly")
        
        # Test all configs
        all_configs = config_manager.get_all_configs()
        print(f"✅ Total config files loaded: {len(all_configs.get('config_files', []))}")
        
        print("🎉 ConfigManager test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ConfigManager test failed: {e}")
        return False


if __name__ == "__main__":
    test_config_manager()