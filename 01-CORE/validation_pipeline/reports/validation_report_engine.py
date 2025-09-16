"""
📊 VALIDATION REPORT ENGINE - ICT ENGINE v6.0 ENTERPRISE
========================================================

Motor de generación de reportes avanzados que compila
resultados de validación entre dashboard live y backtesting.

Funcionalidades:
- Reportes HTML interactivos
- Métricas de accuracy detalladas
- Comparaciones visuales
- Recomendaciones automatizadas
- Exportación JSON/CSV
"""

from protocols.unified_logging import get_unified_logger
import sys
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path

# Importar componentes del pipeline
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent))

try:
    # Logging
    sys.path.append(str(current_dir.parent.parent))
    from smart_trading_logger import enviar_senal_log
    
    LOGGING_AVAILABLE = True
    
except ImportError as e:
    print(f"⚠️ [VALIDATION_REPORT_ENGINE] Logging no disponible: {e}")
    LOGGING_AVAILABLE = False
    
    def enviar_senal_log(level, message, module, category=None):
        print(f"[{level}] [{module}] {message}")


class ValidationReportEngine:
    """
    📊 Motor de Reportes de Validación - Live vs Historical
    
    Genera reportes completos de validación que incluyen:
    - Métricas de accuracy por analizador
    - Comparaciones detalladas live vs historical
    - Visualizaciones de performance
    - Recomendaciones de optimización
    - Exportación en múltiples formatos
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializar motor de reportes
        """
        self.config = config or self._default_config()
        
        enviar_senal_log("INFO", "🚀 Inicializando ValidationReportEngine", 
                        "validation_report_engine", "system")
        
        # Estado del motor de reportes
        self.report_state = {
            'initialized': datetime.now(),
            'reports_generated': 0,
            'last_report': None,
            'output_directory': self._setup_output_directory()
        }
        
        enviar_senal_log("INFO", "✅ ValidationReportEngine inicializado correctamente", 
                        "validation_report_engine", "system")
    
    def _default_config(self) -> Dict:
        """Configuración por defecto del motor de reportes"""
        return {
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
    
    def _setup_output_directory(self) -> Path:
        """Configurar directorio de salida de reportes"""
        try:
            output_dir = Path(__file__).parent.parent / "reports" / "generated_reports"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear subdirectorios
            (output_dir / "html").mkdir(exist_ok=True)
            (output_dir / "json").mkdir(exist_ok=True)
            (output_dir / "csv").mkdir(exist_ok=True)
            (output_dir / "archive").mkdir(exist_ok=True)
            
            enviar_senal_log("INFO", f"📁 Directorio de reportes: {output_dir}", 
                            "validation_report_engine", "system")
            
            return output_dir
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error configurando directorio: {e}", 
                            "validation_report_engine", "system")
            return Path(__file__).parent.parent / "reports"
    
    def generate_complete_report(self, validation_results: Dict[str, Any], 
                               report_name: Optional[str] = None) -> Dict[str, Any]:
        """
        📋 Generar reporte completo de validación
        
        Args:
            validation_results: Resultados completos de validación
            report_name: Nombre personalizado del reporte
        
        Returns:
            Información del reporte generado
        """
        report_start = datetime.now()
        
        # Generar ID único del reporte
        if not report_name:
            report_name = f"validation_report_{report_start.strftime('%Y%m%d_%H%M%S')}"
        
        enviar_senal_log("INFO", f"📊 Generando reporte completo: {report_name}", 
                        "validation_report_engine", "generation")
        
        try:
            # 1. PROCESAR DATOS DE VALIDACIÓN
            processed_data = self._process_validation_data(validation_results)
            
            # 2. GENERAR MÉTRICAS AVANZADAS
            advanced_metrics = self._generate_advanced_metrics(processed_data)
            
            # 3. CREAR ANÁLISIS COMPARATIVO
            comparative_analysis = self._create_comparative_analysis(processed_data)
            
            # 4. GENERAR RECOMENDACIONES
            recommendations = self._generate_recommendations(advanced_metrics, comparative_analysis)
            
            # 5. COMPILAR REPORTE COMPLETO
            complete_report = {
                'report_info': {
                    'name': report_name,
                    'generated_at': report_start,
                    'engine_version': '1.0.0',
                    'company': self.config.get('company_name', 'ICT Engine')
                },
                'validation_summary': validation_results.get('summary', {}),
                'processed_data': processed_data,
                'advanced_metrics': advanced_metrics,
                'comparative_analysis': comparative_analysis,
                'recommendations': recommendations,
                'raw_validation_data': validation_results if self.config.get('include_raw_data', True) else {},
                'generation_info': {
                    'duration': (datetime.now() - report_start).total_seconds(),
                    'formats_generated': [],
                    'output_files': {}
                }
            }
            
            # 6. EXPORTAR EN FORMATOS SOLICITADOS
            export_results = self._export_report(complete_report, report_name)
            complete_report['generation_info'].update(export_results)
            
            # 7. ACTUALIZAR ESTADO
            self.report_state['reports_generated'] += 1
            self.report_state['last_report'] = {
                'name': report_name,
                'generated_at': report_start,
                'files': export_results.get('output_files', {})
            }
            
            # 8. ARCHIVAR REPORTES ANTIGUOS
            if self.config.get('auto_archive', True):
                self._archive_old_reports()
            
            enviar_senal_log("INFO", f"✅ Reporte generado correctamente: {report_name} en {complete_report['generation_info']['duration']:.1f}s", 
                            "validation_report_engine", "generation")
            
            return complete_report
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error generando reporte {report_name}: {e}", 
                            "validation_report_engine", "generation")
            
            return {
                'report_info': {'name': report_name, 'generated_at': report_start},
                'error': str(e),
                'generation_info': {'duration': (datetime.now() - report_start).total_seconds(), 'success': False}
            }
    
    def _process_validation_data(self, validation_results: Dict) -> Dict[str, Any]:
        """Procesar datos de validación para análisis"""
        try:
            # Extraer datos principales
            sm_data = validation_results.get('smart_money_validation', {})
            ob_data = validation_results.get('order_blocks_validation', {})
            fvg_data = validation_results.get('fvg_validation', {})
            
            # Procesar métricas de accuracy
            accuracy_data = {
                'smart_money': {
                    'overall': sm_data.get('accuracy_metrics', {}).get('overall_accuracy', 0.0),
                    'individual': sm_data.get('accuracy_metrics', {}).get('individual_accuracies', {}),
                    'grade': sm_data.get('accuracy_metrics', {}).get('accuracy_grade', 'UNKNOWN')
                },
                'order_blocks': {
                    'overall': ob_data.get('accuracy_metrics', {}).get('overall_accuracy', 0.0),
                    'individual': ob_data.get('accuracy_metrics', {}).get('individual_accuracies', {}),
                    'grade': ob_data.get('accuracy_metrics', {}).get('accuracy_grade', 'UNKNOWN')
                },
                'fvg': {
                    'overall': fvg_data.get('accuracy_metrics', {}).get('overall_accuracy', 0.0),
                    'individual': fvg_data.get('accuracy_metrics', {}).get('individual_accuracies', {}),
                    'grade': fvg_data.get('accuracy_metrics', {}).get('accuracy_grade', 'UNKNOWN')
                }
            }
            
            # Procesar datos de performance
            performance_data = {
                'smart_money': {
                    'live_duration': sm_data.get('live_analysis', {}).get('performance', {}).get('analysis_duration', 0.0),
                    'historical_duration': sm_data.get('historical_analysis', {}).get('performance', {}).get('analysis_duration', 0.0),
                    'total_duration': sm_data.get('execution_info', {}).get('duration', 0.0)
                },
                'order_blocks': {
                    'live_duration': ob_data.get('live_analysis', {}).get('performance', {}).get('analysis_duration', 0.0),
                    'historical_duration': ob_data.get('historical_analysis', {}).get('performance', {}).get('analysis_duration', 0.0),
                    'total_duration': ob_data.get('execution_info', {}).get('duration', 0.0)
                },
                'fvg': {
                    'live_duration': fvg_data.get('live_analysis', {}).get('performance', {}).get('analysis_duration', 0.0),
                    'historical_duration': fvg_data.get('historical_analysis', {}).get('performance', {}).get('analysis_duration', 0.0),
                    'total_duration': fvg_data.get('execution_info', {}).get('duration', 0.0)
                }
            }
            
            # Procesar información de configuración
            validation_info = validation_results.get('validation_info', {})
            
            return {
                'accuracy_data': accuracy_data,
                'performance_data': performance_data,
                'validation_config': {
                    'symbol': validation_info.get('symbol', 'UNKNOWN'),
                    'timeframe': validation_info.get('timeframe', 'UNKNOWN'),
                    'validation_period': validation_info.get('validation_period', 'UNKNOWN'),
                    'started_at': validation_info.get('started_at', datetime.now())
                },
                'data_points_summary': {
                    'smart_money': {
                        'live': sm_data.get('live_analysis', {}).get('data_points', 0),
                        'historical': sm_data.get('historical_analysis', {}).get('data_points', 0)
                    },
                    'order_blocks': {
                        'live': ob_data.get('live_analysis', {}).get('data_points', 0),
                        'historical': ob_data.get('historical_analysis', {}).get('data_points', 0)
                    },
                    'fvg': {
                        'live': fvg_data.get('live_analysis', {}).get('data_points', 0),
                        'historical': fvg_data.get('historical_analysis', {}).get('data_points', 0)
                    }
                }
            }
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error procesando datos de validación: {e}", 
                            "validation_report_engine", "processing")
            
            return {
                'accuracy_data': {},
                'performance_data': {},
                'validation_config': {},
                'data_points_summary': {},
                'processing_error': str(e)
            }
    
    def _generate_advanced_metrics(self, processed_data: Dict) -> Dict[str, Any]:
        """Generar métricas avanzadas de análisis"""
        try:
            accuracy_data = processed_data.get('accuracy_data', {})
            performance_data = processed_data.get('performance_data', {})
            
            # Métricas de accuracy agregadas
            all_accuracies = []
            for analyzer in ['smart_money', 'order_blocks', 'fvg']:
                overall_acc = accuracy_data.get(analyzer, {}).get('overall', 0.0)
                if overall_acc > 0:
                    all_accuracies.append(overall_acc)
            
            # Estadísticas generales
            accuracy_stats = {
                'overall_accuracy': float(round(np.mean(all_accuracies), self.config['accuracy_precision'])) if all_accuracies else 0.0,
                'min_accuracy': round(min(all_accuracies), self.config['accuracy_precision']) if all_accuracies else 0.0,
                'max_accuracy': round(max(all_accuracies), self.config['accuracy_precision']) if all_accuracies else 0.0,
                'accuracy_std': float(round(np.std(all_accuracies), self.config['accuracy_precision'])) if len(all_accuracies) > 1 else 0.0,
                'consistency_score': self._calculate_consistency_score(all_accuracies)
            }
            
            # Métricas de performance
            all_durations = []
            for analyzer in ['smart_money', 'order_blocks', 'fvg']:
                total_duration = performance_data.get(analyzer, {}).get('total_duration', 0.0)
                if total_duration > 0:
                    all_durations.append(total_duration)
            
            performance_stats = {
                'total_validation_time': round(sum(all_durations), 2),
                'average_analyzer_time': float(round(np.mean(all_durations), 2)) if all_durations else 0.0,
                'fastest_analyzer': min(all_durations) if all_durations else 0.0,
                'slowest_analyzer': max(all_durations) if all_durations else 0.0,
                'efficiency_score': self._calculate_efficiency_score(all_durations, all_accuracies)
            }
            
            # Métricas de calidad de datos
            data_points = processed_data.get('data_points_summary', {})
            data_quality_stats = {
                'data_consistency': self._calculate_data_consistency(data_points),
                'coverage_score': self._calculate_coverage_score(data_points),
                'reliability_index': self._calculate_reliability_index(accuracy_stats, performance_stats)
            }
            
            return {
                'accuracy_statistics': accuracy_stats,
                'performance_statistics': performance_stats,
                'data_quality_statistics': data_quality_stats,
                'analyzer_rankings': self._rank_analyzers(accuracy_data, performance_data),
                'improvement_potential': self._calculate_improvement_potential(accuracy_data),
                'calculated_at': datetime.now()
            }
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error generando métricas avanzadas: {e}", 
                            "validation_report_engine", "metrics")
            
            return {
                'accuracy_statistics': {},
                'performance_statistics': {},
                'data_quality_statistics': {},
                'error': str(e)
            }
    
    def _create_comparative_analysis(self, processed_data: Dict) -> Dict[str, Any]:
        """Crear análisis comparativo detallado"""
        try:
            accuracy_data = processed_data.get('accuracy_data', {})
            
            # Análisis por analizador
            analyzer_comparison = {}
            for analyzer in ['smart_money', 'order_blocks', 'fvg']:
                analyzer_data = accuracy_data.get(analyzer, {})
                
                analyzer_comparison[analyzer] = {
                    'overall_score': analyzer_data.get('overall', 0.0),
                    'grade': analyzer_data.get('grade', 'UNKNOWN'),
                    'strengths': self._identify_strengths(analyzer_data.get('individual', {})),
                    'weaknesses': self._identify_weaknesses(analyzer_data.get('individual', {})),
                    'improvement_priority': self._calculate_improvement_priority(analyzer_data)
                }
            
            # Comparación cruzada
            cross_comparison = {
                'best_performer': max(analyzer_comparison.keys(), 
                                    key=lambda x: analyzer_comparison[x]['overall_score']) if analyzer_comparison else None,
                'worst_performer': min(analyzer_comparison.keys(), 
                                     key=lambda x: analyzer_comparison[x]['overall_score']) if analyzer_comparison else None,
                'accuracy_gaps': self._calculate_accuracy_gaps(analyzer_comparison),
                'consistency_analysis': self._analyze_consistency(analyzer_comparison)
            }
            
            return {
                'analyzer_comparison': analyzer_comparison,
                'cross_comparison': cross_comparison,
                'trend_analysis': self._analyze_trends(processed_data),
                'correlation_analysis': self._analyze_correlations(processed_data),
                'analysis_timestamp': datetime.now()
            }
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error en análisis comparativo: {e}", 
                            "validation_report_engine", "analysis")
            
            return {
                'analyzer_comparison': {},
                'cross_comparison': {},
                'error': str(e)
            }
    
    def _generate_recommendations(self, advanced_metrics: Dict, comparative_analysis: Dict) -> Dict[str, Any]:
        """Generar recomendaciones automatizadas"""
        try:
            recommendations = {
                'immediate_actions': [],
                'short_term_improvements': [],
                'long_term_optimizations': [],
                'priority_ranking': [],
                'risk_assessment': []
            }
            
            # Análisis de accuracy
            accuracy_stats = advanced_metrics.get('accuracy_statistics', {})
            overall_accuracy = accuracy_stats.get('overall_accuracy', 0.0)
            
            if overall_accuracy < 0.75:
                recommendations['immediate_actions'].append({
                    'action': 'Critical accuracy review required',
                    'description': f'Overall accuracy ({overall_accuracy:.1%}) is below acceptable threshold',
                    'priority': 'HIGH',
                    'estimated_effort': 'Medium'
                })
            elif overall_accuracy < 0.85:
                recommendations['short_term_improvements'].append({
                    'action': 'Accuracy optimization needed',
                    'description': f'Overall accuracy ({overall_accuracy:.1%}) has room for improvement',
                    'priority': 'MEDIUM',
                    'estimated_effort': 'Low'
                })
            
            # Análisis por analizador
            analyzer_comparison = comparative_analysis.get('analyzer_comparison', {})
            
            for analyzer, data in analyzer_comparison.items():
                score = data.get('overall_score', 0.0)
                grade = data.get('grade', 'UNKNOWN')
                
                if score < 0.75:
                    recommendations['immediate_actions'].append({
                        'action': f'{analyzer.title()} analyzer optimization',
                        'description': f'{analyzer.title()} accuracy ({score:.1%}) needs immediate attention',
                        'priority': 'HIGH',
                        'estimated_effort': 'Medium'
                    })
                
                # Recomendaciones específicas basadas en debilidades
                weaknesses = data.get('weaknesses', [])
                for weakness in weaknesses:
                    recommendations['short_term_improvements'].append({
                        'action': f'Improve {analyzer} - {weakness}',
                        'description': f'Address weakness in {weakness} detection',
                        'priority': 'MEDIUM',
                        'estimated_effort': 'Low'
                    })
            
            # Análisis de performance
            performance_stats = advanced_metrics.get('performance_statistics', {})
            total_time = performance_stats.get('total_validation_time', 0.0)
            
            if total_time > 30:  # más de 30 segundos
                recommendations['long_term_optimizations'].append({
                    'action': 'Performance optimization',
                    'description': f'Total validation time ({total_time:.1f}s) could be optimized',
                    'priority': 'LOW',
                    'estimated_effort': 'High'
                })
            
            # Ranking de prioridades
            all_recommendations = (
                recommendations['immediate_actions'] +
                recommendations['short_term_improvements'] +
                recommendations['long_term_optimizations']
            )
            
            # Ordenar por prioridad
            priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
            recommendations['priority_ranking'] = sorted(
                all_recommendations,
                key=lambda x: priority_order.get(x['priority'], 3)
            )
            
            # Evaluación de riesgos
            recommendations['risk_assessment'] = self._assess_risks(advanced_metrics, comparative_analysis)
            
            return recommendations
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error generando recomendaciones: {e}", 
                            "validation_report_engine", "recommendations")
            
            return {
                'immediate_actions': [],
                'short_term_improvements': [],
                'long_term_optimizations': [],
                'error': str(e)
            }
    
    def _export_report(self, report_data: Dict, report_name: str) -> Dict[str, Any]:
        """Exportar reporte en formatos solicitados"""
        export_results = {
            'formats_generated': [],
            'output_files': {},
            'export_errors': []
        }
        
        try:
            output_dir = self.report_state['output_directory']
            
            # JSON Export
            if 'json' in self.config.get('output_formats', []):
                json_file = output_dir / "json" / f"{report_name}.json"
                try:
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(report_data, f, indent=2, default=str)
                    
                    export_results['formats_generated'].append('json')
                    export_results['output_files']['json'] = str(json_file)
                    
                except Exception as e:
                    export_results['export_errors'].append(f"JSON export error: {e}")
            
            # CSV Export
            if 'csv' in self.config.get('output_formats', []):
                try:
                    csv_file = output_dir / "csv" / f"{report_name}_summary.csv"
                    summary_df = self._create_summary_dataframe(report_data)
                    summary_df.to_csv(csv_file, index=False)
                    
                    export_results['formats_generated'].append('csv')
                    export_results['output_files']['csv'] = str(csv_file)
                    
                except Exception as e:
                    export_results['export_errors'].append(f"CSV export error: {e}")
            
            # HTML Export
            if 'html' in self.config.get('output_formats', []):
                try:
                    html_file = output_dir / "html" / f"{report_name}.html"
                    html_content = self._generate_html_report(report_data)
                    
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    export_results['formats_generated'].append('html')
                    export_results['output_files']['html'] = str(html_file)
                    
                except Exception as e:
                    export_results['export_errors'].append(f"HTML export error: {e}")
            
            enviar_senal_log("INFO", f"📄 Formatos exportados: {', '.join(export_results['formats_generated'])}", 
                            "validation_report_engine", "export")
            
        except Exception as e:
            export_results['export_errors'].append(f"General export error: {e}")
            enviar_senal_log("ERROR", f"❌ Error en exportación: {e}", 
                            "validation_report_engine", "export")
        
        return export_results
    
    def _create_summary_dataframe(self, report_data: Dict) -> pd.DataFrame:
        """Crear DataFrame resumen para exportación CSV"""
        try:
            processed_data = report_data.get('processed_data', {})
            accuracy_data = processed_data.get('accuracy_data', {})
            
            summary_rows = []
            
            for analyzer in ['smart_money', 'order_blocks', 'fvg']:
                analyzer_data = accuracy_data.get(analyzer, {})
                
                row = {
                    'Analyzer': analyzer.title().replace('_', ' '),
                    'Overall_Accuracy': analyzer_data.get('overall', 0.0),
                    'Grade': analyzer_data.get('grade', 'UNKNOWN')
                }
                
                # Agregar accuracies individuales
                individual = analyzer_data.get('individual', {})
                for metric, value in individual.items():
                    row[f'{metric}_accuracy'] = value
                
                summary_rows.append(row)
            
            return pd.DataFrame(summary_rows)
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error creando DataFrame: {e}", 
                            "validation_report_engine", "export")
            return pd.DataFrame({'Error': [str(e)]})
    
    def _generate_html_report(self, report_data: Dict) -> str:
        """Generar reporte HTML interactivo"""
        try:
            # Template HTML básico (se puede expandir con CSS/JS más avanzado)
            html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validation Report - {report_data.get('report_info', {}).get('name', 'Unknown')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #007acc; padding-bottom: 20px; margin-bottom: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .metric-card {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #007acc; border-radius: 4px; }}
        .accuracy-excellent {{ border-left-color: #28a745; }}
        .accuracy-good {{ border-left-color: #ffc107; }}
        .accuracy-poor {{ border-left-color: #dc3545; }}
        .recommendation {{ background: #fff3cd; padding: 10px; margin: 5px 0; border-left: 3px solid #ffc107; border-radius: 3px; }}
        .recommendation.high {{ background: #f8d7da; border-left-color: #dc3545; }}
        .recommendation.low {{ background: #d4edda; border-left-color: #28a745; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #007acc; color: white; }}
        .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Validation Report</h1>
            <h2>{report_data.get('report_info', {}).get('name', 'Unknown Report')}</h2>
            <p>Generated: {report_data.get('report_info', {}).get('generated_at', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Company: {self.config.get('company_name', 'ICT Engine v6.0 Enterprise')}</p>
        </div>
        
        <div class="section">
            <h3>🎯 Executive Summary</h3>
            {self._generate_summary_html(report_data)}
        </div>
        
        <div class="section">
            <h3>📈 Accuracy Metrics</h3>
            {self._generate_accuracy_html(report_data)}
        </div>
        
        <div class="section">
            <h3>💡 Recommendations</h3>
            {self._generate_recommendations_html(report_data)}
        </div>
        
        <div class="section">
            <h3>📊 Detailed Analysis</h3>
            {self._generate_detailed_analysis_html(report_data)}
        </div>
        
        <div class="footer">
            <p>Report generated by ValidationReportEngine v1.0.0</p>
            <p>{self.config.get('company_name', 'ICT Engine v6.0 Enterprise')} - Validation Pipeline</p>
        </div>
    </div>
</body>
</html>
            """
            
            return html_template
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error generando HTML: {e}", 
                            "validation_report_engine", "export")
            return f"<html><body><h1>Error generating report: {e}</h1></body></html>"
    
    def _generate_summary_html(self, report_data: Dict) -> str:
        """Generar HTML del resumen ejecutivo"""
        try:
            summary = report_data.get('validation_summary', {})
            status = summary.get('overall_status', 'UNKNOWN')
            accuracy = summary.get('overall_accuracy', 0.0)
            
            status_color = {
                'PASSED': '#28a745',
                'PARTIAL': '#ffc107', 
                'FAILED': '#dc3545'
            }.get(status, '#6c757d')
            
            return f"""
            <div class="metric-card">
                <h4>Overall Status: <span style="color: {status_color};">{status}</span></h4>
                <p><strong>Overall Accuracy:</strong> {accuracy:.1%}</p>
                <p><strong>Individual Results:</strong></p>
                <ul>
            """ + '\n'.join([
                f"<li>{result['accuracy']:.1%} - {key.title().replace('_', ' ')}</li>"
                for key, result in summary.get('individual_results', {}).items()
            ]) + """
                </ul>
            </div>
            """
        except:
            return "<p>Error generating summary</p>"
    
    def _generate_accuracy_html(self, report_data: Dict) -> str:
        """Generar HTML de métricas de accuracy"""
        try:
            advanced_metrics = report_data.get('advanced_metrics', {})
            accuracy_stats = advanced_metrics.get('accuracy_statistics', {})
            
            return f"""
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Overall Accuracy</td>
                    <td>{accuracy_stats.get('overall_accuracy', 0.0):.1%}</td>
                </tr>
                <tr>
                    <td>Min Accuracy</td>
                    <td>{accuracy_stats.get('min_accuracy', 0.0):.1%}</td>
                </tr>
                <tr>
                    <td>Max Accuracy</td>
                    <td>{accuracy_stats.get('max_accuracy', 0.0):.1%}</td>
                </tr>
                <tr>
                    <td>Consistency Score</td>
                    <td>{accuracy_stats.get('consistency_score', 0.0):.3f}</td>
                </tr>
            </table>
            """
        except:
            return "<p>Error generating accuracy metrics</p>"
    
    def _generate_recommendations_html(self, report_data: Dict) -> str:
        """Generar HTML de recomendaciones"""
        try:
            recommendations = report_data.get('recommendations', {})
            html = ""
            
            for category, items in recommendations.items():
                if category in ['immediate_actions', 'short_term_improvements', 'long_term_optimizations']:
                    html += f"<h4>{category.title().replace('_', ' ')}</h4>"
                    
                    for item in items:
                        priority = item.get('priority', 'MEDIUM').lower()
                        css_class = f"recommendation {priority}"
                        html += f"""
                        <div class="{css_class}">
                            <strong>{item.get('action', 'Unknown Action')}</strong><br>
                            {item.get('description', 'No description')}<br>
                            <em>Priority: {item.get('priority', 'UNKNOWN')} | Effort: {item.get('estimated_effort', 'Unknown')}</em>
                        </div>
                        """
            
            return html
            
        except:
            return "<p>Error generating recommendations</p>"
    
    def _generate_detailed_analysis_html(self, report_data: Dict) -> str:
        """Generar HTML de análisis detallado"""
        try:
            comparative_analysis = report_data.get('comparative_analysis', {})
            analyzer_comparison = comparative_analysis.get('analyzer_comparison', {})
            
            html = "<table><tr><th>Analyzer</th><th>Score</th><th>Grade</th><th>Strengths</th><th>Weaknesses</th></tr>"
            
            for analyzer, data in analyzer_comparison.items():
                strengths = ', '.join(data.get('strengths', []))
                weaknesses = ', '.join(data.get('weaknesses', []))
                
                html += f"""
                <tr>
                    <td>{analyzer.title().replace('_', ' ')}</td>
                    <td>{data.get('overall_score', 0.0):.1%}</td>
                    <td>{data.get('grade', 'UNKNOWN')}</td>
                    <td>{strengths or 'None identified'}</td>
                    <td>{weaknesses or 'None identified'}</td>
                </tr>
                """
            
            html += "</table>"
            return html
            
        except:
            return "<p>Error generating detailed analysis</p>"
    
    # Métodos de utilidad para cálculos avanzados
    def _calculate_consistency_score(self, accuracies: List[float]) -> float:
        """Calcular score de consistencia"""
        if len(accuracies) < 2:
            return 1.0
        return float(round(1.0 - (np.std(accuracies) / np.mean(accuracies)), 3))
    
    def _calculate_efficiency_score(self, durations: List[float], accuracies: List[float]) -> float:
        """Calcular score de eficiencia (accuracy/tiempo)"""
        if not durations or not accuracies:
            return 0.0
        avg_accuracy = float(np.mean(accuracies))
        avg_duration = float(np.mean(durations))
        return float(round(avg_accuracy / avg_duration if avg_duration > 0 else 0.0, 3))
    
    def _calculate_data_consistency(self, data_points: Dict) -> float:
        """Calcular consistencia de datos"""
        # Implementación simplificada
        return 0.85  # Placeholder
    
    def _calculate_coverage_score(self, data_points: Dict) -> float:
        """Calcular score de cobertura de datos"""
        # Implementación simplificada
        return 0.90  # Placeholder
    
    def _calculate_reliability_index(self, accuracy_stats: Dict, performance_stats: Dict) -> float:
        """Calcular índice de confiabilidad"""
        accuracy = accuracy_stats.get('overall_accuracy', 0.0)
        consistency = accuracy_stats.get('consistency_score', 0.0)
        return round((accuracy + consistency) / 2, 3)
    
    def _rank_analyzers(self, accuracy_data: Dict, performance_data: Dict) -> List[Dict]:
        """Ranking de analizadores por performance"""
        rankings = []
        
        for analyzer in ['smart_money', 'order_blocks', 'fvg']:
            accuracy = accuracy_data.get(analyzer, {}).get('overall', 0.0)
            duration = performance_data.get(analyzer, {}).get('total_duration', 0.0)
            
            rankings.append({
                'analyzer': analyzer,
                'accuracy': accuracy,
                'duration': duration,
                'efficiency': accuracy / duration if duration > 0 else 0.0
            })
        
        # Ordenar por accuracy
        return sorted(rankings, key=lambda x: x['accuracy'], reverse=True)
    
    def _calculate_improvement_potential(self, accuracy_data: Dict) -> Dict[str, float]:
        """Calcular potencial de mejora por analizador"""
        potential = {}
        
        for analyzer, data in accuracy_data.items():
            current_accuracy = data.get('overall', 0.0)
            potential[analyzer] = round(1.0 - current_accuracy, 3)
        
        return potential
    
    def _identify_strengths(self, individual_accuracies: Dict) -> List[str]:
        """Identificar fortalezas del analizador"""
        strengths = []
        
        for metric, accuracy in individual_accuracies.items():
            if accuracy >= 0.9:
                strengths.append(metric)
        
        return strengths
    
    def _identify_weaknesses(self, individual_accuracies: Dict) -> List[str]:
        """Identificar debilidades del analizador"""
        weaknesses = []
        
        for metric, accuracy in individual_accuracies.items():
            if accuracy < 0.75:
                weaknesses.append(metric)
        
        return weaknesses
    
    def _calculate_improvement_priority(self, analyzer_data: Dict) -> str:
        """Calcular prioridad de mejora"""
        overall_score = analyzer_data.get('overall', 0.0)
        
        if overall_score < 0.75:
            return 'HIGH'
        elif overall_score < 0.85:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_accuracy_gaps(self, analyzer_comparison: Dict) -> Dict[str, float]:
        """Calcular gaps de accuracy entre analizadores"""
        accuracies = [data['overall_score'] for data in analyzer_comparison.values()]
        
        if len(accuracies) < 2:
            return {}
        
        return {
            'max_gap': float(round(max(accuracies) - min(accuracies), 3)),
            'avg_gap': float(round(np.std(accuracies), 3))
        }
    
    def _analyze_consistency(self, analyzer_comparison: Dict) -> Dict[str, Any]:
        """Analizar consistencia entre analizadores"""
        grades = [data['grade'] for data in analyzer_comparison.values()]
        
        return {
            'consistent_grades': len(set(grades)) == 1,
            'grade_distribution': {grade: grades.count(grade) for grade in set(grades)}
        }
    
    def _analyze_trends(self, processed_data: Dict) -> Dict[str, Any]:
        """Análisis de tendencias (placeholder para implementación futura)"""
        return {'trend_analysis': 'To be implemented with historical data'}
    
    def _analyze_correlations(self, processed_data: Dict) -> Dict[str, Any]:
        """Análisis de correlaciones (placeholder)"""
        return {'correlation_analysis': 'To be implemented with more data points'}
    
    def _assess_risks(self, advanced_metrics: Dict, comparative_analysis: Dict) -> List[Dict]:
        """Evaluar riesgos basados en métricas"""
        risks = []
        
        # Riesgo de accuracy baja
        accuracy_stats = advanced_metrics.get('accuracy_statistics', {})
        overall_accuracy = accuracy_stats.get('overall_accuracy', 0.0)
        
        if overall_accuracy < 0.75:
            risks.append({
                'risk_type': 'Low Accuracy',
                'severity': 'HIGH',
                'description': f'Overall accuracy ({overall_accuracy:.1%}) poses trading risk',
                'mitigation': 'Immediate review and optimization required'
            })
        
        # Riesgo de inconsistencia
        consistency_score = accuracy_stats.get('consistency_score', 0.0)
        if consistency_score < 0.7:
            risks.append({
                'risk_type': 'Inconsistency',
                'severity': 'MEDIUM',
                'description': f'Low consistency ({consistency_score:.3f}) between analyzers',
                'mitigation': 'Review analyzer calibration'
            })
        
        return risks
    
    def _archive_old_reports(self):
        """Archivar reportes antiguos"""
        try:
            max_reports = self.config.get('max_reports_archive', 50)
            
            # Implementación simplificada - mover archivos más antiguos a archivo
            # En una implementación completa, se verificarían fechas y se moverían archivos
            
            enviar_senal_log("INFO", f"📦 Archivando reportes antiguos (max: {max_reports})", 
                            "validation_report_engine", "archive")
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error archivando reportes: {e}", 
                            "validation_report_engine", "archive")
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Obtener estado del motor de reportes"""
        return {
            'initialized': self.report_state['initialized'],
            'reports_generated': self.report_state['reports_generated'],
            'last_report': self.report_state.get('last_report'),
            'output_directory': str(self.report_state['output_directory']),
            'config': self.config,
            'last_update': datetime.now()
        }


# Función de utilidad para crear instancia global
_engine_instance = None

def get_validation_report_engine(config: Optional[Dict] = None) -> ValidationReportEngine:
    """Obtener instancia global del motor de reportes"""
    global _engine_instance
    
    if _engine_instance is None:
        _engine_instance = ValidationReportEngine(config)
    
    return _engine_instance


if __name__ == "__main__":
    # Test básico del motor de reportes
    print("🚀 Testing ValidationReportEngine...")
    
    try:
        engine = ValidationReportEngine()
        status = engine.get_engine_status()
        
        print(f"✅ Motor de reportes inicializado correctamente")
        print(f"📁 Directorio de salida: {status['output_directory']}")
        
        # Test con datos simulados
        mock_validation_results = {
            'validation_info': {
                'symbol': 'EURUSD',
                'timeframe': 'H1',
                'validation_period': 'short',
                'started_at': datetime.now()
            },
            'summary': {
                'overall_status': 'PASSED',
                'overall_accuracy': 0.87,
                'individual_results': {
                    'smart_money': {'accuracy': 0.85, 'status': 'PASSED'},
                    'order_blocks': {'accuracy': 0.89, 'status': 'PASSED'},
                    'fvg': {'accuracy': 0.87, 'status': 'PASSED'}
                }
            }
        }
        
        report = engine.generate_complete_report(mock_validation_results, 'test_report')
        print(f"📊 Reporte de prueba generado: {len(report['generation_info']['formats_generated'])} formatos")
        
    except Exception as e:
        print(f"❌ Error en testing: {e}")