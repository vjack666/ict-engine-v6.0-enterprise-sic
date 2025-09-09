#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 INVESTIGADOR DE PROBLEMAS DE LOGS - ICT ENGINE v6.0 ENTERPRISE
================================================================

Análisis específico de problemas identificados en el sistema de logging:
1. Logs duplicados masivos en APPLICATION (4445 líneas)
2. ERRORs y CRITICALs que necesitan resolución
3. Timestamps inconsistentes entre componentes
4. Categorización incorrecta de logs

Autor: ICT Engine v6.0 Team
Fecha: 2025-09-09
"""

import re
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

# Agregar ruta padre al path para importar módulos centrales
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Agregar específicamente el directorio 01-CORE
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "01-CORE"))

try:
    from smart_trading_logger import SmartTradingLogger, list_daily_log_files
except ImportError:
    print("⚠️ No se pudo importar smart_trading_logger. Ejecutando en modo standalone.")
    list_daily_log_files = None

class LogProblemInvestigator:
    """🔍 Investigador de problemas específicos en logs"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.logs_dir = self.project_root / "05-LOGS"
        self.today = datetime.now().strftime('%Y-%m-%d')
        
        # Inicializar sistema de log central si está disponible
        self.logger = None
        self.use_central_logging = False
        
        if list_daily_log_files is not None:
            try:
                self.logger = SmartTradingLogger("LOG_INVESTIGATOR")
                self.use_central_logging = True
                self.logger.info("🔍 Log Problem Investigator iniciado - usando sistema central")
            except Exception as e:
                print(f"⚠️ Error inicializando sistema central de logs: {e}")
                self.use_central_logging = False
        else:
            print("📋 Log Problem Investigator ejecutándose en modo standalone")
        
    def investigate_application_volume(self):
        """📊 Investigar por qué APPLICATION tiene 4445 logs"""
        if self.use_central_logging and self.logger:
            self.logger.info("🔍 Iniciando investigación de volumen en APPLICATION")
        
        print("🔍 INVESTIGANDO VOLUMEN EXCESIVO EN APPLICATION")
        print("=" * 60)
        
        # Usar sistema central si está disponible
        if self.use_central_logging and list_daily_log_files is not None:
            try:
                files_info = list_daily_log_files()
                if files_info.get('status') == 'success':
                    app_files = [f for f in files_info.get('files', []) if f.get('component') == 'APPLICATION']
                    if app_files:
                        app_file_info = app_files[0]  # Tomar el primer archivo APPLICATION
                        total_lines = app_file_info.get('total_lines', 0)
                        
                        if self.logger:
                            self.logger.info(f"📊 APPLICATION: {total_lines} líneas detectadas via sistema central")
                        
                        print(f"📝 Total líneas en APPLICATION (sistema central): {total_lines}")
                        
                        if total_lines == 0:
                            # Fallback al método manual
                            if self.logger:
                                self.logger.warning("📊 Sistema central no retornó líneas, usando método manual")
                            return self._investigate_application_manual()
                        
                        # Continuar con análisis usando información del sistema central
                        return self._analyze_volume_data(total_lines, app_file_info)
                    else:
                        if self.logger:
                            self.logger.warning("📊 No se encontró archivo APPLICATION en sistema central")
                        return self._investigate_application_manual()
                else:
                    if self.logger:
                        self.logger.error(f"📊 Error en sistema central: {files_info.get('message', 'Unknown')}")
                    return self._investigate_application_manual()
            except Exception as e:
                if self.logger:
                    self.logger.error(f"📊 Excepción usando sistema central: {e}")
                return self._investigate_application_manual()
        else:
            return self._investigate_application_manual()
    
    def _investigate_application_manual(self):
        """📊 Método manual de investigación (fallback)"""
        if self.logger:
            self.logger.info("📊 Usando método manual de investigación de APPLICATION")
        
        app_log = self.logs_dir / "application" / f"ict_engine_{self.today}.log"
        
        if not app_log.exists():
            error_msg = "❌ Archivo APPLICATION no encontrado"
            print(error_msg)
            if self.logger:
                self.logger.error(error_msg)
            return None
        
        with open(app_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📝 Total líneas en APPLICATION: {len(lines)}")
        
        return self._analyze_volume_data(len(lines), None, lines)
    
    def _analyze_volume_data(self, total_lines, file_info=None, lines=None):
        """📊 Analizar datos de volumen (método común)"""
        if self.logger:
            self.logger.info(f"📊 Analizando volumen: {total_lines} líneas")
        
        # Si no tenemos las líneas, intentar leerlas del archivo
        if lines is None and file_info is not None:
            # Intentar obtener líneas del sistema central o del archivo
            app_log = self.logs_dir / "application" / f"ict_engine_{self.today}.log"
            if app_log.exists():
                with open(app_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            else:
                if self.logger:
                    self.logger.warning("📊 No se pudo leer archivo para análisis detallado")
                return {
                    'total_lines': total_lines,
                    'unique_messages': 0,
                    'massive_duplicates': 0,
                    'max_per_second': 0,
                    'top_duplicates': {}
                }
        
        if lines is None:
            if self.logger:
                self.logger.warning("📊 No hay líneas disponibles para análisis")
            return {
                'total_lines': total_lines,
                'unique_messages': 0,
                'massive_duplicates': 0,
                'max_per_second': 0,
                'top_duplicates': {}
            }
        
        # Analizar patrones de duplicación
        timestamps = []
        messages = []
        duplicates = defaultdict(int)
        
        for line in lines:
            if not line.strip():
                continue
                
            # Extraer timestamp
            timestamp_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
            if timestamp_match:
                timestamps.append(timestamp_match.group(1))
            
            # Extraer mensaje principal (sin timestamp)
            message_clean = re.sub(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]', '', line).strip()
            if message_clean:
                messages.append(message_clean)
                duplicates[message_clean] += 1
        
        # Identificar duplicados masivos
        massive_duplicates = {msg: count for msg, count in duplicates.items() if count > 10}
        
        print(f"\n🔢 ANÁLISIS DE DUPLICACIÓN:")
        print(f"   Mensajes únicos: {len(duplicates)}")
        print(f"   Mensajes con >10 repeticiones: {len(massive_duplicates)}")
        
        if massive_duplicates:
            print(f"\n🚨 TOP 5 MENSAJES MÁS DUPLICADOS:")
            for msg, count in sorted(massive_duplicates.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   {count}x: {msg[:80]}...")
        
        # Análisis temporal
        timestamp_counts = Counter(timestamps)
        max_per_second = max(timestamp_counts.values()) if timestamp_counts else 0
        
        print(f"\n⏰ ANÁLISIS TEMPORAL:")
        print(f"   Rango temporal: {min(timestamps) if timestamps else 'N/A'} - {max(timestamps) if timestamps else 'N/A'}")
        print(f"   Máximo logs por segundo: {max_per_second}")
        
        if max_per_second > 50:
            print(f"   🚨 PROBLEMA: {max_per_second} logs por segundo es excesivo")
            if self.logger:
                self.logger.warning(f"🚨 Volumen excesivo detectado: {max_per_second} logs/segundo")
        
        analysis_result = {
            'total_lines': total_lines,
            'unique_messages': len(duplicates),
            'massive_duplicates': len(massive_duplicates),
            'max_per_second': max_per_second,
            'top_duplicates': dict(sorted(massive_duplicates.items(), key=lambda x: x[1], reverse=True)[:5])
        }
        
        if self.logger:
            self.logger.info(f"📊 Análisis completado: {len(duplicates)} mensajes únicos, {len(massive_duplicates)} con duplicación masiva")
        
        return analysis_result
    
    def investigate_errors(self):
        """🚨 Investigar ERRORs y CRITICALs específicos"""
        if self.logger:
            self.logger.info("🚨 Iniciando investigación de errores y críticos")
        
        print("\n🚨 INVESTIGANDO ERRORES Y CRÍTICOS")
        print("=" * 60)
        
        error_summary = {
            'total_errors': 0,
            'total_criticals': 0,
            'by_component': defaultdict(list),
            'error_patterns': defaultdict(int)
        }
        
        # Analizar todos los archivos de log
        for category_dir in self.logs_dir.iterdir():
            if not category_dir.is_dir():
                continue
                
            for log_file in category_dir.glob(f"*{self.today}.log"):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    for i, line in enumerate(lines):
                        if 'ERROR' in line or 'CRITICAL' in line:
                            level = 'ERROR' if 'ERROR' in line else 'CRITICAL'
                            
                            # Extraer componente
                            component_match = re.search(r'\[([^\]]+)\].*\[' + level + r'\]', line)
                            component = component_match.group(1) if component_match else 'UNKNOWN'
                            
                            # Extraer mensaje de error
                            error_msg = line.strip()
                            
                            error_info = {
                                'level': level,
                                'component': component,
                                'file': log_file.name,
                                'line_number': i + 1,
                                'message': error_msg,
                                'context': self._get_context(lines, i)
                            }
                            
                            error_summary['by_component'][component].append(error_info)
                            
                            if level == 'ERROR':
                                error_summary['total_errors'] += 1
                            else:
                                error_summary['total_criticals'] += 1
                            
                            # Categorizar tipo de error
                            if 'Prueba de' in error_msg:
                                error_summary['error_patterns']['TEST_ERRORS'] += 1
                            elif 'RISK_VIOLATION' in error_msg:
                                error_summary['error_patterns']['RISK_VIOLATIONS'] += 1
                            elif 'EMERGENCY' in error_msg:
                                error_summary['error_patterns']['EMERGENCY_ACTIONS'] += 1
                            else:
                                error_summary['error_patterns']['OTHER'] += 1
                
                except Exception as e:
                    print(f"   ⚠️ Error leyendo {log_file}: {e}")
        
        print(f"📊 RESUMEN DE ERRORES:")
        print(f"   Total ERRORs: {error_summary['total_errors']}")
        print(f"   Total CRITICALs: {error_summary['total_criticals']}")
        
        print(f"\n🏷️ TIPOS DE ERRORES:")
        for pattern, count in error_summary['error_patterns'].items():
            print(f"   {pattern}: {count}")
        
        print(f"\n🔧 POR COMPONENTE:")
        for component, errors in error_summary['by_component'].items():
            print(f"   {component}: {len(errors)} error(s)")
            for error in errors[:2]:  # Mostrar primeros 2
                print(f"      - {error['level']}: {error['message'][:80]}...")
        
        return error_summary
    
    def investigate_timestamp_issues(self):
        """⏰ Investigar inconsistencias de timestamps"""
        print("\n⏰ INVESTIGANDO INCONSISTENCIAS DE TIMESTAMPS")
        print("=" * 60)
        
        timestamp_analysis = {
            'by_file': {},
            'format_inconsistencies': [],
            'temporal_gaps': []
        }
        
        for category_dir in self.logs_dir.iterdir():
            if not category_dir.is_dir():
                continue
                
            for log_file in category_dir.glob(f"*{self.today}.log"):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    timestamps = []
                    formats = set()
                    
                    for line in lines:
                        # Buscar diferentes formatos de timestamp
                        timestamp_matches = [
                            re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line),  # [2025-09-09 16:38:22]
                            re.search(r'\[(\d{2}:\d{2}:\d{2})\]', line),  # [16:38:22]
                        ]
                        
                        for match in timestamp_matches:
                            if match:
                                timestamp = match.group(1)
                                timestamps.append(timestamp)
                                formats.add(len(timestamp))  # Longitud como indicador de formato
                                break
                    
                    if timestamps:
                        timestamp_analysis['by_file'][log_file.name] = {
                            'count': len(timestamps),
                            'first': timestamps[0],
                            'last': timestamps[-1],
                            'formats': list(formats)
                        }
                        
                        # Detectar inconsistencias de formato
                        if len(formats) > 1:
                            timestamp_analysis['format_inconsistencies'].append({
                                'file': log_file.name,
                                'formats': list(formats)
                            })
                
                except Exception as e:
                    print(f"   ⚠️ Error analizando timestamps en {log_file}: {e}")
        
        print(f"📊 ANÁLISIS DE TIMESTAMPS:")
        for filename, data in timestamp_analysis['by_file'].items():
            print(f"   {filename}:")
            print(f"      Rango: {data['first']} - {data['last']}")
            print(f"      Formatos: {data['formats']}")
        
        if timestamp_analysis['format_inconsistencies']:
            print(f"\n🚨 INCONSISTENCIAS DE FORMATO:")
            for issue in timestamp_analysis['format_inconsistencies']:
                print(f"   {issue['file']}: Múltiples formatos {issue['formats']}")
        
        return timestamp_analysis
    
    def investigate_categorization_issues(self):
        """📁 Investigar problemas de categorización"""
        print("\n📁 INVESTIGANDO CATEGORIZACIÓN INCORRECTA")
        print("=" * 60)
        
        categorization_issues = {
            'misplaced_logs': [],
            'category_overlap': defaultdict(set),
            'missing_categories': []
        }
        
        # Buscar logs que deberían estar en otras categorías
        app_log = self.logs_dir / "application" / f"ict_engine_{self.today}.log"
        
        if app_log.exists():
            with open(app_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            fvg_logs_in_app = 0
            market_logs_in_app = 0
            pattern_logs_in_app = 0
            
            for line in lines:
                if 'fvg_memory' in line.lower() or 'fvg' in line.lower():
                    fvg_logs_in_app += 1
                elif 'market' in line.lower() or 'trading' in line.lower():
                    market_logs_in_app += 1
                elif 'pattern' in line.lower():
                    pattern_logs_in_app += 1
            
            print(f"🔍 LOGS MAL CATEGORIZADOS EN APPLICATION:")
            print(f"   FVG logs que deberían estar en FVG_MEMORY: {fvg_logs_in_app}")
            print(f"   Market logs que deberían estar en MARKET_DATA: {market_logs_in_app}")
            print(f"   Pattern logs que deberían estar en PATTERNS: {pattern_logs_in_app}")
            
            categorization_issues['misplaced_logs'] = [
                {'type': 'FVG', 'count': fvg_logs_in_app, 'should_be': 'FVG_MEMORY'},
                {'type': 'MARKET', 'count': market_logs_in_app, 'should_be': 'MARKET_DATA'},
                {'type': 'PATTERN', 'count': pattern_logs_in_app, 'should_be': 'PATTERNS'}
            ]
        
        return categorization_issues
    
    def _get_context(self, lines, index, context_lines=2):
        """📄 Obtener contexto alrededor de una línea"""
        start = max(0, index - context_lines)
        end = min(len(lines), index + context_lines + 1)
        return [line.strip() for line in lines[start:end]]
    
    def generate_problem_report(self):
        """📋 Generar reporte completo de problemas"""
        print("🔍 INVESTIGACIÓN COMPLETA DE PROBLEMAS DE LOGS")
        print("=" * 80)
        
        # Realizar todas las investigaciones
        volume_issues = self.investigate_application_volume()
        error_issues = self.investigate_errors()
        timestamp_issues = self.investigate_timestamp_issues()
        categorization_issues = self.investigate_categorization_issues()
        
        # Verificar que tenemos datos válidos
        if not volume_issues:
            volume_issues = {'total_lines': 0, 'massive_duplicates': 0}
        if not error_issues:
            error_issues = {'total_errors': 0, 'total_criticals': 0}
        if not timestamp_issues:
            timestamp_issues = {'format_inconsistencies': []}
        if not categorization_issues:
            categorization_issues = {'misplaced_logs': []}
        
        # Generar reporte final
        print("\n📋 RESUMEN DE PROBLEMAS IDENTIFICADOS")
        print("=" * 80)
        
        problems = []
        
        # Problema 1: Volumen excesivo
        if volume_issues.get('total_lines', 0) > 1000:
            problems.append({
                'type': 'VOLUME_EXCESSIVE',
                'severity': 'HIGH',
                'description': f"APPLICATION tiene {volume_issues.get('total_lines', 0)} logs (>1000)",
                'cause': f"Duplicación masiva: {volume_issues.get('massive_duplicates', 0)} tipos de mensaje",
                'impact': 'Rendimiento degradado, archivos grandes'
            })
        
        # Problema 2: ERRORs críticos
        if error_issues.get('total_errors', 0) > 0 or error_issues.get('total_criticals', 0) > 0:
            problems.append({
                'type': 'CRITICAL_ERRORS',
                'severity': 'CRITICAL',
                'description': f"{error_issues.get('total_errors', 0)} ERRORs, {error_issues.get('total_criticals', 0)} CRITICALs",
                'cause': 'Risk violations, emergency actions, test errors',
                'impact': 'Operación del sistema comprometida'
            })
        
        # Problema 3: Timestamps inconsistentes
        if timestamp_issues.get('format_inconsistencies', []):
            problems.append({
                'type': 'TIMESTAMP_INCONSISTENT',
                'severity': 'MEDIUM',
                'description': f"{len(timestamp_issues.get('format_inconsistencies', []))} archivos con formatos mixtos",
                'cause': 'Configuraciones de logger inconsistentes',
                'impact': 'Dificulta análisis temporal y debugging'
            })
        
        # Problema 4: Categorización incorrecta
        misplaced_total = sum(item.get('count', 0) for item in categorization_issues.get('misplaced_logs', []))
        if misplaced_total > 100:
            problems.append({
                'type': 'CATEGORIZATION_WRONG',
                'severity': 'MEDIUM',
                'description': f"{misplaced_total} logs en categorías incorrectas",
                'cause': 'Reglas de categorización imprecisas',
                'impact': 'Dificulta búsqueda y análisis por componente'
            })
        
        print(f"🚨 TOTAL PROBLEMAS IDENTIFICADOS: {len(problems)}")
        
        for i, problem in enumerate(problems, 1):
            print(f"\n{i}. {problem['type']} ({problem['severity']})")
            print(f"   📝 Descripción: {problem['description']}")
            print(f"   🔍 Causa: {problem['cause']}")
            print(f"   ⚠️ Impacto: {problem['impact']}")
        
        return {
            'total_problems': len(problems),
            'problems': problems,
            'volume_analysis': volume_issues,
            'error_analysis': error_issues,
            'timestamp_analysis': timestamp_issues,
            'categorization_analysis': categorization_issues
        }

def main():
    """🚀 Función principal"""
    investigator = LogProblemInvestigator()
    report = investigator.generate_problem_report()
    
    # Guardar reporte
    report_file = Path(__file__).parent.parent / "03-DOCUMENTATION" / "reports" / f"log_problems_investigation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Reporte detallado guardado en: {report_file}")

if __name__ == "__main__":
    main()
