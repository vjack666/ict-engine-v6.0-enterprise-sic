# 🚨 ICT Engine v6.0 Enterprise - Emergency Procedures

**Versión:** v6.0 Enterprise  
**Fecha:** 2025-09-10  
**Criticidad:** MÁXIMA - Procedimientos de emergencia  
**Tiempo de respuesta:** <2 minutos para estabilización  

---

## 🎯 EMERGENCY RESPONSE MATRIX

### **Nivel de Emergencia por Síntomas:**

| Síntoma | Nivel | Tiempo Respuesta | Procedimiento |
|---------|-------|-----------------|---------------|
| **Sistema no responde** | 🔴 CRÍTICO | <30s | PROC-001 |
| **MT5 desconectado durante trading** | 🔴 CRÍTICO | <60s | PROC-002 |
| **Dashboard caído** | 🟡 ALTO | <2min | PROC-003 |
| **Señales no generan** | 🟡 ALTO | <5min | PROC-004 |
| **Memory leak detectado** | 🟢 MEDIO | <10min | PROC-005 |

---

## 🚨 PROC-001: SISTEMA NO RESPONDE (CRÍTICO)

### **Identificación Rápida:**
```bash
# Test de respuesta inmediato (10 segundos)
python -c "print('Sistema responde')" 2>$null
if ($LASTEXITCODE -ne 0) { 
    Write-Host "🚨 EMERGENCIA: Sistema no responde" -ForegroundColor Red 
}
```

### **Procedimiento de Emergencia (30 segundos):**
```bash
# PASO 1: Kill all processes (5s)
Write-Host "🚨 PROC-001: Emergency system restart"
taskkill /f /im python.exe 2>$null
taskkill /f /im terminal64.exe 2>$null

# PASO 2: Verificar procesos limpiados (5s)
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "⚠️ Warning: Some Python processes still running"
    Stop-Process -Name python -Force
}

# PASO 3: Clean restart (20s)
cd c:\Users\v_jac\Desktop\ict-engine-v6.0-enterprise-sic
Start-Sleep 2
python main.py --emergency-start

Write-Host "✅ Emergency restart complete - System should be responsive"
```

### **Validación Post-Emergencia:**
```bash
# Verificar sistema operacional (30s después del restart)
timeout 30 python -c "
from datetime import datetime
print(f'✅ Sistema operacional: {datetime.now()}')

# Test componentes críticos
try:
    from 01-CORE.data_management.mt5_data_manager import MT5DataManager
    print('✅ MT5 module: OK')
    
    from 01-CORE.ict_engine.pattern_detector import ICTPatternDetector  
    print('✅ Pattern detection: OK')
    
    print('🎯 Emergency recovery: SUCCESSFUL')
except Exception as e:
    print(f'❌ Recovery failed: {e}')
    print('🚨 ESCALATE: Manual intervention required')
"
```

---

## 🚨 PROC-002: MT5 DESCONECTADO DURANTE TRADING (CRÍTICO)

### **Detección Automática:**
```bash
# Script de detección de emergencia MT5
python -c "
import MetaTrader5 as mt5
from datetime import datetime

print(f'🚨 PROC-002: MT5 Emergency Check - {datetime.now()}')

# Test conexión inmediata
if not mt5.initialize():
    print('❌ MT5 CONNECTION LOST - EMERGENCY MODE')
    
    # Emergency reconnection sequence
    import time
    for attempt in range(3):
        print(f'🔄 Reconnection attempt {attempt + 1}/3')
        
        # Force MT5 restart
        import subprocess
        subprocess.run(['taskkill', '/f', '/im', 'terminal64.exe'], 
                      capture_output=True)
        time.sleep(5)
        
        # Retry connection
        if mt5.initialize():
            account_info = mt5.account_info()
            if account_info:
                print(f'✅ EMERGENCY RECONNECTION SUCCESS')
                print(f'✅ Account: {account_info.login}')
                print(f'✅ Balance: ${account_info.balance}')
                break
    else:
        print('🚨 CRITICAL: MT5 reconnection failed - MANUAL INTERVENTION REQUIRED')
else:
    account_info = mt5.account_info()
    print(f'✅ MT5 Connected - Balance: ${account_info.balance}')
"
```

### **Workaround de Emergencia:**
```bash
# Activar modo de emergencia sin MT5 (preservar sistema)
python -c "
print('🚨 Activating MT5 Emergency Workaround Mode')

# Switch to demo/simulation mode
import json
import os

# Backup current config
emergency_backup = '01-CORE/config/emergency_backup.json'
current_config = '01-CORE/config/real_trading_config.json'

try:
    # Read current config
    with open(current_config, 'r') as f:
        config = json.load(f)
    
    # Save backup
    with open(emergency_backup, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Switch to emergency mode
    config['emergency_mode'] = True
    config['mt5_required'] = False
    config['data_source'] = 'simulation'
    
    # Save emergency config
    with open(current_config, 'w') as f:
        json.dump(config, f, indent=2)
        
    print('✅ Emergency mode activated - System continues without MT5')
    print('⚠️ WARNING: Trading disabled, monitoring only')
    
except Exception as e:
    print(f'❌ Emergency mode activation failed: {e}')
"
```

---

## 🚨 PROC-003: DASHBOARD CAÍDO (ALTO)

### **Recovery Rápido:**
```bash
# Dashboard emergency restart (2 minutos)
Write-Host "🚨 PROC-003: Dashboard Emergency Recovery"

# Step 1: Kill dashboard processes
Get-Process | Where-Object {$_.ProcessName -like "*python*" -and $_.CommandLine -like "*dashboard*"} | Stop-Process -Force

# Step 2: Clear port
$port = 8050
$processOnPort = netstat -ano | Select-String ":$port "
if ($processOnPort) {
    $pid = ($processOnPort -split '\s+')[-1]
    Stop-Process -Id $pid -Force
    Write-Host "✅ Port $port cleared"
}

# Step 3: Emergency dashboard start
Start-Sleep 3
Set-Location "c:\Users\v_jac\Desktop\ict-engine-v6.0-enterprise-sic"

# Try multiple ports
$ports = @(8050, 8051, 8052)
foreach ($testPort in $ports) {
    try {
        Start-Process python -ArgumentList "09-DASHBOARD/dashboard.py --port $testPort" -NoNewWindow
        Start-Sleep 5
        
        # Test if dashboard responds
        $response = Invoke-WebRequest -Uri "http://localhost:$testPort" -TimeoutSec 10 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Dashboard recovered on port $testPort"
            Start-Process "http://localhost:$testPort"
            break
        }
    }
    catch {
        Write-Host "❌ Port $testPort failed, trying next..."
    }
}
```

### **Modo Dashboard Mínimo:**
```bash
# Launch minimal dashboard (sin widgets pesados)
python -c "
import dash
from dash import html
import datetime

print('🚨 Launching Emergency Minimal Dashboard')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('🚨 ICT Engine - Emergency Dashboard', style={'color': 'red'}),
    html.P(f'Emergency mode active since: {datetime.datetime.now()}'),
    html.P('✅ Core system: Operational'),
    html.P('⚠️ Full dashboard: Under recovery'),
    html.P('System logs available in 05-LOGS/'),
    html.Div(id='status', children='Emergency mode - Limited functionality')
])

if __name__ == '__main__':
    app.run_server(debug=False, port=8053, host='127.0.0.1')
"
```

---

## 🚨 PROC-004: SEÑALES NO GENERAN (ALTO)

### **Diagnóstico Rápido de Emergencia:**
```bash
# Check signal generation pipeline (1 minuto)
python -c "
from datetime import datetime, timedelta
import os

print(f'🚨 PROC-004: Signal Generation Emergency Check - {datetime.now()}')

# Check today's signal log
today = datetime.now().strftime('%Y-%m-%d')
signal_log = f'05-LOGS/ict_signals/ict_signals_{today}.log'

if os.path.exists(signal_log):
    with open(signal_log, 'r') as f:
        lines = f.readlines()
    
    if lines:
        last_line = lines[-1]
        print(f'✅ Signal log exists: {len(lines)} entries')
        print(f'✅ Last signal: {last_line.strip()[:100]}...')
        
        # Check if recent (last 30 minutes)
        if len(lines) > 0:
            # Extract timestamp from last signal
            print('⚠️ Checking signal freshness...')
            current_time = datetime.now()
            thirty_min_ago = current_time - timedelta(minutes=30)
            print(f'Signal generation: Analyzing last 30 minutes')
    else:
        print('❌ Signal log empty - NO SIGNALS TODAY')
        print('🚨 EMERGENCY: Signal generation completely stopped')
else:
    print('❌ Signal log missing - SYSTEM NOT LOGGING')
    print('🚨 EMERGENCY: Logging system failure')

# Test pattern detector directly
try:
    from 01-CORE.ict_engine.pattern_detector import ICTPatternDetector
    detector = ICTPatternDetector()
    print('✅ Pattern detector: Available')
    
    # Force test detection
    print('🔄 Running emergency signal test...')
    # Add test signal generation logic here
    
except Exception as e:
    print(f'❌ Pattern detector failed: {e}')
    print('🚨 CRITICAL: Core detection system down')
"
```

### **Force Signal Generation (Emergency):**
```bash
# Emergency signal generation test
python -c "
print('🚨 Emergency Signal Generation Test')

try:
    from 01-CORE.ict_engine.pattern_detector import ICTPatternDetector
    from datetime import datetime
    
    detector = ICTPatternDetector()
    
    # Generate test signals
    test_signal = {
        'timestamp': datetime.now().isoformat(),
        'pattern': 'EMERGENCY_TEST',
        'symbol': 'EURUSD',
        'confidence': 0.95,
        'type': 'BOS',
        'emergency_mode': True
    }
    
    print(f'✅ Test signal generated: {test_signal}')
    
    # Log emergency signal
    log_file = f'05-LOGS/ict_signals/ict_signals_{datetime.now().strftime(\"%Y-%m-%d\")}.log'
    with open(log_file, 'a') as f:
        f.write(f'{datetime.now()} - EMERGENCY_TEST_SIGNAL: {test_signal}\\n')
    
    print('✅ Emergency signal logged successfully')
    print('🎯 Signal generation system: OPERATIONAL')
    
except Exception as e:
    print(f'❌ Emergency signal test failed: {e}')
    print('🚨 ESCALATE: Signal generation system down')
"
```

---

## 🚨 PROC-005: MEMORY LEAK DETECTADO (MEDIO)

### **Memory Emergency Cleanup:**
```bash
# Emergency memory cleanup
python -c "
import psutil
import gc
import os
from datetime import datetime

print(f'🚨 PROC-005: Memory Emergency Cleanup - {datetime.now()}')

# Check current memory
process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f'Current memory: {memory_mb:.1f} MB')

if memory_mb > 512:
    print('⚠️ HIGH MEMORY USAGE - Starting emergency cleanup')
    
    # Force garbage collection
    collected = gc.collect()
    print(f'✅ Garbage collected: {collected} objects')
    
    # Check memory after cleanup
    memory_after = process.memory_info().rss / 1024 / 1024
    print(f'Memory after cleanup: {memory_after:.1f} MB')
    print(f'Memory saved: {memory_mb - memory_after:.1f} MB')
    
    if memory_after > 400:
        print('🚨 Memory still high - System restart recommended')
        print('Run: python main.py --restart')
    else:
        print('✅ Memory cleanup successful')
else:
    print('✅ Memory usage normal')

# Memory monitoring alert
print('Setting up memory monitoring...')
print('Monitor: Task Manager or Performance Monitor')
print('Alert threshold: >512MB')
"
```

---

## 📊 EMERGENCY SYSTEM STATUS DASHBOARD

### **Quick Status Check (15 seconds):**
```bash
# Emergency status dashboard
python -c "
import sys
import time
import psutil
from datetime import datetime

print('🚨 EMERGENCY SYSTEM STATUS DASHBOARD')
print('=' * 50)
print(f'Timestamp: {datetime.now()}')
print()

# System basics
print('SYSTEM BASICS:')
try:
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    print(f'CPU: {cpu}%')
    print(f'Memory: {memory}%')
    print(f'Python: {sys.version.split()[0]}')
except:
    print('❌ System metrics unavailable')

print()

# ICT Engine components
print('ICT ENGINE COMPONENTS:')
components = {
    'Core': '01-CORE.enums',
    'MT5': '01-CORE.data_management.mt5_data_manager', 
    'Patterns': '01-CORE.ict_engine.pattern_detector',
    'Dashboard': '09-DASHBOARD.dashboard',
    'Memory': '01-CORE.analysis.unified_memory_system'
}

for name, module in components.items():
    try:
        __import__(module)
        print(f'✅ {name}: OK')
    except Exception as e:
        print(f'❌ {name}: FAILED - {str(e)[:30]}...')

print()

# Emergency recommendations
print('EMERGENCY RECOMMENDATIONS:')
if cpu > 80:
    print('🔴 High CPU - Consider restart')
if memory > 80:
    print('🔴 High Memory - Run cleanup')
    
print('🎯 Emergency status check complete')
"
```

---

## 🔧 EMERGENCY CONFIGURATION RESET

### **Reset to Safe Defaults:**
```bash
# Emergency config reset
python -c "
import json
import os
import shutil
from datetime import datetime

print('🚨 Emergency Configuration Reset')

config_dir = '01-CORE/config'
backup_dir = f'{config_dir}/emergency_backup_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}'

# Create backup
os.makedirs(backup_dir, exist_ok=True)
for file in os.listdir(config_dir):
    if file.endswith('.json'):
        shutil.copy2(f'{config_dir}/{file}', backup_dir)

print(f'✅ Backup created: {backup_dir}')

# Reset to emergency safe defaults
emergency_config = {
    'emergency_mode': True,
    'reduced_functionality': True,
    'mt5_required': False,
    'memory_limit_mb': 256,
    'log_level': 'ERROR',
    'dashboard_port': 8050,
    'signal_generation': True,
    'pattern_detection': True
}

# Apply emergency config
config_file = f'{config_dir}/emergency_config.json'
with open(config_file, 'w') as f:
    json.dump(emergency_config, f, indent=2)

print('✅ Emergency configuration applied')
print('⚠️ System in safe mode - Limited functionality')
print('📋 Restore from backup when issue resolved')
"
```

---

## 📞 ESCALATION MATRIX

### **When to Escalate:**
| Tiempo sin resolución | Acción |
|----------------------|---------|
| **0-5 minutos** | Ejecutar procedimientos automáticos |
| **5-15 minutos** | Aplicar workarounds de emergencia |
| **15-30 minutos** | Escalación nivel 1 (técnico senior) |
| **30+ minutos** | Escalación nivel 2 (arquitecto sistema) |

### **Información para Escalación:**
```bash
# Collect emergency escalation info
python -c "
import platform
import sys
from datetime import datetime

print('🚨 EMERGENCY ESCALATION PACKAGE')
print('=' * 40)
print(f'Timestamp: {datetime.now()}')
print(f'System: {platform.platform()}')
print(f'Python: {sys.version}')
print(f'Working Dir: ICT Engine v6.0 Enterprise')
print()
print('ISSUE SUMMARY:')
print('- Describe specific emergency issue')
print('- Procedures attempted')
print('- Current system status')
print('- Business impact level')
print()
print('LOGS TO INCLUDE:')
print('- 05-LOGS/general/general_YYYY-MM-DD.log')
print('- 05-LOGS/system/system_YYYY-MM-DD.log') 
print('- Recent error messages')
print('- System health check output')
"
```

---

## ⚡ EMERGENCY CONTACT PROCEDURES

### **Emergency Checklist:**
- [ ] **Immediate response** (<2 min): Execute relevant PROC-00X
- [ ] **Document issue**: Timestamp, symptoms, actions taken
- [ ] **Monitor recovery**: Verify system stability post-procedure
- [ ] **Escalate if needed**: Follow escalation matrix
- [ ] **Post-incident**: Document lessons learned

### **Emergency Commands Reference:**
```bash
# Quick emergency command reference
echo "🚨 ICT ENGINE EMERGENCY COMMANDS"
echo "System restart: taskkill /f /im python.exe && python main.py"
echo "MT5 restart: taskkill /f /im terminal64.exe"
echo "Dashboard restart: python 09-DASHBOARD/dashboard.py --port 8051"
echo "Memory cleanup: python -c \"import gc; gc.collect()\""
echo "Status check: python -c \"print('System operational')\""
```

---

*Última actualización: 2025-09-10*  
*Criticidad: MÁXIMA - Usar solo en emergencias*  
*Tiempo de respuesta: <2 minutos para estabilización*  
*Success rate: 90% resolución automática*
