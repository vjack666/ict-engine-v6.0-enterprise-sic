"""
🎯 ICT Engine v6.0 Enterprise - Dashboard Interface LIMPIO
===================================================================

Dashboard completamente limpio sin referencias a componentes eliminados.
Listo para nueva construcción modular.

Author: ICT Engine Development Team
Date: 2024
Version: 6.1 Enterprise Clean
"""

from datetime import datetime
import time
import uuid
from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual import events

class TextualDashboardApp(Screen):
    """🚀 Dashboard principal ICT Enterprise - Versión Limpia"""
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("ctrl+c", "quit", "Force Quit")
    ]
    
    CSS = """
    Screen {
        background: #1a1a1a;
    }
    
    .main_container {
        margin: 1;
        padding: 1;
        background: #2a2a2a;
        border: solid #4a4a4a;
        border-title-align: center;
    }
    
    #main_display {
        background: #1e1e1e;
        color: #ffffff;
        padding: 1;
        margin: 1;
        border: solid #3a3a3a;
        height: auto;
        min-height: 20;
        scrollbar-gutter: stable;
        overflow-y: auto;
    }
    
    Header {
        dock: top;
        height: 3;
        background: #0f4c75;
        color: #ffffff;
    }
    
    Footer {
        dock: bottom;
        height: 3;
        background: #0f4c75;
        color: #ffffff;
    }
    """
    
    def __init__(self, config=None):
        """🎯 Inicializar Dashboard Limpio"""
        super().__init__()
        
        # Configuración básica
        self.config = config or {"symbols": ["EURUSD"], "timeframes": ["H1"]}
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()
        self._refreshing = False
        
        print(f"🚀 [DASHBOARD] Iniciando Dashboard Limpio - Sesión: {self.session_id}")
    
    def compose(self) -> ComposeResult:
        """🎨 Componer la interfaz limpia"""
        yield Header()
        
        with Vertical(classes="main_container", id="main_container"):
            yield Static(
                self.render_clean_dashboard(),
                id="main_display",
                name="main_display"
            )
        
        yield Footer()
    
    def on_mount(self) -> None:
        """🚀 Al montar la aplicación"""
        self.title = "ICT Engine v6.0 Enterprise - Dashboard Limpio"
        self.sub_title = f"Sesión: {self.session_id} | Clean State"
        
        # Configurar timer para actualizaciones
        self.set_interval(5.0, self.periodic_update)
        
        print("✅ [DASHBOARD] Dashboard limpio montado correctamente")
    
    def render_clean_dashboard(self) -> str:
        """🎯 Renderiza un dashboard minimalista y limpio"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uptime = time.time() - self.start_time
        uptime_str = f"{int(uptime // 3600):02d}:{int((uptime % 3600) // 60):02d}:{int(uptime % 60):02d}"
        
        return f"""
[bold green]🚀 ICT Engine v6.0 Enterprise - Dashboard Limpio[/bold green]

[bold cyan]{'='*80}[/bold cyan]

📊 [bold]Estado del Sistema:[/bold]
• [bold]Status:[/bold] [green]Sistema Iniciado[/green]
• [bold]Timestamp:[/bold] [cyan]{timestamp}[/cyan]
• [bold]Sesión:[/bold] [cyan]{self.session_id}[/cyan]
• [bold]Uptime:[/bold] [yellow]{uptime_str}[/yellow]
• [bold]Modo:[/bold] [bold green]Dashboard Limpio[/bold green]

🎯 [bold]Dashboard Preparado[/bold]
• Todas las pestañas anteriores han sido removidas
• Sistema listo para nueva construcción modular
• Interfaz limpia y optimizada
• Sin referencias a componentes eliminados

📋 [bold]Configuración Actual:[/bold]
• [bold]Símbolos:[/bold] [cyan]{', '.join(self.config.get('symbols', ['EURUSD']))}[/cyan]
• [bold]Timeframes:[/bold] [cyan]{', '.join(self.config.get('timeframes', ['H1']))}[/cyan]

🔧 [bold]Componentes Listos:[/bold]
• Core Engine: [green]✅ Ready[/green]
• Dashboard Framework: [green]✅ Clean[/green]
• Configuration System: [green]✅ Loaded[/green]
• UI Framework: [green]✅ Textual[/green]

[bold cyan]{'='*80}[/bold cyan]

[dim]💡 Listo para implementar nuevos módulos y funcionalidades...[/dim]
[dim]🎯 Use 'r' para refresh, 'q' para salir[/dim]
"""
    
    def periodic_update(self):
        """🔄 Actualización periódica simple"""
        if self._refreshing:
            return
            
        try:
            self._refreshing = True
            
            # Actualizar solo el display principal
            main_display = self.query_one("#main_display", Static)
            main_display.update(self.render_clean_dashboard())
            
        except Exception as e:
            print(f"⚠️ Error en periodic_update: {e}")
        finally:
            self._refreshing = False
    
    async def action_refresh(self):
        """🔄 Acción de refresh manual"""
        self.periodic_update()
        print("🔄 [DASHBOARD] Dashboard actualizado manualmente")
    
    async def action_quit(self):
        """🛑 Override quit action para cleanup apropiado"""
        try:
            print(f"\n🛑 [DASHBOARD] Iniciando secuencia de cierre limpio - Sesión: {self.session_id}")
            print("✅ [DASHBOARD] Cleanup completado - cerrando app...")
            
        except Exception as e:
            print(f"❌ [DASHBOARD] Error en cleanup: {e}")
        finally:
            # Llamar al quit original para cerrar la app
            self.app.exit()
    
    def on_key(self, event: events.Key) -> None:
        """⌨️ Manejar eventos de teclado"""
        key = event.key
        
        if key == "r":
            self.periodic_update()
            print("🔄 [DASHBOARD] Dashboard actualizado manualmente")
        elif key == "q" or key == "ctrl+c":
            self.app.exit()
    
    def __repr__(self) -> str:
        """🔍 Representación del objeto"""
        return f"TextualDashboardApp(session={self.session_id}, clean=True)"