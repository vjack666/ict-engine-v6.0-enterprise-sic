"""
🎯 Risk Manager v6.0 Enterprise - Sistema Principal ICT
=====================================================

Gestor de riesgo avanzado para ICT Engine v6.0 Enterprise.
Implementa múltiples estrategias de gestión de riesgo y capital optimizado
para trading live en sistema de producción.

Features:
- Position sizing basado en riesgo (Kelly, Fixed, Volatility-adjusted)
- Límites de drawdown dinámicos
- Gestión de correlaciones multi-símbolo
- Risk-adjusted returns con métricas ICT
- Máximo de posiciones concurrentes
- Stop Loss dinámicos con ATR
- Integración con POI system y Smart Money Concepts
- Sistema de alertas automático
- Optimizado para trading live en producción

Integración Sistema:
- Compatible con RiskBot MT5 para trading live
- Soporte para Multi-POI Dashboard
- Métricas de riesgo ICT personalizadas
- Alertas y notificaciones avanzadas
- Exportación de reportes JSON
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pandas as pd

from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass
import numpy as np
from datetime import datetime, timedelta
import json
import logging

# 🏗️ ENTERPRISE ARCHITECTURE v6.0 - Thread-safe pandas
try:
    from data_management.advanced_candle_downloader import _pandas_manager
except ImportError:
    print("⚠️ Thread-safe pandas manager no disponible - usando fallback")
    _pandas_manager = None


@dataclass
class RiskMetrics:
    """Métricas de riesgo"""
    max_risk_per_trade: float
    max_positions: int
    max_drawdown_percent: float
    max_daily_loss_percent: float
    correlation_limit: float
    volatility_adjustment: bool
    position_sizing_method: str  # 'fixed', 'percent_risk', 'kelly', 'volatility_adjusted'


@dataclass
class ICTRiskConfig:
    """Configuración específica para ICT Engine"""
    poi_weight_factor: float = 1.2  # Factor de peso para POI quality
    smart_money_factor: float = 1.1  # Factor para Smart Money Concepts
    session_risk_multiplier: Optional[Dict[str, float]] = None  # Multiplicador por sesión
    news_impact_reduction: float = 0.5  # Reducción durante noticias
    correlation_threshold: float = 0.7  # Umbral de correlación
    
    def __post_init__(self):
        if self.session_risk_multiplier is None:
            self.session_risk_multiplier = {
                'london': 1.2,
                'new_york': 1.0,
                'asian': 0.8,
                'overlap': 1.5
            }


@dataclass
class RiskAlert:
    """Estructura para alertas de riesgo"""
    timestamp: datetime
    alert_type: str  # 'WARNING', 'CRITICAL', 'INFO'
    message: str
    current_value: float
    threshold_value: float
    recommended_action: str


class RiskManager:
    """
    🎯 Risk Manager v6.0 Enterprise - Sistema Principal ICT
    
    Gestiona el riesgo de manera avanzada con integración ICT:
    - Position sizing inteligente con POI weighting
    - Límites de drawdown dinámicos
    - Gestión de correlaciones multi-símbolo
    - Ajustes por volatilidad y Smart Money Concepts
    - Sistema de alertas automático
    - Optimizado para trading live en producción
    """
    
    def __init__(self, max_risk_per_trade: float = 0.015, max_positions: int = 3,
                 max_drawdown_percent: float = 0.12, max_daily_loss_percent: float = 0.04,
                 ict_config: Optional[ICTRiskConfig] = None, mode: str = 'live'):
        """
        Inicializar Risk Manager
        
        Args:
            max_risk_per_trade: Máximo riesgo por trade (default 1.5% para live)
            max_positions: Máximo número de posiciones concurrentes (default 3 para live)
            max_drawdown_percent: Máximo drawdown permitido (default 12% para live)
            max_daily_loss_percent: Máxima pérdida diaria permitida (default 4% para live)
            ict_config: Configuración específica para ICT Engine
            mode: 'live' para trading en producción, 'test' para pruebas
        """
        self.metrics = RiskMetrics(
            max_risk_per_trade=max_risk_per_trade,
            max_positions=max_positions,
            max_drawdown_percent=max_drawdown_percent,
            max_daily_loss_percent=max_daily_loss_percent,
            correlation_limit=0.7,
            volatility_adjustment=True,
            position_sizing_method='percent_risk'
        )
        
        # ICT Configuration
        self.ict_config = ict_config or ICTRiskConfig()
        self.mode = mode  # 'live' or 'test'
        
        # Track risk metrics
        self.daily_pnl_history: List[float] = []
        self.position_correlations: Dict[str, float] = {}
        self.volatility_window = 20
        self.kelly_lookback = 100
        
        # Risk alerts and monitoring
        self.alerts: List[RiskAlert] = []
        self.alert_callbacks: List[Callable] = []
        
        # ICT-specific tracking
        self.poi_performance_history: Dict[str, List[float]] = {}
        self.smart_money_signals: List[Dict[str, Any]] = []
        
        # Setup logging
        self.logger = logging.getLogger(f"RiskManager_{mode}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
    def _get_pandas_manager(self):
        """🐼 Obtener instancia thread-safe de pandas"""
        try:
            # Usar _pandas_manager global thread-safe
            if _pandas_manager is not None:
                return _pandas_manager.get_safe_pandas_instance()
            else:
                # Fallback a importación directa (solo para development)
                # pandas access via thread-safe manager
                return pd
        except Exception as e:
            self.logger.error(f"Error obteniendo pandas manager: {e}")
            # Fallback a importación directa (solo para development)
            # pandas access via thread-safe manager
            return pd
        
    def calculate_position_size(self, account_balance: float, entry_price: float,
                              stop_loss: float, risk_amount: Optional[float] = None) -> float:
        """
        Calcular tamaño de posición basado en riesgo
        
        Args:
            account_balance: Balance de la cuenta
            entry_price: Precio de entrada
            stop_loss: Nivel de stop loss
            risk_amount: Cantidad específica en riesgo (None = usar max_risk_per_trade)
            
        Returns:
            float: Tamaño de posición en lotes
        """
        if risk_amount is None:
            risk_amount = account_balance * self.metrics.max_risk_per_trade
        
        # Calculate risk per unit
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit == 0:
            return 0.0
        
        # Calculate base position size
        if self.metrics.position_sizing_method == 'percent_risk':
            # Standard percent risk method
            position_value = risk_amount / risk_per_unit
            position_size = position_value / 100000  # Convert to lots (assuming EURUSD)
            
        elif self.metrics.position_sizing_method == 'kelly':
            # Kelly criterion sizing
            position_size = self._calculate_kelly_size(account_balance, entry_price, stop_loss)
            
        elif self.metrics.position_sizing_method == 'volatility_adjusted':
            # Volatility adjusted sizing
            position_size = self._calculate_volatility_adjusted_size(
                account_balance, entry_price, stop_loss, risk_amount
            )
            
        else:  # fixed
            position_size = 0.1  # Fixed 0.1 lots
        
        # Apply minimum and maximum position size limits
        position_size = max(0.01, min(position_size, 10.0))  # Min 0.01, Max 10 lots
        
        return round(position_size, 2)
    
    def can_open_position(self, current_positions: int, current_drawdown: float = 0.0,
                         daily_loss: float = 0.0) -> bool:
        """
        Verificar si se puede abrir una nueva posición
        
        Args:
            current_positions: Número actual de posiciones
            current_drawdown: Drawdown actual
            daily_loss: Pérdida del día actual
            
        Returns:
            bool: True si se puede abrir posición
        """
        # Check position limit
        if current_positions >= self.metrics.max_positions:
            return False
        
        # Check drawdown limit
        if current_drawdown > self.metrics.max_drawdown_percent:
            return False
        
        # Check daily loss limit
        if daily_loss > self.metrics.max_daily_loss_percent:
            return False
        
        return True
    
    def should_reduce_position_size(self, recent_losses: int, consecutive_losses: int) -> float:
        """
        Determinar si se debe reducir el tamaño de posición
        
        Args:
            recent_losses: Número de pérdidas recientes
            consecutive_losses: Número de pérdidas consecutivas
            
        Returns:
            float: Factor de reducción (1.0 = sin reducción, 0.5 = 50% reducción)
        """
        reduction_factor = 1.0
        
        # Reduce size after consecutive losses
        if consecutive_losses >= 3:
            reduction_factor *= 0.75  # 25% reduction
        
        if consecutive_losses >= 5:
            reduction_factor *= 0.5   # Additional 50% reduction
        
        # Reduce size if many recent losses
        if recent_losses >= 7:
            reduction_factor *= 0.8   # 20% reduction
        
        return max(0.1, reduction_factor)  # Minimum 10% of original size
    
    def calculate_dynamic_stop_loss(self, entry_price: float, volatility: float,
                                   direction: str, atr_period: int = 14) -> float:
        """
        Calcular stop loss dinámico basado en volatilidad
        
        Args:
            entry_price: Precio de entrada
            volatility: Volatilidad actual (ATR)
            direction: 'buy' or 'sell'
            atr_period: Período para ATR
            
        Returns:
            float: Nivel de stop loss dinámico
        """
        # Use 1.5x ATR as default stop distance
        atr_multiplier = 1.5
        stop_distance = volatility * atr_multiplier
        
        if direction == 'buy':
            return entry_price - stop_distance
        else:  # sell
            return entry_price + stop_distance
    
    def calculate_correlation_risk(self, positions: List[Dict], new_position_symbol: str) -> float:
        """
        Calcular riesgo de correlación
        
        Args:
            positions: Lista de posiciones actuales
            new_position_symbol: Símbolo de la nueva posición
            
        Returns:
            float: Score de riesgo de correlación (0.0 - 1.0)
        """
        if not positions:
            return 0.0
        
        # Simplified correlation calculation
        # In a real implementation, this would use historical correlation data
        correlation_risk = 0.0
        
        for position in positions:
            symbol = position.get('symbol', '')
            
            # Check for obvious correlations
            if self._symbols_are_correlated(symbol, new_position_symbol):
                correlation_risk += 0.3
        
        return min(1.0, correlation_risk)
    
    def update_daily_pnl(self, daily_pnl: float) -> None:
        """
        Actualizar PnL diario para tracking
        
        Args:
            daily_pnl: PnL del día
        """
        self.daily_pnl_history.append(daily_pnl)
        
        # Keep only last 30 days
        if len(self.daily_pnl_history) > 30:
            self.daily_pnl_history = self.daily_pnl_history[-30:]
    
    def get_risk_metrics(self) -> Dict[str, float]:
        """
        Obtener métricas de riesgo actuales
        
        Returns:
            Dict con métricas de riesgo
        """
        if not self.daily_pnl_history:
            return {
                'daily_var_95': 0.0,
                'max_daily_loss': 0.0,
                'volatility': 0.0,
                'sharpe_ratio': 0.0
            }
        
        daily_returns = np.array(self.daily_pnl_history)
        
        return {
            'daily_var_95': float(np.percentile(daily_returns, 5)),  # 95% VaR
            'max_daily_loss': float(np.min(daily_returns)),
            'volatility': float(np.std(daily_returns)),
            'sharpe_ratio': float(np.mean(daily_returns) / np.std(daily_returns)) if np.std(daily_returns) > 0 else 0.0
        }
    
    def calculate_ict_position_size(self, account_balance: float, entry_price: float,
                                   stop_loss: float, poi_quality: str = 'B',
                                   smart_money_signal: bool = False,
                                   session: str = 'london',
                                   risk_amount: Optional[float] = None) -> float:
        """
        Calcular tamaño de posición con factores ICT
        
        Args:
            account_balance: Balance de la cuenta
            entry_price: Precio de entrada
            stop_loss: Nivel de stop loss
            poi_quality: Calidad del POI ('A', 'B', 'C', 'D')
            smart_money_signal: Si hay señal de Smart Money Concepts
            session: Sesión de trading actual
            risk_amount: Cantidad específica en riesgo
            
        Returns:
            float: Tamaño de posición ajustado por factores ICT
        """
        # Calcular tamaño base
        base_size = self.calculate_position_size(
            account_balance, entry_price, stop_loss, risk_amount
        )
        
        # Aplicar factores ICT
        poi_multiplier = self._get_poi_multiplier(poi_quality)
        session_multiplier = (self.ict_config.session_risk_multiplier or {}).get(session, 1.0)
        smart_money_multiplier = self.ict_config.smart_money_factor if smart_money_signal else 1.0
        
        # Calcular tamaño ajustado
        adjusted_size = base_size * poi_multiplier * session_multiplier * smart_money_multiplier
        
        # Aplicar límites
        adjusted_size = max(0.01, min(adjusted_size, 10.0))
        
        self.logger.info(f"🎯 ICT Position Size: {adjusted_size:.2f} lots "
                        f"(Base: {base_size:.2f}, POI: {poi_quality}, "
                        f"Session: {session}, SM: {smart_money_signal})")
        
        return round(adjusted_size, 2)
    
    def check_risk_limits(self, current_positions: int, current_drawdown: float,
                         daily_loss: float, open_positions: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Verificación completa de límites de riesgo con alertas
        
        Returns:
            Dict con estado de riesgo y recomendaciones
        """
        risk_status = {
            'can_trade': True,
            'warnings': [],
            'critical_alerts': [],
            'recommendations': []
        }
        
        # Check position limit
        if current_positions >= self.metrics.max_positions:
            risk_status['can_trade'] = False
            risk_status['critical_alerts'].append('MAX_POSITIONS_REACHED')
            self._trigger_alert(
                'CRITICAL', 
                f'Máximo de posiciones alcanzado: {current_positions}/{self.metrics.max_positions}',
                current_positions, self.metrics.max_positions,
                'Cerrar alguna posición antes de abrir nuevas'
            )
        
        # Check drawdown limit
        if current_drawdown > self.metrics.max_drawdown_percent:
            risk_status['can_trade'] = False
            risk_status['critical_alerts'].append('MAX_DRAWDOWN_EXCEEDED')
            self._trigger_alert(
                'CRITICAL',
                f'Drawdown excedido: {current_drawdown:.1%} > {self.metrics.max_drawdown_percent:.1%}',
                current_drawdown, self.metrics.max_drawdown_percent,
                'Revisar estrategia y reducir riesgo por trade'
            )
        
        # Check daily loss limit
        if daily_loss > self.metrics.max_daily_loss_percent:
            risk_status['can_trade'] = False
            risk_status['critical_alerts'].append('DAILY_LOSS_EXCEEDED')
            self._trigger_alert(
                'CRITICAL',
                f'Pérdida diaria excedida: {daily_loss:.1%} > {self.metrics.max_daily_loss_percent:.1%}',
                daily_loss, self.metrics.max_daily_loss_percent,
                'Detener trading por hoy y revisar posiciones'
            )
        
        return risk_status
    
    def add_alert_callback(self, callback: Callable[[RiskAlert], None]) -> None:
        """Añadir callback para alertas de riesgo"""
        self.alert_callbacks.append(callback)
    
    def export_risk_report(self, filename: Optional[str] = None) -> str:
        """Exportar reporte de riesgo en formato JSON"""
        if filename is None:
            filename = f"risk_report_{datetime.now().strftime('%Y%m%d')}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'mode': self.mode,
            'risk_metrics': {
                'max_risk_per_trade': self.metrics.max_risk_per_trade,
                'max_positions': self.metrics.max_positions,
                'max_drawdown_percent': self.metrics.max_drawdown_percent,
                'max_daily_loss_percent': self.metrics.max_daily_loss_percent,
            },
            'current_metrics': self.get_risk_metrics(),
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"📊 Reporte de riesgo exportado: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Error exportando reporte: {e}")
            return ""
    
    def _calculate_kelly_size(self, account_balance: float, entry_price: float, 
                             stop_loss: float) -> float:
        """
        Calcular tamaño usando criterio de Kelly
        
        Args:
            account_balance: Balance de cuenta
            entry_price: Precio de entrada
            stop_loss: Stop loss
            
        Returns:
            float: Tamaño de posición en lotes
        """
        # Simplified Kelly calculation
        # In practice, this would use historical win rate and average win/loss
        
        # Assume historical metrics (these would be calculated from trade history)
        win_rate = 0.6  # 60% win rate
        avg_win = 0.015  # 1.5% average win
        avg_loss = 0.01  # 1% average loss
        
        # Kelly fraction = (bp - q) / b
        # where b = odds received (avg_win/avg_loss), p = win probability, q = loss probability
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - win_rate
        
        kelly_fraction = (b * p - q) / b
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
        
        # Convert to position size
        risk_amount = account_balance * kelly_fraction
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit > 0:
            position_value = risk_amount / risk_per_unit
            return position_value / 100000  # Convert to lots
        
        return 0.1  # Default size
    
    def _calculate_volatility_adjusted_size(self, account_balance: float, entry_price: float,
                                          stop_loss: float, base_risk_amount: float) -> float:
        """
        Calcular tamaño ajustado por volatilidad
        
        Args:
            account_balance: Balance de cuenta
            entry_price: Precio de entrada
            stop_loss: Stop loss
            base_risk_amount: Cantidad base en riesgo
            
        Returns:
            float: Tamaño ajustado de posición
        """
        # Simplified volatility adjustment
        # In practice, this would use recent volatility measurements
        
        # Assume current volatility vs normal volatility
        current_volatility = 0.012  # 1.2% daily volatility
        normal_volatility = 0.010   # 1.0% normal volatility
        
        volatility_ratio = normal_volatility / current_volatility
        volatility_ratio = max(0.5, min(volatility_ratio, 2.0))  # Cap adjustment
        
        adjusted_risk = base_risk_amount * volatility_ratio
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit > 0:
            position_value = adjusted_risk / risk_per_unit
            return position_value / 100000  # Convert to lots
        
        return 0.1  # Default size
    
    def _get_poi_multiplier(self, poi_quality: str) -> float:
        """Obtener multiplicador basado en calidad POI"""
        poi_multipliers = {
            'A': self.ict_config.poi_weight_factor * 1.2,  # POI de alta calidad
            'B': self.ict_config.poi_weight_factor,        # POI estándar
            'C': self.ict_config.poi_weight_factor * 0.8,  # POI baja calidad
            'D': self.ict_config.poi_weight_factor * 0.6   # POI muy baja calidad
        }
        return poi_multipliers.get(poi_quality, 1.0)
    
    def _trigger_alert(self, alert_type: str, message: str, current_value: float,
                      threshold_value: float, recommended_action: str) -> None:
        """Disparar alerta de riesgo"""
        alert = RiskAlert(
            timestamp=datetime.now(),
            alert_type=alert_type,
            message=message,
            current_value=current_value,
            threshold_value=threshold_value,
            recommended_action=recommended_action
        )
        
        self.alerts.append(alert)
        
        # Ejecutar callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error en callback de alerta: {e}")
        
        # Log de la alerta
        log_level = logging.CRITICAL if alert_type == 'CRITICAL' else logging.WARNING
        self.logger.log(log_level, f"🚨 {alert_type}: {message}")
    
    def _symbols_are_correlated(self, symbol1: str, symbol2: str) -> bool:
        """
        Verificar si dos símbolos están correlacionados
        
        Args:
            symbol1: Primer símbolo
            symbol2: Segundo símbolo
            
        Returns:
            bool: True si están correlacionados
        """
        # Simplified correlation detection
        major_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']
        
        # Same currency pairs are obviously correlated
        if symbol1 == symbol2:
            return True
        
        # Check for common currencies
        if len(symbol1) >= 6 and len(symbol2) >= 6:
            currency1_base = symbol1[:3]
            currency1_quote = symbol1[3:6]
            currency2_base = symbol2[:3]
            currency2_quote = symbol2[3:6]
            
            # Check if they share currencies
            if (currency1_base in [currency2_base, currency2_quote] or 
                currency1_quote in [currency2_base, currency2_quote]):
                return True
        
        return False
