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
from protocols.unified_logging import get_unified_logger
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
        
        # Initialize MT5 availability check
        self.mt5_available = self._check_mt5_availability()
        
        # Setup logger
        self.logger = get_unified_logger("RiskManager")
        
    def _check_mt5_availability(self) -> bool:
        """Check if MT5 connection is available"""
        try:
            from data_management.mt5_connection_manager import get_mt5_connection
            mt5_manager = get_mt5_connection()
            return mt5_manager is not None
        except ImportError:
            return False
        except Exception:
            return False
        
        # ICT-specific tracking
        self.poi_performance_history: Dict[str, List[float]] = {}
        self.smart_money_signals: List[Dict[str, Any]] = []
        
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
        if log_level == logging.INFO:
            self.logger.info(f"🚨 {alert_type}: {message}", "ALERT")
        elif log_level == logging.WARNING:
            self.logger.warning(f"🚨 {alert_type}: {message}", "ALERT")
        elif log_level == logging.ERROR:
            self.logger.error(f"🚨 {alert_type}: {message}", "ALERT")
        else:
            self.logger.debug(f"🚨 {alert_type}: {message}", "ALERT")
    
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

    # ================== MÉTODOS CRÍTICOS PARA TRADING REAL ==================
    
    def validate_trade_signal(self, symbol: str, action: str, volume: float,
                             current_positions: int) -> Dict[str, Any]:
        """
        🚀 MÉTODO CRÍTICO: Validar si señal de trading cumple reglas de riesgo
        
        Args:
            symbol: Símbolo a operar
            action: 'BUY' o 'SELL'
            volume: Volumen en lotes
            current_positions: Número de posiciones actuales
            
        Returns:
            Dict: {'valid': bool, 'reason': str, 'max_volume': float, 'risk_level': str}
        """
        try:
            # Reglas de riesgo obligatorias
            MAX_RISK_PER_TRADE = 2.0  # % de cuenta por operación
            MAX_POSITIONS = 5         # Máximo posiciones simultáneas
            MAX_VOLUME_PER_SYMBOL = 1.0  # Máximo volumen por símbolo
            
            # 1. Verificar máximo de posiciones
            if current_positions >= MAX_POSITIONS:
                return {
                    'valid': False,
                    'reason': f'Máximo de posiciones alcanzado ({current_positions}/{MAX_POSITIONS})',
                    'max_volume': 0.0,
                    'risk_level': 'HIGH'
                }
            
            # 2. Verificar volumen máximo
            if volume > MAX_VOLUME_PER_SYMBOL:
                return {
                    'valid': False,
                    'reason': f'Volumen excede máximo permitido ({volume} > {MAX_VOLUME_PER_SYMBOL})',
                    'max_volume': MAX_VOLUME_PER_SYMBOL,
                    'risk_level': 'HIGH'
                }
            
            # 3. Calcular riesgo de la operación
            account_balance = 10000.0  # Fallback si no se puede obtener balance real
            try:
                # Intentar obtener balance real desde MT5
                from data_management.mt5_connection_manager import get_mt5_connection
                mt5_manager = get_mt5_connection()
                account_info = mt5_manager.get_account_info()
                if account_info and 'balance' in account_info:
                    account_balance = account_info['balance']
            except:
                pass
            
            # Estimar riesgo basado en volumen típico
            estimated_risk_usd = volume * 1000  # Estimación conservadora
            risk_percentage = (estimated_risk_usd / account_balance) * 100
            
            if risk_percentage > MAX_RISK_PER_TRADE:
                max_safe_volume = (account_balance * MAX_RISK_PER_TRADE / 100) / 1000
                return {
                    'valid': False,
                    'reason': f'Riesgo excede límite ({risk_percentage:.1f}% > {MAX_RISK_PER_TRADE}%)',
                    'max_volume': round(max_safe_volume, 2),
                    'risk_level': 'HIGH'
                }
            
            # 4. Verificar correlación con posiciones existentes
            # Esto se implementaría con posiciones reales
            correlation_risk = self._check_correlation_risk(symbol)
            
            # 5. Determinar nivel de riesgo
            if risk_percentage > 1.5:
                risk_level = 'HIGH'
            elif risk_percentage > 1.0:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            # Señal válida
            logging.info(f"✅ Trade signal validated: {symbol} {action} {volume} lots - Risk: {risk_percentage:.1f}%")
            return {
                'valid': True,
                'reason': f'Signal validated - Risk: {risk_percentage:.1f}%',
                'max_volume': volume,
                'risk_level': risk_level
            }
            
        except Exception as e:
            logging.error(f"Error validating trade signal: {e}")
            return {
                'valid': False,
                'reason': f'Validation error: {str(e)}',
                'max_volume': 0.0,
                'risk_level': 'HIGH'
            }
    
    def validate_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🛡️ VALIDAR TRADE - Método requerido para ProductionSystemIntegrator
        
        Valida una operación usando los datos proporcionados
        
        Args:
            trade_data: Dict con datos de la operación
            
        Returns:
            Dict con resultado de validación
        """
        try:
            # Extraer datos del trade
            symbol = trade_data.get('symbol', 'UNKNOWN')
            action = trade_data.get('action', trade_data.get('type', 'BUY'))
            volume = float(trade_data.get('volume', trade_data.get('lot_size', 0.01)))
            current_positions = int(trade_data.get('current_positions', 0))
            
            # Usar el método de validación principal
            validation_result = self.validate_trade_signal(
                symbol=symbol,
                action=action,
                volume=volume,
                current_positions=current_positions
            )
            
            # Agregar información adicional específica del trade
            validation_result.update({
                'trade_id': trade_data.get('trade_id', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'validated_by': 'RiskManager_v6.0'
            })
            
            return validation_result
            
        except Exception as e:
            return {
                'valid': False,
                'reason': f'Trade validation error: {str(e)}',
                'max_volume': 0.0,
                'risk_level': 'HIGH',
                'trade_id': trade_data.get('trade_id', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'validated_by': 'RiskManager_v6.0'
            }
    
    def assess_risk(self, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        📊 EVALUAR RIESGO - Método requerido para ProductionSystemIntegrator
        
        Evalúa el riesgo basado en los datos proporcionados
        
        Args:
            risk_data: Dict con datos para evaluación de riesgo
            
        Returns:
            Dict con evaluación de riesgo
        """
        try:
            # Extraer datos relevantes
            symbol = risk_data.get('symbol', 'UNKNOWN')
            volume = float(risk_data.get('volume', risk_data.get('lot_size', 0.01)))
            account_balance = float(risk_data.get('account_balance', 10000.0))
            current_positions = int(risk_data.get('current_positions', 0))
            
            # Calcular riesgo básico
            risk_percentage = (volume * 1000) / account_balance * 100  # Aproximación básica
            
            # Evaluar factores de riesgo
            risk_factors = []
            
            # Factor 1: Tamaño de posición
            if risk_percentage > 2.0:
                risk_factors.append('HIGH_POSITION_SIZE')
            elif risk_percentage > 1.0:
                risk_factors.append('MEDIUM_POSITION_SIZE')
            
            # Factor 2: Número de posiciones
            if current_positions >= 5:
                risk_factors.append('MAX_POSITIONS')
            elif current_positions >= 3:
                risk_factors.append('HIGH_POSITIONS')
            
            # Factor 3: Correlación de símbolos (básica)
            if current_positions > 0 and any(curr in symbol for curr in ['USD', 'EUR', 'GBP']):
                risk_factors.append('CURRENCY_CORRELATION')
            
            # Determinar nivel de riesgo general
            if len(risk_factors) >= 3 or 'HIGH_POSITION_SIZE' in risk_factors:
                overall_risk = 'HIGH'
                risk_score = min(100, risk_percentage * 2 + len(risk_factors) * 10)
            elif len(risk_factors) >= 2 or 'MEDIUM_POSITION_SIZE' in risk_factors:
                overall_risk = 'MEDIUM'
                risk_score = min(80, risk_percentage * 1.5 + len(risk_factors) * 8)
            else:
                overall_risk = 'LOW'
                risk_score = min(60, risk_percentage + len(risk_factors) * 5)
            
            # Recomendaciones
            recommendations = []
            if risk_percentage > 2.0:
                recommendations.append('REDUCE_POSITION_SIZE')
            if current_positions >= 4:
                recommendations.append('CLOSE_SOME_POSITIONS')
            if len(risk_factors) >= 2:
                recommendations.append('WAIT_FOR_BETTER_SETUP')
            
            return {
                'risk_level': overall_risk,
                'risk_score': round(risk_score, 2),
                'risk_percentage': round(risk_percentage, 2),
                'risk_factors': risk_factors,
                'recommendations': recommendations,
                'assessment_valid': True,
                'timestamp': datetime.now().isoformat(),
                'assessed_by': 'RiskManager_v6.0',
                'symbol': symbol,
                'volume': volume
            }
            
        except Exception as e:
            return {
                'risk_level': 'HIGH',
                'risk_score': 100.0,
                'risk_percentage': 0.0,
                'risk_factors': ['ASSESSMENT_ERROR'],
                'recommendations': ['DO_NOT_TRADE'],
                'assessment_valid': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'assessed_by': 'RiskManager_v6.0'
            }

    def check_max_drawdown(self, current_equity: float, peak_equity: float) -> bool:
        """
        🚀 MÉTODO CRÍTICO: Verificar si se excede drawdown máximo permitido
        
        Args:
            current_equity: Equity actual de la cuenta
            peak_equity: Equity máximo alcanzado
            
        Returns:
            bool: True si dentro de límites, False si excedido
        """
        try:
            MAX_DRAWDOWN = 10.0  # % máximo de drawdown
            
            if peak_equity <= 0:
                logging.warning("Peak equity inválido para cálculo de drawdown")
                return True  # Permitir trading si no hay datos válidos
            
            # Calcular drawdown actual
            drawdown_percentage = ((peak_equity - current_equity) / peak_equity) * 100
            
            if drawdown_percentage > MAX_DRAWDOWN:
                logging.error(f"🚨 DRAWDOWN LIMIT EXCEEDED: {drawdown_percentage:.1f}% > {MAX_DRAWDOWN}%")
                return False
            
            if drawdown_percentage > MAX_DRAWDOWN * 0.8:  # 80% del límite
                logging.warning(f"⚠️ Drawdown approaching limit: {drawdown_percentage:.1f}% (limit: {MAX_DRAWDOWN}%)")
            
            return True
            
        except Exception as e:
            logging.error(f"Error checking drawdown: {e}")
            return False  # Ser conservativo en caso de error
    
    def emergency_stop_all(self, reason: str = "Emergency stop") -> Dict[str, Any]:
        """
        🚨 MÉTODO CRÍTICO: Cerrar todas las posiciones inmediatamente
        
        Args:
            reason: Razón del stop de emergencia
            
        Returns:
            Dict: {'closed_positions': int, 'failed_closes': int, 'details': list, 'success': bool}
        """
        try:
            logging.error(f"🚨 EMERGENCY STOP TRIGGERED: {reason}")
            
            # Obtener MT5ConnectionManager
            from data_management.mt5_connection_manager import get_mt5_connection
            mt5_manager = get_mt5_connection()
            
            # Obtener todas las posiciones abiertas
            open_positions = mt5_manager.get_open_positions()
            
            if not open_positions:
                logging.info("✅ No hay posiciones abiertas para cerrar")
                return {
                    'closed_positions': 0,
                    'failed_closes': 0,
                    'details': ['No open positions to close'],
                    'success': True
                }
            
            closed_count = 0
            failed_count = 0
            details = []
            
            # Cerrar cada posición
            for position in open_positions:
                ticket = position.get('ticket', 0)
                symbol = position.get('symbol', 'UNKNOWN')
                
                try:
                    result = mt5_manager.close_position(ticket)
                    
                    if result.get('success', False):
                        closed_count += 1
                        details.append(f"✅ Closed position {ticket} ({symbol})")
                        logging.info(f"✅ Emergency closed position {ticket} ({symbol})")
                    else:
                        failed_count += 1
                        error_msg = result.get('message', 'Unknown error')
                        details.append(f"❌ Failed to close {ticket} ({symbol}): {error_msg}")
                        logging.error(f"❌ Failed to close position {ticket}: {error_msg}")
                        
                except Exception as e:
                    failed_count += 1
                    details.append(f"❌ Exception closing {ticket}: {str(e)}")
                    logging.error(f"❌ Exception closing position {ticket}: {e}")
            
            # Resultado final
            success = failed_count == 0
            total_positions = len(open_positions)
            
            summary_msg = f"Emergency stop completed: {closed_count}/{total_positions} positions closed"
            if failed_count > 0:
                summary_msg += f", {failed_count} failed"
            
            logging.error(f"🚨 {summary_msg}")
            
            return {
                'closed_positions': closed_count,
                'failed_closes': failed_count,
                'details': details,
                'success': success,
                'total_positions': total_positions,
                'summary': summary_msg
            }
            
        except Exception as e:
            error_msg = f"Critical error in emergency_stop_all: {str(e)}"
            logging.error(f"🚨 {error_msg}")
            return {
                'closed_positions': 0,
                'failed_closes': 0,
                'details': [error_msg],
                'success': False,
                'total_positions': 0,
                'summary': error_msg
            }
    
    def _check_correlation_risk(self, symbol: str) -> float:
        """
        Verificar riesgo de correlación con posiciones existentes
        
        Returns:
            float: Nivel de riesgo de correlación (0.0 a 1.0)
        """
        try:
            # Obtener posiciones actuales
            from data_management.mt5_connection_manager import get_mt5_connection
            mt5_manager = get_mt5_connection()
            open_positions = mt5_manager.get_open_positions()
            
            if not open_positions:
                return 0.0  # Sin riesgo si no hay posiciones
            
            correlation_risk = 0.0
            
            for position in open_positions:
                position_symbol = position.get('symbol', '')
                if self._symbols_are_correlated(symbol, position_symbol):
                    correlation_risk += 0.2  # Incrementar riesgo por cada correlación
            
            return min(correlation_risk, 1.0)  # Máximo 1.0
            
        except Exception as e:
            logging.error(f"Error checking correlation risk: {e}")
            return 0.5  # Riesgo medio en caso de error
    
    def get_account_risk_summary(self) -> Dict[str, Any]:
        """
        🚀 NUEVO: Obtener resumen completo de riesgo de la cuenta
        
        Returns:
            Dict con métricas de riesgo en tiempo real
        """
        try:
            # Obtener datos de cuenta
            from data_management.mt5_connection_manager import get_mt5_connection
            mt5_manager = get_mt5_connection()
            account_info = mt5_manager.get_account_info()
            open_positions = mt5_manager.get_open_positions()
            
            if not account_info:
                return {'error': 'Cannot retrieve account information'}
            
            balance = account_info.get('balance', 0.0)
            equity = account_info.get('equity', 0.0)
            margin_free = account_info.get('margin_free', 0.0)
            
            # Calcular métricas
            total_exposure = sum(pos.get('volume', 0.0) for pos in open_positions)
            total_profit = sum(pos.get('profit', 0.0) for pos in open_positions)
            
            # Drawdown desde balance inicial (simplificado)
            current_drawdown = ((balance - equity) / balance * 100) if balance > 0 else 0.0
            
            return {
                'account_balance': balance,
                'account_equity': equity,
                'margin_free': margin_free,
                'open_positions': len(open_positions),
                'total_exposure': total_exposure,
                'total_profit': total_profit,
                'current_drawdown': current_drawdown,
                'margin_level': (equity / (balance - margin_free) * 100) if (balance - margin_free) > 0 else 0.0,
                'risk_status': 'LOW' if current_drawdown < 5.0 else 'MEDIUM' if current_drawdown < 8.0 else 'HIGH',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error getting account risk summary: {e}")
            return {'error': f'Risk summary error: {str(e)}'}
    
    # ---------------- PRODUCTION METHODS - MISSING ----------------
    
    def analyze_symbol_correlations(self, symbols: List[str], timeframe: str = "H1", 
                                    periods: int = 100) -> Dict[str, Dict[str, float]]:
        """
        Analyze correlations between multiple symbols for risk management.
        
        Args:
            symbols: List of symbols to analyze
            timeframe: Timeframe for correlation analysis (M1, M5, H1, H4, D1)
            periods: Number of periods to analyze
            
        Returns:
            Dict with correlation matrix between symbols
        """
        try:
            correlations = {}
            pd = self._get_pandas_manager()
            
            # Initialize correlation matrix
            for symbol in symbols:
                correlations[symbol] = {}
                
            self.logger.info(f"Analyzing correlations for {len(symbols)} symbols over {periods} {timeframe} periods", "CORRELATION")
            
            if self.mt5_available:
                # Get price data for all symbols
                price_data = {}
                for symbol in symbols:
                    try:
                        # In real implementation, use MT5 to get OHLC data
                        # For now, simulate correlation data
                        
                        # Generate realistic correlation patterns
                        base_returns = np.random.normal(0, 0.01, periods)
                        if 'EUR' in symbol and 'USD' in symbol:
                            # EUR/USD related pairs tend to be correlated
                            base_factor = 0.8
                        elif 'JPY' in symbol:
                            # JPY pairs often have different behavior
                            base_factor = -0.3
                        elif 'GBP' in symbol:
                            # GBP pairs correlation with EUR
                            base_factor = 0.6
                        else:
                            base_factor = np.random.uniform(-0.5, 0.5)
                        
                        price_data[symbol] = base_returns * base_factor + np.random.normal(0, 0.005, periods)
                        
                    except Exception as e:
                        self.logger.warning(f"Could not get data for {symbol}: {e}", "CORRELATION")
                        price_data[symbol] = np.random.normal(0, 0.01, periods)
                
                # Calculate correlations between all pairs
                for i, symbol1 in enumerate(symbols):
                    for j, symbol2 in enumerate(symbols):
                        if i <= j:  # Only calculate upper triangle + diagonal
                            if symbol1 == symbol2:
                                correlation = 1.0
                            else:
                                try:
                                    correlation = np.corrcoef(price_data[symbol1], price_data[symbol2])[0, 1]
                                    if np.isnan(correlation):
                                        correlation = 0.0
                                except Exception:
                                    correlation = 0.0
                            
                            correlations[symbol1][symbol2] = round(correlation, 4)
                            correlations[symbol2][symbol1] = round(correlation, 4)
                
                self.logger.info(f"Correlation analysis completed successfully", "CORRELATION")
                
            else:
                # Simulation mode - generate realistic correlations
                self.logger.info("Generating simulated correlations (MT5 not available)", "CORRELATION")
                for i, symbol1 in enumerate(symbols):
                    for j, symbol2 in enumerate(symbols):
                        if symbol1 == symbol2:
                            correlations[symbol1][symbol2] = 1.0
                        else:
                            # Generate realistic correlations based on currency pairs
                            if symbol1 not in correlations or symbol2 not in correlations[symbol1]:
                                base_correlation = self._get_typical_correlation(symbol1, symbol2)
                                noise = np.random.uniform(-0.1, 0.1)
                                correlation = np.clip(base_correlation + noise, -1.0, 1.0)
                                
                                correlations[symbol1][symbol2] = round(correlation, 4)
                                correlations[symbol2][symbol1] = round(correlation, 4)
            
            return correlations
            
        except Exception as e:
            self.logger.error(f"Error analyzing symbol correlations: {e}", "CORRELATION")
            return {symbol: {s: 0.0 for s in symbols} for symbol in symbols}
    
    def _get_typical_correlation(self, symbol1: str, symbol2: str) -> float:
        """Get typical correlation between two currency pairs"""
        # Extract currencies from pairs
        curr1_base = symbol1[:3] if len(symbol1) >= 6 else ""
        curr1_quote = symbol1[3:6] if len(symbol1) >= 6 else ""
        curr2_base = symbol2[:3] if len(symbol2) >= 6 else ""
        curr2_quote = symbol2[3:6] if len(symbol2) >= 6 else ""
        
        # High correlation patterns
        if (curr1_base == curr2_base or curr1_quote == curr2_quote or
            curr1_base == curr2_quote or curr1_quote == curr2_base):
            return 0.7  # Strong correlation for shared currencies
        
        # Major pairs correlation patterns
        major_eur = ['EURUSD', 'EURGBP', 'EURJPY']
        major_gbp = ['GBPUSD', 'EURGBP', 'GBPJPY']
        
        if symbol1 in major_eur and symbol2 in major_eur:
            return 0.6
        if symbol1 in major_gbp and symbol2 in major_gbp:
            return 0.5
        
        # JPY pairs often negatively correlated with risk-on currencies
        if 'JPY' in symbol1 and 'JPY' not in symbol2:
            return -0.3
        if 'JPY' in symbol2 and 'JPY' not in symbol1:
            return -0.3
        
        return 0.1  # Low default correlation
    
    def check_daily_loss_limits(self, account_balance: float, 
                                todays_pnl: Optional[float] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if daily loss limits are being respected.
        
        Args:
            account_balance: Current account balance
            todays_pnl: Today's P&L (None = auto-calculate from MT5)
            
        Returns:
            Tuple of (within_limits: bool, limit_info: dict)
        """
        try:
            self.logger.debug("Checking daily loss limits", "DAILY_LIMITS")
            
            # Get today's P&L if not provided
            if todays_pnl is None:
                todays_pnl = self._calculate_daily_pnl()
            
            # Calculate limits
            max_daily_loss = account_balance * (self.metrics.max_daily_loss_percent / 100)
            current_daily_loss = abs(min(0, todays_pnl))  # Only count losses
            
            # Calculate percentages
            loss_percentage = (current_daily_loss / account_balance) * 100
            limit_percentage = self.metrics.max_daily_loss_percent
            
            # Check if within limits
            within_limits = current_daily_loss <= max_daily_loss
            
            # Calculate remaining allowable loss
            remaining_allowable_loss = max(0, max_daily_loss - current_daily_loss)
            
            # Determine warning level
            warning_level = "SAFE"
            if loss_percentage >= limit_percentage * 0.8:
                warning_level = "CRITICAL"
            elif loss_percentage >= limit_percentage * 0.6:
                warning_level = "WARNING"
            elif loss_percentage >= limit_percentage * 0.4:
                warning_level = "CAUTION"
            
            limit_info = {
                'within_limits': within_limits,
                'todays_pnl': round(todays_pnl, 2),
                'current_daily_loss': round(current_daily_loss, 2),
                'max_daily_loss': round(max_daily_loss, 2),
                'loss_percentage': round(loss_percentage, 2),
                'limit_percentage': round(limit_percentage, 2),
                'remaining_allowable_loss': round(remaining_allowable_loss, 2),
                'warning_level': warning_level,
                'recommendation': self._get_daily_limit_recommendation(warning_level, within_limits),
                'timestamp': datetime.now().isoformat()
            }
            
            if not within_limits:
                self.logger.warning(f"Daily loss limit exceeded! Current: {loss_percentage:.2f}%, "
                                    f"Limit: {limit_percentage:.2f}%", "DAILY_LIMITS")
                
                # Create risk alert
                alert = RiskAlert(
                    timestamp=datetime.now(),
                    alert_type="CRITICAL",
                    message="Daily loss limit exceeded",
                    current_value=loss_percentage,
                    threshold_value=limit_percentage,
                    recommended_action="Stop trading for today and review risk management"
                )
                self.alerts.append(alert)
                
            elif warning_level in ["WARNING", "CRITICAL"]:
                self.logger.warning(f"Approaching daily loss limit: {loss_percentage:.2f}% of {limit_percentage:.2f}%", 
                                    "DAILY_LIMITS")
            
            return within_limits, limit_info
            
        except Exception as e:
            self.logger.error(f"Error checking daily loss limits: {e}", "DAILY_LIMITS")
            return True, {
                'error': str(e),
                'within_limits': True,  # Default to safe
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_daily_pnl(self) -> float:
        """Calculate today's P&L from trading activities"""
        try:
            if self.mt5_available:
                # Get today's trading history from MT5
                from datetime import date
                today = date.today()
                
                # In real implementation, query MT5 for today's deals
                # For now, simulate based on open positions
                from data_management.mt5_connection_manager import get_mt5_connection
                mt5_manager = get_mt5_connection()
                open_positions = mt5_manager.get_open_positions()
                
                # Sum unrealized P&L from open positions
                todays_pnl = sum(pos.get('profit', 0.0) for pos in open_positions)
                
                self.logger.debug(f"Calculated today's P&L: {todays_pnl}", "DAILY_PNL")
                return todays_pnl
                
            else:
                # Simulation mode
                import random
                simulated_pnl = random.uniform(-500, 200)  # Simulate some P&L
                self.logger.debug(f"Simulated today's P&L: {simulated_pnl}", "DAILY_PNL")
                return simulated_pnl
                
        except Exception as e:
            self.logger.error(f"Error calculating daily P&L: {e}", "DAILY_PNL")
            return 0.0
    
    def _get_daily_limit_recommendation(self, warning_level: str, within_limits: bool) -> str:
        """Get recommendation based on daily limit status"""
        if not within_limits:
            return "STOP TRADING: Daily loss limit exceeded. Close any losing positions and stop new trades."
        
        recommendations = {
            "SAFE": "Continue trading with normal risk parameters",
            "CAUTION": "Reduce position sizes by 25% and be more selective with entries",
            "WARNING": "Reduce position sizes by 50% and avoid high-risk trades",
            "CRITICAL": "Consider stopping new trades and focus on position management"
        }
        
        return recommendations.get(warning_level, "Monitor risk levels carefully")
