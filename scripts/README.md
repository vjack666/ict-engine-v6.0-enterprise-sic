# 📁 Scripts - ICT Engine v6.0 Enterprise

Esta carpeta contiene los scripts de automatización y utilidades principales del sistema.

## 📄 Archivos

### 🚀 Trading Automático
- **`activate_auto_trading.py`** - Script para iniciar trading automático con Order Blocks
- **`implement_real_trading.py`** - Implementación completa del sistema de trading en cuenta real
- **`enhance_market_display.py`** - Mejoras de visualización de datos de mercado

## 💻 Uso

```bash
# Desde el directorio raíz del proyecto
cd scripts

# Trading automático demo
python activate_auto_trading.py --test

# Implementación cuenta real
python implement_real_trading.py --production

# Mejoras de display
python enhance_market_display.py
```

## 🔧 Configuración

Todos los scripts utilizan automáticamente las configuraciones del proyecto principal y tienen acceso a los módulos en `01-CORE/`.

## 📝 Notas

- Los scripts incluyen manejo de rutas automático para importar módulos del proyecto
- Todos incluyen logging integrado con el sistema unificado
- Compatibles con el protocolo de logging enterprise del proyecto