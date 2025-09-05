# 🔧 CONFIGURACIÓN DE COPILOT PERSONALIZADA

**Archivo:** `07-configuracion-copilot.md`  
**Propósito:** Configuración específica y personalizada para GitHub Copilot en el proyecto ICT Engine

---

## 🎯 **CONFIGURACIÓN DE CONTEXTO**

### **📋 Context Prompt Template (COPIAR AL INICIO DE CADA SESIÓN)**

```markdown
## 🏗️ ICT ENGINE v6.0 ENTERPRISE - CONTEXT SETUP

**ARQUITECTURA:** Python enterprise-grade, SIC v3.1, SLUC v2.1, UnifiedMemorySystem
**COMPLIANCE:** Strict enterprise standards, zero-ambiguity code, full documentation
**LOGGING:** SmartTradingLogger con formato estándar, todas las operaciones loggeadas
**TESTING:** Comprehensive test coverage, enterprise validation patterns
**INTEGRATION:** SIC Bridge para todas las operaciones, MT5 data management

### ⚡ REGLAS CRÍTICAS PARA COPILOT:
1. **NUNCA duplicar funcionalidad existente** - buscar siempre en codebase primero
2. **SIEMPRE usar SIC/SLUC** - no implementar logging o config desde cero
3. **COMPLIANCE OBLIGATORIO** - seguir protocolo enterprise en todo momento  
4. **DOCUMENTATION REQUIRED** - cada función requiere docstring completo
5. **PERFORMANCE AWARE** - validar rendimiento en cada implementación

### 📂 ESTRUCTURA DE PROYECTO:
- `core/`: Módulos principales (POI, memory, analysis)
- `sistema/`: SIC Bridge, SLUC integration
- `tests/`: Test suite enterprise
- `docs/`: Documentación técnica y bitácoras
- `protocolo-trabajo-copilot/`: Este protocolo y templates

### 🧩 COMPONENTES ENTERPRISE ACTIVOS:
- SICBridge: `from sistema.sic_bridge import SICBridge`
- SmartTradingLogger: `from core.smart_trading_logger import SmartTradingLogger`
- UnifiedMemorySystem: `from core.data_management.unified_memory_system import UnifiedMemorySystem`
- POI System: `from core.poi_system import POISystem`

### 📊 CURRENT PHASE STATUS:
- Fase 3 completada: Multi-timeframe engine integration
- Active development: Fractal Analysis enhancement, performance optimization
- Next targets: Enterprise dashboard, advanced pattern recognition

**USO:** Pegar este contexto al inicio de cada nueva conversación con Copilot.
```

### **🎛️ Configuración de VS Code Settings**

```json
{
    "github.copilot.advanced": {
        "length": 2000,
        "temperature": 0.1,
        "top_p": 0.95
    },
    "github.copilot.enable": {
        "*": true,
        "yaml": true,
        "plaintext": false,
        "markdown": true,
        "python": true
    },
    "github.copilot.editor.enableAutoCompletions": true,
    "github.copilot.editor.iterateCodeBlocks": true,
    "github.copilot.advanced.debug.chatHistory": true,
    "github.copilot.renameSuggestions.triggerAutomatically": false,
    "github.copilot.conversation.localeOverride": "es",
    
    // ICT Engine specific settings
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.analysis.extraPaths": [
        "./core",
        "./sistema", 
        "./tests"
    ],
    "python.analysis.autoImportCompletions": true,
    "python.analysis.packageIndexDepths": [
        { "name": "core", "depth": 3 },
        { "name": "sistema", "depth": 2 }
    ]
}
```

---

## 📝 **PROMPTS ESPECIALIZADOS**

### **🔍 Prompt para Análisis de Codebase**
```
Analiza el codebase del ICT Engine v6.0 para [DESCRIPCIÓN_TAREA]. 

CONTEXT REQUIRED:
- Buscar funcionalidad similar existente
- Verificar compliance con SIC/SLUC
- Identificar patrones enterprise
- Revisar documentación previa

DELIVERABLES:
- Análisis de duplicación (OBLIGATORIO)
- Propuesta de implementación con SIC/SLUC
- Plan de testing enterprise
- Documentación y bitácora updates

COMPLIANCE CHECK:
- [ ] SICBridge integration verified
- [ ] SmartTradingLogger implementation
- [ ] Performance benchmarks defined
- [ ] Documentation template used
```

### **⚙️ Prompt para Implementación Enterprise**
```
Implementa [FUNCIONALIDAD] siguiendo el protocolo enterprise ICT Engine v6.0.

REQUIREMENTS:
- Usar SICBridge para configuración
- SmartTradingLogger para todas las operaciones  
- Seguir patterns de core/poi_system.py
- UnifiedMemorySystem para persistence
- Comprehensive error handling

ARCHITECTURE:
- Class-based design con enterprise patterns
- Configuration via SIC
- Full logging via SLUC
- Memory-efficient implementation
- Comprehensive testing

OUTPUT FORMAT:
- Código production-ready
- Tests correspondientes
- Documentación técnica
- Bitácora de implementación
```

### **🧪 Prompt para Testing Enterprise**
```
Crear suite de tests enterprise para [COMPONENTE] en ICT Engine v6.0.

TEST COVERAGE REQUIRED:
- Unit tests para todas las funciones públicas
- Integration tests con SIC/SLUC
- Performance benchmarks
- Error handling validation
- Memory leak detection

ENTERPRISE PATTERNS:
- Usar pytest con fixtures enterprise
- Mock SIC/SLUC appropriately  
- Validate logging output
- Test configuration scenarios
- Memory usage validation

DELIVERABLES:
- test_[componente].py con coverage >90%
- test_integration_[componente].py
- Performance benchmark results
- Test report en formato enterprise
```

### **📊 Prompt para Optimización de Performance**
```
Optimizar performance de [COMPONENTE] en ICT Engine v6.0.

ANALYSIS REQUIRED:
- Profile current performance
- Identify bottlenecks
- Memory usage analysis
- SIC/SLUC overhead assessment

OPTIMIZATION TARGETS:
- Execution time reduction
- Memory footprint optimization
- SIC cache efficiency
- SLUC logging performance

VALIDATION:
- Before/after benchmarks
- Memory profiling results
- Production environment testing
- Enterprise compliance maintained
```

---

## 🎨 **SNIPPETS PERSONALIZADOS**

### **📋 Snippet: Enterprise Class Template**
```python
# ===== ENTERPRISE CLASS TEMPLATE =====
# Prefix: ent-class
from typing import Dict, Any, Optional, List
from sistema.sic_bridge import SICBridge
from core.smart_trading_logger import SmartTradingLogger

class ${1:ClassName}:
    """
    ${2:Brief description of the class}
    
    Esta clase implementa ${3:detailed functionality description}
    siguiendo los estándares enterprise ICT Engine v6.0.
    
    Attributes:
        ${4:attribute_name} (${5:type}): ${6:description}
    
    Enterprise Compliance:
        - SIC Integration: Configuration management
        - SLUC Logging: Comprehensive operation logging
        - Memory Management: Efficient resource utilization
        - Error Handling: Comprehensive exception management
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize ${1:ClassName} with enterprise configuration.
        
        Args:
            config: Optional configuration dict, uses SIC if None
        """
        self.sic = SICBridge()
        self.logger = SmartTradingLogger()
        
        # Load configuration
        self.config = config or self.sic.get_config("${7:config_section}")
        
        # Enterprise initialization
        self._initialize_enterprise_components()
        
        self.logger.info(
            f"${1:ClassName} initialized successfully",
            component="${1:ClassName}",
            config_loaded=bool(self.config)
        )
    
    def _initialize_enterprise_components(self):
        """Initialize enterprise-specific components."""
        ${8:# Implementation here}
        pass
    
    def ${9:main_method}(self, ${10:parameters}) -> ${11:return_type}:
        """
        ${12:Method description}
        
        Args:
            ${10:parameters}: ${13:parameter_description}
        
        Returns:
            ${11:return_type}: ${14:return_description}
        
        Raises:
            ${15:ExceptionType}: ${16:exception_description}
        """
        try:
            self.logger.info(
                f"Starting ${9:main_method}",
                component="${1:ClassName}",
                parameters=${10:parameters}
            )
            
            # Implementation
            ${17:# Your implementation here}
            
            self.logger.info(
                f"${9:main_method} completed successfully",
                component="${1:ClassName}"
            )
            
            return ${18:result}
            
        except Exception as e:
            self.logger.error(
                f"Error in ${9:main_method}: {str(e)}",
                component="${1:ClassName}",
                error_type=type(e).__name__
            )
            raise
```

### **🧪 Snippet: Enterprise Test Template**
```python
# ===== ENTERPRISE TEST TEMPLATE =====
# Prefix: ent-test
import pytest
import unittest.mock as mock
from unittest.mock import MagicMock, patch
from typing import Any, Dict

from sistema.sic_bridge import SICBridge
from core.smart_trading_logger import SmartTradingLogger
from ${1:module_path} import ${2:ClassUnderTest}

class Test${2:ClassUnderTest}:
    """
    Enterprise test suite for ${2:ClassUnderTest}.
    
    Test Coverage:
        - Unit tests for all public methods
        - Integration tests with SIC/SLUC
        - Performance benchmarks
        - Error handling validation
    """
    
    @pytest.fixture
    def mock_sic(self):
        """Mock SIC Bridge for testing."""
        with patch('sistema.sic_bridge.SICBridge') as mock:
            mock_instance = MagicMock()
            mock_instance.get_config.return_value = {
                "${3:config_key}": "${4:config_value}"
            }
            mock.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture  
    def mock_logger(self):
        """Mock Smart Trading Logger for testing."""
        with patch('core.smart_trading_logger.SmartTradingLogger') as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            yield mock_instance
    
    @pytest.fixture
    def ${5:test_instance}(self, mock_sic, mock_logger):
        """Create test instance with mocked dependencies."""
        return ${2:ClassUnderTest}()
    
    def test_initialization_success(self, ${5:test_instance}, mock_sic, mock_logger):
        """Test successful initialization."""
        # Verify SIC configuration loaded
        mock_sic.get_config.assert_called_once()
        
        # Verify logger initialization
        mock_logger.info.assert_called()
        
        # Verify instance state
        assert ${5:test_instance}.config is not None
    
    def test_${6:main_method}_success(self, ${5:test_instance}, mock_logger):
        """Test successful ${6:main_method} execution."""
        # Arrange
        ${7:test_input} = ${8:test_value}
        
        # Act
        result = ${5:test_instance}.${6:main_method}(${7:test_input})
        
        # Assert
        assert result is not None
        mock_logger.info.assert_called()
    
    def test_${6:main_method}_error_handling(self, ${5:test_instance}, mock_logger):
        """Test error handling in ${6:main_method}."""
        # Arrange - force an error condition
        ${9:error_condition}
        
        # Act & Assert
        with pytest.raises(${10:ExpectedException}):
            ${5:test_instance}.${6:main_method}(${11:invalid_input})
        
        # Verify error logging
        mock_logger.error.assert_called()
    
    def test_performance_benchmark(self, ${5:test_instance}):
        """Performance benchmark test."""
        import time
        
        start_time = time.time()
        
        # Execute operation multiple times
        for _ in range(100):
            ${5:test_instance}.${6:main_method}(${12:benchmark_input})
        
        elapsed = time.time() - start_time
        
        # Assert performance target
        assert elapsed < ${13:performance_target}, f"Performance target missed: {elapsed}s"
```

### **📊 Snippet: Logger Pattern**
```python
# ===== LOGGER PATTERN =====
# Prefix: log-pattern
self.logger.info(
    "${1:operation_description}",
    component="${2:component_name}",
    ${3:key1}=${4:value1},
    ${5:key2}=${6:value2}
)
```

### **⚙️ Snippet: SIC Configuration**
```python
# ===== SIC CONFIGURATION =====
# Prefix: sic-config
config = self.sic.get_config("${1:config_section}")
${2:variable_name} = config.get("${3:config_key}", ${4:default_value})

self.logger.info(
    "Configuration loaded",
    component="${5:component_name}",
    config_section="${1:config_section}",
    config_keys=list(config.keys())
)
```

---

## 🔧 **CONFIGURACIONES AVANZADAS**

### **📁 .copilotignore Configuration**
```
# ICT Engine v6.0 - Copilot Ignore Configuration

# Cache directories
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
cache/
.cache/

# Data files (large datasets)
data/candles/*.csv
data/backtest_results/*.json
data/exports/*.xlsx

# Logs (too verbose for context)
logs/*.log
logs/performance/*.txt
logs/debug_sessions/*.json

# Temporary files
*.tmp
*.temp
/temp/
debug_screenshots/

# Config files with sensitive data
config/*_private.json
config/api_keys.json

# Compiled extensions
*.so
*.dll
*.dylib

# IDE files
.vscode/settings.json
.idea/

# Documentation builds
docs/_build/
docs/html/

# Backup files
backups/
*.backup
*.bak
```

### **🎯 Copilot Workspace Configuration**
```json
{
    "github.copilot.workspace": {
        "enabled": true,
        "projectContext": {
            "name": "ICT Engine v6.0 Enterprise",
            "description": "Smart Money Concepts trading engine with enterprise architecture",
            "language": "python",
            "framework": "enterprise-custom",
            "patterns": [
                "sic-bridge-integration",
                "sluc-logging",
                "unified-memory-system",
                "poi-analysis",
                "smart-money-concepts"
            ]
        },
        "codebaseContext": {
            "entryPoints": [
                "main.py",
                "core/poi_system.py",
                "sistema/sic_bridge.py"
            ],
            "keyModules": [
                "core/",
                "sistema/",
                "tests/"
            ],
            "excludePaths": [
                "data/",
                "logs/",
                "cache/",
                "__pycache__/"
            ]
        },
        "developmentContext": {
            "codingStandards": "enterprise-python",
            "testingFramework": "pytest",
            "loggingFramework": "sluc-custom",
            "configurationFramework": "sic-custom"
        }
    }
}
```

### **⚡ Copilot Chat Configuration**
```json
{
    "github.copilot.chat.welcomeMessage": "ICT Engine v6.0 Enterprise Assistant Ready! 🏗️\n\nEnterprise protocols active:\n✅ SIC/SLUC integration\n✅ Performance monitoring\n✅ Full documentation\n✅ Comprehensive testing\n\nWhat would you like to build today?",
    
    "github.copilot.chat.customInstructions": [
        {
            "trigger": "@ict-analyze",
            "prompt": "Analyze this code for ICT Engine v6.0 compliance. Check: 1) SIC/SLUC integration, 2) Enterprise patterns, 3) Performance implications, 4) Documentation completeness, 5) Testing coverage."
        },
        {
            "trigger": "@ict-implement", 
            "prompt": "Implement this feature following ICT Engine v6.0 enterprise standards. Include: 1) SIC Bridge configuration, 2) SmartTradingLogger integration, 3) Comprehensive error handling, 4) Full documentation, 5) Unit tests."
        },
        {
            "trigger": "@ict-optimize",
            "prompt": "Optimize this code for performance while maintaining ICT Engine v6.0 enterprise compliance. Focus on: 1) Memory efficiency, 2) Execution speed, 3) SIC cache usage, 4) SLUC logging overhead."
        },
        {
            "trigger": "@ict-test",
            "prompt": "Create comprehensive enterprise test suite. Include: 1) Unit tests with >90% coverage, 2) Integration tests with SIC/SLUC, 3) Performance benchmarks, 4) Error handling validation."
        }
    ]
}
```

---

## 📚 **RECURSOS DE REFERENCIA**

### **🔗 Links Importantes**
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Python Enterprise Patterns](https://python-patterns.guide/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

### **📖 Referencias del Proyecto**
- `docs/02-architecture/`: Documentación arquitectónica
- `docs/04-development-logs/`: Bitácoras de desarrollo
- `protocolo-trabajo-copilot/01-protocolo-principal.md`: Protocolo principal
- `REGLAS_COPILOT.md`: Reglas específicas del proyecto

### **⚡ Comandos de Referencia Rápida**
```bash
# Verificar estado del proyecto
cat protocolo-trabajo-copilot/06-comandos-rapidos.md

# Buscar funcionalidad existente
grep -r "class.*Analyzer" core/ --include="*.py"

# Verificar compliance SIC/SLUC
python -c "from sistema.sic_bridge import SICBridge; from core.smart_trading_logger import SmartTradingLogger; print('✅ Enterprise ready')"

# Ejecutar tests
python -m pytest tests/ -v --tb=short

# Verificar documentación
find docs/ -name "*.md" -exec ls -lt {} + | head -5
```

---

**📋 ESTADO:** ✅ **CONFIGURACIÓN COPILOT COMPLETA**  
**🎯 OBJETIVO:** Maximizar efectividad de Copilot para desarrollo enterprise  
**⚡ USO:** Aplicar configuraciones al inicio del proyecto y usar prompts especializados
