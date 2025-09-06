# 📚 DOCUMENTACIÓN ICT ENGINE v6.0 ENTERPRISE

**Estado:** ✅ Estructura completa organizada según reglas Copilot  
**Última actualización:** 06/09/2025  
**Metodología:** Documentación por subcarpetas especializadas

---

## 🗂️ **ESTRUCTURA DE DOCUMENTACIÓN COMPLETA**

### **📁 user-guides/** - Guías para Usuarios Finales
**Audiencia:** Traders y usuarios que usarán el sistema en producción  
**Formato:** Paso a paso, con ejemplos prácticos y screenshots

```
user-guides/
├── quick-start-guide.md               # Setup en < 5 minutos
├── trading-operations-manual.md       # Manual de operaciones de trading
├── dashboard-user-guide.md            # Guía del dashboard
├── troubleshooting-user.md            # Solución de problemas usuario
├── configuration-user-guide.md        # Configuración básica
├── pattern-recognition-guide.md       # Guía de patrones ICT
├── risk-management-guide.md           # Gestión de riesgo
├── performance-monitoring.md          # Monitoreo de performance
├── data-sources-guide.md              # Fuentes de datos (MT5, Yahoo)
└── README.md                          # Índice de guías
```

### **📁 technical/docs/** - Documentación Técnica
**Audiencia:** Desarrolladores, arquitectos y mantenimiento técnico  
**Formato:** Técnico, con diagramas de código, APIs y arquitectura

```
technical/docs/
├── 01-getting-started/                # Setup técnico
├── 02-architecture/                   # Arquitectura del sistema
├── 03-integration-plans/              # Planes de integración
├── 07-modules/                        # Documentación por módulo
│   ├── core-engine/
│   ├── pattern-detection/
│   ├── memory-system/
│   └── dashboard/
└── components/                        # Componentes específicos
```

### **📁 development/** - Bitácoras de Desarrollo
**Audiencia:** Equipo de desarrollo  
**Formato:** Cronológico, con fechas y estados de progreso

```
development/
├── phase-logs/                        # Logs por fase
├── implementation-logs/               # Logs de implementación
├── decision-records/                  # Decisiones técnicas
└── testing-logs/                      # Logs de testing
```

### **📁 protocols/** - Protocolos Copilot y Metodologías
**Audiencia:** Desarrolladores con Copilot  
**Formato:** Prescriptivo, instruccional con templates

```
protocols/
├── copilot-work-protocols/            # Protocolos de trabajo
├── coding-standards/                  # Estándares de código
├── templates/                         # Templates reutilizables
└── guidelines/                        # Guías metodológicas
```

### **📁 reports/** - Reportes y Análisis
**Audiencia:** Management y técnico senior  
**Formato:** Ejecutivo, con métricas y conclusiones

```
reports/
├── executive-reports/                 # Reportes ejecutivos
├── technical-analysis/                # Análisis técnicos
├── testing-reports/                   # Reportes de testing
└── metrics-reports/                   # Reportes de métricas
```

### **📁 01-production-ready/** - Documentación Crítica de Producción
**Audiencia:** Operaciones en producción  
**Formato:** Procedimientos críticos, paso a paso sin ambigüedades

- ✅ `quick-start.md` - Guía de inicio rápido validada
- ✅ `modules-inventory.md` - Inventario completo de módulos
- ✅ `dashboard-enterprise.md` - Guía de acceso al dashboard
- ✅ `troubleshooting.md` - Solución de problemas comunes
- ✅ `emergency-procedures.md` - Procedimientos de emergencia
- ✅ `production-checklist.md` - Checklist pre-producción

---

## 🚀 **INICIO RÁPIDO POR TIPO DE USUARIO**

### **👤 Usuario Trader/Final:**
```bash
📂 COMENZAR EN: user-guides/
1. Leer: user-guides/quick-start-guide.md
2. Configurar: user-guides/configuration-user-guide.md
3. Usar: user-guides/dashboard-user-guide.md
```

### **👨‍💻 Desarrollador:**
```bash
📂 COMENZAR EN: technical/docs/
1. Setup: technical/docs/01-getting-started/
2. Arquitectura: technical/docs/02-architecture/
3. Módulos: technical/docs/07-modules/
```

### **⚡ Producción/DevOps:**
```bash
📂 COMENZAR EN: 01-production-ready/
1. Despliegue: deployment-guide.md
2. Monitoreo: monitoring-setup.md
3. Emergencia: emergency-procedures.md
```

### **📊 Management/Reportes:**
```bash
📂 COMENZAR EN: reports/
1. Estado: reports/executive-reports/
2. Métricas: reports/metrics-reports/
3. Progreso: reports/technical-analysis/
```

---

## 🎯 **REGLAS DE DOCUMENTACIÓN POR SUBCARPETA**

### **Regla de Identificación Automática:**
```python
def identificar_subcarpeta(tipo_documento):
    if "usuario final" in tipo_documento:
        return "user-guides/"
    elif "técnico/desarrollador" in tipo_documento:
        return "technical/docs/"
    elif "progreso/bitácora" in tipo_documento:
        return "development/"
    elif "protocolo/metodología" in tipo_documento:
        return "protocols/"
    elif "reporte/análisis" in tipo_documento:
        return "reports/"
    elif "producción/crítico" in tipo_documento:
        return "01-production-ready/"
```

### **Templates por Subcarpeta:**
- **user-guides/**: Orientado a usuario, paso a paso
- **technical/docs/**: Técnico con código y APIs
- **development/**: Cronológico con fechas
- **protocols/**: Prescriptivo/instructivo
- **reports/**: Analítico con métricas
- **01-production-ready/**: Procedimientos críticos

---

## 📋 **CHECKLIST ANTES DE CREAR DOCUMENTACIÓN**

### **Pre-Creación:**
- [ ] ✅ Identificar audiencia objetivo
- [ ] ✅ Determinar subcarpeta apropiada según reglas
- [ ] ✅ Revisar documentos existentes relacionados
- [ ] ✅ Verificar que no duplica contenido existente

### **Durante Creación:**
- [ ] ✅ Usar template apropiado para la subcarpeta
- [ ] ✅ Incluir ejemplos prácticos relevantes
- [ ] ✅ Referenciar código/módulos reales del proyecto
- [ ] ✅ Mantener consistencia con estilo existente

### **Post-Creación:**
- [ ] ✅ Actualizar README.md de la subcarpeta
- [ ] ✅ Agregar referencias cruzadas necesarias
- [ ] ✅ Verificar que cumple el propósito definido
- [ ] ✅ Probar ejemplos/procedimientos incluidos

---

## ⚡ **COMANDOS RÁPIDOS PARA COPILOT**

### **Crear Documentación User-Guides:**
```bash
echo "Crear guía usuario para [FUNCIONALIDAD] en user-guides/[NOMBRE].md"
echo "Audiencia: Usuario final trader"
echo "Formato: Paso a paso con ejemplos"
```

### **Crear Documentación Technical:**
```bash
echo "Crear documentación técnica para [COMPONENTE] en technical/docs/07-modules/[AREA]/[NOMBRE].md"
echo "Audiencia: Desarrollador"
echo "Formato: Técnico con código y APIs"
```

### **Crear Development Log:**
```bash
echo "Crear log de desarrollo para [FASE/COMPONENTE] en development/[TIPO]-logs/[NOMBRE].md"
echo "Audiencia: Equipo desarrollo"
echo "Formato: Cronológico con fechas"
```

---

## 🎯 **METODOLOGÍA DE CALIDAD**

### **Validación Obligatoria:**
1. **SOLO documentar realidad verificable**
2. **VALIDAR cada comando y procedimiento**
3. **USAR template apropiado para cada subcarpeta**
4. **MANTENER consistencia en estructura**
5. **REFERENCIAR código real del proyecto**

### **Estado de Validación Actual:**
- ✅ **Estructura organizada** según reglas Copilot
- ✅ **Subcarpetas especializadas** por audiencia
- ✅ **Templates definidos** para cada tipo
- ✅ **Metodología clara** de creación
- ✅ **Fase 1 completada** en 01-production-ready/

**🎯 OBJETIVO:** Documentación completa, organizada y útil que permita a cualquier usuario/desarrollador trabajar efectivamente con el ICT Engine v6.0 Enterprise.

---

## 📞 **SOPORTE POR TIPO DE CONSULTA**

- **Usuario Final:** Consultar `user-guides/troubleshooting-user.md`
- **Desarrollador:** Revisar `technical/docs/` y `protocols/`
- **Producción:** Seguir `01-production-ready/emergency-procedures.md`
- **Reportes:** Consultar `reports/executive-reports/`
