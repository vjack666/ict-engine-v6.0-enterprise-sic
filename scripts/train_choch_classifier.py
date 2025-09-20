#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

import pandas as pd

# Ensure '01-CORE' is importable
ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "01-CORE"
if str(CORE) not in sys.path:
    sys.path.append(str(CORE))

from analysis.unified_market_memory import get_unified_market_memory
from machine_learning.choch.dataset import CHoCHDataset
from machine_learning.choch.features import build_feature_matrix
from machine_learning.choch.models import (
    BaselineValidityClassifier,
    BaselineDirectionClassifier,
    save_model,
)


def main():
    parser = argparse.ArgumentParser(description="Train baseline CHoCH classifiers")
    parser.add_argument("--memory-dir", type=str, default=None, help="Override memory directory")
    parser.add_argument("--out-dir", type=str, default=None, help="Where to save models")
    parser.add_argument("--min-confidence", type=float, default=0.0, help="Filter by min confidence")
    parser.add_argument("--intel-accel", action="store_true", help="Use Intel sklearnex acceleration if available")
    args = parser.parse_args()

    # Optional Intel acceleration
    if args.intel_accel:
        try:
            from sklearnex import patch_sklearn  # type: ignore
            patch_sklearn()
            print("Intel sklearnex acceleration enabled.")
        except Exception:
            print("sklearnex not available; running with standard scikit-learn.")

    # Ensure memory is initialized/restored
    mem = get_unified_market_memory()
    mem.restore_unified_memory_state()

    ds = CHoCHDataset.from_memory(args.memory_dir)
    if args.min_confidence:
        ds = ds.filter(min_confidence=args.min_confidence)

    df = ds.df
    if df.empty:
        print("No CHoCH events found in memory. Run analyzers first.")
        return

    X, schema = build_feature_matrix(df)
    if X.empty:
        print("Feature matrix is empty. Aborting.")
        return

    # Train validity classifier
    val_clf = BaselineValidityClassifier()
    val_metrics = val_clf.fit(X, pd.concat([df, X[["recency_min"]]], axis=1))
    print(f"Validity accuracy: {val_metrics['accuracy']:.3f}")

    # Train direction classifier
    dir_clf = BaselineDirectionClassifier()
    dir_metrics = dir_clf.fit(X, df)
    print(f"Direction accuracy: {dir_metrics['accuracy']:.3f}")

    # Save
    root = Path(__file__).resolve().parents[1]
    out_dir = Path(args.out_dir) if args.out_dir else (root / "04-DATA" / "models" / "choch")
    out_dir.mkdir(parents=True, exist_ok=True)
    save_model(val_clf, str(out_dir / "validity_rf.joblib"))
    save_model(dir_clf, str(out_dir / "direction_lr.joblib"))
    print(f"Models saved to: {out_dir}")


if __name__ == "__main__":
    main()
