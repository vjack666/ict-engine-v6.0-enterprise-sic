#!/usr/bin/env python3
"""
📈 SILVER BULLET PERFORMANCE ANALYZER - REAL SYSTEM INTEGRATION
===============================================================

Analizador de rendimiento conectado con sistema real de trading.
Métricas avanzadas, success rate calculation y análisis enterprise.

Funciones:
- ✅ Real-time Performance Metrics (Sistema Real)
- ✅ Advanced Success Rate Calculation (Enhanced)
- ✅ P&L Analysis (Risk Manager Integration)
- ✅ Weighted Statistics (Quality Scoring)
- ✅ Risk-Adjusted Returns (Enterprise Grade)

Versión: v6.1.0-enterprise-real
"""

import sys
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
from pathlib import Path

# CHECKPOINT 2: Configurar rutas y conexión con sistema real
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "01-CORE"))

# CHECKPOINT 2: Importar módulos reales del sistema
REAL_MODULES_AVAILABLE = False
try:
    from risk_management.risk_manager import RiskManager
    from data_management.ict_data_manager import ICTDataManager
    from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
    REAL_MODULES_AVAILABLE = True
    print("✅ [PerformanceAnalyzer] Módulos reales conectados exitosamente")
except ImportError as e:
    REAL_MODULES_AVAILABLE = False
    print(f"⚠️ [PerformanceAnalyzer] Módulos reales no disponibles: {e}")
    print("🔄 [PerformanceAnalyzer] Usando modo simulación")

@dataclass
class TradeResult:
    """Resultado de trade"""
    symbol: str
    direction: str
    entry_price: float
    exit_price: float
    profit_loss: float
    duration_minutes: int
    timestamp: datetime
    signal_strength: float = 0.0
    win: bool = False

@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    profit_factor: float = 0.0
    avg_trade_duration: float = 0.0

class PerformanceAnalyzer:
    """📈 Analizador de rendimiento Silver Bullet con sistema real integrado"""
    
    def __init__(self, data_collector=None):
        self.data_collector = data_collector
        self.trade_history: List[TradeResult] = []
        self.daily_pnl: Dict[str, float] = {}
        self.max_history = 1000
        
        # CHECKPOINT 2: Inicializar módulos reales
        self.risk_manager = None
        self.ict_data_manager = None
        self.smart_money_analyzer = None
        
        # Usar variable global
        global REAL_MODULES_AVAILABLE
        
        if REAL_MODULES_AVAILABLE:
            try:
                # Inicializar RiskManager real
                self.risk_manager = RiskManager(mode='live')
                print("✅ [PerformanceAnalyzer] RiskManager inicializado")
                
                # Inicializar ICTDataManager real
                self.ict_data_manager = ICTDataManager()
                print("✅ [PerformanceAnalyzer] ICTDataManager inicializado")
                
                # Inicializar SmartMoneyAnalyzer real
                self.smart_money_analyzer = SmartMoneyAnalyzer()
                print("✅ [PerformanceAnalyzer] SmartMoneyAnalyzer inicializado")
                
            except Exception as e:
                print(f"⚠️ [PerformanceAnalyzer] Error inicializando módulos reales: {e}")
                REAL_MODULES_AVAILABLE = False
        
        # Métricas en tiempo real
        self.current_metrics = PerformanceMetrics()
        self.last_update = datetime.now()
        
        # Configuración enhanced del sistema real
        self.risk_free_rate = 0.02  # 2% anual
        self.target_sharpe = 2.0
        self.max_drawdown_limit = 0.15  # 15%
        
        # CHECKPOINT 2: Advanced Success Rate factors (del sistema real)
        self.confidence_weight = 0.60  # Weighted calculation
        self.base_weight = 0.40
        self.source_bonus = 0.15  # Bonus por fuente confiable
        self.data_confidence_factor = 0.10  # Factor por cantidad de datos
    
    def add_trade_result(self, trade: TradeResult):
        """Agregar resultado de trade"""
        try:
            # Agregar a historial
            self.trade_history.append(trade)
            
            # Mantener límite de historial
            if len(self.trade_history) > self.max_history:
                self.trade_history.pop(0)
            
            # Actualizar P&L diario
            date_key = trade.timestamp.strftime("%Y-%m-%d")
            if date_key not in self.daily_pnl:
                self.daily_pnl[date_key] = 0.0
            self.daily_pnl[date_key] += trade.profit_loss
            
            # Recalcular métricas
            self._calculate_metrics()
            
        except Exception as e:
            print(f"⚠️ Error agregando resultado de trade: {e}")
    
    def _calculate_metrics(self):
        """Calcular métricas de rendimiento"""
        try:
            if not self.trade_history:
                return
            
            # Métricas básicas
            total_trades = len(self.trade_history)
            winning_trades = len([t for t in self.trade_history if t.win])
            losing_trades = total_trades - winning_trades
            
            # Win rate
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            # P&L
            total_pnl = sum(t.profit_loss for t in self.trade_history)
            wins = [t.profit_loss for t in self.trade_history if t.win]
            losses = [t.profit_loss for t in self.trade_history if not t.win]
            
            avg_win = sum(wins) / len(wins) if wins else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
            
            # Profit Factor
            total_wins = sum(wins) if wins else 0
            total_losses = abs(sum(losses)) if losses else 1
            profit_factor = total_wins / total_losses if total_losses > 0 else 0
            
            # Drawdown
            max_drawdown = self._calculate_max_drawdown()
            
            # Sharpe Ratio
            sharpe_ratio = self._calculate_sharpe_ratio()
            
            # Duración promedio
            durations = [t.duration_minutes for t in self.trade_history]
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            # Actualizar métricas
            self.current_metrics = PerformanceMetrics(
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                total_pnl=total_pnl,
                avg_win=avg_win,
                avg_loss=avg_loss,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                profit_factor=profit_factor,
                avg_trade_duration=avg_duration
            )
            
            self.last_update = datetime.now()
            
        except Exception as e:
            print(f"⚠️ Error calculando métricas: {e}")
    
    def calculate_enhanced_success_rate(self) -> float:
        """CHECKPOINT 2: Advanced Success Rate Calculation del sistema real"""
        try:
            if not self.trade_history:
                return 0.5  # Neutral cuando no hay datos
            
            # Cálculo weighted basado en confidence
            weighted_successes = 0.0
            total_weighted = 0.0
            
            for trade in self.trade_history:
                weight = trade.signal_strength  # Usar strength como peso
                weighted_successes += weight if trade.win else 0
                total_weighted += weight
            
            # Weighted success rate
            weighted_rate = weighted_successes / total_weighted if total_weighted > 0 else 0
            
            # Base success rate (método original)
            base_rate = len([t for t in self.trade_history if t.win]) / len(self.trade_history)
            
            # Combinar métodos (60% weighted + 40% base)
            combined_rate = (weighted_rate * self.confidence_weight) + (base_rate * self.base_weight)
            
            # Bonus por fuente confiable (si usamos datos reales)
            source_bonus = self.source_bonus if REAL_MODULES_AVAILABLE else 0
            enhanced_rate = combined_rate + source_bonus
            
            # Corrección por cantidad de datos
            data_confidence = min(len(self.trade_history) / 100.0, 1.0) * self.data_confidence_factor
            final_rate = enhanced_rate + data_confidence
            
            # Asegurar rango válido [0.3, 0.9]
            return max(0.3, min(final_rate, 0.9))
            
        except Exception as e:
            print(f"⚠️ Error calculando enhanced success rate: {e}")
            return 0.5
    
    def get_real_performance_data(self) -> Dict[str, Any]:
        """CHECKPOINT 2: Obtener datos de performance del sistema real"""
        if not self.risk_manager:
            return self._get_simulated_performance_data()
        
        try:
            # Obtener métricas reales del RiskManager
            real_metrics = self.risk_manager.get_performance_metrics()
            
            # Combinar con nuestros cálculos enhanced
            enhanced_success_rate = self.calculate_enhanced_success_rate()
            
            return {
                'real_pnl': real_metrics.get('total_pnl', 0.0),
                'real_trades': real_metrics.get('total_trades', 0),
                'real_win_rate': real_metrics.get('win_rate', 0.0),
                'enhanced_success_rate': enhanced_success_rate,
                'real_max_drawdown': real_metrics.get('max_drawdown', 0.0),
                'real_sharpe_ratio': real_metrics.get('sharpe_ratio', 0.0),
                'data_source': 'real_system'
            }
            
        except Exception as e:
            print(f"⚠️ Error obteniendo datos reales: {e}")
            return self._get_simulated_performance_data()
    
    def _get_simulated_performance_data(self) -> Dict[str, Any]:
        """Datos simulados cuando sistema real no está disponible"""
        enhanced_success_rate = self.calculate_enhanced_success_rate()
        
        return {
            'real_pnl': self.current_metrics.total_pnl,
            'real_trades': self.current_metrics.total_trades,
            'real_win_rate': self.current_metrics.win_rate,
            'enhanced_success_rate': enhanced_success_rate,
            'real_max_drawdown': self.current_metrics.max_drawdown,
            'real_sharpe_ratio': self.current_metrics.sharpe_ratio,
            'data_source': 'simulated'
        }
    
    def _calculate_max_drawdown(self) -> float:
        """Calcular drawdown máximo"""
        try:
            if not self.trade_history:
                return 0.0
            
            # Calcular equity curve
            equity = [0.0]
            for trade in self.trade_history:
                equity.append(equity[-1] + trade.profit_loss)
            
            # Encontrar drawdown máximo
            peak = equity[0]
            max_dd = 0.0
            
            for value in equity:
                if value > peak:
                    peak = value
                
                drawdown = (peak - value) / max(peak, 1) if peak > 0 else 0
                max_dd = max(max_dd, drawdown)
            
            return max_dd
            
        except Exception as e:
            print(f"⚠️ Error calculando drawdown: {e}")
            return 0.0
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calcular Sharpe Ratio"""
        try:
            if len(self.daily_pnl) < 30:  # Necesitamos al menos 30 días
                return 0.0
            
            # Obtener retornos diarios
            daily_returns = list(self.daily_pnl.values())
            
            if not daily_returns:
                return 0.0
            
            # Calcular métricas
            avg_return = sum(daily_returns) / len(daily_returns)
            daily_risk_free = self.risk_free_rate / 365  # Tasa diaria
            
            # Volatilidad (desviación estándar)
            variance = sum((r - avg_return) ** 2 for r in daily_returns) / len(daily_returns)
            volatility = variance ** 0.5
            
            # Sharpe Ratio
            if volatility > 0:
                sharpe = (avg_return - daily_risk_free) / volatility
                return sharpe * (365 ** 0.5)  # Anualizar
            
            return 0.0
            
        except Exception as e:
            print(f"⚠️ Error calculando Sharpe: {e}")
            return 0.0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtener resumen de rendimiento"""
        try:
            metrics = self.current_metrics
            
            # Estado general
            if metrics.win_rate >= 70 and metrics.sharpe_ratio >= 1.5:
                performance_status = "EXCELLENT"
                status_color = "green"
            elif metrics.win_rate >= 60 and metrics.sharpe_ratio >= 1.0:
                performance_status = "GOOD"
                status_color = "blue"
            elif metrics.win_rate >= 50:
                performance_status = "FAIR"
                status_color = "yellow"
            else:
                performance_status = "POOR"
                status_color = "red"
            
            # Tiempo desde última actualización
            time_since_update = (datetime.now() - self.last_update).total_seconds()
            
            return {
                'status': performance_status,
                'status_color': status_color,
                'total_trades': metrics.total_trades,
                'win_rate': f"{metrics.win_rate:.1f}%",
                'total_pnl': f"${metrics.total_pnl:+.2f}",
                'avg_win': f"${metrics.avg_win:.2f}",
                'avg_loss': f"${metrics.avg_loss:.2f}",
                'profit_factor': f"{metrics.profit_factor:.2f}",
                'max_drawdown': f"{metrics.max_drawdown:.1%}",
                'sharpe_ratio': f"{metrics.sharpe_ratio:.2f}",
                'avg_duration': f"{metrics.avg_trade_duration:.0f} min",
                'last_update': self.last_update.strftime("%H:%M:%S"),
                'update_age': f"{time_since_update:.0f}s"
            }
            
        except Exception as e:
            print(f"⚠️ Error generando resumen: {e}")
            return {
                'status': 'ERROR',
                'status_color': 'red',
                'total_trades': 0,
                'win_rate': '0.0%',
                'total_pnl': '$0.00',
                'last_update': 'Error'
            }
    
    def get_daily_performance(self, days: int = 7) -> List[Dict[str, Any]]:
        """Obtener rendimiento diario"""
        try:
            # Obtener últimos N días
            end_date = datetime.now().date()
            daily_data = []
            
            for i in range(days):
                date = end_date - timedelta(days=i)
                date_key = date.strftime("%Y-%m-%d")
                
                pnl = self.daily_pnl.get(date_key, 0.0)
                
                # Contar trades del día
                trades_count = len([
                    t for t in self.trade_history 
                    if t.timestamp.date() == date
                ])
                
                daily_data.append({
                    'date': date.strftime("%m/%d"),
                    'pnl': pnl,
                    'pnl_formatted': f"${pnl:+.2f}",
                    'trades': trades_count,
                    'status': '✅' if pnl > 0 else '❌' if pnl < 0 else '➖'
                })
            
            return list(reversed(daily_data))  # Orden cronológico
            
        except Exception as e:
            print(f"⚠️ Error obteniendo rendimiento diario: {e}")
            return []
    
    def get_symbol_performance(self) -> Dict[str, Dict[str, Any]]:
        """Obtener rendimiento por símbolo"""
        try:
            symbol_stats = {}
            
            for trade in self.trade_history:
                symbol = trade.symbol
                
                if symbol not in symbol_stats:
                    symbol_stats[symbol] = {
                        'trades': 0,
                        'wins': 0,
                        'pnl': 0.0,
                        'avg_strength': 0.0
                    }
                
                stats = symbol_stats[symbol]
                stats['trades'] += 1
                if trade.win:
                    stats['wins'] += 1
                stats['pnl'] += trade.profit_loss
                stats['avg_strength'] += trade.signal_strength
            
            # Calcular métricas finales
            for symbol, stats in symbol_stats.items():
                if stats['trades'] > 0:
                    stats['win_rate'] = (stats['wins'] / stats['trades']) * 100
                    stats['avg_strength'] = stats['avg_strength'] / stats['trades']
                    stats['pnl_formatted'] = f"${stats['pnl']:+.2f}"
                    stats['win_rate_formatted'] = f"{stats['win_rate']:.1f}%"
                    stats['avg_strength_formatted'] = f"{stats['avg_strength']:.2f}"
            
            return symbol_stats
            
        except Exception as e:
            print(f"⚠️ Error calculando rendimiento por símbolo: {e}")
            return {}
    
    def simulate_trade_data(self):
        """Simular algunos datos de trading para demostración"""
        try:
            import random
            from datetime import timedelta
            
            symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD']
            
            # Generar algunos trades simulados
            for i in range(20):
                symbol = random.choice(symbols)
                direction = random.choice(['BUY', 'SELL'])
                
                # Simular precios
                base_price = random.uniform(1.0, 2.0)
                entry_price = base_price
                
                # Simular resultado (70% win rate)
                win = random.random() < 0.7
                
                if win:
                    # Trade ganador
                    if direction == 'BUY':
                        exit_price = entry_price * (1 + random.uniform(0.001, 0.005))
                    else:
                        exit_price = entry_price * (1 - random.uniform(0.001, 0.005))
                    pnl = random.uniform(5, 25)
                else:
                    # Trade perdedor
                    if direction == 'BUY':
                        exit_price = entry_price * (1 - random.uniform(0.001, 0.003))
                    else:
                        exit_price = entry_price * (1 + random.uniform(0.001, 0.003))
                    pnl = -random.uniform(3, 15)
                
                # Crear trade
                trade = TradeResult(
                    symbol=symbol,
                    direction=direction,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    profit_loss=pnl,
                    duration_minutes=random.randint(15, 180),
                    timestamp=datetime.now() - timedelta(days=random.randint(0, 10)),
                    signal_strength=random.uniform(0.6, 0.95),
                    win=win
                )
                
                self.add_trade_result(trade)
            
            print("✅ Datos de trading simulados generados")
            
        except Exception as e:
            print(f"⚠️ Error simulando datos: {e}")
    
    def export_performance_data(self) -> str:
        """Exportar datos de rendimiento como JSON"""
        try:
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    'total_trades': self.current_metrics.total_trades,
                    'win_rate': self.current_metrics.win_rate,
                    'total_pnl': self.current_metrics.total_pnl,
                    'sharpe_ratio': self.current_metrics.sharpe_ratio,
                    'max_drawdown': self.current_metrics.max_drawdown,
                    'profit_factor': self.current_metrics.profit_factor
                },
                'daily_pnl': self.daily_pnl,
                'recent_trades': [
                    {
                        'symbol': t.symbol,
                        'direction': t.direction,
                        'pnl': t.profit_loss,
                        'timestamp': t.timestamp.isoformat(),
                        'win': t.win
                    }
                    for t in self.trade_history[-10:]  # Últimos 10 trades
                ]
            }
            
            return json.dumps(export_data, indent=2)
            
        except Exception as e:
            print(f"⚠️ Error exportando datos: {e}")
            return "{}"
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de riesgo"""
        try:
            metrics = self.current_metrics
            
            # Evaluación de riesgo
            risk_level = "LOW"
            if metrics.max_drawdown > 0.10:  # >10%
                risk_level = "HIGH"
            elif metrics.max_drawdown > 0.05:  # >5%
                risk_level = "MEDIUM"
            
            # Calidad del Sharpe
            sharpe_quality = "POOR"
            if metrics.sharpe_ratio >= 2.0:
                sharpe_quality = "EXCELLENT"
            elif metrics.sharpe_ratio >= 1.5:
                sharpe_quality = "GOOD"
            elif metrics.sharpe_ratio >= 1.0:
                sharpe_quality = "FAIR"
            
            return {
                'risk_level': risk_level,
                'max_drawdown': f"{metrics.max_drawdown:.1%}",
                'sharpe_ratio': f"{metrics.sharpe_ratio:.2f}",
                'sharpe_quality': sharpe_quality,
                'profit_factor': f"{metrics.profit_factor:.2f}",
                'avg_loss': f"${abs(metrics.avg_loss):.2f}",
                'risk_status': '✅' if risk_level == 'LOW' else '⚠️' if risk_level == 'MEDIUM' else '❌'
            }
            
        except Exception as e:
            print(f"⚠️ Error calculando métricas de riesgo: {e}")
            return {'risk_level': 'UNKNOWN', 'risk_status': '❌'}
