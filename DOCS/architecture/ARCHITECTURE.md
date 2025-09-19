# 🏗️ ARQUITECTURA REAL - ICT Engine v6.0 Enterprise

**Basado en:** Análisis directo del código fuente  
**Estado:** Septiembre 2025 - Post-limpieza documental  
**Enfoque:** Arquitectura real vs documentación obsoleta  

## 📊 ARQUITECTURA GENERAL

```
┌─────────────────────────────────────────────────────────────┐
│                  🎯 ICT ENGINE v6.0 ENTERPRISE             │
│                     Arquitectura Real                      │
└─────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │                       │
        ┌─────────────────────┐   ┌─────────────────────┐
        │   📊 DATA LAYER     │   │   🧠 CORE LAYER     │
        │                     │   │                     │
        │ • MT5DataManager    │   │ • UnifiedMemorySystem│
        │ • FTMO Connection   │   │ • SmartMoneyAnalyzer│
        │ • Real-time Data    │   │ • ICTPatternDetector │
        │ • Historical Cache  │   │ • ValidationPipeline │
        └─────────────────────┘   └─────────────────────┘
                    │                       │
                    └───────────┬───────────┘
                                │
        ┌─────────────────────────────────────────────┐
        │            🎮 INTERFACE LAYER               │
        │                                             │
        │ • Web Dashboard (Dash/Plotly)              │
        │ • Terminal Dashboard (Textual)             │
        │ • Dual Interface Simultaneous              │
        └─────────────────────────────────────────────┘
                                │
        ┌─────────────────────────────────────────────┐
        │           🤖 AUTOMATION LAYER               │
        │                                             │
        │ • ExecutionEngine                           │
        │ • EmergencyStopSystem                       │
        │ • AutoPositionSizer                         │
        │ • BlackBox Logging                          │
        └─────────────────────────────────────────────┘
```

## 🔧 COMPONENTES CORE DETALLADOS

### 🧠 **UnifiedMemorySystem v6.1**
```python
# Estado confirmado: ✅ COMPLETAMENTE OPERATIVO
Location: 01-CORE/analysis/unified_memory_system.py
Integration: Smart Money Analyzer + ICT Pattern Detector
Performance: <0.1s response time enterprise
```

**Funcionalidades Verificadas:**
- ✅ **Trader Real Memory:** Sistema aprende de experiencia histórica
- ✅ **Cross-Component Integration:** 3 componentes integrados
- ✅ **Decision Cache:** Cache inteligente 24h cleanup
- ✅ **SLUC v2.1 Logging:** Logging enterprise estructurado
- ✅ **Persistent Storage:** Memoria entre sesiones

### 📊 **MT5DataManager**
```python
# Estado confirmado: ✅ FUNCIONAL CON FTMO
Location: 01-CORE/data_management/mt5_data_manager.py
Connection: FTMO-Demo established
Thread-Safety: Implemented with fallbacks
```

**Capacidades Verificadas:**
- ✅ **Live Data Feed:** Tiempo real MT5 connection
- ✅ **Historical Data:** Múltiples timeframes y símbolos
- ✅ **Error Handling:** Fallbacks robustos enterprise
- ✅ **Performance:** Optimizado para requests concurrentes

### 🎯 **Pattern Detection Engine**

#### **ICTPatternDetector**
```python
# Estado: ✅ Memory-Aware
Location: 01-CORE/ict_engine/ict_pattern_detector.py
Integration: UnifiedMemorySystem connected
Patterns: BOS, CHoCH, FVG, Order Blocks, Silver Bullet
```

#### **SmartMoneyAnalyzer**  
```python
# Estado: ✅ Memory-Integrated
Location: 01-CORE/smart_money_concepts/smart_money_analyzer.py
Killzones: 5 configured
Liquidity Detection: 6 parámetros
Institutional Analysis: 5 parámetros
```

## 🔍 VALIDATION PIPELINE

### **UnifiedAnalysisPipeline**
```python
# Estado: ✅ Pipeline completo implementado
Location: 01-CORE/validation_pipeline/core/unified_analysis_pipeline.py
Components: OrderBlocks + FVG + SmartMoney validators
Integration: MT5DataManager + UnifiedMemorySystem
```

**Validators Enterprise:**
- ✅ **OrderBlocksValidator:** Validación enterprise con módulos reales
- ✅ **FVGValidator:** Sistema FVG enterprise cargado  
- ✅ **SmartMoneyValidator:** Integrado con memory system
- ✅ **LiveSignalValidator:** Comparación live vs historical

## 🖥️ DASHBOARD ARCHITECTURE

### **Dual Dashboard System**
```
┌─────────────────────┐    ┌─────────────────────┐
│   🌐 WEB DASHBOARD   │    │ 🖥️ TERMINAL DASH    │
│                     │    │                     │
│ • Dash Framework    │    │ • Textual Framework │
│ • (REMOVIDO) Plotly │    │ • Rich Console      │
│ • (REMOVIDO) Web    │    │ • Real-time Updates │
│ • (REMOVIDO) Port   │    │ • Cross-platform    │
└─────────────────────┘    └─────────────────────┘
           │                           │
           └─────────┬─────────────────┘
                     │
       ┌─────────────────────────┐
       │    🎛️ TAB SYSTEM        │
       │                         │
       │ • Order Blocks Tab      │
       │ • FVG Analysis Tab      │  
       │ • Smart Money Tab       │
       │ • Market Structure Tab  │
       │ • System Status Tab     │
       └─────────────────────────┘
```

### **Files Architecture (Post-Deprecación Web):**
```
09-DASHBOARD/
├── ict_dashboard.py ✅ Terminal interface (único)
├── dashboard.py ✅ Coordinador interno
├── start_dashboard.py ✅ Launcher terminal
├── web_dashboard.py (DEPRECATED stub)
├── start_web_dashboard.py (DEPRECATED stub)
└── core/
       ├── tabs/ ✅ Modular tab system (lógica reusable)
       ├── real_market_bridge.py ✅ MT5 bridge
       └── widgets/ ✅ Componentes terminal
```

> NOTA: La interfaz web (Dash/Plotly) está oficialmente descontinuada. Stubs preservados únicamente para compatibilidad de imports. No extender, no reintroducir dependencias UI.

### Deprecación Web Dashboard

La arquitectura actual elimina cualquier servidor Dash/Plotly. Razones:
- Reducción de superficie operacional y dependencias pesadas.
- Enfoque en estabilidad core y métricas vía archivos/API ligera.
- Simplificación de pipeline de despliegue (sin ASGI ni capa gráfica web).

Reemplazos:
- Observabilidad: logs estructurados + `metrics_api.py`.
- Interacción: `ict_dashboard.py` (terminal) y futuras herramientas CLI.

Acciones prohibidas:
- Añadir callbacks Dash.
- Incorporar nuevas dependencias visuales web.
- Expandir los stubs más allá de mensajes de error claros.

## 🤖 TRADING AUTOMATION ARCHITECTURE

### **Execution Engine**
```python
# Location: 01-CORE/real_trading/execution_engine.py
# Estado: ✅ Sistema de ejecución automática
```

### **Risk Management**
```python
# EmergencyStopSystem: 01-CORE/real_trading/emergency_stop_system.py
# AutoPositionSizer: 01-CORE/real_trading/auto_position_sizer.py  
# Estado: ✅ Protección riesgo implementada
```

### **Activation System**
```python
# Script: activate_auto_trading.py
# Estado: ✅ Script de activación disponible
# Safety: Demo-only enforcement
```

## 📝 LOGGING ARCHITECTURE

### **Multi-Layer Logging System**
```
┌─────────────────────┐
│  🎯 SLUC v2.1       │ ← Logging centralizado enterprise
├─────────────────────┤
│  🌉 SIC v3.1        │ ← Bridge enterprise sin warnings  
├─────────────────────┤
│  📊 SmartTradingLog │ ← Logging estructurado funcional
├─────────────────────┤
│  📦 BlackBox System │ ← Order Blocks + FVG logging
└─────────────────────┘
```

### **Log Locations:**
```
05-LOGS/
├── trading/ ✅ Trading automation logs
├── order_blocks/ ✅ BlackBox OB logging
├── fvg/ ✅ BlackBox FVG logging
├── system/ ✅ System-level logs
└── patterns/ ✅ Pattern detection logs
```

## 🔄 DATA FLOW REAL

```
📊 MT5 (FTMO) 
       │
       ▼
🔄 MT5DataManager (Thread-safe)
       │
       ▼
🧠 UnifiedMemorySystem (Memory context)
       │
       ▼  
🎯 Pattern Detection (ICT + Smart Money)
       │
       ▼
🔍 Validation Pipeline (Live vs Historical)
       │
       ▼
🖥️ Dual Dashboards (Web + Terminal)
       │
       ▼
🤖 Trading Automation (ExecutionEngine)
       │
       ▼
📝 BlackBox Logging (Full traceability)
```

## 🎯 ARQUITECTURA ENTERPRISE

### **Characteristics Verified:**
- ✅ **Modular Design:** Componentes independientes e intercambiables
- ✅ **Thread-Safe:** Operaciones concurrentes seguras  
- ✅ **Fallback Systems:** Robustez ante fallos de componentes
- ✅ **Enterprise Logging:** Trazabilidad completa estructurada
- ✅ **Memory Management:** Sistema inteligente de cache y persistencia
- ✅ **Real-time Performance:** <0.1s response time crítico
- ✅ **Dual Interface:** Web + Terminal para diferentes usos
- ✅ **Safety First:** EmergencyStop y demo-only enforcement

### **Escalabilidad:**
- **Horizontal:** Múltiples símbolos y timeframes
- **Vertical:** Upgrades de componentes sin breaking changes
- **Integration:** APIs para sistemas externos
- **Monitoring:** Logging enterprise para análisis post-mortem

---

**📊 Arquitectura Documentada desde Análisis Real del Código**  
*Septiembre 2025 - ICT Engine v6.0 Enterprise*

## 🧩 StrategyPipeline (Flujo de Trading)

Ubicación: `01-CORE/trading/strategy_pipeline.py`

- Propósito: Orquestar el flujo de decisión de trading: validación rápida de entorno/datos → evaluación de riesgo y sizing → ejecución (real o simulada) → tracking → métricas.
- Dependencias:
       - `risk_pipeline` (requerido): expone `evaluate_and_size(signal)` y retorna una decisión con `approved`, `lots`, `stage`, `reasons`, `correlation_score`.
       - `env_validator` (opcional): se consulta `last_result()` para bloqueo rápido si `status == 'ERROR'`.
       - `data_validator` (opcional): si `status == 'WARN'`, se marca `data_quality_warning` (no bloquea).
       - `order_tracker` (opcional): registra posiciones si hubo ejecución.
       - `metrics` (opcional): incrementa contadores y gauges.
       - `executor` (opcional): si expone `execute_order`, realiza ejecución real.

Flujo resumido:
1. Pre-chequeo de entorno y calidad de datos (rápido, no bloqueante salvo error).
2. `risk_pipeline.evaluate_and_size(signal)` → si no aprobado, registra rechazo y corta.
3. Ejecución: real (vía `executor`) o simulada (placeholder sin efectos persistentes).
4. Tracking de posición (si aplica) y registro de latencia en métricas.

Métricas emitidas:
- `risk_rejections` (contador) cuando una señal no es aprobada.
- `signals_processed` (contador) y `last_latency_ms` (gauge) en ejecuciones exitosas.


---

## 📈 Métricas en Producción (sin servidor web)

Para monitoreo en tiempo real sin servidor web, el sistema incluye un exportador de métricas en background que serializa el estado del agregador a JSON.

- Componente: `01-CORE/monitoring/metrics_json_exporter.py` (clase `MetricsJSONExporter`)
- Fuente: `PerformanceMetricsAggregator` (`01-CORE/monitoring/performance_metrics_aggregator.py`)
- Salida: `04-DATA/metrics/`
       - `metrics_live.json`
       - `metrics_summary.json`
       - `metrics_cumulative.json`
       - `metrics_all.json` (combinado)

### Activación

El exportador se inicia desde `main.py` si `ICT_EXPORT_METRICS` está activo:

```powershell
$env:ICT_EXPORT_METRICS = '1'
$env:ICT_EXPORT_INTERVAL = '5'  # opcional, segundos
python .\main.py
```

- `ICT_EXPORT_METRICS`: habilita (`'1'`, `'true'`) o deshabilita el exportador.
- `ICT_EXPORT_INTERVAL`: intervalo de export en segundos (mínimo 0.5; por defecto 5).

La escritura es atómica para evitar archivos corruptos en lecturas concurrentes. El exportador se detiene limpiamente durante `shutdown()`.

### Consumo de métricas

Ejemplo rápido en Python:

```python
from pathlib import Path
import json

metrics_dir = Path('04-DATA/metrics')
with open(metrics_dir / 'metrics_live.json', 'r', encoding='utf-8') as f:
              live = json.load(f)
print(live.get('counters', {}))
```

Nota: El archivo `09-DASHBOARD/metrics_api.py` (FastAPI) es opcional y no requerido para este flujo; se mantiene como utilidad futura.

### Wrappers de uso rápido

Para instrumentación simple sin acoplarse a implementaciones internas, utiliza los wrappers:
- `01-CORE/monitoring/metrics_collector.py` → `record_counter`, `record_gauge`, `time_operation`, `export_snapshot`
- `01-CORE/monitoring/baseline_calculator.py` → `ensure_started`, `baseline_summary`, `compare_metric`

Guía práctica con ejemplos: `DOCS/guides/TRACKING_SETUP.md`.