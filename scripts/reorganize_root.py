#!/usr/bin/env python3
"""
Safe root reorganization utility (dry-run by default).

Goals:
- Consolidate stray top-level items into canonical folders without breaking imports
- Offer idempotent, logged operations with --apply to execute
- Provide targeted actions via flags: remove monitoring shim, merge data

Usage:
  python scripts/reorganize_root.py              # dry-run
  python scripts/reorganize_root.py --apply      # perform actions
  python scripts/reorganize_root.py --help       # options

Actions performed (opt-in via flags):
- --remove-monitoring-shim: Remove root 'monitoring/' if it is just a shim
- --merge-data: Move root 'data/' into '04-DATA/data/' preserving structure

Always skipped: VCS, caches, known canonical folders
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
from datetime import datetime


REPO_ROOT = Path(__file__).resolve().parent.parent

CANONICAL_DIRS = {
    '00-ROOT', '01-CORE', '04-DATA', '05-LOGS', '09-DASHBOARD',
    'DOCS', 'scripts', 'tests', 'test_data', 'tools',
    '.git', '.vscode', '.pytest_cache', '__pycache__'
}

LOG_DIR = REPO_ROOT / '05-LOGS' / 'system'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / f"reorg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


def log(msg: str) -> None:
    line = f"[reorg] {msg}"
    print(line)
    try:
        with LOG_FILE.open('a', encoding='utf-8') as f:
            f.write(line + "\n")
    except Exception:
        pass


def is_monitoring_shim(monitoring_dir: Path) -> bool:
    if not monitoring_dir.is_dir():
        return False
    shim = monitoring_dir / 'baseline_metrics_system.py'
    if not shim.exists():
        return False
    try:
        text = shim.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return False
    return 'Shim for monitoring.baseline_metrics_system' in text and '01-CORE/monitoring/baseline_metrics_system.py' in text


def file_hash(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_move(src: Path, dst: Path, apply: bool) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        # If identical, delete src; else, leave src in place
        try:
            if src.is_file() and dst.is_file() and file_hash(src) == file_hash(dst):
                action = f"duplicate -> delete {src.relative_to(REPO_ROOT)}"
                if apply:
                    src.unlink(missing_ok=True)
                return action
        except Exception:
            pass
        return f"conflict -> keep both (src left in place): {src.relative_to(REPO_ROOT)} -> {dst.relative_to(REPO_ROOT)}"
    if apply:
        shutil.move(str(src), str(dst))
    return f"move {src.relative_to(REPO_ROOT)} -> {dst.relative_to(REPO_ROOT)}"


def remove_dir(path: Path, apply: bool) -> str:
    if apply:
        shutil.rmtree(path, ignore_errors=True)
    return f"remove dir {path.relative_to(REPO_ROOT)}"


def merge_data_root(apply: bool) -> None:
    src = REPO_ROOT / 'data'
    if not src.exists():
        log("[data] no root 'data/' to merge")
        return
    dst_root = REPO_ROOT / '04-DATA' / 'data'
    for p in src.rglob('*'):
        if p.is_dir():
            continue
        rel = p.relative_to(src)
        dst = dst_root / rel
        action = safe_move(p, dst, apply)
        log(f"[data] {action}")
    # Clean up empty dirs
    try:
        if apply:
            for root, dirs, files in os.walk(src, topdown=False):
                if not dirs and not files:
                    Path(root).rmdir()
        if src.exists() and not any(src.iterdir()):
            action = remove_dir(src, apply)
            log(f"[data] {action}")
    except Exception:
        pass


def remove_monitoring_shim(apply: bool) -> None:
    mon = REPO_ROOT / 'monitoring'
    if not mon.exists():
        log("[mon] no root 'monitoring/' present")
        return
    if not is_monitoring_shim(mon):
        log("[mon] root 'monitoring/' is not recognized as shim -> skipped")
        return
    action = remove_dir(mon, apply)
    log(f"[mon] {action}")


def plan_only() -> None:
    root_items = sorted([p.name for p in REPO_ROOT.iterdir() if not p.name.startswith('.')])
    log("Root contents (plan): " + ", ".join(root_items))
    log("Canonical dirs kept: " + ", ".join(sorted(CANONICAL_DIRS)))
    # Report potential actions
    mon = REPO_ROOT / 'monitoring'
    if mon.exists():
        if is_monitoring_shim(mon):
            log("[plan] Would remove root 'monitoring/' (shim)")
        else:
            log("[plan] Found root 'monitoring/' (not shim) -> manual review suggested")
    if (REPO_ROOT / 'data').exists():
        log("[plan] Would merge 'data/' into '04-DATA/data/'")


def main() -> None:
    parser = argparse.ArgumentParser(description='Safe root reorganization utility')
    parser.add_argument('--apply', action='store_true', help='Perform changes (defaults to dry-run)')
    parser.add_argument('--remove-monitoring-shim', action='store_true', help='Remove root monitoring/ shim')
    parser.add_argument('--merge-data', action='store_true', help='Merge root data/ into 04-DATA/data/')
    args = parser.parse_args()

    log(f"Starting reorg (apply={args.apply}) at {datetime.now().isoformat(timespec='seconds')}")
    plan_only()

    if args.remove_monitoring_shim:
        remove_monitoring_shim(apply=args.apply)
    if args.merge_data:
        merge_data_root(apply=args.apply)

    log("Reorg completed")


if __name__ == '__main__':
    main()
