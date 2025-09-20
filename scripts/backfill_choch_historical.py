#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = PROJECT_ROOT / '01-CORE'
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

from memory.choch_historical_memory import get_choch_historical_memory

STATE_FILE = PROJECT_ROOT / '04-DATA' / 'memory_persistence' / 'market_context_state.json'

def parse_dt(value):
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)
    if isinstance(value, str):
        try:
            iso = value.replace('Z', '+00:00') if 'Z' in value and '+' not in value else value
            dt = datetime.fromisoformat(iso)
            return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)
    return datetime.now(timezone.utc)

def main():
    if not STATE_FILE.exists():
        print(f"No state file found at {STATE_FILE}")
        return
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    pm = state.get('pattern_memory', {})
    choch_events = pm.get('choch_events', []) or []
    if not choch_events:
        print("No CHoCH events found to backfill.")
        return
    mem = get_choch_historical_memory()
    imported = 0
    for ev in choch_events:
        try:
            data = ev.get('data', {})
            ts = parse_dt(ev.get('timestamp'))
            symbol = data.get('symbol') or state.get('market_context', {}).get('last_symbol') or 'UNKNOWN'
            timeframe = data.get('timeframe', 'UNKNOWN')
            direction = data.get('direction', 'NEUTRAL')
            break_level = float(data.get('break_level', 0.0) or 0.0)
            target_level = float(data.get('target_level', 0.0) or 0.0)
            confidence = float(data.get('confidence', 0.0) or 0.0)
            mem.store_from_detection(symbol=symbol,
                                     timeframe=timeframe,
                                     timestamp=ts,
                                     direction=direction,
                                     break_level=break_level,
                                     target_level=target_level,
                                     confidence=confidence,
                                     context=(data.get('metadata') if isinstance(data.get('metadata'), dict) else {}))
            imported += 1
        except Exception:
            # skip bad event
            pass
    print(f"Imported {imported} CHoCH events into historical memory")

if __name__ == '__main__':
    main()
