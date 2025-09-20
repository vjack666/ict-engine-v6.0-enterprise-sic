#!/usr/bin/env python3
"""
Backfill CHoCH events into Unified Market Memory using historical scans.

- Scans a configurable list of symbols and timeframes
- Uses PatternDetector to detect CHoCH per timeframe (historical window)
- Persists each detected signal into unified memory with proper timestamp
"""

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

import sys

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "01-CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from analysis.pattern_detector import PatternDetector
from analysis.unified_market_memory import update_market_memory


def backfill(symbols: List[str], timeframes: List[str], days: int) -> int:
    detector = PatternDetector()
    total = 0
    for symbol in symbols:
        print(f"\n🔎 Backfilling CHoCH for {symbol} on {timeframes} (days={days})")
        for tf in timeframes:
            # Force a per-TF scan by calling the single-TF path indirectly via detect_choch
            # detect_choch accepts a list; we'll pass [tf] to constrain
            result = detector.detect_choch(symbol, timeframes=[tf], mode='full')
            if not result or not result.get('detected'):
                print(f"   ⚪ No CHoCH for {symbol} {tf}")
                continue

            # Persist all signals found for this TF with timestamps if provided
            all_signals = result.get('all_signals', [])
            tf_results = result.get('tf_results') or result.get('analysis') or {}
            # try to enrich timestamp from tf_results if available
            enriched_signals: List[Dict[str, Any]] = []
            for sig in all_signals:
                ts = None
                try:
                    tf_detail = tf_results.get(sig.get('timeframe')) if isinstance(tf_results, dict) else None
                    if isinstance(tf_detail, dict):
                        ts = tf_detail.get('timestamp') or tf_detail.get('last_timestamp')
                except Exception:
                    ts = None
                s = dict(sig)
                if ts is not None and 'timestamp' not in s:
                    s['timestamp'] = ts
                enriched_signals.append(s)

            payload = {
                'pattern_type': 'CHOCH_MULTI_TIMEFRAME',
                'symbol': symbol,
                'detected': True,
                'direction': result.get('direction'),
                'confidence': result.get('confidence', 0.0),
                'all_signals': enriched_signals or all_signals,
                'tf_results': tf_results,
                'trend_change_confirmed': result.get('trend_change_confirmed', False),
                'execution_summary': result.get('execution_summary', {}),
                # Historical context marker
                'metadata': {'source': 'CHOCH_BACKFILL'}
            }
            update_market_memory(payload)
            added = len(enriched_signals or all_signals)
            total += added
            print(f"   ✅ Persisted {added} CHoCH signal(s) for {symbol} {tf}")
    return total


def main():
    parser = argparse.ArgumentParser(description="Backfill CHoCH events into unified memory")
    parser.add_argument("--symbols", nargs="*", default=["EURUSD", "GBPUSD", "USDCAD", "AUDUSD"], help="Symbols to scan")
    parser.add_argument("--timeframes", nargs="*", default=["H4", "H1", "M15", "M5"], help="Timeframes to scan")
    parser.add_argument("--days", type=int, default=30, help="Historical days per primary TF to analyze")
    args = parser.parse_args()

    count = backfill(args.symbols, args.timeframes, args.days)
    print(f"\n✅ Backfill complete. Persisted {count} CHoCH signals.")


if __name__ == "__main__":
    main()
