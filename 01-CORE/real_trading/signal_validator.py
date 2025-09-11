#!/usr/bin/env python3
"""
signal_validator.py - ICT Engine v6.0 Enterprise
Sistema de validación de señales trading
"""

import time
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime
import logging

@dataclass
class ValidationCriteria:
    """Criterios de validación para señales"""
    min_confluence_score: float = 7.0
    min_rr_ratio: float = 1.5
    max_spread_pips: float = 2.0
    min_distance_to_structure: float = 5.0
    require_momentum_confluence: bool = True

@dataclass 
class SignalValidationResult:
    """Resultado de validación de señal"""
    is_valid: bool
    confidence_score: float
    rejection_reasons: List[str]
    validation_time_ms: float
    risk_reward_ratio: float
    confluence_details: Dict[str, Any]

class SignalValidator:
    """
    Validador enterprise de señales ICT
    
    Integra múltiples criterios de validación:
    - Confluence scoring
    - Risk/Reward analysis
    - Market structure validation
    - Momentum confluence
    """
    
    def __init__(self, criteria: Optional[ValidationCriteria] = None):
        """
        Initialize signal validator
        
        Args:
            criteria: Criterios de validación personalizados
        """
        self.criteria = criteria or ValidationCriteria()
        self.validation_history: List[SignalValidationResult] = []
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup validation logger"""
        logger = logging.getLogger('SignalValidator')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def validate_signal(self, signal: Any) -> SignalValidationResult:
        """
        Validar una señal de trading
        
        Args:
            signal: Objeto signal con propiedades requeridas
            
        Returns:
            SignalValidationResult con detalles de validación
        """
        start_time = time.time()
        
        try:
            # Initialize validation result
            result = SignalValidationResult(
                is_valid=False,
                confidence_score=0.0,
                rejection_reasons=[],
                validation_time_ms=0.0,
                risk_reward_ratio=0.0,
                confluence_details={}
            )
            
            # Validate signal structure
            if not self._validate_signal_structure(signal, result):
                result.validation_time_ms = (time.time() - start_time) * 1000
                return result
            
            # Calculate confluence score
            confluence_score = self._calculate_confluence_score(signal, result)
            
            # Calculate risk/reward ratio
            rr_ratio = self._calculate_risk_reward_ratio(signal, result)
            result.risk_reward_ratio = rr_ratio
            
            # Apply validation criteria
            self._apply_validation_criteria(signal, confluence_score, rr_ratio, result)
            
            # Final validation time
            result.validation_time_ms = (time.time() - start_time) * 1000
            
            # Log validation
            self.logger.info(f"Signal validation: {'PASS' if result.is_valid else 'REJECT'} "
                           f"(Confidence: {result.confidence_score:.1f}, RR: {result.risk_reward_ratio:.2f})")
            
            # Store in history
            self.validation_history.append(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Signal validation error: {e}")
            result = SignalValidationResult(
                is_valid=False,
                confidence_score=0.0,
                rejection_reasons=[f"Validation error: {str(e)}"],
                validation_time_ms=(time.time() - start_time) * 1000,
                risk_reward_ratio=0.0,
                confluence_details={}
            )
            return result
    
    def _validate_signal_structure(self, signal: Any, result: SignalValidationResult) -> bool:
        """Validar estructura básica del signal"""
        required_attrs = ['symbol', 'entry_price', 'stop_loss', 'take_profit']
        
        for attr in required_attrs:
            if not hasattr(signal, attr):
                result.rejection_reasons.append(f"Missing required attribute: {attr}")
                return False
        
        # Validate price levels
        entry = getattr(signal, 'entry_price', 0)
        stop = getattr(signal, 'stop_loss', 0)
        tp = getattr(signal, 'take_profit', 0)
        
        if entry <= 0 or stop <= 0 or tp <= 0:
            result.rejection_reasons.append("Invalid price levels (must be > 0)")
            return False
        
        return True
    
    def _calculate_confluence_score(self, signal: Any, result: SignalValidationResult) -> float:
        """Calcular confluence score"""
        base_score = 5.0
        
        # Check for confluence_score attribute
        if hasattr(signal, 'confluence_score'):
            return float(getattr(signal, 'confluence_score', base_score))
        
        # Calculate basic confluence based on available data
        confluence_factors = {
            'structure_level': 2.0,
            'fvg_present': 1.5,
            'order_block': 1.5,
            'momentum_alignment': 1.0
        }
        
        calculated_score = base_score
        confluence_details = {}
        
        for factor, weight in confluence_factors.items():
            if hasattr(signal, factor) and getattr(signal, factor, False):
                calculated_score += weight
                confluence_details[factor] = True
            else:
                confluence_details[factor] = False
        
        # Cap at 10.0
        calculated_score = min(calculated_score, 10.0)
        
        result.confluence_details = confluence_details
        return calculated_score
    
    def _calculate_risk_reward_ratio(self, signal: Any, result: SignalValidationResult) -> float:
        """Calcular risk/reward ratio"""
        try:
            entry = float(getattr(signal, 'entry_price', 0))
            stop = float(getattr(signal, 'stop_loss', 0))
            tp = float(getattr(signal, 'take_profit', 0))
            
            if entry == 0 or stop == 0 or tp == 0:
                return 0.0
            
            # Check if hasattr risk_reward for direct access
            if hasattr(signal, 'risk_reward'):
                return float(getattr(signal, 'risk_reward', 0))
            
            # Calculate based on price levels
            risk = abs(entry - stop)
            reward = abs(tp - entry)
            
            if risk == 0:
                return 0.0
            
            return reward / risk
            
        except Exception as e:
            self.logger.error(f"RR calculation error: {e}")
            return 0.0
    
    def _apply_validation_criteria(self, signal: Any, confluence_score: float, 
                                 rr_ratio: float, result: SignalValidationResult) -> None:
        """Aplicar criterios de validación"""
        
        # Confluence validation
        if confluence_score < self.criteria.min_confluence_score:
            result.rejection_reasons.append(
                f"Low confluence score: {confluence_score:.1f} < {self.criteria.min_confluence_score}"
            )
        
        # Risk/Reward validation
        if rr_ratio < self.criteria.min_rr_ratio:
            result.rejection_reasons.append(
                f"Poor risk/reward: {rr_ratio:.2f} < {self.criteria.min_rr_ratio}"
            )
        
        # Calculate final confidence score
        confidence_score = 0.0
        
        if confluence_score >= self.criteria.min_confluence_score:
            confidence_score += (confluence_score / 10.0) * 70  # 70% weight for confluence
        
        if rr_ratio >= self.criteria.min_rr_ratio:
            rr_normalized = min(rr_ratio / 3.0, 1.0)  # Normalize to max 3.0 RR
            confidence_score += rr_normalized * 30  # 30% weight for RR
        
        result.confidence_score = confidence_score
        
        # Final validation decision
        if not result.rejection_reasons:
            result.is_valid = True
            self.logger.info(f"Signal VALIDATED - Confluence: {confluence_score:.1f}, RR: {rr_ratio:.2f}")
        else:
            result.is_valid = False
            self.logger.info(f"Signal REJECTED - Reasons: {', '.join(result.rejection_reasons)}")
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de validación"""
        if not self.validation_history:
            return {
                'total_validations': 0,
                'pass_rate': 0.0,
                'avg_confidence': 0.0,
                'avg_validation_time_ms': 0.0
            }
        
        total = len(self.validation_history)
        passed = sum(1 for r in self.validation_history if r.is_valid)
        avg_confidence = sum(r.confidence_score for r in self.validation_history) / total
        avg_time = sum(r.validation_time_ms for r in self.validation_history) / total
        
        return {
            'total_validations': total,
            'pass_rate': (passed / total) * 100,
            'avg_confidence': avg_confidence,
            'avg_validation_time_ms': avg_time,
            'common_rejections': self._get_common_rejections()
        }
    
    def _get_common_rejections(self) -> Dict[str, int]:
        """Obtener razones de rechazo más comunes"""
        rejection_counts = {}
        
        for result in self.validation_history:
            for reason in result.rejection_reasons:
                rejection_counts[reason] = rejection_counts.get(reason, 0) + 1
        
        return dict(sorted(rejection_counts.items(), key=lambda x: x[1], reverse=True))
    
    def update_criteria(self, new_criteria: ValidationCriteria) -> None:
        """Actualizar criterios de validación"""
        self.criteria = new_criteria
        self.logger.info(f"Validation criteria updated: {new_criteria}")
