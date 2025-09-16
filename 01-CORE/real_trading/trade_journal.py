"""Trade Journal
===============
Registro estructurado de operaciones para auditoría y análisis de performance.
"""
from __future__ import annotations
from protocols.unified_logging import get_unified_logger
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import csv
import json
from pathlib import Path


@dataclass
class JournalEntry:
    timestamp: datetime
    symbol: str
    direction: str
    volume: float
    entry_price: float
    exit_price: Optional[float]
    pnl: Optional[float]
    strategy: str
    tags: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)


class TradeJournal:
    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.base_dir = base_dir or Path("05-LOGS") / "trading" / "journal"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._entries: list[JournalEntry] = []

    def record_open(self, symbol: str, direction: str, volume: float, entry_price: float,
                    strategy: str, tags: Optional[List[str]] = None, meta: Optional[Dict[str, Any]] = None) -> JournalEntry:
        entry = JournalEntry(
            timestamp=datetime.now(timezone.utc),
            symbol=symbol,
            direction=direction,
            volume=volume,
            entry_price=entry_price,
            exit_price=None,
            pnl=None,
            strategy=strategy,
            tags=tags or [],
            meta=meta or {}
        )
        self._entries.append(entry)
        return entry

    def record_close(self, entry: JournalEntry, exit_price: float) -> None:
        entry.exit_price = exit_price
        if entry.direction.lower() == "buy":
            entry.pnl = (exit_price - entry.entry_price) * entry.volume
        else:
            entry.pnl = (entry.entry_price - exit_price) * entry.volume

    def export_csv(self, filename: Optional[str] = None) -> Path:
        filename = filename or f"journal_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        path = self.base_dir / filename
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "symbol", "direction", "volume", "entry_price", "exit_price", "pnl", "strategy", "tags", "meta"])
            for e in self._entries:
                writer.writerow([
                    e.timestamp.isoformat(), e.symbol, e.direction, e.volume,
                    e.entry_price, e.exit_price if e.exit_price is not None else "",
                    e.pnl if e.pnl is not None else "", e.strategy,
                    ";".join(e.tags), json.dumps(e.meta)
                ])
        return path

    def export_json(self, filename: Optional[str] = None) -> Path:
        filename = filename or f"journal_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        path = self.base_dir / filename
        data = []
        for e in self._entries:
            data.append({
                "timestamp": e.timestamp.isoformat(),
                "symbol": e.symbol,
                "direction": e.direction,
                "volume": e.volume,
                "entry_price": e.entry_price,
                "exit_price": e.exit_price,
                "pnl": e.pnl,
                "strategy": e.strategy,
                "tags": e.tags,
                "meta": e.meta
            })
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return path

    def get_open_positions(self) -> List[JournalEntry]:
        return [e for e in self._entries if e.exit_price is None]

    def get_all(self) -> List[JournalEntry]:
        return list(self._entries)


__all__ = ["TradeJournal", "JournalEntry"]
