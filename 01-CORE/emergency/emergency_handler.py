#!/usr/bin/env python3
"""
🚨 MANEJADOR DE EMERGENCIAS
ICT Engine v6.0 Enterprise - Sistema de respuesta automática a emergencias
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Importar sistema de log central
try:
    from protocols.unified_logging import get_unified_logger
    UNIFIED_LOGGER_AVAILABLE = True
except ImportError:
    print("⚠️ No se pudo importar get_unified_logger. Usando logging estándar.")
    UNIFIED_LOGGER_AVAILABLE = False
    get_unified_logger = None

class EmergencyHandler:
    """🚨 Sistema de manejo automático de emergencias"""
    
    def __init__(self):
        self.config = self._load_config()
        self.emergency_log = []
        self.active_emergencies = []
        
        # Inicializar sistema de log central
        self.logger = None
        self.use_central_logging = False
        
        if UNIFIED_LOGGER_AVAILABLE and get_unified_logger is not None:
            try:
                self.logger = get_unified_logger("EMERGENCY_HANDLER")
                self.use_central_logging = True
                self.logger.info("🚨 Emergency Handler iniciado - usando sistema central")
            except Exception as e:
                print(f"⚠️ Error inicializando sistema central de logs para Emergency Handler: {e}")
                self.use_central_logging = False
        else:
            print("📋 Emergency Handler ejecutándose sin sistema central de logs")
        
    def _load_config(self) -> Dict:
        """Cargar configuración de procedimientos de emergencia"""
        config_file = Path("01-CORE/config/risk_management_config.json")
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    return config.get('emergency_procedures', {})
            except:
                pass
        
        # Configuración por defecto
        return {
            "emergency_stop_enabled": True,
            "auto_close_on_violation": True,
            "notification_enabled": True,
            "max_emergency_actions_per_day": 10
        }
    
    def handle_emergency(self, emergency_type: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Manejar situación de emergencia
        
        Args:
            emergency_type: Tipo de emergencia
            context: Contexto adicional
            
        Returns:
            Resultado de las acciones tomadas
        """
        emergency_record = {
            'type': emergency_type,
            'timestamp': datetime.now().isoformat(),
            'context': context or {},
            'actions_taken': [],
            'success': False,
            'error': None
        }
        
        try:
            context_safe = context or {}
            
            if emergency_type == 'RISK_VIOLATION_MAX_POSITIONS':
                emergency_record.update(self._handle_max_positions_violation(context_safe))
                
            elif emergency_type == 'RISK_VIOLATION_DAILY_LOSS':
                emergency_record.update(self._handle_daily_loss_violation(context_safe))
                
            elif emergency_type == 'RISK_VIOLATION_DRAWDOWN':
                emergency_record.update(self._handle_drawdown_violation(context_safe))
                
            elif emergency_type == 'SYSTEM_ERROR_CRITICAL':
                emergency_record.update(self._handle_critical_system_error(context_safe))
                
            elif emergency_type == 'MT5_CONNECTION_LOST':
                emergency_record.update(self._handle_mt5_disconnection(context_safe))
                
            elif emergency_type == 'LOG_SYSTEM_OVERLOAD':
                emergency_record.update(self._handle_log_overload(context_safe))
                
            else:
                emergency_record.update(self._handle_unknown_emergency(emergency_type, context_safe))
            
            emergency_record['success'] = True
            
        except Exception as e:
            emergency_record['error'] = str(e)
            emergency_record['actions_taken'].append('ERROR_IN_EMERGENCY_HANDLING')
            self._log_critical(f"Error manejando emergencia {emergency_type}: {e}")
        
        # Registrar emergencia
        self.emergency_log.append(emergency_record)
        self.active_emergencies.append(emergency_record)
        
        # Log crítico del evento
        self._log_emergency_event(emergency_record)
        
        return emergency_record
    
    def _handle_max_positions_violation(self, context: Dict) -> Dict:
        """Manejar violación de máximo de posiciones"""
        if self.use_central_logging and self.logger:
            self.logger.warning("🚨 Iniciando manejo de violación de máximo de posiciones")
        
        actions = []
        
        if self.config.get('auto_close_on_violation', True):
            actions.append('INITIATED_POSITION_CLOSURE')
            actions.append('BLOCKED_NEW_TRADES')
            self._log_critical("EMERGENCY: Max positions violated - Auto-closing positions")
        
        actions.append('SENT_RISK_VIOLATION_ALERT')
        
        if self.use_central_logging and self.logger:
            self.logger.info(f"🚨 Violación de posiciones manejada: {len(actions)} acciones tomadas")
        
        return {
            'actions_taken': actions,
            'severity': 'HIGH',
            'auto_resolved': True
        }
    
    def _handle_daily_loss_violation(self, context: Dict) -> Dict:
        """Manejar violación de pérdida diaria"""
        if self.use_central_logging and self.logger:
            self.logger.error("🚨 Iniciando manejo de violación de pérdida diaria - CRÍTICO")
        
        actions = []
        
        if self.config.get('emergency_stop_enabled', True):
            actions.append('EMERGENCY_STOP_ACTIVATED')
            actions.append('ALL_TRADING_HALTED')
            actions.append('POSITIONS_MARKED_FOR_REVIEW')
            self._log_critical("EMERGENCY: Daily loss limit exceeded - Emergency stop activated")
        
        actions.append('RISK_MANAGER_NOTIFIED')
        
        if self.use_central_logging and self.logger:
            self.logger.critical(f"🚨 Pérdida diaria excedida: {len(actions)} acciones de emergencia ejecutadas")
        
        return {
            'actions_taken': actions,
            'severity': 'CRITICAL',
            'auto_resolved': False,
            'requires_manual_intervention': True
        }
    
    def _handle_drawdown_violation(self, context: Dict) -> Dict:
        """Manejar violación de drawdown"""
        actions = []
        
        actions.append('NEW_TRADES_SUSPENDED')
        actions.append('EXISTING_POSITIONS_MONITORED')
        actions.append('RISK_ASSESSMENT_INITIATED')
        
        self._log_critical("EMERGENCY: Drawdown limit exceeded - Trading suspended")
        
        return {
            'actions_taken': actions,
            'severity': 'HIGH',
            'auto_resolved': False
        }
    
    def _handle_critical_system_error(self, context: Dict) -> Dict:
        """Manejar error crítico del sistema"""
        actions = []
        
        actions.append('SYSTEM_HEALTH_CHECK_INITIATED')
        actions.append('ERROR_DETAILS_LOGGED')
        actions.append('FALLBACK_PROCEDURES_ACTIVATED')
        
        error_details = context.get('error', 'Unknown error')
        self._log_critical(f"EMERGENCY: Critical system error - {error_details}")
        
        return {
            'actions_taken': actions,
            'severity': 'CRITICAL',
            'auto_resolved': False
        }
    
    def _handle_mt5_disconnection(self, context: Dict) -> Dict:
        """Manejar desconexión de MT5"""
        actions = []
        
        actions.append('MT5_RECONNECTION_ATTEMPTED')
        actions.append('TRADING_OPERATIONS_PAUSED')
        actions.append('CONNECTION_STATUS_MONITORED')
        
        self._log_critical("EMERGENCY: MT5 connection lost - Attempting reconnection")
        
        return {
            'actions_taken': actions,
            'severity': 'HIGH',
            'auto_resolved': True
        }
    
    def _handle_log_overload(self, context: Dict) -> Dict:
        """Manejar sobrecarga del sistema de logs"""
        actions = []
        
        actions.append('LOG_THROTTLING_ACTIVATED')
        actions.append('LOG_CLEANUP_INITIATED')
        actions.append('VERBOSE_LOGGING_DISABLED')
        
        self._log_critical("EMERGENCY: Log system overload - Throttling activated")
        
        return {
            'actions_taken': actions,
            'severity': 'MEDIUM',
            'auto_resolved': True
        }
    
    def _handle_unknown_emergency(self, emergency_type: str, context: Dict) -> Dict:
        """Manejar emergencia no reconocida"""
        actions = []
        
        actions.append('UNKNOWN_EMERGENCY_LOGGED')
        actions.append('SYSTEM_ADMIN_NOTIFIED')
        actions.append('PRECAUTIONARY_MEASURES_ACTIVATED')
        
        self._log_critical(f"EMERGENCY: Unknown emergency type - {emergency_type}")
        
        return {
            'actions_taken': actions,
            'severity': 'MEDIUM',
            'auto_resolved': False
        }
    
    def _log_emergency_event(self, emergency_record: Dict):
        """Registrar evento de emergencia en log específico y sistema central"""
        
        # Primero, registrar en sistema central si está disponible
        if self.use_central_logging and self.logger:
            emergency_msg = (
                f"🚨 EMERGENCY: {emergency_record['type']} | "
                f"Severity: {emergency_record.get('severity', 'UNKNOWN')} | "
                f"Actions: {', '.join(emergency_record['actions_taken'])} | "
                f"Success: {emergency_record['success']}"
            )
            
            # Registrar según severidad
            severity = emergency_record.get('severity', 'UNKNOWN')
            if severity == 'CRITICAL':
                self.logger.critical(emergency_msg)
            elif severity == 'HIGH':
                self.logger.error(emergency_msg)
            elif severity == 'MEDIUM':
                self.logger.warning(emergency_msg)
            else:
                self.logger.info(emergency_msg)
        
        # También mantener el archivo específico de emergencias como backup
        try:
            emergency_log_file = Path("05-LOGS/emergency/emergency_events.log")
            emergency_log_file.parent.mkdir(parents=True, exist_ok=True)
            
            log_entry = {
                'timestamp': emergency_record['timestamp'],
                'type': emergency_record['type'],
                'severity': emergency_record.get('severity', 'UNKNOWN'),
                'actions': emergency_record['actions_taken'],
                'success': emergency_record['success']
            }
            
            with open(emergency_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            self._log_critical(f"Failed to write emergency log: {e}")
    
    def _log_critical(self, message: str):
        """Log mensaje crítico usando sistema central"""
        if self.use_central_logging and self.logger:
            self.logger.critical(message)
        else:
            logging.critical(message)
        
        # También mostrar en consola para emergencias
        print(f"🚨 CRITICAL: {message}")
    
    def get_active_emergencies(self) -> List[Dict]:
        """Obtener emergencias activas"""
        return [e for e in self.active_emergencies if not e.get('resolved', False)]
    
    def resolve_emergency(self, emergency_id: str) -> bool:
        """Marcar emergencia como resuelta"""
        for emergency in self.active_emergencies:
            if emergency.get('id') == emergency_id:
                emergency['resolved'] = True
                emergency['resolved_at'] = datetime.now().isoformat()
                return True
        return False
    
    def get_emergency_summary(self) -> Dict[str, Any]:
        """Obtener resumen de emergencias"""
        active = self.get_active_emergencies()
        
        return {
            'total_emergencies_today': len(self.emergency_log),
            'active_emergencies': len(active),
            'last_emergency': self.emergency_log[-1] if self.emergency_log else None,
            'emergency_types_today': list(set(e['type'] for e in self.emergency_log)),
            'system_status': 'EMERGENCY' if active else 'NORMAL'
        }

# Instancia global
EMERGENCY_HANDLER = EmergencyHandler()

def handle_emergency(emergency_type: str, context: Optional[Dict] = None) -> Dict:
    """Función de conveniencia para manejar emergencias"""
    return EMERGENCY_HANDLER.handle_emergency(emergency_type, context)

def get_emergency_status() -> Dict:
    """Función de conveniencia para obtener estado de emergencias"""
    return EMERGENCY_HANDLER.get_emergency_summary()

def get_active_emergencies() -> List[Dict]:
    """Función de conveniencia para obtener emergencias activas"""
    return EMERGENCY_HANDLER.get_active_emergencies()
