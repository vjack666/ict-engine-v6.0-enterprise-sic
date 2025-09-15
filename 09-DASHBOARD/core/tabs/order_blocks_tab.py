#!/usr/bin/env python3
"""ORDER BLOCKS TAB - REAL SYSTEMS ONLY

Optimizado: Usa servicio cacheado para detección no-HF.

Refactor: Usa stubs centralizados en ``core.stubs.dash_stubs`` para
evitar lógica duplicada e inline *type: ignore* al importar Dash.
"""

from datetime import datetime
from typing import Dict, Any, List
import json

from core.stubs.dash_stubs import dash_safe_imports

html, dcc, Input, Output, State, DASHBOARD_AVAILABLE = dash_safe_imports()


try:
    from smart_trading_logger import SmartTradingLogger  # root-level import
except Exception:  # pragma: no cover
    SmartTradingLogger = None  # type: ignore

try:
    from core.order_blocks_service import OrderBlocksRealtimeService  # type: ignore
except Exception:  # pragma: no cover
    OrderBlocksRealtimeService = None  # type: ignore

class RealOrderBlocksTab:
    def __init__(self, app=None, refresh_interval: int = 2500, ttl_seconds: int = 12, **_):
        self.app = app
        self.refresh_interval = refresh_interval
        self.symbols: List[str] = ["EURUSD", "GBPUSD", "USDJPY"]
        self.timeframes: List[str] = ["M5", "M15", "H1", "H4"]
        self.logger = SmartTradingLogger("OrderBlocksTab") if SmartTradingLogger else None
        self._service: Any = None
        self._ttl_seconds = ttl_seconds

    def create_layout(self):
        if not DASHBOARD_AVAILABLE:
            return {"error": "Dashboard not available"}
        controls = html.Div([
            html.Div([
                html.Label("Símbolo"),
                dcc.Dropdown(id="ob-symbol", options=[{"label": s, "value": s} for s in self.symbols], value=self.symbols[0], clearable=False)
            ], className="ob-control"),
            html.Div([
                html.Label("Timeframe"),
                dcc.Dropdown(id="ob-timeframe", options=[{"label": t, "value": t} for t in self.timeframes], value=self.timeframes[1], clearable=False)
            ], className="ob-control"),
            html.Button("🔄 Forzar Refresh", id="ob-force-refresh", n_clicks=0, className="ob-refresh-btn"),
            dcc.Interval(id="ob-interval", interval=self.refresh_interval, n_intervals=0),
            dcc.Store(id="ob-metrics-store"),
            dcc.Store(id="ob-dyn-state", data={"current_interval": self.refresh_interval, "cache_streak": 0, "calc_streak": 0})
        ], className="ob-controls")

        data_section = html.Div([
            html.H3("Order Blocks Activos"),
            html.Div(id="ob-last-update", className="ob-last-update"),
            html.Pre(id="ob-data", children="(Sin datos aún)", className="ob-data-view"),
            html.Div(id="ob-meta", className="ob-meta"),
            html.Div(id="ob-metrics-panel", className="ob-metrics-panel"),
            html.Div([
                html.Div([
                    html.H4("Tabla"),
                    html.Div(id="ob-table" , className="ob-table-container")
                ], className="ob-table-wrapper"),
                html.Div([
                    html.H4("Distribución"),
                    dcc.Graph(id="ob-graph", figure={'data': [], 'layout': {'template': 'plotly_dark', 'height': 300}})
                ], className="ob-graph-wrapper")
            ], className="ob-viz-grid")
        ], className="ob-data-section")

        return html.Div([
            html.H2("Order Blocks - Real Systems"),
            html.P("Detección real de Order Blocks (sin mocks)"),
            controls,
            data_section
        ], className="order-blocks-tab")
    
    def _get_service(self):
        if self._service is None:
            if OrderBlocksRealtimeService is None:
                raise RuntimeError("OrderBlocksRealtimeService no disponible")
            self._service = OrderBlocksRealtimeService(ttl_seconds=self._ttl_seconds)
            if self.logger:
                self.logger.info("Servicio OrderBlocksRealtimeService inicializado", "order_blocks_tab")
        return self._service

    def fetch_real_order_blocks_data(self, symbol: str, timeframe: str, force: bool = False) -> Dict[str, Any]:
        try:
            svc = self._get_service()
            return svc.get_order_blocks(symbol, timeframe, force=force)
        except Exception as e:  # pragma: no cover
            if self.logger:
                self.logger.error(f"Error obteniendo datos OB: {e}", "order_blocks_tab")
            return {"error": str(e), "symbol": symbol, "timeframe": timeframe, "order_blocks": [], "last_update": datetime.now().isoformat()}

    def register_callbacks(self, app):  # noqa: C901 (simple enough)
        if not DASHBOARD_AVAILABLE:
            return

        @app.callback(
            Output("ob-data", "children"),
            Output("ob-last-update", "children"),
            Output("ob-meta", "children"),
            Output("ob-metrics-store", "data"),
            Output("ob-metrics-panel", "children"),
            Output("ob-interval", "interval"),
            Output("ob-dyn-state", "data"),
            Output("ob-table", "children"),
            Output("ob-graph", "figure"),
            Input("ob-interval", "n_intervals"),
            Input("ob-symbol", "value"),
            Input("ob-timeframe", "value"),
            Input("ob-force-refresh", "n_clicks"),
            State("ob-metrics-store", "data"),
            State("ob-dyn-state", "data")
        )
        def _update_ob_data(_, symbol, timeframe, force_clicks, metrics_state, dyn_state):  # pylint: disable=unused-argument
            force = bool(force_clicks and force_clicks > 0)
            payload = self.fetch_real_order_blocks_data(symbol, timeframe, force=force)
            service_metrics = {}
            try:
                if self._service:
                    service_metrics = self._service.get_metrics()
            except Exception:  # pragma: no cover
                pass
            # Dynamic interval logic
            dyn_state = dyn_state or {"current_interval": self.refresh_interval, "cache_streak": 0, "calc_streak": 0}
            cur_interval = dyn_state.get("current_interval", self.refresh_interval)
            cache_streak = dyn_state.get("cache_streak", 0)
            calc_streak = dyn_state.get("calc_streak", 0)
            source = payload.get("source")
            changed = False
            if source == "CACHE":
                cache_streak += 1
                calc_streak = 0
                if cache_streak >= 3 and cur_interval < 6000:
                    cur_interval = min(6000, cur_interval + 1000)
                    cache_streak = 0
                    changed = True
            elif source == "CALC":
                calc_streak += 1
                cache_streak = 0
                if calc_streak >= 2 and cur_interval > 1500:
                    cur_interval = max(1500, cur_interval - 500)
                    calc_streak = 0
                    changed = True
            dyn_state = {"current_interval": cur_interval, "cache_streak": cache_streak, "calc_streak": calc_streak}

            def render_metrics(m: Dict[str, Any]):
                if not m:
                    return html.Div("(Sin métricas)", className="ob-metrics-empty")
                # Calcular hit ratio
                total_access = m.get('hits',0) + m.get('misses',0)
                hit_ratio = (m.get('hits',0) / total_access * 100) if total_access else 0
                latency = round(m.get('avg_latency_ms',0),1)
                classes = ["latency-good" if latency < 150 else ("latency-warn" if latency < 400 else "latency-bad")]
                return html.Div([
                    html.Div([
                        html.Span("Hits"), html.Strong(m.get('hits',0))
                    ], className="metric"),
                    html.Div([
                        html.Span("Misses"), html.Strong(m.get('misses',0))
                    ], className="metric"),
                    html.Div([
                        html.Span("Hit%"), html.Strong(f"{hit_ratio:.1f}%")
                    ], className="metric"),
                    html.Div([
                        html.Span("Avg Lat"), html.Strong(f"{latency} ms", className=" ".join(classes))
                    ], className="metric"),
                    html.Div([
                        html.Span("Cache"), html.Strong(m.get('cache_size','-'))
                    ], className="metric"),
                    html.Div([
                        html.Span("Hist"), html.Strong(m.get('history_len','-'))
                    ], className="metric"),
                ], className="metrics-grid")
            if "error" in payload:
                return (
                    f"ERROR: {payload['error']}",
                    f"❌ {payload.get('last_update','')}",
                    f"Fuente: ERROR | CacheSize: {service_metrics.get('cache_size','-')}",
                    service_metrics,
                    render_metrics(service_metrics),
                    cur_interval,
                    dyn_state,
                    html.Div("Error cargando datos", className="ob-table-error"),
                    {'data': [], 'layout': {'template': 'plotly_dark', 'height': 300, 'title': 'Sin datos'}}
                )
            lines = [
                f"Símbolo: {payload.get('symbol')}",
                f"Timeframe: {payload.get('timeframe')}",
                f"OrderBlocks: {payload.get('count', len(payload.get('order_blocks', [])))}"
            ]
            meta = f"Fuente: {payload.get('source')} | Latencia: {round(payload.get('latency_ms',0),1)}ms | TTL: {self._ttl_seconds}s | CacheSize: {service_metrics.get('cache_size','-')}"
            # Tabla simple (sin DataTable para reducir dependencias)
            rows = []
            header = html.Tr([html.Th("ID"), html.Th("Tipo"), html.Th("Precio"), html.Th("Conf")])
            for ob in payload.get('order_blocks', [])[:50]:
                rows.append(html.Tr([
                    html.Td(ob.get('id')),
                    html.Td(ob.get('type')),
                    html.Td(ob.get('price')),
                    html.Td(round(ob.get('confidence',0),3))
                ]))
            table_component = html.Table([header] + rows, className="ob-table") if rows else html.Div("(Sin bloques)", className="ob-table-empty")

            # Gráfico: puntos en eje Y por índice, X = precio (si hay)
            prices = [ob.get('price') for ob in payload.get('order_blocks', []) if ob.get('price') is not None]
            types = [ob.get('type') for ob in payload.get('order_blocks', []) if ob.get('price') is not None]
            figure = {
                'data': [{
                    'type': 'scattergl',
                    'x': prices,
                    'y': list(range(len(prices))),
                    'mode': 'markers',
                    'marker': {'color': ['#2ecc71' if 'bull' in (t or '').lower() else '#e74c3c' for t in types]},
                    'text': types,
                    'name': 'OrderBlocks'
                }],
                'layout': {
                    'template': 'plotly_dark',
                    'height': 300,
                    'title': f"Distribución Precios ({len(prices)})",
                    'xaxis': {'title': 'Precio'},
                    'yaxis': {'title': 'Idx', 'showticklabels': False},
                    'margin': {'l': 40, 'r': 10, 't': 40, 'b': 40}
                }
            }

            meta = meta + f" | Intervalo: {cur_interval}ms"
            return "\n".join(lines), f"✅ Última actualización: {payload.get('last_update','')}" , meta, service_metrics, render_metrics(service_metrics), cur_interval, dyn_state, table_component, figure

def create_real_order_blocks_tab(app=None, **kwargs):
    return RealOrderBlocksTab(app=app, **kwargs)

OrderBlocksTab = RealOrderBlocksTab
create_order_blocks_tab = create_real_order_blocks_tab

__all__ = ["RealOrderBlocksTab", "create_real_order_blocks_tab", "OrderBlocksTab", "create_order_blocks_tab"]
