# INSTRUCCIONES PARA GESTIÓN REAL DE CUENTA MT5 ✅

## ITEM 1: CONFIGURACIÓN DE CUENTA MT5

### 1.1 Preparar Credenciales
- [x] Obtener número de cuenta demo MT5
- [x] Obtener contraseña de la cuenta
- [x] Identificar servidor del broker
- [x] Verificar que MT5 está instalado

### 1.2 Configurar Sistema
- [x] Editar `01-CORE/config/real_trading_config.json`
- [x] Insertar credenciales de cuenta MT5 ✅ FTMO-Demo configurado
- [x] Configurar ruta del terminal MT5
- [x] Establecer símbolos de trading permitidos

## ITEM 2: LÍMITES DE SEGURIDAD OPERACIONAL

### 2.1 Límites de Cuenta
- [x] Establecer balance mínimo permitido ($1000 configurado)
- [x] Configurar máxima pérdida diaria (5% del balance configurado)
- [x] Definir riesgo máximo por operación (2% del balance configurado)
- [x] Establecer número máximo de trades diarios (10 configurados)

### 2.2 Protecciones Automáticas
- [x] Activar emergency stop por margin level bajo (<200% configurado)
- [x] Configurar cierre automático por drawdown excesivo (10% máximo)
- [x] Establecer límite de pérdidas consecutivas (5 configuradas)
- [x] Activar protección por desconexión MT5 (30s timeout configurado)

## ITEM 3: INICIALIZACIÓN DEL SISTEMA

### 3.1 Arrancar Sistema Principal
- [x] Ejecutar: `python run_real_market_system.py`
- [x] Verificar conexión exitosa con MT5
- [x] Confirmar balance de cuenta visible
- [x] Validar símbolos disponibles para trading

### 3.2 Activar Dashboard de Gestión
- [x] Ejecutar: `python main.py`
- [x] Seleccionar "Opción 3: Sistema Completo + Dashboard Enterprise"
- [x] Verificar dashboard carga correctamente
- [x] Confirmar conexión con sistema principal

## ITEM 4: GESTIÓN DE RIESGOS EN VIVO

### 4.1 Configurar Position Sizing
- [x] Configurar cálculo automático basado en % de riesgo
- [x] Establecer tamaño máximo de posición (0.5 lotes configurado)
- [x] Configurar ajuste por volatilidad del símbolo
- [x] Definir spreads máximos aceptables (30 puntos máximo)

### 4.2 Gestión de Stop Loss y Take Profit
- [x] Configurar stop loss automático (dinámico configurado)
- [x] Establecer ratio risk/reward mínimo (2.0 configurado)
- [x] Activar trailing stop para posiciones ganadoras (50 puntos)
- [x] Configurar modificación automática de niveles

## ITEM 5: OPERACIONES DE TRADING REAL

### 5.1 Ejecución Manual de Trades
- [x] Configurar botones de compra/venta en dashboard
- [x] Establecer confirmación antes de ejecutar trades (60s timeout)
- [x] Configurar ejecución con stop loss automático
- [x] Activar logging de todas las operaciones

### 5.2 Trading Automático
- [x] Configurar filtros de calidad de señal (0.6 confianza mínima)
- [x] Establecer horarios de trading permitidos
- [x] Activar auto-trading desde dashboard (manual por defecto)
- [x] Configurar suspensión automática por límites

## ITEM 6: MONITOREO DE CUENTA EN TIEMPO REAL

### 6.1 Tracking de Balance y Equity
- [x] Configurar actualización cada 5 segundos (1s configurado)
- [x] Activar alertas por cambios significativos
- [x] Configurar tracking de margin level
- [x] Establecer alertas de margin call

### 6.2 Monitoreo de Posiciones Activas
- [x] Visualizar posiciones abiertas en tiempo real
- [x] Tracking de PnL no realizado
- [x] Monitoreo de stop loss y take profit
- [x] Alertas de posiciones cerca de límites

## ITEM 7: GESTIÓN DE EMERGENCIAS

### 7.1 Procedimientos de Emergency Stop
- [x] Configurar botón de emergency stop en dashboard
- [x] Activar cierre inmediato de todas las posiciones
- [x] Desactivar auto-trading automáticamente
- [x] Generar reporte de emergency action

### 7.2 Manejo de Desconexiones
- [x] Configurar reconexión automática a MT5 (3 intentos)
- [x] Establecer procedimientos para pérdida de conexión
- [x] Activar alertas por desconexión prolongada
- [x] Configurar backup de posiciones abiertas

## ITEM 8: REPORTING Y ANÁLISIS

### 8.1 Generación de Reportes Diarios
- [x] Configurar reporte automático de PnL diario
- [x] Generar resumen de trades ejecutados
- [x] Calcular métricas de performance
- [x] Export de datos para análisis (CSV configurado)

### 8.2 Tracking de Performance
- [x] Calcular win rate en tiempo real
- [x] Tracking de drawdown máximo
- [x] Análisis de profit factor
- [x] Seguimiento de trades por símbolo

## ITEM 9: CONFIGURACIÓN AVANZADA

### 9.1 Optimización de Ejecución
- [x] Configurar slippage máximo aceptable (20 puntos)
- [x] Establecer timeout para órdenes (30s)
- [x] Configurar reintentos automáticos (3 intentos)
- [x] Optimizar latencia de ejecución (1000ms threshold)

### 9.2 Gestión Multi-Símbolo
- [x] Configurar correlaciones entre pares (0.7 threshold)
- [x] Establecer límites de exposición total (3 posiciones máx)
- [x] Configurar diversificación automática
- [x] Gestión de riesgo por grupo de símbolos

## ITEM 10: OPERACIÓN CONTINUA

### 10.1 Mantenimiento del Sistema
- [x] Configurar logs de sistema (múltiples niveles)
- [x] Establecer rotación de archivos de log (90 días ejecución)
- [x] Configurar backup de configuraciones (24h interval)
- [x] Monitoring de recursos del sistema (80% CPU threshold)

### 10.2 Escalabilidad Operacional
- [x] Configurar múltiples timeframes de análisis (M5, M15, H1)
- [x] Establecer gestión de memoria eficiente
- [x] Optimizar performance para operación 24/7
- [x] Configurar alertas de sistema críticas

---

## 🎯 **ESTADO ACTUAL DEL SISTEMA**

### ✅ **COMPLETAMENTE CONFIGURADO (100%):**
- **Credenciales MT5:** ✅ FTMO-Demo cuenta 1511525932 configurada
- **Límites de Seguridad:** Balance mínimo $1000, pérdida máxima diaria 5%, riesgo por trade 2%
- **Protecciones Automáticas:** Emergency stops, circuit breakers, timeout protections
- **Dashboard Enterprise:** Interface completa con botones de trading, confirmaciones
- **Monitoreo en Tiempo Real:** Updates cada 1 segundo, alertas configuradas
- **Gestión de Riesgos:** Position sizing dinámico, correlación, volatilidad
- **Sistema de Logging:** Múltiples niveles, retención configurada, exports automáticos

### 🎯 **SISTEMA 100% LISTO:**
- **✅ Todas las configuraciones completadas**
- **✅ Credenciales FTMO-Demo insertadas**
- **✅ Sistema preparado para trading real**

### 📋 **CONFIGURACIÓN COMPLETADA EN `real_trading_config.json`:**

```json
"mt5_connection": {
  "connection_settings": {
    "server": "FTMO-Demo",              // ✅ CONFIGURADO
    "login": "1511525932",              // ✅ CONFIGURADO  
    "password": "6U*ss5@D2RLa",         // ✅ CONFIGURADO
    "timeout": 60000
  }
}
```

## 🚀 **SISTEMA LISTO PARA LANZAMIENTO:**

### **Comando para iniciar trading real:**
```powershell
python run_real_market_system.py
```

### **O sistema completo con dashboard:**
```powershell
python main.py
# Seleccionar opción 3: Sistema Completo + Dashboard Enterprise
```

### 🏆 **SISTEMA 100% LISTO PARA TRADING REAL**

**El sistema ICT Engine v6.0 Enterprise está completamente configurado con credenciales FTMO-Demo para operaciones reales de trading.**

---

*Generado automáticamente el 6 de Septiembre 2025*  
*Sistema de trading real completamente implementado*  
*Credenciales FTMO-Demo configuradas*  
*Safety limits y protecciones empresariales activadas*  
*Dashboard enterprise operativo y listo*
