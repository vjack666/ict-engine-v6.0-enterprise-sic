"""
PerformanceAnalyzer
Análisis de performance y métricas para Silver Bullet Enterprise v6.0
"""

class PerformanceAnalyzer:
    def __init__(self):
        self.metrics = {
            'total_analyses': 0,
            'successful_analyses': 0,
            'average_analysis_time': 0.0,
            'memory_efficiency': 0.0,
            'training_cycles': 0
        }

    def update_metrics(self, analysis_results: dict):
        """
        Actualiza las métricas globales del sistema con los resultados de análisis.
        """
        self.metrics['total_analyses'] += 1
        if analysis_results.get('status') == 'completed':
            self.metrics['successful_analyses'] += 1
        duration = analysis_results.get('duration_seconds', 0.0)
        current_avg = self.metrics['average_analysis_time']
        total_analyses = self.metrics['total_analyses']
        self.metrics['average_analysis_time'] = (
            (current_avg * (total_analyses - 1) + duration) / total_analyses
        )
        memory_enhanced = analysis_results.get('memory_enhanced_signals', 0)
        total_signals = analysis_results.get('total_signals', 1)
        self.metrics['memory_efficiency'] = (
            memory_enhanced / total_signals if total_signals > 0 else 0.0
        )

    def get_metrics(self) -> dict:
        """
        Retorna las métricas globales actuales del sistema.
        """
        return self.metrics.copy()
