#!/usr/bin/env python3
"""
🎯 PATTERNS TAB - Pestaña de Patrones para Dashboard Principal
=============================================================

Integración de los 11 módulos de patrones en el dashboard principal
usando ÚNICAMENTE la arquitectura existente.

Compatible con Textual framework del dashboard principal.
"""

import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Configurar rutas para acceso a módulos
dashboard_root = Path(__file__).parent.parent
project_root = dashboard_root.parent
sys.path.insert(0, str(project_root / "01-CORE"))
sys.path.insert(0, str(dashboard_root))

# Importar sistema modular existente - CORREGIDO
from patterns_analysis.patterns_orchestrator import PatternsOrchestrator
from patterns_analysis.pattern_factory import PatternFactory
from patterns_analysis.base_pattern_module import PatternAnalysisResult

from textual.containers import Container, Vertical, VerticalScroll, Horizontal
from textual.widgets import Static, TabbedContent, TabPane
from textual.reactive import reactive


class PatternsTab:
    """
    Pestaña de Patrones integrada con dashboard principal
    Usa ÚNICAMENTE el sistema modular existente
    """
    
    def __init__(self, main_dashboard_app):
        """
        Inicializar pestaña usando el patrón del dashboard principal
        
        Args:
            main_dashboard_app: Instancia del TextualDashboardApp principal
        """
        self.main_app = main_dashboard_app
        
        # Usar orchestrator existente - NUNCA duplicar código
        self.orchestrator = PatternsOrchestrator()
        
        # Usar factory existente para descubrimiento automático
        self.factory = PatternFactory()
        self.factory.auto_discover_and_generate()
        
        # Cargar patrones usando sistema existente
        self.available_patterns = self.factory.get_available_patterns()
        self.pattern_modules = {}
        
        # Variables de estado según patrón del dashboard principal
        self.current_symbol = "EURUSD"  # Default, se sincroniza con main
        self.current_timeframes = ["H4", "H1", "M15"]
        self.last_update = None
        self._refreshing = False
        
        # Conectar módulos automáticamente
        self._load_pattern_modules()
        
        print(f"🎯 PatternsTab inicializada - {len(self.available_patterns)} patrones disponibles")
    
    def _load_pattern_modules(self):
        """Cargar módulos de patrones usando factory existente"""
        try:
            for pattern_name in self.available_patterns:
                pattern_instance = self.factory.create_pattern_dashboard(pattern_name)
                if pattern_instance:
                    self.pattern_modules[pattern_name] = pattern_instance
            
            print(f"✅ Cargados {len(self.pattern_modules)} módulos de patrones")
        
        except Exception as e:
            print(f"⚠️ Error cargando módulos de patrones: {e}")
    
    def render_patterns_main_view(self) -> str:
        """
        Renderizar vista principal de patrones usando sistema existente
        Sigue el mismo patrón que render_real_trading_system()
        """
        try:
            # Usar orchestrator para vista consolidada
            consolidated = self.orchestrator.get_consolidated_view(
                symbol=self.current_symbol,
                timeframes=self.current_timeframes,
                force_refresh=False
            )
            
            # Header principal
            content = f"""[bold cyan]🎯 ANÁLISIS DE PATRONES ICT - {self.current_symbol}[/bold cyan]
[cyan]{'─' * 80}[/cyan]

[bold]📊 RESUMEN EJECUTIVO[/bold]
• Timestamp: [dim]{datetime.now().strftime('%H:%M:%S')}[/dim]
• Patrones detectados: [bold]{consolidated.total_patterns_detected}[/bold]
• Alta confianza: [bold][green]{consolidated.high_confidence_patterns}[/green][/bold]
• Oportunidades scalping: [bold][yellow]{consolidated.scalping_opportunities}[/yellow][/bold]
"""
            
            # Mejores setups usando datos reales del orchestrator
            if consolidated.best_overall_setup:
                setup = consolidated.best_overall_setup
                content += f"""
[bold]🎯 MEJOR SETUP DETECTADO[/bold]
• Patrón: [bold]{setup.pattern_name.upper().replace('_', ' ')}[/bold]
• Confianza: [bold][green]{setup.confidence:.1f}%[/green][/bold]
• Dirección: [bold]{setup.direction}[/bold]
• Timeframe: [bold]{setup.timeframe}[/bold]
"""
                
                if setup.entry_zone != (0.0, 0.0):
                    content += f"• Entry Zone: [{setup.entry_zone[0]:.5f} - {setup.entry_zone[1]:.5f}]\n"
                if setup.stop_loss > 0:
                    content += f"• Stop Loss: [red]{setup.stop_loss:.5f}[/red]\n"
                if setup.take_profit_1 > 0:
                    content += f"• Take Profit: [green]{setup.take_profit_1:.5f}[/green]\n"
            
            # Lista de patrones activos usando datos reales
            active_patterns = [name for name, summary in consolidated.patterns_summary.items() 
                             if summary.get('confidence', 0) > 50]
            
            if active_patterns:
                content += f"""
[bold]🔥 PATRONES ACTIVOS ({len(active_patterns)})[/bold]
"""
                for pattern in active_patterns[:5]:  # Top 5
                    summary = consolidated.patterns_summary[pattern]
                    conf = summary.get('confidence', 0)
                    direction = summary.get('direction', 'NEUTRAL')
                    
                    conf_color = "green" if conf > 75 else "yellow" if conf > 50 else "red"
                    direction_emoji = "🟢" if direction == "BULLISH" else "🔴" if direction == "BEARISH" else "🟡"
                    
                    # Usar markup más seguro para evitar problemas de etiquetas
                    if conf > 75:
                        conf_display = f"[green]{conf:.1f}%[/green]"
                    elif conf > 50:
                        conf_display = f"[yellow]{conf:.1f}%[/yellow]" 
                    else:
                        conf_display = f"[red]{conf:.1f}%[/red]"
                    
                    content += f"• {direction_emoji} [bold]{pattern.replace('_', ' ').upper()}[/bold]: {conf_display} {direction}\n"
            
            # Navegación a patrones individuales
            content += f"""
[bold]🎮 NAVEGACIÓN[/bold]
• Tecla [bold]4[/bold]: Análisis consolidado (esta vista)
• Teclas [bold]A-K[/bold]: Patrones individuales
• [bold]F5[/bold]: Actualizar datos
"""
            
            # Lista de patrones disponibles con teclas de acceso
            content += f"""
[bold]📋 PATRONES DISPONIBLES ({len(self.available_patterns)})[/bold]
"""
            pattern_keys = "ABCDEFGHIJK"
            for i, pattern in enumerate(self.available_patterns):
                if i < len(pattern_keys):
                    key = pattern_keys[i]
                    enterprise_mark = " [ENTERPRISE]" if pattern in ["silver_bullet", "judas_swing", "liquidity_grab"] else ""
                    confidence = consolidated.patterns_summary.get(pattern, {}).get('confidence', 0)
                    conf_display = f"[green]{confidence:.0f}%[/green]" if confidence > 0 else "[dim]N/A[/dim]"
                    
                    content += f"• [{key}] [bold]{pattern.replace('_', ' ').title()}[/bold]{enterprise_mark} - {conf_display}\n"
            
            return content
        
        except Exception as e:
            return f"[red]❌ Error en análisis de patrones: {e}[/red]"
    
    def render_individual_pattern(self, pattern_name: str) -> str:
        """
        Renderizar vista individual de un patrón usando módulo específico
        """
        try:
            if pattern_name not in self.pattern_modules:
                return f"[red]❌ Patrón no disponible: {pattern_name}[/red]"
            
            pattern_module = self.pattern_modules[pattern_name]
            
            # Usar método del módulo individual para análisis
            result = pattern_module.analyze_pattern(
                symbol=self.current_symbol,
                timeframe=self.current_timeframes[0]  # Usar primer timeframe
            )
            
            # Usar método del módulo para layout
            layout = pattern_module.create_dashboard_layout(result)
            
            # Agregar navegación de vuelta
            layout += f"""

[bold]🎮 NAVEGACIÓN[/bold]
• Tecla [bold]4[/bold]: Volver a vista consolidada
• [bold]F5[/bold]: Actualizar este patrón
• Otras teclas: Ver otros patrones
"""
            
            return layout
        
        except Exception as e:
            return f"[red]❌ Error renderizando patrón {pattern_name}: {e}[/red]"
    
    def update_patterns_data(self):
        """
        Actualizar datos de patrones usando orchestrator existente
        Sigue el mismo patrón que periodic_update() del dashboard principal
        """
        if self._refreshing:
            return
        
        self._refreshing = True
        try:
            # Usar orchestrator para actualización masiva
            self.orchestrator.update_all_patterns(
                symbol=self.current_symbol,
                timeframes=self.current_timeframes,
                priority_only=False
            )
            
            self.last_update = datetime.now()
            
        except Exception as e:
            print(f"⚠️ Error actualizando patrones: {e}")
        finally:
            self._refreshing = False
    
    def get_current_view_content(self, current_view: str = "main") -> str:
        """
        Obtener contenido de la vista actual
        
        Args:
            current_view: "main" para vista consolidada, o nombre del patrón para vista individual
        """
        if current_view == "main":
            return self.render_patterns_main_view()
        else:
            return self.render_individual_pattern(current_view)
    
    def sync_with_main_dashboard(self, symbol: str, timeframes: List[str]):
        """
        Sincronizar configuración con dashboard principal
        """
        self.current_symbol = symbol
        self.current_timeframes = timeframes
        
        # Actualizar datos con nueva configuración
        self.update_patterns_data()
    
    def get_available_pattern_names(self) -> List[str]:
        """Obtener lista de patrones disponibles"""
        return self.available_patterns.copy()
    
    def get_pattern_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de patrones para mostrar en footer o header"""
        try:
            consolidated = self.orchestrator.get_consolidated_view(
                symbol=self.current_symbol,
                timeframes=self.current_timeframes,
                force_refresh=False
            )
            
            return {
                "total_patterns": len(self.available_patterns),
                "active_patterns": consolidated.total_patterns_detected,
                "high_confidence": consolidated.high_confidence_patterns,
                "scalping_ops": consolidated.scalping_opportunities,
                "last_update": self.last_update.strftime('%H:%M:%S') if self.last_update else 'Never'
            }
        
        except Exception as e:
            print(f"⚠️ Error obteniendo stats de patrones: {e}")
            return {
                "total_patterns": len(self.available_patterns),
                "active_patterns": 0,
                "high_confidence": 0,
                "scalping_ops": 0,
                "last_update": 'Error'
            }
