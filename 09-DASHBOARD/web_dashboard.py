#!/usr/bin/env python3
"""
🎯 ICT ENGINE v6.0 ENTERPRISE - WEB DASHBOARD PRINCIPAL
=====================================================

Dashboard web principal usando Dash que integra todas las pestañas del sistema ICT.
Incluye la nueva pestaña Order Blocks con logging avanzado y visualización en tiempo real.

Funcionalidades:
✅ Arquitectura modular con pestañas especializadas
✅ Pestaña Order Blocks con detección en tiempo real
✅ Integración con OrderBlocksBlackBox logging
✅ Auto-refresh cada 0.5 segundos
✅ Interfaz dark theme profesional
✅ Métricas de performance en tiempo real

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 12 Septiembre 2025
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union, Protocol
import time

# Configurar paths
dashboard_root = Path(__file__).parent.absolute()
project_root = dashboard_root.parent
core_path = project_root / "01-CORE"

sys.path.extend([
    str(project_root),
    str(core_path),
    str(dashboard_root),
    str(dashboard_root / "core"),
    str(dashboard_root / "core" / "tabs"),
    str(dashboard_root / "styles")
])

# Dashboard framework imports with fallback
try:
    import dash
    from dash import Dash, html, dcc, Input, Output, callback
    import plotly.graph_objects as go
    import pandas as pd
    print("✅ Dash framework loaded successfully")
except ImportError as e:  # runtime hard failure (no modo mock)
    raise ImportError(f"Dash no instalado. Instala dependencias: pip install dash plotly pandas. Detalle: {e}")

try:
    from core.tabs.order_blocks_tab import OrderBlocksTab, create_order_blocks_tab  # Real tab factory (returns instance)
    print("✅ Order Blocks Tab loaded successfully")
except Exception as e:  # pragma: no cover - must hard fail (no modo mock)
    raise ImportError(f"No se pudo importar OrderBlocksTab real: {e}")

# Performance tab (metrics) - real only (sin fallback)
try:
    from core.tabs.performance_tab import PerformanceTab, create_performance_tab
    print("✅ Performance Tab module loaded")
except Exception as e:  # pragma: no cover
    raise ImportError(f"No se pudo importar Performance Tab real: {e}")

# Risk & Health tab - real only (sin fallback)
try:
    from core.tabs.risk_health_tab import RiskHealthTab, create_risk_health_tab
    print("✅ Risk & Health Tab module loaded")
except Exception as e:  # pragma: no cover
    raise ImportError(f"No se pudo importar Risk & Health Tab real: {e}")


class _HasCreateLayout(Protocol):  # runtime-light structural protocol para tipado
    def create_layout(self) -> Any: ...  # noqa: D401 (simple protocol)


DashboardTabType = _HasCreateLayout  # alias semántico


class ICTWebDashboard:
    """
    🎯 ICT ENGINE WEB DASHBOARD v6.0 ENTERPRISE
    ==========================================
    
    Dashboard web principal que integra todas las pestañas y componentes
    del sistema ICT Engine en una interfaz profesional y escalable.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        
        # Dash requerido: ya validado en import
        
        # Initialize Dash app
        self.app = Dash(
            __name__,
            suppress_callback_exceptions=True,
            external_stylesheets=[
                'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap'
            ],
            title="🎯 ICT Engine v6.0 Enterprise Dashboard"
        )
        
        # Configure server settings
        self.app.server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

        # Initialize tabs (clave -> instancia con .create_layout())
        self.tabs: Dict[str, DashboardTabType] = {}
        self._initialize_tabs()
        
        # Setup layout only if real Dash available
        self._setup_layout()
        
        print(f"🎯 ICT Web Dashboard initialized")
        print(f"   Refresh interval: {self.config['refresh_interval']}ms")
        print(f"   Available tabs: {len(self.tabs)}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuración por defecto del dashboard"""
        return {
            'refresh_interval': 500,  # ms
            'host': '127.0.0.1',
            'port': 8050,
            'debug': True,
            'auto_reload': True,
            'theme': 'dark',
            'default_tab': 'order_blocks',
            'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'XAUUSD'],
            'timeframes': ['M1', 'M5', 'M15', 'M30', 'H1', 'H4']
        }
    
    def _initialize_tabs(self):
        """Inicializar todas las pestañas disponibles (solo implementaciones reales)."""
        # Order Blocks (requerido, la factory devuelve instancia real o lanza)
        try:
            ob_tab = create_order_blocks_tab(app=self.app, refresh_interval=self.config['refresh_interval'])
            self.tabs['order_blocks'] = ob_tab  # asume interfaz con create_layout()
            print("✅ Order Blocks Tab initialized (real)")
        except Exception as e:
            print(f"❌ No se pudo inicializar Order Blocks Tab: {e}")
            raise

        # Performance Tab
        metrics_dir_guess = str(project_root / '04-DATA' / 'metrics')
        try:
            perf_tab = create_performance_tab(app=self.app, metrics_dir=metrics_dir_guess, refresh_interval=self.config['refresh_interval'])
            self.tabs['performance'] = perf_tab
            print(f"✅ Performance Tab initialized (metrics_dir={metrics_dir_guess})")
        except Exception as e:
            print(f"❌ No se pudo inicializar Performance Tab: {e}")
            raise

        # Risk & Health Tab (usa mismo metrics dir e intenta risk dir base)
        try:
            risk_dir_guess = str(project_root / '04-DATA')
            rh_tab = create_risk_health_tab(
                app=self.app,
                metrics_dir=str(project_root / '04-DATA' / 'metrics'),
                risk_dir=risk_dir_guess,
                refresh_interval=self.config['refresh_interval'] * 2
            )
            self.tabs['risk_health'] = rh_tab
            print(f"✅ Risk & Health Tab initialized (risk_dir={risk_dir_guess})")
        except Exception as e:
            print(f"❌ No se pudo inicializar Risk & Health Tab: {e}")
            raise
        
        # Future tabs can be added here
        # self.tabs['fvg_analysis'] = create_fvg_tab(self.app)
        # self.tabs['smart_money'] = create_smart_money_tab(self.app)
        
    def _setup_layout(self):
        """Configurar layout principal del dashboard"""
        
        # Create tab options
        tab_options = []
        if 'order_blocks' in self.tabs:
            tab_options.append({
                'label': '🎯 Order Blocks',
                'value': 'order_blocks'
            })
        
        # Add placeholder tabs for future implementation
        tab_options.extend([
            {'label': '📊 FVG Analysis', 'value': 'fvg_analysis'},
            {'label': '💰 Smart Money', 'value': 'smart_money'},
            {'label': '⚡ Live Trading', 'value': 'live_trading'},
            {'label': '🛡️ Risk & Health', 'value': 'risk_health'},
            {'label': '📈 Performance', 'value': 'performance'}
        ])
        
        self.app.layout = html.Div([
            # Header Section
            html.Div([
                html.Div([
                    html.H1([
                        html.Span("🎯 ", className="header-icon"),
                        "ICT Engine v6.0 Enterprise"
                    ], className="main-title"),
                    html.Div([
                        html.Span("🔄 Live Dashboard", className="status-indicator"),
                        html.Span(id="global-status", className="status-value")
                    ], className="status-section")
                ], className="header-content"),
                
                html.Div([
                    html.Span("⏰ ", className="time-icon"),
                    html.Span(id="current-time", className="current-time")
                ], className="time-section")
            ], className="dashboard-header"),
            
            # Navigation Tabs
            html.Div([
                dcc.Tabs(
                    id="main-tabs",
                    value=self.config['default_tab'],
                    children=[
                        dcc.Tab(
                            label=tab['label'],
                            value=tab['value'],
                            className="custom-tab",
                            selected_className="custom-tab-selected"
                        ) for tab in tab_options
                    ],
                    className="main-tabs-container"
                )
            ], className="navigation-section"),
            
            # Tab Content
            html.Div(id="tab-content", className="tab-content-container"),
            
            # Global refresh interval
            dcc.Interval(
                id="global-interval",
                interval=1000,  # Update time every second
                n_intervals=0
            ),
            
            # Global data store
            dcc.Store(id="global-data-store")
            
        ], className="dashboard-container")
        
        # Register global callbacks
        self._register_global_callbacks()
    
    def _register_global_callbacks(self):
        """Registrar callbacks globales del dashboard"""
        
        # Tab content callback
        @self.app.callback(
            Output("tab-content", "children"),
            Input("main-tabs", "value")
        )
        def render_tab_content(active_tab):
            """Renderizar contenido de la pestaña activa"""
            if active_tab == 'order_blocks' and 'order_blocks' in self.tabs:
                return self.tabs['order_blocks'].create_layout()
            elif active_tab == 'fvg_analysis':
                return self._create_placeholder_tab("📊 FVG Analysis", 
                    "Fair Value Gaps analysis coming soon...")
            elif active_tab == 'smart_money':
                return self._create_placeholder_tab("💰 Smart Money", 
                    "Smart Money Concepts analysis coming soon...")
            elif active_tab == 'live_trading':
                return self._create_placeholder_tab("⚡ Live Trading", 
                    "Live trading interface coming soon...")
            elif active_tab == 'performance':
                if 'performance' in self.tabs:
                    return self.tabs['performance'].create_layout()
                return self._create_placeholder_tab("📈 Performance", 
                    "Performance metrics module not available...")
            elif active_tab == 'risk_health':
                if 'risk_health' in self.tabs:
                    return self.tabs['risk_health'].create_layout()
                return self._create_placeholder_tab("🛡️ Risk & Health", "Risk module not available...")
            else:
                return self._create_placeholder_tab("🚧 Under Construction", 
                    "This tab is being developed...")
        
        # Global time update callback
        @self.app.callback(
            [Output("current-time", "children"),
             Output("global-status", "children")],
            Input("global-interval", "n_intervals")
        )
        def update_global_info(n_intervals):
            """Actualizar información global"""
            current_time = time.strftime("%H:%M:%S")
            
            # Check system status
            status = "🟢 ACTIVE"
            if 'order_blocks' in self.tabs:
                status = "🟢 ACTIVE"
            else:
                status = "🟡 PARTIAL"
            
            return current_time, status
    
    def _create_placeholder_tab(self, title: str, message: str) -> Any:
        """Crear pestaña placeholder para futuras implementaciones"""
        return html.Div([
            html.Div([
                html.H2(title, className="placeholder-title"),
                html.P(message, className="placeholder-message"),
                html.Div([
                    html.Div("🔧", className="construction-icon"),
                    html.P("Esta funcionalidad será implementada próximamente", className="construction-text")
                ], className="construction-notice")
            ], className="placeholder-content")
        ], className="placeholder-tab")
    
    def add_custom_css(self):
        """Agregar CSS personalizado al dashboard"""
        css_content = """
        /* Global Dashboard Styles */
        .dashboard-container {
            background: #0e1117;
            color: #ffffff;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
        }
        
        .dashboard-header {
            background: linear-gradient(135deg, #1e2329 0%, #2d313b 100%);
            border-bottom: 2px solid #00ff88;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header-content {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .main-title {
            color: #ffffff;
            font-size: 28px;
            font-weight: 700;
            margin: 0;
            text-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        }
        
        .header-icon {
            color: #00ff88;
            margin-right: 10px;
        }
        
        .status-section {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-indicator {
            background: rgba(0, 255, 136, 0.1);
            color: #00ff88;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .status-value {
            color: #00ff88;
            font-weight: 600;
        }
        
        .time-section {
            display: flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.05);
            padding: 12px 20px;
            border-radius: 8px;
        }
        
        .time-icon {
            color: #00ff88;
            font-size: 16px;
        }
        
        .current-time {
            color: #ffffff;
            font-family: 'Courier New', monospace;
            font-size: 16px;
            font-weight: 600;
        }
        
        .navigation-section {
            background: #1e2329;
            padding: 0 20px;
            border-bottom: 1px solid #3a3d45;
        }
        
        .main-tabs-container .tab {
            background: transparent !important;
            color: #8a8e96 !important;
            border: none !important;
            border-bottom: 3px solid transparent !important;
            padding: 15px 25px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .main-tabs-container .tab:hover {
            color: #00ff88 !important;
            background: rgba(0, 255, 136, 0.05) !important;
        }
        
        .main-tabs-container .tab--selected {
            color: #00ff88 !important;
            border-bottom-color: #00ff88 !important;
            background: rgba(0, 255, 136, 0.1) !important;
        }
        
        .tab-content-container {
            flex: 1;
            padding: 0;
        }
        
        .placeholder-tab {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 60vh;
        }
        
        .placeholder-content {
            text-align: center;
            max-width: 500px;
            padding: 40px;
            background: linear-gradient(135deg, #1e2329 0%, #252832 100%);
            border-radius: 20px;
            border: 1px solid #3a3d45;
        }
        
        .placeholder-title {
            color: #ffffff;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 15px;
        }
        
        .placeholder-message {
            color: #8a8e96;
            font-size: 16px;
            margin-bottom: 30px;
        }
        
        .construction-notice {
            background: rgba(255, 170, 0, 0.1);
            border: 1px solid rgba(255, 170, 0, 0.3);
            border-radius: 12px;
            padding: 20px;
        }
        
        .construction-icon {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .construction-text {
            color: #ffaa00;
            font-size: 14px;
            margin: 0;
            font-weight: 500;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .dashboard-header {
                flex-direction: column;
                gap: 15px;
            }
            
            .main-title {
                font-size: 20px;
            }
            
            .main-tabs-container .tab {
                padding: 12px 15px !important;
                font-size: 14px !important;
            }
        }
        """
        
        return css_content
    
    def run(self, **kwargs):
        """
        🚀 EJECUTAR DASHBOARD WEB
        ========================
        
        Args:
            **kwargs: Argumentos adicionales para app.run_server()
        """
        # Merge default config with provided kwargs
        run_config = {
            'host': self.config['host'],
            'port': self.config['port'],
            'debug': self.config['debug'],
            'use_reloader': False,  # Disable reloader to avoid issues
            'threaded': True
        }
        run_config.update(kwargs)
        
        # Add custom CSS
        custom_css = self.add_custom_css()
        self.app.index_string = f'''
        <!DOCTYPE html>
        <html>
            <head>
                {{%metas%}}
                <title>{{%title%}}</title>
                {{%favicon%}}
                {{%css%}}
                <style>
                {custom_css}
                </style>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
                {{%app_entry%}}
                <footer>
                    {{%config%}}
                    {{%scripts%}}
                    {{%renderer%}}
                </footer>
            </body>
        </html>
        '''
        
        try:
            print(f"🚀 Starting ICT Web Dashboard...")
            print(f"   URL: http://{run_config['host']}:{run_config['port']}")
            print(f"   Debug mode: {run_config['debug']}")
            print(f"   Available tabs: {list(self.tabs.keys())}")
            print(f"✅ Dashboard ready!")
            
            self.app.run(**run_config)
            
        except KeyboardInterrupt:
            print("\n⏹️ Dashboard stopped by user")
        except Exception as e:
            print(f"❌ Error running dashboard: {e}")
            raise


def create_web_dashboard(config: Optional[Dict[str, Any]] = None) -> ICTWebDashboard:
    """
    🏭 FACTORY FUNCTION PARA WEB DASHBOARD
    ====================================
    
    Args:
        config: Configuración personalizada
        
    Returns:
        Instancia configurada de ICTWebDashboard
    """
    return ICTWebDashboard(config)


def main():
    """Función principal para ejecutar el dashboard"""
    # Configuración personalizada
    config = {
        'refresh_interval': 500,  # 0.5 seconds
        'host': '127.0.0.1',
        'port': 8050,
        'debug': True,
        'default_tab': 'order_blocks'
    }
    
    try:
        # Crear y ejecutar dashboard
        dashboard = create_web_dashboard(config)
        dashboard.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed:")
        print("   pip install dash plotly pandas")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()