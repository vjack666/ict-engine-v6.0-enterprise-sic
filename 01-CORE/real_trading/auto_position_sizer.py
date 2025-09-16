"""
Auto Position Sizer - ICT Engine v6.0 Enterprise
==============================================

Cálculo automático tamaño posición para cuenta real.
Integra con MT5DataManager y Smart Money Analysis existente.

Características:
- Cálculo basado en balance real
- Risk % configurable por trade
- Integración stop loss distance
- Validación especificaciones símbolo
- Correlación pairs analysis
"""

from protocols.unified_logging import get_unified_logger
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Imports del sistema ICT existente
try:
    from ..data_management.mt5_data_manager import MT5DataManager
    from ..enums import TradingDirectionV6
    from ..smart_trading_logger import SmartTradingLogger
except ImportError:
    # Fallback para testing
    MT5DataManager = None
    TradingDirectionV6 = None
    SmartTradingLogger = None

class RiskLevel(Enum):
    """Niveles de riesgo configurables"""
    CONSERVATIVE = 0.5  # 0.5% por trade
    MODERATE = 1.0      # 1.0% por trade
    AGGRESSIVE = 2.0    # 2.0% por trade
    CUSTOM = None       # Valor personalizado

@dataclass
class PositionSizingResult:
    """Resultado cálculo tamaño posición"""
    position_size: float
    risk_amount: float
    pip_distance: float
    pip_value: float
    is_valid: bool
    validation_message: str
    confidence_score: float

class AutoPositionSizer:
    """
    Cálculo automático tamaño posición para cuenta real
    
    Integra con sistema ICT Engine existente para:
    - Obtener balance cuenta MT5
    - Validar especificaciones símbolo
    - Calcular pip values precisos
    - Gestionar correlaciones
    """
    
    def __init__(self, 
                 risk_level: RiskLevel = RiskLevel.MODERATE,
                 custom_risk_percent: Optional[float] = None,
                 max_position_size: float = 10.0,
                 correlation_threshold: float = 0.7):
        """
        Inicializa Auto Position Sizer
        
        Args:
            risk_level: Nivel riesgo predefinido
            custom_risk_percent: % riesgo personalizado (0.1 = 0.1%)
            max_position_size: Tamaño máximo posición (lots)
            correlation_threshold: Umbral correlación para reducción riesgo
        """
        self.risk_level = risk_level
        self.custom_risk_percent = custom_risk_percent
        self.max_position_size = max_position_size
        self.correlation_threshold = correlation_threshold
        
        # Integración con sistema existente
        try:
            if MT5DataManager is not None:
                self.mt5_manager = MT5DataManager()
            else:
                self.mt5_manager = None
                
            if SmartTradingLogger is not None:
                self.logger = SmartTradingLogger("AutoPositionSizer")
            else:
                self.logger = logging.getLogger("AutoPositionSizer")
        except Exception as e:
            self.mt5_manager = None
            self.logger = logging.getLogger("AutoPositionSizer")
            print(f"Warning: Could not initialize MT5 components: {e}")
            
        # Cache para optimización
        self._symbol_specs_cache = {}
        self._pip_values_cache = {}
        
        self.logger.info(f"AutoPositionSizer initialized - Risk Level: {risk_level}")
    
    def calculate_position_size(self,
                              symbol: str,
                              entry_price: float,
                              stop_loss: float,
                              signal_type: str = "BUY",
                              account_balance: Optional[float] = None) -> PositionSizingResult:
        """
        Calcula tamaño posición óptimo para cuenta real
        
        Args:
            symbol: Par de divisas (ej: "EURUSD")
            entry_price: Precio entrada
            stop_loss: Precio stop loss
            signal_type: Tipo señal ("BUY" o "SELL")
            account_balance: Balance cuenta (si None, obtiene de MT5)
        
        Returns:
            PositionSizingResult con todos los detalles cálculo
        """
        try:
            # 1. Obtener balance cuenta
            if account_balance is None:
                account_balance = self._get_account_balance()
                
            if not account_balance or account_balance <= 0:
                return self._create_invalid_result("Invalid account balance")
            
            # 2. Calcular % riesgo efectivo
            risk_percent = self._get_effective_risk_percent()
            risk_amount = account_balance * (risk_percent / 100)
            
            # 3. Calcular distancia en pips
            pip_distance = self._calculate_pip_distance(symbol, entry_price, stop_loss)
            if pip_distance <= 0:
                return self._create_invalid_result("Invalid pip distance")
            
            # 4. Obtener valor pip
            pip_value = self._get_pip_value(symbol, account_balance)
            if pip_value <= 0:
                return self._create_invalid_result("Invalid pip value")
            
            # 5. Calcular tamaño posición base
            base_position_size = risk_amount / (pip_distance * pip_value)
            
            # 6. Aplicar ajustes y validaciones
            adjusted_position_size = self._apply_adjustments(
                symbol, base_position_size, signal_type
            )
            
            # 7. Validar tamaño final
            final_position_size, is_valid, validation_msg = self._validate_position_size(
                symbol, adjusted_position_size
            )
            
            # 8. Calcular confidence score
            confidence_score = self._calculate_confidence_score(
                pip_distance, risk_amount, account_balance
            )
            
            result = PositionSizingResult(
                position_size=final_position_size,
                risk_amount=risk_amount,
                pip_distance=pip_distance,
                pip_value=pip_value,
                is_valid=is_valid,
                validation_message=validation_msg,
                confidence_score=confidence_score
            )
            
            self.logger.info(f"Position size calculated: {symbol} = {final_position_size:.3f} lots")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {str(e)}")
            return self._create_invalid_result(f"Calculation error: {str(e)}")
    
    def _get_account_balance(self) -> float:
        """Obtiene balance cuenta MT5"""
        if self.mt5_manager:
            try:
                connection_status = self.mt5_manager.get_connection_status()
                return connection_status.get('balance', 0.0)
            except Exception as e:
                self.logger.error(f"Error getting account balance: {e}")
        return 0.0
    
    def _get_effective_risk_percent(self) -> float:
        """Calcula % riesgo efectivo a usar"""
        if self.custom_risk_percent:
            return self.custom_risk_percent
        elif self.risk_level == RiskLevel.CUSTOM:
            return 1.0  # Default si custom sin valor
        else:
            return self.risk_level.value
    
    def _calculate_pip_distance(self, symbol: str, entry: float, stop: float) -> float:
        """Calcula distancia en pips entre entrada y stop"""
        pip_factor = self._get_pip_factor(symbol)
        return abs(entry - stop) * pip_factor
    
    def _get_pip_factor(self, symbol: str) -> float:
        """Obtiene factor conversión para pips según símbolo"""
        # Pares principales y cruces EUR/USD, GBP/USD, etc.
        if any(x in symbol.upper() for x in ['USD', 'EUR', 'GBP', 'CHF']):
            if 'JPY' in symbol.upper():
                return 100  # Pares con JPY (2 decimales)
            else:
                return 10000  # Pares principales (4 decimales)
        return 10000  # Default
    
    def _get_pip_value(self, symbol: str, account_balance: float) -> float:
        """Calcula valor de 1 pip para el símbolo"""
        if symbol in self._pip_values_cache:
            return self._pip_values_cache[symbol]
            
        # Lógica cálculo pip value
        # Para cuenta USD: 
        # - EURUSD: $10 per lot per pip
        # - GBPJPY: Variable según tipo cambio
        
        base_pip_value = 10.0  # USD per lot per pip para principales
        
        # Ajustar según símbolo
        if 'JPY' in symbol.upper():
            base_pip_value = 10.0 / 100  # JPY adjustment
        
        self._pip_values_cache[symbol] = base_pip_value
        return base_pip_value
    
    def _apply_adjustments(self, symbol: str, base_size: float, signal_type: str) -> float:
        """Aplica ajustes al tamaño base calculado"""
        adjusted_size = base_size
        
        # 1. Ajuste por correlación (si hay posiciones correlacionadas)
        correlation_factor = self._get_correlation_adjustment(symbol)
        adjusted_size *= correlation_factor
        
        # 2. Ajuste por volatilidad
        volatility_factor = self._get_volatility_adjustment(symbol)
        adjusted_size *= volatility_factor
        
        # 3. Ajuste por time of day
        time_factor = self._get_time_adjustment()
        adjusted_size *= time_factor
        
        return adjusted_size
    
    def _get_correlation_adjustment(self, symbol: str) -> float:
        """Calcula factor reducción por correlación"""
        # TODO: Implementar análisis correlación posiciones activas
        return 1.0  # Sin reducción por ahora
    
    def _get_volatility_adjustment(self, symbol: str) -> float:
        """Calcula factor ajuste por volatilidad"""
        # TODO: Implementar análisis volatilidad
        return 1.0  # Sin ajuste por ahora
    
    def _get_time_adjustment(self) -> float:
        """Calcula factor ajuste por hora del día"""
        # TODO: Implementar ajuste por sesión trading
        return 1.0  # Sin ajuste por ahora
    
    def _validate_position_size(self, symbol: str, position_size: float) -> Tuple[float, bool, str]:
        """Valida y ajusta tamaño posición final"""
        original_size = position_size
        
        # 1. Minimum position size
        min_size = 0.01  # 0.01 lots mínimo
        if position_size < min_size:
            return min_size, False, f"Position size too small, adjusted to {min_size}"
        
        # 2. Maximum position size
        if position_size > self.max_position_size:
            return self.max_position_size, False, f"Position size capped at {self.max_position_size}"
        
        # 3. Lot size step validation (0.01 increments)
        position_size = round(position_size, 2)
        
        # 4. Broker-specific limits (TODO: get from MT5)
        
        return position_size, True, "Valid position size"
    
    def _calculate_confidence_score(self, pip_distance: float, risk_amount: float, balance: float) -> float:
        """Calcula score confianza del cálculo"""
        score = 1.0
        
        # Reducir score si pip distance muy pequeño (scalping)
        if pip_distance < 10:
            score *= 0.8
        
        # Reducir score si riesgo muy alto relative a balance
        risk_percent = (risk_amount / balance) * 100
        if risk_percent > 2.0:
            score *= 0.7
        
        # Reducir score si condiciones subóptimas
        # TODO: Agregar más factores
        
        return max(0.0, min(1.0, score))
    
    def _create_invalid_result(self, message: str) -> PositionSizingResult:
        """Crea resultado inválido con mensaje error"""
        return PositionSizingResult(
            position_size=0.0,
            risk_amount=0.0,
            pip_distance=0.0,
            pip_value=0.0,
            is_valid=False,
            validation_message=message,
            confidence_score=0.0
        )
    
    def get_risk_summary(self, account_balance: Optional[float] = None) -> Dict[str, Any]:
        """Obtiene resumen configuración riesgo actual"""
        if account_balance is None:
            account_balance = self._get_account_balance()
            
        risk_percent = self._get_effective_risk_percent()
        risk_amount = account_balance * (risk_percent / 100) if account_balance else 0
        
        return {
            'account_balance': account_balance,
            'risk_level': self.risk_level.name,
            'risk_percent': risk_percent,
            'risk_amount_per_trade': risk_amount,
            'max_position_size': self.max_position_size,
            'correlation_threshold': self.correlation_threshold
        }
    
    def update_risk_config(self, **kwargs):
        """Actualiza configuración riesgo"""
        if 'risk_level' in kwargs:
            self.risk_level = kwargs['risk_level']
        if 'custom_risk_percent' in kwargs:
            self.custom_risk_percent = kwargs['custom_risk_percent']
        if 'max_position_size' in kwargs:
            self.max_position_size = kwargs['max_position_size']
        if 'correlation_threshold' in kwargs:
            self.correlation_threshold = kwargs['correlation_threshold']
            
        self.logger.info(f"Risk configuration updated: {kwargs}")


# Ejemplo uso:
if __name__ == "__main__":
    # Testing basic functionality
    sizer = AutoPositionSizer(risk_level=RiskLevel.MODERATE)
    
    result = sizer.calculate_position_size(
        symbol="EURUSD",
        entry_price=1.1000,
        stop_loss=1.0950,
        signal_type="BUY",
        account_balance=10000.0  # $10k account
    )
    
    print(f"Position Size: {result.position_size:.3f} lots")
    print(f"Risk Amount: ${result.risk_amount:.2f}")
    print(f"Valid: {result.is_valid}")
    print(f"Message: {result.validation_message}")
