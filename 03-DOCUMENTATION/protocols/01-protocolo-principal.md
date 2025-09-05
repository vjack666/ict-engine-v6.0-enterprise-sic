# 🎯 PROTOCOLO PRINCIPAL - FLUJO DE 5 FASES

**Archivo:** `01-protocolo-principal.md`  
**Propósito:** Flujo estructurado de desarrollo paso a paso  
**Tiempo Total:** 40-80 minutos (variable según complejidad)

---

## 📋 FLUJO PRINCIPAL DE DESARROLLO

### **FASE 1: PREPARACIÓN PRE-PROYECTO** ⏱️ *5-10 min*

#### **1.1 LECTURA OBLIGATORIA DE CONTEXTO**
```markdown
📚 ORDEN CRÍTICO DE LECTURA:
├── 1️⃣ protocolo-trabajo-copilot/README.md - Orientación general
├── 2️⃣ docs/02-architecture/ESTADO_ACTUAL_SISTEMA_v6.md - Estado actual
├── 3️⃣ docs/04-development-logs/[área-específica]/ - Historia del área
├── 4️⃣ logs/fase_X_completada.log - Última fase completada
└── 5️⃣ REGLAS_COPILOT.md - Reglas técnicas detalladas (si necesario)
```

#### **1.2 VERIFICACIÓN DE ESTADO DEL SISTEMA**
```bash
# ✅ COMANDOS DE VERIFICACIÓN RÁPIDA:
1. Verificar estructura: ls -la core/ tests/ docs/
2. Verificar imports: python -c "from sistema.sic_bridge import SICBridge"
3. Verificar datos: ls -la data/
4. Estado último: cat logs/fase_*_completada.log | tail -5
```

#### **1.3 IDENTIFICACIÓN DE ÁREA DE TRABAJO**
```markdown
🎯 PREGUNTA CLAVE: ¿En qué área voy a trabajar?
├── 🧠 MEMORIA → docs/04-development-logs/memoria/
├── 💹 SMART MONEY → docs/04-development-logs/smart-money/
├── 📊 BOS/CHOCH → docs/04-development-logs/bos-choch/
├── 🔧 TESTING → docs/04-development-logs/testing/
├── ⚡ PERFORMANCE → docs/04-development-logs/performance/
└── 🔗 INTEGRATION → docs/04-development-logs/integration/
```

---

### **FASE 2: ANÁLISIS Y DISEÑO** ⏱️ *10-15 min*

#### **2.1 VERIFICACIÓN DE NO DUPLICACIÓN (OBLIGATORIO)**
```bash
# 🔍 BÚSQUEDA EXHAUSTIVA - NO SALTARSE:
find . -name "*.py" -exec grep -l "función_similar" {} \;
find core/ -name "*pattern*" -o -name "*detector*" -o -name "*analyzer*"
grep -r "class.*Similar" core/ --include="*.py"
```

#### **2.2 ANÁLISIS DE ARQUITECTURA REQUERIDA**
```markdown
🏗️ CHECKLIST ARQUITECTURA:
├── ✅ ¿Necesita memoria de trader? → UnifiedMemorySystem
├── ✅ ¿Requiere logging estructurado? → SLUC v2.1
├── ✅ ¿Debe integrarse con SIC? → SICBridge
├── ✅ ¿Necesita datos MT5? → mt5_data_manager
├── ✅ ¿Requiere performance <5s? → Optimizaciones enterprise
└── ✅ ¿Necesita persistencia? → Configurar storage
```

#### **2.3 PLANIFICACIÓN DE TESTS**
```markdown
🧪 ESTRATEGIA DE TESTING:
├── 🎯 Test unitario: ¿Qué función específica testear?
├── 🔗 Test integración: ¿Con qué componentes se integra?
├── 📊 Test datos reales: ¿Requiere validación MT5?
├── ⚡ Test performance: ¿Objetivo <5s verificable?
└── 🧪 Test regresión: ¿Qué funcionalidad NO debe romperse?
```

---

### **FASE 3: IMPLEMENTACIÓN** ⏱️ *Tiempo variable*

#### **3.1 USAR TEMPLATE ENTERPRISE**
```markdown
📋 TEMPLATE COMPLETO DISPONIBLE EN:
└── protocolo-trabajo-copilot/03-templates-implementacion.md

🎯 ELEMENTOS OBLIGATORIOS:
├── ✅ Imports SIC/SLUC enterprise
├── ✅ Error handling robusto
├── ✅ Logging estructurado SLUC
├── ✅ Type hints completos
├── ✅ Docstrings específicos
└── ✅ Performance considerations
```

#### **3.2 CHECKLIST DURANTE IMPLEMENTACIÓN**
```markdown
⚡ VERIFICACIÓN CONTINUA:
├── ✅ Cada función tiene docstring específico
├── ✅ Imports ordenados correctamente (estándar/terceros/internos)
├── ✅ SLUC logging en operaciones importantes
├── ✅ SIC integration donde corresponde
├── ✅ Error handling apropiado
├── ✅ Type hints completos
├── ✅ Performance considerations (si <5s objetivo)
└── ✅ No duplicación de lógica existente
```

---

### **FASE 4: TESTING Y VALIDACIÓN** ⏱️ *15-20 min*

#### **4.1 USAR TEMPLATE DE TESTING ENTERPRISE**
```markdown
📋 TEMPLATE COMPLETO DISPONIBLE EN:
└── protocolo-trabajo-copilot/04-templates-testing.md

🎯 ELEMENTOS OBLIGATORIOS:
├── ✅ Mínimo 3-5 assertions específicas por test
├── ✅ Validación de tipos de retorno explícita
├── ✅ Error handling y edge cases incluidos
├── ✅ Performance <5s validada si es objetivo
├── ✅ Integración SIC/SLUC cuando disponible
└── ✅ Tests funcionando en entorno PowerShell
```

#### **4.2 COMANDO DE TESTING ESTÁNDAR**
```bash
# ✅ PROTOCOLO: Testing command enterprise
python -m pytest tests/test_[modulo]_enterprise.py -v --tb=short

# ✅ PROTOCOLO: Validación de imports
python -c "from [modulo] import [ClasePrincipal]; print('✅ Imports OK')"

# ✅ PROTOCOLO: Test datos reales (si aplica)
python tests/test_[modulo]_real_data.py
```

---

### **FASE 5: DOCUMENTACIÓN Y FINALIZACIÓN** ⏱️ *10-15 min*

#### **5.1 ACTUALIZACIÓN DE BITÁCORAS (OBLIGATORIO)**
```markdown
📋 TEMPLATE COMPLETO DISPONIBLE EN:
└── protocolo-trabajo-copilot/05-templates-documentacion.md

📝 ORDEN DE ACTUALIZACIÓN:
├── 1️⃣ docs/04-development-logs/[área-específica]/[bitácora].md
├── 2️⃣ docs/02-architecture/roadmap_v6.md (si aplica)
├── 3️⃣ logs/fase_X_completada.log (si fase completada)
├── 4️⃣ README.md (si cambia estructura)
└── 5️⃣ docs/05-user-guides/ (si nueva funcionalidad)
```

#### **5.2 VERIFICACIÓN FINAL DE CONSISTENCIA**
```bash
# ✅ PROTOCOLO: Verificación de consistencia
grep -r "TODO\|FIXME\|HACK" [archivos_modificados]
python -m pylint [modulo_nuevo] --score=y
git status  # Verificar qué cambió
```

---

## 🚨 PUNTOS DE CONTROL CRÍTICOS

### **❌ STOP POINTS - NO CONTINUAR SI:**
- No se completó búsqueda exhaustiva de duplicación
- No se definió claramente la arquitectura requerida
- No se tienen tests pasando antes de documentar
- No se verificó integración SIC/SLUC si es requerida

### **✅ GO POINTS - CONTINUAR SI:**
- Contexto del proyecto completamente entendido
- Arquitectura enterprise v6.0 planificada
- Tests específicos definidos y ejecutables
- Performance <5s planificada si es requerida

---

## ⚡ FLUJO RÁPIDO (20 MINUTOS)

### **Para tareas pequeñas/simples:**
```markdown
🚀 FLUJO ACELERADO:
├── 3 min: Leer contexto básico + verificar no duplicación
├── 5 min: Implementar usando template enterprise
├── 7 min: Test básico con template específico
├── 3 min: Actualizar bitácora con template
└── 2 min: Verificación final y cleanup
```

---

## 📊 MÉTRICAS DE ÉXITO DEL PROTOCOLO

### **✅ IMPLEMENTACIÓN EXITOSA:**
- **Setup:** <10 min para preparación completa
- **Desarrollo:** Template enterprise usado correctamente
- **Testing:** Mínimo 3 assertions específicas pasando
- **Documentación:** Bitácora actualizada con template
- **Performance:** <5s si es objetivo del componente

### **❌ SEÑALES DE ALERTA:**
- Más de 15 min en setup/preparación
- Tests genéricos o con 1-2 assertions básicas
- Performance >5s sin justificación técnica
- Bitácoras no actualizadas o incompletas
- Arquitectura no enterprise o legacy detectada

---

## 🎯 FILOSOFÍA DEL PROTOCOLO

### **🔍 PREPARACIÓN EXHAUSTIVA**
> "Invierte 10 minutos leyendo para ahorrar 2 horas implementando mal"

### **🏗️ IMPLEMENTACIÓN ENTERPRISE**
> "Cada línea de código debe cumplir estándares v6.0 enterprise"

### **🧪 VALIDACIÓN ROBUSTA**
> "Si no tiene tests específicos, no está terminado"

### **📝 DOCUMENTACIÓN AUTOMÁTICA**
> "El futuro yo agradecerá la documentación clara de hoy"

---

**📋 ESTADO:** ✅ **PROTOCOLO PRINCIPAL ACTIVO**  
**🎯 RESULTADO:** Desarrollo eficiente y calidad enterprise garantizada  
**⚡ PRÓXIMO:** Usar templates específicos en carpetas 03-09
