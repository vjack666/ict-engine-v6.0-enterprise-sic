# 🧪 PROTOCOLO DE RESOLUCIÓN DE PROBLEMAS

**Archivo:** `08-troubleshooting.md`  
**Propósito:** Guía estructurada para resolución de problemas comunes en ICT Engine v6.0

---

## 🚨 **CLASIFICACIÓN DE PROBLEMAS**

### **⚡ CRÍTICOS (Resolver Inmediatamente)**
- Sistema no arranca / imports fallan
- Pérdida de datos o corrupción
- Performance <50% del baseline
- SIC/SLUC completamente no funcional
- Tests core fallando >80%

### **🔶 ALTOS (Resolver en <2 horas)**
- Funcionalidad enterprise parcialmente no funcional
- Memory leaks detectados
- Performance 50-80% del baseline
- Integration tests fallando
- Logging/configuración problemática

### **🔸 MEDIOS (Resolver en <1 día)**
- Features específicos no funcionando
- Performance 80-90% del baseline
- Unit tests fallando <20%
- Documentación inconsistente
- Warnings en producción

### **🔹 BAJOS (Resolver cuando sea posible)**
- Optimizaciones de código
- Mejoras de UX
- Documentación menor
- Refactoring no crítico

---

## 🔧 **DIAGNOSTIC PROTOCOLS**

### **📊 DIAGNOSTIC RÁPIDO (2 minutos)**

```bash
#!/bin/bash
echo "🩺 ICT ENGINE v6.0 - DIAGNOSTIC RÁPIDO"
echo "====================================="

# 1. ESTRUCTURA BÁSICA
echo "📂 ESTRUCTURA:"
echo "  Core: $(ls core/ 2>/dev/null | wc -l) items"
echo "  Sistema: $(ls sistema/ 2>/dev/null | wc -l) items"
echo "  Tests: $(ls tests/ 2>/dev/null | wc -l) items"
echo "  Logs: $(ls logs/ 2>/dev/null | wc -l) items"

# 2. IMPORTS CRÍTICOS
echo "🔧 IMPORTS CRÍTICOS:"
python -c "
import sys
try:
    from sistema.sic_bridge import SICBridge
    print('  ✅ SIC Bridge')
except Exception as e:
    print(f'  ❌ SIC Bridge: {e}')
    
try:
    from core.smart_trading_logger import SmartTradingLogger
    print('  ✅ SLUC Logger')
except Exception as e:
    print(f'  ❌ SLUC Logger: {e}')
    
try:
    import pandas as pd
    import numpy as np
    print('  ✅ Data Libraries')
except Exception as e:
    print(f'  ❌ Data Libraries: {e}')
" 2>/dev/null

# 3. CONFIGURACIÓN
echo "⚙️ CONFIGURACIÓN:"
if [ -f "config/sic_cache_stats.json" ]; then
    echo "  ✅ SIC Cache disponible"
else
    echo "  ⚠️ SIC Cache no encontrado"
fi

# 4. LOGS RECIENTES
echo "📅 ACTIVIDAD RECIENTE:"
if [ -d "logs/" ]; then
    recent_log=$(ls -t logs/*.log 2>/dev/null | head -1)
    if [ -n "$recent_log" ]; then
        echo "  📄 Último log: $(basename $recent_log)"
        echo "  📅 Última línea: $(tail -1 $recent_log 2>/dev/null | cut -c1-50)..."
    else
        echo "  ⚠️ No hay logs recientes"
    fi
else
    echo "  ❌ Directorio logs no encontrado"
fi

# 5. PERFORMANCE CHECK
echo "⚡ PERFORMANCE:"
python -c "
import time
start = time.time()
sum(range(10000))
elapsed = time.time() - start
print(f'  🕐 Basic test: {elapsed:.4f}s')
if elapsed < 0.1:
    print('  ✅ Performance OK')
else:
    print('  ⚠️ Performance concern')
" 2>/dev/null

echo "====================================="
echo "🎯 Diagnostic completado"
```

### **🔍 DIAGNOSTIC PROFUNDO (5 minutos)**

```bash
#!/bin/bash
echo "🔬 ICT ENGINE v6.0 - DIAGNOSTIC PROFUNDO"
echo "========================================"

# 1. SYSTEM INFO
echo "💻 SYSTEM INFO:"
echo "  OS: $(uname -s 2>/dev/null || echo 'Windows')"
echo "  Python: $(python --version 2>/dev/null || echo 'Not found')"
echo "  Memory: $(python -c 'import psutil; print(f"{psutil.virtual_memory().percent}% used")' 2>/dev/null || echo 'N/A')"
echo "  CPU: $(python -c 'import psutil; print(f"{psutil.cpu_percent()}%")' 2>/dev/null || echo 'N/A')"

# 2. DEPENDENCY CHECK
echo "📦 DEPENDENCIES:"
python -c "
import pkg_resources
import sys

required = ['pandas', 'numpy', 'pytest', 'psutil']
for package in required:
    try:
        version = pkg_resources.get_distribution(package).version
        print(f'  ✅ {package}: {version}')
    except pkg_resources.DistributionNotFound:
        print(f'  ❌ {package}: Not installed')
" 2>/dev/null

# 3. FILE SYSTEM CHECK
echo "💾 FILE SYSTEM:"
echo "  Workspace size: $(du -sh . 2>/dev/null | cut -f1 || echo 'N/A')"
echo "  Free space: $(df -h . 2>/dev/null | tail -1 | awk '{print $4}' || echo 'N/A')"
echo "  Recent files: $(find . -type f -mtime -1 2>/dev/null | wc -l) modified today"

# 4. CODE QUALITY
echo "🎯 CODE QUALITY:"
python_files=$(find . -name "*.py" 2>/dev/null | wc -l)
echo "  Python files: $python_files"
if [ $python_files -gt 0 ]; then
    echo "  Syntax errors: $(python -m py_compile *.py 2>&1 | grep -c "SyntaxError" || echo 0)"
    echo "  TODOs: $(grep -r "TODO\|FIXME" . --include="*.py" 2>/dev/null | wc -l)"
fi

# 5. ENTERPRISE COMPONENTS
echo "🏗️ ENTERPRISE COMPONENTS:"
python -c "
components = [
    ('SICBridge', 'sistema.sic_bridge', 'SICBridge'),
    ('SmartTradingLogger', 'core.smart_trading_logger', 'SmartTradingLogger'),
    ('UnifiedMemorySystem', 'core.data_management.unified_memory_system', 'UnifiedMemorySystem'),
    ('POISystem', 'core.poi_system', 'POISystem')
]

for name, module, class_name in components:
    try:
        __import__(module)
        print(f'  ✅ {name}')
    except ImportError as e:
        print(f'  ❌ {name}: {e}')
    except Exception as e:
        print(f'  ⚠️ {name}: {e}')
" 2>/dev/null

# 6. NETWORK/EXTERNAL
echo "🌐 EXTERNAL DEPENDENCIES:"
python -c "
try:
    import socket
    socket.create_connection(('8.8.8.8', 53), timeout=3)
    print('  ✅ Internet connectivity')
except:
    print('  ⚠️ Internet connectivity issues')
    
# Check if MT5 terminal might be accessible (if needed)
import os
if os.path.exists('C:/Program Files/MetaTrader 5') or os.path.exists('/Applications/MetaTrader 5'):
    print('  ✅ MT5 installation detected')
else:
    print('  ℹ️ MT5 installation not detected')
" 2>/dev/null

echo "========================================"
echo "🎯 Diagnostic profundo completado"
```

---

## 🚨 **PROBLEMAS COMUNES Y SOLUCIONES**

### **❌ PROBLEMA: ImportError SIC/SLUC**

**SÍNTOMAS:**
```
ImportError: No module named 'sistema.sic_bridge'
ImportError: No module named 'core.smart_trading_logger'
```

**DIAGNOSTIC:**
```bash
# Verificar estructura
ls -la sistema/ core/
echo $PYTHONPATH
python -c "import sys; print('\n'.join(sys.path))"
```

**SOLUCIONES:**
```bash
# 1. Fix PYTHONPATH
export PYTHONPATH="$PWD:$PYTHONPATH"

# 2. Verificar archivos __init__.py
touch sistema/__init__.py
touch core/__init__.py

# 3. Re-instalar en modo development
pip install -e .

# 4. Test fix
python -c "from sistema.sic_bridge import SICBridge; print('✅ SIC OK')"
python -c "from core.smart_trading_logger import SmartTradingLogger; print('✅ SLUC OK')"
```

### **❌ PROBLEMA: Performance Degradation**

**SÍNTOMAS:**
- Operaciones >2x tiempo esperado
- Memory usage >200MB baseline
- CPU usage >80% sustained

**DIAGNOSTIC:**
```python
import time
import psutil
import tracemalloc

# Memory profiling
tracemalloc.start()

# Your operation here
start_time = time.time()
# ... operation ...
end_time = time.time()

current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"Time: {end_time - start_time:.4f}s")
print(f"Memory current: {current / 1024 / 1024:.2f}MB")
print(f"Memory peak: {peak / 1024 / 1024:.2f}MB")
print(f"CPU: {psutil.cpu_percent()}%")
```

**SOLUCIONES:**
```python
# 1. Optimize data structures
# Instead of: data = list(range(1000000))
# Use: data = np.arange(1000000)

# 2. Memory-efficient iteration
# Instead of: [process(x) for x in large_list]
# Use: (process(x) for x in large_list)

# 3. Cache frequently used data
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(param):
    # ... expensive computation ...
    return result

# 4. Use chunking for large datasets
def process_in_chunks(data, chunk_size=1000):
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        yield process_chunk(chunk)
```

### **❌ PROBLEMA: Test Failures**

**SÍNTOMAS:**
```
FAILED tests/test_integration.py::test_sic_integration
AssertionError: Expected logging call not found
```

**DIAGNOSTIC:**
```bash
# Run tests with verbose output
python -m pytest tests/ -v --tb=long

# Run specific failing test
python -m pytest tests/test_integration.py::test_sic_integration -v -s

# Check test coverage
python -m pytest tests/ --cov=core --cov=sistema --cov-report=html
```

**SOLUCIONES:**
```python
# 1. Fix mock configuration
@patch('core.smart_trading_logger.SmartTradingLogger')
def test_logging(mock_logger_class):
    mock_logger = mock_logger_class.return_value
    
    # Your test code
    
    # Verify calls correctly
    mock_logger.info.assert_called_with(
        "Expected message",
        component="ExpectedComponent"
    )

# 2. Use proper fixtures
@pytest.fixture
def sic_bridge():
    with patch('sistema.sic_bridge.SICBridge') as mock:
        mock.return_value.get_config.return_value = {"test": "value"}
        yield mock.return_value

# 3. Reset state between tests
def teardown_method(self):
    # Clear caches, reset singletons, etc.
    importlib.reload(module_under_test)
```

### **❌ PROBLEMA: Configuration Issues**

**SÍNTOMAS:**
- Config files not found
- Invalid configuration values
- SIC cache corruption

**DIAGNOSTIC:**
```bash
# Check config files
ls -la config/
cat config/sic_cache_stats.json 2>/dev/null || echo "SIC cache not found"

# Validate JSON
python -c "
import json
try:
    with open('config/ict_patterns_config.json') as f:
        config = json.load(f)
    print('✅ Config JSON valid')
    print(f'Keys: {list(config.keys())}')
except Exception as e:
    print(f'❌ Config JSON error: {e}')
"
```

**SOLUCIONES:**
```bash
# 1. Recreate default config
mkdir -p config/
cat > config/ict_patterns_config.json << 'EOF'
{
    "patterns": {
        "bos": {"enabled": true, "sensitivity": 0.7},
        "choch": {"enabled": true, "sensitivity": 0.8},
        "fvg": {"enabled": true, "min_gap": 0.001}
    },
    "timeframes": ["M1", "M5", "M15", "H1", "H4", "D1"],
    "performance": {
        "cache_size": 1000,
        "memory_limit": "500MB"
    }
}
EOF

# 2. Reset SIC cache
rm -f config/sic_cache_stats.json
python -c "
from sistema.sic_bridge import SICBridge
sic = SICBridge()
sic.reset_cache()
print('✅ SIC cache reset')
"

# 3. Validate all configs
python -c "
import json
import os

config_files = ['ict_patterns_config.json', 'memory_config.json', 'performance_config_enterprise.json']
for file in config_files:
    path = f'config/{file}'
    if os.path.exists(path):
        try:
            with open(path) as f:
                json.load(f)
            print(f'✅ {file}')
        except Exception as e:
            print(f'❌ {file}: {e}')
    else:
        print(f'⚠️ {file}: Not found')
"
```

### **❌ PROBLEMA: Memory Leaks**

**SÍNTOMAS:**
- Memory usage increases over time
- Process doesn't release memory
- System becomes unresponsive

**DIAGNOSTIC:**
```python
import tracemalloc
import gc
import psutil
import time

def memory_monitor(func):
    """Decorator to monitor memory usage."""
    def wrapper(*args, **kwargs):
        # Start monitoring
        tracemalloc.start()
        process = psutil.Process()
        start_memory = process.memory_info().rss
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Check memory
            end_memory = process.memory_info().rss
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            print(f"Memory change: {(end_memory - start_memory) / 1024 / 1024:.2f}MB")
            print(f"Peak usage: {peak / 1024 / 1024:.2f}MB")
            
            # Force garbage collection
            gc.collect()
    
    return wrapper

# Use on suspected functions
@memory_monitor
def suspected_function():
    # ... your code ...
    pass
```

**SOLUCIONES:**
```python
# 1. Explicit cleanup
class ResourceManager:
    def __init__(self):
        self.resources = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for resource in self.resources:
            if hasattr(resource, 'close'):
                resource.close()
        self.resources.clear()

# 2. Use weak references for caches
import weakref

class Cache:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()
    
    def get(self, key):
        return self._cache.get(key)
    
    def set(self, key, value):
        self._cache[key] = value

# 3. Periodic cleanup
import gc
import threading
import time

def periodic_cleanup():
    while True:
        time.sleep(300)  # Every 5 minutes
        collected = gc.collect()
        if collected > 0:
            print(f"Garbage collected: {collected} objects")

cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
cleanup_thread.start()
```

---

## 🛠️ **RECOVERY PROCEDURES**

### **🔄 RESET COMPLETO DEL SISTEMA**

```bash
#!/bin/bash
echo "🔄 ICT ENGINE v6.0 - RESET COMPLETO"
echo "=================================="

# 1. Backup current state
echo "📦 Creating backup..."
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p backups/$timestamp
cp -r config/ backups/$timestamp/ 2>/dev/null || echo "No config to backup"
cp -r logs/ backups/$timestamp/ 2>/dev/null || echo "No logs to backup"

# 2. Clear caches
echo "🧹 Clearing caches..."
rm -rf __pycache__/ cache/ .pytest_cache/ 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
rm -f config/sic_cache_stats.json 2>/dev/null

# 3. Reset Python environment
echo "🐍 Resetting Python environment..."
export PYTHONPATH="$PWD:$PYTHONPATH"

# 4. Recreate essential directories
echo "📁 Recreating directories..."
mkdir -p config/ logs/ data/ tests/temp/

# 5. Test basic functionality
echo "🧪 Testing basic functionality..."
python -c "
try:
    from sistema.sic_bridge import SICBridge
    from core.smart_trading_logger import SmartTradingLogger
    print('✅ Core imports working')
except Exception as e:
    print(f'❌ Core imports failed: {e}')
"

# 6. Run quick tests
echo "🧪 Running quick tests..."
if [ -d "tests/" ]; then
    python -m pytest tests/ --tb=short -q
fi

echo "=================================="
echo "🎯 Reset completo finalizado"
echo "📦 Backup guardado en: backups/$timestamp"
```

### **⚡ RECOVERY RÁPIDO (2 minutos)**

```bash
#!/bin/bash
echo "⚡ ICT ENGINE v6.0 - RECOVERY RÁPIDO"

# Clear Python cache
find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null
export PYTHONPATH="$PWD:$PYTHONPATH"

# Test core functionality
python -c "
from sistema.sic_bridge import SICBridge
from core.smart_trading_logger import SmartTradingLogger
logger = SmartTradingLogger()
logger.info('System recovery test', component='RECOVERY')
print('✅ Recovery successful')
"

echo "🎯 Recovery rápido completado"
```

### **🔧 PARTIAL RECOVERY PROCEDURES**

```bash
# Recovery SIC/SLUC only
reset_sic_sluc() {
    echo "🔧 Resetting SIC/SLUC..."
    rm -f config/sic_cache_stats.json
    python -c "
from sistema.sic_bridge import SICBridge
from core.smart_trading_logger import SmartTradingLogger
sic = SICBridge()
logger = SmartTradingLogger()
logger.info('SIC/SLUC reset', component='RECOVERY')
print('✅ SIC/SLUC reset complete')
    "
}

# Recovery configuration only
reset_config() {
    echo "⚙️ Resetting configuration..."
    mkdir -p config/
    # Recreate essential configs
    echo '{"cache_enabled": true, "performance_mode": "enterprise"}' > config/sic_cache_stats.json
    echo '{"logging_level": "INFO", "enterprise_mode": true}' > config/memory_config.json
    echo "✅ Configuration reset complete"
}

# Recovery logs only
reset_logs() {
    echo "📄 Resetting logs..."
    mkdir -p logs/
    timestamp=$(date +%Y%m%d_%H%M%S)
    echo "[$timestamp] ICT Engine v6.0 - Log system reset" > logs/ict_engine_$(date +%Y%m%d).log
    echo "✅ Logs reset complete"
}
```

---

## 📊 **MONITORING Y PREVENCIÓN**

### **📈 Health Check Automático**

```python
# health_check.py
import time
import psutil
import json
import os
from datetime import datetime
from typing import Dict, Any

class HealthMonitor:
    """Monitor de salud del sistema ICT Engine v6.0."""
    
    def __init__(self):
        self.baseline = self._get_baseline()
        self.alerts = []
    
    def _get_baseline(self) -> Dict[str, Any]:
        """Obtener baseline de performance."""
        return {
            "memory_limit": 500,  # MB
            "cpu_limit": 80,      # %
            "execution_time_limit": 5.0  # seconds
        }
    
    def check_system_health(self) -> Dict[str, Any]:
        """Verificación completa de salud del sistema."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {}
        }
        
        # Memory check
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        results["checks"]["memory"] = {
            "current": memory_mb,
            "limit": self.baseline["memory_limit"],
            "status": "ok" if memory_mb < self.baseline["memory_limit"] else "warning"
        }
        
        # CPU check
        cpu_percent = psutil.cpu_percent(interval=1)
        results["checks"]["cpu"] = {
            "current": cpu_percent,
            "limit": self.baseline["cpu_limit"],
            "status": "ok" if cpu_percent < self.baseline["cpu_limit"] else "warning"
        }
        
        # Import check
        try:
            from sistema.sic_bridge import SICBridge
            from core.smart_trading_logger import SmartTradingLogger
            results["checks"]["imports"] = {"status": "ok"}
        except Exception as e:
            results["checks"]["imports"] = {"status": "error", "error": str(e)}
            results["status"] = "critical"
        
        # Performance check
        start_time = time.time()
        # Simulate operation
        sum(range(10000))
        elapsed = time.time() - start_time
        
        results["checks"]["performance"] = {
            "execution_time": elapsed,
            "limit": self.baseline["execution_time_limit"],
            "status": "ok" if elapsed < self.baseline["execution_time_limit"] else "warning"
        }
        
        # Overall status
        statuses = [check.get("status", "ok") for check in results["checks"].values()]
        if "error" in statuses:
            results["status"] = "critical"
        elif "warning" in statuses:
            results["status"] = "warning"
        
        return results
    
    def save_health_report(self, results: Dict[str, Any]):
        """Guardar reporte de salud."""
        os.makedirs("logs/health/", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs/health/health_check_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        return filename

# Uso
if __name__ == "__main__":
    monitor = HealthMonitor()
    health = monitor.check_system_health()
    report_file = monitor.save_health_report(health)
    
    print(f"Health Status: {health['status']}")
    print(f"Report saved: {report_file}")
    
    if health["status"] != "healthy":
        print("⚠️ Issues detected - check health report for details")
```

### **🚨 Alert System**

```python
# alert_system.py
import smtplib
import json
from email.mime.text import MimeText
from datetime import datetime
from typing import Dict, List

class AlertSystem:
    """Sistema de alertas para ICT Engine v6.0."""
    
    def __init__(self, config_file: str = "config/alert_config.json"):
        self.config = self._load_config(config_file)
        self.active_alerts = []
    
    def _load_config(self, config_file: str) -> Dict:
        """Cargar configuración de alertas."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "email_enabled": False,
                "log_enabled": True,
                "recipients": [],
                "thresholds": {
                    "memory_critical": 1000,  # MB
                    "cpu_critical": 95,       # %
                    "error_rate_critical": 10 # errors/minute
                }
            }
    
    def check_and_alert(self, health_data: Dict):
        """Verificar condiciones y enviar alertas si es necesario."""
        alerts = []
        
        # Memory alert
        memory_check = health_data["checks"].get("memory", {})
        if memory_check.get("status") == "warning":
            alerts.append({
                "type": "memory_warning",
                "message": f"Memory usage high: {memory_check['current']:.1f}MB",
                "severity": "medium"
            })
        
        # CPU alert
        cpu_check = health_data["checks"].get("cpu", {})
        if cpu_check.get("status") == "warning":
            alerts.append({
                "type": "cpu_warning", 
                "message": f"CPU usage high: {cpu_check['current']:.1f}%",
                "severity": "medium"
            })
        
        # Import error alert
        import_check = health_data["checks"].get("imports", {})
        if import_check.get("status") == "error":
            alerts.append({
                "type": "import_error",
                "message": f"Import error: {import_check.get('error', 'Unknown')}",
                "severity": "high"
            })
        
        # Send alerts
        for alert in alerts:
            self._send_alert(alert)
        
        return alerts
    
    def _send_alert(self, alert: Dict):
        """Enviar alerta individual."""
        timestamp = datetime.now().isoformat()
        alert_msg = f"[{timestamp}] {alert['type']}: {alert['message']}"
        
        # Log alert
        if self.config.get("log_enabled", True):
            with open("logs/alerts.log", "a") as f:
                f.write(f"{alert_msg}\n")
        
        # Email alert (if configured)
        if self.config.get("email_enabled", False) and alert["severity"] in ["high", "critical"]:
            self._send_email_alert(alert_msg)
        
        print(f"🚨 ALERT: {alert_msg}")
    
    def _send_email_alert(self, message: str):
        """Enviar alerta por email."""
        # Implementation depends on your email setup
        pass

# Uso integrado con health check
if __name__ == "__main__":
    from health_check import HealthMonitor
    
    monitor = HealthMonitor()
    alert_system = AlertSystem()
    
    health = monitor.check_system_health()
    alerts = alert_system.check_and_alert(health)
    
    if alerts:
        print(f"⚠️ {len(alerts)} alerts generated")
    else:
        print("✅ No alerts - system healthy")
```

---

**📋 ESTADO:** ✅ **PROTOCOLO DE TROUBLESHOOTING COMPLETO**  
**🎯 OBJETIVO:** Resolución estructurada y sistemática de problemas  
**⚡ USO:** Seguir clasificación y usar scripts de diagnostic según severidad
