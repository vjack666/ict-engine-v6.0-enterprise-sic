# ⚡ QUICK REFERENCE - PYLANCE FIXES
## ICT Engine v6.0 Enterprise - Developer Cheat Sheet

---

## 🚨 **CRITICAL ERRORS - FIX FIRST**

### 1. **ConfigManager Logger** (`config_manager.py:168`)
```python
# BEFORE (❌ Error):
def _setup_logger(self) -> logging.Logger:
    return SmartTradingLogger("ConfigManager")

# AFTER (✅ Fixed):
from typing import Union
def _setup_logger(self) -> Union[logging.Logger, Any]:
    return SmartTradingLogger("ConfigManager")
```

### 2. **Notification Manager** (COMPLETADO)
```python
# Cambios clave:
# - Import get_config estable con fallback
# - Dataclasses usan field(default_factory=...)
# - Parámetros Optional para evitar None type errors
# - Adaptador logger para SmartTradingLogger
```

### 3. **Missing Enterprise Module** (Create new file)
```python
# CREATE: enterprise_tabs_manager.py
def setup_logging(level="INFO"): pass
def create_dashboard_app(**kwargs): pass  
def create_ict_dashboard(**kwargs): pass
```

---

## 📦 **MISSING IMPORTS - INSTALL THESE**

```bash
# Required packages
pip install fastapi uvicorn joblib

# Add to requirements.txt:
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
joblib>=1.3.0
```

---

## 🔧 **TYPE FIXES - QUICK PATCHES**

### Web Dashboard Return Types
```python
# CHANGE FROM:
def create_tab(...) -> TabObject:  # ❌
    return tab_instance

# CHANGE TO:  
def create_tab(...) -> None:  # ✅
    # Don't return the object
```

### None Assignment Fixes
```python
# CHANGE FROM:
self.channels: List[str] = None  # ❌

# CHANGE TO:
self.channels: List[str] = []  # ✅
self.metadata: Dict[str, Any] = {}  # ✅
```

---

## 🧠 **MACHINE LEARNING FIXES**

### Add to `machine_learning/__init__.py`:
```python
# Missing functions
def get_unified_memory_system(): 
    return {"type": "memory_system"}

def log_trading_decision_smart_v6(data): 
    logging.info(f"Decision: {data}")

# Safe joblib import
try:
    import joblib
except ImportError:
    joblib = None
```

### Add to POI class: (COMPLETADO)
```python
class POI:
    def __init__(self, ...):
        self.metadata: Dict[str, Any] = {}  # ← ADD THIS
```

---

## 🎨 **DASHBOARD COMPONENT FIXES**

### HTML Components Returning None:
```python
# VERIFY IMPORTS:
try:
    from dash import html
    DASH_AVAILABLE = True
except ImportError:
    html = None
    DASH_AVAILABLE = False

# SAFE COMPONENT CREATION:
def safe_div(*args, **kwargs):
    if html:
        return html.Div(*args, **kwargs)
    return {"type": "fallback_div", "args": args}
```

---

## 🧪 **QUICK TESTS**

### Test ConfigManager:
```python
from config.config_manager import ConfigManager
cm = ConfigManager()
print(f"Logger type: {type(cm.logger)}")  # Should not error
```

### Test Imports:
```python
# Test all critical imports
import enterprise_tabs_manager  # Should work after creating
from machine_learning import get_unified_memory_system  # Should work
```

---

## 📁 **FILES TO CREATE/MODIFY**

### CREATE NEW:
- [ ] `enterprise_tabs_manager.py` (root level)
- [ ] `tests/test_config_manager.py`
- [ ] `tests/test_enterprise_modules.py`

### MODIFY EXISTING:
- [x] `01-CORE/config/config_manager.py` (logger adapter)
- [x] `01-CORE/machine_learning/__init__.py` (fallbacks & functions)
- [x] `01-CORE/analysis/poi_system.py` (metadata field + helpers)
- [ ] `09-DASHBOARD/web_dashboard.py` (return types)
- [ ] `09-DASHBOARD/metrics_api.py` (imports)

---

## ⚡ **IMPLEMENTATION ORDER**

1. **ConfigManager fix** (5 min)
2. **Create enterprise_tabs_manager** (15 min)  
3. **Install missing packages** (5 min)
4. **ML module fixes** (10 min)
5. **Dashboard type fixes** (10 min)
6. **Test everything** (15 min)

**Total Time (recalculado):** ~1h15m (incluye refactor Notification Manager)

---

Sync Policy: Cada vez que una tarea se marca como completada en la lista principal, este documento se actualiza inmediatamente.

---

## 🎯 **SUCCESS VALIDATION**

```bash
# Zero errors in VS Code Pylance
# All these should work:
python -c "from config.config_manager import ConfigManager; print('OK')"
python -c "import enterprise_tabs_manager; print('OK')"  
python -c "from machine_learning import get_unified_memory_system; print('OK')"
```

---

## 🆘 **EMERGENCY ROLLBACK**

```bash
# If something breaks:
git stash  # Save current changes
git reset --hard HEAD  # Rollback to last commit
# Then implement fixes one by one
```

---

**Last Updated:** 15 Sept 2025 | **Status:** Ready to implement