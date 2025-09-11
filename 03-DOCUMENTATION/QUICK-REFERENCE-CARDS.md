# ⚡ QUICK REFERENCE CARDS - GITHUB COPILOT
## ICT ENGINE v6.0 ENTERPRISE - ACCESO RÁPIDO

**Propósito:** Acceso inmediato a información crítica  
**Formato:** Cards de 5, 15, y 30 minutos  
**Optimizado para:** GitHub Copilot + Desarrollo ágil

---

## 🚨 **EMERGENCY CARD - 5 MINUTOS**

### **🔥 SISTEMA NO FUNCIONA - TROUBLESHOOTING INMEDIATO**
```bash
# 1. VERIFICACIÓN BÁSICA (1 min)
python main.py --version                   # ¿Sistema responde?
python -c "import MetaTrader5; print('MT5 OK')"  # ¿MT5 disponible?

# 2. COMANDOS DE EMERGENCIA (2 min)  
cat 03-DOCUMENTATION/protocols/06-comandos-rapidos.md | head -15
cat 03-DOCUMENTATION/emergency-procedures.md | head -20

# 3. SOLUCIONES INMEDIATAS (2 min)
grep -A3 "SOLUTION:" 03-DOCUMENTATION/troubleshooting.md   # Soluciones rápidas
cat 03-DOCUMENTATION/reports/DASHBOARD_HANGING_SOLUTION.md | head -10  # Dashboard fix
```

### **⚡ PATHS CRÍTICOS:**
```
🚨 Emergency: 03-DOCUMENTATION/emergency-procedures.md
🔧 Quick Fix: 03-DOCUMENTATION/troubleshooting.md  
🖥️ Dashboard: 03-DOCUMENTATION/reports/DASHBOARD_HANGING_SOLUTION.md
⚙️ Config: 03-DOCUMENTATION/configuration-guide.md
✅ Checklist: 03-DOCUMENTATION/production-checklist.md
```

### **🎯 COMANDOS MÁS FRECUENTES:**
```bash
# Restart sistema completo
python main.py --restart-all

# Dashboard recovery  
python 09-DASHBOARD/start_dashboard.py --recovery

# MT5 reconnect
python -c "from core.mt5_manager import MT5Manager; MT5Manager().reconnect()"

# Check logs críticos
tail -50 05-LOGS/system/general.log | grep ERROR
tail -30 05-LOGS/mt5/connection.log | grep FAILED
```

---

## 🔧 **DEVELOPMENT CARD - 15 MINUTOS**

### **📋 ANTES DE PROGRAMAR (5 min) - LECTURA OBLIGATORIA**
```markdown
1. ✅ 03-DOCUMENTATION/protocols/REGLAS_COPILOT.md (líneas 1-50)         # Reglas fundamentales
2. ✅ ESTADO_REAL_SISTEMA_REFERENCIA.md (líneas 1-30)                    # Estado actual
3. ✅ 03-DOCUMENTATION/protocols/02-documentos-obligatorios.md (tu área) # Docs específicos
```

### **🏗️ TEMPLATES DE DESARROLLO (5 min)**
```markdown
📂 TEMPLATES POR CASO DE USO:

🎯 NUEVO PATTERN ICT:
└─ 03-DOCUMENTATION/protocols/03-templates-implementacion.md → "ICT Pattern Template"

🔗 NUEVA INTEGRACIÓN:
└─ 03-DOCUMENTATION/protocols/03-templates-implementacion.md → "Integration Template" 

🧪 TESTING:
└─ 03-DOCUMENTATION/protocols/04-templates-testing.md → "Test Template Enterprise"

📝 DOCUMENTACIÓN:
└─ 03-DOCUMENTATION/protocols/05-templates-documentacion.md → "Bitácora Template"
```

### **🔍 CONTEXTO POR COMPONENTE (5 min)**
```markdown
🧠 SMART MONEY:
└─ 03-DOCUMENTATION/technical/docs/04-development-logs/smart-money/

🔄 BOS/CHoCH:  
└─ 03-DOCUMENTATION/reports/REPORTE_FINAL_MIGRACION_MULTI_TIMEFRAME_BOS.md

🧱 ORDER BLOCKS:
└─ 03-DOCUMENTATION/technical/docs/04-development-logs/order-blocks/

💾 MEMORIA SYSTEM:
└─ 03-DOCUMENTATION/technical/docs/04-development-logs/memoria/

📊 PERFORMANCE:
└─ 03-DOCUMENTATION/technical/docs/04-development-logs/performance/
```

### **⚡ WORKFLOW RÁPIDO:**
```bash
# 1. Leer contexto específico (2 min)
cat 03-DOCUMENTATION/COPILOT-CONTEXT-CARDS.md | grep -A5 "[TU-COMPONENTE]"

# 2. Copiar template apropiado (1 min)  
cat 03-DOCUMENTATION/protocols/03-templates-implementacion.md | grep -A20 "[Tu Template]"

# 3. Verificar estado actual (1 min)
grep -i "[tu-componente]" ESTADO_REAL_SISTEMA_REFERENCIA.md

# 4. Implementar siguiendo reglas (10 min)
# 5. Test con template de testing (1 min)
cat 03-DOCUMENTATION/protocols/04-templates-testing.md | grep -A15 "Test Template"
```

---

## 🏢 **ENTERPRISE CARD - 30 MINUTOS**

### **🚀 DEPLOY A PRODUCCIÓN (15 min)**
```markdown
📋 CHECKLIST DEPLOY:

1. ✅ PRE-DEPLOY (5 min):
   └─ cat 03-DOCUMENTATION/production-checklist.md                    # Verificaciones
   └─ cat 03-DOCUMENTATION/performance-monitoring.md | head -20       # Métricas baseline

2. ✅ DEPLOY PROCESS (5 min):
   └─ cat 03-DOCUMENTATION/enterprise-deployment.md | head -40        # Proceso deploy
   └─ python scripts/deploy_enterprise.py --environment=prod          # Ejecutar deploy

3. ✅ POST-DEPLOY (5 min):
   └─ cat 03-DOCUMENTATION/real-environment-setup.md | head -30       # Setup ambiente
   └─ Ejecutar validation tests
```

### **👥 MULTI-ACCOUNT MANAGEMENT (10 min)**
```markdown
📋 SETUP MULTI-CUENTA:

1. ✅ CONFIGURACIÓN (5 min):
   └─ cat 03-DOCUMENTATION/multi-account-management.md | head -30     # Config multi-account
   └─ Configurar cuentas FTMO/Prop Firm

2. ✅ VALIDACIÓN (3 min):
   └─ Verificar conexiones MT5 por cuenta
   └─ Test de trading signals por cuenta

3. ✅ MONITOREO (2 min):  
   └─ cat 03-DOCUMENTATION/performance-monitoring.md | grep "multi"   # Setup monitoreo
   └─ Configurar alertas por cuenta
```

### **📊 MONITORING & ALERTS (5 min)**
```markdown
📋 SETUP MONITOREO:

1. ✅ MÉTRICAS (2 min):
   └─ cat 03-DOCUMENTATION/performance-monitoring.md | head -25       # Métricas clave
   
2. ✅ ALERTAS (2 min):
   └─ cat 03-DOCUMENTATION/mt5-connection-optimization.md | head -20  # Alertas conexión
   
3. ✅ DASHBOARDS (1 min):
   └─ cat 03-DOCUMENTATION/dashboard-components-reference.md | head -15 # Referencias dashboard
```

---

## 🎯 **CONTEXT CARDS PARA COPILOT**

### **🤖 AI-FRIENDLY SUMMARIES**

#### **📋 SMART MONEY ANALYSIS**
```
CONTEXT: Sistema análisis Smart Money v6.0 enterprise
ESTADO: ✅ Fase 1 completada, integración con memoria activa
ARCHIVOS: 03-DOCUMENTATION/development/BITACORA_DESARROLLO_SMART_MONEY_v6.md
USO: Análisis institucional, detección manipulación, confluence
TESTING: Validado con datos MT5 reales, performance <0.1s
NEXT: Expansión multi-timeframe, alertas avanzadas
```

#### **🔄 BOS/CHoCH PATTERNS**  
```
CONTEXT: Break of Structure + Change of Character detection
ESTADO: ✅ Migración multi-timeframe completada
ARCHIVOS: 03-DOCUMENTATION/reports/REPORTE_FINAL_MIGRACION_MULTI_TIMEFRAME_BOS.md
USO: Detección cambios estructura, confirmación tendencias
TESTING: Pipeline H4→M15→M5 validado, edge cases cubiertos
NEXT: Optimización signals, integration con Order Blocks
```

#### **🧱 ORDER BLOCKS**
```
CONTEXT: Order Blocks ICT enterprise con memoria unificada
ESTADO: ✅ Integración UnifiedMemorySystem completada
ARCHIVOS: 03-DOCUMENTATION/technical/docs/04-development-logs/order-blocks/
USO: Zonas institucionales, levels de confluencia
TESTING: Memory-aware funcionando, validación exhaustiva
NEXT: Refinamiento detection, multi-symbol expansion
```

#### **💾 MEMORIA SYSTEM**
```
CONTEXT: UnifiedMemorySystem v6.0 - Memoria trader real
ESTADO: 🔄 Fase 4 incompleta, testing MT5 pendiente  
ARCHIVOS: 03-DOCUMENTATION/technical/docs/04-development-logs/memoria/
USO: Contexto histórico, memory-aware patterns
TESTING: Parcial, requiere testing MT5 real completo
NEXT: Completar Fase 4, validación producción
```

#### **📊 PERFORMANCE SYSTEM**
```
CONTEXT: Sistema optimización procesamiento datos enterprise  
ESTADO: ✅ Plan optimización 2025-09-03 aplicado
ARCHIVOS: 03-DOCUMENTATION/technical/docs/04-development-logs/performance/
USO: Optimización latencia, escalabilidad enterprise
TESTING: Métricas <0.1s conseguidas, thread-safe validado
NEXT: Monitoring avanzado, auto-scaling
```

---

## 🔍 **SEARCH OPTIMIZATION TAGS**

### **🏷️ TAGS POR CASOS DE USO:**
```
#emergency #troubleshooting #quick-fix #recovery
#development #implementation #template #pattern
#enterprise #deployment #production #multi-account  
#smart-money #bos-choch #order-blocks #memoria
#performance #optimization #monitoring #testing
#integration #migration #setup #configuration
```

### **🎯 ALIASES FRECUENTES:**
```
"no funciona" → troubleshooting.md + emergency-procedures.md
"nuevo pattern" → protocols/03-templates-implementacion.md  
"deploy" → enterprise-deployment.md + production-checklist.md
"performance" → performance-optimization.md + performance-monitoring.md
"setup" → quick-start.md + configuration-guide.md
"memoria" → technical/docs/04-development-logs/memoria/
"smart money" → technical/docs/04-development-logs/smart-money/
```

---

## 📈 **WORKFLOW MAPS**

### **🔄 "NECESITO IMPLEMENTAR NUEVO PATRÓN ICT"**
```
1. 03-DOCUMENTATION/protocols/REGLAS_COPILOT.md (2 min)               # Reglas base
2. 03-DOCUMENTATION/protocols/03-templates-implementacion.md (3 min)  # Template patrón
3. 03-DOCUMENTATION/technical/docs/04-development-logs/[área]/ (5 min) # Contexto específico
4. Implementar usando template (20 min)
5. 03-DOCUMENTATION/protocols/04-templates-testing.md (10 min)        # Validación  
6. 03-DOCUMENTATION/protocols/05-templates-documentacion.md (5 min)   # Documentar
```

### **🔄 "NECESITO INTEGRAR NUEVO MÓDULO"**
```
1. 03-DOCUMENTATION/technical/docs/03-integration-plans/ (10 min)     # Planes existentes
2. 03-DOCUMENTATION/data-flow-reference.md (5 min)                   # Flujo datos
3. 03-DOCUMENTATION/module-integration.md (5 min)                    # Integración
4. Implementar integración (30 min)
5. 03-DOCUMENTATION/production-checklist.md (10 min)                # Verificar
```

### **🔄 "NECESITO RESOLVER PROBLEMA URGENTE"**
```
1. 03-DOCUMENTATION/troubleshooting.md (3 min)                       # Problemas comunes
2. 03-DOCUMENTATION/emergency-procedures.md (5 min)                  # Procedimientos
3. 03-DOCUMENTATION/reports/DASHBOARD_*_SOLUTION.md (2 min)         # Fixes específicos  
4. Aplicar solución (10 min)
5. 03-DOCUMENTATION/protocols/05-templates-documentacion.md (3 min)  # Documentar fix
```

---

## ✅ **VALIDATION QUICK CHECKS**

### **🎯 ANTES DE IMPLEMENTAR:**
```bash
# Check 1: ¿Leí las reglas? (30 seg)
grep -i "implementación" 03-DOCUMENTATION/protocols/REGLAS_COPILOT.md | head -3

# Check 2: ¿Tengo el contexto? (30 seg)  
ls 03-DOCUMENTATION/technical/docs/04-development-logs/[mi-área]/

# Check 3: ¿Estado actual claro? (30 seg)
grep -i "[mi-componente]" ESTADO_REAL_SISTEMA_REFERENCIA.md
```

### **🎯 DURANTE DESARROLLO:**
```bash
# Check 1: ¿Sigo template? (15 seg)
# Compare mi código vs. template

# Check 2: ¿Tests passing? (30 seg)
python -m pytest tests/test_[mi-componente].py

# Check 3: ¿Performance OK? (15 seg)  
# Verificar métricas <0.1s
```

### **🎯 AL FINALIZAR:**
```bash  
# Check 1: ¿Checklist completo? (1 min)
cat 03-DOCUMENTATION/production-checklist.md | head -10

# Check 2: ¿Documentación actualizada? (30 seg)
# Actualicé bitácora correspondiente?

# Check 3: ¿No rompí nada? (1 min)
python main.py --quick-test
```

---

## 🚀 **COPILOT SHORTCUTS - COPY & PASTE READY**

### **⚡ EMERGENCY SHORTCUTS:**
```bash
# Sistema no responde
python main.py --version && python -c "import MetaTrader5; print('MT5 OK')"

# Dashboard recovery
python 09-DASHBOARD/start_dashboard.py --recovery

# Logs críticos
tail -50 05-LOGS/system/general.log | grep ERROR
```

### **🔧 DEVELOPMENT SHORTCUTS:**
```bash
# Quick context
cat 03-DOCUMENTATION/COPILOT-CONTEXT-CARDS.md | grep -A5 "SMART MONEY"

# Template access
cat 03-DOCUMENTATION/protocols/03-templates-implementacion.md | grep -A20 "ICT Pattern"

# Status check
grep -i "smart.money" ESTADO_REAL_SISTEMA_REFERENCIA.md
```

### **🏢 ENTERPRISE SHORTCUTS:**
```bash
# Production check
cat 03-DOCUMENTATION/production-checklist.md | head -15

# Deploy guide
cat 03-DOCUMENTATION/enterprise-deployment.md | head -30

# Multi-account
cat 03-DOCUMENTATION/multi-account-management.md | head -25
```

---

**⚡ Acceso optimizado para máxima velocidad de desarrollo - ICT Engine v6.0 Enterprise**  
**🎯 Cards diseñadas para GitHub Copilot efficiency**

---

*Última actualización: 11 Septiembre 2025 - Quick Reference Cards para desarrollo ágil*
