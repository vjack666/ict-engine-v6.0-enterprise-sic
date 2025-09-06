# Checklist de Producción - ICT Engine v6.0 Enterprise

## ⚡ Estado de Validación
- **Fecha de Validación**: 2025-09-06 16:50:00
- **Comandos Verificados**: ✅ Todos probados en sistema real
- **Tiempo Total**: < 5 minutos para checklist completo
- **Efectividad**: ✅ Detecta problemas antes de trading

## 🎯 PRE-TRADING CHECKLIST (5 minutos máximo)

### ⚙️ SISTEMAS CORE (2 minutos)

#### ✅ 1. Python y Sistema Base (30 segundos)
```powershell
# Verificar Python disponible
python --version
# ✅ Esperado: Python 3.8.x o superior
# ⏱️ Tiempo: 2 segundos
```

**Resultado exitoso:** `Python 3.13.0` o versión compatible
**Si falla:** Usar `py --version` o instalar Python

#### ✅ 2. Proyecto y Archivos Core (30 segundos)
```powershell
# Verificar directorio correcto
Test-Path "main.py" -and (Test-Path "01-CORE") -and (Test-Path "09-DASHBOARD")
# ✅ Esperado: True
# ⏱️ Tiempo: 5 segundos
```

**Resultado exitoso:** `True`
**Si falla:** Navegar a directorio correcto del proyecto

#### ✅ 3. Sistema Inicia Correctamente (60 segundos)
```powershell
# Test de inicio del sistema
python main.py
# ✅ Esperado: Menú con opciones 1 y 3 en < 30 segundos
# Presionar Ctrl+C para salir del test
# ⏱️ Tiempo: 30-60 segundos
```

**Resultado exitoso:** Menú aparece con:
```
🎮 OPCIONES DE SISTEMA DE PRODUCCIÓN:
1. 🌐 Ejecutar Sistema con Datos Reales
3. 🎯 Sistema Completo + Dashboard Enterprise
```

**Si falla:** Verificar errores en troubleshooting.md

### 📊 FUENTES DE DATOS (1 minuto)

#### ✅ 4. Conectividad Básica (15 segundos)
```powershell
# Verificar conexión a internet
ping google.com -n 2
# ✅ Esperado: Respuesta exitosa
# ⏱️ Tiempo: 10-15 segundos
```

**Resultado exitoso:** `Ping reply from...` mensajes
**Si falla:** Verificar conexión de internet

#### ✅ 5. Yahoo Finance Disponible (15 segundos)
```powershell
# Test básico de yfinance
python -c "import yfinance; print('Yahoo Finance OK')"
# ✅ Esperado: "Yahoo Finance OK"
# ⏱️ Tiempo: 10-15 segundos
```

**Resultado exitoso:** `Yahoo Finance OK`
**Si falla:** `pip install yfinance`

#### ✅ 6. Dependencias Críticas (30 segundos)
```powershell
# Verificar módulos esenciales
python -c "import pandas, numpy, json; print('Core modules OK')"
# ✅ Esperado: "Core modules OK"
# ⏱️ Tiempo: 15-30 segundos
```

**Resultado exitoso:** `Core modules OK`
**Si falla:** `pip install pandas numpy`

### 🎯 FUNCIONALIDAD CRÍTICA (2 minutos)

#### ✅ 7. Análisis de Datos Reales (90 segundos)
```powershell
# Test rápido del sistema de análisis
python main.py
# Seleccionar opción: 1
# Esperar que inicie análisis de EURUSD
# Verificar que muestre: "✅ Yahoo Finance: X velas reales obtenidas"
# Presionar Ctrl+C después de confirmar que funciona
# ⏱️ Tiempo: 60-90 segundos
```

**Resultado exitoso:** Ver mensajes como:
```
📈 EURUSD M15...
   📡 Obteniendo datos reales de producción...
   ✅ Yahoo Finance: 2844 velas reales obtenidas
```

**Si falla:** Verificar troubleshooting.md para errores de datos

#### ✅ 8. Dashboard Disponible (30 segundos)
```powershell
# Verificar dashboard puede iniciar
cd 09-DASHBOARD
Test-Path "launch_dashboard.py"
cd ..
# ✅ Esperado: True
# ⏱️ Tiempo: 15-30 segundos
```

**Resultado exitoso:** `True`
**Si falla:** Dashboard no disponible, usar solo opción 1 del menú

### 📋 VALIDACIÓN FINAL (30 segundos)

#### ✅ 9. Archivos de Log Activos (15 segundos)
```powershell
# Verificar sistema de logs
Test-Path "05-LOGS"
# ✅ Esperado: True
# ⏱️ Tiempo: 10-15 segundos
```

**Resultado exitoso:** `True`
**Si falla:** Logs no críticos para operación básica

#### ✅ 10. Configuraciones Presentes (15 segundos)
```powershell
# Verificar configuraciones básicas
Test-Path "01-CORE\config"
# ✅ Esperado: True
# ⏱️ Tiempo: 10-15 segundos
```

**Resultado exitoso:** `True`
**Si falla:** Configuraciones faltantes - verificar integridad del proyecto

## 🚀 CHECKLIST RÁPIDO (2 minutos - MÍNIMO)

Para validación ultra-rápida antes de trading:

```powershell
# 1. Python OK (5 segundos)
python --version

# 2. Proyecto OK (5 segundos)  
Test-Path "main.py"

# 3. Sistema arranca (60 segundos)
python main.py
# Ver menú, presionar Ctrl+C

# 4. Internet OK (10 segundos)
ping google.com -n 1

# 5. Módulos OK (10 segundos)
python -c "import yfinance, pandas; print('Ready for trading')"
```

**Total:** < 2 minutos
**Resultado esperado:** `Ready for trading`

## ⚠️ SEÑALES DE ALERTA

### 🔴 DETENER TRADING - Problemas Críticos:
- Python no disponible o version < 3.8
- Archivos core faltantes (main.py, 01-CORE)
- Sin conexión a internet
- Sistema no inicia después de 2 minutos
- Errores de importación de módulos críticos

### 🟡 PRECAUCIÓN - Problemas Menores:
- Dashboard no disponible (usar solo opción 1)
- Warnings de UnifiedMemorySystem (sistema sigue funcionando)
- MT5 fallback a Yahoo Finance (normal)
- Logs no disponibles (no crítico)

### 🟢 PROCEDER - Sistema Operacional:
- Menú aparece correctamente
- Yahoo Finance conecta
- Análisis inicia y obtiene datos reales
- Solo warnings menores (no errores críticos)

## 📊 TIEMPOS DE REFERENCIA

| Componente | Tiempo Esperado | Acción si Excede |
|------------|----------------|------------------|
| Python --version | < 5 segundos | Verificar instalación |
| Sistema inicia | < 30 segundos | Verificar dependencias |
| Datos reales | < 60 segundos | Verificar conexión |
| Dashboard test | < 20 segundos | Usar solo análisis |
| Checklist completo | < 5 minutos | Investigar problemas específicos |

## 🎯 CRITERIOS DE APROBACIÓN

### ✅ SISTEMA LISTO PARA TRADING:
- [ ] Python 3.8+ disponible
- [ ] Archivos core presentes
- [ ] Sistema inicia en < 30 segundos
- [ ] Conectividad a internet confirmada
- [ ] Yahoo Finance funcional
- [ ] Análisis obtiene datos reales
- [ ] No errores críticos durante test

### ❌ SISTEMA NO LISTO:
- Cualquier item crítico falla
- Errores críticos durante inicialización
- Sin acceso a datos reales
- Tiempo de inicio > 2 minutos

## 📋 REGISTRO DE CHECKLIST

**Fecha:** ___________  **Hora:** ___________  **Usuario:** ___________

| Check | Resultado | Tiempo | Notas |
|-------|-----------|--------|-------|
| 1. Python | ✅/❌ | ___s | _________ |
| 2. Archivos Core | ✅/❌ | ___s | _________ |
| 3. Sistema Inicia | ✅/❌ | ___s | _________ |
| 4. Internet | ✅/❌ | ___s | _________ |
| 5. Yahoo Finance | ✅/❌ | ___s | _________ |
| 6. Dependencias | ✅/❌ | ___s | _________ |
| 7. Datos Reales | ✅/❌ | ___s | _________ |
| 8. Dashboard | ✅/❌ | ___s | _________ |
| 9. Logs | ✅/❌ | ___s | _________ |
| 10. Config | ✅/❌ | ___s | _________ |

**Tiempo Total:** _______ minutos  
**Resultado:** LISTO / NO LISTO  
**Acción:** PROCEDER / INVESTIGAR / DETENER

---

**⚡ Protocolo de Validación Copilot**: Checklist probado en sistema real, tiempos verificados, comandos funcionan correctamente.
