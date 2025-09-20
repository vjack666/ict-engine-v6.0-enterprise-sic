from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _default_memory_dir() -> Path:
    # MarketContextV6 persists to 04-DATA/memory_persistence/market_context_state.json
    return _project_root() / "04-DATA" / "memory_persistence"


def _safe_to_datetime(val: Any) -> datetime:
    if isinstance(val, datetime):
        return val if val.tzinfo else val.replace(tzinfo=timezone.utc)
    if isinstance(val, (int, float)):
        return datetime.fromtimestamp(float(val), tz=timezone.utc)
    if isinstance(val, str):
        try:
            iso = val.replace("Z", "+00:00")
            dt = datetime.fromisoformat(iso)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)
    return datetime.now(timezone.utc)


def _iter_memory_files(directory: Path) -> Iterable[Path]:
    # Primary file name used by MarketContextV6
    main = directory / "market_context_state.json"
    if main.exists():
        yield main
    # Any additional snapshots
    for p in sorted(directory.glob("*.json")):
        if p.name == "market_context_state.json":
            continue
        yield p


def _extract_choch_events(memory_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    pm = memory_json.get("pattern_memory", {}) if isinstance(memory_json, dict) else {}
    events = pm.get("choch_events", []) or []
    out: List[Dict[str, Any]] = []
    for ev in events:
        try:
            if not isinstance(ev, dict):
                continue
            ts = _safe_to_datetime(ev.get("timestamp"))
            price = float(ev.get("price", 0.0) or 0.0)
            data = ev.get("data", {}) if isinstance(ev.get("data"), dict) else {}
            direction = str(data.get("direction", "NEUTRAL")).upper()
            confidence = float(data.get("confidence", 0.0) or 0.0)
            timeframe = str(data.get("timeframe", "UNKNOWN")).upper()
            break_level = float(data.get("break_level", price) or price)
            target_level = float(data.get("target_level", price) or price)
            symbol = data.get("symbol")
            out.append(
                {
                    "timestamp": ts,
                    "price": price,
                    "direction": direction,
                    "confidence": confidence,
                    "timeframe": timeframe,
                    "break_level": break_level,
                    "target_level": target_level,
                    "symbol": symbol,
                }
            )
        except Exception:
            # Skip malformed
            continue
    return out


def load_choch_dataframe(memory_dir: Optional[Path | str] = None) -> pd.DataFrame:
    directory = Path(memory_dir) if memory_dir else _default_memory_dir()
    records: List[Dict[str, Any]] = []
    for file in _iter_memory_files(directory):
        try:
            with open(file, "r", encoding="utf-8") as f:
                js = json.load(f)
            records.extend(_extract_choch_events(js))
        except Exception:
            continue

    if not records:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "price",
                "direction",
                "confidence",
                "timeframe",
                "break_level",
                "target_level",
                "symbol",
            ]
        )

    df = pd.DataFrame.from_records(records)
    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


@dataclass
class CHoCHDataset:
    df: pd.DataFrame

    @classmethod
    def from_memory(cls, memory_dir: Optional[Path | str] = None) -> "CHoCHDataset":
        return cls(load_choch_dataframe(memory_dir))

    def filter(
        self,
        symbol: Optional[str] = None,
        timeframes: Optional[List[str]] = None,
        min_confidence: Optional[float] = None,
    ) -> "CHoCHDataset":
        data = self.df.copy()
        if symbol:
            data = data[data["symbol"] == symbol]
        if timeframes:
            tfs = [tf.upper() for tf in timeframes]
            data = data[data["timeframe"].isin(tfs)]
        if min_confidence is not None:
            data = data[data["confidence"] >= float(min_confidence)]
        return CHoCHDataset(data.reset_index(drop=True))
