# 🤖 PROTOCOLO GITHUB COPILOT: BRIDGE SIC v3.1 ENTERPRISE

**Protocolo**: ICT-SIC-BRIDGE-001  
**Versión**: 1.0  
**Fecha**: 2 Septiembre 2025  
**Estado**: ACTIVO  

---

## 🎯 **REGLAS OBLIGATORIAS PARA COPILOT**

### **1. IMPORTS SIC v3.1** ⚠️ **CRÍTICO**
```python
# ✅ SIEMPRE usar esta estructura para SIC v3.1
from sistema.sic_v3_1.enterprise_interface import SICv31Enterprise, SICEnterpriseInterface
from sistema.sic_v3_1.advanced_debug import AdvancedDebugger

# ❌ NUNCA usar imports directos como:
# from sistema.sic_v3_1 import *  # NO HACER
# import sistema.sic_v3_1.algo   # NO HACER
```

### **2. INICIALIZACIÓN ESTÁNDAR** ⚠️ **OBLIGATORIO**
```python
# ✅ Patrón estándar de inicialización
def initialize_sic_v31():
    """Inicializar SIC v3.1 Enterprise con ImportCenter"""
    try:
        sic = SICv31Enterprise()
        
        # Verificar estado
        stats = sic.get_system_stats()
        if stats['status'] != 'active':
            print(f"⚠️ SIC v3.1 en modo fallback: {stats['status']}")
        
        return sic
    except ImportError as e:
        print(f"❌ Error importando SIC v3.1: {e}")
        return None

# Uso en módulos
sic_enterprise = initialize_sic_v31()
```

### **3. IMPORTS INTELIGENTES** ⚠️ **RECOMENDADO**
```python
# ✅ Usar el sistema de imports inteligentes
def safe_import_with_sic(module_name: str):
    """Import seguro usando SIC v3.1 Enterprise"""
    if sic_enterprise:
        return sic_enterprise.smart_import(module_name)
    else:
        # Fallback tradicional
        try:
            return __import__(module_name)
        except ImportError:
            return None
```

### **4. DEBUGGING ENTERPRISE** ⚠️ **OBLIGATORIO**
```python
# ✅ Configurar debugging enterprise en nuevos módulos
def setup_enterprise_debugging():
    """Configurar debugging avanzado"""
    try:
        from sistema.sic_v3_1.advanced_debug import AdvancedDebugger
        
        debugger = AdvancedDebugger({
            'debug_level': 'INFO',
            'session_id': f'copilot_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        })
        
        return debugger
    except ImportError:
        print("⚠️ AdvancedDebugger no disponible - usando logging básico")
        return None

# Usar en funciones críticas
debugger = setup_enterprise_debugging()
if debugger:
    debugger.log_import_debug('mi_modulo', 'enterprise', 'inicializacion', 0.001, True)
```

---

## 🔧 **PATRONES DE CÓDIGO ESTÁNDAR**

### **Patrón 1: Módulo con SIC v3.1 Integration**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÓDULO ENTERPRISE CON SIC v3.1
Plantilla estándar para nuevos módulos.
"""

import sys
from typing import Optional, Any

# SIC v3.1 Enterprise Integration
try:
    from sistema.sic_v3_1.enterprise_interface import SICv31Enterprise
    from sistema.sic_v3_1.advanced_debug import AdvancedDebugger
    SIC_V31_AVAILABLE = True
except ImportError:
    print("⚠️ SIC v3.1 no disponible - funcionalidad limitada")
    SIC_V31_AVAILABLE = False

class MiModuloEnterprise:
    """Clase enterprise con integración SIC v3.1"""
    
    def __init__(self):
        self.sic_enterprise = None
        self.debugger = None
        
        if SIC_V31_AVAILABLE:
            self._initialize_enterprise_features()
    
    def _initialize_enterprise_features(self):
        """Inicializar características enterprise"""
        try:
            # SIC v3.1 Enterprise
            self.sic_enterprise = SICv31Enterprise()
            
            # Advanced Debugger
            self.debugger = AdvancedDebugger({
                'debug_level': 'INFO',
                'module_name': self.__class__.__name__
            })
            
            print(f"✅ {self.__class__.__name__} Enterprise: SIC v3.1 conectado")
            
        except Exception as e:
            print(f"⚠️ Error inicializando enterprise features: {e}")
    
    def smart_import_dependency(self, module_name: str) -> Optional[Any]:
        """Import inteligente usando SIC v3.1"""
        if self.sic_enterprise:
            return self.sic_enterprise.smart_import(module_name)
        
        # Fallback tradicional
        try:
            return __import__(module_name)
        except ImportError:
            return None
```

### **Patrón 2: Función con Enterprise Debugging**
```python
def funcion_enterprise(param1, param2):
    """Función con debugging enterprise integrado"""
    
    # Setup debugging
    if debugger:
        debugger.log_import_debug(
            module_name=__name__,
            import_type='function_call',
            operation='funcion_enterprise',
            duration=0.0,
            success=True,
            details={'params': [param1, param2]}
        )
    
    try:
        # Lógica de la función
        resultado = procesar_datos(param1, param2)
        
        if debugger:
            debugger.debug(f"Función completada exitosamente: {resultado}", 'INFO')
        
        return resultado
        
    except Exception as e:
        if debugger:
            debugger.diagnose_import_problem(__name__, e)
        raise
```

### **Patrón 3: Inicialización de Módulo**
```python
# ✅ Incluir siempre al final de nuevos módulos
def initialize_module():
    """Inicialización estándar del módulo"""
    global sic_enterprise, debugger
    
    if SIC_V31_AVAILABLE:
        try:
            sic_enterprise = SICv31Enterprise()
            debugger = AdvancedDebugger({'module_name': __name__})
            
            stats = sic_enterprise.get_system_stats()
            print(f"✅ Módulo {__name__} - SIC v3.1: {stats['status']}")
            
        except Exception as e:
            print(f"⚠️ Error en inicialización enterprise: {e}")

# Auto-inicialización
if __name__ == "__main__":
    initialize_module()
else:
    # Inicialización automática al importar
    initialize_module()
```

---

## 🚨 **ERRORES COMUNES Y CÓMO EVITARLOS**

### **❌ Error 1: Import Directo Incorrecto**
```python
# ❌ NO HACER
from sistema.sic_v3_1 import *

# ✅ CORRECTO
from sistema.sic_v3_1.enterprise_interface import SICv31Enterprise
```

### **❌ Error 2: No Verificar Disponibilidad**
```python
# ❌ NO HACER - Puede fallar
sic = SICv31Enterprise()

# ✅ CORRECTO - Siempre verificar
try:
    sic = SICv31Enterprise()
    if sic.get_system_stats()['status'] != 'active':
        print("⚠️ SIC v3.1 en modo fallback")
except ImportError:
    print("❌ SIC v3.1 no disponible")
    sic = None
```

### **❌ Error 3: No Usar ImportCenter**
```python
# ❌ NO HACER - Import directo
import modulo_personalizado

# ✅ CORRECTO - Usar SIC v3.1
if sic_enterprise:
    modulo = sic_enterprise.smart_import('modulo_personalizado')
else:
    modulo = __import__('modulo_personalizado')
```

---

## 📋 **CHECKLIST PARA NUEVOS DESARROLLOS**

### **✅ Pre-desarrollo**
- [ ] Verificar que SIC v3.1 está instalado
- [ ] Incluir imports estándar de SIC v3.1
- [ ] Configurar AdvancedDebugger
- [ ] Definir estructura del módulo

### **✅ Durante desarrollo**
- [ ] Usar patrones estándar documentados
- [ ] Implementar smart_import para dependencias
- [ ] Añadir logging enterprise en funciones críticas
- [ ] Incluir manejo de errores robusto

### **✅ Post-desarrollo**
- [ ] Probar inicialización del módulo
- [ ] Verificar que no hay warnings SIC v3.1
- [ ] Documentar funcionalidades enterprise
- [ ] Añadir al sistema de testing

---

## 🔧 **COMANDOS DE VERIFICACIÓN**

### **Verificar SIC v3.1**
```bash
python -c "from sistema.sic_v3_1 import SICv31Enterprise; sic = SICv31Enterprise(); print('Status:', sic.get_system_stats()['status'])"
```

### **Verificar ImportCenter**
```bash
python -c "from utils.import_center import ImportCenter; ic = ImportCenter(); print('Verification:', ic.verify_installation())"
```

### **Test Completo**
```bash
cd "ict-engine-v6.0-enterprise-sic"
python install_sic_v31_import_center.py
```

---

## 📞 **SOPORTE Y REFERENCIAS**

**Documentación principal**: `03-DOCUMENTATION/reports/IMPLEMENTACION_BRIDGE_SIC_V31_COMPLETADA.md`  
**Bitácora técnica**: `04-development-logs/integration/BITACORA_BRIDGE_SIC_V31.md`  
**Instalador**: `install_sic_v31_import_center.py`  

**Desarrollado por**: ICT Engine v6.0 Enterprise Team  
**Última actualización**: 2 Septiembre 2025  

---

## ⚠️ **IMPORTANTE PARA COPILOT**

**Este protocolo es OBLIGATORIO para cualquier desarrollo que involucre:**
- Nuevos módulos del ICT Engine
- Integraciones con sistema SIC
- Funcionalidades enterprise
- Módulos que requieran imports inteligentes

**NO omitir estas reglas - son esenciales para la estabilidad del sistema.**
