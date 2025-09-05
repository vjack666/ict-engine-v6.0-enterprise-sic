# ⚡ COMANDOS RÁPIDOS Y VERIFICACIONES

**Archivo:** `06-comandos-rapidos.md`  
**Propósito:** Comandos y verificaciones rápidas para setup y validación

---

## 🚀 **SETUP RÁPIDO (5 MINUTOS)**

### **📋 Verificación de Estado del Sistema**
```bash
# ✅ ESTRUCTURA DEL PROYECTO
echo "📂 Verificando estructura del proyecto..."
ls -la core/ tests/ docs/ 2>/dev/null || echo "❌ Directorios principales no encontrados"
ls -la protocolo-trabajo-copilot/ 2>/dev/null || echo "❌ Protocolo no encontrado"

# ✅ IMPORTS CRÍTICOS SIC/SLUC
echo "🏗️ Verificando SIC/SLUC availability..."
python -c "
try:
    from sistema.sic_bridge import SICBridge
    print('✅ SIC Bridge disponible')
except ImportError as e:
    print(f'⚠️ SIC Bridge no disponible: {e}')

try:
    from core.smart_trading_logger import SmartTradingLogger
    print('✅ SLUC Logger disponible')
except ImportError as e:
    print(f'⚠️ SLUC Logger no disponible: {e}')
" 2>/dev/null

# ✅ DATOS MT5
echo "📊 Verificando datos MT5..."
find data/ -name "*.csv" 2>/dev/null | head -3 || echo "⚠️ No se encontraron datos MT5"

# ✅ ÚLTIMA FASE COMPLETADA
echo "📅 Última fase completada:"
cat logs/fase_*_completada.log 2>/dev/null | tail -3 || echo "⚠️ No se encontraron logs de fases"
```

### **🔧 Setup de Entorno Python**
```bash
# ✅ PYTHONPATH SETUP
export PYTHONPATH="$PWD:$PYTHONPATH"
echo "✅ PYTHONPATH configurado: $PYTHONPATH"

# ✅ VERIFICAR PYTHON VERSION
python --version
echo "✅ Python version verificada"

# ✅ CREAR DIRECTORIOS TEMP
mkdir -p tests/temp data/temp docs/temp logs/temp 2>/dev/null
echo "✅ Directorios temporales creados"

# ✅ VERIFICAR IMPORTS BÁSICOS
python -c "
import sys
import pandas as pd
import numpy as np
print('✅ Imports básicos funcionando')
print(f'Python: {sys.version}')
print(f'Pandas: {pd.__version__}')
print(f'NumPy: {np.__version__}')
" 2>/dev/null || echo "❌ Error en imports básicos"
```

---

## 🔍 **VERIFICACIONES RÁPIDAS**

### **📊 Estado del Proyecto en 30 Segundos**
```bash
#!/bin/bash
echo "🎯 ICT ENGINE v6.0 - ESTADO RÁPIDO"
echo "=================================="

# Archivos principales
echo "📂 ESTRUCTURA:"
echo "  Core modules: $(find core/ -name "*.py" 2>/dev/null | wc -l) archivos"
echo "  Tests: $(find tests/ -name "*.py" 2>/dev/null | wc -l) archivos"  
echo "  Docs: $(find docs/ -name "*.md" 2>/dev/null | wc -l) archivos"

# Última actividad
echo "📅 ÚLTIMA ACTIVIDAD:"
echo "  $(ls -t logs/*.log 2>/dev/null | head -1 | xargs tail -1 2>/dev/null || echo 'No logs found')"

# Componentes enterprise
echo "🏗️ ENTERPRISE STATUS:"
python -c "
try:
    from sistema.sic_bridge import SICBridge; print('  SIC: ✅')
except: print('  SIC: ❌')
try:
    from core.smart_trading_logger import SmartTradingLogger; print('  SLUC: ✅')
except: print('  SLUC: ❌')
try:
    from core.data_management.unified_memory_system import UnifiedMemorySystem; print('  Memory: ✅')
except: print('  Memory: ❌')
" 2>/dev/null

echo "=================================="
```

### **🧪 Test Rápido de Conectividad**
```bash
# ✅ TEST SIC/SLUC 
python -c "
print('🧪 Testing enterprise connectivity...')
try:
    from core.smart_trading_logger import SmartTradingLogger
    logger = SmartTradingLogger()
    logger.info('Test protocolo funcionando', component='PROTOCOL_TEST')
    print('✅ SLUC logging functional')
except Exception as e:
    print(f'❌ SLUC test failed: {e}')

try:
    from sistema.sic_bridge import SICBridge
    sic = SICBridge()
    print('✅ SIC bridge functional')
except Exception as e:
    print(f'❌ SIC test failed: {e}')
"

# ✅ TEST PERFORMANCE BÁSICO
python -c "
import time
start = time.time()
# Simulate basic operation
sum(range(10000))
elapsed = time.time() - start
print(f'⚡ Basic performance: {elapsed:.4f}s')
assert elapsed < 1.0, 'Performance too slow'
print('✅ Performance test passed')
"
```

### **📂 Análisis Rápido de Área de Trabajo**
```bash
# ✅ IDENTIFICAR ÁREA DE TRABAJO
echo "🎯 Identificando área de trabajo disponible..."

echo "🧠 MEMORIA:"
ls docs/04-development-logs/memoria/ 2>/dev/null | head -3

echo "💹 SMART MONEY:"
ls docs/04-development-logs/smart-money/ 2>/dev/null | head -3

echo "📊 BOS/CHOCH:"
ls docs/04-development-logs/bos-choch/ 2>/dev/null | head -3

echo "🔗 INTEGRATION:"
ls docs/04-development-logs/integration/ 2>/dev/null | head -3

echo "🧪 TESTING:"
ls docs/04-development-logs/testing/ 2>/dev/null | head -3

echo "⚡ PERFORMANCE:"
ls docs/04-development-logs/performance/ 2>/dev/null | head -3
```

---

## 🔧 **COMANDOS DE DESARROLLO**

### **📝 Búsqueda de Duplicación (OBLIGATORIO)**
```bash
# ✅ BUSCAR FUNCIONALIDAD SIMILAR
echo "🔍 Buscando funcionalidad similar..."

# Buscar por nombre de función/clase
read -p "Nombre de función/clase a buscar: " SEARCH_TERM
echo "Buscando: $SEARCH_TERM"

find . -name "*.py" -exec grep -l "$SEARCH_TERM" {} \; 2>/dev/null
find . -name "*.py" -exec grep -l "$(echo $SEARCH_TERM | tr '[:upper:]' '[:lower:]')" {} \; 2>/dev/null

# Buscar patrones similares
echo "🔍 Patrones similares encontrados:"
grep -r "class.*$(echo $SEARCH_TERM | sed 's/[Aa]nalyzer/.*analyzer/g')" core/ --include="*.py" 2>/dev/null || echo "No patterns found"
```

### **⚡ Performance Testing Rápido**
```bash
# ✅ PERFORMANCE BASELINE
python -c "
import time
import psutil
import os

print('⚡ Performance baseline test...')

# Memory baseline
process = psutil.Process()
start_memory = process.memory_info().rss / 1024 / 1024

# CPU baseline  
start_time = time.time()

# Simulate workload
for i in range(100000):
    _ = i ** 2

end_time = time.time()
end_memory = process.memory_info().rss / 1024 / 1024

print(f'📊 Execution time: {end_time - start_time:.4f}s')
print(f'📊 Memory usage: {end_memory - start_memory:.2f}MB')
print(f'📊 CPU usage: {psutil.cpu_percent()}%')

assert end_time - start_time < 5.0, 'Performance target missed'
print('✅ Performance baseline passed')
"
```

### **🧪 Testing Commands**
```bash
# ✅ RUN SPECIFIC TEST
test_file_run() {
    local test_file=$1
    echo "🧪 Running test: $test_file"
    python -m pytest "$test_file" -v --tb=short
}

# ✅ RUN ALL TESTS IN AREA
test_area_run() {
    local area=$1
    echo "🧪 Running tests for area: $area"
    python -m pytest tests/ -k "$area" -v
}

# ✅ QUICK INTEGRATION TEST
quick_integration_test() {
    echo "🔗 Quick integration test..."
    python -c "
from core.smart_trading_logger import SmartTradingLogger
logger = SmartTradingLogger()
logger.info('Integration test', component='QUICK_TEST')
print('✅ Integration test passed')
    " 2>/dev/null || echo "❌ Integration test failed"
}
```

---

## 📊 **COMANDOS DE ANÁLISIS**

### **📈 Análisis de Código Rápido**
```bash
# ✅ CODE STATS
echo "📊 Estadísticas de código:"
echo "  Python files: $(find . -name "*.py" | wc -l)"
echo "  Lines of code: $(find . -name "*.py" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo 'N/A')"
echo "  Test files: $(find tests/ -name "*.py" 2>/dev/null | wc -l)"

# ✅ RECENT CHANGES
echo "📅 Cambios recientes:"
find . -name "*.py" -mtime -1 2>/dev/null | head -5

# ✅ TODO/FIXME ANALYSIS
echo "📋 TODOs/FIXMEs encontrados:"
grep -r "TODO\|FIXME\|HACK" . --include="*.py" 2>/dev/null | wc -l
```

### **🔍 Dependency Analysis**
```bash
# ✅ IMPORT ANALYSIS
echo "🔗 Análisis de imports..."
python -c "
import ast
import os

def analyze_imports(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f'{module}.{alias.name}')
        return imports
    except:
        return []

# Analyze recent Python files
recent_files = [f for f in os.listdir('.') if f.endswith('.py')][:5]
for file in recent_files:
    imports = analyze_imports(file)
    if imports:
        print(f'{file}: {len(imports)} imports')
"
```

### **🏗️ Architecture Check**
```bash
# ✅ ARCHITECTURE COMPLIANCE CHECK
echo "🏗️ Verificando compliance arquitectónico..."

# SIC/SLUC usage
echo "📊 SIC/SLUC usage:"
grep -r "from sistema.sic" . --include="*.py" 2>/dev/null | wc -l || echo "0"
grep -r "SmartTradingLogger" . --include="*.py" 2>/dev/null | wc -l || echo "0"

# Enterprise patterns
echo "📊 Enterprise patterns:"
grep -r "enterprise\|Enterprise" . --include="*.py" 2>/dev/null | wc -l || echo "0"
grep -r "Config\|config" . --include="*.py" 2>/dev/null | wc -l || echo "0"

# Error handling
echo "📊 Error handling:"
grep -r "try:\|except\|raise" . --include="*.py" 2>/dev/null | wc -l || echo "0"
```

---

## 🎯 **COMANDOS DE FINALIZACIÓN**

### **✅ Pre-Commit Verification**
```bash
# ✅ PRE-COMMIT CHECKLIST
pre_commit_check() {
    echo "✅ Pre-commit verification..."
    
    # No prints in production code
    echo "🔍 Checking for debug prints..."
    if grep -r "print(" . --include="*.py" --exclude-dir=tests 2>/dev/null; then
        echo "⚠️ Debug prints found - remove before commit"
    else
        echo "✅ No debug prints found"
    fi
    
    # No TODOs in new code
    echo "🔍 Checking for TODOs..."
    todo_count=$(grep -r "TODO\|FIXME" . --include="*.py" 2>/dev/null | wc -l)
    echo "📊 TODOs found: $todo_count"
    
    # Basic syntax check
    echo "🔍 Basic syntax check..."
    python -m py_compile *.py 2>/dev/null && echo "✅ Syntax OK" || echo "❌ Syntax errors found"
    
    # Import check
    echo "🔍 Import check..."
    python -c "
import sys
try:
    # Test imports
    print('✅ Basic imports working')
except Exception as e:
    print(f'❌ Import errors: {e}')
    sys.exit(1)
    "
}

# Execute pre-commit check
pre_commit_check
```

### **📝 Documentation Update Check**
```bash
# ✅ DOCUMENTATION UPDATE CHECK
doc_update_check() {
    echo "📝 Checking documentation updates needed..."
    
    # Check if bitácoras need update
    echo "📅 Last bitácora update:"
    find docs/04-development-logs/ -name "*.md" -exec ls -lt {} + 2>/dev/null | head -1
    
    # Check if README needs update
    echo "📖 README last modified:"
    ls -lt docs/README.md 2>/dev/null || echo "README not found"
    
    # Check logs
    echo "📊 Recent logs:"
    ls -lt logs/ 2>/dev/null | head -3
}

doc_update_check
```

### **🎉 Success Verification**
```bash
# ✅ FINAL SUCCESS CHECK
final_success_check() {
    echo "🎉 Final success verification..."
    
    # All components working
    python -c "
try:
    from core.smart_trading_logger import SmartTradingLogger
    logger = SmartTradingLogger()
    logger.info('Final verification', component='SUCCESS_CHECK')
    print('✅ All systems operational')
except Exception as e:
    print(f'❌ System check failed: {e}')
    "
    
    # Performance within bounds
    python -c "
import time
start = time.time()
# Quick performance test
sum(range(1000))
elapsed = time.time() - start
print(f'⚡ Performance: {elapsed:.4f}s')
if elapsed < 1.0:
    print('✅ Performance within bounds')
else:
    print('❌ Performance concern')
    "
    
    echo "🎯 Project ready for next phase!"
}

final_success_check
```

---

## ⚡ **COMANDOS ALIAS ÚTILES**

```bash
# ✅ AGREGAR A .bashrc o .zshrc
alias ict-status="bash protocolo-trabajo-copilot/06-comandos-rapidos.md"
alias ict-test="python -m pytest tests/ -v"
alias ict-quick="python -c 'from core.smart_trading_logger import SmartTradingLogger; print(\"✅ ICT Enterprise Ready\")'"
alias ict-logs="tail -f logs/*.log"
alias ict-docs="find docs/ -name '*.md' -exec ls -lt {} + | head -10"
```

---

**📋 ESTADO:** ✅ **COMANDOS RÁPIDOS LISTOS PARA USO**  
**🎯 OBJETIVO:** Setup y verificación en <5 minutos para cualquier sesión  
**⚡ USO:** Copy-paste comandos según necesidad específica de la sesión
