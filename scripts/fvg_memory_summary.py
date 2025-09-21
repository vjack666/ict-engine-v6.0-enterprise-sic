#!/usr/bin/env python3
"""
Quick FVG Memory Summary CLI
----------------------------
Prints counts per symbol/timeframe and shows the latest active FVGs.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CORE = ROOT / "01-CORE"
sys.path.insert(0, str(CORE))

def main():
    try:
        from analysis.fvg_memory_manager import FVGMemoryManager  # type: ignore
    except Exception as e:
        print(f"Failed to import FVGMemoryManager: {e}")
        sys.exit(1)

    mgr = FVGMemoryManager()
    data = mgr.fvg_data
    db = data.get("fvg_database", {})
    print("=== FVG Memory Summary ===")
    total = 0
    for sym, tfs in db.items():
        if not isinstance(tfs, dict):
            continue
        print(f"\nSymbol: {sym}")
        for tf, arr in tfs.items():
            if tf == "statistics":
                continue
            if isinstance(arr, list):
                n = len(arr)
                total += n
                active = sum(1 for x in arr if x.get("status") in ("unfilled", "partially_filled"))
                print(f"  {tf}: {n} total ({active} active)")
        stats = tfs.get("statistics", {})
        if stats:
            print(f"  Stats: success_rate={stats.get('success_rate', 0):.2f} total={stats.get('total_fvgs', 0)}")

    print(f"\nGlobal total: {total}")

    actives = mgr.get_active_fvgs()
    actives = sorted(actives, key=lambda x: x.get("creation_timestamp", ""), reverse=True)[:5]
    if actives:
        print("\nLatest active FVGs:")
        for a in actives:
            print(f"- {a.get('symbol')} {a.get('timeframe')} {a.get('fvg_type')} gap={a.get('gap_size_pips'):.2f} status={a.get('status')} id={a.get('fvg_id')}")
    else:
        print("\nNo active FVGs found.")

if __name__ == "__main__":
    main()
