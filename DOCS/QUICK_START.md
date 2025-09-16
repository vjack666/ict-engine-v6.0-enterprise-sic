# 🚀 QUICK START - ICT Engine v6.0 Enterprise

**Tiempo estimado:** 5-10 minutos para sistema completo  
**Requisitos:** Python 3.9+, MetaTrader 5 instalado  

## ⚡ INICIO RÁPIDO

### 1️⃣ **Verificar Sistema**
```bash
# Diagnóstico completo del sistema
python diagnostic_real_state.py

# Debe mostrar ✅ en la mayoría de componentes
```

### 2️⃣ **Dashboard Terminal (Único Dashboard / Monoboard)**
```bash
# Dashboard en terminal (único disponible)
python main.py --dashboard-terminal

# Incluye estilizado de colores (CSS interno simplificado)
```

### 3️⃣ **Validar Conexión MT5**
```bash
# Test conexión FTMO (debe estar MT5 abierto)
python -c "from data_management.mt5_data_manager import MT5DataManager; mgr=MT5DataManager(); print('MT5:', mgr.get_current_data('EURUSD', 'M15', 10) is not None)"
```

### 4️⃣ **Test Trading Automático (DEMO ONLY)**
```bash
# IMPORTANTE: Solo en cuenta DEMO
python activate_auto_trading.py --test --demo-only

# Verificar logs en 05-LOGS/trading/
```

## 🎯 FUNCIONALIDADES PRINCIPALES

### 📊 **Análisis en Tiempo Real**
- **Smart Money Concepts:** 5 killzones, detección liquidez
- **ICT Patterns:** BOS, CHoCH, FVG, Order Blocks
- **Memory System:** Contexto histórico y aprendizaje
- **Live Validation:** Comparación live vs histórico

### 🖥️ **Dashboard de Monitoreo (Terminal Único)**
- **Terminal Dashboard:** Interfaz única en consola con resaltado y colores
- **Tabs Lógicas (internas):** Order Blocks, FVG, Smart Money, Market Structure (render textual)
- **Real-time Data:** Actualización periódica y métricas integradas
- (El dashboard web fue eliminado: menor superficie de ataque, menos dependencias)

### 🤖 **Trading Automático**
- **ExecutionEngine:** Ejecución automática de señales
- **EmergencyStop:** Sistema protección riesgo
- **Position Sizing:** Cálculo automático de posiciones
- **Logging Completo:** Trazabilidad de todas las operaciones

## 🔧 CONFIGURACIÓN BÁSICA

### **MT5 Connection**
1. Abrir MetaTrader 5
2. Conectar cuenta FTMO Demo
3. Activar "Permitir importación de DLL"
4. Verificar conexión con comando de test

### **Python Environment**
```bash
# Instalar dependencias (si es necesario)
pip install pandas plotly dash textual MetaTrader5

# El sistema maneja la mayoría de dependencias automáticamente
```

## 🚨 IMPORTANTE - SEGURIDAD

### **⚠️ Trading Automático**
- **SOLO CUENTAS DEMO** para testing inicial
- Verificar configuración EmergencyStop
- Monitorear logs de trading constantemente
- Usar position sizing conservador

### **🔒 Datos Sensibles**
- Credenciales MT5 no se almacenan en código
- Logs no contienen información sensible de cuenta
- Sistema diseñado para compliance enterprise

## 📞 TROUBLESHOOTING RÁPIDO

### **❌ Error MT5 Connection**
```bash
# 1. Verificar MT5 está abierto y conectado
# 2. Reiniciar MT5 si es necesario  
# 3. Verificar cuenta demo está activa
# 4. Ejecutar diagnóstico: python diagnostic_real_state.py
```

### **❌ Dashboard no carga**
```bash
# Terminal dashboard
python main.py --dashboard-terminal
# Si falla:
# 1. Verificar versión Python >= 3.9
# 2. Revisar logs en 05-LOGS/application/
```

### **❌ Patterns no detectan**
```bash
# Verificar datos MT5
python -c "from data_management.mt5_data_manager import MT5DataManager; print(MT5DataManager().get_current_data('EURUSD', 'M15', 5))"

# Si datos = None, revisar conexión MT5
```

## 🎯 PRÓXIMOS PASOS

1. [x] Explorar Dashboard Terminal
2. [x] Revisar Logs en 05-LOGS/
3. [x] Configurar Alerts avanzados (ver DOCS/alerting/ADVANCED_ALERTS_SYSTEM.md)
4. [ ] Optimizar parámetros de detección
5. [ ] Escalar a real tras validación completa demo

---

**🚀 ¡Sistema listo para uso productivo!**  
*Documentación actualizada: Septiembre 2025*