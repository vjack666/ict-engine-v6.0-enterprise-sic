"""
PremiumDiscountAnalyzer: Módulo centralizado para análisis de zonas premium/discount/equilibrium según metodología ICT.
Incluye lógica de rango, fair value, market state y base para integración ML.
"""
from typing import Dict, Any, Optional
import numpy as np

class PremiumDiscountAnalyzer:
    def __init__(self, ml_model: Optional[Any] = None):
        """
        ml_model: modelo de machine learning opcional para clasificación avanzada de market state.
        """
        self.ml_model = ml_model

    def analyze_market_state(self, price_data: Dict[str, float]) -> Dict[str, Any]:
        """
        price_data: dict con claves 'high', 'low', 'close', 'open' (puede incluir más)
        Retorna dict con 'state' (premium/discount/equilibrium), 'equilibrium', 'distance', y score ML si aplica.
        """
        high = price_data.get('high')
        low = price_data.get('low')
        close = price_data.get('close')
        if high is None or low is None or close is None:
            return {'state': 'unknown', 'reason': 'missing_data'}

        equilibrium = (high + low) / 2
        range_size = high - low
        if range_size == 0:
            return {'state': 'unknown', 'reason': 'zero_range'}

        # Definición ICT: Discount = por debajo del equilibrium, Premium = por encima
        if close < equilibrium:
            state = 'discount'
        elif close > equilibrium:
            state = 'premium'
        else:
            state = 'equilibrium'

        # Distancia relativa al equilibrium
        distance = (close - equilibrium) / range_size

        result = {
            'state': state,
            'equilibrium': equilibrium,
            'distance': distance,
            'range_high': high,
            'range_low': low,
            'close': close
        }

        # Si hay modelo ML, usarlo para refinar la clasificación
        if self.ml_model is not None:
            features = np.array([[high, low, close, equilibrium, distance]])
            ml_score = self.ml_model.predict_proba(features)[0]
            result['ml_score'] = ml_score.tolist()

        return result

    def is_discount_zone(self, price_data: Dict[str, float]) -> bool:
        """True si el precio está en zona de descuento."""
        res = self.analyze_market_state(price_data)
        return res.get('state') == 'discount'

    def is_premium_zone(self, price_data: Dict[str, float]) -> bool:
        """True si el precio está en zona premium."""
        res = self.analyze_market_state(price_data)
        return res.get('state') == 'premium'

    def get_equilibrium(self, price_data: Dict[str, float]) -> Optional[float]:
        high = price_data.get('high')
        low = price_data.get('low')
        if high is not None and low is not None:
            return (high + low) / 2
        return None

    # Extensible: agregar métodos para análisis multi-timeframe, fair value gaps, etc.
