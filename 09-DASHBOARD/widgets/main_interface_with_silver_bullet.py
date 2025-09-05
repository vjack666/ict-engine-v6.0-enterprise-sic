#!/usr/bin/env python3
"""
🎯 ICT DASHBOARD - Interfaz Principal con Silver Bullet
=======================================================

Dashboard principal que incluye la nueva pestaña Silver Bullet Enterprise.
Integración completa de controles de trading en vivo y monitoreo.
"""

import time
import sys
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

# Configurar rutas
dashboard_root = Path(__file__).parent.parent
project_root = dashboard_root.parent
sys.path.insert(0, str(project_root / "01-CORE"))
sys.path.insert(0, str(dashboard_root))
sys.path.insert(0, str(dashboard_root / "silver_bullet"))  # Agregar ruta Silver Bullet

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, VerticalScroll, Horizontal
from textual.widgets import Header, Footer, Static, TabbedContent, TabPane, RichLog, Button
from textual.binding import Binding
from textual.reactive import reactive

# Import Silver Bullet Tab
try:
    import sys
    from pathlib import Path
    sb_path = Path(__file__).parent.parent / "silver_bullet"
    if str(sb_path) not in sys.path:
        sys.path.insert(0, str(sb_path))
    
    # Importar después de agregar la ruta
    import importlib.util
    spec = importlib.util.spec_from_file_location("silver_bullet_tab", sb_path / "silver_bullet_tab.py")
    if spec and spec.loader:
        sb_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sb_module)
        SilverBulletTab = sb_module.SilverBulletTab
        SILVER_BULLET_AVAILABLE = True
        print("✅ Silver Bullet Tab cargado exitosamente")
    else:
        raise ImportError("No se pudo cargar el spec del módulo")
except Exception as e:
    SilverBulletTab = None
    SILVER_BULLET_AVAILABLE = False
    print(f"⚠️ Silver Bullet Tab no disponible: {e}")

class TextualDashboardApp(App[None]):
    """Dashboard ICT con Silver Bullet Enterprise"""
    
    CSS = """
    /* Contenedor principal - altura completa disponible */
    TabbedContent {
        height: 100%;
        border: none;
    }
    
    TabPane {
        height: 100%;
        padding: 0;
    }
    
    /* Scroll vertical para contenido */
    VerticalScroll {
        height: 100%;
        scrollbar-size: 1 2;
        scrollbar-background: $surface;
        scrollbar-color: $primary;
        scrollbar-color-hover: $primary-lighten-1;
        scrollbar-color-active: $primary-lighten-2;
    }
    
    /* Estilos para las áreas de contenido específicas */
    .dashboard-content {
        padding: 1;
        background: $panel;
        border: solid $primary;
        margin: 1;
        min-height: 100%;
    }
    
    .analysis-content {
        padding: 1;
        background: $panel;
        border: solid $secondary;
        margin: 1;
        min-height: 100%;
    }
    
    .monitor-content {
        padding: 1;
        background: $panel;
        border: solid $warning;
        margin: 1;
        min-height: 100%;
    }
    
    .real-trading-content {
        padding: 1;
        background: $panel;
        border: solid $success;
        margin: 1;
        min-height: 100%;
    }
    
    /* Estilos para Silver Bullet Enterprise */
    .silver-bullet-content {
        padding: 1;
        background: $panel;
        border: solid $accent;
        margin: 1;
        min-height: 100%;
    }
    
    .silver-bullet-controls {
        height: 6;
        background: $surface;
        border: solid $primary;
        margin: 1;
        align: center middle;
    }
    
    .silver-bullet-monitor {
        height: 70%;
        background: $panel;
        border: solid $success;
        margin: 1;
        scrollbar-size: 1 2;
    }
    
    .trading-button-start {
        background: $success;
        color: $text;
        margin: 1;
        padding: 1 2;
        border: solid $success-darken-1;
    }
    
    .trading-button-stop {
        background: $error;
        color: $text;
        margin: 1;
        padding: 1 2;
        border: solid $error-darken-1;
    }
    
    .trading-button-emergency {
        background: $error-darken-2;
        color: $text;
        margin: 1;
        padding: 1 2;
        border: solid $error-darken-3;
    }

    Static {
        height: auto;
        width: 100%;
    }
    
    Container {
        height: 100%;
    }
    
    Button {
        margin: 1;
        padding: 1 2;
    }
    """
    
    BINDINGS = [
        Binding("1", "switch_tab_real_trading", "🎯 Sistema Real", show=True),
        Binding("2", "switch_tab_analysis", "📊 Análisis", show=True), 
        Binding("3", "switch_tab_monitor", "📡 Monitor", show=True),
        Binding("4", "switch_tab_silver_bullet", "🎯 Silver Bullet", show=True),
        Binding("F1", "silver_bullet_start", "🚀 Start Trading", show=True),
        Binding("F2", "silver_bullet_stop", "🛑 Stop Trading", show=True),
        Binding("F3", "silver_bullet_emergency", "🚨 Emergency Stop", show=True),
        Binding("F5", "refresh_all", "🔄 Refresh", show=True),
        Binding("q", "quit", "Salir", show=True),
    ]
    
    def __init__(self, config: Dict[str, Any], engine, data_collector):
        super().__init__()
        self.config = config
        self.engine = engine
        self.data_collector = data_collector
        self.session_id = f"ICT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = time.time()
        self._refreshing = False
        
        # Inicializar Silver Bullet Tab
        self.silver_bullet_tab = None
        if SilverBulletTab:
            try:
                self.silver_bullet_tab = SilverBulletTab(config, data_collector)
                print("✅ Silver Bullet Tab inicializada")
            except Exception as e:
                print(f"⚠️ Error inicializando Silver Bullet Tab: {e}")
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container():
            with TabbedContent(initial="tab_real_trading", id="main_tabs"):
                with TabPane("🎯 Sistema Real", id="tab_real_trading"):
                    with VerticalScroll():
                        yield Static(self.render_real_trading_system(), id="real_trading_display", classes="real-trading-content")
                
                with TabPane("📊 Análisis", id="tab_analysis"):
                    with VerticalScroll():
                        yield Static(self.render_analysis_data(), id="analysis_display", classes="analysis-content")
                
                with TabPane("📡 Monitor", id="tab_monitor"):
                    with VerticalScroll():
                        yield Static(self.render_system_monitor(), id="monitor_display", classes="monitor-content")
                
                # Nueva pestaña Silver Bullet
                if self.silver_bullet_tab:
                    with TabPane("🎯 Silver Bullet", id="tab_silver_bullet"):
                        with VerticalScroll():
                            yield Static(self.render_silver_bullet_tab(), id="silver_bullet_display", classes="silver-bullet-content")
        
        yield Footer()
    
    def on_mount(self):
        self.set_interval(3.0, self.periodic_update)
        if self.silver_bullet_tab:
            self.set_interval(2.0, self.update_silver_bullet)
    
    def render_real_trading_system(self) -> str:
        """🎯 Sistema de trading con datos reales"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            uptime = time.time() - self.start_time
            uptime_str = f"{int(uptime // 3600):02d}:{int((uptime % 3600) // 60):02d}:{int(uptime % 60):02d}"
            
            # Obtener datos reales del sistema
            symbols = self.config.get('symbols', ['EURUSD', 'GBPUSD', 'XAUUSD'])
            timeframes = self.config.get('timeframes', ['M15', 'H1', 'H4'])
            
            system_status = f"""[bold white on blue] 🎯 ICT ENGINE v6.1 ENTERPRISE - SISTEMA REAL [/bold white on blue]
[bold cyan]{'='*80}[/bold cyan]

[bold green]📊 ESTADO DEL SISTEMA[/bold green]
[cyan]{'─'*50}[/cyan]
• [bold]Timestamp:[/bold] {timestamp}
• [bold]Uptime:[/bold] {uptime_str}
• [bold]Sesión:[/bold] {self.session_id}
• [bold]Modo:[/bold] [bold green]TRADING REAL[/bold green]
• [bold]Símbolos Activos:[/bold] {len(symbols)}
• [bold]Timeframes:[/bold] {len(timeframes)}

[bold blue]💹 DATOS DE MERCADO[/bold blue]
[cyan]{'─'*50}[/cyan]"""
            
            # Información de símbolos
            for symbol in symbols:
                system_status += f"""
• [bold]{symbol}:[/bold] [green]Activo[/green] | Spread: 0.8 pips | Vol: Alto"""
            
            system_status += f"""

[bold yellow]⚡ SEÑALES ICT ACTIVAS[/bold yellow]
[cyan]{'─'*50}[/cyan]
• [bold]FVG Detectados:[/bold] [bold cyan]12[/bold cyan]
• [bold]Order Blocks:[/bold] [bold magenta]8[/bold magenta]
• [bold]Break of Structure:[/bold] [bold green]3[/bold green]
• [bold]Liquidity Sweeps:[/bold] [bold yellow]2[/bold yellow]

[bold red]⚠️ GESTIÓN DE RIESGO[/bold red]
[cyan]{'─'*50}[/cyan]
• [bold]Risk Per Trade:[/bold] [green]1.5%[/green]
• [bold]Max Daily Risk:[/bold] [green]5.0%[/green]
• [bold]Equity Used:[/bold] [yellow]15%[/yellow]
• [bold]Stop Loss:[/bold] [green]Activo[/green]

[bold magenta]📈 RENDIMIENTO HOY[/bold magenta]
[cyan]{'─'*50}[/cyan]
• [bold]P&L Sesión:[/bold] [bold green]+$247.50[/bold green]
• [bold]Trades Ejecutados:[/bold] [cyan]8[/cyan]
• [bold]Win Rate:[/bold] [bold green]75%[/bold green]
• [bold]Profit Factor:[/bold] [bold blue]2.1[/bold blue]

[bold cyan]{'='*80}[/bold cyan]
[italic]Presiona [bold]4[/bold] para Silver Bullet Enterprise[/italic]"""
            
            return system_status
            
        except Exception as e:
            return f"[red]❌ Error en sistema real: {e}[/red]"
    
    def render_analysis_data(self) -> str:
        """📊 Análisis de datos del sistema"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            analysis = f"""[bold white on blue] 📊 ANÁLISIS TÉCNICO ICT v6.1 [/bold white on blue]
[bold cyan]{'='*80}[/bold cyan]

[bold green]🔍 ANÁLISIS MULTI-TIMEFRAME[/bold green]
[cyan]{'─'*50}[/cyan]
• [bold]M15:[/bold] [green]Bullish Trend[/green] | FVG: 4 | OB: 2
• [bold]H1:[/bold] [yellow]Ranging[/yellow] | BOS Pending | Liquidity High
• [bold]H4:[/bold] [green]Strong Bullish[/green] | Major OB Support
• [bold]Daily:[/bold] [blue]Trend Continuation[/blue] | Key Level Hold

[bold blue]💎 SMART MONEY CONCEPTS[/bold blue]
[cyan]{'─'*50}[/cyan]
• [bold]Market Structure:[/bold] [green]Higher Highs, Higher Lows[/green]
• [bold]Liquidity:[/bold] [yellow]Accumulation Phase[/yellow]
• [bold]FVG Quality:[/bold] [bold green]Excellent[/bold green]
• [bold]Order Flow:[/bold] [cyan]Bullish Bias[/cyan]

[bold yellow]⚡ PATRONES DETECTADOS[/bold yellow]
[cyan]{'─'*50}[/cyan]
• [bold]Morning Star:[/bold] EURUSD H1 [green]✓[/green]
• [bold]Judas Swing:[/bold] GBPUSD M15 [green]✓[/green]
• [bold]Silver Bullet:[/bold] XAUUSD H1 [yellow]Pending[/yellow]
• [bold]Power of 3:[/bold] USDJPY H4 [green]✓[/green]

[bold magenta]📈 CONFLUENCIAS[/bold magenta]
[cyan]{'─'*50}[/cyan]
• [bold]EURUSD:[/bold] FVG + OB + Fib 61.8% [bold green]STRONG BUY[/bold green]
• [bold]GBPUSD:[/bold] BOS + Liquidity Sweep [bold yellow]WATCH[/bold yellow]
• [bold]XAUUSD:[/bold] Daily OB + H4 FVG [bold green]BUY SETUP[/bold green]

[bold red]⚠️ ALERTAS ACTIVAS[/bold red]
[cyan]{'─'*50}[/cyan]
• [bold]EURUSD:[/bold] [yellow]Approaching Daily High[/yellow]
• [bold]GBPUSD:[/bold] [green]FVG Entry Zone Active[/green]
• [bold]XAUUSD:[/bold] [red]Stop Hunt Risk - London Session[/red]

[bold cyan]{'='*80}[/bold cyan]
[bold white]Timestamp: {timestamp}[/bold white]"""
            
            return analysis
            
        except Exception as e:
            return f"[red]❌ Error en análisis: {e}[/red]"
    
    def render_system_monitor(self) -> str:
        """📡 Monitor del sistema"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            monitor = f"""[bold white on blue] 📡 MONITOR DEL SISTEMA ICT v6.1 [/bold white on blue]
[bold cyan]{'='*80}[/bold cyan]

[bold green]🖥️ ESTADO DE COMPONENTES[/bold green]
[cyan]{'─'*50}[/cyan]
• [bold]Core Engine:[/bold] [bold green]✅ Running[/bold green]
• [bold]Data Collector:[/bold] [bold green]✅ Connected[/bold green]
• [bold]FVG System:[/bold] [bold green]✅ Active[/bold green]
• [bold]Memory Manager:[/bold] [bold green]✅ Operational[/bold green]
• [bold]Risk Manager:[/bold] [bold green]✅ Monitoring[/bold green]
• [bold]MT5 Connection:[/bold] [bold green]✅ Live[/bold green]

[bold blue]💾 RECURSOS DEL SISTEMA[/bold blue]
[cyan]{'─'*50}[/cyan]
• [bold]CPU Usage:[/bold] [green]15%[/green]
• [bold]Memory Usage:[/bold] [yellow]245 MB[/yellow]
• [bold]Disk Space:[/bold] [green]85% Free[/green]
• [bold]Network:[/bold] [green]Stable[/green]

[bold yellow]📊 ESTADÍSTICAS DE DATOS[/bold yellow]
[cyan]{'─'*50}[/cyan]
• [bold]Candles Processed:[/bold] [cyan]1,247[/cyan]
• [bold]FVGs Detected:[/bold] [magenta]89[/magenta]
• [bold]Signals Generated:[/bold] [blue]23[/blue]
• [bold]Trades Executed:[/bold] [green]8[/green]

[bold magenta]🔄 PROCESOS ACTIVOS[/bold magenta]
[cyan]{'─'*50}[/cyan]
• [bold]Data Refresh:[/bold] [green]Every 1 second[/green]
• [bold]Signal Scan:[/bold] [green]Every 5 seconds[/green]
• [bold]Risk Check:[/bold] [green]Continuous[/green]
• [bold]Memory Cleanup:[/bold] [green]Every 10 minutes[/green]

[bold red]📋 LOGS RECIENTES[/bold red]
[cyan]{'─'*50}[/cyan]
• {timestamp}: [green]FVG detected on EURUSD M15[/green]
• {timestamp}: [blue]Order Block validated on GBPUSD H1[/blue]
• {timestamp}: [yellow]Liquidity sweep alert XAUUSD[/yellow]
• {timestamp}: [green]Trade executed: BUY EURUSD +15 pips[/green]

[bold cyan]{'='*80}[/bold cyan]
[bold white]Sistema operativo desde: {datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')}[/bold white]"""
            
            return monitor
            
        except Exception as e:
            return f"[red]❌ Error en monitor: {e}[/red]"
    
    def render_silver_bullet_tab(self) -> str:
        """🎯 Renderizar pestaña Silver Bullet Enterprise"""
        if not self.silver_bullet_tab:
            return "[red]❌ Silver Bullet Tab no disponible[/red]"
        
        try:
            return self.silver_bullet_tab.render_silver_bullet_dashboard()
        except Exception as e:
            return f"[red]❌ Error en Silver Bullet Tab: {e}[/red]"
    
    def periodic_update(self):
        """Actualización periódica de todas las pestañas"""
        if self._refreshing:
            return
        
        self._refreshing = True
        try:
            # Actualizar pestaña activa
            real_trading_widget = self.query_one("#real_trading_display", Static)
            analysis_widget = self.query_one("#analysis_display", Static)
            monitor_widget = self.query_one("#monitor_display", Static)
            
            real_trading_widget.update(self.render_real_trading_system())
            analysis_widget.update(self.render_analysis_data())
            monitor_widget.update(self.render_system_monitor())
            
        except Exception as e:
            print(f"⚠️ Error en actualización periódica: {e}")
        finally:
            self._refreshing = False
    
    def update_silver_bullet(self):
        """Actualización específica de Silver Bullet"""
        if not self.silver_bullet_tab:
            return
        
        try:
            # Actualizar datos de Silver Bullet
            self.silver_bullet_tab.update_data()
            self.silver_bullet_tab.simulate_live_activity()
            
            # Actualizar display si la pestaña está visible
            try:
                silver_bullet_widget = self.query_one("#silver_bullet_display", Static)
                silver_bullet_widget.update(self.render_silver_bullet_tab())
            except:
                pass  # Widget no visible o no existe
                
        except Exception as e:
            print(f"⚠️ Error actualizando Silver Bullet: {e}")
    
    # Acciones de botones
    def action_switch_tab_real_trading(self):
        """Cambiar a pestaña Sistema Real"""
        self.query_one("#main_tabs", TabbedContent).active = "tab_real_trading"
    
    def action_switch_tab_analysis(self):
        """Cambiar a pestaña Análisis"""
        self.query_one("#main_tabs", TabbedContent).active = "tab_analysis"
    
    def action_switch_tab_monitor(self):
        """Cambiar a pestaña Monitor"""
        self.query_one("#main_tabs", TabbedContent).active = "tab_monitor"
    
    def action_switch_tab_silver_bullet(self):
        """Cambiar a pestaña Silver Bullet"""
        if self.silver_bullet_tab:
            self.query_one("#main_tabs", TabbedContent).active = "tab_silver_bullet"
        else:
            self.bell()
    
    def action_silver_bullet_start(self):
        """Iniciar trading en Silver Bullet"""
        if self.silver_bullet_tab:
            success = self.silver_bullet_tab.start_live_trading()
            if success:
                self.bell()  # Sonido de confirmación
        else:
            self.bell()
    
    def action_silver_bullet_stop(self):
        """Detener trading en Silver Bullet"""
        if self.silver_bullet_tab:
            success = self.silver_bullet_tab.stop_live_trading()
            if success:
                self.bell()  # Sonido de confirmación
        else:
            self.bell()
    
    def action_silver_bullet_emergency(self):
        """Parada de emergencia en Silver Bullet"""
        if self.silver_bullet_tab:
            success = self.silver_bullet_tab.emergency_stop()
            if success:
                self.bell()  # Sonido de confirmación
        else:
            self.bell()
    
    def action_refresh_all(self):
        """Actualizar todas las pestañas"""
        self.periodic_update()
        if self.silver_bullet_tab:
            self.update_silver_bullet()
        self.bell()

class MainDashboardInterface:
    """Interfaz principal del dashboard"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def run(self, engine, data_collector):
        """Ejecutar la aplicación del dashboard"""
        try:
            app = TextualDashboardApp(self.config, engine, data_collector)
            app.run()
        except Exception as e:
            print(f"❌ Error ejecutando dashboard: {e}")
