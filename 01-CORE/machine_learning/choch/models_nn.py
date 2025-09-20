from __future__ import annotations

"""
Neural-network style baselines for CHOCH classification.

Default implementation uses scikit-learn's MLPClassifier to avoid
adding heavy dependencies. If you want a full deep network with GPU,
we can switch to PyTorch (optional dependency) later.
"""

from dataclasses import dataclass
from typing import Dict, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler


def _safe_split(X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, random_state: int = 42):
    if len(X) < 5:
        return X, X, y, y
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=None)


@dataclass
class MLPValidityClassifier:
    """
    Simple neural-network baseline (sklearn MLP) for validity.
    Label rule: valid if confidence >= 75 and recency <= 240.
    """
    model: Optional[MLPClassifier] = None
    scaler: Optional[StandardScaler] = None

    def fit(self, X: pd.DataFrame, df_raw: pd.DataFrame) -> Dict[str, float]:
        y = ((df_raw["confidence"] >= 75) & (df_raw.get("recency_min", np.nan) <= 240)).astype(int)
        X_train, X_test, y_train, y_test = _safe_split(X, y)
        scaler = StandardScaler(with_mean=False)
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)
        clf = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
        clf.fit(X_train_s, y_train)
        self.model = clf
        self.scaler = scaler
        preds = clf.predict(X_test_s)
        return {"accuracy": float(accuracy_score(y_test, preds))}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None or self.scaler is None:
            raise RuntimeError("Model not trained")
        return self.model.predict(self.scaler.transform(X))


@dataclass
class MLPDirectionClassifier:
    """
    Simple neural-network baseline (sklearn MLP) for direction.
    Classes: -1 (BEARISH), 0 (NEUTRAL), 1 (BULLISH)
    """
    model: Optional[MLPClassifier] = None
    scaler: Optional[StandardScaler] = None

    def fit(self, X: pd.DataFrame, df_raw: pd.DataFrame) -> Dict[str, float]:
        target_map = {"BEARISH": -1, "NEUTRAL": 0, "BULLISH": 1}
        y = df_raw["direction"].map(lambda d: target_map.get(str(d).upper(), 0)).astype(int)
        X_train, X_test, y_train, y_test = _safe_split(X, y)
        scaler = StandardScaler(with_mean=False)
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)
        clf = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
        clf.fit(X_train_s, y_train)
        self.model = clf
        self.scaler = scaler
        preds = clf.predict(X_test_s)
        return {"accuracy": float(accuracy_score(y_test, preds))}

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self.model is None or self.scaler is None:
            raise RuntimeError("Model not trained")
        return self.model.predict(self.scaler.transform(X))


def save_model(obj, path: str) -> None:
    joblib.dump(obj, path)


def load_model(path: str):
    return joblib.load(path)
