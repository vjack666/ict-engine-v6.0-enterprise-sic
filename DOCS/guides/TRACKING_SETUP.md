# 📈 Métricas y Baselines — Guía Rápida

Esta guía explica cómo instrumentar y consumir métricas en ICT Engine v6.0 Enterprise sin duplicar lógica, reutilizando los sistemas existentes.

- Wrappers: `01-CORE/monitoring/metrics_collector.py`, `01-CORE/monitoring/baseline_calculator.py`
- Núcleo: `PerformanceMetricsAggregator`, `BaselineMetricsSystem`
- Exportador JSON opcional: `01-CORE/monitoring/metrics_json_exporter.py`

## 1) Instrumentación mínima

Ejemplos de uso rápido con el wrapper de métricas:

```python
from monitoring.metrics_collector import record_counter, record_gauge, time_operation

record_counter("orders.executed")            # contador +1
record_gauge("latency.ms", 12.3)            # gauge en float

# Mide tiempo de bloque y registra automáticamente:
# - counter: ops.analysis
# - gauge:   latency.analysis_ms
with time_operation("analysis"):
    run_analysis()
```

Notas:
- El wrapper intenta reutilizar una instancia global expuesta por `main.get_performance_metrics_instance()`.
- Si no existe, crea un `PerformanceMetricsAggregator` local.
- En caso extremo, degrada a un shim de no-ops (nunca rompe el flujo).

## 2) Baselines: comparación y resumen

```python
from monitoring.baseline_calculator import ensure_started, baseline_summary, compare_metric

ensure_started()  # inicia el sistema de baselines si no estaba activo
summary = baseline_summary()  # dict resumido de baselines

# Compara un valor contra su baseline definido
cmp = compare_metric("ict_process", "cpu_usage_percent", 42.0)
# → { exists, baseline_value, current_value, deviation_percent, status, unit }
```

Características:
- No duplica reglas de baseline: delega en `BaselineMetricsSystem` existente.
- Reutiliza la lógica interna para determinar `status` según desviación y métrica.

## 3) Exportación a JSON (opcional, sin servidor web)

Para observabilidad en tiempo real mediante archivos JSON:

- Componente: `01-CORE/monitoring/metrics_json_exporter.py`
- Salida: `04-DATA/metrics/metrics_live.json`, `metrics_summary.json`, `metrics_cumulative.json`, `metrics_all.json`

Activación desde PowerShell (Windows):

```powershell
$env:ICT_EXPORT_METRICS = '1'
$env:ICT_EXPORT_INTERVAL = '5'  # opcional, segundos (min 0.5)
python .\main.py
```

La escritura es atómica y el exportador se detiene limpiamente al hacer shutdown del sistema.

## 4) Convenciones de nombres

- Contadores: `ops.<nombre>` para operaciones, `orders.*`, `risk_*`, etc.
- Latencias: `latency.<nombre>_ms` (en milisegundos).
- Gauges genéricos: `*.ms`, `*.percent`, `memory.*`, `cpu.*`.

## 5) Buenas prácticas

- No lanzar excepciones desde la capa de métricas: la observabilidad no debe romper el flujo de negocio.
- Preferir `time_operation()` para medir bloques críticos de forma uniforme.
- Mantener bajo el intervalo del exportador (3–10s) para evitar I/O excesivo.
- Documentar nuevos nombres de métricas en el módulo que las emite.

## 6) Lectura programática rápida

```python
from pathlib import Path
import json

metrics_dir = Path('04-DATA/metrics')
with open(metrics_dir / 'metrics_live.json', 'r', encoding='utf-8') as f:
    live = json.load(f)
print(live.get('counters', {}))
```

## 7) Problemas comunes

- Archivo bloqueado en Windows: asegúrate de que no haya otro proceso con handle abierto permanente.
- Métricas vacías: si no se han emitido métricas, los JSON contendrán estructuras vacías; valida claves.
- Deviations extrañas: confirma que el baseline para `component_metric` exista y que la unidad (unit) coincida.
