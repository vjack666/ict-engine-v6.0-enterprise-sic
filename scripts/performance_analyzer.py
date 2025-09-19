#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 PERFORMANCE ANALYZER - ICT ENGINE v6.0 ENTERPRISE
====================================================

Analiza el rendimiento actual del sistema y genera reporte de métricas.
Identifica bottlenecks y áreas de optimización.

Autor: ICT Engine v6.0 Team
Fecha: 19 Septiembre 2025
"""

import json
import time
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import statistics

class PerformanceAnalyzer:
    """Analizador de rendimiento del sistema ICT Engine"""
    
    def __init__(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.metrics_dir = self.repo_root / "04-DATA" / "metrics"
        self.logs_dir = self.repo_root / "05-LOGS"
        
        self.analysis_results = {}
        self.recommendations = []
        
    def analyze_current_system_metrics(self) -> Dict[str, Any]:
        """Analizar métricas actuales del sistema"""
        print("🔍 Analizando métricas del sistema...")
        
        try:
            # Leer métricas del sistema
            system_metrics_file = self.metrics_dir / "system_metrics.json"
            if system_metrics_file.exists():
                with open(system_metrics_file, 'r', encoding='utf-8') as f:
                    system_data = json.load(f)
            else:
                system_data = self._collect_live_system_metrics()
            
            # Leer métricas de trading
            trading_metrics_file = self.metrics_dir / "trading_metrics.json"
            trading_data = {}
            if trading_metrics_file.exists():
                with open(trading_metrics_file, 'r', encoding='utf-8') as f:
                    trading_data = json.load(f)
            
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'system_metrics': system_data,
                'trading_metrics': trading_data,
                'performance_assessment': self._assess_performance(system_data, trading_data)
            }
            
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing metrics: {e}")
            return {'error': str(e)}
    
    def _collect_live_system_metrics(self) -> Dict[str, Any]:
        """Recolectar métricas del sistema en tiempo real"""
        cpu_percent = psutil.cpu_percent(interval=1.0)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network_connections = len(psutil.net_connections())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_usage_percent': disk.percent,
            'network_connections': network_connections,
            'process_count': len(psutil.pids())
        }
    
    def _assess_performance(self, system_data: Dict, trading_data: Dict) -> Dict[str, Any]:
        """Evaluar el rendimiento del sistema"""
        assessment = {
            'overall_health': 'unknown',
            'bottlenecks': [],
            'strengths': [],
            'concerns': []
        }
        
        # Evaluar CPU
        cpu_percent = system_data.get('cpu_percent', 0)
        if cpu_percent > 80:
            assessment['bottlenecks'].append(f"High CPU usage: {cpu_percent:.1f}%")
            assessment['concerns'].append('CPU_HIGH')
        elif cpu_percent < 30:
            assessment['strengths'].append(f"Low CPU usage: {cpu_percent:.1f}%")
        
        # Evaluar Memoria
        memory_percent = system_data.get('memory_percent', 0)
        if memory_percent > 85:
            assessment['bottlenecks'].append(f"High memory usage: {memory_percent:.1f}%")
            assessment['concerns'].append('MEMORY_HIGH')
        elif memory_percent < 70:
            assessment['strengths'].append(f"Moderate memory usage: {memory_percent:.1f}%")
        
        # Evaluar conectividad de trading
        if trading_data.get('mt5_connected', False):
            assessment['strengths'].append("MT5 connection stable")
        else:
            assessment['bottlenecks'].append("MT5 not connected")
            assessment['concerns'].append('MT5_DISCONNECTED')
        
        # Evaluar latencia del broker
        broker_ping = trading_data.get('broker_ping_ms', 9999)
        if broker_ping > 100:
            assessment['concerns'].append('HIGH_LATENCY')
            assessment['bottlenecks'].append(f"High broker latency: {broker_ping:.1f}ms")
        elif broker_ping < 50:
            assessment['strengths'].append(f"Low broker latency: {broker_ping:.1f}ms")
        
        # Determinar salud general
        if not assessment['bottlenecks']:
            assessment['overall_health'] = 'excellent'
        elif len(assessment['bottlenecks']) <= 2:
            assessment['overall_health'] = 'good'
        else:
            assessment['overall_health'] = 'needs_attention'
            
        return assessment
    
    def benchmark_system_operations(self) -> Dict[str, Any]:
        """Benchmarking de operaciones del sistema"""
        print("⚡ Ejecutando benchmarks...")
        
        benchmarks = {}
        
        # Benchmark 1: File I/O
        start_time = time.time()
        test_file = Path("temp_benchmark.txt")
        with open(test_file, 'w') as f:
            f.write("benchmark test" * 1000)
        with open(test_file, 'r') as f:
            content = f.read()
        test_file.unlink()
        file_io_time = (time.time() - start_time) * 1000
        benchmarks['file_io_ms'] = file_io_time
        
        # Benchmark 2: JSON processing
        start_time = time.time()
        test_data = {'test': list(range(1000))}
        for _ in range(100):
            json_str = json.dumps(test_data)
            json.loads(json_str)
        json_processing_time = (time.time() - start_time) * 1000
        benchmarks['json_processing_ms'] = json_processing_time
        
        # Benchmark 3: Memory allocation
        start_time = time.time()
        big_list = list(range(100000))
        del big_list
        memory_alloc_time = (time.time() - start_time) * 1000
        benchmarks['memory_allocation_ms'] = memory_alloc_time
        
        # Benchmark 4: Threading overhead
        start_time = time.time()
        threads = []
        for i in range(10):
            thread = threading.Thread(target=lambda: time.sleep(0.01))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        threading_time = (time.time() - start_time) * 1000
        benchmarks['threading_overhead_ms'] = threading_time
        
        return benchmarks
    
    def analyze_log_patterns(self) -> Dict[str, Any]:
        """Analizar patrones en los logs para identificar issues"""
        print("📋 Analizando patrones de logs...")
        
        log_analysis = {
            'error_patterns': [],
            'performance_issues': [],
            'memory_events': [],
            'connection_issues': [],
            'summary': {},
            'error': None
        }
        
        try:
            # Analizar logs del sistema más reciente
            system_log_file = self.logs_dir / "system" / f"system_{datetime.now().strftime('%Y-%m-%d')}.log"
            if system_log_file.exists():
                with open(system_log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    logs = f.readlines()
                
                # Buscar patrones
                error_count = 0
                memory_cleanup_count = 0
                alert_count = 0
                performance_issues = []
                connection_issues = []
                
                for line in logs:
                    line_lower = line.lower()
                    
                    # Analizar errores
                    if 'error' in line_lower:
                        error_count += 1
                        if error_count <= 5:  # Solo los primeros 5 errores
                            log_analysis['error_patterns'].append(line.strip())
                    
                    # Analizar eventos de memoria
                    if 'memory cleanup' in line_lower or 'memory pressure' in line_lower:
                        memory_cleanup_count += 1
                        log_analysis['memory_events'].append(line.strip())
                    
                    # Analizar alertas procesadas
                    if 'alert' in line_lower and 'processed' in line_lower:
                        alert_count += 1
                    
                    # Analizar problemas de performance
                    if any(keyword in line_lower for keyword in ['slow', 'timeout', 'delay', 'performance']):
                        performance_issues.append(line.strip())
                        if len(log_analysis['performance_issues']) < 3:  # Solo los primeros 3
                            log_analysis['performance_issues'].append(line.strip())
                    
                    # Analizar problemas de conexión
                    if any(keyword in line_lower for keyword in ['connection', 'disconnect', 'network', 'broker']):
                        connection_issues.append(line.strip())
                        if len(log_analysis['connection_issues']) < 3:  # Solo los primeros 3
                            log_analysis['connection_issues'].append(line.strip())
                
                log_analysis['summary'] = {
                    'total_errors': error_count,
                    'memory_cleanups': memory_cleanup_count,
                    'alerts_processed': alert_count,
                    'log_lines_analyzed': len(logs)
                }
                
        except Exception as e:
            log_analysis['error'] = f"Could not analyze logs: {str(e)}"
        
        return log_analysis
    
    def generate_optimization_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generar recomendaciones de optimización"""
        recommendations = []
        
        # Análisis de rendimiento
        performance = analysis.get('performance_assessment', {})
        concerns = performance.get('concerns', [])
        
        if 'MEMORY_HIGH' in concerns:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Memory Optimization',
                'issue': 'High memory usage detected',
                'recommendation': 'Increase memory cleanup frequency, reduce cache sizes',
                'estimated_impact': 'Medium'
            })
        
        if 'CPU_HIGH' in concerns:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'CPU Optimization',
                'issue': 'High CPU usage detected',
                'recommendation': 'Review heavy computational tasks, optimize algorithms',
                'estimated_impact': 'High'
            })
        
        if 'HIGH_LATENCY' in concerns:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Network Optimization',
                'issue': 'High broker latency',
                'recommendation': 'Review network connection, consider connection pooling',
                'estimated_impact': 'Medium'
            })
        
        if 'MT5_DISCONNECTED' in concerns:
            recommendations.append({
                'priority': 'CRITICAL',
                'category': 'Connectivity',
                'issue': 'MT5 disconnected',
                'recommendation': 'Implement robust reconnection logic, monitor connection health',
                'estimated_impact': 'Critical'
            })
        
        # Recomendaciones basadas en benchmarks
        benchmarks = analysis.get('benchmarks', {})
        if benchmarks.get('file_io_ms', 0) > 100:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'I/O Performance',
                'issue': 'Slow file operations',
                'recommendation': 'Optimize file I/O with async operations or caching',
                'estimated_impact': 'Medium'
            })
        
        # Recomendaciones basadas en análisis de logs
        log_analysis = analysis.get('log_analysis', {})
        log_summary = log_analysis.get('summary', {})
        
        # Si hay muchos errores en los logs
        error_count = log_summary.get('total_errors', 0)
        if error_count > 10:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Error Reduction',
                'issue': f'High error rate detected: {error_count} errors in logs',
                'recommendation': 'Review error patterns, improve error handling and validation',
                'estimated_impact': 'High'
            })
        
        # Si hay muchas limpiezas de memoria
        memory_cleanups = log_summary.get('memory_cleanups', 0)
        if memory_cleanups > 5:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Memory Management',
                'issue': f'Frequent memory cleanups: {memory_cleanups} events',
                'recommendation': 'Review memory usage patterns, consider more aggressive cleanup',
                'estimated_impact': 'Medium'
            })
        
        # Si hay problemas de performance en logs
        if log_analysis.get('performance_issues'):
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Performance Issues',
                'issue': 'Performance issues detected in logs',
                'recommendation': 'Review slow operations, optimize bottlenecks',
                'estimated_impact': 'Medium'
            })
        
        # Si hay problemas de conexión
        if log_analysis.get('connection_issues'):
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Connection Stability',
                'issue': 'Connection issues detected in logs',
                'recommendation': 'Improve connection error handling and retry logic',
                'estimated_impact': 'High'
            })
        
        return recommendations
    
    def generate_report(self) -> Dict[str, Any]:
        """Generar reporte completo de análisis de rendimiento"""
        print("📊 Generando reporte de análisis de rendimiento...")
        
        # Recolectar datos
        system_analysis = self.analyze_current_system_metrics()
        benchmarks = self.benchmark_system_operations()
        log_analysis = self.analyze_log_patterns()
        
        # Compilar análisis completo
        full_analysis = {
            **system_analysis,
            'benchmarks': benchmarks,
            'log_analysis': log_analysis
        }
        
        # Generar recomendaciones
        recommendations = self.generate_optimization_recommendations(full_analysis)
        
        # Crear reporte final
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'analyzer_version': '1.0',
                'system': 'ICT Engine v6.0 Enterprise'
            },
            'executive_summary': {
                'overall_health': full_analysis.get('performance_assessment', {}).get('overall_health', 'unknown'),
                'critical_issues': len([r for r in recommendations if r['priority'] == 'CRITICAL']),
                'high_priority_issues': len([r for r in recommendations if r['priority'] == 'HIGH']),
                'total_recommendations': len(recommendations)
            },
            'detailed_analysis': full_analysis,
            'benchmarks': benchmarks,
            'optimization_recommendations': recommendations
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any]) -> Path:
        """Guardar reporte en archivo"""
        reports_dir = self.repo_root / "04-DATA" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"performance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filepath

def main():
    """Función principal"""
    print("🚀 ICT Engine v6.0 - Performance Analyzer")
    print("=" * 50)
    
    analyzer = PerformanceAnalyzer()
    
    try:
        # Generar reporte completo
        report = analyzer.generate_report()
        
        # Guardar reporte
        filepath = analyzer.save_report(report)
        
        print(f"✅ Reporte generado: {filepath}")
        
        # Mostrar resumen ejecutivo
        summary = report['executive_summary']
        print(f"📈 Resumen Ejecutivo:")
        print(f"   • Salud general: {summary['overall_health'].upper()}")
        print(f"   • Issues críticos: {summary['critical_issues']}")
        print(f"   • Issues alta prioridad: {summary['high_priority_issues']}")
        print(f"   • Total recomendaciones: {summary['total_recommendations']}")
        
        # Mostrar top 3 recomendaciones
        recommendations = report['optimization_recommendations'][:3]
        if recommendations:
            print(f"🔧 Top 3 Recomendaciones:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. [{rec['priority']}] {rec['issue']}")
                print(f"      → {rec['recommendation']}")
        
    except Exception as e:
        print(f"❌ Error durante análisis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())