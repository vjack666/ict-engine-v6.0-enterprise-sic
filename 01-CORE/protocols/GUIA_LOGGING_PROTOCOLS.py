#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📋 GUÍA DE PROTOCOLOS DE LOGGING CENTRAL - ICT ENGINE v6.0 ENTERPRISE
=====================================================================

Guía completa para implementar y mantener protocolos de logging centralizado
en todo el sistema ICT Engine v6.0 Enterprise.

Autor: ICT Engine v6.0 Team
Fecha: 13 Septiembre 2025
"""

# =====================================
# 1. IMPORTACIÓN DE PROTOCOLOS
# =====================================

"""
PATRÓN ESTÁNDAR DE IMPORTACIÓN:

```python
# Importar protocolos de logging central
try:
    from ..protocols import setup_module_logging, LogLevel, EnterpriseLoggerProtocol
    PROTOCOLS_AVAILABLE = True
except ImportError:
    PROTOCOLS_AVAILABLE = False
    setup_module_logging = None
    LogLevel = None

# Importar logging estándar SIEMPRE
import logging

# Fallback tradicional SmartTradingLogger
try:
    from ..smart_trading_logger import SmartTradingLogger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False
    SmartTradingLogger = None
```

IMPORTANTE: Siempre declara variables fallback como None para evitar "possibly unbound"
"""

# =====================================
# 2. INICIALIZACIÓN EN __INIT__
# =====================================

"""
PATRÓN DE INICIALIZACIÓN DE LOGGER:

```python
def __init__(self, config=None):
    # ... otros parámetros ...
    
    # Configurar logger usando protocolos centrales
    if PROTOCOLS_AVAILABLE and setup_module_logging and LogLevel:
        self.logger = setup_module_logging("ComponentName", LogLevel.INFO)
    elif LOGGER_AVAILABLE and SmartTradingLogger:
        self.logger = SmartTradingLogger("ComponentName")
    else:
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("ComponentName")
    
    # Logging inicial seguro
    self._safe_log("info", "ComponentName inicializado")
```
"""

# =====================================
# 3. MÉTODO _safe_log OBLIGATORIO
# =====================================

"""
TODO MÓDULO DEBE INCLUIR ESTE MÉTODO:

```python
def _safe_log(self, level: str, message: str):
    \"\"\"Método seguro para logging con fallbacks\"\"\"
    try:
        if PROTOCOLS_AVAILABLE and setup_module_logging and LogLevel:
            getattr(self.logger, level)(message, "ComponentName")
        elif LOGGER_AVAILABLE and hasattr(self.logger, level):
            try:
                # Probar con 2 parámetros (SmartTradingLogger)
                getattr(self.logger, level)(message, "ComponentName")
            except TypeError:
                # Fallback a 1 parámetro (logging estándar)
                getattr(self.logger, level)(f"[ComponentName] {message}")
        else:
            print(f"[{level.upper()}] [ComponentName] {message}")
    except Exception:
        print(f"[{level.upper()}] [ComponentName] {message}")
```
"""

# =====================================
# 4. USO EN MÉTODOS
# =====================================

"""
EN LUGAR DE:
- self.logger.info("mensaje") 
- self.logger.error("error", "component")

USA SIEMPRE:
- self._safe_log("info", "mensaje")
- self._safe_log("error", "error descripción")

EJEMPLO:
```python
def some_method(self):
    try:
        # Lógica del método
        self._safe_log("info", "Operación completada exitosamente")
    except Exception as e:
        self._safe_log("error", f"Error en operación: {e}")
```
"""

# =====================================
# 5. EVITAR "POSSIBLY UNBOUND"
# =====================================

"""
PROBLEMA COMÚN:
```python
# MALO - puede causar "possibly unbound"
try:
    data = get_some_data()
except Exception:
    pass

# Usar data aquí causa error
if data:  # ERROR: possibly unbound
    process_data(data)
```

SOLUCIÓN:
```python
# BUENO - inicializar siempre antes del try
data = None  # o valor por defecto apropiado

try:
    data = get_some_data()
except Exception as e:
    self._safe_log("error", f"Error obteniendo data: {e}")
    data = default_data()  # valor fallback

# Ahora data está garantizado que existe
if data:
    process_data(data)
```
"""

# =====================================
# 6. ESTRUCTURA DE ARCHIVOS
# =====================================

"""
ESTRUCTURA REQUERIDA:

01-CORE/
├── protocols/
│   ├── __init__.py                    # Exports de protocolos
│   └── logging_central_protocols.py   # Implementación
├── component/
│   ├── __init__.py                    # Exports con protocolo
│   └── component_module.py            # Usa protocolos
"""

# =====================================
# 7. EXPORTS EN __init__.py
# =====================================

"""
TODO __init__.py DEBE SEGUIR ESTE PATRÓN:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Module initialization following logging protocols.
\"\"\"

try:
    from .module_implementation import MainClass, HelperClass
    # Otras importaciones...
    
    __all__ = [
        'MainClass',
        'HelperClass',
        # Otros exports...
    ]
    
except ImportError as e:
    # Logging de error de importación
    print(f"[WARNING] [ModuleName] Import error: {e}")
    __all__ = []
```
"""

# =====================================
# 8. VALIDACIÓN Y TESTING
# =====================================

"""
SIEMPRE INCLUIR EN TESTING:

```python
def test_logging_integration():
    \"\"\"Test de integración con protocolos de logging\"\"\"
    from protocols.logging_central_protocols import ProtocolValidator
    
    component = YourComponent()
    
    # Validar cumplimiento de protocolo
    is_compliant = ProtocolValidator.validate_logger_implementation(component.logger)
    assert is_compliant, "Logger no cumple con protocolos"
    
    # Test de logging
    component._safe_log("info", "Test message")
    component._safe_log("warning", "Test warning")
    component._safe_log("error", "Test error")
```
"""

# =====================================
# 9. CHECKLIST DE IMPLEMENTACIÓN
# =====================================

"""
✅ CHECKLIST OBLIGATORIO:

□ Importación de protocolos con fallbacks
□ Variables fallback definidas como None
□ Método _safe_log implementado
□ Inicialización de logger en __init__
□ Uso exclusivo de _safe_log para logging
□ Variables inicializadas antes de try/except
□ __init__.py actualizado con exports
□ Tests de protocolos incluidos
□ Sin errores Pylance "possibly unbound"
□ Documentación actualizada
"""

# =====================================
# 10. MIGRACIÓN DE MÓDULOS EXISTENTES
# =====================================

"""
PASOS PARA MIGRAR MÓDULO EXISTENTE:

1. Agregar importación de protocolos al inicio
2. Modificar __init__ para usar setup_module_logging
3. Agregar método _safe_log
4. Reemplazar todas las llamadas directas a logger
5. Inicializar variables antes de try/except
6. Actualizar __init__.py del paquete
7. Ejecutar tests y verificar sin errores Pylance
8. Documentar cambios realizados
"""

# =====================================
# 11. TROUBLESHOOTING COMÚN
# =====================================

"""
PROBLEMAS FRECUENTES Y SOLUCIONES:

1. "possibly unbound" en variables:
   - Inicializar SIEMPRE antes del try/except
   - Usar valores por defecto apropiados

2. "Argument missing for parameter 'component'":
   - Usar _safe_log en lugar de logger directo
   - Verificar que SmartTradingLogger esté correctamente importado

3. Imports no resueltos:
   - Verificar estructura de carpetas
   - Actualizar __init__.py con exports correctos
   - Usar importaciones relativas apropiadas

4. Logger no funciona:
   - Verificar disponibilidad de protocolos
   - Confirmar fallbacks configurados
   - Revisar inicialización en __init__
"""

print("📋 Guía de Protocolos de Logging Central - ICT Engine v6.0")
print("Usar esta guía para mantener consistencia en todo el sistema")
print("Actualizado: 13 Septiembre 2025")