"""
CHOCH ML Package
----------------

Módulos para cargar CHoCH históricos desde la memoria persistente,
crear features, entrenar clasificadores base y ofrecer utilidades de
recuperación para los módulos de análisis CHoCH.

Import paths:
- machine_learning.choch.dataset
- machine_learning.choch.features
- machine_learning.choch.models
- machine_learning.choch.retrieval
"""

from .dataset import CHoCHDataset, load_choch_dataframe
from .features import build_feature_matrix
from .models import (
    BaselineValidityClassifier,
    BaselineDirectionClassifier,
    save_model,
    load_model,
)
from .retrieval import (
    find_historical_choch,
    get_recent_choch,
    get_choch_by_symbol_timeframe,
)

__all__ = [
    "CHoCHDataset",
    "load_choch_dataframe",
    "build_feature_matrix",
    "BaselineValidityClassifier",
    "BaselineDirectionClassifier",
    "save_model",
    "load_model",
    "find_historical_choch",
    "get_recent_choch",
    "get_choch_by_symbol_timeframe",
]
