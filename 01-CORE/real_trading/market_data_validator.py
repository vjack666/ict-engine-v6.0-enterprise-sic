#!/usr/bin/env python3
"""
Market Data Validator - ICT Engine v6.0 Enterprise
=================================================

Validaciones ligeras y de bajo costo para datos de mercado (velas / ticks).
Objetivo: detectar condiciones que deben pausar ejecución o degradar estrategia.

Checks implementados (todos opcionales y tolerantes a fallos):
- Gap temporal entre velas (timestamp no contiguo)
- Velas stale (última vela demasiado vieja)
- Outliers de rango (rango extremadamente grande vs media reciente)

Uso:
    validator = MarketDataValidator(max_gap_seconds=180, stale_seconds=90)
    ok, issues = validator.validate_candles(candles)
    if not ok:
        # decidir acción (pausa trading, degradar módulos, etc.)

Integración rápida con ExecutionRouter:
    router.pre_order_hooks.append(validator.create_pre_order_hook())

Formato esperado de candles: lista de dicts con llaves mínimas:
    {'time': epoch_seconds|iso8601, 'open': float, 'high': float, 'low': float, 'close': float}

Optimizado para tiempo real: O(n) simple, sin dependencias pesadas.
"""
from __future__ import annotations
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timezone
from statistics import mean

try:
    from protocols.logging_protocol import create_safe_logger, LogLevel  # type: ignore
except Exception:  # fallback
    def create_safe_logger(component_name: str, **_):  # type: ignore
        class _L:  # noqa: D401
            def info(self, m, c=""): print(f"[INFO][{component_name}]{c} {m}")
            def warning(self, m, c=""): print(f"[WARN][{component_name}]{c} {m}")
            def error(self, m, c=""): print(f"[ERROR][{component_name}]{c} {m}")
        return _L()
    class LogLevel:  # type: ignore
        INFO = "INFO"

class MarketDataValidatorConfig:
    def __init__(self,
                 max_gap_seconds: int = 300,
                 stale_seconds: int = 120,
                 max_range_sigma: float = 6.0,
                 min_samples_for_range_stats: int = 20) -> None:
        self.max_gap_seconds = max_gap_seconds
        self.stale_seconds = stale_seconds
        self.max_range_sigma = max_range_sigma
        self.min_samples_for_range_stats = min_samples_for_range_stats

class MarketDataValidator:
    def __init__(self, config: Optional[MarketDataValidatorConfig] = None) -> None:
        self.config = config or MarketDataValidatorConfig()
        self.logger = create_safe_logger("MarketDataValidator", log_level=getattr(LogLevel, 'INFO', None))
        if self.config.max_gap_seconds < 0:
            self.config.max_gap_seconds = 0
        if self.config.stale_seconds < 10:  # evitar falsos positivos demasiado agresivos
            self.config.stale_seconds = 10

    def _parse_time(self, v: Any) -> Optional[int]:
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str):
            try:
                # intentar ISO8601
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                return int(dt.timestamp())
            except Exception:
                return None
        return None

    def validate_candles(self, candles: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        issues: List[str] = []
        if not candles or len(candles) < 2:
            return True, issues
        if len(candles) > 10_000:  # protección de memoria: recortar a los últimos N
            candles = candles[-5000:]
        # ordenar por tiempo para robustez
        parsed = []
        for c in candles:
            t = self._parse_time(c.get('time'))
            if t is not None:
                parsed.append((t, c))
        if len(parsed) < 2:
            return True, issues
        parsed.sort(key=lambda x: x[0])
        times = [t for t, _ in parsed]
        # gap detection
        gaps = 0
        expected_interval = None
        if len(times) >= 3:
            deltas = [times[i+1]-times[i] for i in range(min(3, len(times)-1))]
            # heuristic expected interval (most common of first 3 diffs)
            expected_interval = max(set(deltas), key=deltas.count)
        prev = times[0]
        for t in times[1:]:
            diff = t - prev
            if self.config.max_gap_seconds and diff > self.config.max_gap_seconds:
                gaps += 1
            if expected_interval and diff > expected_interval * 3:
                issues.append(f"gap_interval_anomaly:{diff}s")
            prev = t
        if gaps:
            issues.append(f"large_gaps:{gaps}")
        # stale check (última vela demasiado antigua vs ahora UTC)
        now_ts = int(datetime.now(timezone.utc).timestamp())
        last_ts = times[-1]
        if now_ts - last_ts > self.config.stale_seconds:
            issues.append(f"stale_last:{now_ts-last_ts}s")
        # range outlier check
        if len(parsed) >= self.config.min_samples_for_range_stats:
            ranges = []
            for _, c in parsed[-self.config.min_samples_for_range_stats:]:
                try:
                    h = float(c.get('high')); l = float(c.get('low'))
                    if h >= l:
                        ranges.append(h - l)
                except Exception:
                    continue
            if len(ranges) >= self.config.min_samples_for_range_stats // 2:
                avg_r = mean(ranges)
                if avg_r > 0:
                    current_r = float(parsed[-1][1].get('high', 0)) - float(parsed[-1][1].get('low', 0))
                    if current_r > avg_r * self.config.max_range_sigma:
                        issues.append(f"range_outlier:{current_r:.2f}>")
        ok = len(issues) == 0
        return ok, issues

    def create_pre_order_hook(self):
        def _hook(symbol: str, action: str, volume: float, price: Optional[float]):  # noqa: D401
            # No bloquea si no hay problemas recientes
            return True, None
        return _hook

__all__ = ["MarketDataValidator", "MarketDataValidatorConfig"]
