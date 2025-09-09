# 🔍 debug_connections.py - Herramienta de Diagnóstico MT5

**📁 Ubicación:** `06-TOOLS/debug_connections.py`  
**🎯 Propósito:** Diagnóstico completo de conexiones y módulos MT5 del ICT Engine v6.0  
**📅 Actualizado:** Septiembre 9, 2025  

---

## 🚀 **FUNCIONALIDADES**

### **🔧 1. test_mt5_system_modules()**
Diagnóstico de módulos MT5 integrados en el sistema:
- ✅ **MT5 Data Manager** - Verificación de disponibilidad y conexión
- ✅ **MT5 Connection Manager** - Estado de conexión y métodos disponibles  
- ✅ **MT5 Directo** - Prueba de importación y inicialización directa

### **⚙️ 2. test_system_configuration()**
Verificación de configuraciones del sistema:
- 📋 **Archivos de configuración** - Búsqueda en directorios del sistema
- 🔧 **Configuraciones MT5/Trading** - Identificación de configs específicas
- 📁 **Rutas de configuración** - Validación de paths

### **🚨 3. test_emergency_procedures()**
Validación de procedimientos de emergencia:
- 🚨 **Emergency Handler** - Verificación de disponibilidad
- 💰 **Risk Validator** - Validación de métodos críticos
- ✅ **Métodos críticos** - Test de funciones esenciales

---

## 📋 **USO**

### **🖥️ Ejecución:**
```powershell
# Desde el directorio raíz del proyecto
python 06-TOOLS/debug_connections.py

# O desde 06-TOOLS
cd 06-TOOLS
python debug_connections.py
```

### **📊 Salida Esperada:**
```
🔍 ICT ENGINE v6.0 - DIAGNÓSTICO COMPLETO DE CONEXIONES
============================================================

=== DIAGNÓSTICO DE MÓDULOS MT5 DEL SISTEMA ===
Timestamp: 2025-09-09 17:45:00.123456
--------------------------------------------------

1. VERIFICANDO MT5 DATA MANAGER:
   MT5 disponible: True/False
   MT5 Manager creado: True/False
   Métodos disponibles: X

2. VERIFICANDO MT5 CONNECTION MANAGER:
   Connection Manager creado: True
   Estado de conexión: {...}
   Métodos disponibles: X

3. VERIFICANDO MT5 DIRECTO:
   MetaTrader5 importado correctamente
   Inicialización: True/False

=== VERIFICANDO CONFIGURACIONES DEL SISTEMA ===
Configuraciones encontradas: X
   ✅ ../01-CORE/config/...

=== VERIFICANDO PROCEDIMIENTOS DE EMERGENCIA ===
   ✅ Emergency Handler disponible
   ✅ Risk Validator disponible
   ✅ handle_emergency - DISPONIBLE

============================================================
✅ DIAGNÓSTICO COMPLETADO - SISTEMA OPERATIVO
============================================================
```

---

## 🔧 **DEPENDENCIAS**

### **📦 Módulos del Sistema:**
- `data_management.mt5_data_manager` - Manager principal de MT5
- `data_management.mt5_connection_manager` - Gestor de conexiones
- `emergency.emergency_handler` - Handler de emergencias
- `risk_management.risk_validator` - Validador de riesgo

### **📚 Módulos Externos:**
- `MetaTrader5` (opcional) - Para pruebas directas
- `sys`, `os`, `datetime` - Módulos estándar

---

## 🎯 **CASOS DE USO**

### **🔍 Diagnóstico General:**
- Verificar estado del sistema antes de trading
- Validar conexiones MT5 después de reinstalación
- Troubleshooting de problemas de conectividad

### **🛠️ Desarrollo:**
- Verificar módulos durante desarrollo
- Validar configuraciones nuevas
- Test de funcionalidades MT5

### **🚨 Emergencias:**
- Diagnóstico rápido durante problemas
- Verificación de procedimientos de emergencia
- Validación del estado del sistema

---

## ⚠️ **NOTAS IMPORTANTES**

### **🔐 Seguridad:**
- No modifica configuraciones del sistema
- Solo lee y verifica estado
- No ejecuta operaciones de trading

### **🏥 Troubleshooting:**
- Si MT5 no está disponible, mostrará advertencias pero continuará
- Errores de importación son manejados gracefully
- Proporciona información detallada para debugging

### **📈 Performance:**
- Ejecución rápida (< 5 segundos típicamente)
- No impacta sistemas en producción
- Safe para ejecutar durante trading activo

---

## 📝 **HISTORIAL DE CAMBIOS**

### **v2.0 - Septiembre 9, 2025:**
- ✅ Movido de 09-DASHBOARD a 06-TOOLS
- ✅ Reescrito para usar módulos MT5 del sistema
- ✅ Agregado diagnóstico de procedimientos de emergencia
- ✅ Mejorado manejo de errores
- ✅ Removidas dependencias obsoletas (patterns_orchestrator)

### **v1.0 - Original:**
- Diagnóstico básico de conexiones
- Dependencia de patterns_orchestrator
- Ubicación en dashboard

---

**🛠️ Herramienta de diagnóstico profesional para ICT Engine v6.0 Enterprise**  
**📋 Esencial para mantenimiento y troubleshooting del sistema**
