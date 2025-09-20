from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Any

import numpy as np
import pandas as pd

# Local imports (01-CORE must be on sys.path by caller, as done in CLI)
from analysis.unified_market_memory import get_unified_market_memory
from .dataset import CHoCHDataset
from .features import build_feature_matrix
from .models import load_model as load_sklearn_model


@dataclass
class CHOCHModelService:
    models_dir: Path
    validity_model_path: Path
    direction_model_path: Path
    _validity_model: Optional[Any] = None
    _direction_model: Optional[Any] = None

    @classmethod
    def default(cls) -> "CHOCHModelService":
        root = Path(__file__).resolve().parents[3]
        models = root / "04-DATA" / "models" / "choch"
        return cls(
            models_dir=models,
            validity_model_path=models / "validity_rf.joblib",
            direction_model_path=models / "direction_lr.joblib",
        )

    def ensure_loaded(self) -> None:
        if self._validity_model is None and self.validity_model_path.exists():
            self._validity_model = load_sklearn_model(str(self.validity_model_path))
        if self._direction_model is None and self.direction_model_path.exists():
            self._direction_model = load_sklearn_model(str(self.direction_model_path))

    def predict_for_symbol_tf(self, symbol: str, timeframe: str) -> Dict[str, object]:
        # Make sure memory is available
        mem = get_unified_market_memory()
        mem.restore_unified_memory_state()

        # Load dataset
        ds = CHoCHDataset.from_memory()
        df = ds.df
        if df.empty:
            return {"status": "no-data", "message": "No CHoCH events in memory"}

        # Filter to symbol/tf
        sel = df[(df["symbol"] == symbol) & (df["timeframe"].str.upper() == timeframe.upper())]
        if sel.empty:
            return {"status": "no-data", "message": "No CHoCH for symbol/timeframe"}

        X, _ = build_feature_matrix(sel)
        if X.empty:
            return {"status": "no-data", "message": "Empty features"}

        self.ensure_loaded()
        result: Dict[str, object] = {
            "status": "ok",
            "count": int(len(sel)),
            "symbol": symbol,
            "timeframe": timeframe,
        }

        # Validity
        if self._validity_model is not None and hasattr(self._validity_model, "predict"):
            try:
                pred_valid = self._validity_model.predict(X)
                result["pred_validity"] = getattr(pred_valid, "tolist", lambda: pred_valid)()
            except Exception:
                result["pred_validity"] = []
        else:
            result["pred_validity"] = []

        # Direction
        if self._direction_model is not None and hasattr(self._direction_model, "predict"):
            try:
                pred_dir = self._direction_model.predict(X)
                result["pred_direction"] = getattr(pred_dir, "tolist", lambda: pred_dir)()
            except Exception:
                result["pred_direction"] = []
        else:
            result["pred_direction"] = []

        return result
