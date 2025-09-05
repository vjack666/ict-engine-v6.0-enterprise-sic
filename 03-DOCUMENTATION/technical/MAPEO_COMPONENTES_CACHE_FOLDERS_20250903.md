# 📁 MAPEO DE COMPONENTES QUE LLENAN LAS CARPETAS CACHE/MEMORY
## Sistema ICT Engine v6.0 Enterprise

---

## 📊 RESUMEN DE CARPETAS EN 04-DATA/cache

### 🗂️ Estructura de Carpetas
```
04-DATA/cache/
├── analysis/           # Análisis histórico y resultados de patrones
├── memory/            # Memoria de contexto de mercado
├── memory_persistence/ # Persistencia de memoria como trader real
└── reports/           # Reportes de análisis y estado del sistema
```

---

## 🔍 MAPEO DETALLADO: ¿QUIÉN ESCRIBE DÓNDE?

### 📁 04-DATA/cache/analysis/
**Componente Principal:** `ICTHistoricalAnalyzer v6.0`
- **Archivo:** `01-CORE/core/analysis/ict_historical_analyzer_v6.py`
- **Directorio configurado:** `self.historical_cache_dir = self.cache_dir / "historical_analysis"`
- **Archivos generados:**
  - `historical_analysis_cache.json` - Cache de análisis histórico
- **Contenido:**
  - Resultados de análisis de patrones ICT
  - Datos históricos procesados
  - Cache de estructuras de mercado

### 📁 04-DATA/cache/memory/
**Componentes Principales:**
1. **MarketContext v6.0 Enterprise**
   - **Archivo:** `01-CORE/core/analysis/market_context_v6.py`
   - **Directorio configurado:** `self.memory_cache_dir = "cache/memory"`
   - **Archivos generados:**
     - `market_context_state.json` - Estado del contexto de mercado
   
2. **ICTHistoricalAnalyzer v6.0**
   - **Archivo:** `01-CORE/core/analysis/ict_historical_analyzer_v6.py`
   - **Directorio configurado:** `self.cache_dir = "cache/memory"`
   - **Contenido:**
     - Retención de 50 períodos
     - Máximo 200 POIs
     - TTL: 24.0h
     - 7 timeframes

**Contenido:**
- Estado de contexto de mercado actual
- Memoria de POIs (Points of Interest)
- Cache de análisis multi-timeframe
- Datos de retención de períodos

### 📁 04-DATA/cache/memory_persistence/
**Componente Principal:** `MemoryPersistenceManager`
- **Archivo:** `01-CORE/core/analysis/unified_memory_system.py`
- **Directorio configurado:** `self.persistence_dir = Path("data/memory_persistence")`
- **Archivos generados:**
  - `{symbol}_context.json` - Contexto persistente por símbolo
- **Contenido:**
  - Memoria de trader como experiencia real
  - Contexto persistente por símbolo
  - Datos de aprendizaje del sistema

### 📁 04-DATA/cache/reports/
**Componente Principal:** `run_complete_system.py`
- **Función:** `save_analysis_data()`
- **Directorio configurado:** `reports_dir = data_path / "reports" / "production"`
- **Archivos generados:**
  - `analysis_report_{symbol}_{timeframe}_{timestamp}.json`
  - `system_status_report_{timestamp}.json`
- **Contenido:**
  - Reportes de análisis por símbolo y timeframe
  - Reportes de estado del sistema
  - Métricas de rendimiento
  - Resultados de verificación

---

## 🔄 FLUJO DE DATOS POR COMPONENTE

### 1. **Sistema de Memoria Principal (cache/memory/)**
```
MarketContext v6.0 → market_context_state.json
ICTHistoricalAnalyzer → historical_analysis_cache.json
```

### 2. **Sistema de Análisis (cache/analysis/)**
```
ICTHistoricalAnalyzer → historical_analysis/
                     └── historical_analysis_cache.json
```

### 3. **Sistema de Persistencia (cache/memory_persistence/)**
```
UnifiedMemorySystem → {symbol}_context.json (EURUSD_context.json, etc.)
```

### 4. **Sistema de Reportes (cache/reports/)**
```
run_complete_system.py → production/
                      ├── analysis_report_{symbol}_{timeframe}_{timestamp}.json
                      └── system_status_report_{timestamp}.json
```

---

## 📝 CONFIGURACIONES CLAVE

### Cache Directory Settings
```json
{
  "cache_settings": {
    "cache_directory": "cache/memory",
    "historical_analysis_cache": {
      "enabled": true,
      "ttl_hours": 24.0,
      "max_entries": 1000
    }
  }
}
```

### Memory Configuration
```json
{
  "market_context": {
    "retention_periods": 50,
    "max_pois": 200,
    "cache_dir": "cache/memory"
  }
}
```

---

## 🎯 COMPONENTES POR FUNCIONALIDAD

### 📊 Análisis de Mercado
- **MarketStructureAnalyzer** → Cache interno (`_analysis_cache`)
- **POISystem** → Cache interno (`poi_cache`)
- **ICTHistoricalAnalyzer** → `cache/memory/` y `cache/analysis/`

### 🧠 Sistema de Memoria
- **UnifiedMemorySystem** → `cache/memory_persistence/`
- **MarketContext** → `cache/memory/`

### 📈 Detección de Patrones
- **SilverBulletEnterprise** → Usa UnifiedMemorySystem (futuro)
- **PatternDetector** → A través de ICTHistoricalAnalyzer

### 📋 Reportes y Estado
- **run_complete_system.py** → `cache/reports/`
- **ICTDataManager** → Métricas internas

---

## 🔍 LOGS DE EVIDENCIA

### Evidencia en Logs (ict_engine_*.log):
```
[market_memory] ✅ Market Context v6.0 Enterprise inicializado - Cache: cache/memory
[historical_memory] ✅ ICT Historical Analyzer v6.0 Enterprise inicializado - Cache: cache\memory, TTL: 24.0h
```

### Configuración por Defecto:
```python
# ict_historical_analyzer_v6.py línea 145
"cache_directory": "cache/memory"

# market_context_v6.py línea 136
self.memory_cache_dir = "cache/memory"

# unified_memory_system.py línea 628
self.persistence_dir = Path("data/memory_persistence")
```

---

## ✅ ESTADO ACTUAL VERIFICADO

### ✅ Carpetas Activas:
- `04-DATA/cache/analysis/` - ICTHistoricalAnalyzer
- `04-DATA/cache/memory/` - MarketContext + ICTHistoricalAnalyzer
- `04-DATA/cache/memory_persistence/` - UnifiedMemorySystem
- `04-DATA/cache/reports/` - run_complete_system.py

### ✅ Componentes Mapeados:
- **4 carpetas principales** identificadas
- **6 componentes principales** mapeados
- **Configuraciones** verificadas en código
- **Flujo de datos** documentado

---

**Generado:** 2025-09-03 11:45:00  
**Sistema:** ICT Engine v6.0 Enterprise SIC  
**Estado:** Mapeo completo verificado ✅
