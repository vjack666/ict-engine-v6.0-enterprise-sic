"""
📊 VALIDATION REPORTS - ICT ENGINE v6.0 ENTERPRISE
=================================================

Módulo de generación de reportes avanzados para
validación entre dashboard live y backtesting histórico.

Funcionalidades:
- ValidationReportEngine: Motor principal de reportes
- Exportación HTML, JSON, CSV
- Métricas avanzadas y análisis comparativo
- Recomendaciones automatizadas
- Archivado y gestión de reportes
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

# Import del motor principal
from .validation_report_engine import ValidationReportEngine, get_validation_report_engine

# Versión del módulo
__version__ = "1.0.0"

# Configuración por defecto para reportes
DEFAULT_REPORT_CONFIG = {
    'output_formats': ['html', 'json', 'csv'],
    'include_visualizations': True,
    'include_raw_data': True,
    'accuracy_precision': 3,
    'report_template': 'detailed',
    'auto_archive': True,
    'max_reports_archive': 50,
    'company_name': 'ICT Engine v6.0 Enterprise',
    'report_branding': True
}

# Templates de reportes disponibles
REPORT_TEMPLATES = {
    'detailed': 'Reporte completo con todas las métricas y análisis',
    'summary': 'Reporte resumido con métricas principales',
    'executive': 'Reporte ejecutivo para toma de decisiones'
}

# Formatos de exportación soportados
SUPPORTED_FORMATS = ['html', 'json', 'csv', 'pdf']  # PDF para implementación futura


def generate_validation_report(validation_results: Dict[str, Any], 
                             report_name: Optional[str] = None,
                             config: Optional[Dict] = None) -> Dict[str, Any]:
    """
    🚀 Función de conveniencia para generar reportes de validación
    
    Args:
        validation_results: Resultados completos de validación
        report_name: Nombre personalizado del reporte
        config: Configuración opcional del reporte
    
    Returns:
        Información del reporte generado
    """
    # Obtener instancia del motor de reportes
    engine = get_validation_report_engine(config)
    
    # Generar reporte
    return engine.generate_complete_report(validation_results, report_name)


def create_custom_report_config(output_formats: Optional[List[str]] = None,
                               company_name: Optional[str] = None,
                               include_raw_data: bool = True,
                               auto_archive: bool = True) -> Dict[str, Any]:
    """
    🔧 Crear configuración personalizada de reportes
    
    Args:
        output_formats: Formatos de salida deseados
        company_name: Nombre de la empresa para branding
        include_raw_data: Incluir datos brutos en el reporte
        auto_archive: Auto-archivar reportes antiguos
    
    Returns:
        Configuración personalizada
    """
    config = DEFAULT_REPORT_CONFIG.copy()
    
    if output_formats:
        # Validar formatos
        valid_formats = [f for f in output_formats if f in SUPPORTED_FORMATS]
        config['output_formats'] = valid_formats
    
    if company_name:
        config['company_name'] = company_name
    
    config['include_raw_data'] = include_raw_data
    config['auto_archive'] = auto_archive
    
    return config


def get_report_status() -> Dict[str, Any]:
    """
    📈 Obtener estado del sistema de reportes
    
    Returns:
        Estado actual del sistema de reportes
    """
    try:
        engine = get_validation_report_engine()
        return engine.get_engine_status()
    except Exception as e:
        return {
            'error': str(e),
            'module_info': {
                'version': __version__,
                'supported_formats': SUPPORTED_FORMATS,
                'available_templates': list(REPORT_TEMPLATES.keys()),
                'last_update': datetime.now()
            }
        }


def list_available_templates() -> Dict[str, str]:
    """
    📋 Listar templates de reportes disponibles
    
    Returns:
        Dict con templates y sus descripciones
    """
    return REPORT_TEMPLATES.copy()


def validate_report_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    ✅ Validar configuración de reporte
    
    Args:
        config: Configuración a validar
    
    Returns:
        Resultado de validación con errores/warnings
    """
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'corrected_config': config.copy()
    }
    
    try:
        # Validar formatos de salida
        if 'output_formats' in config:
            invalid_formats = [f for f in config['output_formats'] if f not in SUPPORTED_FORMATS]
            if invalid_formats:
                validation_result['errors'].append(f"Formatos no soportados: {invalid_formats}")
                validation_result['valid'] = False
                
                # Corregir configuración
                valid_formats = [f for f in config['output_formats'] if f in SUPPORTED_FORMATS]
                validation_result['corrected_config']['output_formats'] = valid_formats
        
        # Validar precision
        if 'accuracy_precision' in config:
            precision = config['accuracy_precision']
            if not isinstance(precision, int) or precision < 1 or precision > 6:
                validation_result['warnings'].append("accuracy_precision debe ser entero entre 1-6, usando 3")
                validation_result['corrected_config']['accuracy_precision'] = 3
        
        # Validar template
        if 'report_template' in config:
            template = config['report_template']
            if template not in REPORT_TEMPLATES:
                validation_result['warnings'].append(f"Template '{template}' no reconocido, usando 'detailed'")
                validation_result['corrected_config']['report_template'] = 'detailed'
        
        # Validar max_reports_archive
        if 'max_reports_archive' in config:
            max_reports = config['max_reports_archive']
            if not isinstance(max_reports, int) or max_reports < 1:
                validation_result['warnings'].append("max_reports_archive debe ser entero positivo, usando 50")
                validation_result['corrected_config']['max_reports_archive'] = 50
        
    except Exception as e:
        validation_result['valid'] = False
        validation_result['errors'].append(f"Error validando configuración: {e}")
    
    return validation_result


def create_report_summary(report_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    📄 Crear resumen de reporte generado
    
    Args:
        report_info: Información del reporte generado
    
    Returns:
        Resumen del reporte
    """
    try:
        summary = {
            'report_name': report_info.get('report_info', {}).get('name', 'Unknown'),
            'generated_at': report_info.get('report_info', {}).get('generated_at', datetime.now()),
            'formats_generated': report_info.get('generation_info', {}).get('formats_generated', []),
            'output_files': report_info.get('generation_info', {}).get('output_files', {}),
            'duration': report_info.get('generation_info', {}).get('duration', 0.0),
            'overall_status': report_info.get('validation_summary', {}).get('overall_status', 'UNKNOWN'),
            'overall_accuracy': report_info.get('validation_summary', {}).get('overall_accuracy', 0.0),
            'recommendations_count': len(report_info.get('recommendations', {}).get('priority_ranking', [])),
            'success': not report_info.get('error')
        }
        
        return summary
        
    except Exception as e:
        return {
            'error': str(e),
            'report_name': 'Unknown',
            'success': False
        }


def archive_reports(max_age_days: int = 30, max_count: int = 50) -> Dict[str, Any]:
    """
    📦 Archivar reportes antiguos
    
    Args:
        max_age_days: Días máximos antes de archivar
        max_count: Número máximo de reportes antes de archivar
    
    Returns:
        Resultado del archivado
    """
    try:
        engine = get_validation_report_engine()
        
        # Implementación simplificada
        # En una versión completa, se revisarían fechas y se moverían archivos
        
        return {
            'archived_reports': 0,
            'remaining_reports': 0,
            'archive_location': str(engine.report_state['output_directory'] / "archive"),
            'success': True
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'success': False
        }


def get_module_info() -> Dict[str, Any]:
    """
    ℹ️ Obtener información del módulo de reportes
    
    Returns:
        Información completa del módulo
    """
    return {
        'module_name': 'validation_reports',
        'version': __version__,
        'description': 'Módulo de generación de reportes avanzados para validación ICT',
        'supported_formats': SUPPORTED_FORMATS,
        'available_templates': REPORT_TEMPLATES,
        'default_config': DEFAULT_REPORT_CONFIG,
        'main_components': [
            'ValidationReportEngine',
            'HTML Export',
            'JSON Export', 
            'CSV Export',
            'Advanced Metrics',
            'Comparative Analysis',
            'Automated Recommendations'
        ],
        'last_update': datetime.now()
    }


# Exportar funciones principales
__all__ = [
    # Motor principal
    'ValidationReportEngine',
    'get_validation_report_engine',
    
    # Funciones de conveniencia
    'generate_validation_report',
    'create_custom_report_config',
    'get_report_status',
    
    # Utilidades
    'list_available_templates',
    'validate_report_config',
    'create_report_summary',
    'archive_reports',
    'get_module_info',
    
    # Configuración
    'DEFAULT_REPORT_CONFIG',
    'REPORT_TEMPLATES',
    'SUPPORTED_FORMATS',
    
    # Meta
    '__version__'
]


if __name__ == "__main__":
    # Test básico del módulo
    print(f"🚀 Testing Validation Reports v{__version__}...")
    
    try:
        # Test info del módulo
        info = get_module_info()
        print(f"✅ Módulo: {info['module_name']} v{info['version']}")
        
        # Test estado de reportes
        status = get_report_status()
        print(f"📊 Estado del sistema de reportes obtenido")
        
        # Test configuración personalizada
        custom_config = create_custom_report_config(
            output_formats=['html', 'json'],
            company_name='Test Company',
            auto_archive=True
        )
        print(f"🔧 Configuración personalizada creada con {len(custom_config['output_formats'])} formatos")
        
        # Test validación de configuración
        validation = validate_report_config(custom_config)
        print(f"✅ Configuración válida: {validation['valid']}")
        
        # Test templates disponibles
        templates = list_available_templates()
        print(f"📋 Templates disponibles: {len(templates)}")
        
    except Exception as e:
        print(f"❌ Error en testing: {e}")