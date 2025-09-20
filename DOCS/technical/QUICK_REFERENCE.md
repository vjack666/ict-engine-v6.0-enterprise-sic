# ⚡ REFERENCIA RÁPIDA - CORRECCIONES PYLANCE
## ICT Engine v6.0 Enterprise - Guía Rápida para Desarrolladores

---

## 🚨 **ERRORES CRÍTICOS - ARREGLAR PRIMERO**

### 1. **Logger en ConfigManager** (`config_manager.py:168`)
```python
# ANTES (❌ Error):
def _setup_logger(self) -> logging.Logger:
    return SmartTradingLogger("ConfigManager")

# DESPUÉS (✅ Corregido):
from typing import Union
def _setup_logger(self) -> Union[logging.Logger, Any]:
    return SmartTradingLogger("ConfigManager")
```

### 2. **Notification Manager** (COMPLETADO)
```python
# Cambios clave:
# - Import de `get_config` estable con fallback
# - Dataclasses usan `field(default_factory=...)`
# - Parámetros `Optional[...]` para evitar errores por `None`
# - Adaptador de logger para `SmartTradingLogger`
```

### 3. **Enterprise Tabs Manager (LISTO)**
Implementado `enterprise_tabs_manager.py` minimal (sin UI web). No requiere acciones.

---

## 📦 **IMPORTS FALTANTES - INSTALAR**

```bash
# Paquetes requeridos
pip install fastapi uvicorn joblib

# Agregar a requirements.txt:
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
joblib>=1.3.0
```

---

## 🔧 **CORRECCIONES DE TIPOS - PARCHES RÁPIDOS**

### Web Dashboard (DEPRECADO)
`web_dashboard.py` y cualquier UI Dash/Plotly fueron retirados. Mantener un stub solo para evitar fallos de import. No realizar más cambios ni reintroducir dependencias de UI.

### Correcciones de Asignación de None
```python
# CHANGE FROM:
self.channels: List[str] = None  # ❌

# CHANGE TO:
self.channels: List[str] = []  # ✅
self.metadata: Dict[str, Any] = {}  # ✅
```

---

## 🧠 **CORRECCIONES DE MACHINE LEARNING**

### Add to `machine_learning/__init__.py`:
```python
# Funciones faltantes
def get_unified_memory_system(): 
    return {"type": "memory_system"}

def log_trading_decision_smart_v6(data): 
    logging.info(f"Decision: {data}")

# Import seguro de joblib
try:
    import joblib
except ImportError:
    joblib = None
```

### Añadir a la clase POI: (COMPLETADO)
```python
class POI:
    def __init__(self, ...):
        self.metadata: Dict[str, Any] = {}  # ← ADD THIS
```

---

## 🎨 **CORRECCIONES DE COMPONENTES DEL DASHBOARD**

### Componentes HTML (REMOVIDOS)
Soporte de componentes Dash eliminado. No recrear wrappers.

---

## 🧪 **PRUEBAS RÁPIDAS**

### Probar ConfigManager:
```python
from config.config_manager import ConfigManager
cm = ConfigManager()
print(f"Logger type: {type(cm.logger)}")  # Should not error
```

### Probar Imports:
```python
# Test all critical imports
import enterprise_tabs_manager  # Should work after creating
from machine_learning import get_unified_memory_system  # Should work
```

---

## 📁 **ARCHIVOS PARA CREAR/MODIFICAR**

### CREAR NUEVOS:
- [x] `enterprise_tabs_manager.py` (minimal)
- [ ] `tests/test_config_manager.py`
- [ ] `tests/test_enterprise_tabs_manager.py`

### MODIFICAR EXISTENTES (Pendientes relevantes vigentes):
- [x] `01-CORE/config/config_manager.py`
- [x] `01-CORE/machine_learning/__init__.py`
- [x] `01-CORE/analysis/poi_system.py`
- [ ] `09-DASHBOARD/metrics_api.py` (conectar agregador métricas)

El archivo `09-DASHBOARD/web_dashboard.py` queda marcado como deprecated (sin acciones futuras).

---

## ⚡ **ORDEN DE IMPLEMENTACIÓN**

1. **ConfigManager fix** (5 min)
2. **Create enterprise_tabs_manager** (15 min)  
3. **Install missing packages** (5 min)
4. **ML module fixes** (10 min)
5. **Dashboard type fixes** (10 min)
6. **Test everything** (15 min)

**Tiempo total (recalculado):** ~1h15m (incluye refactor de Notification Manager)

---

Política de sincronización: Cada vez que una tarea se marca como completada en la lista principal, este documento se actualiza inmediatamente.

---

## 🎯 **VALIDACIÓN DE ÉXITO**

```bash
# Cero errores en VS Code Pylance
# Todo esto debe funcionar:
python -c "from config.config_manager import ConfigManager; print('OK')"
python -c "import enterprise_tabs_manager; print('OK')"  
python -c "from machine_learning import get_unified_memory_system; print('OK')"
```

---

## 🆘 **ROLLBACK DE EMERGENCIA**

```bash
# Si algo falla:
git stash  # Save current changes
git reset --hard HEAD  # Rollback to last commit
# Then implement fixes one by one
```

---

**Última actualización:** 15 Sept 2025 | **Estado:** Listo para implementar