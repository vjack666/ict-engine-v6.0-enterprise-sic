#!/usr/bin/env python3
"""
🎯 SILVER BULLET TAB - PESTAÑA PRINCIPAL
=======================================

Pestaña principal del dashboard Silver Bullet Enterprise.
Incluye controles de trading, monitoreo en tiempo real, análisis de señales
y gestión de riesgo integrada.

Funciones:
- ✅ Trading Controls (Start/Stop Live Trading)
- ✅ Real-time Signal Monitor con Scroll
- ✅ Performance Analytics Dashboard
- ✅ Risk Management Integration
- ✅ Live P&L Tracking
- ✅ Emergency Stop Controls

Versión: v6.1.0-enterprise
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Configurar rutas
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "01-CORE"))
sys.path.insert(0, str(Path(__file__).parent))  # Agregar directorio silver_bullet

# Imports de Textual
try:
    from textual.app import ComposeResult
    from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
    from textual.widgets import Static, Button, RichLog, Label
    from textual.reactive import reactive
    from textual.binding import Binding
    from rich.text import Text
    from rich.panel import Panel
    from rich.columns import Columns
    from rich.table import Table
except ImportError as e:
    print(f"⚠️ Textual no disponible: {e}")

# Imports de módulos Silver Bullet enhanced
try:
    from trading_controls import TradingControls, TradingState
    from signal_monitor import SignalMonitor
    from performance_analyzer import PerformanceAnalyzer
    from quality_scorer import QualityScorer
    SILVER_BULLET_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Módulos Silver Bullet no disponibles: {e}")
    SILVER_BULLET_MODULES_AVAILABLE = False
    # Clases dummy para evitar errores
    class TradingControls: pass
    class TradingState: pass
    class SignalMonitor: pass
    class PerformanceAnalyzer: pass
    class QualityScorer: pass

# CHECKPOINT 4: RiskManager del sistema real
try:
    from risk_management import RiskManager
    from data_management.ict_data_manager import ICTDataManager
    REAL_SYSTEM_AVAILABLE = True
    print("✅ [SilverBulletTab] Sistema real conectado")
except ImportError:
    RiskManager = None
    ICTDataManager = None
    REAL_SYSTEM_AVAILABLE = False
    print("⚠️ [SilverBulletTab] Sistema real no disponible")

class SilverBulletTab:
    """🎯 Pestaña principal Silver Bullet Enterprise"""
    
    def __init__(self, config: Dict[str, Any], data_collector=None):
        self.config = config
        self.data_collector = data_collector
        
        # CHECKPOINT 6: Componentes principales con Quality Scorer
        self.trading_controls = TradingControls(data_collector)
        self.signal_monitor = SignalMonitor(data_collector)
        self.performance_analyzer = PerformanceAnalyzer(data_collector)
        self.quality_scorer = QualityScorer()
        
        # Sistema real integrado
        self.risk_manager = None
        self.data_manager = None
        
        if REAL_SYSTEM_AVAILABLE and RiskManager and ICTDataManager:
            try:
                self.risk_manager = RiskManager(mode='live')
                self.data_manager = ICTDataManager()
                print("✅ Sistema real integrado al Silver Bullet Dashboard")
            except Exception as e:
                print(f"⚠️ Error inicializando sistema real: {e}")
        
        # Estado interno
        self.last_update = datetime.now()
        self.auto_refresh = True
        self.refresh_interval = 2.0  # segundos
        
        # Generar datos simulados para demo
        self.performance_analyzer.simulate_trade_data()
    
    def get_enhanced_signals(self, symbol: str = "EURUSD", timeframe: str = "M15") -> Dict[str, Any]:
        """📈 Obtener señales con quality scoring integrado"""
        try:
            # Obtener señales básicas
            signals = self.signal_monitor.get_signals(symbol, timeframe)
            
            # CHECKPOINT 7: Aplicar quality scoring
            if signals.get('setup_data'):
                quality_metrics = self.quality_scorer.score_signal_quality(
                    signals['setup_data'], 
                    symbol, 
                    timeframe
                )
                signals.update(quality_metrics)
            
            return signals
            
        except Exception as e:
            print(f"⚠️ Error obteniendo señales enhanced: {e}")
            return {'error': str(e), 'timestamp': datetime.now()}
    
    def get_comprehensive_performance(self) -> Dict[str, Any]:
        """📊 Análisis de rendimiento con quality scoring"""
        try:
            # Métricas básicas de rendimiento
            performance = self.performance_analyzer.get_performance_summary()
            
            # CHECKPOINT 8: Agregar quality insights
            quality_insights = self.quality_scorer.get_quality_insights()
            performance['quality_insights'] = quality_insights
            
            return performance
            
        except Exception as e:
            print(f"⚠️ Error en análisis comprehensive: {e}")
            return {'error': str(e), 'timestamp': datetime.now()}
    
    def render_silver_bullet_dashboard(self) -> str:
        """🎯 Renderizar dashboard principal Silver Bullet"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Obtener estados de los componentes
            trading_summary = self.trading_controls.get_status_summary()
            signal_summary = self.signal_monitor.get_signal_summary()
            performance_summary = self.performance_analyzer.get_performance_summary()
            risk_metrics = self.performance_analyzer.get_risk_metrics()
            
            # Construir header
            header = f"""[bold white on blue] 🎯 SILVER BULLET ENTERPRISE v6.1 - LIVE TRADING DASHBOARD [/bold white on blue]
[bold cyan]{'='*80}[/bold cyan]"""
            
            # Estado del sistema
            system_status = f"""
[bold green]🚀 ESTADO DEL SISTEMA[/bold green]
[cyan]{'─'*40}[/cyan]
• [bold]Timestamp:[/bold] {timestamp}
• [bold]Trading Status:[/bold] [bold {'green' if trading_summary['is_active'] else 'red'}]{trading_summary['status']}[/bold {'green' if trading_summary['is_active'] else 'red'}]
• [bold]Duración:[/bold] {trading_summary['duration']}
• [bold]Posiciones Activas:[/bold] [bold yellow]{trading_summary['positions']}[/bold yellow]
• [bold]P&L Sesión:[/bold] [bold {'green' if '+' in trading_summary['pnl'] else 'red'}]{trading_summary['pnl']}[/bold {'green' if '+' in trading_summary['pnl'] else 'red'}]"""
            
            # Controles de trading
            trading_controls = f"""
[bold blue]🎮 CONTROLES DE TRADING[/bold blue]
[cyan]{'─'*40}[/cyan]
• [bold]Estado Actual:[/bold] {'🟢 ACTIVO' if trading_summary['is_active'] else '🔴 DETENIDO'}
• [bold]Última Señal:[/bold] {trading_summary['last_signal']}
• [bold]Errores:[/bold] [bold {'red' if int(trading_summary['errors']) > 0 else 'green'}]{trading_summary['errors']}[/bold {'red' if int(trading_summary['errors']) > 0 else 'green'}]
• [bold]Risk Manager:[/bold] [bold green]{'✅ Activo' if self.risk_manager else '❌ No disponible'}[/bold green]"""
            
            # Monitor de señales
            signals_section = f"""
[bold yellow]📊 MONITOR DE SEÑALES[/bold yellow]
[cyan]{'─'*40}[/cyan]
• [bold]Señales Activas:[/bold] [bold cyan]{signal_summary['active_signals']}[/bold cyan]
• [bold]Señales Fuertes:[/bold] [bold green]{signal_summary['strong_signals']}[/bold green]
• [bold]BUY Signals:[/bold] [bold green]{signal_summary['buy_signals']}[/bold green] | [bold]SELL Signals:[/bold] [bold red]{signal_summary['sell_signals']}[/bold red]
• [bold]Confluencias:[/bold] [bold magenta]{signal_summary['confluences']}[/bold magenta]
• [bold]Fortaleza Promedio:[/bold] [bold cyan]{signal_summary['avg_strength']:.2f}[/bold cyan]
• [bold]Última Actualización:[/bold] {signal_summary['last_update']}"""
            
            # Análisis de rendimiento
            performance_section = f"""
[bold magenta]📈 ANÁLISIS DE RENDIMIENTO[/bold magenta]
[cyan]{'─'*40}[/cyan]
• [bold]Estado General:[/bold] [bold {performance_summary['status_color']}]{performance_summary['status']}[/bold {performance_summary['status_color']}]
• [bold]Total Trades:[/bold] {performance_summary['total_trades']}
• [bold]Win Rate:[/bold] [bold green]{performance_summary['win_rate']}[/bold green]
• [bold]P&L Total:[/bold] [bold {'green' if '+' in performance_summary['total_pnl'] else 'red'}]{performance_summary['total_pnl']}[/bold {'green' if '+' in performance_summary['total_pnl'] else 'red'}]
• [bold]Profit Factor:[/bold] [bold blue]{performance_summary['profit_factor']}[/bold blue]
• [bold]Sharpe Ratio:[/bold] [bold cyan]{performance_summary['sharpe_ratio']}[/bold cyan]"""
            
            # Gestión de riesgo
            risk_section = f"""
[bold red]⚠️ GESTIÓN DE RIESGO[/bold red]
[cyan]{'─'*40}[/cyan]
• [bold]Nivel de Riesgo:[/bold] [bold {'green' if risk_metrics['risk_level'] == 'LOW' else 'yellow' if risk_metrics['risk_level'] == 'MEDIUM' else 'red'}]{risk_metrics['risk_level']}[/bold {'green' if risk_metrics['risk_level'] == 'LOW' else 'yellow' if risk_metrics['risk_level'] == 'MEDIUM' else 'red'}] {risk_metrics['risk_status']}
• [bold]Max Drawdown:[/bold] [bold red]{risk_metrics['max_drawdown']}[/bold red]
• [bold]Sharpe Quality:[/bold] [bold blue]{risk_metrics['sharpe_quality']}[/bold blue]
• [bold]Pérdida Promedio:[/bold] [bold red]{risk_metrics['avg_loss']}[/bold red]"""
            
            # Top señales
            top_signals = self.signal_monitor.get_top_signals(3)
            signals_list = ""
            if top_signals:
                signals_list = "\n[bold cyan]🎯 TOP SEÑALES ACTIVAS[/bold cyan]\n[cyan]{'─'*40}[/cyan]\n"
                for i, signal in enumerate(top_signals, 1):
                    formatted_signal = self.signal_monitor.format_signal_for_display(signal)
                    signals_list += f"{i}. {formatted_signal}\n"
            else:
                signals_list = "\n[bold cyan]🎯 TOP SEÑALES ACTIVAS[/bold cyan]\n[cyan]{'─'*40}[/cyan]\n[yellow]No hay señales activas[/yellow]\n"
            
            # Rendimiento diario
            daily_performance = self.performance_analyzer.get_daily_performance(5)
            daily_section = "\n[bold blue]📅 RENDIMIENTO ÚLTIMOS 5 DÍAS[/bold blue]\n[cyan]{'─'*40}[/cyan]\n"
            for day in daily_performance:
                daily_section += f"• {day['date']}: {day['status']} {day['pnl_formatted']} ({day['trades']} trades)\n"
            
            # Instrucciones de control
            controls_help = f"""
[bold white]⌨️ CONTROLES DISPONIBLES[/bold white]
[cyan]{'─'*40}[/cyan]
• [bold]F1:[/bold] Iniciar Trading en Vivo
• [bold]F2:[/bold] Detener Trading
• [bold]F3:[/bold] Parada de Emergencia
• [bold]F5:[/bold] Actualizar Dashboard
• [bold]ESC:[/bold] Volver al menú principal"""
            
            # Combinar todas las secciones
            full_dashboard = f"""{header}
{system_status}
{trading_controls}
{signals_section}
{performance_section}
{risk_section}
{signals_list}
{daily_section}
{controls_help}

[bold cyan]{'='*80}[/bold cyan]
[bold white]🎯 Silver Bullet Enterprise - Sistema de Trading Profesional[/bold white]"""
            
            return full_dashboard
            
        except Exception as e:
            return f"[red]❌ Error renderizando Silver Bullet Dashboard: {e}[/red]"
    
    def start_live_trading(self) -> bool:
        """🚀 Iniciar trading en vivo"""
        try:
            success = self.trading_controls.start_live_trading()
            if success:
                print("🚀 Silver Bullet Live Trading INICIADO desde Dashboard")
            return success
        except Exception as e:
            print(f"❌ Error iniciando trading desde dashboard: {e}")
            return False
    
    def stop_live_trading(self) -> bool:
        """🛑 Detener trading en vivo"""
        try:
            success = self.trading_controls.stop_live_trading()
            if success:
                print("🛑 Silver Bullet Live Trading DETENIDO desde Dashboard")
            return success
        except Exception as e:
            print(f"❌ Error deteniendo trading desde dashboard: {e}")
            return False
    
    def emergency_stop(self) -> bool:
        """🚨 Parada de emergencia"""
        try:
            success = self.trading_controls.emergency_stop()
            if success:
                print("🚨 EMERGENCY STOP ejecutado desde Dashboard")
            return success
        except Exception as e:
            print(f"❌ Error en emergency stop desde dashboard: {e}")
            return False
    
    def update_data(self):
        """Actualizar datos de todos los componentes"""
        try:
            # Actualizar señales
            self.signal_monitor.update_signals()
            
            # Limpiar señales antiguas
            self.signal_monitor.cleanup_old_signals()
            
            # Actualizar timestamp
            self.last_update = datetime.now()
            
        except Exception as e:
            print(f"⚠️ Error actualizando datos Silver Bullet: {e}")
    
    def get_trading_status(self) -> Dict[str, Any]:
        """Obtener estado del trading"""
        return self.trading_controls.get_status_summary()
    
    def get_performance_data(self) -> Dict[str, Any]:
        """Obtener datos de rendimiento"""
        return {
            'summary': self.performance_analyzer.get_performance_summary(),
            'daily': self.performance_analyzer.get_daily_performance(),
            'risk': self.performance_analyzer.get_risk_metrics(),
            'by_symbol': self.performance_analyzer.get_symbol_performance()
        }
    
    def export_silver_bullet_report(self) -> str:
        """Exportar reporte completo de Silver Bullet"""
        try:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'silver_bullet_dashboard': 'v6.1.0-enterprise',
                'trading_status': self.get_trading_status(),
                'signals': {
                    'summary': self.signal_monitor.get_signal_summary(),
                    'active_signals': len(self.signal_monitor.active_signals),
                    'top_signals': [
                        {
                            'symbol': s.symbol,
                            'timeframe': s.timeframe,
                            'direction': s.direction,
                            'strength': s.strength,
                            'confidence': s.confidence
                        }
                        for s in self.signal_monitor.get_top_signals(5)
                    ]
                },
                'performance': self.get_performance_data(),
                'risk_manager_active': self.risk_manager is not None
            }
            
            import json
            return json.dumps(report_data, indent=2)
            
        except Exception as e:
            print(f"⚠️ Error exportando reporte: {e}")
            return "{}"
    
    def simulate_live_activity(self):
        """Simular actividad para demostración"""
        try:
            # Actualizar señales
            self.signal_monitor.update_signals()
            
            # Simular algunos resultados de trading aleatorios
            import random
            if random.random() < 0.1:  # 10% chance cada actualización
                try:
                    from performance_analyzer import TradeResult
                except ImportError:
                    # Crear TradeResult dummy si no está disponible
                    class TradeResult:
                        def __init__(self, **kwargs):
                            for k, v in kwargs.items():
                                setattr(self, k, v)
                from datetime import datetime
                
                symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
                symbol = random.choice(symbols)
                direction = random.choice(['BUY', 'SELL'])
                win = random.random() < 0.7  # 70% win rate
                
                trade = TradeResult(
                    symbol=symbol,
                    direction=direction,
                    entry_price=random.uniform(1.0, 2.0),
                    exit_price=random.uniform(1.0, 2.0),
                    profit_loss=random.uniform(5, 25) if win else -random.uniform(3, 15),
                    duration_minutes=random.randint(15, 120),
                    timestamp=datetime.now(),
                    signal_strength=random.uniform(0.6, 0.95),
                    win=win
                )
                
                self.performance_analyzer.add_trade_result(trade)
                print(f"📊 Nuevo trade simulado: {symbol} {direction} {'✅' if win else '❌'}")
            
        except Exception as e:
            print(f"⚠️ Error simulando actividad: {e}")
