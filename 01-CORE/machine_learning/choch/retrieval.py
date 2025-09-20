from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from .dataset import CHoCHDataset


def get_recent_choch(
    symbol: Optional[str] = None,
    timeframe: Optional[str] = None,
    within_minutes: int = 240,
    memory_dir: Optional[Path | str] = None,
) -> pd.DataFrame:
    ds = CHoCHDataset.from_memory(memory_dir)
    df = ds.df
    if df.empty:
        return df
    if symbol:
        df = df[df["symbol"] == symbol]
    if timeframe:
        df = df[df["timeframe"].str.upper() == timeframe.upper()]
    cutoff = pd.Timestamp(datetime.now(timezone.utc)) - pd.Timedelta(minutes=within_minutes)
    return df[df["timestamp"] >= cutoff].sort_values("timestamp")


def find_historical_choch(
    symbol: Optional[str] = None,
    timeframes: Optional[List[str]] = None,
    min_confidence: float = 60.0,
    memory_dir: Optional[Path | str] = None,
) -> pd.DataFrame:
    ds = CHoCHDataset.from_memory(memory_dir)
    ds = ds.filter(symbol=symbol, timeframes=timeframes, min_confidence=min_confidence)
    return ds.df


def get_choch_by_symbol_timeframe(
    symbol: str,
    timeframe: str,
    limit: int = 50,
    memory_dir: Optional[Path | str] = None,
) -> pd.DataFrame:
    ds = CHoCHDataset.from_memory(memory_dir)
    df = ds.df
    if df.empty:
        return df
    df = df[(df["symbol"] == symbol) & (df["timeframe"].str.upper() == timeframe.upper())]
    return df.sort_values("timestamp").tail(limit).reset_index(drop=True)
