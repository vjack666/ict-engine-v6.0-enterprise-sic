import os, sys, json
from datetime import datetime

# Ensure 01-CORE is on path
ROOT = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(WS, '01-CORE'))

from typing import Dict, Any, List

try:
    from analysis.pattern_detector import PatternDetector
    from analysis.unified_market_memory import update_market_memory
except Exception as e:
    print(json.dumps({"error": f"PatternDetector import failed: {e}"}))
    raise

symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF', 'AUDUSD']
timeframes = ['H4', 'M15', 'M5']

pdtr = PatternDetector()

out: Dict[str, Any] = {
    'generated_at': datetime.utcnow().isoformat() + 'Z',
    'timeframes': timeframes,
    'results': {}
}

for sym in symbols:
    try:
        res = pdtr.detect_choch(sym, timeframes=timeframes, mode='live_ready')
        try:
            payload = {
                'pattern_type': 'CHOCH_MULTI_TIMEFRAME',
                'symbol': sym,
                'detected': res.get('detected', False),
                'direction': res.get('direction', 'NEUTRAL'),
                'confidence': res.get('confidence', 0.0),
                'all_signals': res.get('all_signals', []),
                'tf_results': res.get('tf_results', {}),
                'trend_change_confirmed': res.get('trend_change_confirmed', False),
                'execution_summary': res.get('execution_summary', {})
            }
            update_market_memory(payload)
        except Exception as ie:
            pass
        tf_results: Dict[str, Any] = res.get('tf_results', {})
        sym_entry: Dict[str, Any] = {'detected_any': res.get('detected', False), 'by_timeframe': {}}
        for tf in timeframes:
            tf_data = tf_results.get(tf, {})
            detected = tf_data.get('detected', False)
            if detected:
                sym_entry['by_timeframe'][tf] = {
                    'direction': tf_data.get('direction', 'NEUTRAL'),
                    'confidence': tf_data.get('confidence', 0.0),
                    'break_level': tf_data.get('break_level', 0.0),
                    'target_level': tf_data.get('target_level', 0.0)
                }
            else:
                sym_entry['by_timeframe'][tf] = {'detected': False}
        out['results'][sym] = sym_entry
    except Exception as e:
        out['results'][sym] = {'error': str(e)}

print(json.dumps(out, indent=2))
