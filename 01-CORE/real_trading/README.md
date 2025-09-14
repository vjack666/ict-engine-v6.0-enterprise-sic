# Real Trading Module - ICT Engine v6.0 Enterprise

Módulo central para gestión de trading en cuenta real con enfoque en:
- Consistencia de ejecución
- Gestión de riesgo dinámica
- Observabilidad (salud, métricas, latencia, journal)
- Seguridad operacional (emergency stop, watchdog)

## 📦 Componentes Core
| Componente | Archivo | Rol |
|-----------|---------|-----|
| `ExecutionEngine` | `execution_engine.py` | Envío y gestión de órdenes |
| `SignalValidator` | `signal_validator.py` | Validación estructural y contextual de señales |
| `EmergencyStopSystem` | `emergency_stop_system.py` | Parada global bajo condiciones críticas |
| `AutoPositionSizer` | `auto_position_sizer.py` | Cálculo básico de tamaño (deprecated si se usa RiskManager) |

## 🆕 Subsystemas Avanzados
| Componente | Archivo | Función |
|-----------|---------|---------|
| `AccountHealthMonitor` | `account_health_monitor.py` | Monitorea balance, equity, drawdown, margin level, exposición |
| `ConnectionWatchdog` | `connection_watchdog.py` | Supervisa conexión, latencia y reconexiones |
| `LatencyMonitor` | `latency_monitor.py` | Registra latencia p50/p95/max por etapa |
| `MetricsCollector` | `metrics_collector.py` | Agregación de métricas operativas |
| `TradeJournal` | `trade_journal.py` | Registro estructurado (JSON/CSV) de operaciones |
| `DynamicRiskAdjuster` | `dynamic_risk_adjuster.py` | Ajusta lotes/stops/concurrencia según mercado y salud |

## 🧠 Integración con `EnterpriseRealTradingManagerFixed`
Estos componentes se inicializan opcionalmente mediante flags al crear el manager (archivo: `validation_pipeline/enterprise_real_trading_integration.py`).

```python
from validation_pipeline.enterprise_real_trading_integration import create_enterprise_trading_manager_fixed, RiskLevel

manager = create_enterprise_trading_manager_fixed(
    risk_level=RiskLevel.MODERATE,
    enable_account_health=True,
    enable_connection_watchdog=True,
    enable_latency_monitor=True,
    enable_metrics=True,
    enable_trade_journal=True,
    enable_dynamic_risk=True
)
```

## 🔁 Flujo Operativo Simplificado
1. Llega señal (generador externo / módulo SMC / dashboard)
2. Validación -> `SignalValidator`
3. Cálculo tamaño -> RiskManager + `DynamicRiskAdjuster` (si activo)
4. Ejecución -> `ExecutionEngine`
5. Registro -> `TradeJournal` + `MetricsCollector` + latencia
6. Monitoreo continuo -> `AccountHealthMonitor`, `ConnectionWatchdog`

## 📊 Ejemplo Procesamiento de Señal
```python
signal = {
    'symbol': 'EURUSD', 'direction': 'BUY', 'entry_price': 1.1000,
    'stop_loss': 1.0950, 'take_profit': 1.1100,
    'confidence_score': 0.84, 'signal_type': 'smart_money',
    'timeframe': 'M15', 'signal_id': 'SIG_LIVE_001',
    'market_conditions': {'volatility': 1.15, 'trend_confidence': 0.7}
}
result = manager.process_trading_signal(signal)
print(result.success, result.error_message)
print(manager.get_performance_metrics())
```

## 📈 Métricas Clave Expuestas
`manager.get_performance_metrics()` puede incluir:
- `total_trades`, `successful_trades`, `failed_trades`, `success_rate`
- `metrics_snapshot` (agregados de `MetricsCollector`)
- `latency_stats` (p50/p95/por etapa)
- `account_health` (estado + margin + exposure)

## 🛡️ Seguridad & Riesgo
| Mecanismo | Protección |
|-----------|-----------|
| Emergency Stop | Bloquea toda nueva ejecución en estado crítico |
| Dynamic Risk | Reduce tamaño en volatilidad alta o estado WARNING/CRITICAL |
| Account Health | Detecta drawdown temprano y margen bajo |
| Connection Watchdog | Reintenta conexión y evita órdenes a ciegas |

## 🗃️ Journal
```python
# Exportar journal luego de varias operaciones
path_json = manager.trade_journal.export_json()  # si activo
path_csv = manager.trade_journal.export_csv()
```
Estructura de entrada: timestamp, symbol, direction, volume, entry/exit, pnl, strategy, tags, meta.

## 🔧 Extensiones Futuras (Sugeridas)
- Persistencia journal en base (PostgreSQL / DuckDB)
- WebSocket para difusión de fills y métricas
- Integración con gestor de sesiones multi-cuenta
- Motor de orquestación para batch de señales priorizadas

## 🧪 Modo Fallback
Si algún módulo no está disponible, el sistema:
- Inicializa stub interno
- Evita levantar excepciones fatales
- Marca diferencias en métricas (sin romper estructura)

## ✅ Checklist Integridad
- [x] Módulos avanzados integrados
- [x] Flags de activación por subsistema
- [x] Degradación controlada
- [x] Export centralizada vía `get_performance_metrics()`

## 📄 Nota
Este módulo depende de configuraciones de riesgo externas (RiskManager) ya integradas en el stack. Asegúrate de usarlo en entorno con datos de cuenta reales para métricas correctas.

---
¿Necesitas guía para integrar con el dashboard o MT5 real? Pide y la agrego.
