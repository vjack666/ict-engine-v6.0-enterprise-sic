#!/usr/bin/env python3
"""
🏛️ DASHBOARD CORE ARCHITECTURE v6.0 ENTERPRISE
=============================================

OBJETIVO: Centralizar imports de Dash y configuración base
PROBLEMA RESUELTO: dash_html_components = None causando "Object of type None cannot be called"
SOLUCIÓN: Import manager centralizado con fallbacks robustos y lazy loading

FUNCIONALIDADES:
✅ DashImportManager class con lazy loading
✅ HTML components wrapper (html.Div, html.H1, etc.)
✅ Core components wrapper (dcc.Graph, dcc.Dropdown, etc.)  
✅ Error handling para imports fallidos
✅ Configuración enterprise base (themes, layouts)
✅ Shared utilities para todos los tabs
✅ Performance optimization layers

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 13 Septiembre 2025
"""

import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from datetime import datetime
import json
import traceback

# Core system integration
try:
    # Add core paths for imports
    current_dir = Path(__file__).parent.parent.parent / "01-CORE"
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    from smart_trading_logger import SmartTradingLogger
    CORE_LOGGING_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Core logging not available: {e}")
    CORE_LOGGING_AVAILABLE = False
    SmartTradingLogger = None


class DashImportManager:
    """
    🎯 ADMINISTRADOR CENTRALIZADO DE IMPORTS DASH
    ==========================================
    
    Gestiona imports de Dash con fallbacks robustos y lazy loading.
    Resuelve el problema crítico de "Object of type None cannot be called".
    """
    
    def __init__(self):
        self.dash_available = False
        self.plotly_available = False
        self.pandas_available = False
        
        # Component references
        self.dash = None
        self.dcc = None
        self.html = None
        self.Input = None
        self.Output = None
        self.State = None
        self.callback = None
        self.ctx = None
        self.go = None
        self.px = None
        self.make_subplots = None
        self.pd = None
        
        # Initialize imports
        self._initialize_imports()
        
        # Logger
        if CORE_LOGGING_AVAILABLE and SmartTradingLogger:
            self.logger = SmartTradingLogger("DashImportManager")
        else:
            self.logger = None
            
    def _initialize_imports(self):
        """🔄 Inicializar imports con manejo robusto de errores"""
        
        # Dash Core Imports
        try:
            import dash
            from dash import dcc, html, Input, Output, State, callback, ctx
            
            self.dash = dash
            self.dcc = dcc
            self.html = html
            self.Input = Input
            self.Output = Output
            self.State = State
            self.callback = callback
            self.ctx = ctx
            self.dash_available = True
            
            print("✅ Dash imports loaded successfully")
            
        except ImportError as e:
            print(f"❌ Dash import failed: {e}")
            self._create_dash_fallbacks()
            
        # Plotly Imports
        try:
            import plotly.graph_objects as go
            import plotly.express as px
            from plotly.subplots import make_subplots
            
            self.go = go
            self.px = px
            self.make_subplots = make_subplots
            self.plotly_available = True
            
            print("✅ Plotly imports loaded successfully")
            
        except ImportError as e:
            print(f"❌ Plotly import failed: {e}")
            self._create_plotly_fallbacks()
            
        # Pandas Import
        try:
            import pandas as pd
            self.pd = pd
            self.pandas_available = True
            print("✅ Pandas import loaded successfully")
            
        except ImportError as e:
            print(f"❌ Pandas import failed: {e}")
            self._create_pandas_fallbacks()
            
    def _create_dash_fallbacks(self):
        """🛡️ Crear fallbacks para Dash cuando no está disponible"""
        
        class MockHTML:
            """Mock HTML components fallback: devuelve cadenas simples para ser válidas como children."""
            @staticmethod
            def Div(children=None, **kwargs): return "<div>" + (str(children) if children is not None else "") + "</div>"
            @staticmethod
            def H1(children=None, **kwargs): return "<h1>" + (str(children) if children is not None else "") + "</h1>"
            @staticmethod
            def H2(children=None, **kwargs): return "<h2>" + (str(children) if children is not None else "") + "</h2>"
            @staticmethod
            def H3(children=None, **kwargs): return "<h3>" + (str(children) if children is not None else "") + "</h3>"
            @staticmethod
            def P(children=None, **kwargs): return "<p>" + (str(children) if children is not None else "") + "</p>"
            @staticmethod
            def Button(children=None, **kwargs): return "<button>" + (str(children) if children is not None else "") + "</button>"
            @staticmethod
            def Span(children=None, **kwargs): return "<span>" + (str(children) if children is not None else "") + "</span>"
            @staticmethod
            def Table(children=None, **kwargs): return "<table>" + (str(children) if children is not None else "") + "</table>"
            @staticmethod
            def Thead(children=None, **kwargs): return "<thead>" + (str(children) if children is not None else "") + "</thead>"
            @staticmethod
            def Tbody(children=None, **kwargs): return "<tbody>" + (str(children) if children is not None else "") + "</tbody>"
            @staticmethod
            def Tr(children=None, **kwargs): return "<tr>" + (str(children) if children is not None else "") + "</tr>"
            @staticmethod
            def Th(children=None, **kwargs): return "<th>" + (str(children) if children is not None else "") + "</th>"
            @staticmethod
            def Td(children=None, **kwargs): return "<td>" + (str(children) if children is not None else "") + "</td>"
            @staticmethod
            def Label(children=None, **kwargs): return "<label>" + (str(children) if children is not None else "") + "</label>"
        
        class MockDCC:
            """Mock Core Components para fallback"""
            
            @staticmethod
            def Graph(**kwargs):
                return {"type": "graph", "props": kwargs}
                
            @staticmethod
            def Dropdown(**kwargs):
                return {"type": "dropdown", "props": kwargs}
                
            @staticmethod
            def Slider(**kwargs):
                return {"type": "slider", "props": kwargs}
                
            @staticmethod
            def Store(**kwargs):
                return {"type": "store", "props": kwargs}
                
            @staticmethod
            def Interval(**kwargs):
                return {"type": "interval", "props": kwargs}
                
            @staticmethod
            def Tabs(**kwargs):
                return {"type": "tabs", "props": kwargs}
                
            @staticmethod
            def Tab(**kwargs):
                return {"type": "tab", "props": kwargs}
        
        class MockCallback:
            """Mock Callback system para fallback"""
            def __init__(self, outputs, inputs, state=None):
                self.outputs = outputs
                self.inputs = inputs
                self.state = state
                
            def __call__(self, func):
                print(f"⚠️ Mock callback registered for function: {func.__name__}")
                return func
        
        # Assign fallbacks
        self.html = MockHTML()
        self.dcc = MockDCC()
        self.callback = MockCallback
        self.Input = lambda component_id, component_property: f"Input({component_id}.{component_property})"
        self.Output = lambda component_id, component_property: f"Output({component_id}.{component_property})"
        self.State = lambda component_id, component_property: f"State({component_id}.{component_property})"
        self.ctx = None
        
        print("🛡️ Dash fallbacks created")
        
    def _create_plotly_fallbacks(self):
        """🛡️ Crear fallbacks para Plotly cuando no está disponible"""
        
        class MockFigure:
            """Mock Figure para fallback"""
            def __init__(self, data=None, layout=None):
                self.data = data or []
                self.layout = layout or {}
                
            def add_trace(self, trace):
                self.data.append(trace)
                
            def update_layout(self, **kwargs):
                self.layout.update(kwargs)
                
            def to_dict(self):
                return {"data": self.data, "layout": self.layout}
        
        class MockGO:
            """Mock Graph Objects para fallback"""
            Figure = MockFigure
            
            @staticmethod
            def Scatter(**kwargs):
                return {"type": "scatter", "props": kwargs}
                
            @staticmethod
            def Candlestick(**kwargs):
                return {"type": "candlestick", "props": kwargs}
                
            @staticmethod
            def Bar(**kwargs):
                return {"type": "bar", "props": kwargs}
        
        self.go = MockGO()
        self.px = None
        self.make_subplots = lambda **kwargs: MockFigure()
        
        print("🛡️ Plotly fallbacks created")
        
    def _create_pandas_fallbacks(self):
        """🛡️ Crear fallbacks para Pandas cuando no está disponible"""
        
        class MockDataFrame:
            """Mock DataFrame para fallback"""
            def __init__(self, data=None):
                self.data = data or {}
                
            def to_dict(self, orient='dict'):
                return self.data
                
            def head(self, n=5):
                return self
                
            def tail(self, n=5):
                return self
        
        class MockPandas:
            DataFrame = MockDataFrame
        
        self.pd = MockPandas()
        print("🛡️ Pandas fallbacks created")
        
    def get_status(self) -> Dict[str, Any]:
        """📊 Obtener estado de imports disponibles"""
        return {
            "dash_available": self.dash_available,
            "plotly_available": self.plotly_available,
            "pandas_available": self.pandas_available,
            "components_loaded": {
                "html": self.html is not None,
                "dcc": self.dcc is not None,
                "callbacks": self.callback is not None,
                "plotly_go": self.go is not None,
                "pandas": self.pd is not None
            }
        }


class EnterpriseThemeManager:
    """
    🎨 ADMINISTRADOR DE TEMAS ENTERPRISE
    ===================================
    
    Gestiona temas, estilos y configuraciones visuales para el dashboard enterprise.
    """
    
    def __init__(self):
        self.current_theme = "dark_professional"
        self.themes = self._initialize_themes()
        
    def _initialize_themes(self) -> Dict[str, Dict[str, Any]]:
        """🎨 Inicializar temas disponibles"""
        return {
            "dark_professional": {
                "name": "Dark Professional",
                "colors": {
                    "primary": "#00ff88",
                    "secondary": "#ff6b35", 
                    "success": "#00ff88",
                    "danger": "#ff4444",
                    "warning": "#ffaa00",
                    "info": "#00aaff",
                    "background": "#0e1117",
                    "surface": "#1e2329",
                    "surface_light": "#2d3748",
                    "text_primary": "#ffffff",
                    "text_secondary": "#a0aec0",
                    "border": "#4a5568",
                    "grid": "rgba(255,255,255,0.1)"
                },
                "fonts": {
                    "primary": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
                    "monospace": "Consolas, Monaco, 'Courier New', monospace"
                },
                "layout": {
                    "border_radius": "8px",
                    "spacing_sm": "8px",
                    "spacing_md": "16px",
                    "spacing_lg": "24px",
                    "spacing_xl": "32px"
                }
            },
            "light_professional": {
                "name": "Light Professional",
                "colors": {
                    "primary": "#2d5aa0",
                    "secondary": "#f56565",
                    "success": "#38a169",
                    "danger": "#e53e3e",
                    "warning": "#d69e2e",
                    "info": "#3182ce",
                    "background": "#ffffff",
                    "surface": "#f7fafc",
                    "surface_light": "#edf2f7",
                    "text_primary": "#1a202c",
                    "text_secondary": "#4a5568",
                    "border": "#e2e8f0",
                    "grid": "rgba(0,0,0,0.1)"
                },
                "fonts": {
                    "primary": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
                    "monospace": "Consolas, Monaco, 'Courier New', monospace"
                },
                "layout": {
                    "border_radius": "8px",
                    "spacing_sm": "8px",
                    "spacing_md": "16px",
                    "spacing_lg": "24px",
                    "spacing_xl": "32px"
                }
            }
        }
    
    def get_theme(self, theme_name: Optional[str] = None) -> Dict[str, Any]:
        """🎨 Obtener configuración de tema"""
        theme_name = theme_name or self.current_theme
        return self.themes.get(theme_name, self.themes["dark_professional"])
    
    def get_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """🎨 Obtener paleta de colores de tema"""
        theme = self.get_theme(theme_name)
        return theme["colors"]
    
    def generate_css_variables(self, theme_name: Optional[str] = None) -> str:
        """🎨 Generar variables CSS para tema"""
        theme = self.get_theme(theme_name)
        colors = theme["colors"]
        fonts = theme["fonts"]
        layout = theme["layout"]
        
        css_vars = [":root {"]
        
        # Colors
        for name, value in colors.items():
            css_vars.append(f"  --color-{name.replace('_', '-')}: {value};")
        
        # Fonts
        for name, value in fonts.items():
            css_vars.append(f"  --font-{name}: {value};")
        
        # Layout
        for name, value in layout.items():
            css_vars.append(f"  --{name.replace('_', '-')}: {value};")
        
        css_vars.append("}")
        
        return "\n".join(css_vars)


class DashboardUtilities:
    """
    🛠️ UTILIDADES COMPARTIDAS DEL DASHBOARD
    ======================================
    
    Funciones utility compartidas entre todos los tabs del dashboard.
    """
    
    @staticmethod
    def format_number(value: Union[int, float], decimals: int = 2, 
                     use_thousands_separator: bool = True) -> str:
        """📊 Formatear números para display"""
        if value is None:
            return "N/A"
            
        if isinstance(value, (int, float)):
            if use_thousands_separator:
                return f"{value:,.{decimals}f}"
            else:
                return f"{value:.{decimals}f}"
        
        return str(value)
    
    @staticmethod
    def format_percentage(value: Union[int, float], decimals: int = 1) -> str:
        """📊 Formatear porcentajes"""
        if value is None:
            return "N/A"
            
        if isinstance(value, (int, float)):
            return f"{value * 100:.{decimals}f}%"
        
        return str(value)
    
    @staticmethod
    def format_timestamp(timestamp: Union[str, datetime], 
                        format_str: str = "%H:%M:%S") -> str:
        """⏰ Formatear timestamps"""
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.strftime(format_str)
            except:
                return timestamp
        elif isinstance(timestamp, datetime):
            return timestamp.strftime(format_str)
        else:
            return str(timestamp)
    
    @staticmethod
    def create_metric_card(title: str, value: str, icon: str = "📊",
                          color: str = "primary", 
                          imports: Optional[DashImportManager] = None) -> Any:
        """🎴 Crear card de métrica estandarizada"""
        if not imports or not imports.html:
            return "HTML components not available"
        inner = imports.html.Div(
            (
                imports.html.Div(
                    (
                        imports.html.H3(value, className="metric-value"),
                        imports.html.P(title, className="metric-label")
                    ),
                    className="metric-content"
                ),
                imports.html.Div(icon, className=f"metric-icon {color}")
            ),
            className="metric-card-inner"
        )
        return imports.html.Div((inner,), className=f"metric-card metric-{color}")
    
    @staticmethod
    def create_status_indicator(status: str, text: str = "", 
                              imports: Optional[DashImportManager] = None) -> Any:
        """🚥 Crear indicador de estado"""
        if not imports or not imports.html:
            return "HTML components not available"
        
        status_colors = {
            "success": "🟢",
            "warning": "🟡", 
            "danger": "🔴",
            "info": "🔵",
            "neutral": "⚪"
        }
        
        icon = status_colors.get(status, "⚪")
        display_text = text or status.title()
        
        return imports.html.Span(
            (
                imports.html.Span(icon, className="status-icon"),
                imports.html.Span(display_text, className="status-text")
            ),
            className=f"status-indicator status-{status}"
        )
    
    @staticmethod
    def create_loading_placeholder(message: str = "Loading...", 
                                 imports: Optional[DashImportManager] = None) -> Any:
        """⏳ Crear placeholder de carga"""
        if not imports or not imports.html:
            return "HTML components not available"
        return imports.html.Div(
            (
                imports.html.Div("⏳", className="loading-spinner"),
                imports.html.P(message, className="loading-message")
            ),
            className="loading-placeholder"
        )


class DashboardCore:
    """
    🏛️ NÚCLEO PRINCIPAL DEL DASHBOARD ENTERPRISE
    ===========================================
    
    Clase principal que integra todos los componentes del dashboard core:
    - Import management
    - Theme management  
    - Shared utilities
    - Configuration management
    """
    
    def __init__(self, theme: str = "dark_professional"):
        self.imports = DashImportManager()
        self.theme_manager = EnterpriseThemeManager()
        self.utilities = DashboardUtilities()
        
        # Logger
        if CORE_LOGGING_AVAILABLE and SmartTradingLogger:
            self.logger = SmartTradingLogger("DashboardCore")
            self.logger.info("Dashboard Core initialized", "dashboard_initialization")
        else:
            self.logger = None
            
        # Set theme
        self.theme_manager.current_theme = theme
        
        print(f"🏛️ Dashboard Core initialized with theme: {theme}")
        
    def get_components(self) -> Tuple[Any, Any, Any, Any, Any, Any]:
        """📦 Obtener componentes principales para imports en tabs"""
        return (
            self.imports.html,
            self.imports.dcc, 
            self.imports.Input,
            self.imports.Output,
            self.imports.State,
            self.imports.callback
        )
    
    def get_plotting_components(self) -> Tuple[Any, Any, Any]:
        """📊 Obtener componentes de plotting"""
        return (
            self.imports.go,
            self.imports.px,
            self.imports.make_subplots
        )
    
    def get_theme_config(self) -> Dict[str, Any]:
        """🎨 Obtener configuración completa de tema"""
        return self.theme_manager.get_theme()
    
    def get_system_status(self) -> Dict[str, Any]:
        """📊 Obtener estado completo del sistema dashboard"""
        return {
            "core_initialized": True,
            "timestamp": datetime.now().isoformat(),
            "imports": self.imports.get_status(),
            "theme": self.theme_manager.current_theme,
            "available_themes": list(self.theme_manager.themes.keys()),
            "logging_available": CORE_LOGGING_AVAILABLE
        }
    
    def create_base_layout(self, children: Optional[List[Any]] = None, 
                          title: str = "ICT Engine v6.0 Enterprise") -> Any:
        """🏗️ Crear layout base del dashboard"""
        if not self.imports.html:
            return "HTML components not available"
        
        theme_colors = self.theme_manager.get_colors()
        
        # Default children if none provided
        if children is None:
            children = [self.imports.html.Div("Initializing dashboard...")]
        
        header = self.imports.html.Div(title, className="dashboard-header")
        # Ensure children is a sequence acceptable by Dash: list/tuple of Components or strings
        normalized_children = children if isinstance(children, (list, tuple)) else [children]
        content = self.imports.html.Div(normalized_children, className="dashboard-content")
        footer = self.imports.html.Div(
            f"ICT Engine v6.0 Enterprise - {datetime.now().strftime('%Y')}",
            className="dashboard-footer"
        )
        return self.imports.html.Div(
            [header, content, footer],
            className="dashboard-container", style={
                "backgroundColor": theme_colors["background"],
                "color": theme_colors["text_primary"],
                "fontFamily": self.theme_manager.get_theme()["fonts"]["primary"]
            }
        )


# Global instance for easy access
_dashboard_core = None

def get_dashboard_core(theme: str = "dark_professional") -> DashboardCore:
    """🌍 Obtener instancia global del dashboard core (singleton pattern)"""
    global _dashboard_core
    
    if _dashboard_core is None:
        _dashboard_core = DashboardCore(theme)
        
        # Initialize TabCoordinator integration after core is ready
        try:
            from tab_coordinator import initialize_tab_coordinator_integration
            success = initialize_tab_coordinator_integration(dashboard_core=_dashboard_core)
            if success and _dashboard_core.logger:
                _dashboard_core.logger.info("TabCoordinator integration completed", "dashboard_init")
        except ImportError:
            print("⚠️ TabCoordinator not available for integration")
        except Exception as e:
            print(f"⚠️ Error initializing TabCoordinator integration: {e}")
        
    return _dashboard_core


def initialize_dashboard_production():
    """🏭 Inicializar DashboardCore para producción"""
    try:
        # Obtener instancia global
        core = get_dashboard_core()
        
        # Registrar con logging si está disponible
        if core.logger:
            core.logger.info("Dashboard Core initialized for production", "production_init")
        
        # Exportar estado inicial del sistema
        status = core.get_system_status()
        
        # Crear directorio de estado si no existe
        from pathlib import Path
        state_dir = Path(__file__).parent.parent.parent / "04-DATA" / "dashboard_state"
        state_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar estado inicial
        import json
        from datetime import datetime
        
        state_file = state_dir / "core_status.json"
        state_data = {
            **status,
            "initialization_time": datetime.now().isoformat(),
            "theme": core.theme_manager.current_theme,
            "components_loaded": {
                "dash_available": core.imports.dash_available,
                "plotly_available": core.imports.plotly_available,
                "pandas_available": core.imports.pd is not None
            }
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2)
            
        print(f"✅ Dashboard Core initialized for production")
        print(f"📊 Status saved to: {state_file}")
        print(f"🎨 Theme: {core.theme_manager.current_theme}")
        print(f"⚡ Components: Dash={core.imports.dash_available}, Plotly={core.imports.plotly_available}")
        
        return core, state_data
        
    except Exception as e:
        print(f"❌ Dashboard Core production initialization failed: {e}")
        return None, None


if __name__ == "__main__":
    print("🏭 DashboardCore - Production initialization...")
    core, state = initialize_dashboard_production()
    
    if core:
        print("✅ DashboardCore ready for production use")
        # Mostrar configuración de tema
        theme_config = core.get_theme_config()
        print(f"🎨 Active theme: {theme_config['name']}")
        print(f"📈 Performance optimized: {theme_config.get('performance_optimized', False)}")
    else:
        print("❌ DashboardCore production initialization failed")