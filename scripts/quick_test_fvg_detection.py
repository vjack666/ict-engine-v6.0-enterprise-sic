#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick FVG Detection Test
- Downloads candles
- Invokes ICTPatternDetector._detect_fvg_patterns()
- Prints a concise summary and sample entries
"""
from __future__ import annotations
import argparse
from pathlib import Path
from typing import Any
from datetime import datetime, timezone

import sys
BASE = Path(__file__).resolve().parent.parent
CORE = BASE / '01-CORE'
for p in (BASE, CORE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from protocols.unified_logging import get_unified_logger  # type: ignore


def load_candles(symbol: str, timeframe: str, n: int) -> Any:
    try:
        from data_management.advanced_candle_downloader import AdvancedCandleDownloader  # type: ignore
        dl = AdvancedCandleDownloader()
        df = dl.download_ohlc_data(symbol=symbol, timeframe=timeframe, num_candles=n)
        if df is None:
            raise RuntimeError("No se obtuvieron velas (df=None)")
        return df.tail(n)
    except Exception as e:
        logger = get_unified_logger("QuickFVGTest")
        logger.error(f"No se pudieron cargar velas: {e}", "DATA")
        raise


def detect_fvg(symbol: str, timeframe: str, n: int, placeholders: bool = False):
    from ict_engine.pattern_detector import ICTPatternDetector  # type: ignore

    config = {
        'symbol': symbol,
        'allow_fvg_placeholder_for_tests': placeholders,
        'enable_fvg_memory_persistence': False,
    }
    det = ICTPatternDetector(config=config)

    df = load_candles(symbol, timeframe, n)
    patterns = det._detect_fvg_patterns(df, timeframe)

    return patterns


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--symbol', default='AUDUSD')
    parser.add_argument('-t', '--timeframe', default='M5')
    parser.add_argument('-n', '--num', type=int, default=600)
    parser.add_argument('--placeholders', action='store_true')
    args = parser.parse_args()

    patterns = detect_fvg(args.symbol, args.timeframe, args.num, args.placeholders)
    logger = get_unified_logger("QuickFVGTest")

    def _fmt(p):
        md = p.metadata or {}
        return {
            'symbol': p.symbol,
            'tf': p.timeframe,
            'entry': round(float(p.entry_price), 6),
            'conf': round(float(p.confidence), 3),
            'dir': md.get('direction'),
            'gap_pips': md.get('gap_pips'),
            'fill%': md.get('fill_percentage'),
            'choch_bonus': md.get('choch_historical_bonus'),
            'choch_samples': md.get('choch_samples'),
            'status': md.get('status'),
            'id': md.get('fvg_id'),
            'ts': getattr(p.timestamp, 'isoformat', lambda: str(p.timestamp))(),
        }

    total = len(patterns)
    boosted = sum(1 for p in patterns if (p.metadata or {}).get('choch_historical_bonus'))
    print("\n=== FVG DETECTION SUMMARY ===")
    print(f"symbol={args.symbol} timeframe={args.timeframe} candles={args.num}")
    print(f"patterns={total} choch_boosted={boosted}")

    for idx, p in enumerate(patterns[:5]):
        print(f"{idx+1:02d}", _fmt(p))

    out_dir = BASE / '04-DATA' / 'reports'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"quick_fvg_{args.symbol}_{args.timeframe}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    try:
        import json
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump([_fmt(p) for p in patterns], f, ensure_ascii=False, indent=2)
        print(f"Saved: {out_file}")
    except Exception as e:
        logger.error(f"No se pudo guardar el reporte: {e}", "IO")


if __name__ == '__main__':
    main()
