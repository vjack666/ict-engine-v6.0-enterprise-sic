#!/usr/bin/env python3
"""
🛡️ RISK & HEALTH TAB - ICT ENGINE v6.0 ENTERPRISE
=================================================

Resumen rápido de estado de riesgo, salud del sistema, latencia y bloqueos de ejecución.
Fuente de datos:
- metrics_live.json / metrics_summary.json (ExecutionRouter)
- risk_guard snapshot (si existe archivo JSON con violaciones)
- heartbeat / health (placeholder extensible)
- slippage (stats dentro de metrics_live.json si presentes)

Diseñado como stub resiliente: funciona aun sin Dash instalado.
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional, List
import json
from typing import Any as _Any

# Intento importar dash/plotly reales
try:
    from dash import html, dcc, Input, Output  # type: ignore
    DASH_OK: bool = True
except Exception:  # fallback stub
    DASH_OK = False
    class _HtmlNS:
        def Div(self, *children: _Any, **props: _Any): return {"type":"Div","children":list(children),"props":props}
        def H2(self, *children: _Any, **props: _Any): return {"type":"H2","children":list(children),"props":props}
        def H3(self, *children: _Any, **props: _Any): return {"type":"H3","children":list(children),"props":props}
        def P(self, *children: _Any, **props: _Any): return {"type":"P","children":list(children),"props":props}
    class _DccNS:
        def Interval(self, *_, **props: _Any): return {"type":"Interval","props":props}
    def Input(*a, **k): return (a,k)  # type: ignore
    def Output(*a, **k): return (a,k)  # type: ignore
    html = _HtmlNS()  # type: ignore
    dcc = _DccNS()  # type: ignore

class RiskHealthTab:
    def __init__(self, app, metrics_dir: Optional[str], risk_dir: Optional[str] = None, refresh_interval: int = 2000):
        self.app = app
        self.metrics_dir = Path(metrics_dir) if metrics_dir else None
        self.risk_dir = Path(risk_dir) if risk_dir else None
        self.refresh_interval = refresh_interval
        if DASH_OK and app is not None:
            self._register_callbacks()

    # ------------ Lectura archivos -------------
    def _read_json(self, base: Optional[Path], filename: str) -> Dict[str, Any]:
        if not base: return {}
        path = base / filename
        if not path.exists():
            return {}
        try:
            with open(path,'r',encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _read_metrics_live(self):
        return self._read_json(self.metrics_dir, 'metrics_live.json')
    def _read_metrics_summary(self):
        return self._read_json(self.metrics_dir, 'metrics_summary.json')
    def _read_risk_snapshot(self):
        # Archivo opcional: risk_guard_status.json (extensible)
        return self._read_json(self.risk_dir, 'risk_guard_status.json')

    # ------------ Layout -------------
    def create_layout(self):
        if not DASH_OK:
            return {"error":"Dash not available","component":"RiskHealthTab","refresh_ms": self.refresh_interval}
        return html.Div([
            dcc.Interval(id='risk-health-interval', interval=self.refresh_interval, n_intervals=0),
            html.Div([
                html.H2("🛡️ Risk & System Health", className='risk-title'),
                html.Div(id='risk-health-kpis', className='risk-kpis'),
                html.Div(id='risk-health-violations', className='risk-violations'),
                html.Div(id='risk-health-updated', className='risk-updated'),
            ], className='risk-container')
        ], className='risk-wrapper')

    # ------------ KPIs rendering -------------
    def _render_kpis(self, live: Dict[str, Any], risk: Dict[str, Any]):
        def box(title: str, value: Any, subtitle: str = ""):
            return html.Div([
                html.Div(title, className='kpi-title'),
                html.Div(value, className='kpi-value'),
                html.Div(subtitle, className='kpi-subtitle')
            ], className='kpi-box')
        if not live:
            return html.Div("Esperando métricas...", className='kpi-empty')
        total = live.get('orders_total',0)
        ok = live.get('orders_ok',0)
        fail = live.get('orders_failed',0)
        fail_rate = (fail/total*100) if total else 0
        lat_avg = live.get('avg_latency_ms',0)
        slippage = (live.get('slippage') or {}) if isinstance(live.get('slippage'), dict) else {}
        slip_avg = slippage.get('avg',0.0)
        slip_p95 = slippage.get('p95',0.0)
        blocked = live.get('blocked_reasons') or {}
        return html.Div([
            box('Órdenes Totales', total),
            box('Fallos %', f"{fail_rate:.1f}%", f"Fail {fail}"),
            box('Latencia Avg', f"{lat_avg:.1f} ms"),
            box('Slippage Avg', f"{slip_avg:.2f}"),
            box('Slippage P95', f"{slip_p95:.2f}"),
            box('Bloqueos', sum(blocked.values()) if isinstance(blocked, dict) else 0)
        ], className='kpis-grid')

    def _render_violations(self, risk: Dict[str, Any]):
        violations = risk.get('violations') if risk else None
        if not violations:
            return html.Div("Sin violaciones de riesgo recientes", className='risk-ok')
        return html.Div([
            html.H3("Violaciones de Riesgo"),
            html.Div(", ".join(violations), className='risk-viol-list')
        ], className='risk-viol-box')

    # ------------ Callbacks -------------
    def _register_callbacks(self):
        if not DASH_OK:
            return
        @self.app.callback(  # type: ignore[attr-defined]
            [Output('risk-health-kpis','children'),
             Output('risk-health-violations','children'),
             Output('risk-health-updated','children')],
            Input('risk-health-interval','n_intervals')
        )
        def update_risk_health(_n):  # pragma: no cover
            live = self._read_metrics_live()
            risk = self._read_risk_snapshot()
            kpis = self._render_kpis(live, risk)
            viols = self._render_violations(risk)
            updated = f"Actualizado: {live.get('timestamp','-')}" if live else 'Sin datos'
            return kpis, viols, updated


def create_risk_health_tab(app, metrics_dir: Optional[str], risk_dir: Optional[str] = None, refresh_interval: int = 2000) -> RiskHealthTab:
    return RiskHealthTab(app, metrics_dir=metrics_dir, risk_dir=risk_dir, refresh_interval=refresh_interval)

__all__ = ['RiskHealthTab', 'create_risk_health_tab']
