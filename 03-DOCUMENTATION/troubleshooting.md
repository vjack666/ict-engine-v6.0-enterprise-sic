# 🔧 ICT Engine v6.0 Enterprise - Troubleshooting Guide

**📅 Última actualización:** Septiembre 9, 2025  
**🎯 Versión:** v6.0 Enterprise SIC  
**⚡ Tiempo de resolución:** 2-30 minutos según severidad  

---

## 🚨 **CLASIFICACIÓN DE PROBLEMAS**

### **⚡ CRÍTICOS (Resolver INMEDIATAMENTE)**
- 🚫 Sistema no arranca / imports fallan
- 💾 Pérdida de datos o corrupción  
- ⚡ Performance <50% del baseline
- 🚨 Risk violations activas (MAX_POSITIONS, EMERGENCY_STOP)
- 🔴 Tests core fallando >80%

### **🔶 ALTOS (Resolver en <2 horas)**
- 🔧 Funcionalidad enterprise parcialmente no funcional
- 🧠 Memory leaks detectados
- 📊 Performance 50-80% del baseline
- 🔗 Integration tests fallando
- 📝 Logging/configuración problemática

### **🔸 MEDIOS (Resolver en <1 día)**
- 🛠️ Features específicos no funcionando
- 📈 Performance 80-90% del baseline
- 🧪 Unit tests fallando <20%
- 📚 Documentación inconsistente
- ⚠️ Warnings en producción

---

## 🩺 **DIAGNÓSTICO RÁPIDO (2 minutos)**

### **1️⃣ VALIDACIÓN AUTOMÁTICA DEL SISTEMA**
```powershell
# Ejecutar diagnóstico completo
python 06-TOOLS\validation_quick_test.py

# ✅ Resultado esperado: Score >= 80%
# ❌ Si Score < 60%: Problema crítico detectado
```

### **2️⃣ VERIFICACIÓN DE ESTRUCTURA**
```powershell
# Verificar integridad del proyecto
Write-Host "📂 Verificando estructura del proyecto..." -ForegroundColor Green
$folders = @("01-CORE", "03-DOCUMENTATION", "04-DATA", "05-LOGS", "06-TOOLS", "09-DASHBOARD")
foreach ($folder in $folders) {
    if (Test-Path $folder) {
        Write-Host "  ✅ $folder" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $folder FALTANTE" -ForegroundColor Red
    }
}
```

### **3️⃣ VERIFICACIÓN DE CONFIGURACIONES CRÍTICAS**
```powershell
# Verificar archivos de configuración esenciales
Write-Host "⚙️ Verificando configuraciones críticas..." -ForegroundColor Green
$configs = @(
    "01-CORE\config\log_throttle_config.json",
    "01-CORE\config\risk_management_config.json", 
    "01-CORE\config\timestamp_config.json",
    "01-CORE\config\log_categorization_rules.json"
)
foreach ($config in $configs) {
    if (Test-Path $config) {
        Write-Host "  ✅ $(Split-Path $config -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $(Split-Path $config -Leaf) FALTANTE" -ForegroundColor Red
    }
}
```

---

## 🚨 **PROBLEMAS CRÍTICOS Y SOLUCIONES**

### **❌ PROBLEMA: Sistema no arranca**

**🔍 Síntomas:**
- Error al ejecutar `python main.py`
- ModuleNotFoundError
- Import errors masivos

**⚡ SOLUCIÓN INMEDIATA:**
```powershell
# 1. Verificar versión de Python
python --version
# Debe ser Python 3.8 o superior

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Verificar imports críticos
python -c "
try:
    import pandas as pd
    import numpy as np
    print('✅ Librerías básicas OK')
except Exception as e:
    print(f'❌ Error en librerías: {e}')
"

# 4. Ejecutar auto-reparación
python 06-TOOLS\system_auto_repair.py
```

### **❌ PROBLEMA: Risk Violations Activas**

**🔍 Síntomas:**
- ERROR: RISK_VIOLATION: MAX_POSITIONS
- CRITICAL: EMERGENCY_ACTION: EMERGENCY_STOP
- Sistema bloqueado para trading

**⚡ SOLUCIÓN INMEDIATA:**
```powershell
# 1. Verificar estado actual de risk management
python -c "
import json
with open('01-CORE/config/risk_management_config.json') as f:
    config = json.load(f)
    print(f'Max positions: {config[\"max_positions\"]}')
    print(f'Max drawdown: {config[\"max_drawdown_percent\"]}%')
    print(f'Emergency stop: {config[\"emergency_stop_enabled\"]}')
"

# 2. Resolver violaciones manualmente
python 01-CORE\risk_management\risk_validator.py --reset-emergency

# 3. Verificar resolución
python 06-TOOLS\validation_quick_test.py
```

### **❌ PROBLEMA: Logs Duplicados Masivos**

**🔍 Síntomas:**
- Archivos de log >1000 líneas
- Mensajes idénticos repetidos
- Performance degradada

**⚡ SOLUCIÓN INMEDIATA:**
```powershell
# 1. Ejecutar limpieza rápida
python 06-TOOLS\clean_test_logs.py

# 2. Verificar rate limiting
python -c "
import json
with open('01-CORE/config/log_throttle_config.json') as f:
    config = json.load(f)
    print(f'Max logs/seg: {config[\"max_logs_per_second\"]}')
    print(f'Rate limiting: {config.get(\"enabled\", False)}')
"

# 3. Reiniciar logger con throttling
python -c "
from core.smart_trading_logger import SmartTradingLogger
logger = SmartTradingLogger('test')
logger.info('Test después de throttling')
print('✅ Logger funcionando con rate limiting')
"
```

### **❌ PROBLEMA: Timestamps Inconsistentes**

**🔍 Síntomas:**
- Formatos de tiempo mezclados en logs
- Dificultad para analizar cronología
- Validation score bajo

**⚡ SOLUCIÓN INMEDIATA:**
```powershell
# 1. Verificar configuración de timestamps
python -c "
import json
with open('01-CORE/config/timestamp_config.json') as f:
    config = json.load(f)
    print(f'Formato: {config[\"format\"]}')
    print(f'Timezone: {config[\"timezone\"]}')
    print(f'Estandarizado: {config[\"standardized\"]}')
"

# 2. Estandarizar timestamps existentes
python 01-CORE\utils\timestamp_standardizer.py --fix-existing

# 3. Verificar corrección
python 06-TOOLS\validation_quick_test.py
```

---

## 🔧 **HERRAMIENTAS DE DIAGNÓSTICO AVANZADO**

### **🩺 Health Check Completo**
```powershell
# Crear script de health check
@"
import json
import psutil
import os
from datetime import datetime
from pathlib import Path

def system_health_check():
    results = {
        'timestamp': datetime.now().isoformat(),
        'status': 'unknown',
        'checks': {}
    }
    
    # Check 1: Memory usage
    memory = psutil.virtual_memory()
    results['checks']['memory'] = {
        'current': memory.used / 1024 / 1024,  # MB
        'total': memory.total / 1024 / 1024,   # MB
        'percent': memory.percent,
        'status': 'ok' if memory.percent < 80 else 'warning'
    }
    
    # Check 2: Disk space
    disk = psutil.disk_usage('.')
    results['checks']['disk'] = {
        'free': disk.free / 1024 / 1024,      # MB
        'total': disk.total / 1024 / 1024,    # MB
        'percent': (disk.used / disk.total) * 100,
        'status': 'ok' if disk.free > 1000 else 'warning'  # 1GB free
    }
    
    # Check 3: Critical files
    critical_files = [
        '01-CORE/config/log_throttle_config.json',
        '01-CORE/config/risk_management_config.json',
        '01-CORE/utils/realtime_log_deduplicator.py'
    ]
    
    missing_files = []
    for file_path in critical_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    results['checks']['files'] = {
        'total_critical': len(critical_files),
        'missing': len(missing_files),
        'missing_files': missing_files,
        'status': 'ok' if len(missing_files) == 0 else 'error'
    }
    
    # Check 4: Import test
    try:
        import pandas as pd
        import numpy as np
        results['checks']['imports'] = {'status': 'ok'}
    except Exception as e:
        results['checks']['imports'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # Overall status
    all_statuses = [check.get('status', 'unknown') for check in results['checks'].values()]
    if 'error' in all_statuses:
        results['status'] = 'critical'
    elif 'warning' in all_statuses:
        results['status'] = 'warning'
    else:
        results['status'] = 'healthy'
    
    return results

if __name__ == '__main__':
    health = system_health_check()
    print(json.dumps(health, indent=2))
    
    if health['status'] == 'critical':
        print('\n🚨 CRITICAL ISSUES DETECTED')
        exit(1)
    elif health['status'] == 'warning':
        print('\n⚠️ WARNINGS DETECTED')
        exit(2)
    else:
        print('\n✅ SYSTEM HEALTHY')
        exit(0)
"@ | Out-File -FilePath "06-TOOLS\health_check.py" -Encoding UTF8

# Ejecutar health check
python 06-TOOLS\health_check.py
```

### **📊 Performance Monitor**
```powershell
# Monitor de performance en tiempo real
python -c "
import time
import psutil
import threading
from datetime import datetime

class PerformanceMonitor:
    def __init__(self):
        self.monitoring = False
        
    def start_monitoring(self, duration=60):
        self.monitoring = True
        start_time = datetime.now()
        
        print(f'🔍 Iniciando monitoreo de performance por {duration} segundos...')
        print('Timestamp,CPU%,Memory MB,Disk Read MB/s,Disk Write MB/s')
        
        prev_disk = psutil.disk_io_counters()
        
        for i in range(duration):
            if not self.monitoring:
                break
                
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().used / 1024 / 1024
            
            current_disk = psutil.disk_io_counters()
            disk_read = (current_disk.read_bytes - prev_disk.read_bytes) / 1024 / 1024
            disk_write = (current_disk.write_bytes - prev_disk.write_bytes) / 1024 / 1024
            prev_disk = current_disk
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f'{timestamp},{cpu_percent:.1f},{memory:.1f},{disk_read:.2f},{disk_write:.2f}')
            
        print('✅ Monitoreo completado')
    
    def stop_monitoring(self):
        self.monitoring = False

# Usar: monitor.start_monitoring(30) para 30 segundos
monitor = PerformanceMonitor()
print('Monitor de performance listo. Usar: monitor.start_monitoring(30)')
"
```

---

## 🛠️ **AUTO-REPARACIÓN DEL SISTEMA**

### **🔧 Script de Auto-Reparación**
```powershell
# Crear script de auto-reparación completa
@"
#!/usr/bin/env python3
'''
🔧 AUTO-REPARACIÓN DEL SISTEMA ICT ENGINE v6.0
Repara automáticamente los problemas más comunes
'''

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

class SystemAutoRepair:
    def __init__(self):
        self.base_path = Path('.')
        self.repair_log = []
        
    def log_repair(self, action: str, status: str, details: str = ''):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'status': status,
            'details': details
        }
        self.repair_log.append(entry)
        print(f'[{status}] {action}: {details}')
    
    def repair_missing_configs(self):
        '''Crear configuraciones faltantes'''
        config_dir = self.base_path / '01-CORE' / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Config templates
        configs = {
            'log_throttle_config.json': {
                'max_logs_per_second': 10,
                'max_duplicates_per_minute': 5,
                'emergency_threshold': 100,
                'enabled': True
            },
            'risk_management_config.json': {
                'max_positions': 3,
                'max_drawdown_percent': 5.0,
                'emergency_stop_enabled': True,
                'monitoring_enabled': True
            },
            'timestamp_config.json': {
                'format': '%Y-%m-%d %H:%M:%S',
                'timezone': 'UTC',
                'standardized': True
            },
            'log_categorization_rules.json': {
                'application': {'keywords': ['system', 'startup'], 'priority': 1},
                'fvg_memory': {'keywords': ['fvg', 'fair value gap'], 'priority': 5},
                'market_data': {'keywords': ['market', 'price'], 'priority': 4}
            }
        }
        
        for config_name, config_data in configs.items():
            config_file = config_dir / config_name
            if not config_file.exists():
                with open(config_file, 'w') as f:
                    json.dump(config_data, f, indent=2)
                self.log_repair('CREATE_CONFIG', 'SUCCESS', config_name)
            else:
                self.log_repair('CHECK_CONFIG', 'EXISTS', config_name)
    
    def repair_missing_utils(self):
        '''Crear utilidades faltantes'''
        utils_dir = self.base_path / '01-CORE' / 'utils'
        utils_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear deduplicador básico si no existe
        dedup_file = utils_dir / 'realtime_log_deduplicator.py'
        if not dedup_file.exists():
            dedup_code = '''# Realtime Log Deduplicator
import hashlib
from collections import deque
from datetime import datetime, timedelta

class RealtimeLogDeduplicator:
    def __init__(self):
        self.message_history = deque(maxlen=1000)
        self.message_counts = {}
    
    def should_log(self, message: str) -> bool:
        message_hash = hashlib.md5(message.encode()).hexdigest()
        recent_count = self.message_counts.get(message_hash, 0)
        if recent_count >= 5:  # Max 5 duplicates
            return False
        self.message_counts[message_hash] = recent_count + 1
        return True

DEDUPLICATOR = RealtimeLogDeduplicator()
'''
            with open(dedup_file, 'w') as f:
                f.write(dedup_code)
            self.log_repair('CREATE_UTIL', 'SUCCESS', 'realtime_log_deduplicator.py')
    
    def repair_logs_structure(self):
        '''Reparar estructura de logs'''
        logs_dir = self.base_path / '05-LOGS'
        
        # Crear subdirectorios necesarios
        subdirs = ['application', 'fvg_memory', 'market_data', 'patterns', 'dashboard', 'emergency']
        for subdir in subdirs:
            subdir_path = logs_dir / subdir
            subdir_path.mkdir(parents=True, exist_ok=True)
            self.log_repair('CREATE_LOG_DIR', 'SUCCESS', subdir)
    
    def clean_corrupted_logs(self):
        '''Limpiar logs corruptos'''
        logs_dir = self.base_path / '05-LOGS'
        cleaned_count = 0
        
        for log_file in logs_dir.rglob('*.log'):
            try:
                if log_file.stat().st_size > 10 * 1024 * 1024:  # >10MB
                    backup_file = log_file.with_suffix('.log.backup')
                    shutil.move(str(log_file), str(backup_file))
                    cleaned_count += 1
                    self.log_repair('CLEAN_LOG', 'SUCCESS', f'{log_file.name} (>10MB)')
            except Exception as e:
                self.log_repair('CLEAN_LOG', 'ERROR', f'{log_file.name}: {e}')
        
        if cleaned_count > 0:
            self.log_repair('CLEAN_LOGS_TOTAL', 'SUCCESS', f'{cleaned_count} archivos limpiados')
    
    def run_full_repair(self):
        '''Ejecutar reparación completa'''
        print('🔧 INICIANDO AUTO-REPARACIÓN DEL SISTEMA')
        print('=' * 50)
        
        self.repair_missing_configs()
        self.repair_missing_utils()
        self.repair_logs_structure()
        self.clean_corrupted_logs()
        
        # Guardar log de reparaciones
        repair_log_file = self.base_path / '03-DOCUMENTATION' / 'reports' / f'auto_repair_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.json'
        repair_log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(repair_log_file, 'w') as f:
            json.dump(self.repair_log, f, indent=2)
        
        print(f'\\n✅ AUTO-REPARACIÓN COMPLETADA')
        print(f'📋 Log guardado: {repair_log_file}')
        print(f'🔧 Acciones realizadas: {len(self.repair_log)}')
        
        # Estadísticas
        success_count = len([r for r in self.repair_log if r['status'] == 'SUCCESS'])
        error_count = len([r for r in self.repair_log if r['status'] == 'ERROR'])
        
        print(f'✅ Éxitos: {success_count}')
        print(f'❌ Errores: {error_count}')
        
        return success_count > error_count

if __name__ == '__main__':
    repairer = SystemAutoRepair()
    success = repairer.run_full_repair()
    exit(0 if success else 1)
"@ | Out-File -FilePath "06-TOOLS\system_auto_repair.py" -Encoding UTF8

# Ejecutar auto-reparación
python 06-TOOLS\system_auto_repair.py
```

---

## 📋 **PROCEDIMIENTOS DE EMERGENCIA**

### **🚨 EMERGENCY STOP - Detener Sistema Inmediatamente**
```powershell
# 1. Parar todos los procesos
Get-Process python | Where-Object {$_.MainWindowTitle -like "*ICT*"} | Stop-Process -Force

# 2. Limpiar estado de emergencia
python -c "
import json
emergency_file = '04-DATA/emergency/system_state_emergency.json'
try:
    with open(emergency_file, 'w') as f:
        json.dump({
            'status': 'MANUAL_STOP',
            'timestamp': '$(Get-Date -Format "yyyy-MM-ddTHH:mm:ss")',
            'reason': 'Manual emergency stop'
        }, f, indent=2)
    print('✅ Emergency state saved')
except:
    print('⚠️ Could not save emergency state')
"

# 3. Verificar que todo esté detenido
Get-Process python | Where-Object {$_.MainWindowTitle -like "*ICT*"}
```

### **🔄 RESTART COMPLETO DEL SISTEMA**
```powershell
# 1. Emergency stop
# (ejecutar procedimiento anterior)

# 2. Auto-reparación
python 06-TOOLS\system_auto_repair.py

# 3. Validación completa
python 06-TOOLS\validation_quick_test.py

# 4. Restart seguro
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Sistema validado, reiniciando..." -ForegroundColor Green
    python main.py
} else {
    Write-Host "❌ Sistema NO validado, revisar errores" -ForegroundColor Red
}
```

---

## ✅ **VERIFICACIÓN POST-RESOLUCIÓN**

### **📊 Checklist de Validación Final**
```powershell
Write-Host "📋 CHECKLIST DE VALIDACIÓN FINAL" -ForegroundColor Yellow
Write-Host "=" * 40

# 1. Validación automática
Write-Host "1️⃣ Ejecutando validación automática..." -ForegroundColor Green
python 06-TOOLS\validation_quick_test.py
$validation_result = $LASTEXITCODE

# 2. Verificar logs
Write-Host "2️⃣ Verificando logs..." -ForegroundColor Green
$log_count = (Get-ChildItem "05-LOGS\application\*.log" | Measure-Object).Count
if ($log_count -gt 0) {
    Write-Host "   ✅ Logs siendo generados" -ForegroundColor Green
} else {
    Write-Host "   ❌ No se están generando logs" -ForegroundColor Red
}

# 3. Verificar configuraciones
Write-Host "3️⃣ Verificando configuraciones..." -ForegroundColor Green
$config_count = (Get-ChildItem "01-CORE\config\*.json" | Measure-Object).Count
Write-Host "   📁 Configuraciones encontradas: $config_count"

# 4. Test de funcionalidad básica
Write-Host "4️⃣ Test de funcionalidad básica..." -ForegroundColor Green
python -c "
try:
    from core.smart_trading_logger import SmartTradingLogger
    logger = SmartTradingLogger('test')
    logger.info('Test post-reparación')
    print('   ✅ Logger funcionando')
except Exception as e:
    print(f'   ❌ Error en logger: {e}')
"

# Resultado final
if ($validation_result -eq 0) {
    Write-Host "`n🎉 SISTEMA COMPLETAMENTE REPARADO Y FUNCIONAL" -ForegroundColor Green
    Write-Host "✅ Listo para operación normal" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ SISTEMA REQUIERE ATENCIÓN ADICIONAL" -ForegroundColor Yellow
    Write-Host "📞 Considerar soporte técnico especializado" -ForegroundColor Yellow
}
```

---

## 📞 **ESCALACIÓN Y SOPORTE**

### **🔴 Cuándo Escalar a Soporte Técnico:**
- ❌ Score de validación persistentemente < 60%
- 🚨 Errores críticos que no se resuelven con auto-reparación
- 💾 Corrupción de datos o pérdida de configuraciones
- ⚡ Performance degradada >50% sin causa aparente
- 🔄 Sistema entra en loop de errores

### **📋 Información a Recopilar para Soporte:**
```powershell
# Crear paquete de diagnóstico para soporte
@"
# PAQUETE DE DIAGNÓSTICO - ICT ENGINE v6.0
# Generado: $(Get-Date)

## INFORMACIÓN DEL SISTEMA
$(python --version)
$(Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory)

## VALIDACIÓN ACTUAL
"@ | Out-File -FilePath "diagnostico_soporte.txt"

python 06-TOOLS\validation_quick_test.py >> diagnostico_soporte.txt 2>&1

Write-Host "📋 Paquete de diagnóstico creado: diagnostico_soporte.txt"
Write-Host "📧 Adjuntar este archivo al solicitar soporte técnico"
```

---

**🎯 OBJETIVO FINAL:** Resolver cualquier problema en <30 minutos usando procedimientos estructurados y herramientas automatizadas.

**✅ CRITERIO DE ÉXITO:** Sistema funcionando con score de validación >= 80% y sin errores críticos.
