# 📊 ICT Engine v6.0 Enterprise - Data Flow Reference

**📅 Creado:** Septiembre 10, 2025  
**🎯 Versión:** v6.0 Enterprise SIC  
**✅ Estado:** Documentación Operacional FASE 2  
**⏱️ Tiempo de referencia:** 5-10 minutos  

---

## 🔄 **OVERVIEW DEL FLUJO DE DATOS**

Mapeo del flujo **MT5 → Sistema ICT → Señales** que está operando exitosamente con 5,000+ velas por símbolo y 11 patrones ICT funcionando.

**Validado en producción:** Score 80%+, UnifiedMemorySystem v6.1, conexión MT5 estable.

---

## 📈 **FASE 1: CAPTURA DE DATOS MT5**

### **🔌 Punto de Entrada: MT5DataManager**
- **Archivo:** `01-CORE/data_management/mt5_data_manager.py`
- **Función:** Conexión directa con FTMO Demo
- **Output:** Raw market data (OHLCV)

### **📥 Descarga Masiva: AdvancedCandleDownloader**
- **Archivo:** `01-CORE/data_management/advanced_candle_downloader.py`  
- **Capacidad:** 5,000+ velas por símbolo
- **Símbolos:** EURUSD, GBPUSD, USDJPY, XAUUSD
- **Timeframes:** M15, H1, H4, D1

### **🔄 Pipeline de Validación**
```
MT5 Raw Data → DataValidator → CleanData → ICTDataManager
```
- **Validador:** `data_management/data_validator_real_trading.py`
- **Manager:** `data_management/ict_data_manager.py`

---

## 🧠 **FASE 2: PROCESAMIENTO INTELIGENTE**

### **💾 Sistema de Memoria Central**
- **Core:** `analysis/unified_memory_system.py`
- **Versión:** v6.1 (optimizada)
- **Capacidad:** 512MB cache, 30 días historial
- **Persistencia:** Auto-save cada 5 minutos

### **🔍 Adaptador de Condiciones**
- **Archivo:** `analysis/market_condition_adapter.py`
- **Función:** Clasifica sesiones (Londres/NY/Asia)
- **Output:** Market context para patrones

### **🎯 Detector de Estructura**
- **Archivo:** `analysis/market_structure_analyzer.py`
- **Detecta:** BOS, CHOCH, Swings, Niveles
- **Integración:** FVG + Liquidity + POI

---

## 🎯 **FASE 3: DETECCIÓN DE PATRONES ICT**

### **🎪 Orchestrador Principal**
- **Archivo:** `patterns_analysis/patterns_orchestrator.py`
- **Coordina:** 11 patrones ICT simultáneamente
- **Scoring:** Sistema de confluencias

### **🔥 Patrones Core Activos:**

#### **Silver Bullet**
- **Detector:** `ict_engine/advanced_patterns/silver_bullet_detector_enterprise.py`
- **Killzones:** Londres (08:00-10:00), NY (13:30-15:30)
- **Confluence:** FVG + Liquidity + POI

#### **Judas Swing**
- **Detector:** `ict_engine/advanced_patterns/judas_swing_detector_enterprise.py`
- **Window:** 30 minutos detección
- **Confirmación:** 3 velas

#### **Liquidity Grab**
- **Detector:** `ict_engine/advanced_patterns/liquidity_grab_detector_enterprise.py`
- **Lookback:** 20 períodos
- **Niveles:** Auto-identificación

#### **FVG (Fair Value Gaps)**
- **Manager:** `analysis/fvg_memory_manager.py`
- **Gaps activos:** Hasta 50 simultáneos
- **Cleanup:** 72 horas auto

### **📊 Sistema de Scoring**
```
Pattern Strength (40%) + Timeframe Alignment (30%) + Market Structure (20%) + Volume (10%) = Final Score
```
- **Mínimo viable:** 60%
- **Alta confianza:** 80%+

---

## 🎛️ **FASE 4: INTEGRACIÓN Y OUTPUT**

### **🔄 Multi-Timeframe Analysis**
- **Archivo:** `analysis/multi_timeframe_analyzer.py`
- **Sincronización:** M15 ↔ H1 ↔ H4 ↔ D1
- **Confluencias:** Cross-timeframe validation

### **🎯 POI System Integration**
- **Core:** `poi_system.py`
- **Niveles:** Support, Resistance, Pivot Points
- **Integración:** Pattern + POI + Market Structure

### **📈 Dashboard Data Bridge**
- **Collector:** `09-DASHBOARD/bridge/data_collector.py`
- **Real-time:** Updates cada 60 segundos
- **Components:** 12 dashboards especializados

---

## 🚨 **FASE 5: RISK MANAGEMENT & OUTPUT**

### **⚖️ Risk Validator Pipeline**
- **Validator:** `risk_management/risk_validator.py`
- **Checks:** Position size, drawdown, correlation
- **Emergency:** Auto-stop si límites excedidos

### **📊 Trading Signals Output**
```
Pattern Detection → Risk Validation → Signal Generation → Dashboard Display
```

### **🔔 Alert System**
- **Logger:** `smart_trading_logger.py`
- **Rate limiting:** 100 msg/min
- **Categories:** INFO, WARNING, CRITICAL

---

## 📊 **FLUJO DE DATOS EN TIEMPO REAL**

### **⏱️ Ciclo de Actualización (60 segundos)**
```
1. MT5 Data Fetch (5s)
2. Data Validation (5s)  
3. Memory Update (10s)
4. Pattern Analysis (20s)
5. Risk Check (5s)
6. Dashboard Update (15s)
```

### **🔄 Estados del Sistema**
- **IDLE:** Esperando datos
- **PROCESSING:** Analizando patrones
- **SIGNAL:** Señal generada
- **RISK_CHECK:** Validando riesgo
- **READY:** Listo para siguiente ciclo

---

## 🎯 **PUNTOS CRÍTICOS DE INTEGRACIÓN**

### **🔗 Conexiones Clave**
1. **MT5 ↔ ICTDataManager:** Estabilidad conexión
2. **UnifiedMemory ↔ Patterns:** Sincronización estado
3. **Patterns ↔ Dashboard:** Real-time updates
4. **RiskValidator ↔ Signals:** Validación continua

### **⚡ Performance Bottlenecks**
- **Memory usage:** Monitoreado <512MB
- **Pattern processing:** Paralelizado
- **Dashboard updates:** Throttled 60s
- **Log volume:** Rate limited

---

## 📈 **MÉTRICAS OPERACIONALES**

### **📊 Throughput Actual**
- **Velas procesadas:** 5,000+ por símbolo
- **Patrones detectados:** 11 simultáneos
- **Actualizaciones:** Cada 60 segundos
- **Memoria utilizada:** <512MB

### **⏱️ Latencias Medidas**
- **MT5 fetch:** 3-8 segundos
- **Pattern detection:** 15-25 segundos
- **Dashboard update:** 10-20 segundos
- **Total cycle:** <60 segundos

---

## 🔧 **CONFIGURACIÓN DEL FLUJO**

### **📋 Archivos de Control**
- **Data flow:** `config/performance_config_enterprise.json`
- **Memory:** `config/memory_config.json`
- **Network:** `config/network_config.json`
- **Patterns:** `config/ict_patterns_config.json`

### **🎛️ Parámetros Críticos**
- **Batch size:** 100 velas
- **Concurrent downloads:** 4 símbolos
- **Update interval:** 60 segundos
- **Cache timeout:** 300 segundos

---

## 🚨 **MONITOREO DEL FLUJO**

### **📝 Logs Críticos**
- **Data flow:** `05-LOGS/data_management/`
- **Patterns:** `05-LOGS/patterns/`
- **Performance:** `05-LOGS/system/`
- **Errors:** `05-LOGS/emergency/`

### **🔍 Comandos de Monitoreo**
```powershell
# Monitoreo en tiempo real
Get-Content "05-LOGS\application\ict_engine_$(Get-Date -Format 'yyyy-MM-dd').log" -Wait -Tail 20

# Estado del flujo
python -c "from analysis.unified_memory_system import UNIFIED_MEMORY; print(UNIFIED_MEMORY.get_system_status())"
```

---

## 📞 **TROUBLESHOOTING DEL FLUJO**

### **🚨 Problemas Comunes**
1. **MT5 disconnect:** Revisar `network_config.json`
2. **Memory overflow:** Ajustar `memory_config.json`
3. **Pattern delays:** Verificar `performance_config.json`
4. **Dashboard lag:** Revisar update intervals

### **🔧 Referencias de Solución**
- **Conexión:** `troubleshooting.md` sección MT5
- **Performance:** `configuration-guide.md` sección Performance
- **Emergencias:** `emergency-procedures.md`

---

**✅ DATA FLOW REFERENCE VALIDADO:** Flujo documentado basado en sistema real operando con 5,000+ velas, 11 patrones ICT, y score 80%+.

**🎯 PRÓXIMO DOCUMENTO FASE 2:** `module-integration.md` - Mapear cómo los 11 patrones ICT trabajan juntos en el UnifiedMemorySystem v6.1.
