# 📊 MONITOREO DE PRODUCCIÓN - ICT ENGINE v6.0 ENTERPRISE

## 🎯 Resumen

Se han implementado exitosamente dos módulos críticos de monitoreo de producción que complementan el sistema existente de Health Monitor, proporcionando supervisión completa del sistema en tiempo real para cuentas reales de trading.

> ✅ NOTA IMPORTANTE (UI / Dashboard)
> A partir de la versión actual se eliminó completamente la interfaz Web (Dash/Plotly). Solo se mantiene un único "monoboard" / dashboard en terminal con estilizado (colores/CSS interno simple) suficiente para operación y monitoreo. Cualquier referencia previa a `web_dashboard.py`, `start_web_dashboard.py` o acceso vía navegador ha quedado deprecada y no debe usarse en producción.

Resumen de cambios UI:
- Eliminado: Web dashboard (servidor HTTP, tabs gráficas, dependencias Dash/Plotly)
- Conservado: Dashboard terminal integrado (menú principal opción monitoreo y vistas en texto enriquecido)
- Objetivo: Reducir superficie operativa, complejidad de dependencias y puntos de fallo en producción.
- Seguridad: Sin puerto expuesto; todo monitoreo ocurre dentro del proceso controlado.

---

## 🚀 Módulos Implementados

### 1. Production System Monitor (`production_system_monitor.py`)
**📍 Ubicación:** `01-CORE/monitoring/production_system_monitor.py`

**Funcionalidades:**
- [x] Monitoreo de recursos del sistema (CPU, RAM, Disco)
- [x] Seguimiento de conexiones de red activas
- [x] Conteo de procesos en ejecución
- [x] Evaluación automática de salud del sistema
- [x] Sistema de alertas por umbrales configurables
- [x] Persistencia de métricas en archivos JSON
- [x] Integración completa con logging central

**Estados de Salud:**
- `EXCELLENT`: Sistema operando de forma óptima (≥90% puntuación)
- `GOOD`: Funcionamiento normal con reservas (75-89%)
- `WARNING`: Degradación detectada, atención requerida (50-74%)
- `CRITICAL`: Estado crítico, intervención inmediata (<50%)

### 2. Production Performance Monitor (`production_performance_monitor.py`)
**📍 Ubicación:** `01-CORE/monitoring/production_performance_monitor.py`

**Funcionalidades:**
- [x] Medición de latencia en tiempo real (P95, P99, promedio)
- [x] Seguimiento de throughput (operaciones por segundo)
- [x] Tasa de error por componente
- [x] Análisis de performance por componente individual
- [x] Sistema de ventanas deslizantes para métricas
- [x] Alertas automáticas por degradación de performance
- [x] Decorador para medición automática de operaciones

**Estados de Performance:**
- `OPTIMAL`: Performance excelente (≥90% puntuación)
- `GOOD`: Performance aceptable (70-89%)
- `DEGRADED`: Performance degradada (40-69%)
- `CRITICAL`: Performance crítica (<40%)

---

## 🔧 Integración con Main.py

### Nuevo Menú Principal
Se agregó la **Opción 4: 📊 [MONITOREO] Sistema de Monitoreo de Producción** al menú principal del sistema.

### Métodos Implementados

#### `run_production_monitoring()`
Método principal que orquesta el inicio de todos los monitores de producción.

#### `_start_health_monitor()`
Inicializa el Health Monitor existente del sistema.

#### `_start_system_monitor()`  
Inicializa el nuevo Production System Monitor.

#### `_start_performance_monitor()`
Inicializa el nuevo Production Performance Monitor.

#### `_display_monitoring_summary()`
Muestra resumen visual del estado de todos los monitores.

---

## 📋 Configuración

### System Monitor - Configuración por Defecto
```python
{
    'monitoring_interval': 5.0,  # segundos entre muestras
    'metrics_history_size': 1000,  # número de muestras a mantener
    'thresholds': {
        'cpu_warning': 70.0,      # % CPU para alerta warning
        'cpu_critical': 90.0,     # % CPU para alerta crítica
        'memory_warning': 80.0,   # % RAM para alerta warning
        'memory_critical': 95.0,  # % RAM para alerta crítica
        'disk_warning': 85.0,     # % Disco para alerta warning
        'disk_critical': 95.0,    # % Disco para alerta crítica
    },
    'persist_metrics': True,      # guardar métricas en archivo
    'max_alerts': 500            # máximo número de alertas a mantener
}
```

### Performance Monitor - Configuración por Defecto
```python
{
    'snapshot_interval': 10.0,   # segundos entre snapshots
    'history_size': 500,         # snapshots a mantener
    'component_window_size': 1000, # muestras por componente
    'thresholds': {
        'latency_warning_ms': 100.0,    # latencia warning en ms
        'latency_critical_ms': 500.0,   # latencia crítica en ms
        'error_rate_warning': 1.0,      # % tasa error warning
        'error_rate_critical': 5.0,     # % tasa error crítica
        'throughput_min_ops_sec': 10.0, # mínimo throughput
        'response_time_p95_ms': 200.0,  # P95 máximo aceptable
    },
    'auto_create_components': True, # auto-crear trackers
    'persist_snapshots': True,      # persistir snapshots
    'max_alerts': 200              # máximo alertas
}
```

---

## 💻 Ejemplos de Uso

### 1. Uso Básico - Sistema Monitor
```python
from monitoring.production_system_monitor import ProductionSystemMonitor

# Crear monitor
monitor = ProductionSystemMonitor()

# Iniciar monitoreo
monitor.start_monitoring()

# Obtener estado actual
status = monitor.get_current_status()
print(f"CPU: {status['cpu_percent']}% | RAM: {status['memory_percent']}%")

# Detener
monitor.stop_monitoring()
```

### 2. Uso Básico - Performance Monitor
```python
from monitoring.production_performance_monitor import ProductionPerformanceMonitor

# Crear monitor
monitor = ProductionPerformanceMonitor()

# Iniciar monitoreo
monitor.start_monitoring()

# Registrar operación
monitor.record_operation("TradingEngine", "execute_order", 45.2, True)

# Obtener performance actual
perf = monitor.get_current_performance()
print(f"Latencia P95: {perf['p95_latency_ms']}ms")
```

### 3. Decorador para Medición Automática
```python
from monitoring.production_performance_monitor import time_operation

monitor = ProductionPerformanceMonitor()

@time_operation(monitor, "DataProcessor", "process_candles")
def process_market_data(data):
    # Tu código aquí
    return processed_data
```

### 4. Callbacks para Alertas
```python
def alert_handler(alert):
    if alert.severity == 'critical':
        send_emergency_notification(alert.message)
    
monitor.add_alert_callback(alert_handler)
```

---

## 📊 Archivos de Salida

### Métricas del Sistema
- **📍 Ubicación:** `data/system_metrics.json`
- **📝 Contenido:** Métricas de CPU, RAM, Disco por timestamp
- **🔄 Frecuencia:** Cada 5 segundos (configurable)

### Métricas de Performance  
- **📍 Ubicación:** `data/performance_metrics.json`
- **📝 Contenido:** Snapshots de latencia, throughput, errores
- **🔄 Frecuencia:** Cada 10 segundos (configurable)

### Alertas del Sistema
- **📍 Ubicación:** `data/system_alerts.json`
- **📝 Contenido:** Histórico de alertas con timestamps y severidad

---

## 🔍 Monitoreo en el Dashboard

### Opción 4 del Menú Principal
Al seleccionar la opción 4, el sistema:

1. ✅ **Inicia Health Monitor** - Monitor de salud existente
2. ✅ **Inicia System Monitor** - Nuevo monitor de recursos
3. ✅ **Inicia Performance Monitor** - Nuevo monitor de performance
4. ✅ **Muestra Resumen** - Estado de todos los monitores

### Salida Ejemplo
```
============================================================
🚀 RESUMEN DEL SISTEMA DE MONITOREO DE PRODUCCIÓN
============================================================
✅ Health Monitor: ACTIVO
✅ System Monitor: ACTIVO  
✅ Performance Monitor: ACTIVO
============================================================
```

---

## 🛡️ Características de Producción

### ✅ Logging Central Integrado
- Todos los módulos usan `protocols/logging_central_protocols.py`
- Logs estructurados con componente y nivel
- Fallback automático si logging no está disponible

### ✅ Manejo Robusto de Errores
- Try-catch en todas las operaciones críticas
- Degradación graceful ante fallos
- Logging de errores con contexto completo

### ✅ Threading Seguro
- Monitores ejecutan en threads separados
- Stop events para terminación limpia
- Timeouts configurables

### ✅ Configuración Flexible
- Configuración via diccionarios Python
- Umbrales ajustables por entorno
- Intervalos de monitoreo configurables

### ✅ Persistencia de Datos
- Métricas guardadas automáticamente
- Formato JSON para fácil análisis
- Rotación automática de archivos

---

## 🚨 Sistema de Alertas

### Niveles de Severidad
- **INFO**: Información general
- **WARNING**: Situación que requiere atención
- **CRITICAL**: Situación crítica que requiere acción inmediata

### Tipos de Alertas

#### System Monitor
- CPU usage > threshold
- Memory usage > threshold  
- Disk usage > threshold
- Network connectivity issues

#### Performance Monitor
- Latency P95 > threshold
- Error rate > threshold
- Throughput < minimum
- Component performance degradation

---

## 📈 Métricas Clave

### Sistema
- **CPU %**: Porcentaje de uso de CPU
- **Memory %**: Porcentaje de uso de RAM  
- **Disk %**: Porcentaje de uso de disco
- **Connections**: Número de conexiones activas
- **Processes**: Número de procesos en ejecución
- **Uptime**: Tiempo de actividad del sistema

### Performance
- **Avg Latency**: Latencia promedio en ms
- **P95 Latency**: Percentil 95 de latencia
- **P99 Latency**: Percentil 99 de latencia
- **Throughput**: Operaciones por segundo
- **Error Rate**: Porcentaje de errores
- **Component Status**: Estado por componente

---

## 🔧 Solución de Problemas

### Monitor No Inicia
```python
# Verificar paths
import sys
from pathlib import Path
CORE_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(CORE_PATH))

# Verificar logging
try:
    from protocols.logging_central_protocols import setup_module_logging
    logger = setup_module_logging("Test", "INFO")
    print("✅ Logging disponible")
except ImportError:
    print("❌ Logging no disponible")
```

### Importación Falla
```python
# Verificar ubicación de archivos
from pathlib import Path
monitor_path = Path("01-CORE/monitoring/production_system_monitor.py")
print(f"Existe: {monitor_path.exists()}")

# Verificar dependencias
import psutil
print(f"psutil version: {psutil.__version__}")
```

### Performance Baja
```python
# Ajustar intervalos
config = {
    'monitoring_interval': 10.0,  # reducir frecuencia
    'history_size': 100,          # reducir historial
    'component_window_size': 500  # reducir ventana
}
```

---

## ✅ Estado Actual

### ✅ **Completado Exitosamente**
1. [x] Production System Monitor implementado y probado
2. [x] Production Performance Monitor implementado y probado  
3. [x] Integración con main.py completada
4. [x] Logging central integrado en todos los módulos
5. [x] Menú principal actualizado con nueva opción
6. [x] Sistema probado sin errores de Pylance/tipo
7. [x] Documentación completa creada

### 🚀 **Sistema Listo para Producción**
- No hay errores de tipo/Pylance
- Todos los módulos usan logging central
- Integración completa con arquitectura existente
- Pruebas exitosas en entorno real
- Configuración optimizada para trading

---

## 📞 Soporte y Mantenimiento

### Archivos Críticos
- `01-CORE/monitoring/production_system_monitor.py`
- `01-CORE/monitoring/production_performance_monitor.py`
- `main.py` (métodos de monitoreo agregados)
- `protocols/logging_central_protocols.py` (logging central)

### Logs de Monitoreo
- Health Monitor: `05-LOGS/health_monitoring/`
- System Metrics: `data/system_metrics.json`
- Performance Metrics: `data/performance_metrics.json`

### Contacto
- 📧 Sistema: ICT Engine v6.0 Enterprise
- 📅 Fecha: 15 Septiembre 2025
- 🏷️ Versión: Production Ready v1.0

---

**🎯 Los módulos de monitoreo de producción están completamente implementados, integrados y listos para uso en cuentas reales de trading.**