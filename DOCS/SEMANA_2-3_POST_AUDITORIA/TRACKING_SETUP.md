# 📄 TRACKING_SETUP.md - Configuración de Métricas y Alertas

**Objetivo:** Dejar listo el entorno de tracking para Semana 2-3.  
**Responsable:** GitHub Copilot  
**Fecha:** 17 Sept 2025

---

## 1) Métricas en Código (rápido)

- [x] Agregar `metrics_collector.py` (wrapper sin duplicación)
- [x] Exponer helpers `record_metric/record_counter/record_gauge/time_operation`
- [ ] Persistir en `04-DATA/metrics/metrics.ndjson` (opcional; hoy export a JSON via `MetricsJSONExporter`)
- [ ] Cron para baseline cada 15 min (usar `baseline_calculator.ensure_started` por ahora)

Ejemplo de uso:
```python
from monitoring.metrics_collector import record_metric, time_operation

record_metric('mt5.latency_ms', 22.5)  # gauge por defecto

with time_operation('data_pipeline'):
  process_data()
```

---

## 2) Dashboard de Métricas (ligero)

- [ ] `09-DASHBOARD/metrics_dashboard.py`
- [ ] Leer `metrics.ndjson` y graficar con Plotly
- [ ] KPIs: latency, throughput, accuracy, cpu, memory

---

## 3) Alertas Proactivas

- [ ] `01-CORE/alerting/proactive_alerts.py`
- [ ] Thresholds definidos en `METRICAS_Y_KPIS.md`
- [ ] Notificaciones a logs + archivo `alerts.ndjson`

Ejemplo threshold YAML:
```yaml
critical:
  memory_usage_pct: "> 1"
  cpu_usage_pct: "> 50"
warning:
  memory_usage_pct: "> 0.7"
  cpu_usage_pct: "> 35"
```

---

## 4) Tareas Programadas (opcional)

- [ ] Script `scripts/schedule_metrics_tasks.py`
- [ ] Ejecutar baseline y limpieza de archivos viejos

---

## 5) Validación Rápida

- [ ] Ejecutar `main.py` y verificar nuevas métricas
- [ ] Confirmar almacenamiento en `04-DATA/metrics`  
- [ ] Ver graficación básica en dashboard

---

## 6) Próximos pasos

- Implementar collectors por categoría (reutilizando `metrics_collector`)
- Conectar alertas con AdvancedAlertManager
- Añadir export a CSV/Parquet para análisis externo

---

## Anexo: Baselines

- Wrapper disponible: `monitoring/baseline_calculator.py`
- API: `ensure_started()`, `baseline_summary()`, `compare_metric(component, metric, value)`

Ejemplo:
```python
from monitoring.baseline_calculator import ensure_started, compare_metric

ensure_started()
res = compare_metric('ict_process', 'cpu_usage_percent', 37.5)
if res.get('exists') and res.get('status') == 'critical':
  # tomar acción
  pass
```
