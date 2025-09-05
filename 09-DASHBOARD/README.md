# 🎯 ICT Dashboard v6.1 Enterprise

Dashboard modular y escalable para el ICT Engine v6.1 Enterprise, basado en los tests existentes y diseñado para uso en producción.

## 📋 Características

### ✅ **Interfaz Moderna**
- **Rich Interface**: Interfaz rica en consola con layouts dinámicos
- **Textual Interface**: Interfaz tabbed avanzada con navegación por teclado
- **Temas Personalizables**: Soporte para múltiples temas visuales

### ✅ **Datos en Tiempo Real**
- **FVG Statistics**: Estadísticas de Fair Value Gaps en vivo
- **Market Data**: Datos de mercado actualizados continuamente  
- **Coherence Analysis**: Análisis de coherencia del mercado integrado
- **System Metrics**: Métricas de rendimiento del sistema

### ✅ **Sistema de Alertas**
- **Alertas Inteligentes**: Sistema de notificaciones por severidad
- **Historial de Alertas**: Registro completo de eventos del sistema
- **Filtrado Avanzado**: Filtros por tipo, severidad y tiempo

## 🏗️ Arquitectura

```
09-DASHBOARD/
├── ict_dashboard.py          # 🎯 Dashboard principal
├── core/                     # 🔧 Motor del dashboard
│   ├── dashboard_engine.py   # Motor principal y gestión de estado
│   └── data_collector.py     # Recolección de datos en tiempo real
├── widgets/                  # 🎨 Interfaces de usuario
│   └── main_interface.py     # Interfaz principal Rich/Textual
├── components/               # 📊 Componentes visuales
│   ├── fvg_widget.py         # Widget de estadísticas FVG
│   ├── market_widget.py      # Widget de datos de mercado
│   ├── coherence_widget.py   # Widget de análisis de coherencia
│   └── alerts_widget.py      # Widget de alertas
├── themes/                   # 🎨 Temas visuales
├── utils/                    # 🛠️ Utilidades
└── data/                     # 📊 Datos del dashboard
```

## 🚀 Uso Rápido

### **Inicio Básico**
```python
from ict_dashboard import ICTDashboard

# Crear dashboard con configuración por defecto
dashboard = ICTDashboard()

# Iniciar dashboard
dashboard.start()
```

### **Configuración Personalizada**
```python
from ict_dashboard import ICTDashboard

# Configuración personalizada
config = {
    'symbols': ['EURUSD', 'GBPUSD', 'XAUUSD'],
    'timeframes': ['M15', 'H1'],
    'update_interval': 2.0,
    'theme': 'professional',
    'layout_mode': 'tabbed',  # 'tabbed' o 'grid'
    'enable_alerts': True,
    'show_debug': True
}

# Crear dashboard personalizado
dashboard = ICTDashboard(config)
dashboard.start()
```

## 📊 Pestañas del Dashboard

### **📈 Overview**
- Resumen general del sistema
- Estado actual del mercado
- Métricas principales

### **📊 FVG Stats**
- Estadísticas de Fair Value Gaps
- FVGs activos por símbolo/timeframe
- Tasa de éxito y rendimiento

### **💹 Market Data**
- Datos de mercado en tiempo real
- Precios, cambios y volatilidad
- Tendencias por símbolo

### **🧠 Coherence**
- Análisis de coherencia del mercado
- Score de coherencia y recomendaciones
- Estado de Kill Zones

### **🚨 Alerts**
- Alertas del sistema por severidad
- Historial de eventos
- Notificaciones en tiempo real

## ⌨️ Controles de Teclado

- **Q**: Salir del dashboard
- **R**: Actualizar datos manualmente
- **S**: Toggle de estadísticas
- **Tab**: Navegar entre pestañas
- **Esc**: Menú principal

## 🔧 Configuración

### **Parámetros de Configuración**
```python
{
    'update_interval': 2.0,        # Intervalo de actualización (segundos)
    'symbols': ['EURUSD', ...],    # Símbolos a monitorear
    'timeframes': ['M15', 'H1'],   # Timeframes del análisis
    'theme': 'dark',               # Tema visual
    'enable_alerts': True,         # Habilitar alertas
    'auto_refresh': True,          # Auto-actualización
    'show_debug': False,           # Mostrar información de debug
    'data_source': 'live',         # 'live' o 'mock'
    'layout_mode': 'tabbed'        # 'tabbed' o 'grid'
}
```

## 🔗 Integración

### **Con Sistema FVG**
El dashboard se integra automáticamente con:
- `FVGMemoryManager`: Estadísticas de FVG en tiempo real
- `MarketConditionAdapter`: Análisis de coherencia del mercado
- Sistema de alertas del ICT Engine

### **Con Tests Existentes**
Basado en funcionalidades de:
- `progress_dashboard.py`: Interfaz tabbed y métricas
- `progress_dashboard_blackbox.py`: Instrumentación y logging
- `dashboard_real_time.py`: Datos en tiempo real

## 📈 Métricas Monitoreadas

- **Sistema**: Memoria, CPU, uptime, threads
- **FVG**: Estadísticas completas de Fair Value Gaps
- **Mercado**: Precios, volatilidad, tendencias
- **Coherencia**: Score, momentum, kill zones
- **Alertas**: Eventos por severidad y tiempo

## 🎨 Temas Disponibles

- **dark**: Tema oscuro por defecto
- **professional**: Tema profesional con colores conservadores
- **trading**: Tema optimizado para trading
- **minimal**: Tema minimalista

## 🚦 Estados del Sistema

- **🟢 NORMAL_TRADING**: Condiciones normales de trading
- **🟡 CAUTIOUS_TRADING**: Trading cauteloso recomendado
- **🔴 AVOID_TRADING**: Evitar trading por condiciones adversas
- **⚪ ANALYSIS_MODE**: Modo solo análisis

## 📝 Logging

El dashboard incluye logging detallado:
- Eventos de interfaz
- Actualizaciones de datos
- Errores y excepciones
- Métricas de rendimiento

## 🔄 Actualizaciones

### **Automáticas**
- Datos de mercado cada 2 segundos
- Estadísticas FVG cada 5 segundos
- Análisis de coherencia cada 10 segundos

### **Manuales**
- Presionar 'R' para actualización forzada
- Click en botones de actualización
- Comandos de consola

---

**Versión**: v6.1.0-enterprise-dashboard  
**Fecha**: 4 de Septiembre 2025  
**Equipo**: ICT Engine v6.1 Enterprise Team
