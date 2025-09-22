from __future__ import annotations
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Lightweight, dependency-free persistent store for CHoCH historical events.
# JSON schema adheres to user's spec with extras for analytics bookkeeping.

# 🚀 Import cache system for performance optimization
try:
    from memory.choch_cache import get_choch_cache
    _cache_available = True
except ImportError:
    _cache_available = False

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
        
        # 🧠 LOW-MEM MODE: Reduce memory footprint when ICT_LOW_MEM is set
        self.low_mem_mode = bool(os.environ.get('ICT_LOW_MEM'))
        
        # 🧪 Test optimization modes from validation tests
        self.quick_test_mode = bool(os.environ.get('ICT_QUICK_TEST_MODE', '0') == '1')
        self.disable_heavy_init = bool(os.environ.get('ICT_DISABLE_HEAVY_INIT', '0') == '1')
        
        if self.low_mem_mode or self.quick_test_mode:
            # Reduce max records and retention for memory/speed optimization
            if self.quick_test_mode:
                self.max_records = min(max_records, 50)  # Mínimo para tests rápidos
                self.retention_days = min(retention_days, 7)  # Una semana para tests
            else:
                self.max_records = min(max_records, 200)  # Low-mem standard
                self.retention_days = min(retention_days, 30)  # Un mes para low-mem
            print(f"[INFO] 🧠 CHoCH Memory: Optimized mode - {self.max_records} max records, {self.retention_days} day retention")
        else:
            self.max_records = max_records
            
        self._db: Dict[str, Any] = {
            'metadata': {
                'version': 'v1',
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'retention_days': self.retention_days,
                'max_records': self.max_records,
                'low_mem_mode': self.low_mem_mode,
                'quick_test_mode': self.quick_test_mode,
                'disable_heavy_init': self.disable_heavy_init,
            },
            'records': []  # List[CHoCHEvent dicts]
        }
        
        # Skip loading/saving in quick test mode for speed
        if not self.quick_test_mode:
            self._load()
        else:
            # En test rápido, solo crear directorios si no existen
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)

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
        # Skip saving in quick test mode for speed
        if self.quick_test_mode:
            return
            
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self._db, f, indent=2)
        
        # best-effort backup (skip in test modes)
        if not (self.disable_heavy_init or self.low_mem_mode):
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
        # 🚀 Try cache first for performance optimization
        if _cache_available:
            cache = get_choch_cache()
            cached_result = cache.get_historical_bonus(symbol, timeframe, break_level)
            if cached_result is not None:
                return cached_result
        
        # Compute bonus if not cached
        sims = self.retrieve_similar(symbol, timeframe, break_level, session=session, volatility_band=volatility_band)
        stats = self.analyze_success_rate(sims)
        samples = int(stats.get('count', 0) or 0)
        if samples < 3:
            result = {"historical_bonus": 0.0, "samples": samples}
        else:
            success_rate = stats.get('success_rate', 0.0)
            # Map success rate [0,100] to bonus [-20,+20]
            bonus = (success_rate - 50.0) * 0.4  # 0.4 => 50% -> 0; 100% -> +20; 0% -> -20
            result = {"historical_bonus": max(-20.0, min(20.0, bonus)), "samples": samples}
        
        # Store in cache for future queries
        if _cache_available:
            cache.set_historical_bonus(symbol, timeframe, break_level, result)
        
        return result

    # === Smart retrieval & analysis APIs ===
    def find_similar_choch_in_history(self, symbol: str, timeframe: str, direction: Optional[str] = None,
                                      break_level_range: Optional[Tuple[float, float]] = None) -> List[Dict[str, Any]]:
        results = []
        for r in self._db.get('records', []):
            if r.get('symbol') != symbol or r.get('timeframe') != timeframe:
                continue
            if direction and r.get('direction') != direction:
                continue
            if break_level_range is not None:
                try:
                    br = float(r.get('break_level', 0.0))
                    if not (break_level_range[0] <= br <= break_level_range[1]):
                        continue
                except Exception:
                    continue
            results.append(r)
        return results

    def calculate_historical_success_rate(self, symbol: str, timeframe: str, direction: Optional[str] = None) -> float:
        # 🚀 Try cache first
        if _cache_available and direction is None:  # Only cache general success rates
            cache = get_choch_cache()
            cached_rate = cache.get_success_rate(symbol, timeframe)
            if cached_rate is not None:
                return cached_rate
        
        # Compute if not cached
        events = [r for r in self._db.get('records', []) if r.get('symbol') == symbol and r.get('timeframe') == timeframe and (direction is None or r.get('direction') == direction)]
        stats = self.analyze_success_rate(events)
        success_rate = float(stats.get('success_rate', 0.0))
        
        # Store in cache (only for general rates)
        if _cache_available and direction is None:
            cache.set_success_rate(symbol, timeframe, success_rate)
        
        return success_rate

    def adjust_confidence_with_memory(self, base_confidence: float, symbol: str, timeframe: str, break_level: float) -> float:
        try:
            hb = self.compute_historical_bonus(symbol, timeframe, break_level)
            bonus = hb.get('historical_bonus', 0.0)
            # base_confidence assumed 0-100; clamp after bonus
            return max(0.0, min(100.0, float(base_confidence) + float(bonus)))
        except Exception:
            return float(base_confidence)

    def predict_target_based_on_history(self, symbol: str, timeframe: str, direction: str, break_level: float,
                                        default_target: Optional[float] = None) -> Optional[float]:
        sims = self.retrieve_similar(symbol, timeframe, break_level)
        sims = [s for s in sims if s.get('direction') == direction]
        if not sims:
            return default_target
        # Average target level of similar events
        targets: List[float] = []
        for s in sims:
            val = s.get('target_level')
            if val is None:
                continue
            try:
                targets.append(float(val))
            except Exception:
                continue
        if not targets:
            return default_target
        return sum(targets) / len(targets)

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

def find_similar_choch_in_history(symbol: str, timeframe: str, direction: Optional[str] = None, break_level_range: Optional[Tuple[float,float]] = None) -> List[Dict[str, Any]]:
    mem = get_choch_historical_memory()
    return mem.find_similar_choch_in_history(symbol, timeframe, direction, break_level_range)

def calculate_historical_success_rate(symbol: str, timeframe: str, direction: Optional[str] = None) -> float:
    mem = get_choch_historical_memory()
    return mem.calculate_historical_success_rate(symbol, timeframe, direction)

def adjust_confidence_with_memory(base_confidence: float, symbol: str, timeframe: str, break_level: float) -> float:
    mem = get_choch_historical_memory()
    return mem.adjust_confidence_with_memory(base_confidence, symbol, timeframe, break_level)

def predict_target_based_on_history(symbol: str, timeframe: str, direction: str, break_level: float, default_target: Optional[float] = None) -> Optional[float]:
    mem = get_choch_historical_memory()
    return mem.predict_target_based_on_history(symbol, timeframe, direction, break_level, default_target)

def update_choch_outcome(event_id: str, outcome: str, pips_moved: Optional[float] = None, time_to_target: Optional[str] = None) -> bool:
    mem = get_choch_historical_memory()
    return mem.update_outcome(event_id, outcome, pips_moved, time_to_target)
