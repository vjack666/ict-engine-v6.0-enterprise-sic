#!/usr/bin/env python3
from __future__ import annotations
import argparse
import sys
from pathlib import Path

# Ensure 01-CORE is on sys.path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = PROJECT_ROOT / '01-CORE'
if str(CORE_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_PATH))

from memory.choch_historical_memory import get_choch_historical_memory

def main():
    parser = argparse.ArgumentParser(description="Inspect CHoCH historical memory")
    parser.add_argument('--symbol', type=str, default=None)
    parser.add_argument('--timeframe', type=str, default=None)
    parser.add_argument('--level', type=float, default=None, help='Break level for similar retrieval')
    args = parser.parse_args()

    mem = get_choch_historical_memory()
    recs = mem._db.get('records', [])
    print(f"Total CHoCH records: {len(recs)}")

    # Summaries
    if args.symbol:
        by_sym = [r for r in recs if r.get('symbol') == args.symbol]
        print(f"For symbol {args.symbol}: {len(by_sym)} records")
        if args.timeframe:
            by_tf = [r for r in by_sym if r.get('timeframe') == args.timeframe]
            print(f"  In TF {args.timeframe}: {len(by_tf)} records")
            if args.level is not None:
                sims = mem.retrieve_similar(args.symbol, args.timeframe, args.level)
                stats = mem.analyze_success_rate(sims)
                print(f"  Similar near level {args.level}: {stats}")

    # Show last 5
    print("\nLast 5 events:")
    for r in recs[-5:]:
        print(f"- {r.get('timestamp')} {r.get('symbol')} {r.get('timeframe')} {r.get('direction')} conf={r.get('confidence')}")

if __name__ == '__main__':
    main()
