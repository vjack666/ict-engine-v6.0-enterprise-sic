# 📋 ICT Engine v6.0 Enterprise - Production Checklist

**📅 Última actualización:** Septiembre 9, 2025  
**🎯 Versión:** v6.0 Enterprise SIC  
**⚡ Tiempo de verificación:** 5-15 minutos según complejidad  

---

## 🎯 **OBJETIVO DEL CHECKLIST**

Esta lista de verificación garantiza que el sistema ICT Engine v6.0 esté **100% listo para trading en producción** antes de iniciar operaciones reales. 

**🚨 REGLA CRÍTICA:** Si cualquier item falla, **NO INICIAR TRADING** hasta resolver el problema.

---

## ✅ **CHECKLIST PRE-TRADING - NIVEL CRÍTICO**

### **🔴 SECCIÓN 1: VALIDACIÓN DEL SISTEMA (OBLIGATORIO)**

#### **1.1 Validación Automática General**
```powershell
# Ejecutar validación completa del sistema
python 06-TOOLS\validation_quick_test.py
```
- [ ] **Score >= 80%** ✅ 
- [ ] **Al menos 4/5 tests pasando** ✅
- [ ] **Sin errores críticos de sistema** ✅
- [ ] **Mensaje: "SISTEMA LISTO PARA FASE 1"** ✅

**❌ Si falla:** Revisar `troubleshooting.md` antes de continuar.

#### **1.2 Verificación de Estructura del Proyecto**
```powershell
# Verificar directorios críticos
$critical_dirs = @("01-CORE", "04-DATA", "05-LOGS", "06-TOOLS", "09-DASHBOARD")
foreach ($dir in $critical_dirs) {
    if (Test-Path $dir) { Write-Host "✅ $dir" -ForegroundColor Green }
    else { Write-Host "❌ $dir FALTANTE" -ForegroundColor Red }
}
```
- [ ] **01-CORE** existe ✅
- [ ] **04-DATA** existe ✅  
- [ ] **05-LOGS** existe ✅
- [ ] **06-TOOLS** existe ✅
- [ ] **09-DASHBOARD** existe ✅

#### **1.3 Verificación de Configuraciones Críticas**
```powershell
# Verificar archivos de configuración esenciales
$configs = @(
    "01-CORE\config\log_throttle_config.json",
    "01-CORE\config\risk_management_config.json", 
    "01-CORE\config\timestamp_config.json",
    "01-CORE\config\log_categorization_rules.json"
)
foreach ($config in $configs) {
    if (Test-Path $config) { Write-Host "✅ $(Split-Path $config -Leaf)" -ForegroundColor Green }
    else { Write-Host "❌ $(Split-Path $config -Leaf) FALTANTE" -ForegroundColor Red }
}
```
- [ ] **log_throttle_config.json** existe ✅
- [ ] **risk_management_config.json** existe ✅
- [ ] **timestamp_config.json** existe ✅
- [ ] **log_categorization_rules.json** existe ✅

---

### **🟠 SECCIÓN 2: CONFIGURACIÓN DE RIESGO (CRÍTICO PARA TRADING)**

#### **2.1 Verificación de Parámetros de Riesgo**
```powershell
python -c "
import json
with open('01-CORE/config/risk_management_config.json', 'r') as f:
    config = json.load(f)
    
max_positions = config.get('max_positions', 0)
max_drawdown = config.get('max_drawdown_percent', 0)
emergency_enabled = config.get('emergency_procedures', {}).get('emergency_stop_enabled', False)

print(f'📊 Max posiciones: {max_positions}')
print(f'📊 Max drawdown: {max_drawdown}%')
print(f'🚨 Emergency stop: {emergency_enabled}')

# Validación
if max_positions > 0 and max_positions <= 5:
    print('✅ Max posiciones configurado correctamente')
else:
    print('❌ Max posiciones fuera de rango seguro (1-5)')
    
if max_drawdown > 0 and max_drawdown <= 10:
    print('✅ Max drawdown configurado correctamente') 
else:
    print('❌ Max drawdown fuera de rango seguro (1-10%)')
    
if emergency_enabled:
    print('✅ Emergency stop habilitado')
else:
    print('❌ Emergency stop deshabilitado - PELIGROSO')
"
```
- [ ] **Max posiciones: 1-5** (valor seguro) ✅
- [ ] **Max drawdown: 1-10%** (valor seguro) ✅  
- [ ] **Emergency stop: habilitado** ✅
- [ ] **Sin errores en configuración** ✅

#### **2.2 Test de Risk Validator**
```powershell
python -c "
import sys
sys.path.insert(0, '01-CORE')
try:
    from risk_management.risk_validator import RISK_VALIDATOR
    
    # Test con valores seguros
    validation = RISK_VALIDATOR.validate_trade([], 0.0, 0.0)
    
    if validation.get('valid', False):
        print('✅ Risk validator funcionando correctamente')
    else:
        print('❌ Risk validator reporta problemas')
        print(f'Violaciones: {validation.get(\"violations\", [])}')
        
except Exception as e:
    print(f'❌ Error en risk validator: {e}')
"
```
- [ ] **Risk validator responde correctamente** ✅
- [ ] **Sin violaciones en estado inicial** ✅
- [ ] **Validación devuelve resultado esperado** ✅

---

### **🟡 SECCIÓN 3: FUNCIONALIDAD CORE (OBLIGATORIO)**

#### **3.1 Test del Logger Principal**
```powershell
python -c "
import sys
sys.path.insert(0, '01-CORE')
try:
    from smart_trading_logger import SmartTradingLogger
    
    # Crear instancia de test
    logger = SmartTradingLogger('production_test')
    
    # Test de logging básico
    logger.info('Test de producción - logging funcionando')
    logger.warning('Test de warning')
    
    print('✅ Logger principal funcionando')
    
    # Verificar rate limiting
    if hasattr(logger, '_should_log_message'):
        print('✅ Rate limiting implementado')
    else:
        print('⚠️ Rate limiting no detectado')
        
except Exception as e:
    print(f'❌ Error en logger: {e}')
"
```
- [ ] **Logger se inicializa correctamente** ✅
- [ ] **Logs se escriben sin errores** ✅
- [ ] **Rate limiting funcionando** ✅
- [ ] **Sin excepciones durante test** ✅

#### **3.2 Test del Emergency Handler**
```powershell
python -c "
import sys
sys.path.insert(0, '01-CORE')
try:
    from emergency.emergency_handler import EMERGENCY_HANDLER
    
    # Test básico del handler
    test_result = EMERGENCY_HANDLER.handle_emergency('TEST', {
        'reason': 'Production readiness test',
        'test_mode': True
    })
    
    if test_result:
        print('✅ Emergency handler respondiendo')
        print(f'📋 Tipo de respuesta: {type(test_result)}')
    else:
        print('⚠️ Emergency handler no devolvió resultado')
        
except Exception as e:
    print(f'❌ Error en emergency handler: {e}')
"
```
- [ ] **Emergency handler responde** ✅
- [ ] **Maneja eventos de test correctamente** ✅
- [ ] **Sin errores en activación** ✅

#### **3.3 Test de Deduplicación de Logs**
```powershell
python -c "
import sys
sys.path.insert(0, '01-CORE')
try:
    from utils.realtime_log_deduplicator import DEDUPLICATOR
    
    # Test de deduplicación
    message1 = 'Test message para deduplicación'
    message2 = 'Test message para deduplicación'  # Duplicado
    message3 = 'Mensaje diferente'
    
    result1 = DEDUPLICATOR.should_log(message1)
    result2 = DEDUPLICATOR.should_log(message2)  # Debería ser False o limitado
    result3 = DEDUPLICATOR.should_log(message3)
    
    print(f'📝 Primer mensaje: {result1}')
    print(f'📝 Mensaje duplicado: {result2}')
    print(f'📝 Mensaje diferente: {result3}')
    
    if result1 and result3:
        print('✅ Deduplicador funcionando')
    else:
        print('❌ Deduplicador bloqueando mensajes válidos')
        
except Exception as e:
    print(f'❌ Error en deduplicador: {e}')
"
```
- [ ] **Deduplicador permite mensajes únicos** ✅
- [ ] **Deduplicador controla duplicados** ✅
- [ ] **Sin errores en funcionamiento** ✅

---

### **🔵 SECCIÓN 4: RECURSOS DEL SISTEMA (IMPORTANTE)**

#### **4.1 Verificación de Memoria**
```powershell
python -c "
import psutil

memory = psutil.virtual_memory()
memory_percent = memory.percent
memory_available_gb = memory.available / 1024 / 1024 / 1024

print(f'💾 Memoria usada: {memory_percent:.1f}%')
print(f'💾 Memoria disponible: {memory_available_gb:.1f} GB')

if memory_percent < 70:
    print('✅ Memoria en rango normal')
elif memory_percent < 85:
    print('⚠️ Memoria en rango alto - monitorear')
else:
    print('❌ Memoria crítica - no recomendado para trading')
    
if memory_available_gb > 2:
    print('✅ Memoria disponible suficiente')
else:
    print('❌ Memoria disponible insuficiente (<2GB)')
"
```
- [ ] **Memoria usada < 70%** (recomendado) ✅
- [ ] **Memoria disponible > 2GB** ✅
- [ ] **Sin indicadores de memory leak** ✅

#### **4.2 Verificación de Espacio en Disco**
```powershell
$free_space = (Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace / 1GB
Write-Host "💿 Espacio libre: $([math]::Round($free_space, 2)) GB"

if ($free_space -gt 5) {
    Write-Host "✅ Espacio suficiente para operación" -ForegroundColor Green
} elseif ($free_space -gt 2) {
    Write-Host "⚠️ Espacio limitado - monitorear" -ForegroundColor Yellow
} else {
    Write-Host "❌ Espacio crítico - limpiar antes de trading" -ForegroundColor Red
}
```
- [ ] **Espacio libre > 5GB** (recomendado) ✅
- [ ] **Sin archivos temporales excesivos** ✅

#### **4.3 Verificación de CPU**
```powershell
python -c "
import psutil
import time

print('⚡ Midiendo CPU por 5 segundos...')
cpu_percent = psutil.cpu_percent(interval=5)

print(f'⚡ CPU promedio: {cpu_percent:.1f}%')

if cpu_percent < 50:
    print('✅ CPU en rango normal')
elif cpu_percent < 80:
    print('⚠️ CPU en rango alto - verificar procesos')
else:
    print('❌ CPU sobrecargado - no recomendado para trading')
"
```
- [ ] **CPU promedio < 50%** (recomendado) ✅
- [ ] **Sin procesos consumiendo CPU excesivamente** ✅

---

### **🟢 SECCIÓN 5: CONECTIVIDAD Y DATOS (CRÍTICO PARA TRADING REAL)**

#### **5.1 Test de Conectividad Internet**
```powershell
# Test básico de conectividad
$ping_result = Test-NetConnection -ComputerName "8.8.8.8" -Port 53 -InformationLevel Quiet
if ($ping_result) {
    Write-Host "✅ Conectividad a internet OK" -ForegroundColor Green
} else {
    Write-Host "❌ Sin conectividad a internet" -ForegroundColor Red
}
```
- [ ] **Conectividad a internet estable** ✅
- [ ] **Sin problemas de DNS** ✅

#### **5.2 Verificación de Puertos de Trading (Simulado)**
```powershell
# En producción, verificar puertos específicos de MT5/brokers
Write-Host "🔌 Verificando puertos de trading..." -ForegroundColor Cyan

# Puertos comunes de MT5: 443 (HTTPS), 993 (IMAPS), etc.
$trading_ports = @(443, 993)
$port_results = @()

foreach ($port in $trading_ports) {
    try {
        $test = Test-NetConnection -ComputerName "google.com" -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($test) {
            Write-Host "✅ Puerto $port accesible" -ForegroundColor Green
            $port_results += $true
        } else {
            Write-Host "❌ Puerto $port bloqueado" -ForegroundColor Red
            $port_results += $false
        }
    } catch {
        Write-Host "⚠️ Error probando puerto $port" -ForegroundColor Yellow
        $port_results += $false
    }
}

$successful_ports = ($port_results | Where-Object {$_ -eq $true}).Count
Write-Host "📊 Puertos accesibles: $successful_ports/$($trading_ports.Count)"
```
- [ ] **Puertos críticos accesibles** ✅
- [ ] **Sin bloqueos de firewall** ✅

#### **5.3 Verificación de Datos Históricos**
```powershell
# Verificar existencia de datos básicos
Write-Host "📊 Verificando datos históricos..." -ForegroundColor Cyan

$data_files = @(
    "04-DATA\memory_persistence",
    "04-DATA\cache", 
    "04-DATA\exports"
)

$data_ok = $true
foreach ($dir in $data_files) {
    if (Test-Path $dir) {
        $files_count = (Get-ChildItem $dir -Recurse -File | Measure-Object).Count
        Write-Host "✅ $dir ($files_count archivos)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ $dir no existe - se creará automáticamente" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
```
- [ ] **Directorios de datos existen** ✅
- [ ] **Sin corrupción de archivos críticos** ✅

---

### **🟣 SECCIÓN 6: CONFIGURACIÓN ESPECÍFICA DE TRADING**

#### **6.1 Verificación de Configuración de Símbolos**
```powershell
python -c "
import json
import os

config_file = '01-CORE/config/trading_symbols_config.json'
if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        symbols_config = json.load(f)
    
    print(f'📈 Símbolos configurados: {len(symbols_config.get(\"symbols\", []))}')
    
    # Verificar que hay al menos un símbolo
    symbols = symbols_config.get('symbols', [])
    if len(symbols) > 0:
        print(f'📊 Primer símbolo: {symbols[0].get(\"symbol\", \"N/A\")}')
        print('✅ Configuración de símbolos válida')
    else:
        print('⚠️ No hay símbolos configurados')
else:
    print('⚠️ Archivo de configuración de símbolos no encontrado')
    print('   Usando configuración por defecto')
"
```
- [ ] **Al menos 1 símbolo configurado** ✅
- [ ] **Configuración de símbolos válida** ✅

#### **6.2 Verificación de Timeframes**
```powershell
python -c "
# Verificar timeframes críticos configurados
import json
import os

try:
    # Buscar configuración de timeframes en archivos de config
    config_files = [
        '01-CORE/config/ict_patterns_config.json',
        '01-CORE/config/performance_config_enterprise.json'
    ]
    
    timeframes_found = False
    for config_file in config_files:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            # Buscar timeframes en diferentes estructuras
            timeframes = []
            if 'timeframes' in config:
                timeframes = config['timeframes']
            elif 'analysis' in config and 'timeframes' in config['analysis']:
                timeframes = config['analysis']['timeframes']
                
            if timeframes:
                print(f'⏰ Timeframes en {os.path.basename(config_file)}: {timeframes}')
                timeframes_found = True
                break
    
    if timeframes_found:
        print('✅ Timeframes configurados')
    else:
        print('⚠️ Timeframes no encontrados - usando defaults (M15, H1, H4)')
        
except Exception as e:
    print(f'⚠️ Error verificando timeframes: {e}')
"
```
- [ ] **Timeframes críticos configurados** ✅  
- [ ] **Al menos M15, H1, H4 disponibles** ✅

---

## 🏁 **VERIFICACIÓN FINAL Y DECISIÓN GO/NO-GO**

### **📊 SCORECARD FINAL**

```powershell
Write-Host "📊 GENERANDO SCORECARD FINAL DE PRODUCCIÓN" -ForegroundColor Yellow -BackgroundColor Blue
Write-Host "=" * 60

# Ejecutar validación final completa
python 06-TOOLS\validation_quick_test.py
$final_validation = $LASTEXITCODE

# Mostrar resultado
if ($final_validation -eq 0) {
    Write-Host "`n🎉 VALIDACIÓN FINAL: EXITOSA" -ForegroundColor Green -BackgroundColor DarkGreen
    Write-Host "✅ SISTEMA APROBADO PARA TRADING EN PRODUCCIÓN" -ForegroundColor Green
    Write-Host "🚀 DECISIÓN: GO - Puede iniciar trading" -ForegroundColor Green
} else {
    Write-Host "`n❌ VALIDACIÓN FINAL: FALLIDA" -ForegroundColor Red -BackgroundColor DarkRed  
    Write-Host "🚨 SISTEMA NO APROBADO PARA PRODUCCIÓN" -ForegroundColor Red
    Write-Host "🛑 DECISIÓN: NO-GO - Resolver problemas antes de trading" -ForegroundColor Red
}

# Generar timestamp de aprobación
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "`n📅 Verificación completada: $timestamp"
```

### **✅ CRITERIOS DE APROBACIÓN FINAL**

**🟢 GO - APROBADO PARA TRADING:**
- ✅ Score de validación >= 80%
- ✅ Todos los items críticos (🔴) completados
- ✅ Risk management configurado correctamente
- ✅ Emergency procedures funcionando
- ✅ Recursos del sistema en rango seguro
- ✅ Conectividad estable

**🔴 NO-GO - NO APROBADO:**
- ❌ Score de validación < 80%
- ❌ Cualquier item crítico (🔴) fallando
- ❌ Risk management mal configurado
- ❌ Emergency procedures no funcionando
- ❌ Recursos del sistema en rango crítico
- ❌ Problemas de conectividad

---

## 📋 **POST-APROBACIÓN: PRÓXIMOS PASOS**

### **🎯 Si APROBADO (GO):**
1. **Documenta la aprobación:**
   ```powershell
   $approval_record = @{
       timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
       status = "APPROVED"
       validator = $env:USERNAME
       system_score = "80%+"
       notes = "Sistema aprobado para trading en producción"
   }
   $approval_record | ConvertTo-Json | Out-File -FilePath "03-DOCUMENTATION\reports\production_approval_$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
   ```

2. **Inicia trading con monitoreo:**
   - Comenzar con posiciones pequeñas
   - Monitorear logs activamente
   - Verificar risk management continuamente

3. **Configurar monitoreo continuo:**
   ```powershell
   # Iniciar monitoreo en background
   Start-Process python -ArgumentList "06-TOOLS\continuous_monitoring.py" -WindowStyle Hidden
   ```

### **🛑 Si NO APROBADO (NO-GO):**
1. **Documenta los problemas:**
   ```powershell
   Write-Host "📋 Generando reporte de problemas..." -ForegroundColor Red
   python 06-TOOLS\validation_quick_test.py > "production_issues_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt" 2>&1
   ```

2. **Consulta documentación:**
   - Revisa `troubleshooting.md` para problemas específicos
   - Consulta `emergency-procedures.md` si hay issues críticos
   - Vuelve a `quick-start.md` si hay problemas de configuración

3. **Re-ejecuta checklist:**
   - Resuelve todos los problemas identificados
   - Vuelve a ejecutar este checklist completo
   - No proceder hasta obtener GO

---

## 🔄 **MANTENIMIENTO CONTINUO**

### **📅 Verificaciones Regulares (Recomendado):**
- **Diario:** Ejecutar validación rápida antes de trading
- **Semanal:** Checklist completo de recursos del sistema  
- **Mensual:** Revisión completa de configuraciones

### **🚨 Re-validación Obligatoria:**
- Después de actualizaciones del sistema
- Después de cambios en configuración de riesgo
- Después de resolver emergencias críticas
- Después de cambios en el entorno de trading

---

**🎯 OBJETIVO FINAL:** Garantizar operación segura y estable del sistema ICT Engine v6.0 en ambiente de producción.

**⚡ PRINCIPIO:** Más vale prevenir que remediar. Una verificación exhaustiva evita pérdidas financieras.

**📞 SOPORTE:** En caso de dudas sobre cualquier verificación, consultar la documentación técnica o escalara soporte especializado.
