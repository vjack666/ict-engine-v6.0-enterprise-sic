import os, sys, json
from datetime import datetime

# Ensure 01-CORE is on path
ROOT = os.path.dirname(os.path.abspath(__file__))
WS = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(WS, '01-CORE'))

from analysis.unified_market_memory import (
    get_last_choch_for_trading,
    get_choch_trading_levels,
)

pairs = [
    'EURUSD', 'USDCAD', 'USDCHF', 'AUDUSD'
]

timeframes = ['W1', 'D1', 'H4', 'H1', 'M15', 'M5']

summary = {
    'generated_at': datetime.utcnow().isoformat() + 'Z',
    'pairs': {},
}

for sym in pairs:
    sym_data = {'overall': None, 'by_timeframe': {}}
    try:
        overall = get_last_choch_for_trading(sym)
        sym_data['overall'] = overall
    except Exception as e:
        sym_data['overall_error'] = str(e)
    for tf in timeframes:
        try:
            last_tf = get_last_choch_for_trading(sym, timeframe=tf)
            levels = get_choch_trading_levels(sym, timeframe=tf)
            sym_data['by_timeframe'][tf] = {
                'last_choch': last_tf,
                'levels': levels,
            }
        except Exception as e:
            sym_data['by_timeframe'][tf] = {'error': str(e)}
    summary['pairs'][sym] = sym_data

print(json.dumps(summary, default=str, indent=2))
