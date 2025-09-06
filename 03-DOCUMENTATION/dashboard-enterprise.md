# Dashboard Enterprise - Guía de Uso

## ⚡ Estado de Validación
- **Fecha de Validación**: 2025-09-06 16:11:30
- **Archivo Principal Verificado**: ✅ `09-DASHBOARD/launch_dashboard.py` existe
- **Ruta Confirmada**: `C:\Users\v_jac\Desktop\ict-engine-v6.0-enterprise-sic\09-DASHBOARD\`
- **Estado del Módulo**: ✅ DISPONIBLE

## 🚀 Acceso al Dashboard

### Método Principal (VERIFICADO)
```powershell
# Navegar al directorio del dashboard
cd 09-DASHBOARD

# Ejecutar el launcher
python launch_dashboard.py
```

### Método Alternativo
```powershell
# Ejecutar desde directorio raíz
python 09-DASHBOARD\launch_dashboard.py
```

## 📊 Componentes del Dashboard CONFIRMADOS

### Archivos Principales
```
✅ launch_dashboard.py            - Lanzador principal del dashboard
✅ dashboard.py                   - Dashboard principal  
✅ ict_dashboard.py               - Dashboard ICT específico
✅ start_dashboard.py             - Iniciador alternativo
✅ debug_connections.py           - Herramientas de debug
✅ test_real_data.py              - Pruebas con datos reales
```

### Estructura de Soporte
```
✅ bridge/                        - Comunicación con el sistema principal
✅ components/                    - Componentes de interfaz de usuario
✅ config/                        - Configuraciones del dashboard
✅ core/                          - Núcleo del dashboard
✅ data/                          - Gestión de datos del dashboard
✅ patterns_analysis/             - Análisis de patrones visuales
✅ themes/                        - Temas y estilos visuales
✅ utils/                         - Utilidades del dashboard
✅ widgets/                       - Widgets personalizados
```

## 🎯 Funcionalidades Esperadas

### Análisis en Tiempo Real
- **Visualización de Patterns ICT**: Basado en `ict_dashboard.py`
- **Análisis Smart Money**: Integración con sistema principal
- **Multi-Timeframe Views**: Soporte para M15, H1, H4
- **Real-Time Data**: Conexión con fuentes de datos en vivo

### Dashboard Enterprise
- **Interface Profesional**: Dashboard empresarial especializado
- **Análisis de Patrones**: Visualización de los 14+ patterns detectados
- **Monitoring en Vivo**: Monitoreo de EURUSD, GBPUSD, USDJPY, XAUUSD
- **Debug Tools**: Herramientas de depuración incluidas

## 🔧 Configuración

### Dependencias del Dashboard
El dashboard utiliza la misma base del sistema principal:
- **Sistema de Análisis**: Conecta con `01-CORE/analysis/`
- **Smart Money**: Integración con `01-CORE/smart_money_concepts/`
- **Memoria Unificada**: Acceso al `UnifiedMemorySystem v6.1`

### Datos en Tiempo Real
- **Fuente Principal**: Yahoo Finance (confirmado operacional)
- **Fallback MT5**: Configurado pero requiere ajustes en `get_historical_data`
- **Persistencia**: Archivos JSON en `04-DATA/`

## 📋 Comandos de Verificación

### Verificar Dashboard
```powershell
# Confirmar existencia del launcher
Test-Path "09-DASHBOARD\launch_dashboard.py"

# Verificar estructura completa
Get-ChildItem "09-DASHBOARD" -Recurse -Name
```

### Debug del Dashboard
```powershell
# Ejecutar herramientas de debug
cd 09-DASHBOARD
python debug_connections.py

# Probar con datos reales
python test_real_data.py
```

## ⚠️ Notas de Integración

### Conexión con Sistema Principal
El dashboard está diseñado para trabajar en conjunto con:
- **Sistema de Producción**: `run_real_market_system.py`
- **Análisis Completo**: `run_complete_system.py`
- **Core Engine**: `main.py`

### Datos Compartidos
- **Análisis JSON**: Lee los archivos `production_analysis_*.json`
- **Reportes**: Accede a `production_system_report_*.json`
- **Memoria**: Sincroniza con `UnifiedMemorySystem`

## 🎯 Próximos Pasos

### Para Usar el Dashboard:
1. **Ejecutar Sistema Principal**: `python main.py` (generar datos)
2. **Lanzar Dashboard**: `cd 09-DASHBOARD && python launch_dashboard.py`
3. **Monitorear**: Visualizar análisis en tiempo real

### Para Debug:
1. **Verificar Conexiones**: `python debug_connections.py`
2. **Probar Datos**: `python test_real_data.py`
3. **Revisar Logs**: Consultar `05-LOGS/application/`

---

**⚡ Protocolo de Validación Copilot**: Dashboard verificado mediante confirmación de archivos y estructura del sistema.
