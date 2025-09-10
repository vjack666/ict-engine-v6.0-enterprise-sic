"""
Analizador de Logs Black Box MT5 v6.0 Enterprise
Herramienta para análisis de logs de health monitoring tipo caja negra

Este script permite:
- Análisis de patrones de salud MT5
- Detección de anomalías en rendimiento
- Estadísticas de uptime/downtime
- Alertas de degradación de performance
- Reportes consolidados de health monitoring
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics

@dataclass
class AnalysisResult:
    """Resultado de análisis de logs"""
    time_period: str
    total_checks: int
    healthy_checks: int
    failed_checks: int
    uptime_percentage: float
    avg_response_time_ms: float
    max_response_time_ms: float
    min_response_time_ms: float
    performance_degradations: List[Dict]
    critical_alerts: List[Dict]
    reconnection_events: int
    balance_changes: List[Dict]
    recommendations: List[str]

class MT5LogAnalyzer:
    """
    Analizador de logs black box para MT5 Health Monitoring
    """
    
    def __init__(self, logs_base_path: str):
        """
        Inicializar analizador
        
        Args:
            logs_base_path: Ruta base de logs de health monitoring
        """
        self.logs_path = Path(logs_base_path)
        self.daily_path = self.logs_path / "daily"
        self.alerts_path = self.logs_path / "alerts"
        self.performance_path = self.logs_path / "performance"
        self.connections_path = self.logs_path / "connections"
        
        print(f"🔍 MT5 Log Analyzer inicializado")
        print(f"   📁 Base path: {self.logs_path}")
        
    def analyze_day(self, target_date: Optional[str] = None) -> AnalysisResult:
        """
        Analizar logs de un día específico
        
        Args:
            target_date: Fecha en formato YYYY-MM-DD (None = hoy)
            
        Returns:
            AnalysisResult: Resultado del análisis
        """
        if target_date is None:
            target_date = datetime.now().strftime("%Y-%m-%d")
            
        print(f"📊 Analizando logs del {target_date}...")
        
        # Cargar logs del día
        health_data = self._load_daily_health_logs(target_date)
        if not health_data:
            print(f"❌ No se encontraron logs para {target_date}")
            return self._empty_result(target_date)
            
        # Realizar análisis
        result = self._analyze_health_data(health_data, target_date)
        
        print(f"✅ Análisis completado: {result.total_checks} checks procesados")
        return result
        
    def _load_daily_health_logs(self, date: str) -> List[Dict]:
        """Cargar logs de salud de un día específico"""
        json_file = self.daily_path / f"health_checks_{date}.json"
        
        if not json_file.exists():
            return []
            
        health_data = []
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
                # Dividir por líneas o por separador de objetos JSON
                if content:
                    # Intentar dividir por nuevas líneas primero
                    lines = content.split('\\n')
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        # Si la línea contiene múltiples objetos JSON, separarlos
                        # Buscar múltiples objetos JSON en una línea
                        json_objects = []
                        brace_count = 0
                        current_object = ""
                        
                        for char in line:
                            current_object += char
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    # Objeto JSON completo encontrado
                                    json_objects.append(current_object.strip())
                                    current_object = ""
                        
                        # Procesar cada objeto JSON encontrado
                        for json_str in json_objects:
                            if json_str:
                                try:
                                    data = json.loads(json_str)
                                    health_data.append(data)
                                except json.JSONDecodeError as e:
                                    print(f"⚠️ Error parsing JSON object: {e}")
                                    print(f"   Problematic JSON: {json_str[:100]}...")
                                    continue
                            
        except Exception as e:
            print(f"❌ Error loading daily logs: {e}")
            
        return health_data
        
    def _analyze_health_data(self, health_data: List[Dict], date: str) -> AnalysisResult:
        """Analizar datos de salud"""
        if not health_data:
            return self._empty_result(date)
            
        # Extraer métricas
        total_checks = len(health_data)
        healthy_checks = 0
        failed_checks = 0
        response_times = []
        performance_degradations = []
        critical_alerts = []
        reconnection_events = 0
        balance_changes = []
        
        prev_balance = None
        
        for entry in health_data:
            metrics = entry.get('metrics', {})
            status = metrics.get('status', '')
            response_time = metrics.get('response_time_ms', 0)
            balance = metrics.get('account_balance', 0)
            failed_count = metrics.get('failed_checks_count', 0)
            reconnections = metrics.get('reconnection_attempts', 0)
            
            # Contar checks saludables vs fallidos
            if 'HEALTHY' in status:
                healthy_checks += 1
            else:
                failed_checks += 1
                
            # Registrar tiempos de respuesta válidos
            if response_time > 0:
                response_times.append(response_time)
                
            # Detectar degradación de performance (>5 segundos)
            if response_time > 5000:
                performance_degradations.append({
                    'timestamp': entry.get('timestamp'),
                    'response_time_ms': response_time,
                    'status': status
                })
                
            # Detectar alertas críticas
            if failed_count > 0:
                critical_alerts.append({
                    'timestamp': entry.get('timestamp'),
                    'failed_checks': failed_count,
                    'status': status,
                    'error_message': metrics.get('error_message')
                })
                
            # Contar eventos de reconexión
            if reconnections > 0:
                reconnection_events += reconnections
                
            # Detectar cambios de balance
            if prev_balance is not None and balance != prev_balance:
                balance_changes.append({
                    'timestamp': entry.get('timestamp'),
                    'from_balance': prev_balance,
                    'to_balance': balance,
                    'change': balance - prev_balance
                })
            prev_balance = balance
            
        # Calcular estadísticas
        uptime_percentage = (healthy_checks / total_checks * 100) if total_checks > 0 else 0
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = max_response_time = min_response_time = 0
            
        # Generar recomendaciones
        recommendations = self._generate_recommendations(
            uptime_percentage, avg_response_time, len(performance_degradations),
            len(critical_alerts), reconnection_events
        )
        
        return AnalysisResult(
            time_period=date,
            total_checks=total_checks,
            healthy_checks=healthy_checks,
            failed_checks=failed_checks,
            uptime_percentage=uptime_percentage,
            avg_response_time_ms=avg_response_time,
            max_response_time_ms=max_response_time,
            min_response_time_ms=min_response_time,
            performance_degradations=performance_degradations,
            critical_alerts=critical_alerts,
            reconnection_events=reconnection_events,
            balance_changes=balance_changes,
            recommendations=recommendations
        )
        
    def _generate_recommendations(self, uptime: float, avg_response: float, 
                                degradations: int, alerts: int, reconnections: int) -> List[str]:
        """Generar recomendaciones basadas en métricas"""
        recommendations = []
        
        # Uptime recommendations
        if uptime < 95:
            recommendations.append(f"🔴 CRÍTICO: Uptime bajo ({uptime:.1f}%) - Revisar estabilidad de conexión")
        elif uptime < 99:
            recommendations.append(f"🟡 ATENCIÓN: Uptime subóptimo ({uptime:.1f}%) - Monitorear conexión")
        else:
            recommendations.append(f"✅ Uptime excelente ({uptime:.1f}%)")
            
        # Response time recommendations
        if avg_response > 1000:
            recommendations.append(f"🔴 CRÍTICO: Tiempo de respuesta alto ({avg_response:.1f}ms) - Optimizar conexión")
        elif avg_response > 500:
            recommendations.append(f"🟡 ATENCIÓN: Tiempo de respuesta elevado ({avg_response:.1f}ms)")
        else:
            recommendations.append(f"✅ Tiempo de respuesta óptimo ({avg_response:.1f}ms)")
            
        # Performance degradations
        if degradations > 5:
            recommendations.append(f"🔴 CRÍTICO: {degradations} degradaciones de performance - Revisar red/servidor")
        elif degradations > 0:
            recommendations.append(f"🟡 ATENCIÓN: {degradations} degradaciones detectadas")
            
        # Critical alerts
        if alerts > 3:
            recommendations.append(f"🔴 CRÍTICO: {alerts} alertas críticas - Acción inmediata requerida")
        elif alerts > 0:
            recommendations.append(f"🟡 ATENCIÓN: {alerts} alertas registradas")
            
        # Reconnection events
        if reconnections > 5:
            recommendations.append(f"🔴 CRÍTICO: {reconnections} reconexiones - Inestabilidad de conexión")
        elif reconnections > 0:
            recommendations.append(f"🟡 ATENCIÓN: {reconnections} eventos de reconexión")
            
        return recommendations
        
    def _empty_result(self, date: str) -> AnalysisResult:
        """Crear resultado vacío"""
        return AnalysisResult(
            time_period=date,
            total_checks=0,
            healthy_checks=0,
            failed_checks=0,
            uptime_percentage=0,
            avg_response_time_ms=0,
            max_response_time_ms=0,
            min_response_time_ms=0,
            performance_degradations=[],
            critical_alerts=[],
            reconnection_events=0,
            balance_changes=[],
            recommendations=["❌ No hay datos para analizar"]
        )
        
    def generate_report(self, result: AnalysisResult, save_to_file: bool = True) -> str:
        """
        Generar reporte detallado de análisis
        
        Args:
            result: Resultado de análisis
            save_to_file: Si guardar el reporte en archivo
            
        Returns:
            str: Reporte formateado
        """
        report_lines = [
            "=" * 80,
            f"📊 MT5 HEALTH MONITORING ANALYSIS REPORT",
            f"📅 Período: {result.time_period}",
            f"⏰ Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 80,
            "",
            "📈 RESUMEN EJECUTIVO:",
            f"   ✅ Total checks: {result.total_checks}",
            f"   🟢 Healthy: {result.healthy_checks} ({result.uptime_percentage:.1f}%)",
            f"   🔴 Failed: {result.failed_checks}",
            f"   ⚡ Avg response: {result.avg_response_time_ms:.1f}ms",
            f"   📊 Max response: {result.max_response_time_ms:.1f}ms",
            f"   📊 Min response: {result.min_response_time_ms:.1f}ms",
            "",
            "🔍 ANÁLISIS DETALLADO:",
            f"   🚨 Performance degradations: {len(result.performance_degradations)}",
            f"   ⚠️ Critical alerts: {len(result.critical_alerts)}",
            f"   🔄 Reconnection events: {result.reconnection_events}",
            f"   💰 Balance changes: {len(result.balance_changes)}",
            "",
        ]
        
        # Agregar degradaciones de performance si existen
        if result.performance_degradations:
            report_lines.extend([
                "🚨 DEGRADACIONES DE PERFORMANCE:",
                ""
            ])
            for deg in result.performance_degradations[:5]:  # Mostrar primeras 5
                timestamp = deg['timestamp'][:19]  # Solo fecha/hora
                report_lines.append(f"   {timestamp} | {deg['response_time_ms']:.1f}ms | {deg['status']}")
            
            if len(result.performance_degradations) > 5:
                report_lines.append(f"   ... y {len(result.performance_degradations) - 5} más")
            report_lines.append("")
            
        # Agregar alertas críticas si existen
        if result.critical_alerts:
            report_lines.extend([
                "⚠️ ALERTAS CRÍTICAS:",
                ""
            ])
            for alert in result.critical_alerts[:5]:  # Mostrar primeras 5
                timestamp = alert['timestamp'][:19]
                error_msg = alert.get('error_message', 'N/A')[:50]  # Truncar mensaje
                report_lines.append(f"   {timestamp} | Failed: {alert['failed_checks']} | {error_msg}")
                
            if len(result.critical_alerts) > 5:
                report_lines.append(f"   ... y {len(result.critical_alerts) - 5} más")
            report_lines.append("")
            
        # Agregar cambios de balance si existen
        if result.balance_changes:
            report_lines.extend([
                "💰 CAMBIOS DE BALANCE:",
                ""
            ])
            for change in result.balance_changes:
                timestamp = change['timestamp'][:19]
                change_amount = change['change']
                symbol = "+" if change_amount > 0 else ""
                report_lines.append(f"   {timestamp} | {symbol}{change_amount:.2f} | {change['from_balance']:.2f} → {change['to_balance']:.2f}")
            report_lines.append("")
            
        # Agregar recomendaciones
        if result.recommendations:
            report_lines.extend([
                "💡 RECOMENDACIONES:",
                ""
            ])
            for rec in result.recommendations:
                report_lines.append(f"   {rec}")
            report_lines.append("")
            
        report_lines.extend([
            "=" * 80,
            f"📊 Reporte generado por MT5 Log Analyzer v6.0 Enterprise",
            "=" * 80
        ])
        
        report_text = "\\n".join(report_lines)
        
        # Guardar a archivo si se solicita
        if save_to_file:
            report_file = self.logs_path / f"analysis_report_{result.time_period}.txt"
            try:
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                print(f"📄 Reporte guardado en: {report_file}")
            except Exception as e:
                print(f"❌ Error guardando reporte: {e}")
                
        return report_text
        
    def analyze_multiple_days(self, days: int = 7) -> Dict[str, AnalysisResult]:
        """
        Analizar múltiples días
        
        Args:
            days: Número de días hacia atrás a analizar
            
        Returns:
            Dict con resultados de cada día
        """
        results = {}
        end_date = datetime.now()
        
        print(f"📊 Analizando últimos {days} días...")
        
        for i in range(days):
            current_date = end_date - timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            
            print(f"   📅 Procesando {date_str}...")
            result = self.analyze_day(date_str)
            results[date_str] = result
            
        return results

def main():
    """Función principal para análisis de logs"""
    print("🔍 MT5 Black Box Log Analyzer v6.0 Enterprise")
    print("=" * 60)
    
    # Configurar paths
    logs_path = "05-LOGS/health_monitoring"
    
    # Verificar que existe la carpeta de logs
    if not Path(logs_path).exists():
        print(f"❌ No se encontró la carpeta de logs: {logs_path}")
        print("   Asegúrate de que el sistema de monitoreo haya ejecutado al menos una vez")
        return
        
    # Crear analizador
    analyzer = MT5LogAnalyzer(logs_path)
    
    # Analizar día actual
    print("\\n📊 ANÁLISIS DEL DÍA ACTUAL:")
    print("-" * 40)
    
    today_result = analyzer.analyze_day()
    
    if today_result.total_checks > 0:
        # Mostrar resumen
        print(f"✅ Checks realizados: {today_result.total_checks}")
        print(f"📊 Uptime: {today_result.uptime_percentage:.1f}%")
        print(f"⚡ Tiempo promedio respuesta: {today_result.avg_response_time_ms:.1f}ms")
        print(f"🚨 Degradaciones: {len(today_result.performance_degradations)}")
        print(f"⚠️ Alertas críticas: {len(today_result.critical_alerts)}")
        
        # Generar reporte completo
        print("\\n📄 GENERANDO REPORTE DETALLADO...")
        report = analyzer.generate_report(today_result)
        print("\\n" + report)
        
    else:
        print("❌ No hay datos para el día actual")
        print("   Ejecuta el sistema de monitoreo para generar logs")
        
    # Analizar últimos 3 días si hay datos
    print("\\n📈 ANÁLISIS MULTI-DÍA (últimos 3 días):")
    print("-" * 40)
    
    multi_results = analyzer.analyze_multiple_days(3)
    
    for date, result in multi_results.items():
        if result.total_checks > 0:
            print(f"📅 {date}: {result.total_checks} checks | Uptime: {result.uptime_percentage:.1f}% | Avg: {result.avg_response_time_ms:.1f}ms")
        else:
            print(f"📅 {date}: Sin datos")

if __name__ == "__main__":
    main()
