#!/usr/bin/env python3
"""
SMOKE IMPORTS CHECK - ICT ENGINE v6.0 ENTERPRISE
==============================================

Objetivo: Verificar rápidamente que los módulos críticos del sistema
pueden importarse sin lanzar excepciones graves en el entorno actual.

Uso:
    python -m 01-CORE.validation_pipeline.smoke_imports_check  (ajustar PYTHONPATH)
    ó simplemente: python smoke_imports_check.py (si se ejecuta dentro de 01-CORE/validation_pipeline)

Salida:
- Resume en JSON por stdout: { module: {status: OK|FAIL, error?: str, seconds: float} }
- Código de salida 0 si todo OK, >0 si alguno falla.

No ejecuta lógica pesada: sólo importación. Seguro para CI / pre-run.
"""
from __future__ import annotations
import importlib, json, time, sys, traceback, importlib.util
from typing import List, Dict, Any, Tuple
from pathlib import Path

# --------------------------------- PATH SETUP ---------------------------------
BASE = Path(__file__).resolve().parents[2]  # raíz del repo
CORE_DIR = BASE / '01-CORE'
DASH_DIR = BASE / '09-DASHBOARD'

for p in (BASE, CORE_DIR):
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

# --------------------------- LISTAS DE MÓDULOS A PROBAR -----------------------
# Paquetes importables al añadir 01-CORE al sys.path
PACKAGE_MODULES: List[str] = [
    # Protocolos
    'protocols.logging_central_protocols',
    # Real trading core
    'real_trading.execution_router',
    'real_trading.slippage_tracker',
    'real_trading.market_data_validator',
    'real_trading.execution_metrics',
    'real_trading.execution_audit_logger',
    # Risk management
    'risk_management.risk_guard',
    'risk_management.risk_guard_validator',
    # Validation pipeline engines
    'validation_pipeline.core.validation_engine',
    'validation_pipeline.engines.real_ict_backtest_engine',
]

# Módulos alojados en carpeta con nombre inválido como paquete (09-DASHBOARD)
PATH_MODULES: List[Tuple[str, Path]] = [
    ('dashboard.performance_tab', DASH_DIR / 'core' / 'tabs' / 'performance_tab.py'),
    ('dashboard.risk_health_tab', DASH_DIR / 'core' / 'tabs' / 'risk_health_tab.py'),
]

results: Dict[str, Dict[str, Any]] = {}
failures = 0

def _record_success(name: str, elapsed: float):
    results[name] = {"status": "OK", "seconds": round(elapsed, 4)}

def _record_failure(name: str, elapsed: float, e: Exception):
    global failures
    failures += 1
    results[name] = {
        "status": "FAIL",
        "seconds": round(elapsed, 4),
        "error_class": type(e).__name__,
        "error_message": str(e),
        "trace_tail": traceback.format_exc().splitlines()[-4:]
    }

# ------------------------------ IMPORT PAQUETES --------------------------------
for mod in PACKAGE_MODULES:
    start = time.time()
    try:
        importlib.import_module(mod)
        _record_success(mod, time.time() - start)
    except Exception as e:  # pragma: no cover - smoke failure path
        _record_failure(mod, time.time() - start, e)

# --------------------------- IMPORT POR RUTA (DASH) ---------------------------
for label, path in PATH_MODULES:
    start = time.time()
    try:
        if not path.exists():
            raise FileNotFoundError(f"No encontrado: {path}")
        spec = importlib.util.spec_from_file_location(f"smoke.{label}", path)
        if spec is None or spec.loader is None:  # pragma: no cover
            raise ImportError(f"Spec inválido para {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        _record_success(label, time.time() - start)
    except Exception as e:  # pragma: no cover
        _record_failure(label, time.time() - start, e)

# -------------------------------- RESUMEN FINAL --------------------------------
summary = {
    "total": len(results),
    "ok": sum(1 for r in results.values() if r['status'] == 'OK'),
    "fail": sum(1 for r in results.values() if r['status'] == 'FAIL')
}

output = {"summary": summary, "modules": results}
print(json.dumps(output, ensure_ascii=False, indent=2))

if summary['fail']:
    sys.exit(min(255, summary['fail']))
