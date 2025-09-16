# 🧪 Tests - ICT Engine v6.0 Enterprise

Esta carpeta contiene todas las pruebas, validaciones y tests de estrés del sistema.

## 📄 Archivos

### 🧪 Tests de Estrés
- **`integrated_stress_test.py`** - Suite integrada de pruebas de estrés del sistema completo
- **`stress_test_production.py`** - Pruebas de estrés específicas para ambiente de producción

### ✅ Validadores
- **`validate_data_management.py`** - Validación completa del módulo data_management

## 💻 Uso

```bash
# Desde el directorio raíz del proyecto
cd tests

# Test de estrés integrado
python integrated_stress_test.py

# Test de producción
python stress_test_production.py

# Validación de data management
python validate_data_management.py
```

## 📊 Métricas Validadas

### Tests de Estrés
- ⏱️ **Startup time** < 30 segundos
- 🧠 **Memory usage** < 512MB bajo carga  
- ⚡ **CPU usage** < 25% promedio
- 🔧 **Config loading** < 5 segundos
- 📊 **Dashboard response** < 2 segundos
- 📝 **Log writing throughput** > 1000 entries/s

### Tests de Producción
- 🚀 **Latencia** < 50ms en condiciones normales
- 📈 **Throughput** > 1000 validaciones/segundo  
- ❌ **Error rate** < 2% máximo
- 🔄 **Recovery time** < 30 segundos

## 🔧 Configuración

- Los tests acceden automáticamente a los módulos del proyecto
- Incluyen manejo de rutas relativas para importaciones
- Compatibles con el sistema de logging unificado
- Generan reportes detallados de performance

## 📝 Notas

- Todos los tests son no-destructivos para el ambiente de producción
- Incluyen validaciones de integridad del sistema
- Compatibles con ejecución en paralelo
- Optimizados para CI/CD pipelines