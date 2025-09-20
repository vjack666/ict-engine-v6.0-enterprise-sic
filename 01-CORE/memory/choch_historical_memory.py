from __future__ import annotations
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Lightweight, dependency-free persistent store for CHoCH historical events.
# JSON schema adheres to user's spec with extras for analytics bookkeeping.

DEFAULT_STORAGE = Path(__file__).resolve().parent / 'choch_historical.json'
DEFAULT_BACKUP = Path(__file__).resolve().parents[2] / '04-DATA' / 'cache' / 'choch_backup.json'

RETENTION_DAYS_DEFAULT = 180
MAX_RECORDS_DEFAULT = 1000

@dataclass
class CHoCHEvent:
    id: str
    symbol: str
    timeframe: str
    timestamp: str  # ISO8601
    direction: str  # BULLISH | BEARISH
    break_level: float
    target_level: float
    stop_level: Optional[float] = None
    confidence: float = 0.0
    price_at_break: Optional[float] = None
    session: Optional[str] = None
    volatility: Optional[float] = None
    trend_strength: Optional[float] = None
    outcome: str = 'PENDING'  # PENDING | SUCCESS | FAILED
    pips_moved: Optional[float] = None
    time_to_target: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class CHoCHHistoricalMemory:
    def __init__(self,
                 storage_path: Path = DEFAULT_STORAGE,
                 backup_path: Path = DEFAULT_BACKUP,
                 retention_days: int = RETENTION_DAYS_DEFAULT,
                 max_records: int = MAX_RECORDS_DEFAULT):
        self.storage_path = Path(storage_path)
        self.backup_path = Path(backup_path)
        self.retention_days = retention_days
        self.max_records = max_records
        self._db: Dict[str, Any] = {
            'metadata': {
                'version': 'v1',
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'retention_days': retention_days,
                'max_records': max_records,
            },
            'records': []  # List[CHoCHEvent dicts]
        }
        self._load()

    # ---------- Core persistence ----------
    def _load(self) -> None:
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self._db = json.load(f)
        except Exception:
            # If load fails, keep empty db but ensure dirs exist
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self._db, f, indent=2)
        # best-effort backup
        try:
            self.backup_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.backup_path, 'w', encoding='utf-8') as b:
                json.dump(self._db, b, indent=2)
        except Exception:
            pass

    # ---------- Helpers ----------
    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _gen_id(self, symbol: str, timeframe: str, ts: str) -> str:
        return f"CHOCH_{symbol}_{timeframe}_{ts.replace(':','').replace('-','').replace('+','').replace('Z','')}"

    def _pip(self, symbol: str) -> float:
        return 0.01 if symbol.upper().endswith('JPY') else 0.0001

    # ---------- Public API ----------
    def store(self, event: CHoCHEvent) -> CHoCHEvent:
        recs: List[Dict[str, Any]] = self._db.get('records', [])
        recs.append(asdict(event))
        # retention + cap
        cutoff = self._now() - timedelta(days=self.retention_days)
        def _parse_ts(d: Dict[str, Any]) -> datetime:
            try:
                ts = d.get('timestamp')
                if not ts:
                    return self._now()
                return datetime.fromisoformat(str(ts).replace('Z','+00:00'))
            except Exception:
                return self._now()
        recs = [r for r in recs if _parse_ts(r) >= cutoff]
        if len(recs) > self.max_records:
            recs = recs[-self.max_records:]
        self._db['records'] = recs
        self._db['metadata']['last_updated'] = self._now().isoformat()
        self._save()
        return event

    def store_from_detection(self,
                             symbol: str,
                             timeframe: str,
                             timestamp: Any,
                             direction: str,
                             break_level: float,
                             target_level: float,
                             confidence: float,
                             stop_level: Optional[float] = None,
                             session: Optional[str] = None,
                             volatility: Optional[float] = None,
                             trend_strength: Optional[float] = None,
                             context: Optional[Dict[str, Any]] = None) -> CHoCHEvent:
        # normalize timestamp
        if isinstance(timestamp, datetime):
            ts_iso = timestamp.astimezone(timezone.utc).isoformat()
        else:
            try:
                ts_iso = datetime.fromisoformat(str(timestamp).replace('Z','+00:00')).astimezone(timezone.utc).isoformat()
            except Exception:
                ts_iso = self._now().isoformat()
        ev_id = self._gen_id(symbol, timeframe, ts_iso)
        event = CHoCHEvent(
            id=ev_id,
            symbol=symbol,
            timeframe=timeframe,
            timestamp=ts_iso,
            direction=direction,
            break_level=float(break_level),
            target_level=float(target_level),
            stop_level=float(stop_level) if stop_level is not None else None,
            confidence=float(confidence),
            context=context or {},
            session=session,
            volatility=volatility,
            trend_strength=trend_strength,
        )
        return self.store(event)

    def retrieve_similar(self,
                          symbol: str,
                          timeframe: str,
                          break_level: float,
                          level_tolerance_pips: float = 50.0,
                          session: Optional[str] = None,
                          volatility_band: Optional[Tuple[float,float]] = None) -> List[Dict[str, Any]]:
        pip = self._pip(symbol)
        tol = level_tolerance_pips * pip
        results = []
        for r in self._db.get('records', []):
            if r.get('symbol') != symbol or r.get('timeframe') != timeframe:
                continue
            if abs(float(r.get('break_level', 0.0)) - float(break_level)) > tol:
                continue
            if session and r.get('session') and r.get('session') != session:
                continue
            if volatility_band and r.get('volatility') is not None:
                v = float(r.get('volatility'))
                lo, hi = volatility_band
                if not (lo <= v <= hi):
                    continue
            results.append(r)
        return results

    def analyze_success_rate(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not events:
            return {"count": 0, "success_rate": 0.0, "avg_pips": 0.0, "avg_time_to_target_hours": None}
        labeled = [e for e in events if str(e.get('outcome')) in ('SUCCESS','FAILED')]
        if not labeled:
            return {"count": 0, "success_rate": 0.0, "avg_pips": 0.0, "avg_time_to_target_hours": None}
        total = len(labeled)
        succ = sum(1 for e in labeled if e.get('outcome') == 'SUCCESS')
        pips_vals = [float(e.get('pips_moved', 0) or 0) for e in labeled if e.get('pips_moved') is not None]
        avg_pips = sum(pips_vals) / len(pips_vals) if pips_vals else 0.0
        # parse time_to_target in naive hours if provided like "8 hours"
        hours = []
        for e in labeled:
            t = e.get('time_to_target')
            if isinstance(t, str) and 'hour' in t:
                try:
                    hours.append(float(t.split()[0]))
                except Exception:
                    pass
        avg_hours = sum(hours) / len(hours) if hours else None
        return {"count": total, "success_rate": (succ/total)*100.0, "avg_pips": avg_pips, "avg_time_to_target_hours": avg_hours}

    def compute_historical_bonus(self, symbol: str, timeframe: str, break_level: float,
                                 session: Optional[str] = None, volatility_band: Optional[Tuple[float,float]] = None) -> Dict[str, float]:
        sims = self.retrieve_similar(symbol, timeframe, break_level, session=session, volatility_band=volatility_band)
        stats = self.analyze_success_rate(sims)
        samples = int(stats.get('count', 0) or 0)
        if samples < 3:
            return {"historical_bonus": 0.0, "samples": samples}
        success_rate = stats.get('success_rate', 0.0)
        # Map success rate [0,100] to bonus [-20,+20]
        bonus = (success_rate - 50.0) * 0.4  # 0.4 => 50% -> 0; 100% -> +20; 0% -> -20
        return {"historical_bonus": max(-20.0, min(20.0, bonus)), "samples": samples}

    def update_outcome(self, event_id: str, outcome: str, pips_moved: Optional[float] = None, time_to_target: Optional[str] = None) -> bool:
        recs = self._db.get('records', [])
        for r in recs:
            if r.get('id') == event_id:
                r['outcome'] = outcome
                if pips_moved is not None:
                    r['pips_moved'] = float(pips_moved)
                if time_to_target is not None:
                    r['time_to_target'] = str(time_to_target)
                self._db['metadata']['last_updated'] = self._now().isoformat()
                self._save()
                return True
        return False

    def clean(self) -> None:
        # Enforce retention and cap
        cutoff = self._now() - timedelta(days=self.retention_days)
        def _parse_ts(d: Dict[str, Any]) -> datetime:
            try:
                ts = d.get('timestamp')
                if not ts:
                    return self._now()
                return datetime.fromisoformat(str(ts).replace('Z','+00:00'))
            except Exception:
                return self._now()
        recs = [r for r in self._db.get('records', []) if _parse_ts(r) >= cutoff]
        if len(recs) > self.max_records:
            recs = recs[-self.max_records:]
        self._db['records'] = recs
        self._db['metadata']['last_updated'] = self._now().isoformat()
        self._save()

# Convenience singleton
_memory_instance: Optional[CHoCHHistoricalMemory] = None

def get_choch_historical_memory() -> CHoCHHistoricalMemory:
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = CHoCHHistoricalMemory()
    return _memory_instance

# Thin helpers for external modules

def store_choch_event(**kwargs) -> CHoCHEvent:
    mem = get_choch_historical_memory()
    return mem.store_from_detection(**kwargs)

def retrieve_similar_choch(**kwargs) -> List[Dict[str, Any]]:
    mem = get_choch_historical_memory()
    return mem.retrieve_similar(**kwargs)

def compute_historical_bonus(**kwargs) -> Dict[str, float]:
    mem = get_choch_historical_memory()
    return mem.compute_historical_bonus(**kwargs)

def update_choch_outcome(event_id: str, outcome: str, pips_moved: Optional[float] = None, time_to_target: Optional[str] = None) -> bool:
    mem = get_choch_historical_memory()
    return mem.update_outcome(event_id, outcome, pips_moved, time_to_target)
