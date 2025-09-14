#!/usr/bin/env python3
"""
📈 PERFORMANCE TAB - ICT ENGINE v6.0 ENTERPRISE
==============================================

Pestaña de métricas de ejecución: ordenes totales, éxito, fallo, latencias
(incluye percentiles) y mini-histórico.

Lee periódicamente los JSON generados por `ExecutionRouter`:
- metrics_live.json
- metrics_summary.json

Dependencias: dash, plotly, pandas (para formateo opcional)
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional
import json
import time

try:
    from dash import html, dcc, Input, Output
    import plotly.graph_objects as go
    DASH_OK = True
except Exception:
    DASH_OK = False
    html = dcc = Input = Output = None  # type: ignore
    go = None  # type: ignore


class PerformanceTab:
    def __init__(self, app, metrics_dir: Optional[str], refresh_interval: int = 1000):
        if not DASH_OK:
            raise ImportError("Dash no disponible para PerformanceTab")
        self.app = app
        self.metrics_dir = Path(metrics_dir) if metrics_dir else None
        self.refresh_interval = refresh_interval
        self._register_callbacks()

    # ------------- Helpers de lectura -----------------
    def _read_json(self, file_name: str) -> Dict[str, Any]:
        if not self.metrics_dir:
            return {}
        path = self.metrics_dir / file_name
        if not path.exists():
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _read_live(self):
        return self._read_json('metrics_live.json')

    def _read_summary(self):
        return self._read_json('metrics_summary.json')

    # ------------- Layout -----------------
    def create_layout(self):
        return html.Div([
            dcc.Interval(id='perf-metrics-interval', interval=self.refresh_interval, n_intervals=0),
            html.Div([
                html.H2("📈 Performance Metrics", className="perf-title"),
                html.Div(id='perf-kpis', className='perf-kpis'),
                html.Div([
                    dcc.Graph(id='perf-latency-chart', figure=self._empty_latency_fig(), className='perf-chart'),
                    dcc.Graph(id='perf-orders-chart', figure=self._empty_orders_fig(), className='perf-chart')
                ], className='perf-charts-row'),
                html.Div(id='perf-updated', className='perf-updated')
            ], className='perf-container')
        ], className='perf-wrapper')

    # ------------- Figures base -------------
    def _empty_latency_fig(self):
        fig = go.Figure()
        fig.update_layout(template='plotly_dark', height=300, margin=dict(l=40,r=20,t=40,b=40))
        fig.update_xaxes(title_text='Snapshot')
        fig.update_yaxes(title_text='Latency (ms)')
        return fig

    def _empty_orders_fig(self):
        fig = go.Figure()
        fig.update_layout(template='plotly_dark', height=300, margin=dict(l=40,r=20,t=40,b=40))
        fig.update_xaxes(title_text='Snapshot')
        fig.update_yaxes(title_text='Orders')
        return fig

    # ------------- Callbacks -------------
    def _register_callbacks(self):
        @self.app.callback(
            [Output('perf-kpis', 'children'),
             Output('perf-latency-chart', 'figure'),
             Output('perf-orders-chart', 'figure'),
             Output('perf-updated', 'children')],
            Input('perf-metrics-interval', 'n_intervals')
        )
        def update_perf(_n):  # pragma: no cover - UI callback
            live = self._read_live()
            summary = self._read_summary()
            history = summary.get('history', []) if summary else []

            # KPIs
            kpi_children = self._render_kpis(live, summary)
            latency_fig = self._build_latency_fig(history)
            orders_fig = self._build_orders_fig(history)
            updated = f"Last update: {live.get('timestamp','-')}" if live else 'No data yet'
            return kpi_children, latency_fig, orders_fig, updated

    def _render_kpis(self, live: Dict[str, Any], summary: Dict[str, Any]):
        def box(title: str, value: Any, subtitle: str = ""):
            return html.Div([
                html.Div(title, className='kpi-title'),
                html.Div(value, className='kpi-value'),
                html.Div(subtitle, className='kpi-subtitle')
            ], className='kpi-box')

        if not live:
            return html.Div("Waiting metrics...", className='kpi-empty')

        total = live.get('orders_total',0)
        ok = live.get('orders_ok',0)
        fail = live.get('orders_failed',0)
        avg_lat = live.get('avg_latency_ms',0)
        pct = live.get('latency_percentiles', {})
        fail_rate = (fail/total*100) if total else 0

        return html.Div([
            box('Total Orders', total),
            box('Success', ok, f"Rate {(ok/total*100):.1f}%" if total else "-"),
            box('Failed', fail, f"Rate {fail_rate:.1f}%"),
            box('Avg Latency', f"{avg_lat:.1f} ms"),
            box('P50/P90', f"{pct.get('p50',0):.0f}/{pct.get('p90',0):.0f} ms"),
            box('P95/P99', f"{pct.get('p95',0):.0f}/{pct.get('p99',0):.0f} ms")
        ], className='kpis-grid')

    def _build_latency_fig(self, history: list[dict]):
        fig = self._empty_latency_fig()
        if not history:
            return fig
        x = list(range(len(history)))
        lat = [h.get('lat',0) for h in history]
        fig.add_trace(go.Scatter(x=x, y=lat, mode='lines+markers', name='Avg Lat'))
        return fig

    def _build_orders_fig(self, history: list[dict]):
        fig = self._empty_orders_fig()
        if not history:
            return fig
        x = list(range(len(history)))
        total = [h.get('total',0) for h in history]
        ok = [h.get('ok',0) for h in history]
        fail = [h.get('fail',0) for h in history]
        fig.add_trace(go.Bar(x=x, y=total, name='Total', marker_color='#2b8') )
        fig.add_trace(go.Bar(x=x, y=ok, name='OK', marker_color='#0a5') )
        fig.add_trace(go.Bar(x=x, y=fail, name='Fail', marker_color='#c33') )
        fig.update_layout(barmode='group')
        return fig


def create_performance_tab(app, metrics_dir: Optional[str], refresh_interval: int = 1000) -> PerformanceTab:
    return PerformanceTab(app, metrics_dir=metrics_dir, refresh_interval=refresh_interval)

__all__ = [ 'PerformanceTab', 'create_performance_tab' ]
