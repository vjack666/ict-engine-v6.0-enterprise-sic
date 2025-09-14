# ICT Engine v6.0 Enterprise - Production Control Modules

## Overview
Este documento resume los módulos críticos que protegen la ejecución en tiempo real.
Incluye propósito, señales clave y puntos de integración.

| Módulo | Ruta | Objetivo | Bloquea Ejecución | Persistencia |
|--------|------|----------|------------------|--------------|
| ExecutionRouter | `01-CORE/real_trading/execution_router.py` | Enrutamiento, retries, circuit breaker, métricas | Sí (pre-checks) | metrics_live/summary JSON + audit JSONL |
| Circuit Breaker (embebido) | (dentro de ExecutionRouter) | Corta ejecuciones ante fallos repetidos | Sí | Estado en memoria |
| RiskGuard | `01-CORE/risk_management/risk_guard.py` | Límites de riesgo y drawdown | Indirecto (usado externamente) | No directo |
| HeartbeatMonitor | `01-CORE/real_trading/heartbeat_monitor.py` | Detecta servicios stale | No (solo alerta) | No |
| MarketDataValidator | `01-CORE/real_trading/market_data_validator.py` | Gaps, stale y outliers de velas | Potencial (hook futuro) | No |
| TradeReconciler | `01-CORE/real_trading/trade_reconciler.py` | Detecta discrepancias journal vs broker | No | JSON por ejecución |
| SlippageTracker | `01-CORE/real_trading/slippage_tracker.py` | Estadísticas de slippage | No (observa) | slippage_stats.json |
| ExecutionMetricsRecorder | `01-CORE/real_trading/execution_metrics.py` | Percentiles off-line y cumulativos | No | múltiples JSON |
| ExecutionAuditLogger | `01-CORE/real_trading/execution_audit_logger.py` | Trazabilidad orden a orden | No | JSONL append |
| Logging Protocol | `01-CORE/protocols/logging_protocol.py` | Estándar de logging central | N/A | Logs rotados |

## Flujo de Bloqueo de Órdenes (Pre-Checks ExecutionRouter)
1. Health (HealthMonitor si presente)
2. Latencia (LatencyMonitor)
3. RiskValidator (interfaz / adaptador externo)
4. CircuitBreaker (fallos recientes)
5. Hooks personalizados (`pre_order_hooks`)

Salida: cadena de razón o None (permite continuar).

## Integración Recomendable del MarketDataValidator
```python
validator = MarketDataValidator()
router.pre_order_hooks.append(lambda s,a,v,p: (validator.validate_candles(get_recent_candles())[0], 'market_data_invalid'))
```
(Se puede refinar para cachear resultado y no validar en cada orden).

## Extensiones Futuras Sugeridas
- RiskGuard -> implementar adapter a `RiskValidatorProtocol` para bloqueo directo.
- MarketDataValidator -> caching de último resultado + TTL.
- SlippageTracker -> incluir percentiles en metrics_summary.
- HeartbeatMonitor -> feed a panel de estado en dashboard.

## Buenas Prácticas
- Mantener hooks ligeros (<2ms) para no añadir latencia.
- Limitar persistencia a intervalos razonables (ya implementado en metrics/audit).
- Evitar `type: ignore`; usar stubs o `Optional` seguro.

## Checklist Operativo Diario
- Revisar `metrics_live.json` -> latencia y ratio de fallo.
- Leer `execution_audit.jsonl` para anomalías recientes.
- Ejecutar reconciliación y revisar discrepancias (si aplica broker real).
- Verificar `slippage_stats.json` para desviaciones anormales.

---
Documento generado automáticamente (fecha de creación) para referencia de producción.
