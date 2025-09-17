# 🧠 GUÍA DE USO - SISTEMA DE MEMORIA ICT ENGINE v6.0

Esta guía explica cómo usar el sistema completo de gestión de memoria optimizado.

## 🚀 INICIO RÁPIDO

### Para Producción (Recomendado)
```python
from scripts.ict_memory_manager import start_ict_memory_management

# Iniciar gestión automática
memory_manager = start_ict_memory_management()
print("✅ Sistema de memoria activo")
```

### Para Análisis/Debugging
```powershell
# Ver uso actual de memoria por componente
python .\scripts\memory_profiler.py

# Realizar limpieza manual
python .\scripts\memory_optimizer.py  

# Test lazy loading
python .\scripts\lazy_loader.py

# Sistema completo
python .\scripts\ict_memory_manager.py
```

## 🔧 CONFIGURACIÓN

### Límites por Defecto
- SmartMoneyAnalyzer: 70MB
- UnifiedMemorySystem: 30MB
- DataManagement: 40MB
- Dashboard: 25MB
- Global: 200MB

### Modificar Límites
```python
from scripts.ict_memory_manager import get_ict_memory_manager

manager = get_ict_memory_manager()
# Cambiar límite de SmartMoneyAnalyzer a 50MB
manager.component_limiter.component_limits['SmartMoneyAnalyzer'] = 50.0
```

## 📊 MONITOREO

### Obtener Estado
```python
from scripts.ict_memory_manager import get_memory_status

status = get_memory_status()
print(f"Memoria: {status['system_memory']['rss_mb']:.1f}MB")
print(f"Estado: {status['status']}")
```

### Logs Automáticos
El sistema registra automáticamente en el SmartTradingLogger:
- Warnings cuando memoria > 70%
- Críticos cuando memoria > 85%
- Eventos de cleanup y optimización

## ⚡ LAZY LOADING

### Uso Manual
```python
from scripts.lazy_loader import get_lazy_smart_money_analyzer

# Solo se carga cuando se accede realmente
sma = get_lazy_smart_money_analyzer()
result = sma.analyze_market_structure(data)  # Aquí se carga
```

### Verificación
```python
from scripts.lazy_loader import get_lazy_loader_status

status = get_lazy_loader_status()
print("Módulos cargados:", status)
```

## 🧹 LIMPIEZA MANUAL

### Cleanup Inmediato
```python
from scripts.ict_memory_manager import get_ict_memory_manager

manager = get_ict_memory_manager()
result = manager.perform_intelligent_cleanup()
print(f"Liberado: {result['freed_mb']:.1f}MB")
```

### Descargar Módulo Específico
```python
from scripts.lazy_loader import get_lazy_smart_money_analyzer

sma = get_lazy_smart_money_analyzer()
sma.unload()  # Libera memoria inmediatamente
```

## 📈 INTEGRACIÓN CON TRADING

### En main.py
```python
# Al inicio del sistema
from scripts.ict_memory_manager import start_ict_memory_management
memory_manager = start_ict_memory_management()

# Durante trading, usar lazy loading
from scripts.lazy_loader import get_lazy_smart_money_analyzer
analyzer = get_lazy_smart_money_analyzer()

# El sistema se gestiona automáticamente
```

### Con Dashboard
```python
# En dashboard startup
from scripts.ict_memory_manager import get_memory_status

def get_memory_widget_data():
    status = get_memory_status()
    return {
        'memory_mb': status['system_memory']['rss_mb'],
        'memory_percent': status['system_memory']['percent'],
        'status': status['status'],
        'cleanups': status['cleanup_stats']['total_cleanups']
    }
```

## ⚠️ TROUBLESHOOTING

### Memoria sigue alta
1. Verificar que el sistema esté activo:
```python
from scripts.ict_memory_manager import get_ict_memory_manager
manager = get_ict_memory_manager()
print("Monitoreo activo:", manager.monitoring)
```

2. Forzar cleanup manual:
```python
manager.perform_intelligent_cleanup()
```

3. Revisar límites:
```python
print(manager.component_limiter.component_limits)
```

### Módulos no se descargan
```python
from scripts.lazy_loader import check_memory_usage
check_memory_usage()  # Fuerza verificación
```

### Logs no aparecen
Verificar que SmartTradingLogger esté disponible:
```python
try:
    from smart_trading_logger import SmartTradingLogger
    logger = SmartTradingLogger('MemoryTest')
    logger.info("Test de memoria", component='TEST')
    print("✅ Logging funcional")
except Exception as e:
    print(f"⚠️ Error en logging: {e}")
```

## 📋 MEJORES PRÁCTICAS

1. **Siempre usar lazy loading** para componentes pesados
2. **Iniciar memory manager** al arranque del sistema  
3. **Monitorear logs** para warnings de memoria
4. **Ajustar límites** según el hardware disponible
5. **Usar cleanup manual** solo para debugging

---

*Sistema de Memoria ICT Engine v6.0 Enterprise*  
*Optimizado para trading en producción*