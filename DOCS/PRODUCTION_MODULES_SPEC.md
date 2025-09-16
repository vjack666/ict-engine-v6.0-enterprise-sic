# Production Modules Specification (Gap Closure Plan)

Estado: Draft v1
Fecha: 2025-09-15
Autor: System Automation

## Objetivo
Completar los componentes críticos para operación en cuenta real eliminando lógica demo/test, asegurando:
- Consistencia de estado (posiciones, órdenes, riesgo, memoria)
- Observabilidad (logging central, métricas, alerting avanzado)
- Robustez (reintentos, degradación controlada, reconciliación)
- Seguridad operacional (kill-switch, límites, saneamiento de inputs)

## Prioridad de Implementación
P0 = Bloqueante trading real
P1 = Impacta confiabilidad
P2 = Optimización / mejora evolutiva

| Código | Módulo | Prioridad | Descripción Resumida |
|--------|--------|-----------|-----------------------|
| EXE | `execution/execution_engine.py` | P0 | Orquesta ciclo de órdenes: submit, modify, cancel, fill tracking y routing. |
| POS | `execution/position_reconciler.py` | P0 | Reconciliación periódica posiciones/net exposure vs broker. |
| ACC | `data_management/account_state_tracker.py` | P0 | Snapshot robusto de equity, balance, margen, drawdown y latencias. |
| RSK | `risk_management/real_time_risk_guard.py` | P0 | Guard rails (max loss diario, por trade, correlación, exposure). |
| KSW | `emergency/kill_switch.py` | P0 | Centraliza triggers críticos y cierra/ bloquea operaciones. |
| HLT | `data_management/mt5_health_monitor.py` (refactor) | P0 | Monitoreo robusto MT5 (conectividad, latencia, data freshness). |
| SIZ | (reutiliza `risk_management/position_sizing.py`) | P0 | Se integra vía RiskPipeline, no se crea archivo nuevo. |
| SIG | `trading/signal_validation_gate.py` | P0 | Última compuerta: integra validaciones estructurales + riesgo + régimen. |
| CNF | `analysis/confluence/scenario_scorer.py` | P1 | Scoring cruzado de patrones, memory y estructura. |
| TGT | `trading/target_stop_engine.py` | P1 | Cálculo dinámico de TP/SL adaptativo (estructura + volatilidad). |
| MMR | `analysis/memory/insights_engine.py` | P1 | Genera insights unificados a partir de unified memory. |
| LAT | `monitoring/latency_metrics_collector.py` | P1 | Captura latencias (data fetch, análisis, ejecución). |
| MTR | `monitoring/broker_metrics_publisher.py` | P1 | Publica métricas clave (slippage, fill ratio, rejects). |
| VAL | `validation/accuracy_real_metrics_adapter.py` | P1 | Reemplaza métricas pseudo-aleatorias por cálculos deterministas. |
| ALN | `real_trading/state_alignment_service.py` | P1 | Alinea estados internos vs broker tras restart. |
| AUD | `monitoring/audit_trail_logger.py` | P2 | Registro normativo de eventos críticos (órdenes, overrides, kills). |
| PRF | `optimization/performance_profiler.py` | P2 | Micro-perf timings y profiling interno. |
| DED | `analysis/dedup/signal_deduplicator.py` | P2 | Evita señales redundantes intra-ventana lógica. |

## Dependencias y Orden Recomendado (FOCOS)
1. EXE -> SIZ -> TGT -> SIG (Pipeline de decisión a ejecución)
2. ACC -> POS -> RSK -> KSW (Estado + Riesgo + Control)
3. HLT -> LAT -> MTR (Observabilidad broker)
4. VAL -> CNF -> MMR -> DED (Calidad analítica)
5. AUD -> PRF (Trazabilidad y optimización)
6. ALN (Integración tras reinicios; depende de ACC, POS)

## Descripción Detallada (P0)
### execution/execution_engine.py (EXE)
Responsabilidad: API única para colocar/cancelar/modificar órdenes y manejar fills. 
Funciones clave:
- submit_order(order_spec) -> order_id
- modify_order(order_id, params)
- cancel_order(order_id)
- poll_fills() / on_fill(event)
- get_open_orders(), get_positions_snapshot()
Requisitos:
- Idempotencia en reintentos
- Timeouts y fallback a cancel si supera SLA
- Logging estructurado + alertas en fallos críticos

### execution/position_reconciler.py (POS)
Responsabilidad: Comparar posiciones internas vs broker y corregir.
- run_reconciliation(cause: str)
- diff_positions() -> dict
- apply_corrections()
- schedule (cada N minutos + on_start + post-kill-switch)
Alertas si: diferencia net exposure > tolerancia, posición huérfana, símbolo inesperado.

### data_management/account_state_tracker.py (ACC)
Responsabilidad: Snapshot robusto de estado de cuenta y métricas derivadas.
- capture_snapshot()
- get_latest()
- compute_drawdown_series()
- detect_anomalies()
Persistencia rotativa opcional (JSON / parquet). Alimenta RSK y dashboards.

### risk_management/real_time_risk_guard.py (RSK)
Responsabilidad: Evaluar cada señal / orden contra límites dinámicos.
Chequeos: max_risk_per_trade %, daily_loss_limit, max_concurrent_positions, sector/correlation, volatility halt.
- evaluate(order_context) -> Approved | Rejected(reason)
- register_fill(fill_event)
- update_equity(equity_snapshot)

### emergency/kill_switch.py (KSW)
Responsabilidad: Punto único para disparar stop total.
Triggers: exceso drawdown, pérdida conexión, latencia > umbral, errores repetidos ejecución, inconsistent_state.
- trigger(reason, metadata)
- is_active()
- reset(auth)
Integra con alerting y cierra posiciones mediante EXE.

### data_management/mt5_health_monitor.py (HLT) (Refactor)
Reemplazar pass por:
- check_connection()
- measure_latency()
- data_freshness(symbol)
- aggregate_health() -> status enum (OK, DEGRADED, CRITICAL)
Publicar métricas y generar alertas en degradaciones.

### Position Sizing (SIZ)
No se crea módulo nuevo. Se reutiliza `risk_management/position_sizing.py` a través de `RiskPipeline` mezclando (si aplica) hint ICT de `RiskManager`.

### trading/signal_validation_gate.py (SIG)
Última compuerta antes de ejecutar:
- validate(signal_payload) -> {'approved': bool, 'reasons': [...]} (sin pseudo-random)
Reglas: coherencia timeframe, estructura confirmada, riesgo aprobado (RSK), no duplicado (DED), ventana temporal válida.

## P1 Resumidos
(TGT) Dinámica TP/SL; (CNF) Score integrado multi-fuente; (MMR) insights memory; (LAT/MTR) métricas técnicas; (VAL) remueve random; (ALN) alineación tras restart.

## Integración en `main.py`
Añadir inicialización escalonada:
1. Health + Account trackers
2. Execution + Position Reconciler + Risk Guard + RiskPipeline (inyecta RiskManager, PositionSizingCalculator, RealTimeRiskGuard)
3. Kill Switch y Alerting binding
4. Validation Gate + TargetStop
5. Confluence/Scoring + Memory Insights
6. Métricas y Auditoría

Hook points:
- En generación de señal -> SIG -> RSK -> SIZ -> TGT -> EXE
- Ciclo periódico (scheduler) -> ACC capture, POS reconciliation, HLT aggregation
- On startup -> ALN.align_states()
- On fill -> RSK.register_fill + ACC.capture_snapshot

## Reemplazo de Lógica Aleatoria
Archivos con `random.uniform` para métricas (validation pipeline) deben reemplazarse por cálculos deterministas basados en:
- comparaciones históricas vs ground-truth (si disponible)
- heurísticas fijas (umbral > X) en ausencia de ground-truth

## Alerting Integración
Todos los módulos P0 usan AdvancedAlertManager con:
- channel: SYSTEM / RISK / EXECUTION / HEALTH
Dedup: por (module, error_code, symbol) 5m
Rate limit: 1 cada 30s por tipo crítico.

## Métricas Base (Primer Set)
- execution.submit.success_total / fail_total
- execution.latency_ms (histogram buckets)
- risk.rejections_total (por reason)
- account.drawdown_pct_current
- health.connection_status (gauge 0-2)
- kill_switch.active (gauge boolean)

## Pasos Siguientes
1. Confirmar alcance P0 listado
2. Scaffold directorios + stubs productivos (sin pass vacíos; raise explicativo si no implementado)
3. Integrar inicialización en `main.py`
4. Reemplazar random metrics validation
5. Refactor health monitor
6. Migrar prints a alerting + logging

---
Fin del documento.
