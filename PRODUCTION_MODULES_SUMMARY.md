# ICT Engine v6.0 Enterprise - Production Control Modules

## Overview
Este documento resume los módulos críticos que protegen la ejecución en tiempo real.
Incluye propósito, señales clave y puntos de integración.

| Módulo | Ruta | Objetivo | Bloquea Ejecución | Persistencia |
|--------|------|----------|------------------|--------------|
| ExecutionRouter | `01-CORE/real_trading/execution_router.py` | Enrutamiento, retries, circuit breaker, métricas | Sí (pre-checks) | metrics_live/summary JSON + audit JSONL |
| Circuit Breaker (embebido) | (dentro de ExecutionRouter) | Corta ejecuciones ante fallos repetidos | Sí | Estado en memoria |
| RiskGuard | `01-CORE/risk_management/risk_guard.py` | Límites de riesgo y drawdown | Indirecto (usado externamente) | `risk_guard_status.json` snapshot |
| RiskGuardValidator | `01-CORE/real_trading/risk_guard_validator.py` | Adaptador RiskGuard a RiskValidatorProtocol | Sí (pre-check directo) | Lee snapshot RiskGuard |
| HeartbeatMonitor | `01-CORE/real_trading/heartbeat_monitor.py` | Detecta servicios stale | No (solo alerta) | No |
| MarketDataValidator | `01-CORE/real_trading/market_data_validator.py` | Gaps, stale y outliers de velas | Potencial (hook futuro) | No |
| TradeReconciler | `01-CORE/real_trading/trade_reconciler.py` | Detecta discrepancias journal vs broker | No | JSON por ejecución |
| SlippageTracker | `01-CORE/real_trading/slippage_tracker.py` | Estadísticas de slippage | No (observa) | slippage_stats.json |
| ExecutionMetricsRecorder | `01-CORE/real_trading/execution_metrics.py` | Percentiles off-line y cumulativos | No | live/summary/cumulative JSON + blocked_reasons |
| ExecutionAuditLogger | `01-CORE/real_trading/execution_audit_logger.py` | Trazabilidad orden a orden | No | JSONL append |
| RateLimiter | `01-CORE/real_trading/rate_limiter.py` | Token bucket global y por símbolo | Sí (pre-check) | rate_limits.json |
| SessionStateManager | `01-CORE/real_trading/session_state_manager.py` | Persistencia contexto órdenes | No | session_state.json + events.jsonl |
| CompositeHealthMonitor | `01-CORE/real_trading/composite_health_monitor.py` | Health agregado (latencia+data+heartbeat) | Sí (reemplaza HealthMonitor) | No |
| AlertDispatcher | `01-CORE/real_trading/alert_dispatcher.py` | Canal unificado eventos críticos | No (observa/alerta) | alerts.jsonl + rotación |
| PositionSizer | `01-CORE/real_trading/position_sizer.py` | Cálculo volumen basado en riesgo fijo / volatilidad | Indirecto (ajusta volume previo) | No |
| PortfolioExposureTracker | `01-CORE/real_trading/portfolio_exposure_tracker.py` | Seguimiento exposición por símbolo y total | No (observa post-ejecución) | portfolio_exposure.json |
| TradeComplianceChecker | `01-CORE/real_trading/trade_compliance_checker.py` | Lista negra, horas restringidas, spread, cooldown pérdidas | Sí (bloquea antes de pre-checks) | No |
| ExecutionRetryPolicy | `01-CORE/real_trading/execution_retry_policy.py` | Retries internos con backoff y jitter | Indirecto (envío encapsulado) | No |
| Logging Protocol | `01-CORE/protocols/logging_protocol.py` | Estándar de logging central | N/A | Logs rotados |
| PerformanceTab (Dashboard) | `09-DASHBOARD/core/tabs/performance_tab.py` | Visualización métricas ejecución | No | Lee JSON existentes |
| RiskHealthTab (Dashboard) | `09-DASHBOARD/core/tabs/risk_health_tab.py` | Resumen riesgo, slippage, bloqueos | No | Lectura pasiva |
| Smoke Imports Script | `01-CORE/validation_pipeline/smoke_imports_check.py` | Verifica importabilidad crítica | N/A | Salida JSON stdout |

## Flujo de Bloqueo / Control de Órdenes (ExecutionRouter)
Orden actualizado con módulos nuevos:
0. **PositionSizer** (ajusta `volume` según riesgo si habilitado)
1. **TradeComplianceChecker** (blacklist, horas, spread, cooldown)
2. **RateLimiter** (tokens global/símbolo)
3. **Health Monitor** (simple o Composite)
4. **Latencia** (LatencyMonitor)
5. **RiskValidator** (RiskGuardValidator / custom)
6. **CircuitBreaker** (fallos ventana)
7. **Hooks personalizados** (`pre_order_hooks`)
8. **MarketDataValidator** (TTL para validar velas)
9. **ExecutionRetryPolicy** (retries internos por envío executor)

Nota: El router mantiene bucle externo de retries (`max_retries`). Si se habilita `ExecutionRetryPolicy` conviene reducir `max_retries` para evitar multiplicación de intentos (ej: policy 3 intentos * router 3 ciclos = 9). Ajustar según tolerancia.

Salida: cadena de razón o None (permite continuar).

## Sistema de Alertas Críticas
**AlertDispatcher** centraliza todos los eventos críticos:
- **Circuit Breaker**: Al activarse o fallos de ejecución
- **Risk Blocks**: Validación de riesgo fallida
- **Order Failures**: Fallos finales tras todos los retries
- **System Health**: Latencia alta, sistemas no saludables
- **Rate Limiting**: Límites alcanzados

Configuración de severidad y canales:
- **Consola/Log**: Para alertas MEDIUM+
- **Archivo JSONL**: Todas las alertas con rotación
- **Callbacks**: Para integración webhook/dashboard futura

## Persistencia y Snapshots
- **ExecutionRouter**: `metrics_live.json`, `metrics_summary.json`
- **RiskGuard**: `risk_guard_status.json` (cada evaluación)
- **SlippageTracker**: `slippage_stats.json` 
- **SessionState**: `session_state.json`, `session_events.jsonl`
- **RateLimiter**: `rate_limits.json`
- **Audit**: `execution_audit.jsonl` (append atomico)
- **Alertas**: `alerts.jsonl` (rotación automática)

## Integración Recomendable Completa
```python
# Setup completo de ExecutionRouter con todos los módulos
from alert_dispatcher import AlertDispatcher, AlertDispatcherConfig
from rate_limiter import RateLimiter, RateLimiterConfig  
from session_state_manager import SessionStateManager, SessionStateConfig
from composite_health_monitor import CompositeHealthMonitor, CompositeHealthConfig
from risk_guard_validator import RiskGuardValidator
from market_data_validator import MarketDataValidator

# Configurar alertas
alert_config = AlertDispatcherConfig(max_alerts_per_minute=30)
alerts = AlertDispatcher(alert_config)

# Configurar rate limiting
rate_config = RateLimiterConfig(global_rate=100, per_symbol_rate=10)
rate_limiter = RateLimiter(rate_config)

# Health monitor compuesto
health_config = CompositeHealthConfig(max_latency_ms=500, max_market_data_age_sec=30)
health_monitor = CompositeHealthMonitor(latency_monitor=latency_mon, config=health_config)

# Risk validator directo
risk_validator = RiskGuardValidator(risk_guard_instance, alerts)

# Session state
session_state = SessionStateManager(SessionStateConfig())

# ExecutionRouter con todos los módulos
router = ExecutionRouter(
    primary_executor=primary_exec,
    backup_executor=backup_exec,
    risk_validator=risk_validator,
    latency_monitor=latency_mon,
    health_monitor=health_monitor,
    alert_dispatcher=alerts,
    config=router_config
)

# Hook adicional para market data
md_validator = MarketDataValidator()
router.pre_order_hooks.append(
    lambda s,a,v,p: (md_validator.validate_candles(get_recent_candles())[0], 'market_data_invalid')
)
```

## Dashboard Integration
- **PerformanceTab**: Lee `metrics_live.json`, `metrics_summary.json`, `slippage_stats.json`
- **RiskHealthTab**: Lee `risk_guard_status.json`, alertas recientes, blocked_reasons
- **OrderBlocksTab**: Detección en tiempo real con visualización y métricas

## Extensiones Completadas ✅
- ✅ RiskGuard -> RiskGuardValidator adapter para bloqueo directo
- ✅ SlippageTracker -> percentiles incluidos en ExecutionRouter metrics
- ✅ RiskHealthTab -> integrado con snapshot RiskGuard (`risk_guard_status.json`)
- ✅ ExecutionRouter -> export blocked_reasons en metrics_live
- ✅ Logging Protocol -> estandarizado en todos los módulos
- ✅ RateLimiter -> token bucket con hook pre-order
- ✅ SessionStateManager -> persistencia contexto órdenes
- ✅ CompositeHealthMonitor -> health agregado reemplaza HealthMonitor simple
- ✅ AlertDispatcher -> canal unificado para eventos críticos con integración
- ✅ PositionSizer -> sizing de riesgo integrado antes de pre-checks
- ✅ TradeComplianceChecker -> bloquea por reglas de compliance previas
- ✅ PortfolioExposureTracker -> persistencia de exposición por símbolo tras fills
- ✅ ExecutionRetryPolicy -> backoff interno opcional encapsulando send_order

## Buenas Prácticas
- Mantener hooks ligeros (<2ms) para no añadir latencia.
- Limitar persistencia a intervalos razonables (ya implementado en metrics/audit).
- Rate limiting configurado conservadoramente para evitar blocks innecesarios.
- Alertas con severidad apropiada para evitar ruido.
- Health monitoring con timeouts razonables para servicios externos.
- Session state para recuperación tras reinicio.

## Smoke Testing
Ejecutar `smoke_imports_check.py` antes de deploy para verificar que todos los módulos críticos son importables.

## Arquitectura de Producción
Todos los módulos están diseñados para:
- **Fallo seguro**: Errores internos no bloquean ejecución principal
- **Performance**: Operaciones <5ms en path crítico
- **Observabilidad**: Logging estructurado y métricas detalladas
- **Persistencia atómica**: Sin corrupción ante interrupciones
- **Type safety**: Sin `type: ignore`, compatibilidad Pylance completa
- Evitar `type: ignore`; usar stubs o `Optional` seguro.

## Checklist Operativo Diario
- Revisar `metrics_live.json` -> latencia y ratio de fallo.
- Leer `execution_audit.jsonl` para anomalías recientes.
- Ejecutar reconciliación y revisar discrepancias (si aplica broker real).
- Verificar `slippage_stats.json` para desviaciones anormales.
- Ejecutar `python 01-CORE/validation_pipeline/smoke_imports_check.py` antes de despliegues.

---
Documento actualizado: incluye snapshot de riesgo, blocked_reasons y estandarización de logging. (última actualización automática)
