from __future__ import annotations
from typing import Dict, Any
from pathlib import Path
import json

from .features import extract_mss_features
from .model import MSSBaselineModel

class MSSShiftScorer:
    """Service to score MSS probability using a lightweight model.
    If a trained model is available in the future, replace MSSBaselineModel.
    """
    def __init__(self):
        self._model = MSSBaselineModel()
        self._pip_cache: Dict[str, float] = {}

    def _get_pip_value(self, symbol: str) -> float:
        """Obtener pip_value por símbolo desde config; fallback por heurística."""
        key = (symbol or "").upper()
        if key in self._pip_cache:
            return self._pip_cache[key]
        try:
            config_path = Path(__file__).resolve().parents[2] / 'config' / 'trading_symbols_config.json'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                sym_cfg = (cfg.get('symbol_configurations', {}) or {}).get(key)
                if sym_cfg and 'pip_value' in sym_cfg:
                    val = float(sym_cfg['pip_value'])
                    self._pip_cache[key] = val
                    return val
        except Exception:
            pass

        s = key
        if 'JPY' in s or s.endswith('JPY'):
            self._pip_cache[key] = 0.01
            return 0.01
        if s in {"XAUUSD", "GOLD", "XAU"}:
            self._pip_cache[key] = 0.01
            return 0.01
        self._pip_cache[key] = 0.0001
        return 0.0001

    def _ref_pips_by_timeframe(self, timeframe: str) -> float:
        tf = (timeframe or "").upper()
        # Valores de referencia aproximados para ATR medio en pips por TF
        table = {
            'M1': 3.0,
            'M5': 8.0,
            'M15': 20.0,
            'M30': 30.0,
            'H1': 45.0,
            'H2': 60.0,
            'H3': 80.0,
            'H4': 100.0,
            'H6': 140.0,
            'H8': 180.0,
            'H12': 220.0,
            'D1': 150.0,
            'W1': 350.0,
            'MN1': 800.0,
        }
        return table.get(tf, 20.0)

    def score(self, window, symbol: str = "EURUSD", timeframe: str = "M15") -> Dict[str, Any]:
        feats = extract_mss_features(window)
        p = float(self._model.predict_proba(feats))
        # Confidence normalizado por símbolo/TF: volatilidad relativa a N pips del TF
        pip = self._get_pip_value(symbol)
        ref_pips = self._ref_pips_by_timeframe(timeframe)
        denom = max(pip * ref_pips, 1e-9)
        vol_component = min(1.0, feats.get('volatility', 0.0) / denom)
        body_component = min(1.0, feats.get('body_ratio', 0.0))
        conf = 0.5 * vol_component + 0.5 * body_component
        return {
            'prob_shift': p,
            'confidence': float(conf),
            'features': feats,
            'symbol': symbol,
            'timeframe': timeframe,
        }
