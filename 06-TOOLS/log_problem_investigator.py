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
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

class LogProblemInvestigator:
    """🔍 Investigador de problemas específicos en logs"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.logs_dir = self.project_root / "05-LOGS"
        self.today = datetime.now().strftime('%Y-%m-%d')
        
    def investigate_application_volume(self):
        """📊 Investigar por qué APPLICATION tiene 4445 logs"""
        print("🔍 INVESTIGANDO VOLUMEN EXCESIVO EN APPLICATION")
        print("=" * 60)
        
        app_log = self.logs_dir / "application" / f"ict_engine_{self.today}.log"
        
        if not app_log.exists():
            print("❌ Archivo APPLICATION no encontrado")
            return
        
        with open(app_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📝 Total líneas en APPLICATION: {len(lines)}")
        
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
        
        return {
            'total_lines': len(lines),
            'unique_messages': len(duplicates),
            'massive_duplicates': len(massive_duplicates),
            'max_per_second': max_per_second,
            'top_duplicates': dict(sorted(massive_duplicates.items(), key=lambda x: x[1], reverse=True)[:5])
        }
    
    def investigate_errors(self):
        """🚨 Investigar ERRORs y CRITICALs específicos"""
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
                            component_match = re.search(r'\[([^\]]+)\].*\[' + level + '\]', line)
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
        
        # Generar reporte final
        print("\n📋 RESUMEN DE PROBLEMAS IDENTIFICADOS")
        print("=" * 80)
        
        problems = []
        
        # Problema 1: Volumen excesivo
        if volume_issues['total_lines'] > 1000:
            problems.append({
                'type': 'VOLUME_EXCESSIVE',
                'severity': 'HIGH',
                'description': f"APPLICATION tiene {volume_issues['total_lines']} logs (>1000)",
                'cause': f"Duplicación masiva: {volume_issues['massive_duplicates']} tipos de mensaje",
                'impact': 'Rendimiento degradado, archivos grandes'
            })
        
        # Problema 2: ERRORs críticos
        if error_issues['total_errors'] > 0 or error_issues['total_criticals'] > 0:
            problems.append({
                'type': 'CRITICAL_ERRORS',
                'severity': 'CRITICAL',
                'description': f"{error_issues['total_errors']} ERRORs, {error_issues['total_criticals']} CRITICALs",
                'cause': 'Risk violations, emergency actions, test errors',
                'impact': 'Operación del sistema comprometida'
            })
        
        # Problema 3: Timestamps inconsistentes
        if timestamp_issues['format_inconsistencies']:
            problems.append({
                'type': 'TIMESTAMP_INCONSISTENT',
                'severity': 'MEDIUM',
                'description': f"{len(timestamp_issues['format_inconsistencies'])} archivos con formatos mixtos",
                'cause': 'Configuraciones de logger inconsistentes',
                'impact': 'Dificulta análisis temporal y debugging'
            })
        
        # Problema 4: Categorización incorrecta
        misplaced_total = sum(item['count'] for item in categorization_issues['misplaced_logs'])
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
