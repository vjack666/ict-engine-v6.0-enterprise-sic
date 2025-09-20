from __future__ import annotations
from typing import Dict, Any
import math

class MSSBaselineModel:
    """Lightweight heuristic model acting as a placeholder for a trained classifier.
    Produces a probability-like score for structure shift based on feature aggregates.
    """
    def predict_proba(self, features: Dict[str, Any]) -> float:
        vol = float(features.get('volatility', 0.0))
        body = float(features.get('body_ratio', 0.0))
        direction = float(features.get('direction_consistency', 0.5))
        gap = float(features.get('gap_flag', 0.0))

        # Normalize volatility to pip-ish space: assume typical ATR ~ 0.0005-0.002
        vol_norm = max(0.0, min(1.5, vol / 0.002))  # cap at 1.5

        # Simple logistic style combine
        z = 1.2 * vol_norm + 0.8 * body + 0.5 * (direction - 0.5) + 0.4 * gap - 0.6
        # Sigmoid
        return 1.0 / (1.0 + math.exp(-z))
