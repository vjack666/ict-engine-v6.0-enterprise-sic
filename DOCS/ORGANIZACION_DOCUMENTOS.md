# 📁 Organización de Documentos - ICT Engine v6.0

**Fecha:** 19 Septiembre 2025  
**Propósito:** Establecer reglas claras de organización de documentos y módulos

## 📋 Reglas de Organización

### 🎯 **Principio General**
> **"Todo documento debe crearse directamente en su carpeta correspondiente"**

### 📁 **Estructura de Carpetas DOCS/**

#### 🔬 **`DOCS/reports/`** - Reportes y Análisis
- ✅ Reportes de performance
- ✅ Análisis de sistemas
- ✅ Resultados de auditorías
- ✅ Métricas y estadísticas
- **Ejemplo**: `PERFORMANCE_ANALYZER_COMPLETED.md`

#### 🏗️ **`DOCS/architecture/`** - Arquitectura del Sistema  
- ✅ Diagramas de arquitectura
- ✅ Diseños de sistema
- ✅ Patrones y estructuras
- ✅ Especificaciones técnicas

#### 📖 **`DOCS/guides/`** - Guías y Tutoriales
- ✅ Guías de uso
- ✅ Manuales de instalación
- ✅ Tutoriales paso a paso
- ✅ Documentación de usuario

#### 🔧 **`DOCS/technical/`** - Documentación Técnica
- ✅ Especificaciones técnicas
- ✅ APIs y interfaces
- ✅ Protocolos de comunicación
- ✅ Documentación de código

#### 🚀 **`DOCS/implementation/`** - Implementación
- ✅ Planes de implementación
- ✅ Estrategias de despliegue
- ✅ Cronogramas de desarrollo
- ✅ Documentos de planificación

#### ✅ **`DOCS/completed/`** - Proyectos Completados
- ✅ Documentación de proyectos finalizados
- ✅ Archivos históricos
- ✅ Lecciones aprendidas
- ✅ Post-mortems

#### ⚠️ **`DOCS/alerting/`** - Sistema de Alertas
- ✅ Configuración de alertas
- ✅ Documentación de thresholds
- ✅ Planes de respuesta
- ✅ Escalación de alertas

#### 🔍 **`DOCS/analysis/`** - Análisis Específicos
- ✅ Análisis de datos
- ✅ Estudios de caso
- ✅ Investigaciones técnicas
- ✅ Análisis de tendencias

#### 🤖 **`DOCS/machine_learning/`** - Machine Learning
- ✅ Modelos ML
- ✅ Datasets y entrenamiento
- ✅ Evaluaciones de modelos
- ✅ Documentación de algoritmos

#### ⚡ **`DOCS/optimization/`** - Optimizaciones
- ✅ Planes de optimización
- ✅ Análisis de bottlenecks
- ✅ Mejoras de rendimiento
- ✅ Benchmarks y comparativas

## 📁 **Estructura de Carpetas de Código**

### 🔧 **`scripts/`** - Scripts y Herramientas
- ✅ Scripts de utilidad
- ✅ Herramientas de análisis
- ✅ Automatizaciones
- **Ejemplo**: `performance_analyzer.py`

### ⚙️ **`01-CORE/`** - Código Principal
- ✅ Módulos core del sistema
- ✅ Funcionalidades principales
- ✅ Componentes centrales

### 📊 **`09-DASHBOARD/`** - Dashboard y UI
- ✅ Interfaces de usuario
- ✅ Componentes web
- ✅ Visualizaciones

### 🛠️ **`FIXES/`** - Correcciones y Parches
- ✅ Scripts de corrección
- ✅ Parches temporales
- ✅ Hotfixes

### 📈 **`monitoring/`** - Monitoreo
- ✅ Scripts de monitoreo
- ✅ Métricas de sistema
- ✅ Health checks

## 🎯 **Reglas Específicas de Creación**

### ✅ **Al Crear Documentos:**

1. **Identifica el Tipo de Documento**
   - ¿Es un reporte? → `DOCS/reports/`
   - ¿Es una guía? → `DOCS/guides/`
   - ¿Es documentación técnica? → `DOCS/technical/`

2. **Usa Nombres Descriptivos**
   - ✅ `PERFORMANCE_ANALYZER_COMPLETED.md`
   - ✅ `SISTEMA_ALERTAS_IMPLEMENTACION.md`
   - ❌ `doc1.md`, `temp.md`

3. **Incluye Metadata en el Documento**
   ```markdown
   **Fecha:** DD Mes YYYY
   **Autor:** Nombre
   **Propósito:** Descripción clara
   **Estado:** En Desarrollo/Completado/Archivado
   ```

### ✅ **Al Crear Módulos de Código:**

1. **Scripts de Utilidad** → `scripts/`
2. **Código Core** → `01-CORE/`
3. **Correcciones** → `FIXES/`
4. **Tests** → `tests/`

### ✅ **Al Crear Datos:**

1. **Métricas** → `04-DATA/metrics/`
2. **Reportes** → `04-DATA/reports/`
3. **Logs** → `05-LOGS/`
4. **Cache** → `04-DATA/cache/`

## 📋 **Checklist de Creación de Documentos**

- [ ] ¿Identifiqué la carpeta correcta?
- [ ] ¿El nombre es descriptivo y claro?
- [ ] ¿Incluí metadata en el documento?
- [ ] ¿El documento está en español?
- [ ] ¿Agregué emojis para mejor legibilidad?
- [ ] ¿El contenido está bien estructurado?

## 🔄 **Mantenimiento**

### 📅 **Revisión Mensual**
- Revisar documentos obsoletos
- Actualizar índices
- Archivar documentos completados
- Reorganizar si es necesario

### 🧹 **Limpieza**
- Mover documentos temporales
- Consolidar documentos similares
- Eliminar duplicados
- Actualizar referencias

---

**📝 Nota**: Esta organización debe ser seguida por todos los desarrolladores y mantenida consistentemente para facilitar la navegación y mantenimiento del proyecto.

**✅ Ejemplo de Uso**: El documento `PERFORMANCE_ANALYZER_COMPLETED.md` fue movido correctamente de la raíz a `DOCS/reports/` siguiendo estas reglas.