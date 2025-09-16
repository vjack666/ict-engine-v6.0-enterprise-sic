# 🔧 Tools - ICT Engine v6.0 Enterprise

Esta carpeta contiene utilidades y herramientas auxiliares del sistema.

## 📄 Archivos

### 📋 Validadores
- **`validate_docs.sh`** - Script shell para validar documentación y consistencia del proyecto

## 💻 Uso

```bash
# Desde el directorio raíz del proyecto
cd tools

# Validar documentación (Linux/WSL)
./validate_docs.sh

# Validar documentación (Windows con Git Bash)
bash validate_docs.sh
```

## 🎯 Funcionalidades

### validate_docs.sh
- ✅ Validación de estructura de directorios
- 📄 Verificación de archivos de documentación requeridos
- 🔍 Detección de enlaces rotos en markdown
- 📊 Validación de consistencia entre README y código
- 🔧 Verificación de archivos de configuración

## 📝 Notas

- Las herramientas están diseñadas para ser ejecutadas desde cualquier ambiente
- Compatible con Windows, Linux y macOS
- Integradas con el flujo de CI/CD del proyecto
- Generan reportes detallados de validación