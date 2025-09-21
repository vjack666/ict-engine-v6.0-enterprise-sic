#!/usr/bin/env python3
"""
Baseline Pattern Scan
=====================

Runs core pattern detectors to capture baseline signal counts and confidence
before CHoCH-memory integration changes. Outputs a concise JSON report.

Detectors included:
- Silver Bullet Enterprise
- Judas Swing Enterprise
- Liquidity Grab Enterprise
- Order Block Mitigation Enterprise

Usage (PowerShell):
python -X utf8 .\\scripts\\baseline_pattern_scan.py -s AUDUSD -t M5 -n 600 -o .\\04-DATA\\reports

"""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import sys
import os

# Prepare sys.path for local package-style imports
REPO_ROOT = Path(__file__).resolve().parents[1]
CORE_DIR = REPO_ROOT / "01-CORE"
if str(CORE_DIR) not in sys.path:
    sys.path.insert(0, str(CORE_DIR))

# Imports using workspace module layout
_import_error = None
try:
    from data_management.advanced_candle_downloader import AdvancedCandleDownloader  # type: ignore
except Exception as e:
    AdvancedCandleDownloader = None  # type: ignore
    _import_error = e

# Pattern detectors
SilverBulletDetectorEnterprise = None
JudasSwingDetectorEnterprise = None
LiquidityGrabDetectorEnterprise = None
OrderBlockMitigationDetectorEnterprise = None

_detector_import_error = None
try:
    from ict_engine.advanced_patterns.silver_bullet_enterprise import SilverBulletDetectorEnterprise  # type: ignore
    from ict_engine.advanced_patterns.judas_swing_enterprise import JudasSwingDetectorEnterprise  # type: ignore
    from ict_engine.advanced_patterns.liquidity_grab_enterprise import LiquidityGrabDetectorEnterprise  # type: ignore
    from ict_engine.advanced_patterns.order_block_mitigation_enterprise import OrderBlockMitigationDetectorEnterprise  # type: ignore
except Exception as e:
    _detector_import_error = e


def _safe_len(x: Any) -> int:
    try:
        return len(x)
    except Exception:
        return 0


def _optimize_dataframe(df, low_mem: bool):
    try:
        if not low_mem or df is None:
            return df
        use_cols = [c for c in ['open','high','low','close'] if c in getattr(df, 'columns', [])]
        if use_cols:
            df = df[use_cols]
        # downcast numeric to float32
        try:
            df = df.astype('float32')
        except Exception:
            pass
        # keep only a reasonable analysis window
        tail_n = 2000
        try:
            if len(df) > tail_n:
                df = df.tail(tail_n)
        except Exception:
            pass
        return df
    except Exception:
        return df


def run_baseline(symbol: str, timeframe: str, num_candles: int, out_dir: Path, low_mem: bool = False) -> Dict[str, Any]:
    if AdvancedCandleDownloader is None:
        raise RuntimeError(f"Failed to import AdvancedCandleDownloader: {_import_error}")

    downloader = AdvancedCandleDownloader()
    data = downloader.download_ohlc_data(symbol=symbol, timeframe=timeframe, num_candles=num_candles)
    if data is None or getattr(data, 'empty', True):
        raise RuntimeError(f"No data downloaded for {symbol} {timeframe}")
    data = _optimize_dataframe(data, low_mem)

    # Initialize detectors
    sb = SilverBulletDetectorEnterprise() if SilverBulletDetectorEnterprise else None
    js = JudasSwingDetectorEnterprise() if JudasSwingDetectorEnterprise else None
    lg = LiquidityGrabDetectorEnterprise() if LiquidityGrabDetectorEnterprise else None
    ob = OrderBlockMitigationDetectorEnterprise() if OrderBlockMitigationDetectorEnterprise else None

    results: Dict[str, Any] = {
        'meta': {
            'symbol': symbol,
            'timeframe': timeframe,
            'num_candles': int(num_candles),
            'generated_at': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        },
        'detectors': {},
    }

    def record(name: str, signals: List[Any]) -> None:
        if not signals:
            results['detectors'][name] = {
                'count': 0,
                'avg_confidence': 0.0,
                'max_confidence': 0.0,
            }
            return
        confidences = []
        for s in signals:
            c = getattr(s, 'confidence', None)
            if c is None and isinstance(s, dict):
                c = s.get('confidence')
            if c is not None:
                try:
                    confidences.append(float(c))
                except Exception:
                    pass
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        max_conf = max(confidences) if confidences else 0.0
        results['detectors'][name] = {
            'count': _safe_len(signals),
            'avg_confidence': round(avg_conf, 2),
            'max_confidence': round(max_conf, 2),
        }

    # Run each detector safely
    try:
        if sb and hasattr(sb, 'detect_silver_bullet_patterns'):
            sb_signals = sb.detect_silver_bullet_patterns(data=data, symbol=symbol, timeframe=timeframe)
            record('silver_bullet', sb_signals)
    except Exception as e:
        results['detectors']['silver_bullet'] = {'error': str(e)}

    try:
        if js and hasattr(js, 'detect_judas_swing_patterns'):
            js_signals = js.detect_judas_swing_patterns(data=data, symbol=symbol, timeframe=timeframe)
            record('judas_swing', js_signals)
    except Exception as e:
        results['detectors']['judas_swing'] = {'error': str(e)}

    try:
        if lg and hasattr(lg, 'detect_liquidity_grab_patterns'):
            lg_signals = lg.detect_liquidity_grab_patterns(data=data, symbol=symbol, timeframe=timeframe)
            record('liquidity_grab', lg_signals)
    except Exception as e:
        results['detectors']['liquidity_grab'] = {'error': str(e)}

    try:
        if ob and hasattr(ob, 'detect_order_block_mitigation_patterns'):
            ob_signals = ob.detect_order_block_mitigation_patterns(data=data, symbol=symbol, timeframe=timeframe)
            record('order_block_mitigation', ob_signals)
    except Exception as e:
        results['detectors']['order_block_mitigation'] = {'error': str(e)}

    # Save report
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"baseline_{symbol}_{timeframe}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out_path = out_dir / filename
    with out_path.open('w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    results['output_file'] = str(out_path)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description='Run baseline pattern scan and save a JSON report.')
    parser.add_argument('-s', '--symbol', default='AUDUSD', help='Symbol, e.g., AUDUSD')
    parser.add_argument('-t', '--timeframe', default='M5', help='Timeframe, e.g., M5, M15')
    parser.add_argument('-n', '--num-candles', default=600, type=int, help='Number of candles to download')
    parser.add_argument('-o', '--out-dir', default='04-DATA/reports', help='Output folder for the JSON report')
    parser.add_argument('--low-mem', action='store_true', help='Reduce RAM usage (smaller window, float32, minimal columns).')
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    try:
        results = run_baseline(args.symbol, args.timeframe, int(args.num_candles), out_dir, low_mem=bool(args.low_mem))
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(json.dumps({'error': str(e)}, indent=2))
        raise


if __name__ == '__main__':
    main()
