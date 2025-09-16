#!/usr/bin/env python3
"""
🚨 VALIDADOR DE RIESGO
ICT Engine v6.0 Enterprise - Sistema de validación y gestión de riesgos
"""

from protocols.unified_logging import get_unified_logger
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

class RiskValidator:
    """🚨 Sistema de validación de riesgos en tiempo real"""
    
    def __init__(self):
        self.config = self._load_config()
        self.current_positions = []
        self.daily_pnl = 0.0
        self.violations = []
        
    def _load_config(self) -> Dict:
        """Cargar configuración de gestión de riesgos"""
        config_file = Path("01-CORE/config/risk_management_config.json")
        if config_file.exists():
            try:
                with open(config_file) as f:
                    return json.load(f)
            except:
                pass
        
        # Configuración por defecto
        return {
            "max_positions": 3,
            "max_drawdown_percent": 5.0,
            "max_daily_loss": 1000.0,
            "emergency_procedures": {
                "emergency_stop_enabled": True,
                "auto_close_on_violation": True
            }
        }
    
    def validate_new_position(self, position_data: Dict) -> Dict[str, Any]:
        """
        Validar si se puede abrir una nueva posición
        
        Args:
            position_data: Datos de la posición a validar
            
        Returns:
            Resultado de la validación
        """
        result = {
            'allowed': True,
            'violations': [],
            'warnings': [],
            'action_required': None
        }
        
        # Validar número máximo de posiciones
        if len(self.current_positions) >= self.config.get('max_positions', 3):
            result['allowed'] = False
            result['violations'].append('MAX_POSITIONS_EXCEEDED')
            result['action_required'] = 'REJECT_TRADE'
        
        # Validar tamaño de posición
        position_size = position_data.get('lot_size', 0)
        max_lot_size = self.config.get('position_size_limits', {}).get('max_lot_size', 0.1)
        
        if position_size > max_lot_size:
            result['allowed'] = False
            result['violations'].append('POSITION_SIZE_EXCEEDED')
        
        # Validar exposición total
        total_exposure = self._calculate_total_exposure()
        max_exposure = self.config.get('position_size_limits', {}).get('max_total_exposure', 0.3)
        
        if total_exposure + position_size > max_exposure:
            result['warnings'].append('HIGH_EXPOSURE_WARNING')
        
        # Validar pérdida diaria
        if abs(self.daily_pnl) >= self.config.get('max_daily_loss', 1000.0):
            result['allowed'] = False
            result['violations'].append('DAILY_LOSS_LIMIT_EXCEEDED')
            result['action_required'] = 'EMERGENCY_STOP'
        
        return result
    
    def check_current_risk_status(self) -> Dict[str, Any]:
        """Verificar estado actual de riesgo del sistema"""
        status = {
            'risk_level': 'LOW',
            'violations': [],
            'warnings': [],
            'recommendations': [],
            'emergency_action_required': False
        }
        
        # Verificar número de posiciones
        current_positions_count = len(self.current_positions)
        max_positions = self.config.get('max_positions', 3)
        
        if current_positions_count >= max_positions:
            status['violations'].append('MAX_POSITIONS_VIOLATION')
            status['risk_level'] = 'CRITICAL'
            status['emergency_action_required'] = True
        elif current_positions_count >= max_positions * 0.8:
            status['warnings'].append('APPROACHING_MAX_POSITIONS')
            status['risk_level'] = 'HIGH'
        
        # Verificar drawdown
        drawdown_percent = self._calculate_drawdown_percent()
        max_drawdown = self.config.get('max_drawdown_percent', 5.0)
        
        if drawdown_percent >= max_drawdown:
            status['violations'].append('MAX_DRAWDOWN_EXCEEDED')
            status['risk_level'] = 'CRITICAL'
            status['emergency_action_required'] = True
        elif drawdown_percent >= max_drawdown * 0.8:
            status['warnings'].append('HIGH_DRAWDOWN_WARNING')
            if status['risk_level'] == 'LOW':
                status['risk_level'] = 'MEDIUM'
        
        # Verificar pérdida diaria
        daily_loss = abs(min(0, self.daily_pnl))
        max_daily_loss = self.config.get('max_daily_loss', 1000.0)
        
        if daily_loss >= max_daily_loss:
            status['violations'].append('DAILY_LOSS_LIMIT_EXCEEDED')
            status['risk_level'] = 'CRITICAL'
            status['emergency_action_required'] = True
        
        return status
    
    def handle_risk_violation(self, violation_type: str) -> Dict[str, Any]:
        """
        Manejar violación de riesgo detectada
        
        Args:
            violation_type: Tipo de violación
            
        Returns:
            Acciones tomadas
        """
        violation = {
            'type': violation_type,
            'timestamp': datetime.now().isoformat(),
            'actions_taken': [],
            'success': False
        }
        
        emergency_config = self.config.get('emergency_procedures', {})
        
        try:
            if violation_type == 'MAX_POSITIONS_VIOLATION':
                if emergency_config.get('auto_close_on_violation', True):
                    # Simular cierre de posiciones más riesgosas
                    violation['actions_taken'].append('CLOSE_RISKIEST_POSITIONS')
                    self._log_emergency_action('EMERGENCY_POSITION_CLOSURE', violation_type)
            
            elif violation_type == 'DAILY_LOSS_LIMIT_EXCEEDED':
                if emergency_config.get('emergency_stop_enabled', True):
                    violation['actions_taken'].append('EMERGENCY_STOP_ACTIVATED')
                    self._log_emergency_action('EMERGENCY_STOP', violation_type)
            
            elif violation_type == 'MAX_DRAWDOWN_EXCEEDED':
                violation['actions_taken'].append('STOP_NEW_TRADES')
                self._log_emergency_action('TRADING_HALT', violation_type)
            
            violation['success'] = True
            
        except Exception as e:
            violation['error'] = str(e)
            violation['actions_taken'].append('ERROR_IN_EMERGENCY_HANDLING')
        
        # Registrar violación
        self.violations.append(violation)
        
        return violation
    
    def _calculate_total_exposure(self) -> float:
        """Calcular exposición total actual"""
        return sum(pos.get('lot_size', 0) for pos in self.current_positions)
    
    def _calculate_drawdown_percent(self) -> float:
        """Calcular porcentaje de drawdown actual"""
        # Simulación - en implementación real obtener de MT5
        return abs(min(0, self.daily_pnl)) / 10000.0 * 100  # Asumiendo balance de 10k
    
    def _log_emergency_action(self, action: str, reason: str):
        """Registrar acción de emergencia"""
        message = f"EMERGENCY ACTION: {action} - Reason: {reason}"
        
        # Log crítico
        logging.critical(message)
        
        # También registrar en archivo específico de emergencias
        try:
            emergency_log = Path("05-LOGS/emergency/emergency_actions.log")
            emergency_log.parent.mkdir(parents=True, exist_ok=True)
            
            with open(emergency_log, 'a') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass  # Si no se puede escribir, continuar
    
    def update_positions(self, positions: List[Dict]):
        """Actualizar lista de posiciones actuales"""
        self.current_positions = positions
    
    def update_daily_pnl(self, pnl: float):
        """Actualizar P&L diario"""
        self.daily_pnl = pnl
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Obtener resumen completo de riesgo"""
        return {
            'current_positions': len(self.current_positions),
            'max_positions_allowed': self.config.get('max_positions', 3),
            'daily_pnl': self.daily_pnl,
            'total_exposure': self._calculate_total_exposure(),
            'drawdown_percent': self._calculate_drawdown_percent(),
            'violations_today': len(self.violations),
            'last_violation': self.violations[-1] if self.violations else None,
            'risk_status': self.check_current_risk_status()
        }

# Instancia global
RISK_VALIDATOR = RiskValidator()

def validate_position(position_data: Dict) -> Dict:
    """Función de conveniencia para validar posición"""
    return RISK_VALIDATOR.validate_new_position(position_data)

def check_risk_status() -> Dict:
    """Función de conveniencia para verificar estado de riesgo"""
    return RISK_VALIDATOR.check_current_risk_status()

def handle_violation(violation_type: str) -> Dict:
    """Función de conveniencia para manejar violaciones"""
    return RISK_VALIDATOR.handle_risk_violation(violation_type)
