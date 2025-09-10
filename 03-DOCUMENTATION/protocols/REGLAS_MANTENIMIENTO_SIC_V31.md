# 🔧 REGLAS DE MANTENIMIENTO: BRIDGE SIC v3.1 ENTERPRISE

**Documento**: ICT-MAINT-SIC-001  
**Versión**: 1.0  
**Fecha**: 2 Septiembre 2025  
**Estado**: ACTIVO  

---

## 🎯 **REGLAS OBLIGATORIAS DE MANTENIMIENTO**

### **1. VERIFICACIÓN DIARIA** ⚠️ **CRÍTICO**

#### **Comando de Verificación Rápida**
```bash
# Ejecutar DIARIAMENTE antes de cualquier desarrollo
cd "c:\Users\v_jac\Desktop\itc engine v5.0\ict-engine-v6.0-enterprise-sic"
python -c "from sistema.sic_v3_1 import SICv31Enterprise; sic = SICv31Enterprise(); stats = sic.get_system_stats(); print(f'SIC v3.1 Status: {stats[\"status\"]} | ImportCenter: {stats[\"import_center_available\"]} | Base: {stats[\"base_sic_available\"]}')"
```

#### **Resultado Esperado**
```
✅ SIC v3.1 Status: active | ImportCenter: True | Base: True
```

#### **Si hay problemas:**
```bash
# Reinstalar automáticamente
python install_sic_v31_import_center.py
```

### **2. MONITOREO DE WARNINGS** ⚠️ **OBLIGATORIO**

#### **Verificar Módulos Críticos**
```bash
# PatternDetector
python -c "from core.analysis.pattern_detector import PatternDetector; print('✅ PatternDetector OK')"

# MT5DataManager  
python -c "from utils.mt5_data_manager import MT5DataManager; print('✅ MT5DataManager OK')"

# MultiTimeframeAnalyzer
python -c "from core.analysis.multi_timeframe_analyzer import MultiTimeframeAnalyzer; print('✅ MultiTimeframeAnalyzer OK')"
```

#### **❌ Si aparece warning "Sistema SIC v3.1 no disponible":**
1. **PARAR todo desarrollo inmediatamente**
2. Ejecutar reinstalación: `python install_sic_v31_import_center.py`
3. Verificar con comando de verificación rápida
4. Solo continuar cuando status = "active"

### **3. ACTUALIZACIONES DEL SISTEMA** ⚠️ **CRÍTICO**

#### **Antes de cualquier cambio mayor:**
```bash
# 1. Backup del estado actual
python -c "from sistema.sic_v3_1 import SICv31Enterprise; sic = SICv31Enterprise(); import json; stats = sic.get_system_stats(); print('Backup stats:', json.dumps(stats, indent=2))" > backup_sic_v31_$(date +%Y%m%d).json

# 2. Verificar ImportCenter
python -c "from utils.import_center import ImportCenter; ic = ImportCenter(); print('ImportCenter verification:', ic.verify_installation())"

# 3. Solo proceder si todo está ✅
```

#### **Después de cualquier cambio:**
```bash
# Verificación post-cambio OBLIGATORIA
python install_sic_v31_import_center.py
```

---

## 📋 **PROTOCOLO DE RESOLUCIÓN DE PROBLEMAS**

### **🚨 PROBLEMA: Warning SIC v3.1 reaparece**

#### **Diagnóstico Paso a Paso:**
```bash
# 1. Verificar si existe el módulo
ls "c:\Users\v_jac\Desktop\proyecto principal\docs\sistema\sic_v3_1\"

# 2. Verificar contenido de archivos
python -c "import sys; sys.path.insert(0, 'c:/Users/v_jac/Desktop/proyecto principal/docs'); import sistema.sic_v3_1; print('Módulo existe:', sistema.sic_v3_1.__version__)"

# 3. Verificar ImportCenter
python -c "from utils.import_center import ImportCenter; ic = ImportCenter(); print('ImportCenter OK:', ic.verify_installation())"
```

#### **Solución Automática:**
```bash
# Reinstalación completa
cd "c:\Users\v_jac\Desktop\itc engine v5.0\ict-engine-v6.0-enterprise-sic"
python install_sic_v31_import_center.py
```

### **🚨 PROBLEMA: ImportError en SIC v3.1**

#### **Diagnóstico:**
```bash
# Verificar paths del sistema
python -c "import sys; print('Paths:', [p for p in sys.path if 'proyecto principal' in p or 'itc engine' in p])"

# Verificar módulo base SIC
python -c "import sys; sys.path.insert(0, 'c:/Users/v_jac/Desktop/proyecto principal/docs'); from sistema import sic; print('SIC base OK')"
```

#### **Solución:**
1. Verificar que `proyecto principal/docs/sistema/sic.py` existe
2. Reinstalar bridge: `python install_sic_v31_import_center.py`
3. Si persiste, verificar permisos de archivos

### **🚨 PROBLEMA: ImportCenter no disponible**

#### **Diagnóstico:**
```bash
# Verificar ImportCenter
ls "c:\Users\v_jac\Desktop\itc engine v5.0\ict-engine-v6.0-enterprise-sic\01-CORE\utils\import_center.py"

python -c "import sys; sys.path.insert(0, 'c:/Users/v_jac/Desktop/itc engine v5.0/ict-engine-v6.0-enterprise-sic/01-CORE'); from utils.import_center import ImportCenter; print('ImportCenter OK')"
```

#### **Solución:**
1. Verificar que archivo `utils/import_center.py` existe
2. Verificar paths en el script instalador
3. Reinstalar si es necesario

---

## 🔄 **RUTINAS DE MANTENIMIENTO PROGRAMADAS**

### **📅 DIARIO** (Antes de comenzar desarrollo)
```bash
# Script de verificación diaria
#!/bin/bash
echo "🔍 Verificación SIC v3.1 - $(date)"

# Test básico
python -c "from sistema.sic_v3_1 import SICv31Enterprise; sic = SICv31Enterprise(); stats = sic.get_system_stats(); exit(0 if stats['status'] == 'active' else 1)"

if [ $? -eq 0 ]; then
    echo "✅ SIC v3.1 funcionando correctamente"
else
    echo "❌ SIC v3.1 requiere atención - ejecutando reinstalación"
    python install_sic_v31_import_center.py
fi
```

### **📅 SEMANAL** (Lunes antes de trabajo)
```bash
# Verificación completa semanal
echo "🔍 Verificación semanal SIC v3.1 - $(date)"

# 1. Test de todos los módulos críticos
python -c "from core.analysis.pattern_detector import PatternDetector; print('✅ PatternDetector')"
python -c "from utils.mt5_data_manager import MT5DataManager; print('✅ MT5DataManager')"
python -c "from core.analysis.multi_timeframe_analyzer import MultiTimeframeAnalyzer; print('✅ MultiTimeframeAnalyzer')"

# 2. Estadísticas completas
python -c "from sistema.sic_v3_1 import SICv31Enterprise; sic = SICv31Enterprise(); import json; print('Stats:', json.dumps(sic.get_system_stats(), indent=2))"

# 3. Diagnósticos ImportCenter
python -c "from sistema.sic_v3_1 import SICv31Enterprise; sic = SICv31Enterprise(); print('ImportCenter Diagnostics:', sic.get_import_center_diagnostics())"
```

### **📅 MENSUAL** (Primer día del mes)
```bash
# Mantenimiento completo mensual
echo "🔧 Mantenimiento mensual SIC v3.1 - $(date)"

# 1. Backup de configuración actual
python -c "from sistema.sic_v3_1 import SICv31Enterprise; sic = SICv31Enterprise(); import json; open(f'backup_sic_v31_{datetime.now().strftime(\"%Y%m%d\")}.json', 'w').write(json.dumps(sic.get_system_stats(), indent=2))"

# 2. Reinstalación preventiva
python install_sic_v31_import_center.py

# 3. Verificación completa
python -c "
from sistema.sic_v3_1 import SICv31Enterprise, AdvancedDebugger
sic = SICv31Enterprise()
debugger = AdvancedDebugger()
print('✅ Mantenimiento mensual completado')
print('SIC Status:', sic.get_system_stats()['status'])
print('Debug Stats:', debugger.get_debug_summary())
"
```

---

## 📁 **ARCHIVOS CRÍTICOS A MONITOREAR**

### **🔒 NUNCA MODIFICAR MANUALMENTE:**
```
c:/Users/v_jac/Desktop/proyecto principal/docs/sistema/sic_v3_1/__init__.py
c:/Users/v_jac/Desktop/proyecto principal/docs/sistema/sic_v3_1/enterprise_interface.py
c:/Users/v_jac/Desktop/proyecto principal/docs/sistema/sic_v3_1/advanced_debug.py
```

### **✅ SOLO MODIFICAR VIA INSTALADOR:**
- Usar siempre: `install_sic_v31_import_center.py`
- NUNCA editar archivos del bridge directamente
- Si necesitas cambios, modifica el instalador y re-ejecuta

### **📊 ARCHIVOS DE MONITOREO:**
```
01-CORE/utils/import_center.py                    # ImportCenter principal
03-DOCUMENTATION/protocols/COPILOT_PROTOCOLO_SIC_V31_BRIDGE.md    # Protocolo Copilot
03-DOCUMENTATION/reports/IMPLEMENTACION_BRIDGE_SIC_V31_COMPLETADA.md    # Documentación
04-development-logs/integration/BITACORA_BRIDGE_SIC_V31.md    # Bitácora
```

---

## 🚨 **SEÑALES DE ALERTA**

### **🔴 ALERTA CRÍTICA - PARAR TODO:**
- Warning: "Sistema SIC v3.1 no disponible (usando fallback)"
- ImportError en `from sistema.sic_v3_1`
- Status != "active" en verificación diaria

### **🟡 ALERTA MEDIA - INVESTIGAR:**
- ImportCenter: False en stats
- Warnings en PatternDetector o MT5DataManager
- Errores en AdvancedDebugger

### **🟢 NORMAL:**
- Status: "active"
- ImportCenter: True
- Base SIC: True
- Sin warnings en módulos críticos

---

## 📋 **CHECKLIST DE EMERGENCIA**

### **Si el sistema no funciona (Status != "active"):**
- [ ] Verificar que `proyecto principal/docs/sistema/sic.py` existe
- [ ] Verificar que `utils/import_center.py` existe  
- [ ] Ejecutar: `python install_sic_v31_import_center.py`
- [ ] Verificar resultado con comando de verificación rápida
- [ ] Si persiste, contactar equipo de desarrollo

### **Si aparecen warnings después de cambios:**
- [ ] Identificar qué módulo muestra warnings
- [ ] Verificar que usa imports correctos de SIC v3.1
- [ ] Ejecutar reinstalación del bridge
- [ ] Probar módulo específico individualmente
- [ ] Documentar en bitácora si es un problema nuevo

---

## 📞 **CONTACTO Y SOPORTE**

**Responsable**: ICT Engine v6.0 Enterprise Team  
**Documentación**: `03-DOCUMENTATION/`  
**Instalador**: `install_sic_v31_import_center.py`  
**Última actualización**: 2 Septiembre 2025  

**En caso de problemas críticos**: Ejecutar instalador automáticamente y documentar en bitácora.

---

## ⚠️ **IMPORTANTE**

**Estas reglas son OBLIGATORIAS y CRÍTICAS para el funcionamiento del sistema.**  
**NO omitir verificaciones diarias.**  
**SIEMPRE usar el instalador para cambios.**  
**DOCUMENTAR cualquier problema en la bitácora.**
