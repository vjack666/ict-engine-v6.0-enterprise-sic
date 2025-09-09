# 🚀 ICT Engine v6.0 Enterprise - Quick Start Guide

**📅 Última actualización:** Septiembre 9, 2025  
**🎯 Versión:** v6.0 Enterprise SIC  
**⚡ Tiempo estimado:** 5-10 minutos  

---

## 🎯 **OBJETIVO**

Esta guía te permitirá **arrancar el sistema ICT Engine v6.0 en menos de 10 minutos** con todas las configuraciones críticas validadas y funcionando correctamente.

---

## ✅ **PRE-REQUISITOS VALIDADOS**

Antes de comenzar, verifica que tienes:

- ✅ **Python 3.8+** instalado y funcionando
- ✅ **Windows PowerShell** (recomendado) o terminal similar
- ✅ **Permisos de escritura** en el directorio del proyecto
- ✅ **Conexión a internet** para validaciones de mercado (opcional)

---

## ⚡ **ARRANQUE RÁPIDO - 3 COMANDOS ESENCIALES**

### **1️⃣ NAVEGACIÓN AL PROYECTO**
```powershell
# Navegar al directorio principal
cd ict-engine-v6.0-enterprise-sic

# Verificar estructura del proyecto
Get-ChildItem -Directory | Select-Object Name
```

**✅ Resultado esperado:**
```
Name
----
00-ROOT
01-CORE
03-DOCUMENTATION
04-DATA
05-LOGS
06-TOOLS
07-DEPLOYMENT
08-ARCHIVE
09-DASHBOARD
```

### **2️⃣ VALIDACIÓN DEL SISTEMA**
```powershell
# Ejecutar validación rápida del sistema
python 06-TOOLS\validation_quick_test.py
```

**✅ Resultado esperado:**
- Score >= 80%
- Al menos 4/5 tests pasando
- Mensaje: "SISTEMA LISTO PARA FASE 1"

### **3️⃣ ARRANQUE DEL SISTEMA PRINCIPAL**
```powershell
# Iniciar el sistema ICT Engine
python main.py
```

**✅ Resultado esperado:**
- Inicio sin errores críticos
- Carga de configuraciones exitosa
- Logger funcionando correctamente

---

## 🔧 **CONFIGURACIONES CRÍTICAS VERIFICADAS**

El sistema ha sido pre-configurado con los siguientes componentes estabilizados:

### **📁 Configuraciones Core (01-CORE/config/)**
```
✅ log_throttle_config.json           - Control de rate limiting
✅ risk_management_config.json        - Gestión de riesgo
✅ timestamp_config.json              - Estandarización temporal
✅ log_categorization_rules.json      - Categorización automática
```

### **🛠️ Utilidades del Sistema**
```
✅ realtime_log_deduplicator.py       - Prevención de spam de logs
✅ log_categorizer.py                 - Categorización inteligente
✅ risk_validator.py                  - Validación de trading
✅ emergency_handler.py               - Manejo de emergencias
```

---

## 📊 **MODOS DE OPERACIÓN DISPONIBLES**

### **🧪 MODO TESTING (Recomendado para inicio)**
```powershell
# Sistema completo con validaciones
python run_complete_system.py
```

### **💼 MODO REAL MARKET**
```powershell
# ⚠️ SOLO para trading real - requiere configuración adicional
python run_real_market_system.py
```

### **📊 DASHBOARD INTERACTIVO**
```powershell
# Interface visual del sistema
python 09-DASHBOARD\launch_dashboard.py
```

---

## 🚨 **VERIFICACIONES POST-ARRANQUE**

Después del arranque exitoso, verifica:

### **1️⃣ LOGS FUNCIONANDO**
```powershell
# Verificar generación de logs
Get-ChildItem "04-DATA\logs\" -Name "*.log" | Select-Object -First 5
```

### **2️⃣ STATUS DEL SISTEMA**
```powershell
# Verificar archivos de estado
Get-ChildItem "04-DATA\status\" -Name "*.json" | Select-Object -First 3
```

### **3️⃣ MEMORIA OPERATIVA**
```powershell
# Verificar sistema de memoria
Test-Path "04-DATA\memory_persistence\fvg_memory.json"
```

---

## ⚠️ **SOLUCIÓN RÁPIDA DE PROBLEMAS COMUNES**

### **❌ Error: ModuleNotFoundError**
```powershell
# Instalar dependencias
pip install -r 00-ROOT\requirements.txt
```

### **❌ Error: Permisos de archivo**
```powershell
# Verificar permisos (ejecutar como administrador si es necesario)
icacls . /grant Everyone:F
```

### **❌ Error: Configuración faltante**
```powershell
# Re-ejecutar validación para verificar archivos
python 06-TOOLS\validation_quick_test.py
```

---

## 🎯 **COMANDOS DE VALIDACIÓN RÁPIDA**

### **✅ Verificación completa en 30 segundos:**
```powershell
# 1. Estructura del proyecto
Write-Host "📁 Verificando estructura..." -ForegroundColor Green
Get-ChildItem -Directory | Measure-Object | Select-Object Count

# 2. Configuraciones críticas
Write-Host "⚙️ Verificando configs..." -ForegroundColor Green
Get-ChildItem "01-CORE\config\*.json" | Measure-Object | Select-Object Count

# 3. Sistema principal
Write-Host "🚀 Validando sistema..." -ForegroundColor Green
python 06-TOOLS\validation_quick_test.py
```

---

## 📈 **PRÓXIMOS PASOS RECOMENDADOS**

Una vez que el sistema esté funcionando:

1. **📖 Leer** `troubleshooting.md` para problemas específicos
2. **🚨 Revisar** `emergency-procedures.md` para manejo de crisis
3. **📋 Usar** `production-checklist.md` antes de trading real
4. **📊 Explorar** el dashboard para monitoreo visual

---

## 🏆 **CRITERIOS DE ÉXITO**

**✅ ARRANQUE EXITOSO si:**
- Validación score >= 80%
- Sin errores críticos al inicio
- Logs generándose correctamente
- Dashboard accesible (si se ejecuta)

**🚨 SOLICITAR AYUDA si:**
- Score < 80% en validación
- Errores críticos persistentes
- Fallos en configuraciones core

---

## 📞 **SOPORTE TÉCNICO RÁPIDO**

### **🔧 Auto-diagnóstico:**
```powershell
python 06-TOOLS\validation_quick_test.py
```

### **🧹 Limpieza rápida:**
```powershell
python 06-TOOLS\clean_test_logs.py
```

### **📊 Status completo:**
```powershell
python 06-TOOLS\system_status_check.py
```

---

**🎯 ¡SISTEMA LISTO PARA OPERACIÓN!**

> 💡 **Tip:** Mantén este documento abierto durante tu primera sesión para referencia rápida.
