# 📄 TRACKING_SETUP.md - Configuración de Métricas y Alertas

**Objetivo:** Dejar listo el entorno de tracking para Semana 2-3.  
**Responsable:** GitHub Copilot  
**Fecha:** 17 Sept 2025

---

## 1) Métricas en Código (rápido)

- [ ] Agregar `metrics_collector.py` (skeleton)
- [ ] Exponer función `record_metric(name, value, tags=None)`
- [ ] Persistir en `04-DATA/metrics/metrics.ndjson`
- [ ] Cron para baseline cada 15 min

Ejemplo de uso:
```python
from monitoring.metrics_collector import record_metric
record_metric('mt5.latency_ms', 22.5, {'symbol': 'EURUSD'})
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

- Implementar collectors por categoría
- Conectar alertas con AdvancedAlertManager
- Añadir export a CSV/Parquet para análisis externo
