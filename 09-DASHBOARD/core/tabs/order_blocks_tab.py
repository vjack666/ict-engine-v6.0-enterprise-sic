#!/usr/bin/env python3
"""
🎯 ORDER BLOCKS TAB v6.0 ENTERPRISE - DASHBOARD INTEGRATION
==========================================================

Pestaña especializada para visualización en tiempo real de Order Blocks.
Integra con OrderBlocksBlackBox logging y SmartMoneyAnalyzer detection.

Funcionalidades:
✅ Detección en tiempo real de Order Blocks
✅ Visualización interactiva con gráficos
✅ Métricas de performance y estadísticas
✅ Filtros por tipo (Bullish/Bearish) y confidence
✅ Integración completa con logging system
✅ Auto-refresh cada 0.5 segundos

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 12 Septiembre 2025
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import time

# Dashboard framework imports
try:
    import dash
    from dash import dcc, html, Input, Output, State, callback, ctx
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import pandas as pd
    DASH_AVAILABLE = True
except ImportError:
    print("⚠️ Dash not available - OrderBlocksTab will use fallback mode")
    DASH_AVAILABLE = False
    dash = None
    dcc = html = Input = Output = State = callback = ctx = None
    go = px = make_subplots = pd = None

# Core system imports with fallbacks
try:
    import sys
    import os
    # Add paths for imports
    current_dir = Path(__file__).parent.parent.parent.parent / "01-CORE"
    sys.path.insert(0, str(current_dir))
    
    from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
    from order_blocks_logging.order_blocks_black_box import OrderBlocksBlackBox
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Core systems not available: {e}")
    CORE_AVAILABLE = False
    SmartMoneyAnalyzer = None
    OrderBlocksBlackBox = None


class OrderBlocksTab:
    """
    🎯 PESTAÑA ORDER BLOCKS v6.0 ENTERPRISE
    =====================================
    
    Componente principal para la visualización de Order Blocks en tiempo real.
    Integra detección, logging y visualización en una interfaz interactiva.
    """
    
    def __init__(self, app=None, refresh_interval: int = 500):
        self.app = app
        self.refresh_interval = refresh_interval  # ms
        
        # Core components
        if CORE_AVAILABLE:
            self.analyzer = SmartMoneyAnalyzer()
            self.logger = OrderBlocksBlackBox()
        else:
            self.analyzer = None
            self.logger = None
            
        # Data storage
        self.current_data = {
            'order_blocks': [],
            'last_update': datetime.now().isoformat(),
            'metrics': {
                'total_blocks': 0,
                'bullish_blocks': 0,
                'bearish_blocks': 0,
                'avg_confidence': 0.0
            }
        }
        
        # Visual configuration
        self.colors = {
            'bullish': '#00ff88',
            'bearish': '#ff4444',
            'background': '#0e1117',
            'surface': '#1e2329',
            'text': '#ffffff'
        }
        
        print(f"🎯 OrderBlocksTab initialized (refresh: {refresh_interval}ms)")
        
    def create_layout(self) -> html.Div:
        """
        🎨 CREAR LAYOUT PRINCIPAL
        ========================
        
        Returns:
            Layout principal de la pestaña Order Blocks
        """
        if not DASH_AVAILABLE:
            return html.Div([
                html.H3("⚠️ Order Blocks Tab - Dash no disponible"),
                html.P("Instalar dash y plotly para habilitar esta funcionalidad")
            ])
            
        return html.Div([
            # Header Section
            html.Div([
                html.H2("🎯 Order Blocks Detection v6.0", 
                       className="tab-title"),
                html.Div([
                    html.Span("🔄 Auto-refresh: ", className="status-label"),
                    html.Span(f"{self.refresh_interval}ms", className="status-value"),
                    html.Span(" | ⏰ Last Update: ", className="status-label"),
                    html.Span(id="ob-last-update", className="status-value")
                ], className="status-bar")
            ], className="tab-header"),
            
            # Controls Section
            html.Div([
                html.Div([
                    html.Label("Symbol:", className="control-label"),
                    dcc.Dropdown(
                        id="ob-symbol-selector",
                        options=[
                            {"label": "EURUSD", "value": "EURUSD"},
                            {"label": "GBPUSD", "value": "GBPUSD"},
                            {"label": "USDJPY", "value": "USDJPY"},
                            {"label": "AUDUSD", "value": "AUDUSD"}
                        ],
                        value="EURUSD",
                        className="control-dropdown"
                    )
                ], className="control-group"),
                
                html.Div([
                    html.Label("Timeframe:", className="control-label"),
                    dcc.Dropdown(
                        id="ob-timeframe-selector",
                        options=[
                            {"label": "M1", "value": "M1"},
                            {"label": "M5", "value": "M5"},
                            {"label": "M15", "value": "M15"},
                            {"label": "M30", "value": "M30"},
                            {"label": "H1", "value": "H1"}
                        ],
                        value="M15",
                        className="control-dropdown"
                    )
                ], className="control-group"),
                
                html.Div([
                    html.Label("Min Confidence:", className="control-label"),
                    dcc.Slider(
                        id="ob-confidence-slider",
                        min=0.0,
                        max=1.0,
                        step=0.1,
                        value=0.5,
                        marks={i/10: f"{i/10:.1f}" for i in range(0, 11, 2)},
                        className="control-slider"
                    )
                ], className="control-group"),
                
                html.Button("🔄 Refresh Now", 
                           id="ob-manual-refresh",
                           className="refresh-button")
            ], className="controls-section"),
            
            # Metrics Cards Section
            html.Div([
                # Total Blocks Card
                html.Div([
                    html.Div([
                        html.H3(id="ob-total-count", children="0"),
                        html.P("Total Order Blocks", className="metric-label")
                    ], className="metric-content"),
                    html.Div("📦", className="metric-icon")
                ], className="metric-card metric-total"),
                
                # Bullish Blocks Card
                html.Div([
                    html.Div([
                        html.H3(id="ob-bullish-count", children="0"),
                        html.P("Bullish Blocks", className="metric-label")
                    ], className="metric-content"),
                    html.Div("📈", className="metric-icon bullish")
                ], className="metric-card metric-bullish"),
                
                # Bearish Blocks Card
                html.Div([
                    html.Div([
                        html.H3(id="ob-bearish-count", children="0"),
                        html.P("Bearish Blocks", className="metric-label")
                    ], className="metric-content"),
                    html.Div("📉", className="metric-icon bearish")
                ], className="metric-card metric-bearish"),
                
                # Average Confidence Card
                html.Div([
                    html.Div([
                        html.H3(id="ob-avg-confidence", children="0.0%"),
                        html.P("Avg Confidence", className="metric-label")
                    ], className="metric-content"),
                    html.Div("🎯", className="metric-icon")
                ], className="metric-card metric-confidence")
            ], className="metrics-grid"),
            
            # Chart Section
            html.Div([
                dcc.Graph(
                    id="ob-main-chart",
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
                    }
                )
            ], className="chart-section"),
            
            # Order Blocks Table Section
            html.Div([
                html.H3("📋 Detected Order Blocks", className="section-title"),
                html.Div(id="ob-blocks-table", className="blocks-table")
            ], className="table-section"),
            
            # Auto-refresh Component
            dcc.Interval(
                id="ob-refresh-interval",
                interval=self.refresh_interval,
                n_intervals=0
            ),
            
            # Data Store
            dcc.Store(id="ob-data-store", data=self.current_data)
            
        ], className="order-blocks-tab")
    
    def fetch_order_blocks_data(self, symbol: str = "EURUSD", 
                               timeframe: str = "M15") -> Dict[str, Any]:
        """
        🔍 OBTENER DATOS DE ORDER BLOCKS
        ===============================
        
        Args:
            symbol: Par de divisas
            timeframe: Marco temporal
            
        Returns:
            Datos estructurados de Order Blocks detectados
        """
        if not CORE_AVAILABLE or not self.analyzer:
            # Mock data for fallback
            return {
                'order_blocks': [],
                'last_update': datetime.now().isoformat(),
                'metrics': {
                    'total_blocks': 0,
                    'bullish_blocks': 0,
                    'bearish_blocks': 0,
                    'avg_confidence': 0.0
                },
                'error': 'Core systems not available'
            }
        
        try:
            # 🎯 DETECCIÓN USANDO SMARTMONEYANALYZER
            start_time = time.time()
            order_blocks = self.analyzer.find_order_blocks(symbol, timeframe)
            detection_time = (time.time() - start_time) * 1000
            
            # 📊 CALCULAR MÉTRICAS
            bullish_blocks = [ob for ob in order_blocks if 'bullish' in ob.get('type', '').lower()]
            bearish_blocks = [ob for ob in order_blocks if 'bearish' in ob.get('type', '').lower()]
            
            avg_confidence = 0.0
            if order_blocks:
                total_confidence = sum(ob.get('confidence', 0) for ob in order_blocks)
                avg_confidence = total_confidence / len(order_blocks)
            
            # 🎯 CAJA NEGRA - Log dashboard update
            if self.logger:
                dashboard_data = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'blocks_detected': len(order_blocks),
                    'detection_time_ms': detection_time
                }
                self.logger.log_dashboard_update(
                    "OrderBlocksTab", "data_fetch", dashboard_data, success=True
                )
            
            return {
                'order_blocks': order_blocks,
                'last_update': datetime.now().isoformat(),
                'metrics': {
                    'total_blocks': len(order_blocks),
                    'bullish_blocks': len(bullish_blocks),
                    'bearish_blocks': len(bearish_blocks),
                    'avg_confidence': avg_confidence
                },
                'performance': {
                    'detection_time_ms': detection_time,
                    'symbol': symbol,
                    'timeframe': timeframe
                }
            }
            
        except Exception as e:
            # 🎯 CAJA NEGRA - Log error
            if self.logger:
                self.logger.log_error("OrderBlocksTab", "fetch_data", e, 
                                    {'symbol': symbol, 'timeframe': timeframe})
            
            print(f"❌ Error fetching Order Blocks: {e}")
            return {
                'order_blocks': [],
                'last_update': datetime.now().isoformat(),
                'metrics': {
                    'total_blocks': 0,
                    'bullish_blocks': 0,
                    'bearish_blocks': 0,
                    'avg_confidence': 0.0
                },
                'error': str(e)
            }
    
    def create_order_blocks_chart(self, data: Dict[str, Any], 
                                 min_confidence: float = 0.5) -> go.Figure:
        """
        📊 CREAR GRÁFICO DE ORDER BLOCKS
        ===============================
        
        Args:
            data: Datos de Order Blocks
            min_confidence: Confidence mínima para mostrar
            
        Returns:
            Gráfico de Plotly con Order Blocks visualizados
        """
        if not DASH_AVAILABLE:
            return None
            
        # Filtrar por confidence
        order_blocks = data.get('order_blocks', [])
        filtered_blocks = [
            ob for ob in order_blocks 
            if ob.get('confidence', 0) >= min_confidence
        ]
        
        fig = go.Figure()
        
        if filtered_blocks:
            # Separar bullish y bearish blocks
            bullish_blocks = [ob for ob in filtered_blocks if 'bullish' in ob.get('type', '').lower()]
            bearish_blocks = [ob for ob in filtered_blocks if 'bearish' in ob.get('type', '').lower()]
            
            # Add Bullish Order Blocks
            if bullish_blocks:
                bullish_prices = [ob.get('price', 0) for ob in bullish_blocks]
                bullish_confidences = [ob.get('confidence', 0) for ob in bullish_blocks]
                
                fig.add_trace(go.Scatter(
                    y=bullish_prices,
                    x=list(range(len(bullish_prices))),
                    mode='markers',
                    marker=dict(
                        color=self.colors['bullish'],
                        size=[conf * 30 + 5 for conf in bullish_confidences],
                        symbol='triangle-up',
                        line=dict(width=2, color='white')
                    ),
                    name='Bullish Order Blocks',
                    text=[f"Price: {price:.5f}<br>Confidence: {conf:.2%}" 
                          for price, conf in zip(bullish_prices, bullish_confidences)],
                    hovertemplate='<b>%{text}</b><extra></extra>'
                ))
            
            # Add Bearish Order Blocks
            if bearish_blocks:
                bearish_prices = [ob.get('price', 0) for ob in bearish_blocks]
                bearish_confidences = [ob.get('confidence', 0) for ob in bearish_blocks]
                
                fig.add_trace(go.Scatter(
                    y=bearish_prices,
                    x=list(range(len(bearish_prices))),
                    mode='markers',
                    marker=dict(
                        color=self.colors['bearish'],
                        size=[conf * 30 + 5 for conf in bearish_confidences],
                        symbol='triangle-down',
                        line=dict(width=2, color='white')
                    ),
                    name='Bearish Order Blocks',
                    text=[f"Price: {price:.5f}<br>Confidence: {conf:.2%}" 
                          for price, conf in zip(bearish_prices, bearish_confidences)],
                    hovertemplate='<b>%{text}</b><extra></extra>'
                ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"🎯 Order Blocks Detection - {data.get('performance', {}).get('symbol', 'EURUSD')} {data.get('performance', {}).get('timeframe', 'M15')}",
                x=0.5,
                font=dict(color=self.colors['text'], size=18)
            ),
            xaxis=dict(
                title="Block Index",
                gridcolor='rgba(255,255,255,0.1)',
                color=self.colors['text']
            ),
            yaxis=dict(
                title="Price Level",
                gridcolor='rgba(255,255,255,0.1)',
                color=self.colors['text']
            ),
            plot_bgcolor=self.colors['background'],
            paper_bgcolor=self.colors['background'],
            font=dict(color=self.colors['text']),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=400
        )
        
        return fig
    
    def create_blocks_table(self, data: Dict[str, Any], 
                           min_confidence: float = 0.5) -> html.Div:
        """
        📋 CREAR TABLA DE ORDER BLOCKS
        =============================
        
        Args:
            data: Datos de Order Blocks
            min_confidence: Confidence mínima para mostrar
            
        Returns:
            Componente HTML con tabla de Order Blocks
        """
        order_blocks = data.get('order_blocks', [])
        filtered_blocks = [
            ob for ob in order_blocks 
            if ob.get('confidence', 0) >= min_confidence
        ]
        
        if not filtered_blocks:
            return html.Div([
                html.P("📭 No Order Blocks detected with the current filters", 
                      className="no-data-message")
            ])
        
        # Sort by confidence (highest first)
        sorted_blocks = sorted(
            filtered_blocks, 
            key=lambda x: x.get('confidence', 0), 
            reverse=True
        )
        
        table_rows = []
        for i, ob in enumerate(sorted_blocks[:10]):  # Show top 10
            block_type = ob.get('type', 'UNKNOWN')
            is_bullish = 'bullish' in block_type.lower()
            
            row = html.Tr([
                html.Td(f"{i+1}", className="table-cell"),
                html.Td(
                    html.Span(
                        "📈" if is_bullish else "📉",
                        className=f"type-indicator {'bullish' if is_bullish else 'bearish'}"
                    ),
                    className="table-cell"
                ),
                html.Td(f"{ob.get('price', 0):.5f}", className="table-cell price-cell"),
                html.Td(f"{ob.get('confidence', 0):.2%}", className="table-cell confidence-cell"),
                html.Td(f"{ob.get('volume', 0):,}", className="table-cell volume-cell"),
                html.Td(
                    f"{ob.get('range_high', 0):.5f} - {ob.get('range_low', 0):.5f}",
                    className="table-cell range-cell"
                )
            ], className="table-row")
            
            table_rows.append(row)
        
        return html.Div([
            html.Table([
                html.Thead([
                    html.Tr([
                        html.Th("#", className="table-header"),
                        html.Th("Type", className="table-header"),
                        html.Th("Price", className="table-header"),
                        html.Th("Confidence", className="table-header"),
                        html.Th("Volume", className="table-header"),
                        html.Th("Range", className="table-header")
                    ])
                ]),
                html.Tbody(table_rows)
            ], className="blocks-table-content")
        ])
    
    def register_callbacks(self):
        """
        🔄 REGISTRAR CALLBACKS DE DASH
        =============================
        
        Registra todos los callbacks necesarios para la interactividad
        """
        if not DASH_AVAILABLE or not self.app:
            return
        
        # Main data update callback
        @self.app.callback(
            [Output("ob-data-store", "data"),
             Output("ob-last-update", "children")],
            [Input("ob-refresh-interval", "n_intervals"),
             Input("ob-manual-refresh", "n_clicks"),
             Input("ob-symbol-selector", "value"),
             Input("ob-timeframe-selector", "value")],
            prevent_initial_call=False
        )
        def update_order_blocks_data(n_intervals, refresh_clicks, symbol, timeframe):
            """Update Order Blocks data from SmartMoneyAnalyzer"""
            data = self.fetch_order_blocks_data(symbol, timeframe)
            last_update = datetime.now().strftime("%H:%M:%S")
            return data, last_update
        
        # Metrics cards update callback
        @self.app.callback(
            [Output("ob-total-count", "children"),
             Output("ob-bullish-count", "children"),
             Output("ob-bearish-count", "children"),
             Output("ob-avg-confidence", "children")],
            [Input("ob-data-store", "data")]
        )
        def update_metrics_cards(data):
            """Update metrics cards with current data"""
            metrics = data.get('metrics', {})
            return (
                str(metrics.get('total_blocks', 0)),
                str(metrics.get('bullish_blocks', 0)),
                str(metrics.get('bearish_blocks', 0)),
                f"{metrics.get('avg_confidence', 0):.1%}"
            )
        
        # Chart update callback
        @self.app.callback(
            Output("ob-main-chart", "figure"),
            [Input("ob-data-store", "data"),
             Input("ob-confidence-slider", "value")]
        )
        def update_chart(data, min_confidence):
            """Update main Order Blocks chart"""
            return self.create_order_blocks_chart(data, min_confidence)
        
        # Table update callback
        @self.app.callback(
            Output("ob-blocks-table", "children"),
            [Input("ob-data-store", "data"),
             Input("ob-confidence-slider", "value")]
        )
        def update_blocks_table(data, min_confidence):
            """Update Order Blocks table"""
            return self.create_blocks_table(data, min_confidence)
        
        print("🔄 OrderBlocksTab callbacks registered successfully")


def create_order_blocks_tab(app=None, refresh_interval: int = 500) -> OrderBlocksTab:
    """
    🏭 FACTORY FUNCTION PARA ORDER BLOCKS TAB
    ========================================
    
    Args:
        app: Aplicación Dash
        refresh_interval: Intervalo de actualización en ms
        
    Returns:
        Instancia configurada de OrderBlocksTab
    """
    tab = OrderBlocksTab(app, refresh_interval)
    
    if app:
        tab.register_callbacks()
        
    return tab


# Testing and validation functions
def test_order_blocks_tab():
    """🧪 Test function para validar OrderBlocksTab"""
    print("🧪 Testing OrderBlocksTab...")
    
    try:
        tab = OrderBlocksTab()
        print("✅ OrderBlocksTab initialized")
        
        # Test data fetching
        data = tab.fetch_order_blocks_data("EURUSD", "M15")
        print(f"✅ Data fetched: {data['metrics']['total_blocks']} blocks")
        
        # Test layout creation
        if DASH_AVAILABLE:
            layout = tab.create_layout()
            print("✅ Layout created successfully")
        else:
            print("⚠️ Dash not available - layout test skipped")
        
        print("🎉 OrderBlocksTab test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ OrderBlocksTab test failed: {e}")
        return False


if __name__ == "__main__":
    test_order_blocks_tab()