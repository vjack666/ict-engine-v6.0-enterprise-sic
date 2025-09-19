#!/usr/bin/env python3
"""
🚀 METRICS API (FastAPI) - ICT ENGINE v6.0 ENTERPRISE
====================================================

Endpoints:
- GET /metrics/live
- GET /metrics/summary
- GET /metrics/cumulative
- GET /metrics/all  (agregado de los tres)

Uso rápido:
> uvicorn metrics_api:app --reload --port 8090

Lee los archivos JSON generados por ExecutionRouter. No mantiene estado en memoria
más allá de lecturas puntuales.
"""
from __future__ import annotations
try:
    from fastapi import FastAPI, HTTPException  # type: ignore
    from fastapi.responses import JSONResponse  # type: ignore
    FASTAPI_AVAILABLE = True
except ImportError:  # Fallback stubs so Pylance no marque errores si falta fastapi
    FASTAPI_AVAILABLE = False
    class HTTPException(Exception):  # type: ignore
        def __init__(self, status_code: int, detail: str):  # minimal shape
            self.status_code = status_code
            self.detail = detail
    class _StubJSONResponse(dict):  # simple container
        pass
    JSONResponse = _StubJSONResponse  # type: ignore
    class _StubApp:
        def __init__(self, *_, **__): ...
        def get(self, *_, **__):  # decorator stub
            def _wrap(fn): return fn
            return _wrap
    def FastAPI(*_, **__):  # type: ignore
        return _StubApp()
from pathlib import Path
from typing import Dict, Any, Protocol, runtime_checkable, cast, Optional
import json
import os
import sys

METRICS_DIR = Path(os.environ.get('ICT_METRICS_DIR', Path(__file__).parent.parent / '04-DATA' / 'metrics'))

app = FastAPI(title="ICT Engine Metrics API", version="1.0.0")


def _read_json(name: str) -> Dict[str, Any]:
    path = METRICS_DIR / name
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File {name} not found")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                # Support JSON-lines by reading the last non-empty line
                f.seek(0)
                lines = [ln.strip() for ln in f.readlines() if ln.strip()]
                if not lines:
                    return {}
                # Try parse last valid JSON object
                for ln in reversed(lines):
                    try:
                        return json.loads(ln)
                    except Exception:
                        continue
                return {}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading {name}: {e}")


@app.get('/metrics/live')
async def get_live():  # pragma: no cover - runtime
    return JSONResponse(_read_json('metrics_live.json'))


@app.get('/metrics/summary')
async def get_summary():  # pragma: no cover - runtime
    return JSONResponse(_read_json('metrics_summary.json'))


@app.get('/metrics/cumulative')
async def get_cumulative():  # pragma: no cover - runtime
    return JSONResponse(_read_json('metrics_cumulative.json'))


@app.get('/metrics/all')
async def get_all():  # pragma: no cover - runtime
    data = {}
    for name in ['metrics_live.json', 'metrics_summary.json', 'metrics_cumulative.json']:
        try:
            data[name.replace('.json','')] = _read_json(name)
        except HTTPException:
            data[name.replace('.json','')] = {'error': 'not_found'}
    return JSONResponse(data)


@app.get('/metrics/aggregator')
async def get_aggregator_metrics():  # pragma: no cover - runtime
    """📈 Obtener métricas del PerformanceMetricsAggregator en tiempo real"""
    try:
        # Import main to access performance_metrics instance
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        
        from main import get_performance_metrics_instance

        @runtime_checkable
        class _AggregatorLike(Protocol):
            def get_live_metrics(self) -> Dict[str, Any]: ...
            def get_summary_metrics(self) -> Dict[str, Any]: ...
            def get_cumulative_metrics(self) -> Dict[str, Any]: ...
            last_update: Any

        aggregator = cast(_AggregatorLike | None, get_performance_metrics_instance())
        if aggregator is None:
            raise HTTPException(status_code=503, detail="PerformanceMetricsAggregator not initialized")
            
        # Export current metrics from aggregator
        metrics_data = {
            'live_metrics': aggregator.get_live_metrics(),
            'summary_metrics': aggregator.get_summary_metrics(),
            'cumulative_metrics': aggregator.get_cumulative_metrics(),
            'timestamp': (aggregator.last_update.isoformat() if getattr(aggregator, 'last_update', None) else None)
        }
        
        return JSONResponse(metrics_data)
        
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"PerformanceMetricsAggregator not available: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting aggregator metrics: {e}")


@app.get('/dashboard/coordinator/state')
async def get_coordinator_state():  # pragma: no cover - runtime
    """📊 Obtener estado completo del TabCoordinator"""
    try:
        # Import here to avoid circular dependencies
        from core.tab_coordinator import get_coordinator_metrics
        
        metrics = get_coordinator_metrics()
        
        if "error" in metrics:
            raise HTTPException(status_code=503, detail=metrics["error"])
            
        return JSONResponse(metrics)
        
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"TabCoordinator not available: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting coordinator state: {e}")


@app.get('/dashboard/coordinator/export')  
async def get_coordinator_export():  # pragma: no cover - runtime
    """💾 Exportar estado completo del TabCoordinator"""
    try:
        from core.tab_coordinator import get_tab_coordinator
        
        coordinator = get_tab_coordinator()
        if coordinator is None:
            raise HTTPException(status_code=503, detail="TabCoordinator not initialized")
            
        export_data = coordinator.export_state()
        return JSONResponse(export_data)
        
    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"TabCoordinator not available: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting coordinator state: {e}")


# -------------------- Lightweight helpers for tests/importers --------------------
def _read_first_existing(paths: list[Path]) -> Optional[Dict[str, Any]]:
    for p in paths:
        try:
            if p.exists():
                with open(p, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            continue
    return None


def get_system_metrics() -> Dict[str, Any]:
    """Return system metrics dict from known locations.

    Looks in `04-DATA/data/system_metrics.json`, `data/system_metrics.json` (legacy), and `04-DATA/metrics/system_metrics.json`.
    If none found, computes a live snapshot via ProductionSystemMonitor.
    """
    base = Path(__file__).parent.parent
    candidates = [
        base / '04-DATA' / 'data' / 'system_metrics.json',
        base / 'data' / 'system_metrics.json',  # legacy
        base / '04-DATA' / 'metrics' / 'system_metrics.json',
    ]
    data = _read_first_existing(candidates)
    if isinstance(data, dict) and data:
        return data
    # Fallback: compute a real-time snapshot using ProductionSystemMonitor utility
    try:
        sys.path.append(str(base / '01-CORE'))
        from monitoring.production_system_monitor import get_system_health_check  # type: ignore
        snapshot = get_system_health_check()
        if isinstance(snapshot, dict):
            return snapshot
    except Exception:
        pass
    # Last resort: minimal structure with current timestamp
    from datetime import datetime
    return {
        'timestamp': datetime.now().isoformat(),
        'status': 'unknown'
    }


def get_trading_metrics() -> Dict[str, Any]:
    """Return trading metrics dict from known locations.

    Looks in `04-DATA/data/trading_metrics.json`, `data/trading_metrics.json` (legacy), and `04-DATA/metrics/trading_metrics.json`.
    """
    base = Path(__file__).parent.parent
    candidates = [
        base / '04-DATA' / 'data' / 'trading_metrics.json',
        base / 'data' / 'trading_metrics.json',  # legacy
        base / '04-DATA' / 'metrics' / 'trading_metrics.json',
    ]
    data = _read_first_existing(candidates) or {}
    return data


def get_risk_metrics() -> Dict[str, Any]:
    """Return risk metrics snapshot, computing on the fly if missing."""
    base = Path(__file__).parent.parent
    risk_json = base / '04-DATA' / 'metrics' / 'risk_metrics.json'
    if risk_json.exists():
        try:
            with open(risk_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    # Compute using RiskTracker
    try:
        sys.path.append(str(base / '01-CORE'))
        from risk_management.risk_tracking import RiskTracker  # type: ignore
        tracker = RiskTracker()
        return tracker.compute_snapshot()
    except Exception:
        return {"error": "risk_tracking_unavailable"}


@app.get('/metrics/risk')
async def get_risk():  # pragma: no cover - runtime
    return JSONResponse(get_risk_metrics())


@app.get('/metrics/alerts')
async def get_alerts():  # pragma: no cover - runtime
    """🚨 Obtener alertas activas y recientes"""
    try:
        # Cargar desde alert_threshold_manager
        import sys
        from pathlib import Path
        from datetime import datetime
        base = Path(__file__).parent.parent
        sys.path.append(str(base / '01-CORE'))
        
        from monitoring.alert_threshold_manager import get_alert_threshold_manager
        manager = get_alert_threshold_manager()
        
        # Obtener alertas recientes (últimas 100)
        recent_alerts = manager.get_recent_breaches(limit=100)
        
        # Intentar cargar desde archivos también
        fallback_data = _read_first_existing([
            base / '04-DATA' / 'data' / 'alerts_active.json',
            base / 'data' / 'alerts_active.json',  # legacy
            base / '04-DATA' / 'alerts' / 'alerts.json'
        ]) or {}
        
        return JSONResponse({
            'recent_breaches': recent_alerts,
            'fallback_data': fallback_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        from datetime import datetime
        return JSONResponse({
            'error': f'alerts_unavailable: {str(e)}',
            'recent_breaches': [],
            'fallback_data': {},
            'timestamp': datetime.now().isoformat()
        })


@app.get('/metrics/thresholds')
async def get_thresholds():  # pragma: no cover - runtime
    """⚙️ Obtener configuración de umbrales de alertas"""
    try:
        import sys
        from pathlib import Path
        from datetime import datetime
        base = Path(__file__).parent.parent
        sys.path.append(str(base / '01-CORE'))
        
        from monitoring.alert_threshold_manager import get_alert_threshold_manager
        manager = get_alert_threshold_manager()
        
        # Obtener todas las configuraciones de umbrales
        thresholds = manager.get_all_thresholds()
        
        return JSONResponse({
            'thresholds': thresholds,
            'config_path': str(manager.config_path),
            'last_reload': manager.last_config_load.isoformat(),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        from datetime import datetime
        return JSONResponse({
            'error': f'thresholds_unavailable: {str(e)}',
            'thresholds': {},
            'timestamp': datetime.now().isoformat()
        })


if __name__ == '__main__':  # pragma: no cover
    try:
        import uvicorn  # type: ignore
    except ImportError:
        print("⚠️ uvicorn no instalado. Instalar con: pip install uvicorn[standard]")
    else:
        print(f"Starting Metrics API on http://127.0.0.1:8090 (METRICS_DIR={METRICS_DIR})")
        uvicorn.run("metrics_api:app", host="127.0.0.1", port=8090, reload=True)
