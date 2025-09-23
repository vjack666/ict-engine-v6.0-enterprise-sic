"""
QualityScorer
Scoring de calidad de setups y señales para Silver Bullet Enterprise v6.0
"""

class QualityScorer:
    def __init__(self, high_quality_threshold: float = 0.75):
        self.high_quality_threshold = high_quality_threshold

    def calculate_quality_score(self, signal: dict) -> float:
        """
        Calcula el score de calidad de una señal Silver Bullet.
        Args:
            signal: dict con datos de la señal (premium/discount, estructura, confluencia, memoria, etc)
        Returns:
            float: score de calidad entre 0.0 y 1.0
        """
        score = 0.0
        # Ponderación de factores clave
        if signal.get('premium_zone'):
            score += 0.2
        if signal.get('discount_zone'):
            score += 0.2
        if signal.get('structure_score', 0) > 0.7:
            score += 0.2
        if signal.get('confluence_score', 0) > 0.6:
            score += 0.2
        if signal.get('memory_confidence', 0) > 0.6:
            score += 0.1
        if signal.get('historical_success_rate', 0) > 0.6:
            score += 0.1
        # Limitar score máximo
        return min(score, 1.0)
