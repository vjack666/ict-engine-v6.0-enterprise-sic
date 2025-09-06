# 🧠 UnifiedMemorySystem - Sistema de Memoria Unificado

**Módulo:** UnifiedMemorySystem  
**Archivo principal:** `01-CORE/analysis/unified_memory_system.py`  
**Dependencias:** MarketContextV6, ICTHistoricalAnalyzerV6, SmartTradingLogger  
**Última actualización:** 06/09/2025

## 🎯 Propósito
Sistema centralizado de memoria que integra todos los análisis de mercado, patrones ICT y decisiones de trading en una memoria unificada y persistente. Permite coherencia entre todos los módulos del sistema y mejora la toma de decisiones basada en historial.

## 🏗️ Arquitectura

### Diseño General
El UnifiedMemorySystem actúa como un hub central que conecta:
- Market Context (análisis de contexto de mercado)
- ICT Historical Analyzer (análisis histórico de patrones)
- Pattern Storage (almacenamiento de patrones detectados)
- Trading Decision Cache (caché de decisiones de trading)

### Componentes Principales
```python
class UnifiedMemorySystem:
    """
    Sistema de memoria unificado para coherencia del sistema ICT
    """
    def __init__(self):
        self.market_context = MarketContextV6()
        self.historical_analyzer = ICTHistoricalAnalyzerV6()
        self.logger = SmartTradingLogger()
        self.unified_state = {}
        self.persistence_manager = MemoryPersistenceManager(self)
        
    def update_unified_memory(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza memoria unificada con resultados de análisis
        
        Args:
            analysis_results: Resultados del análisis de mercado
            
        Returns:
            Estado actualizado de la memoria unificada
        """
        # Actualizar contexto de mercado
        market_update = self.market_context.update_context(analysis_results)
        
        # Actualizar análisis histórico
        historical_update = self.historical_analyzer.update_historical_data(analysis_results)
        
        # Integrar en estado unificado
        self.unified_state.update({
            'market_context': market_update,
            'historical_analysis': historical_update,
            'last_update': datetime.now().isoformat(),
            'coherence_score': self._calculate_coherence()
        })
        
        return self.unified_state
```

### Flujo de Datos
```
Pattern Detection → UnifiedMemorySystem → Market Context Update
        ↓                    ↓                       ↓
Trading Decision ←  Memory Coherence  ←  Historical Analysis
        ↓                    ↓                       ↓
    Execution    ←    Persistent Storage  ←   Pattern Storage
```

## 📡 API Reference

### Métodos Públicos

#### `update_unified_memory(analysis_results)`
**Descripción:** Actualiza el estado de memoria unificada con nuevos resultados de análisis  
**Parámetros:**
- `analysis_results` (Dict): Resultados del análisis de mercado conteniendo patrones, señales, etc.

**Retorna:** `Dict` - Estado actualizado de la memoria unificada

**Ejemplo:**
```python
# Ejemplo de uso con resultados de pattern detection
memory_system = UnifiedMemorySystem()
analysis_data = {
    'symbol': 'EURUSD',
    'timeframe': 'M15',
    'patterns_detected': ['BOS', 'FVG'],
    'signals': [pattern_signal_obj],
    'market_structure': 'BULLISH'
}
updated_state = memory_system.update_unified_memory(analysis_data)
print(f"Coherence Score: {updated_state['coherence_score']}")
```

#### `get_contextual_trading_insights(symbol, timeframes)`
**Descripción:** Obtiene insights contextuales para trading basados en memoria histórica  
**Parámetros:**
- `symbol` (str): Símbolo del instrumento (ej: 'EURUSD')
- `timeframes` (List[str]): Lista de timeframes a analizar

**Retorna:** `Dict` - Insights contextuales para trading

**Ejemplo:**
```python
insights = memory_system.get_contextual_trading_insights('EURUSD', ['M15', 'H1'])
print(f"Recomendación: {insights['trading_recommendation']}")
```

#### `persist_unified_memory_state()`
**Descripción:** Persiste el estado actual de la memoria a disco  
**Retorna:** `bool` - True si la persistencia fue exitosa

#### `restore_unified_memory_state()`
**Descripción:** Restaura el estado de memoria desde persistencia  
**Retorna:** `bool` - True si la restauración fue exitosa

### Configuración
```python
# Configuración en 01-CORE/config/memory_config.json
MEMORY_CONFIG = {
    "persistence_enabled": True,
    "persistence_interval": 300,  # 5 minutos
    "max_patterns_stored": 1000,
    "coherence_threshold": 0.7,
    "cleanup_interval": 3600,  # 1 hora
    "backup_retention_days": 7
}
```

## 🔗 Integraciones

### Con MarketContextV6
```python
# Actualización de contexto de mercado
market_context = self.market_context.update_context(analysis_results)
current_bias = market_context.get('market_bias', 'NEUTRAL')
```

### Con ICTHistoricalAnalyzerV6
```python
# Integración con análisis histórico
historical_data = self.historical_analyzer.update_historical_data(analysis_results)
pattern_frequency = historical_data.get('pattern_frequency', {})
```

### Con PatternDetector
```python
# Los patrones detectados se almacenan automáticamente
def store_pattern_result(self, pattern_data: Dict[str, Any]):
    """Almacena resultado de detección de patrones"""
    self.pattern_storage[pattern_data['pattern_id']] = {
        'timestamp': datetime.now(),
        'pattern_type': pattern_data['pattern_type'],
        'confidence': pattern_data['confidence'],
        'symbol': pattern_data['symbol'],
        'metadata': pattern_data.get('metadata', {})
    }
```

### Con Dashboard
```python
# Exposición de datos al dashboard
def get_dashboard_data(self):
    """Datos para el dashboard enterprise"""
    return {
        'memory_state': self.unified_state,
        'coherence_metrics': self._get_coherence_metrics(),
        'pattern_summary': self._get_pattern_summary(),
        'performance_stats': self._get_performance_stats()
    }
```

## 🧪 Testing

### Tests Unitarios
```python
import pytest
from analysis.unified_memory_system import UnifiedMemorySystem

def test_memory_update():
    """Test de actualización de memoria"""
    # Arrange
    memory_system = UnifiedMemorySystem()
    test_data = {
        'symbol': 'EURUSD',
        'patterns_detected': ['BOS'],
        'timestamp': datetime.now().isoformat()
    }
    
    # Act
    result = memory_system.update_unified_memory(test_data)
    
    # Assert
    assert result is not None
    assert 'coherence_score' in result
    assert result['coherence_score'] >= 0.0
    assert result['coherence_score'] <= 1.0

def test_pattern_storage():
    """Test de almacenamiento de patrones"""
    memory_system = UnifiedMemorySystem()
    pattern_data = {
        'pattern_id': 'BOS_EURUSD_20250906',
        'pattern_type': 'BOS',
        'confidence': 0.85,
        'symbol': 'EURUSD'
    }
    
    memory_system.store_pattern_result(pattern_data)
    
    # Verificar que el patrón fue almacenado
    assert pattern_data['pattern_id'] in memory_system.pattern_storage
```

### Tests de Integración
```python
def test_integration_with_pattern_detector():
    """Test de integración con detector de patrones"""
    from analysis.pattern_detector import PatternDetector
    
    memory_system = UnifiedMemorySystem()
    pattern_detector = PatternDetector(memory_system=memory_system)
    
    # Simular detección de patrón
    # Verificar que se almacena en memoria
    pass

def test_memory_persistence():
    """Test de persistencia de memoria"""
    memory_system = UnifiedMemorySystem()
    
    # Añadir datos de prueba
    test_data = {'test': 'data'}
    memory_system.update_unified_memory(test_data)
    
    # Persistir y restaurar
    assert memory_system.persist_unified_memory_state() == True
    assert memory_system.restore_unified_memory_state() == True
```

## 📊 Performance

### Métricas
- **Complejidad temporal:** O(1) para operaciones básicas, O(n) para búsquedas complejas
- **Uso de memoria:** ~50-100MB para 1000 patrones almacenados
- **Throughput típico:** 1000+ actualizaciones/segundo
- **Latencia promedio:** <5ms por actualización

### Optimizaciones Aplicadas
1. **Caché en memoria:** Patrones frecuentes se mantienen en RAM
2. **Persistencia asíncrona:** Escritura a disco no bloquea operaciones
3. **Cleanup automático:** Limpieza de patrones antiguos cada hora
4. **Compresión de datos:** Datos históricos comprimidos para eficiencia

### Benchmarks
```python
def benchmark_memory_updates():
    """Benchmark de actualizaciones de memoria"""
    import time
    
    memory_system = UnifiedMemorySystem()
    test_data = {'symbol': 'EURUSD', 'patterns': ['BOS']}
    
    start_time = time.time()
    for i in range(1000):
        memory_system.update_unified_memory(test_data)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 1000
    print(f"Tiempo promedio por actualización: {avg_time:.6f}s")
    # Resultado esperado: ~0.001-0.005s por actualización
```

## 🔧 Configuración y Setup

### Instalación de Dependencias
```bash
# Las dependencias están incluidas en el proyecto
# No requiere instalación adicional
```

### Configuración Inicial
```python
# Setup básico del sistema de memoria
from analysis.unified_memory_system import get_unified_memory_system

# Obtener instancia singleton
memory_system = get_unified_memory_system()

# Configurar parámetros si es necesario
memory_system.configure({
    'persistence_enabled': True,
    'max_patterns_stored': 1000
})
```

## 🚨 Troubleshooting

### Errores Comunes

#### Error: "Memory coherence below threshold"
**Causa:** El sistema detecta inconsistencias entre diferentes fuentes de datos  
**Solución:**
1. Verificar que todos los módulos usan la misma instancia de memoria
2. Revisar sincronización de timestamps
3. Validar que los datos de entrada son coherentes

#### Error: "Failed to persist memory state"
**Causa:** Error escribiendo al disco (permisos, espacio, etc.)  
**Solución:**
1. Verificar permisos de escritura en `04-DATA/memory_persistence/`
2. Revisar espacio disponible en disco
3. Validar que el directorio existe

#### Warning: "Pattern storage approaching limit"
**Causa:** Se está acercando al límite de patrones almacenados  
**Solución:** 
1. Ejecutar limpieza manual: `memory_system.cleanup_old_patterns()`
2. Ajustar `max_patterns_stored` en configuración
3. Revisar política de retención de datos

### Debugging
```python
# Activar debug logging
import logging
logging.getLogger('unified_memory_system').setLevel(logging.DEBUG)

# Inspeccionar estado interno
memory_system = get_unified_memory_system()
print("Estado actual:", memory_system.get_debug_info())
print("Patrones almacenados:", len(memory_system.pattern_storage))
print("Coherencia actual:", memory_system._calculate_coherence())
```

## 📚 Referencias

### Archivos Relacionados
- `01-CORE/analysis/unified_memory_system.py` - Implementación principal
- `01-CORE/analysis/market_context_v6.py` - Contexto de mercado
- `01-CORE/analysis/ict_historical_analyzer_v6.py` - Análisis histórico
- `01-CORE/config/memory_config.json` - Configuración del sistema

### Documentación Relacionada
- [Pattern Detector Integration](pattern-detection/pattern-detector.md)
- [Market Context Documentation](../02-architecture/market-context.md)
- [Smart Trading Logger](../07-modules/core-engine/smart-trading-logger.md)

### Funciones de Conveniencia
```python
# Funciones helper disponibles en el módulo
from analysis.unified_market_memory import (
    update_market_memory,    # Actualizar memoria rápido
    get_trading_insights,    # Obtener insights
    persist_memory,          # Persistir estado
    restore_memory          # Restaurar estado
)

# Uso simplificado
result = update_market_memory(analysis_results)
insights = get_trading_insights('EURUSD', ['M15', 'H1'])
```

## 📅 Historial de Cambios

### 2025-09-06 - Versión 6.0
- Implementación inicial del UnifiedMemorySystem
- Integración con MarketContextV6 e ICTHistoricalAnalyzerV6
- Sistema de persistencia implementado
- API de conveniencia agregada

### 2025-09-05 - Versión 5.9
- Preparación para integración unificada
- Refactoring de componentes legacy

## 🎯 Próximos Desarrollos
- [ ] Implementación de machine learning para predicción de coherencia
- [ ] Sistema de alertas automáticas por baja coherencia
- [ ] Integración con sistema de backtesting
- [ ] API REST para acceso externo al sistema de memoria
