# 📚 DOCUMENTOS OBLIGATORIOS PRE-PROYECTO

**Archivo:** `02-documentos-obligatorios.md`  
**Propósito:** Lista completa de documentos que se deben leer antes de cualquier implementación

---

## 🚨 **LECTURA OBLIGATORIA - ORDEN CRÍTICO**

### **🏛️ Nivel 1: Reglas y Compliance (SIEMPRE LEER)**
```markdown
📋 ARCHIVOS FUNDAMENTALES (TIEMPO: 3-5 min):
✅ protocolo-trabajo-copilot/README.md                    # Protocolo general
✅ REGLAS_COPILOT.md                                      # Reglas técnicas
✅ ANALISIS_INTEGRACION_OPTIMA_DATOS_REALES.md            # Integración base
✅ REPORTE_FINAL_MIGRACION_MULTI_TIMEFRAME_BOS.md         # Migración crítica
```

### **🔧 Nivel 2: Estado del Sistema (CRÍTICO)**
```markdown
📊 ESTADO ACTUAL Y ARQUITECTURA (TIEMPO: 5-7 min):
✅ docs/02-architecture/ESTADO_ACTUAL_SISTEMA_v6.md       # Estado actual
✅ docs/02-architecture/ESTADO_REAL_VERIFICADO_v6.md      # Verificación
✅ docs/02-architecture/ESTRUCTURA_FINAL.md               # Estructura final
✅ docs/02-architecture/roadmap_v6.md                     # Roadmap actual
```

### **📝 Nivel 3: Bitácoras de Fases (CONTEXTO HISTÓRICO)**
```markdown
🗂️ BITÁCORAS DE DESARROLLO (TIEMPO: 2-3 min):
✅ logs/fase_1_completada.log                             # Fase 1 completada
✅ logs/fase_2_completada.log                             # Fase 2 completada
✅ logs/fase_3_completada.log                             # Fase 3 completada
✅ logs/documentacion_actualizada.log                     # Documentación actualizada
```

---

## 🎯 **DOCUMENTOS POR ÁREA DE TRABAJO**

### **🏗️ Si trabajas en ARQUITECTURA:**
```markdown
📐 LECTURA ESPECÍFICA ARQUITECTURA:
✅ docs/02-architecture/PLAN_DESARROLLO_REAL_ICT.md       # Plan desarrollo ICT
✅ docs/02-architecture/MEMORIA_Y_CONTEXTO_TRADER_REAL.md # Memoria trader
✅ docs/02-architecture/PLAN_MIGRACION_MEMORIA.md         # Plan memoria
✅ docs/02-architecture/ANALISIS_NODOS_BOS.md             # Análisis nodos BOS
```

### **🧠 Si trabajas en MEMORIA/TRADING:**
```markdown
🧠 LECTURA ESPECÍFICA MEMORIA:
✅ docs/04-development-logs/memoria/MEMORIA_TRADER_REAL_PLAN_COMPLETO.md
✅ docs/04-development-logs/memoria/PRESENTACION_EJECUTIVA_MEMORIA_TRADER.md
✅ docs/04-development-logs/memoria/FASE3_COMPLETION_REPORT.md
✅ docs/04-development-logs/memoria/CONCLUSION_FINAL_REGLA9.md
```

### **💹 Si trabajas en SMART MONEY/PATTERNS:**
```markdown
💹 LECTURA ESPECÍFICA SMART MONEY:
✅ docs/04-development-logs/smart-money/BITACORA_DESARROLLO_SMART_MONEY_v6.md
✅ docs/04-development-logs/order-blocks/ORDER_BLOCKS_IMPLEMENTATION_PLAN.md
✅ docs/04-development-logs/order-blocks/ANALISIS_MANUAL_EXHAUSTIVO.md
✅ docs/04-development-logs/bos-choch/README.md
```

### **🔌 Si trabajas en INTEGRACIÓN:**
```markdown
🔗 LECTURA ESPECÍFICA INTEGRACIÓN:
✅ docs/03-integration-plans/PLAN_INTEGRACION_ICT_v5.md   # Integración ICT
✅ docs/03-integration-plans/PLAN_INTEGRACION_MODULOS.md  # Integración módulos
✅ docs/03-integration-plans/MIGRACION_BOS_ENTERPRISE_v6.md # Migración BOS
✅ docs/04-development-logs/integration/BITACORA_INTEGRACION_SISTEMA_REAL.md
```

### **🧪 Si trabajas en TESTING:**
```markdown
🧪 LECTURA ESPECÍFICA TESTING:
✅ docs/04-development-logs/testing/ (todos los archivos)
✅ docs/06-reports/REPORTE_CONSOLIDADO_VALIDACION_SIC.md
✅ test_reports/ (últimos reportes)
```

### **🔮 Si trabajas en FRACTAL ANALYZER:**
```markdown
🔮 LECTURA ESPECÍFICA FRACTAL:
✅ docs/02-architecture/FRACTAL_ANALYZER_ENTERPRISE_V62_TECHNICAL_DOCS.md
✅ docs/05-user-guides/FRACTAL_ANALYZER_ENTERPRISE_V62_GUIDE.md
✅ core/ict_engine/fractal_analyzer_enterprise.py (v6.1 actual)
✅ tests/test_fractal_*.py (tests existentes)
```

---

## 📖 **GUÍAS DE USUARIO Y DOCUMENTACIÓN COMPLEMENTARIA**

### **📖 Para entender cómo usar componentes:**
```markdown
👥 USER GUIDES:
✅ docs/05-user-guides/BACKTEST_ENGINE_v6_GUIDE.md         # Backtest Guide
✅ docs/05-user-guides/MODULAR_ICT_BACKTESTER_GUIDE.md     # Modular Backtest
✅ docs/05-user-guides/mt5_data_manager_v6.md              # MT5 Data Manager
```

### **📊 Para entender estado de componentes:**
```markdown
📈 REPORTS Y ANÁLISIS:
✅ docs/06-reports/ANALISIS_BITACORAS_VS_REALIDAD.md       # Análisis bitácoras
✅ docs/06-reports/CERTIFICACION_ORDER_BLOCKS_SUMMA_CUM_LAUDE.md # Order Blocks
✅ docs/06-reports/REPORTE_FINAL_FASE_4_DISPLACEMENT_MT5_REAL.md # Displacement
✅ docs/06-reports/INTEGRACION_MEMORIA_UNIFICADA_SIC_SLUC_COMPLETADA.md
```

### **⚙️ Para configuración y setup:**
```markdown
🎯 GETTING STARTED:
✅ docs/01-getting-started/README.md                      # Inicio general
✅ docs/01-getting-started/DEVELOPMENT_SETUP.md           # Setup desarrollo
✅ docs/01-getting-started/PLAN_MIGRACION_BOS.md          # Plan migración
```

---

## ⚡ **PROTOCOLOS DE LECTURA SEGÚN TIEMPO DISPONIBLE**

### **🚀 LECTURA RÁPIDA (5 minutos) - MÍNIMO VIABLE:**
```bash
# Setup básico para emergencias
cat docs/02-architecture/ESTADO_ACTUAL_SISTEMA_v6.md | head -20
cat logs/fase_*_completada.log | tail -5
ls docs/04-development-logs/
cat protocolo-trabajo-copilot/07-reglas-criticas.md | head -20
```

### **📊 LECTURA COMPLETA (15-20 minutos) - RECOMENDADO:**
```markdown
1️⃣ Nivel 1-3 completo (Reglas + Estado + Bitácoras)
2️⃣ Área específica de trabajo según tarea
3️⃣ Reportes relacionados con el componente
4️⃣ Templates específicos para la implementación
```

### **🎯 LECTURA EXHAUSTIVA (30-40 minutos) - ÓPTIMO:**
```markdown
1️⃣ Todo el Nivel 1-3
2️⃣ Toda la documentación del área específica
3️⃣ Reportes completos relacionados
4️⃣ User guides del componente
5️⃣ Integration plans relevantes
6️⃣ Análisis de código existente similar
```

---

## 🔍 **COMANDOS PARA VERIFICAR DOCUMENTACIÓN**

### **📋 Verificar existencia de documentos:**
```bash
# Verificar estructura de documentación
find docs/ -name "*.md" | sort
ls -la logs/
ls -la protocolo-trabajo-copilot/

# Verificar documentos críticos
ls -la REGLAS_COPILOT.md ANALISIS_INTEGRACION_OPTIMA_DATOS_REALES.md
```

### **📊 Obtener contexto rápido:**
```bash
# Estado actual en 1 minuto
cat docs/02-architecture/ESTADO_ACTUAL_SISTEMA_v6.md | head -30
cat logs/fase_*_completada.log | tail -10
wc -l docs/04-development-logs/*/*.md
```

### **🔍 Buscar información específica:**
```bash
# Buscar por componente
grep -r "fractal\|Fractal" docs/ --include="*.md"
grep -r "memory\|Memory" docs/04-development-logs/ --include="*.md"
grep -r "SIC\|SLUC" docs/ --include="*.md"
```

---

## 📝 **CHECKLIST DE LECTURA PRE-PROYECTO**

### **✅ Antes de implementar CUALQUIER funcionalidad:**
```markdown
📋 VERIFICACIÓN OBLIGATORIA:
├── ✅ Leído protocolo principal (este directorio)
├── ✅ Verificado estado actual del sistema
├── ✅ Revisado bitácoras de área específica
├── ✅ Confirmado no duplicación de funcionalidad
├── ✅ Entendido contexto arquitectónico
├── ✅ Identificado componentes de integración
├── ✅ Revisado reportes de componentes relacionados
└── ✅ Definido plan de testing específico
```

### **❌ NO PROCEDER si no se ha:**
- Leído documentación básica de contexto
- Verificado existencia de funcionalidad similar
- Entendido la arquitectura enterprise v6.0
- Identificado componentes SIC/SLUC requeridos
- Revisado bitácoras del área de trabajo

---

## 🎯 **OPTIMIZACIÓN DE TIEMPO DE LECTURA**

### **📚 Primera vez trabajando en el proyecto:**
- **Tiempo:** 40-60 minutos
- **Cobertura:** Lectura exhaustiva recomendada
- **Enfoque:** Entender arquitectura completa

### **🔄 Trabajando en área conocida:**
- **Tiempo:** 10-15 minutos  
- **Cobertura:** Nivel 1-3 + área específica
- **Enfoque:** Actualizaciones y contexto reciente

### **⚡ Fix rápido/emergencia:**
- **Tiempo:** 5 minutos
- **Cobertura:** Estado actual + reglas críticas
- **Enfoque:** No romper funcionamiento existente

---

**📋 ESTADO:** ✅ **DOCUMENTACIÓN CLASIFICADA Y ORGANIZADA**  
**🎯 OBJETIVO:** Lectura eficiente y contexto completo garantizado  
**⚡ USO:** Elegir protocolo de lectura según tiempo disponible y experiencia
