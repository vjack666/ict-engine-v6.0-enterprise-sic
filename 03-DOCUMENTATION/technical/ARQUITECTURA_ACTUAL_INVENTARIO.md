# 📋 INVENTARIO COMPLETO - ARQUITECTURA ICT ENGINE v6.0 ENTERPRISE
## Fecha: 6 Septiembre 2025

## 🏗️ ESTRUCTURA GENERAL DEL PROYECTO

### 📁 ROOT LEVEL
```
├── main.py                     # ⭐ Orchestrator principal
├── import_manager.py          # 🔧 Gestor centralizado de imports
├── run_complete_system.py     # 🎯 Sistema completo de análisis
├── run_real_market_system.py  # 💰 Sistema de mercado real
└── test_silver_bullet_optimizations.py  # 🧪 Testing
```

## 📂 01-CORE - NÚCLEO DEL SISTEMA

### 🧠 ANÁLISIS Y DETECCIÓN
```
01-CORE/analysis/
├── ict_historical_analyzer_v6.py    # 📊 Análisis histórico ICT
├── market_context_v6.py             # 🌍 Contexto de mercado
├── market_structure_analyzer.py     # 🏗️ Estructura de mercado
├── multi_timeframe_analyzer.py      # ⏱️ Análisis multi-timeframe
├── pattern_detector.py              # 🔍 Detector de patrones base
├── poi_detector_adapted.py          # 📍 Detector POI adaptado
├── unified_memory_system.py         # 🧠 Sistema de memoria unificado
├── unified_market_memory.py         # 💾 Memoria de mercado
├── fvg_integration_patch.py         # 🔧 Integración FVG
├── fvg_memory_manager.py            # 📝 Gestor memoria FVG
└── market_condition_adapter.py     # 🔄 Adaptador condiciones
```

### 🎯 MOTOR ICT ENGINE
```
01-CORE/ict_engine/
├── pattern_detector.py                    # 🔍 Detector principal
├── displacement_detector_enterprise.py    # ⚡ Displacement Enterprise
├── fractal_analyzer_enterprise.py         # 🌀 Fractales Enterprise
├── ict_types.py                           # 📋 Tipos ICT
└── advanced_patterns/
    ├── pattern_analyzer_enterprise.py     # 📊 Analizador Enterprise
    ├── judas_swing_enterprise.py          # 🎭 Judas Swing
    ├── liquidity_grab_enterprise.py       # 💧 Liquidity Grab
    ├── order_block_mitigation_enterprise.py # 📦 Order Blocks
    └── silver_bullet_enterprise.py        # 🔫 Silver Bullet
```

### 💰 SMART MONEY CONCEPTS
```
01-CORE/smart_money_concepts/
└── smart_money_analyzer.py  # 💡 Analizador Smart Money principal
```

### 📊 GESTIÓN DE DATOS
```
01-CORE/data_management/
├── mt5_data_manager.py                # 📈 Gestor datos MT5
├── mt5_connection_manager.py          # 🔌 Gestor conexión MT5
├── ict_data_manager.py               # 🎯 Gestor datos ICT
└── data_validator_real_trading.py    # ✅ Validador datos reales
```

### 🛠️ UTILIDADES
```
01-CORE/utils/
└── mt5_data_manager.py  # 📊 Gestor MT5 utils (duplicado?)
```

### ⚙️ OPTIMIZACIÓN
```
01-CORE/optimization/
└── detector_pool_manager.py  # 🎯 Pool de detectores
```

### 🎛️ CONFIGURACIÓN
```
01-CORE/config/
├── cache_config.json
├── ict_patterns_config.json
├── memory_config.json
├── performance_config_enterprise.json
└── [otros configs...]
```

## 📱 09-DASHBOARD - INTERFAZ DE USUARIO

### 🎛️ NÚCLEO DASHBOARD
```
09-DASHBOARD/
├── dashboard.py              # 📊 Dashboard principal
├── ict_dashboard.py         # 🎯 Dashboard ICT
├── launch_dashboard.py      # 🚀 Lanzador
├── start_dashboard.py       # ▶️ Iniciador
└── test_real_data.py        # 🧪 Test datos reales
```

### 🌉 PUENTES Y COMUNICACIÓN
```
09-DASHBOARD/bridge/
└── dashboard_bridge.py  # 🌉 Puente dashboard-core
```

### 🧩 COMPONENTES
```
09-DASHBOARD/components/
├── alerts_widget.py      # 🚨 Widget alertas
├── coherence_widget.py   # 🔗 Widget coherencia
└── [otros widgets...]
```

## 🔄 FLUJO DE DATOS IDENTIFICADO

### 📊 ENTRADA DE DATOS
1. **MT5DataManager** → Obtiene datos reales de MetaTrader5
2. **ICTDataManager** → Gestiona datos para análisis ICT
3. **ImportManager** → Maneja imports seguros

### 🔍 PROCESAMIENTO
1. **ICTPatternDetector** → Detecta patrones ICT
2. **SmartMoneyAnalyzer** → Analiza conceptos Smart Money
3. **UnifiedMemorySystem** → Gestiona memoria y aprendizaje

### 📱 SALIDA
1. **Dashboard** → Interfaz visual
2. **DashboardBridge** → Comunicación dashboard-core
3. **Archivos JSON** → Reportes de producción

## ⚠️ PROBLEMAS IDENTIFICADOS

### 🔴 DUPLICACIONES
- `mt5_data_manager.py` existe en `/data_management/` y `/utils/`
- Múltiples detectores de patrones con funcionalidad similar

### 🟡 WARNINGS EN EJECUCIÓN
- `'UnifiedMemorySystem' object has no attribute 'get_historical_patterns'`
- `'UnifiedMemorySystem' object has no attribute 'get_session_statistics'`
- Algunos dashboard objects sin atributo `'project_root'`

### 🟢 FUNCIONAMIENTO CORRECTO
- ✅ Conexión MT5 exitosa
- ✅ Obtención de datos reales (500 velas)
- ✅ Detección básica de patrones
- ✅ Análisis Smart Money
- ✅ Generación de reportes JSON

## 🎯 PRÓXIMOS PASOS RECOMENDADOS

### 1. 🔧 CONSOLIDACIÓN
- Eliminar duplicaciones de módulos
- Unificar detectores de patrones
- Resolver conflicts de atributos faltantes

### 2. 🚀 OPTIMIZACIÓN
- Mejorar UnifiedMemorySystem
- Completar métodos faltantes
- Optimizar flujo de datos

### 3. 📊 EXPANSIÓN
- Ampliar análisis de mercado
- Mejorar dashboard widgets
- Añadir más patrones ICT

---
**Estado**: ✅ Sistema funcional con áreas de mejora identificadas
**Prioridad**: 🔴 Alta - Resolver duplicaciones y warnings
**Siguiente**: 🎯 Consolidación de módulos y optimización de memoria
