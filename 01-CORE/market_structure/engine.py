#!/usr/bin/env python3
"""Market Structure Core Engine (Minimal v1)

Responsabilidad:
- Proveer detección básica (placeholders) de eventos market structure.
- Estructura lista para ampliación sin romper integraciones.

Metas diseño:
- Métodos puros retornan dict estructurado.
- Logging opcional vía SmartTradingLogger si disponible.
- Validaciones de entrada ligeras.
- Orientado a integrarse con sistema ML (features).
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Sequence
from datetime import datetime

try:  # logger opcional
    from smart_trading_logger import SmartTradingLogger  # type: ignore
except Exception:  # pragma: no cover
    SmartTradingLogger = None  # type: ignore

Candle = Dict[str, Any]  # Esperado: {'time': ts/int/str, 'open': float, 'high': float, 'low': float, 'close': float, ...}

@dataclass
class MarketStructureResult:
    symbol: str
    timeframe: str
    timestamp: str
    choch_events: List[Dict[str, Any]]
    bos_events: List[Dict[str, Any]]
    order_blocks: List[Dict[str, Any]]
    fvg_zones: List[Dict[str, Any]]
    multi_timeframe_context: Dict[str, Any]
    market_bias: Optional[str]
    meta: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MarketStructureEngine:
    def __init__(self, enable_logging: bool = True):
        self.logger = SmartTradingLogger("MarketStructure") if (enable_logging and SmartTradingLogger) else None

    # ---------------------- Helpers ---------------------- #
    def _log(self, level: str, msg: str, channel: str = "market_structure", **ctx):  # pragma: no cover (no critical)
        if not self.logger:
            return
        try:
            log_fn = getattr(self.logger, level, None)
            if callable(log_fn):
                log_fn(msg, channel, extra=ctx)  # type: ignore
        except Exception:
            pass

    def _validate_candles(self, candles: Sequence[Candle]):
        if not candles or len(candles) < 3:
            raise ValueError("Se requieren al menos 3 velas para análisis básico")
        needed = {"high", "low", "close"}
        sample = candles[-1]
        if not needed.issubset(sample.keys()):
            raise ValueError(f"Candle incompleta: faltan claves {needed - set(sample.keys())}")

    def _ts(self) -> str:
        return datetime.utcnow().isoformat()

    # ---------------------- Core Detections (Placeholders) ---------------------- #
    def detect_choch(self, candles: Sequence[Candle]) -> List[Dict[str, Any]]:
        """Detectar CHoCH (placeholder). Regla simplificada:
        - Señala cambio si última vela cierra > high de las 2 previas o < low de las 2 previas.
        """
        try:
            self._validate_candles(candles)
        except Exception as e:
            self._log("warn", f"detect_choch invalido: {e}")
            return []
        last = candles[-1]
        prev2 = candles[-3:]
        high_ref = max(c["high"] for c in prev2[:-1])
        low_ref = min(c["low"] for c in prev2[:-1])
        events: List[Dict[str, Any]] = []
        if last["close"] > high_ref:
            events.append({"type": "CHOCH_BULL", "price": last["close"], "time": last.get("time", self._ts())})
        elif last["close"] < low_ref:
            events.append({"type": "CHOCH_BEAR", "price": last["close"], "time": last.get("time", self._ts())})
        return events

    def detect_bos(self, candles: Sequence[Candle]) -> List[Dict[str, Any]]:
        """Detectar Break of Structure (placeholder). Regla simplificada:
        - Última vela rompe high o low extremo de las últimas N (N=5) velas previas.
        """
        try:
            self._validate_candles(candles)
        except Exception as e:
            self._log("warn", f"detect_bos invalido: {e}")
            return []
        lookback = candles[-6:-1] if len(candles) > 6 else candles[:-1]
        if not lookback:
            return []
        last = candles[-1]
        high_lb = max(c["high"] for c in lookback)
        low_lb = min(c["low"] for c in lookback)
        events: List[Dict[str, Any]] = []
        if last["high"] > high_lb:
            events.append({"type": "BOS_UP", "trigger": last["high"], "time": last.get("time", self._ts())})
        if last["low"] < low_lb:
            events.append({"type": "BOS_DOWN", "trigger": last["low"], "time": last.get("time", self._ts())})
        return events

    def identify_order_blocks(self, candles: Sequence[Candle]) -> List[Dict[str, Any]]:
        """Identificación muy simplificada: toma última vela con cuerpo grande como bloque potencial.
        Regla placeholder: tamaño cuerpo >= 70% del rango vela y rango > mediana últimos 10 rangos.
        """
        try:
            self._validate_candles(candles)
        except Exception as e:
            self._log("warn", f"identify_order_blocks invalido: {e}")
            return []
        tail = candles[-20:]
        ranges = [(c["high"] - c["low"]) for c in tail if c["high"] >= c["low"]]
        if not ranges:
            return []
        sorted_ranges = sorted(ranges)
        median_range = sorted_ranges[len(sorted_ranges)//2]
        last = candles[-1]
        rng = last["high"] - last["low"]
        body = abs(last["close"] - last.get("open", last["close"]))
        if rng <= 0:
            return []
        cond_body = body >= 0.7 * rng
        cond_range = rng > median_range
        if cond_body and cond_range:
            direction = "BULL" if last["close"] > last.get("open", last["close"]) else "BEAR"
            return [{
                "id": f"OB-{last.get('time', self._ts())}",
                "type": direction,
                "price": last["close"],
                "high": last["high"],
                "low": last["low"],
                "confidence": 0.55,
                "time": last.get("time", self._ts())
            }]
        return []

    def detect_fair_value_gaps(self, candles: Sequence[Candle]) -> List[Dict[str, Any]]:
        """Detectar FVG básico: gap entre low vela actual y high anterior (o viceversa) que no se solapa.
        Busca últimos 5 tríos."""
        if len(candles) < 3:
            return []
        res: List[Dict[str, Any]] = []
        window = candles[-10:]
        for i in range(2, len(window)):
            c0, c1, c2 = window[i-2], window[i-1], window[i]
            # Gap alcista: high c0 < low c2 y cuerpo medio no lo rellena
            if c0["high"] < c2["low"] and not (c1["low"] <= c0["high"] <= c1["high"]):
                res.append({
                    "type": "FVG_BULL",
                    "start": c0["high"],
                    "end": c2["low"],
                    "mid_time": c1.get("time", self._ts()),
                    "detected": self._ts()
                })
            # Gap bajista
            if c0["low"] > c2["high"] and not (c1["low"] <= c2["high"] <= c1["high"]):
                res.append({
                    "type": "FVG_BEAR",
                    "start": c2["high"],
                    "end": c0["low"],
                    "mid_time": c1.get("time", self._ts()),
                    "detected": self._ts()
                })
        return res

    def analyze_multi_timeframe(self, contexts: Dict[str, Sequence[Candle]]) -> Dict[str, Any]:
        """Combinar señales de múltiples TFs (placeholder). Prioriza coincidencias CHOCH/BOS."""
        summary: Dict[str, Any] = {"timeframes": {}, "agreement_score": 0}
        score = 0
        considered = 0
        for tf, seq in contexts.items():
            choch = self.detect_choch(seq)
            bos = self.detect_bos(seq)
            summary["timeframes"][tf] = {"choch": choch, "bos": bos}
            if choch:
                score += 1
            if bos:
                score += 1
            considered += 2
        summary["agreement_score"] = (score / considered) if considered else 0
        return summary

    def get_market_bias(self, choch_events: List[Dict[str, Any]], bos_events: List[Dict[str, Any]], order_blocks: List[Dict[str, Any]]) -> Optional[str]:
        """Derivar bias simplificado."""
        bull = any(e["type"].endswith("BULL") or e["type"].endswith("UP") for e in choch_events + bos_events + order_blocks)
        bear = any(e["type"].endswith("BEAR") or e["type"].endswith("DOWN") for e in choch_events + bos_events + order_blocks)
        if bull and not bear:
            return "BULLISH"
        if bear and not bull:
            return "BEARISH"
        if bull and bear:
            return "NEUTRAL"
        return None

    # ---------------------- Orquestador Principal ---------------------- #
    def run_full_analysis(self, symbol: str, timeframe: str, candles: Sequence[Candle], mtf_context: Optional[Dict[str, Sequence[Candle]]] = None) -> MarketStructureResult:
        self._log("info", f"Analizando {symbol} {timeframe} ({len(candles)} velas)")
        choch = self.detect_choch(candles)
        bos = self.detect_bos(candles)
        obs = self.identify_order_blocks(candles)
        fvgs = self.detect_fair_value_gaps(candles)
        mtf = self.analyze_multi_timeframe(mtf_context) if mtf_context else {"agreement_score": None, "timeframes": {}}
        bias = self.get_market_bias(choch, bos, obs)
        meta = {
            "version": "ms_core_v1",
            "candles_used": len(candles),
            "mtf_used": list(mtf_context.keys()) if mtf_context else [],
            "generated": self._ts()
        }
        result = MarketStructureResult(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=self._ts(),
            choch_events=choch,
            bos_events=bos,
            order_blocks=obs,
            fvg_zones=fvgs,
            multi_timeframe_context=mtf,
            market_bias=bias,
            meta=meta
        )
        return result

__all__ = [
    "MarketStructureEngine",
    "MarketStructureResult"
]
