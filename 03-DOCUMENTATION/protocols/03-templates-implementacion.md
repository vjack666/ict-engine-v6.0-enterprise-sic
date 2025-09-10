# 🏗️ TEMPLATES DE IMPLEMENTACIÓN ENTERPRISE

**Archivo:** `03-templates-implementacion.md`  
**Propósito:** Templates de código enterprise listo para copy-paste

---

## 🎯 **TEMPLATE PRINCIPAL ENTERPRISE v6.0**

### **📋 CABECERA ESTÁNDAR ENTERPRISE**
```python
#!/usr/bin/env python3
"""
[TÍTULO DEL MÓDULO] - ICT ENGINE v6.0 ENTERPRISE
================================================

[DESCRIPCIÓN ESPECÍFICA DEL PROPÓSITO]

✅ ARQUITECTURA ENTERPRISE:
- SIC v3.1: [✅/❌] [Justificación si es ❌]
- SLUC v2.1: [✅/❌] [Uso específico del logging]
- Memoria Trader: [✅/❌] [Tipo de memoria requerida]
- Performance <5s: [✅/❌] [Optimizaciones implementadas]
- MT5 Integration: [✅/❌] [Tipo de datos utilizados]

🎯 FUNCIONALIDAD:
[Descripción específica de qué hace este módulo]

📊 MÉTRICAS:
- Tiempo respuesta objetivo: [X]s
- Memoria máxima: [X]MB
- Precisión objetivo: [X]%

Autor: ICT Engine Enterprise Team
Fecha: [FECHA ACTUAL]
Versión: v6.0.X-enterprise-[estado]
"""

# 📋 IMPORTS ENTERPRISE ESTÁNDAR
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import sys
import os
import time
import logging

# 🏗️ SIC/SLUC ENTERPRISE (OBLIGATORIO si aplica)
try:
    from sistema.sic_bridge import SICBridge
    from core.smart_trading_logger import SmartTradingLogger
    ENTERPRISE_READY = True
except ImportError as e:
    print(f"⚠️ ENTERPRISE COMPONENTS NOT AVAILABLE: {e}")
    ENTERPRISE_READY = False

# 📊 DATA SCIENCE IMPORTS (si aplica)
try:
    import pandas as pd
    import numpy as np
    ANALYTICS_READY = True
except ImportError:
    ANALYTICS_READY = False

# 🧠 MEMORIA IMPORTS (si aplica)
try:
    from core.data_management.unified_memory_system import UnifiedMemorySystem
    MEMORY_READY = True
except ImportError:
    MEMORY_READY = False

# [RESTO DE IMPORTS ESPECÍFICOS DEL MÓDULO]
```

---

## 🏛️ **TEMPLATE CLASE ENTERPRISE PRINCIPAL**

```python
@dataclass
class [NombreClase]Config:
    """Configuración enterprise para [NombreClase]"""
    # Performance settings
    max_execution_time: float = 5.0  # segundos
    memory_limit_mb: int = 100
    enable_caching: bool = True
    
    # Logging settings
    log_level: str = "INFO"
    enable_performance_logging: bool = True
    enable_memory_logging: bool = True
    
    # Integration settings
    use_sic_bridge: bool = True
    use_memory_system: bool = True
    enable_fallback: bool = True

class [NombreClase]:
    """
    [DOCUMENTACIÓN ESPECÍFICA DE LA CLASE]
    
    ✅ ENTERPRISE FEATURES:
    - [Lista específica de características enterprise]
    - [Integración SIC/SLUC con detalles]
    - [Performance optimizations implementadas]
    - [Memory management strategy]
    
    📊 USAGE:
    ```python
    analyzer = [NombreClase](config=[NombreClase]Config())
    result = analyzer.metodo_principal(datos)
    ```
    """
    
    def __init__(self, config: Optional[[NombreClase]Config] = None):
        """
        Inicialización enterprise con configuración robusta
        
        Args:
            config: Configuración enterprise opcional
        """
        # ✅ CONFIGURACIÓN
        self.config = config or [NombreClase]Config()
        
        # ✅ OBLIGATORIO: Logger SLUC enterprise
        self.logger = SmartTradingLogger() if ENTERPRISE_READY else logging.getLogger(__name__)
        
        # ✅ OBLIGATORIO: SIC Bridge si disponible y configurado
        self.sic = None
        if ENTERPRISE_READY and self.config.use_sic_bridge:
            try:
                self.sic = SICBridge()
                self.logger.info("🏗️ SIC Bridge inicializado exitosamente", 
                               component="[COMPONENTE]")
            except Exception as e:
                self.logger.warning(f"⚠️ SIC Bridge no disponible: {e}", 
                                  component="[COMPONENTE]")
        
        # 🧠 MEMORIA SYSTEM (si aplica)
        self.memory = None
        if MEMORY_READY and self.config.use_memory_system:
            try:
                self.memory = UnifiedMemorySystem()
                self.logger.info("🧠 Sistema de memoria inicializado", 
                               component="[COMPONENTE]")
            except Exception as e:
                self.logger.warning(f"⚠️ Sistema de memoria no disponible: {e}",
                                  component="[COMPONENTE]")
        
        # 📊 MÉTRICAS PERFORMANCE
        self.metrics = {
            'total_executions': 0,
            'successful_executions': 0,
            'average_execution_time': 0.0,
            'peak_memory_usage': 0,
            'error_count': 0
        }
        
        # ⚡ CACHE (si habilitado)
        self.cache = {} if self.config.enable_caching else None
        
        # 🚀 LOG INICIALIZACIÓN COMPLETA
        self.logger.info(f"✅ {self.__class__.__name__} inicializado correctamente",
                        component="[COMPONENTE]",
                        extra={
                            'enterprise_ready': ENTERPRISE_READY,
                            'memory_ready': MEMORY_READY,
                            'config': self.config.__dict__
                        })
    
    def metodo_principal(self, datos: Any, **kwargs) -> Dict[str, Any]:
        """
        Método principal enterprise con logging y métricas completas
        
        Args:
            datos: [Descripción específica del tipo de datos]
            **kwargs: Parámetros adicionales
            
        Returns:
            Dict con resultado estructurado enterprise
            
        Raises:
            ValueError: Si datos no son válidos
            RuntimeError: Si excede tiempo límite o memoria
        """
        # ⏱️ INICIO TIMING PERFORMANCE
        start_time = time.time()
        self.metrics['total_executions'] += 1
        
        # ✅ OBLIGATORIO: Log inicio con contexto completo
        self.logger.info("🚀 Iniciando [operación específica]", 
                        component="[COMPONENTE]",
                        extra={
                            'input_type': type(datos).__name__,
                            'input_size': len(datos) if hasattr(datos, '__len__') else 'N/A',
                            'kwargs': kwargs,
                            'execution_id': self.metrics['total_executions']
                        })
        
        try:
            # 🔍 VALIDACIÓN DE ENTRADA
            self._validar_entrada(datos)
            
            # 💾 CHECK CACHE (si habilitado)
            cache_key = self._generar_cache_key(datos, kwargs)
            if self.cache and cache_key in self.cache:
                self.logger.debug("📦 Resultado obtenido desde cache",
                                component="[COMPONENTE]",
                                extra={'cache_key': cache_key})
                return self.cache[cache_key]
            
            # 🧠 MEMORIA CONTEXT (si disponible)
            memory_context = None
            if self.memory:
                memory_context = self.memory.get_context('[CONTEXTO_ESPECÍFICO]')
            
            # 🏗️ LÓGICA PRINCIPAL
            resultado = self._procesar_logica_principal(datos, memory_context, **kwargs)
            
            # 💾 GUARDAR EN CACHE (si habilitado)
            if self.cache and cache_key:
                self.cache[cache_key] = resultado
            
            # 🧠 ACTUALIZAR MEMORIA (si disponible)
            if self.memory and resultado.get('success', False):
                self.memory.store_pattern('[PATTERN_TYPE]', resultado)
            
            # ⏱️ CALCULAR MÉTRICAS
            execution_time = time.time() - start_time
            self.metrics['successful_executions'] += 1
            self._actualizar_metricas_performance(execution_time)
            
            # ⚠️ VERIFICAR PERFORMANCE LÍMITE
            if execution_time > self.config.max_execution_time:
                self.logger.warning(f"⚠️ Performance limit exceeded: {execution_time:.3f}s > {self.config.max_execution_time}s",
                                  component="[COMPONENTE]")
            
            # ✅ OBLIGATORIO: Log éxito con métricas detalladas
            self.logger.info("✅ [Operación específica] completada exitosamente",
                           component="[COMPONENTE]",
                           extra={
                               'execution_time': execution_time,
                               'result_summary': self._crear_resumen_resultado(resultado),
                               'performance_within_limits': execution_time <= self.config.max_execution_time,
                               'cache_used': cache_key in self.cache if self.cache else False,
                               'memory_updated': memory_context is not None
                           })
            
            return resultado
            
        except Exception as e:
            # ⏱️ TIEMPO DE ERROR
            execution_time = time.time() - start_time
            self.metrics['error_count'] += 1
            
            # ✅ OBLIGATORIO: Log error con contexto completo
            self.logger.error(f"❌ Error en [operación específica]: {str(e)}",
                             component="[COMPONENTE]",
                             extra={
                                 'error_type': type(e).__name__,
                                 'error_details': str(e),
                                 'execution_time_before_error': execution_time,
                                 'input_data_summary': self._crear_resumen_entrada(datos),
                                 'kwargs': kwargs,
                                 'stack_trace': True  # Para logging detallado
                             })
            
            # 🔄 FALLBACK (si configurado)
            if self.config.enable_fallback:
                return self._ejecutar_fallback(datos, e)
            
            raise
    
    def _validar_entrada(self, datos: Any) -> None:
        """Validación robusta de datos de entrada"""
        if datos is None:
            raise ValueError("Datos de entrada no pueden ser None")
        
        # [VALIDACIONES ESPECÍFICAS DEL MÓDULO]
        
    def _procesar_logica_principal(self, datos: Any, memory_context: Optional[Dict], **kwargs) -> Dict[str, Any]:
        """
        Lógica principal del procesamiento
        
        [IMPLEMENTACIÓN ESPECÍFICA AQUÍ]
        """
        # PLACEHOLDER - IMPLEMENTAR LÓGICA ESPECÍFICA
        resultado = {
            'success': True,
            'data': datos,  # PLACEHOLDER
            'timestamp': datetime.now().isoformat(),
            'execution_context': {
                'memory_available': memory_context is not None,
                'kwargs': kwargs
            }
        }
        
        return resultado
    
    def _generar_cache_key(self, datos: Any, kwargs: Dict) -> Optional[str]:
        """Genera clave de cache única para los datos"""
        if not self.config.enable_caching:
            return None
        
        # IMPLEMENTAR LÓGICA DE CACHE KEY ESPECÍFICA
        return f"[MODULO]_{hash(str(datos))}_{hash(str(sorted(kwargs.items())))}"
    
    def _crear_resumen_resultado(self, resultado: Dict) -> Dict:
        """Crea resumen del resultado para logging"""
        return {
            'success': resultado.get('success', False),
            'data_size': len(resultado.get('data', [])) if hasattr(resultado.get('data'), '__len__') else 'N/A',
            'timestamp': resultado.get('timestamp')
        }
    
    def _crear_resumen_entrada(self, datos: Any) -> Dict:
        """Crea resumen de datos de entrada para logging"""
        return {
            'type': type(datos).__name__,
            'size': len(datos) if hasattr(datos, '__len__') else 'N/A',
            'sample': str(datos)[:100] if hasattr(datos, '__str__') else 'N/A'
        }
    
    def _actualizar_metricas_performance(self, execution_time: float) -> None:
        """Actualiza métricas de performance"""
        # Media móvil simple de tiempo de ejecución
        if self.metrics['successful_executions'] == 1:
            self.metrics['average_execution_time'] = execution_time
        else:
            total_time = self.metrics['average_execution_time'] * (self.metrics['successful_executions'] - 1)
            self.metrics['average_execution_time'] = (total_time + execution_time) / self.metrics['successful_executions']
    
    def _ejecutar_fallback(self, datos: Any, error: Exception) -> Dict[str, Any]:
        """Ejecuta lógica de fallback en caso de error"""
        self.logger.info("🔄 Ejecutando fallback por error", 
                        component="[COMPONENTE]",
                        extra={'original_error': str(error)})
        
        return {
            'success': False,
            'fallback': True,
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de performance del componente"""
        return {
            **self.metrics,
            'success_rate': (self.metrics['successful_executions'] / self.metrics['total_executions'] * 100) 
                           if self.metrics['total_executions'] > 0 else 0,
            'component': "[COMPONENTE]",
            'enterprise_ready': ENTERPRISE_READY,
            'memory_ready': MEMORY_READY
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica salud del componente"""
        health = {
            'status': 'healthy',
            'checks': {
                'sic_bridge': self.sic is not None,
                'memory_system': self.memory is not None,
                'logger': self.logger is not None,
                'cache': self.cache is not None if self.config.enable_caching else True
            },
            'metrics': self.get_metrics(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Determinar estado general
        if not all(health['checks'].values()):
            health['status'] = 'degraded'
        
        if self.metrics['error_count'] > 0 and self.metrics['total_executions'] > 0:
            error_rate = self.metrics['error_count'] / self.metrics['total_executions']
            if error_rate > 0.1:  # >10% error rate
                health['status'] = 'unhealthy'
        
        return health
```

---

## ⚡ **TEMPLATE FUNCIÓN SIMPLE ENTERPRISE**

```python
def funcion_enterprise(parametros: TipoParametros, 
                      logger: Optional[SmartTradingLogger] = None) -> Dict[str, Any]:
    """
    Función enterprise con logging y error handling robusto
    
    Args:
        parametros: [Descripción específica]
        logger: Logger opcional (se crea uno si no se proporciona)
    
    Returns:
        Dict con resultado estructurado
    """
    # Setup logger
    if logger is None:
        logger = SmartTradingLogger() if ENTERPRISE_READY else logging.getLogger(__name__)
    
    start_time = time.time()
    
    # Log inicio
    logger.info("🚀 Iniciando [función específica]",
                component="[COMPONENTE]", 
                extra={'params': parametros})
    
    try:
        # Validación
        if not parametros:
            raise ValueError("Parámetros requeridos")
        
        # Lógica principal
        resultado = {
            'success': True,
            'data': parametros,  # PLACEHOLDER
            'execution_time': 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        # Calcular tiempo
        execution_time = time.time() - start_time
        resultado['execution_time'] = execution_time
        
        # Log éxito
        logger.info("✅ [Función específica] completada",
                   component="[COMPONENTE]",
                   extra={'execution_time': execution_time,
                          'result_summary': resultado})
        
        return resultado
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        # Log error
        logger.error(f"❌ Error en [función específica]: {e}",
                    component="[COMPONENTE]",
                    extra={'error_type': type(e).__name__,
                           'execution_time': execution_time,
                           'params': parametros})
        
        # Retornar error estructurado
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__,
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        }
```

---

## 🎯 **CHECKLIST DE IMPLEMENTACIÓN**

### **✅ Antes de usar templates:**
```markdown
📋 VERIFICACIÓN OBLIGATORIA:
├── ✅ Reemplazar [TODOS_LOS_PLACEHOLDERS] con valores específicos
├── ✅ Adaptar imports según necesidades del módulo
├── ✅ Definir validaciones específicas en _validar_entrada()
├── ✅ Implementar lógica real en _procesar_logica_principal()
├── ✅ Configurar logging component name consistente
├── ✅ Ajustar performance limits según requisitos
├── ✅ Definir cache strategy si aplica
└── ✅ Implementar health checks específicos
```

### **🏗️ Customización por tipo de módulo:**
- **Detector/Analyzer:** Agregar precision/recall metrics
- **Data Manager:** Agregar data validation y cleanup
- **Trading Component:** Agregar risk management y position sizing
- **Memory Component:** Agregar compression y TTL management
- **Integration Component:** Agregar connection pooling y retry logic

---

**📋 ESTADO:** ✅ **TEMPLATES ENTERPRISE LISTOS PARA USO**  
**🎯 OBJETIVO:** Copy-paste con customización mínima para calidad enterprise  
**⚡ USO:** Copiar template completo y adaptar placeholders a necesidades específicas
