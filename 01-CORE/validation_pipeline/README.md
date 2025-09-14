# Validation Pipeline - ICT Engine v6.0 Enterprise

Pipeline de validación unificada que compara resultados LIVE vs HISTÓRICO usando **los mismos componentes** para garantizar métricas consistentes y auditables.

## 🎯 Objetivos Clave
- Reutilización exacta de analizadores y validadores enterprise (Smart Money, Order Blocks, FVG)
- Backtesting histórico coherente con condiciones operativas reales
- Métricas de accuracy, coverage y consistencia entre entornos
- Reportes estructurados (HTML / JSON / CSV) y fácil integración con dashboard
- Seguridad y estabilidad: degradación graciosa si faltan componentes

## 🧩 Arquitectura de Carpetas
```
validation_pipeline/
  core/                   # Pipeline unificado live
  engines/                # Motores de backtesting (RealICTBacktestEngine)
  analyzers/              # Validadores especializados
  reports/                # Motor de reportes y utilidades
  enterprise_real_trading_integration.py  # Integración trading producción extendida
  enterprise_validation_integration.py    # Integración dinámica validation+trading
  run_validation_pipeline.py              # Script de ejecución (opcional)
  __init__.py             # Punto de entrada de alto nivel
```

## 🔌 Componentes Principales
| Componente | Descripción | Estado Fallback |
|-----------|-------------|-----------------|
| `UnifiedAnalysisPipeline` | Orquestación análisis live | Simulado si no disponible |
| `RealICTBacktestEngine` | Backtesting con mismos analizadores | Simulado si faltan analizadores |
| `SmartMoneyValidatorEnterprise` | Validación señales Smart Money | Simulado |
| `OrderBlocksValidatorEnterprise` | Validación bloques institucionales | Simulado |
| `FVGValidatorEnterprise` | Validación Fair Value Gaps | Simulado |
| `ValidationReportEngine` | Generación reportes estructurados | Simulado |
| `EnterpriseRealTradingManagerFixed` | Ejecución trading real + módulos avanzados | Fallback básico |

## 🆕 Módulos Avanzados de Producción (Integración Trading)
Estos módulos fueron añadidos para robustecer operación real:
- `AccountHealthMonitor`: monitoreo drawdown, margin level, exposición
- `ConnectionWatchdog`: estabilidad de conexión + reconexiones
- `LatencyMonitor`: p50 / p95 / max por etapa del pipeline
- `MetricsCollector`: snapshot consolidado de métricas operativas
- `TradeJournal`: journal estructurado (CSV/JSON) de operaciones
- `DynamicRiskAdjuster`: ajuste dinámico (lotes / stops / concurrencia)

Activados opcionalmente con flags al crear el manager:
```python
manager = create_enterprise_trading_manager_fixed(
    enable_account_health=True,
    enable_connection_watchdog=True,
    enable_latency_monitor=True,
    enable_metrics=True,
    enable_trade_journal=True,
    enable_dynamic_risk=True
)
```

## ⚙️ Flujo de Validación (Simplificado)
1. Carga de configuraciones (`DEFAULT_PIPELINE_CONFIG` o personalizada)
2. Ejecución análisis live (pipeline unificado)
3. Backtesting histórico reutilizando mismos validadores
4. Comparación y cálculo de métricas (accuracy, coverage, ratios)
5. Generación de reportes (si habilitado)
6. Exportación de resumen de estado y métricas

## 🚀 Ejemplo Rápido (Validación Completa)
```python
from validation_pipeline import execute_complete_validation_pipeline

result = execute_complete_validation_pipeline(
    symbol='EURUSD', timeframe='H1', validation_period='short'
)
print(result['pipeline_results']['summary'])
```

## 🔄 Backtesting Directo
```python
from validation_pipeline.engines import get_real_backtest_engine
engine = get_real_backtest_engine(max_candles=1500)
res = engine.run_backtest('GBPUSD', 'M15', period='short')
print(res['summary'])
```

## 🤖 Integración con Trading en Producción
```python
from validation_pipeline.enterprise_real_trading_integration import (
    create_enterprise_trading_manager_fixed, RiskLevel
)

manager = create_enterprise_trading_manager_fixed(risk_level=RiskLevel.CONSERVATIVE)
result = manager.process_trading_signal({
    'symbol': 'EURUSD', 'direction': 'BUY', 'entry_price': 1.1000,
    'stop_loss': 1.0950, 'take_profit': 1.1100,
    'confidence_score': 0.85, 'signal_type': 'smart_money',
    'timeframe': 'M15', 'signal_id': 'SIG_DEMO_01',
    'market_conditions': {'volatility': 1.1, 'trend_confidence': 0.65}
})
print(result.success, result.error_message)
print(manager.get_performance_metrics())
```

## 🛡️ Seguridad y Riesgo
| Control | Descripción | Acción |
|---------|-------------|--------|
| Emergency Stop System | Parada global | Bloquea ejecución si condiciones críticas |
| Account Health | Monitorea drawdown/margin | Reduce riesgo dinámicamente |
| Dynamic Risk | Ajusta lotes & concurrencia | Basado en volatilidad + salud |
| Connection Watchdog | Recuperación tras fallos | Reconecta y notifica |
| Journal | Auditoría operaciones | Export JSON/CSV |

## 🔍 Métricas Expuestas
`manager.get_performance_metrics()` puede incluir:
- `total_trades`, `successful_trades`, `failed_trades`
- `success_rate`, `total_risk_amount`
- `metrics_snapshot` (si métricas activas)
- `latency_stats` (p50/p95/max por etapa)
- `account_health` (estado, margen, exposición)

## 🧪 Modos Simulados
Si algún módulo no está disponible, el sistema:
- Marca `mode: simulated` en resultados
- Proporciona métricas sintéticas controladas
- Mantiene estructura para no romper integraciones downstream

## 🔧 Configuración Personalizada
```python
from validation_pipeline import create_pipeline_config
cfg = create_pipeline_config(
    symbols=['EURUSD','USDJPY'],
    timeframes=['M15','H1'],
    validation_periods=['short','medium'],
    generate_reports=True,
    report_formats=['html','json']
)
```

## 📁 Reportes
Generados vía `generate_validation_report()` (si disponible):
- HTML interactivo
- JSON estructurado
- CSV tabular (extensible)

## 🧱 Extensiones Futuras (Sugeridas)
- Persistencia en base de datos (PostgreSQL / DuckDB)
- Endpoint REST para métricas en vivo
- Sistema de alertas (webhook / Telegram) basado en health
- Motor de optimización parametrizada (walk-forward)

## ✅ Checklist Integridad
- [x] Backtest Engine restaurado
- [x] Módulos producción avanzados
- [x] Integración trading ampliada
- [x] Fallbacks robustos sin `type: ignore`
- [x] Imports resueltos

## 📄 Licencia / Uso Interno
Este módulo forma parte del stack Enterprise ICT Engine v6.0. Uso interno controlado.

---
¿Necesitas agregar secciones para despliegue en servidor o integración dashboard? Indica y lo incorporo.
