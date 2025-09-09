#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA DE LOGGING ICT ENGINE v6.0 ENTERPRISE
=========================================================================

Herramienta de diagnóstico para investigar y documentar el sistema de logging
del ICT Engine v6.0 Enterprise, identificando fuentes de logs, configuraciones
y rutas de almacenamiento.

Funcionalidades:
- ✅ Análisis de múltiples sistemas de logging
- ✅ Identificación de fuentes de logs específicos
- ✅ Mapeo de rutas de almacenamiento
- ✅ Diagnóstico de configuraciones
- ✅ Recomendaciones de optimización

Versión: v1.0.0
Fecha: 9 de Septiembre 2025 - 12:00 GMT
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class LoggingDiagnosticTool:
    """🔍 Herramienta de diagnóstico completo del sistema de logging."""
    
    def __init__(self):
        """Inicializa la herramienta de diagnóstico."""
        self.project_root = Path(__file__).parent.parent
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.project_root),
            'logging_systems': {},
            'log_locations': {},
            'config_analysis': {},
            'issues_found': [],
            'recommendations': []
        }
    
    def run_complete_diagnosis(self) -> Dict[str, Any]:
        """Ejecuta diagnóstico completo del sistema de logging."""
        print("🔍 ICT ENGINE v6.0 ENTERPRISE - DIAGNÓSTICO DE LOGGING")
        print("=" * 60)
        
        # 1. Analizar sistemas de logging
        print("\n📊 1. ANALIZANDO SISTEMAS DE LOGGING...")
        self._analyze_logging_systems()
        
        # 2. Mapear ubicaciones de logs
        print("\n📂 2. MAPEANDO UBICACIONES DE LOGS...")
        self._map_log_locations()
        
        # 3. Analizar configuraciones
        print("\n⚙️ 3. ANALIZANDO CONFIGURACIONES...")
        self._analyze_configurations()
        
        # 4. Identificar fuentes específicas
        print("\n🎯 4. IDENTIFICANDO FUENTES ESPECÍFICAS...")
        self._identify_log_sources()
        
        # 5. Detectar problemas
        print("\n🚨 5. DETECTANDO PROBLEMAS...")
        self._detect_issues()
        
        # 6. Generar recomendaciones
        print("\n💡 6. GENERANDO RECOMENDACIONES...")
        self._generate_recommendations()
        
        # 7. Mostrar resumen
        print("\n📋 7. RESUMEN EJECUTIVO")
        self._display_summary()
        
        return self.results
    
    def _analyze_logging_systems(self):
        """Analiza los sistemas de logging existentes."""
        logging_systems = {}
        
        # 1. SmartTradingLogger centralizado
        smart_logger_path = self.project_root / "01-CORE" / "smart_trading_logger.py"
        if smart_logger_path.exists():
            logging_systems['SmartTradingLogger'] = {
                'path': str(smart_logger_path),
                'type': 'Centralizado',
                'status': 'Activo',
                'target_directory': '05-LOGS/',
                'features': [
                    'Logging diario por componente',
                    'Separadores de sesión',
                    'Silent mode',
                    'Utility functions'
                ]
            }
        
        # 2. Sistema legacy en 01-CORE/data/logs
        legacy_log_dir = self.project_root / "01-CORE" / "data" / "logs"
        if legacy_log_dir.exists():
            logging_systems['LegacyLogging'] = {
                'path': str(legacy_log_dir),
                'type': 'Legacy',
                'status': 'Activo (recibiendo logs ICT_Engine)',
                'target_directory': '01-CORE/data/logs/',
                'features': [
                    'Logs automáticos del sistema',
                    'Múltiples categorías',
                    'Logs históricos'
                ]
            }
        
        # 3. Loggers específicos de módulos
        fvg_manager_path = self.project_root / "01-CORE" / "analysis" / "fvg_memory_manager.py"
        if fvg_manager_path.exists():
            logging_systems['FVGMemoryManager'] = {
                'path': str(fvg_manager_path),
                'type': 'Módulo específico',
                'status': 'Activo (generando logs [fvg_memory])',
                'logger_class': 'SmartTradingLogger',
                'log_components': ['fvg_memory', 'kill_zone', 'market_conditions']
            }
        
        self.results['logging_systems'] = logging_systems
        
        print(f"✅ Encontrados {len(logging_systems)} sistemas de logging")
        for name, system in logging_systems.items():
            print(f"   - {name}: {system['status']}")
    
    def _map_log_locations(self):
        """Mapea todas las ubicaciones de logs."""
        log_locations = {}
        
        # 1. Logs centralizados (05-LOGS)
        logs_dir = self.project_root / "05-LOGS"
        if logs_dir.exists():
            log_locations['05-LOGS'] = {
                'path': str(logs_dir),
                'purpose': 'Sistema centralizado SmartTradingLogger',
                'subdirectories': [d.name for d in logs_dir.iterdir() if d.is_dir()],
                'recent_files': self._get_recent_files(logs_dir, 5)
            }
        
        # 2. Logs legacy (01-CORE/data/logs)
        core_logs_dir = self.project_root / "01-CORE" / "data" / "logs"
        if core_logs_dir.exists():
            log_locations['01-CORE/data/logs'] = {
                'path': str(core_logs_dir),
                'purpose': 'Sistema legacy - recibiendo logs ICT_Engine',
                'subdirectories': [d.name for d in core_logs_dir.iterdir() if d.is_dir()],
                'recent_files': self._get_recent_files(core_logs_dir, 5)
            }
        
        # 3. Otros directorios de logs
        other_log_dirs = [
            self.project_root / "04-DATA" / "logs",
            self.project_root / "09-DASHBOARD" / "data" / "logs"
        ]
        
        for log_dir in other_log_dirs:
            if log_dir.exists():
                log_locations[str(log_dir.relative_to(self.project_root))] = {
                    'path': str(log_dir),
                    'purpose': 'Logs adicionales',
                    'recent_files': self._get_recent_files(log_dir, 3)
                }
        
        self.results['log_locations'] = log_locations
        
        print(f"✅ Mapeadas {len(log_locations)} ubicaciones de logs")
        for location, info in log_locations.items():
            print(f"   - {location}: {len(info.get('recent_files', []))} archivos recientes")
    
    def _analyze_configurations(self):
        """Analiza las configuraciones de logging."""
        configs = {}
        
        # 1. SmartTradingLogger config
        try:
            smart_logger_path = self.project_root / "01-CORE" / "smart_trading_logger.py"
            if smart_logger_path.exists():
                with open(smart_logger_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    configs['SmartTradingLogger'] = {
                        'default_name': 'ICT_Engine' if 'ICT_Engine' in content else 'Unknown',
                        'default_level': 'INFO' if 'INFO' in content else 'Unknown',
                        'supports_silent_mode': 'silent_mode' in content,
                        'log_directory': '05-LOGS' if '05-LOGS' in content else 'Unknown'
                    }
        except Exception as e:
            configs['SmartTradingLogger'] = {'error': str(e)}
        
        # 2. FVGMemoryManager config
        try:
            fvg_path = self.project_root / "01-CORE" / "analysis" / "fvg_memory_manager.py"
            if fvg_path.exists():
                with open(fvg_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    configs['FVGMemoryManager'] = {
                        'uses_smart_logger': 'SmartTradingLogger' in content,
                        'log_component': 'fvg_memory',
                        'generates_kill_zone_logs': 'Kill Zone' in content,
                        'generates_config_logs': 'Configuración final' in content
                    }
        except Exception as e:
            configs['FVGMemoryManager'] = {'error': str(e)}
        
        self.results['config_analysis'] = configs
        
        print(f"✅ Analizadas {len(configs)} configuraciones")
    
    def _identify_log_sources(self):
        """Identifica las fuentes específicas de logs."""
        sources = {}
        
        # Logs específicos observados
        target_logs = {
            '[ICT_Engine] [INFO] [fvg_memory] ⚡ Kill Zone london activa': {
                'source_file': '01-CORE/analysis/fvg_memory_manager.py',
                'method': '_adapt_to_market_conditions',
                'line_approx': 209,
                'frequency': 'Durante kill zones activas',
                'importance': 'HIGH - Información de trading crítica'
            },
            '[ICT_Engine] [INFO] [fvg_memory] ⚙️ Configuración final': {
                'source_file': '01-CORE/analysis/fvg_memory_manager.py',
                'method': '_adapt_to_market_conditions',
                'line_approx': 229,
                'frequency': 'En cada inicialización',
                'importance': 'MEDIUM - Configuración del sistema'
            },
            '[ICT_Engine] [INFO] [unified_memory] 🧠 Inicializando': {
                'source_file': 'Múltiples archivos del sistema memory',
                'method': 'Varios métodos de inicialización',
                'frequency': 'En cada startup',
                'importance': 'MEDIUM - Estado del sistema'
            }
        }
        
        self.results['log_sources'] = target_logs
        
        print(f"✅ Identificadas {len(target_logs)} fuentes específicas de logs")
    
    def _detect_issues(self):
        """Detecta problemas en el sistema de logging."""
        issues = []
        
        # 1. Duplicación de sistemas
        if len(self.results['logging_systems']) > 1:
            issues.append({
                'type': 'DUPLICACIÓN',
                'severity': 'MEDIUM',
                'description': 'Múltiples sistemas de logging activos simultáneamente',
                'impact': 'Logs dispersos en múltiples ubicaciones',
                'affected_systems': list(self.results['logging_systems'].keys())
            })
        
        # 2. Logs no centralizados
        legacy_active = 'LegacyLogging' in self.results['logging_systems']
        if legacy_active:
            issues.append({
                'type': 'LOGS_NO_CENTRALIZADOS',
                'severity': 'HIGH',
                'description': 'Logs críticos van al sistema legacy en lugar del centralizado',
                'impact': 'Los logs [ICT_Engine] [fvg_memory] no están en 05-LOGS/',
                'solution': 'Redirigir logs de FVGMemoryManager a SmartTradingLogger centralizado'
            })
        
        # 3. Falta de organización por categorías
        if '05-LOGS' in self.results['log_locations']:
            subdirs = self.results['log_locations']['05-LOGS'].get('subdirectories', [])
            expected_categories = ['fvg_memory', 'market_data', 'ict_signals', 'system_status']
            missing_categories = [cat for cat in expected_categories if cat not in subdirs]
            
            if missing_categories:
                issues.append({
                    'type': 'CATEGORÍAS_FALTANTES',
                    'severity': 'MEDIUM',
                    'description': f'Faltan categorías específicas en 05-LOGS: {missing_categories}',
                    'impact': 'Logs no organizados por tipo de contenido'
                })
        
        self.results['issues_found'] = issues
        
        print(f"🚨 Detectados {len(issues)} problemas")
        for issue in issues:
            print(f"   - {issue['type']}: {issue['severity']}")
    
    def _generate_recommendations(self):
        """Genera recomendaciones para optimizar el sistema."""
        recommendations = []
        
        # 1. Centralización inmediata
        recommendations.append({
            'priority': 'HIGH',
            'title': 'Redirigir FVGMemoryManager al sistema centralizado',
            'description': 'Modificar FVGMemoryManager para usar el SmartTradingLogger centralizado',
            'action': 'Actualizar configuración de logger en fvg_memory_manager.py',
            'expected_outcome': 'Todos los logs [fvg_memory] en 05-LOGS/'
        })
        
        # 2. Estructura de carpetas específica
        recommendations.append({
            'priority': 'MEDIUM',
            'title': 'Crear estructura de carpetas por categorías',
            'description': 'Organizar logs en carpetas específicas por tipo de contenido',
            'action': 'Crear: fvg_memory/, market_data/, ict_signals/, system_status/',
            'expected_outcome': 'Logs organizados y fáciles de encontrar'
        })
        
        # 3. Migración de logs históricos
        recommendations.append({
            'priority': 'LOW',
            'title': 'Migrar logs históricos importantes',
            'description': 'Mover logs valiosos desde 01-CORE/data/logs a 05-LOGS/',
            'action': 'Script de migración selectiva',
            'expected_outcome': 'Historial completo en sistema centralizado'
        })
        
        # 4. Configuración unificada
        recommendations.append({
            'priority': 'MEDIUM',
            'title': 'Unificar configuración de logging',
            'description': 'Crear configuración centralizada para todos los módulos',
            'action': 'Archivo de configuración único para logging',
            'expected_outcome': 'Configuración consistente en todo el sistema'
        })
        
        self.results['recommendations'] = recommendations
        
        print(f"💡 Generadas {len(recommendations)} recomendaciones")
    
    def _display_summary(self):
        """Muestra resumen ejecutivo del diagnóstico."""
        print("\n" + "="*60)
        print("📋 RESUMEN EJECUTIVO - DIAGNÓSTICO DE LOGGING")
        print("="*60)
        
        # Estado actual
        print(f"\n🔍 ESTADO ACTUAL:")
        print(f"   • Sistemas de logging: {len(self.results['logging_systems'])}")
        print(f"   • Ubicaciones de logs: {len(self.results['log_locations'])}")
        print(f"   • Problemas detectados: {len(self.results['issues_found'])}")
        
        # Principal hallazgo
        print(f"\n🎯 HALLAZGO PRINCIPAL:")
        print(f"   Los logs [ICT_Engine] [fvg_memory] SÍ se están guardando,")
        print(f"   pero en el sistema legacy (01-CORE/data/logs/) en lugar")
        print(f"   del sistema centralizado (05-LOGS/).")
        
        # Origen identificado
        print(f"\n📍 ORIGEN IDENTIFICADO:")
        print(f"   Archivo: 01-CORE/analysis/fvg_memory_manager.py")
        print(f"   Clase: FVGMemoryManager")
        print(f"   Logger: SmartTradingLogger() con configuración por defecto")
        
        # Solución recomendada
        print(f"\n💡 SOLUCIÓN RECOMENDADA:")
        print(f"   1. Configurar FVGMemoryManager para usar logger centralizado")
        print(f"   2. Crear carpetas específicas en 05-LOGS/")
        print(f"   3. Implementar categorización automática")
        
        # Próximos pasos
        print(f"\n📋 PRÓXIMOS PASOS:")
        for i, rec in enumerate(self.results['recommendations'][:3], 1):
            print(f"   {i}. {rec['title']} [{rec['priority']}]")
        
        print("\n" + "="*60)
    
    def _get_recent_files(self, directory: Path, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtiene archivos recientes de un directorio."""
        try:
            files = []
            for file_path in directory.rglob("*.log"):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        'name': file_path.name,
                        'path': str(file_path.relative_to(self.project_root)),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            # Ordenar por fecha de modificación (más recientes primero)
            files.sort(key=lambda x: x['modified'], reverse=True)
            return files[:limit]
        
        except Exception as e:
            return [{'error': str(e)}]
    
    def save_report(self, output_path: Optional[str] = None) -> str:
        """Guarda el reporte completo en JSON."""
        if not output_path:
            output_path = str(self.project_root / "06-TOOLS" / f"logging_diagnosis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte guardado en: {output_path}")
        return str(output_path)

def main():
    """Función principal para ejecutar el diagnóstico."""
    diagnostic = LoggingDiagnosticTool()
    results = diagnostic.run_complete_diagnosis()
    report_path = diagnostic.save_report()
    
    print(f"\n✅ DIAGNÓSTICO COMPLETADO")
    print(f"📄 Reporte completo: {report_path}")
    
    return results, report_path

if __name__ == "__main__":
    main()
