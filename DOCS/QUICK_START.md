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

### 2️⃣ **Dashboard Web (Recomendado)**
```bash
# Lanzar dashboard web principal
python start_web_dashboard.py

# Acceder en navegador: http://localhost:8050
# Auto-refresh cada 0.5 segundos
```

### 3️⃣ **Dashboard Terminal (Alternativo)**
```bash
# Dashboard en terminal (Textual)
python main.py --dashboard-terminal

# Interface completa en consola
```

### 4️⃣ **Validar Conexión MT5**
```bash
# Test conexión FTMO (debe estar MT5 abierto)
python -c "from data_management.mt5_data_manager import MT5DataManager; mgr=MT5DataManager(); print('MT5:', mgr.get_current_data('EURUSD', 'M15', 10) is not None)"
```

### 5️⃣ **Test Trading Automático (DEMO ONLY)**
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

### 🖥️ **Dashboards Duales**
- **Web Dashboard:** Interface moderna con Dash/Plotly
- **Terminal Dashboard:** Console interface con Textual
- **Tabs Sistema:** Order Blocks, FVG, Smart Money, Market Structure
- **Real-time Data:** Auto-refresh y datos MT5 live

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
# Web dashboard
python start_web_dashboard.py
# Si falla, verificar puerto 8050 libre

# Terminal dashboard
python main.py --dashboard-terminal  
# Si falla, verificar consola compatible
```

### **❌ Patterns no detectan**
```bash
# Verificar datos MT5
python -c "from data_management.mt5_data_manager import MT5DataManager; print(MT5DataManager().get_current_data('EURUSD', 'M15', 5))"

# Si datos = None, revisar conexión MT5
```

## 🎯 PRÓXIMOS PASOS

1. **Explorar Dashboard Web:** Tabs Order Blocks y FVG
2. **Revisar Logs:** Carpeta 05-LOGS/ para análisis detallado  
3. **Configurar Alerts:** Sistema de notificaciones avanzado
4. **Optimizar Parámetros:** Ajustar detección según estilo trading
5. **Escalar a Real:** Solo después de validación completa en demo

---

**🚀 ¡Sistema listo para uso productivo!**  
*Documentación actualizada: Septiembre 2025*