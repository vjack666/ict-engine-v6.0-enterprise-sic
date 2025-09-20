from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def _encode_direction(series: pd.Series) -> pd.Series:
    mapping = {"BULLISH": 1, "BEARISH": -1, "NEUTRAL": 0}
    return series.map(lambda x: mapping.get(str(x).upper(), 0)).astype(int)


def _one_hot_timeframe(series: pd.Series) -> pd.DataFrame:
    tfs = ["M1", "M5", "M15", "H1", "H4", "D1", "W1"]
    out = {f"tf_{tf}": (series.str.upper() == tf).astype(int) for tf in tfs}
    return pd.DataFrame(out, index=series.index)


def _recency_minutes(ts: pd.Series) -> pd.Series:
    now = pd.Timestamp(datetime.now(timezone.utc))
    return (now - pd.to_datetime(ts, utc=True)).dt.total_seconds() / 60.0


def build_feature_matrix(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Build numeric features from CHoCH event DataFrame.

    Returns:
        (X, schema) where X is a DataFrame of features, and schema maps
        feature names to brief descriptions.
    """
    if df is None or df.empty:
        return pd.DataFrame(), {}

    X = pd.DataFrame(index=df.index)

    X["dir_enc"] = _encode_direction(df["direction"].astype(str))
    X["confidence"] = df["confidence"].astype(float).fillna(0.0)
    X["price"] = df["price"].astype(float).fillna(0.0)
    X["break_level"] = df["break_level"].astype(float).fillna(0.0)
    X["target_level"] = df["target_level"].astype(float).fillna(0.0)

    # Relative levels to price
    with np.errstate(divide="ignore", invalid="ignore"):
        X["break_rel"] = np.where(X["price"] != 0, (X["break_level"] - X["price"]) / X["price"], 0.0)
        X["target_rel"] = np.where(X["price"] != 0, (X["target_level"] - X["price"]) / X["price"], 0.0)

    # Time features
    X["recency_min"] = _recency_minutes(df["timestamp"])

    # Timeframe one-hot
    X = pd.concat([X, _one_hot_timeframe(df["timeframe"].astype(str))], axis=1)

    # Rolling aggregates per symbol (if present)
    if "symbol" in df.columns:
        grp = df.groupby("symbol").cumcount()
        X["event_index"] = grp.astype(int)
    else:
        X["event_index"] = np.arange(len(df))

    schema = {
        "dir_enc": "Directional encoding (BULLISH=1, BEARISH=-1, NEUTRAL=0)",
        "confidence": "Reported confidence (0-100)",
        "price": "Event price at detection",
        "break_level": "Break level",
        "target_level": "Target level",
        "break_rel": "(break_level - price)/price",
        "target_rel": "(target_level - price)/price",
        "recency_min": "Minutes since event timestamp",
        "tf_*": "One-hot timeframe flags",
        "event_index": "Sequence index per symbol",
    }

    return X.fillna(0.0), schema
