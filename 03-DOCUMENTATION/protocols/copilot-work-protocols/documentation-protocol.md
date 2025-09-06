# 📝 PROTOCOLO DE DOCUMENTACIÓN COPILOT

**Propósito:** Estandarizar la creación de documentación usando las reglas establecidas  
**Audiencia:** Desarrolladores trabajando con GitHub Copilot  
**Aplicabilidad:** Toda documentación creada en el proyecto ICT Engine v6.0

---

## 🎯 Objetivo
Crear documentación **organizada, específica por audiencia y completamente validada** usando la estructura de subcarpetas especializada.

---

## 📋 Procedimiento de Documentación

### Paso 1: Identificar Audiencia y Subcarpeta
**Acción:** Determinar quién va a leer el documento
**Input:** Tipo de información a documentar
**Output:** Subcarpeta apropiada según reglas

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

### Paso 2: Seleccionar Template Apropiado
**Validación:** ¿El template corresponde a la subcarpeta?
**Criterios de calidad:** Usar template específico de cada subcarpeta

| Subcarpeta | Template | Características |
|------------|----------|----------------|
| `user-guides/` | Usuario final | Paso a paso, ejemplos prácticos |
| `technical/docs/` | Técnico | Código, APIs, arquitectura |
| `development/` | Cronológico | Fechas, estados, métricas |
| `protocols/` | Prescriptivo | Instrucciones, checklists |
| `reports/` | Ejecutivo | Métricas, análisis, conclusiones |
| `01-production-ready/` | Crítico | Procedimientos sin ambigüedades |

### Paso 3: Validar Información
**Acción:** Verificar que toda información es real y probada
**Input:** Contenido propuesto para el documento
**Output:** Contenido validado contra el sistema real

```bash
# Validación obligatoria
echo "¿Cada comando ha sido probado en el sistema real?"
echo "¿Los ejemplos funcionan correctamente?"
echo "¿La información corresponde al código actual?"
echo "¿Los procedimientos son reproducibles?"
```

### Paso 4: Crear Documento con Estructura Estándar
**Acción:** Escribir documento usando template apropiado
**Input:** Información validada y template seleccionado
**Output:** Documento completo con estructura consistente

### Paso 5: Actualizar Índices y Referencias
**Acción:** Mantener READMEs y referencias actualizadas
**Input:** Nuevo documento creado
**Output:** Estructura de documentación actualizada

---

## ✅ Checklist de Validación de Documentación

### Pre-Creación:
- [ ] ✅ Audiencia objetivo identificada claramente
- [ ] ✅ Subcarpeta apropiada determinada según reglas
- [ ] ✅ Documentos existentes relacionados revisados
- [ ] ✅ Verificado que no duplica contenido existente
- [ ] ✅ Propósito específico del documento definido

### Durante Creación:
- [ ] ✅ Template apropiado utilizado para la subcarpeta
- [ ] ✅ Ejemplos prácticos relevantes incluidos
- [ ] ✅ Código/módulos reales del proyecto referenciados
- [ ] ✅ Consistencia con estilo existente mantenida
- [ ] ✅ Información técnica exacta y validada

### Post-Creación:
- [ ] ✅ README.md de la subcarpeta actualizado
- [ ] ✅ Referencias cruzadas necesarias agregadas
- [ ] ✅ Verificado que cumple el propósito definido
- [ ] ✅ Ejemplos/procedimientos probados en sistema real
- [ ] ✅ Índice general actualizado si es necesario

---

## 🔧 Troubleshooting de Documentación

### Problema: No sé en qué subcarpeta poner el documento
**Solución:** 
1. Identificar audiencia principal (¿quién lo va a leer?)
2. Aplicar la función `identificar_subcarpeta()`
3. Si hay duda, priorizar por nivel de criticidad: producción > usuario > técnico > desarrollo

### Problema: El documento puede servir para múltiples audiencias
**Solución:**
1. Crear documento principal en subcarpeta de audiencia primaria
2. Crear documentos de referencia cruzada en otras subcarpetas
3. Usar enlaces entre documentos para conectar información

### Problema: La información técnica es muy compleja para validar
**Solución:**
1. Dividir en secciones más pequeñas
2. Validar cada sección individualmente
3. Usar comentarios de código real como respaldo
4. Consultar con experto técnico si es necesario

---

## 📚 Referencias de Templates

### Template User-Guides:
```markdown
# 👤 [TÍTULO]
**Audiencia:** Usuario final trader
**Tiempo estimado:** [X] minutos
**Prerrequisitos:** [Lista]
## 🎯 Objetivo
## 📋 Pasos
## ✅ Verificación
## 🔧 Solución de Problemas
```

### Template Technical:
```markdown
# 🔧 [TÍTULO]
**Módulo:** [Nombre]
**Archivo principal:** `01-CORE/[ruta]`
## 🏗️ Arquitectura
## 📡 API Reference
## 🔗 Integraciones
## 🧪 Testing
```

### Template Development:
```markdown
# 📝 [TÍTULO]
**Fecha:** [YYYY-MM-DD]
**Fase:** [Número]
## 📊 Resumen Ejecutivo
## ✅ Tareas Completadas
## 🔄 Tareas en Progreso
## 🎯 Próximos Pasos
```

### Template Reports:
```markdown
# 📊 [TÍTULO]
**Fecha:** [YYYY-MM-DD]
**Audiencia:** [Management/Técnico]
## 📈 Resumen Ejecutivo
## 🎯 KPIs Principales
## 📊 Análisis Detallado
## 📋 Recomendaciones
```

---

## ⚡ Comandos Rápidos Copilot

### Crear Documentación User-Guides:
```bash
echo "CREAR: user-guides/[nombre].md"
echo "AUDIENCIA: Usuario final trader"
echo "FORMATO: Paso a paso con ejemplos"
echo "VALIDAR: Reproducible en sistema real"
```

### Crear Documentación Technical:
```bash
echo "CREAR: technical/docs/07-modules/[area]/[nombre].md"
echo "AUDIENCIA: Desarrollador"
echo "FORMATO: Técnico con código y APIs"
echo "VALIDAR: Referencias a código real en 01-CORE/"
```

### Crear Development Log:
```bash
echo "CREAR: development/[tipo]-logs/[nombre].md"
echo "AUDIENCIA: Equipo desarrollo"
echo "FORMATO: Cronológico con fechas"
echo "VALIDAR: Fechas y métricas reales"
```

### Crear Reporte:
```bash
echo "CREAR: reports/[categoria]-reports/[nombre].md"
echo "AUDIENCIA: Management/Técnico senior"
echo "FORMATO: Ejecutivo con métricas"
echo "VALIDAR: Datos reales del sistema"
```

---

## 🎯 Criterios de Calidad

### Calidad Mínima Requerida:
1. **Claridad:** Comprensible para audiencia objetivo
2. **Completitud:** Información necesaria incluida
3. **Actualización:** Sincronizada con código actual
4. **Verificabilidad:** Procedimientos probados en sistema real
5. **Consistencia:** Formato apropiado para subcarpeta

### Métricas de Calidad:
- **User-guides:** ¿Un usuario nuevo puede seguir los pasos?
- **Technical:** ¿Un desarrollador puede implementar basándose en esto?
- **Development:** ¿El progreso está claramente documentado?
- **Reports:** ¿Las conclusiones son accionables?

---

## 🔄 Mantenimiento de Documentación

### Frecuencia de Actualización:
- **01-production-ready/**: Inmediata al cambiar funcionalidad crítica
- **user-guides/**: Al cambiar UI o procedimientos de usuario
- **technical/docs/**: Al cambiar APIs o arquitectura
- **development/**: Al final de cada sesión de desarrollo
- **reports/**: Según frecuencia definida (diaria/semanal/mensual)

### Proceso de Actualización:
1. Detectar cambio en sistema/código
2. Identificar documentos afectados
3. Validar información actualizada
4. Actualizar documentos usando protocolo
5. Verificar consistencia en referencias cruzadas
