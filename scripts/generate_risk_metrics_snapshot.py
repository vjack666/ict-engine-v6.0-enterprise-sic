#!/usr/bin/env python3
"""
Generate Risk Metrics Snapshot
==============================
Creates or refreshes 04-DATA/metrics/risk_metrics.json using RiskTracker.
"""
from pathlib import Path
import sys

# Ensure core is on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '01-CORE'))

from risk_management.risk_tracking import RiskTracker  # type: ignore

if __name__ == '__main__':
    tracker = RiskTracker()
    path = tracker.export_snapshot()
    print(f"Risk metrics snapshot written to: {path}")
