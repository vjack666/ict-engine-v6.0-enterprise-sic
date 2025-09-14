"""Order Blocks Realtime Service (Optimizado, no alta frecuencia)

Proporciona acceso controlado y cacheado a detección de Order Blocks
utilizando componentes reales (SmartMoneyAnalyzer) sin recalcular en cada
intervalo de UI.

Características:
- Lazy load de SmartMoneyAnalyzer (solo al primer uso real)
- Cache TTL por (símbolo, timeframe)
- Métricas internas básicas (hits, misses, latencia acumulada)
- Interfaz compacta para el tab

NOTA: No implementa persistencia todavía (fase C) ni ajuste dinámico del
intervalo (fase E). Se enfoca en la optimización inicial (A).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple, Deque
from collections import deque
import json
import time
import os

try:  # Logger opcional
    from smart_trading_logger import SmartTradingLogger  # type: ignore
except Exception:  # pragma: no cover
    SmartTradingLogger = None  # type: ignore


@dataclass
class CacheEntry:
    data: Dict[str, Any]
    created: datetime
    latency_ms: float
    symbol: str
    timeframe: str


class OrderBlocksRealtimeService:
    """Servicio optimizado para detección de Order Blocks.

    Parámetros:
        ttl_seconds: Vida de cada resultado en cache.
        max_age_fail_seconds: Tiempo para permitir reutilizar último éxito si la detección falla.
    """

    def __init__(self, ttl_seconds: int = 12, max_age_fail_seconds: int = 60,
                 history_size: int = 100,
                 persistence_path: Optional[str] = None):
        self.ttl = timedelta(seconds=ttl_seconds)
        self.max_age_fail = timedelta(seconds=max_age_fail_seconds)
        self._cache: Dict[Tuple[str, str], CacheEntry] = {}
        self._analyzer = None
        self.logger = SmartTradingLogger("OrderBlocksService") if SmartTradingLogger else None
        self.metrics = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "avg_latency_ms": 0.0,
            "last_error": None,
        }
        self.history: Deque[Dict[str, Any]] = deque(maxlen=history_size)
        self.persistence_path = persistence_path or os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "04-DATA", "memory_persistence")),
            "order_blocks_live.json"
        )
        # Asegurar carpeta
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
        except Exception:  # pragma: no cover
            pass

    # ------------------------ Internals ------------------------
    def _log(self, level: str, msg: str, ctx: str = "service"):
        if self.logger:
            try:
                getattr(self.logger, level.lower())(msg, ctx)  # info/debug/error
            except Exception:  # pragma: no cover
                pass

    def _load_analyzer(self):
        if self._analyzer is not None:
            return
        try:
            from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer  # type: ignore
            self._analyzer = SmartMoneyAnalyzer()
            self._log("info", "SmartMoneyAnalyzer inicializado", "init")
        except Exception as e:  # pragma: no cover
            self.metrics["errors"] += 1
            self.metrics["last_error"] = str(e)
            raise RuntimeError(f"No se pudo inicializar SmartMoneyAnalyzer: {e}") from e

    def _is_valid(self, entry: CacheEntry) -> bool:
        return datetime.now() - entry.created < self.ttl

    # ------------------------ Public API ------------------------
    def get_order_blocks(self, symbol: str, timeframe: str, force: bool = False) -> Dict[str, Any]:
        key = (symbol, timeframe)
        now = datetime.now()
        entry = self._cache.get(key)

        if not force and entry and self._is_valid(entry):
            self.metrics["hits"] += 1
            return {
                "source": "CACHE",
                "latency_ms": entry.latency_ms,
                "last_update": entry.created.isoformat(),
                **entry.data,
            }

        self.metrics["misses"] += 1

        # Intentar cargar analyzer
        try:
            self._load_analyzer()
        except Exception as e:
            # Fallback: usar último dato válido si existe
            if entry and now - entry.created < self.max_age_fail:
                self._log("error", f"Fallo detección, usando cache previa: {e}", "fallback")
                return {
                    "source": "STALE_CACHE",
                    "latency_ms": entry.latency_ms,
                    "last_update": entry.created.isoformat(),
                    **entry.data,
                }
            raise

        # Real detection
        start = time.time()
        try:
            # Aquí llamamos a un método hipotético; se ajustará si el analyzer expone otro nombre.
            detect_method = getattr(self._analyzer, "find_order_blocks", None) or getattr(self._analyzer, "analyze_smart_money_concepts", None)
            if detect_method is None:
                raise RuntimeError("SmartMoneyAnalyzer no expone método de detección de Order Blocks soportado")

            # Estrategia flexible: si es analyze_smart_money_concepts necesita datos multi-timeframe.
            raw_result = None
            if detect_method.__name__ == "analyze_smart_money_concepts":
                # Intentar construir una estructura mínima; si falla, lanzar error claro.
                market_data = {timeframe: {"symbol": symbol, "timeframe": timeframe}}
                raw_result = detect_method(symbol, market_data)
                # Extraer order blocks si vienen anidados
                order_blocks = []
                if isinstance(raw_result, dict):
                    # Buscar claves plausibles
                    for k in ("order_blocks", "blocks", "orderBlocks"):
                        if k in raw_result and isinstance(raw_result[k], list):
                            order_blocks = raw_result[k]
                            break
            else:
                raw_result = detect_method(symbol=symbol, timeframe=timeframe)
                order_blocks = raw_result if isinstance(raw_result, list) else []

            latency_ms = (time.time() - start) * 1000

            # Normalizar
            normalized = []
            for idx, ob in enumerate(order_blocks):
                if isinstance(ob, dict):
                    price = ob.get("price") or ob.get("level") or ob.get("base_price")
                    ob_type = ob.get("type") or ob.get("direction") or "unknown"
                    conf = ob.get("confidence") or ob.get("score") or 0
                else:
                    price = None
                    ob_type = "unknown"
                    conf = 0
                normalized.append({
                    "id": idx,
                    "type": ob_type,
                    "price": price,
                    "confidence": conf,
                })

            payload = {
                "symbol": symbol,
                "timeframe": timeframe,
                "order_blocks": normalized,
                "count": len(normalized),
                "latency_ms": latency_ms,
            }

            # Guardar cache
            self._cache[key] = CacheEntry(data=payload, created=now, latency_ms=latency_ms, symbol=symbol, timeframe=timeframe)

            # Métricas
            prev_avg = self.metrics["avg_latency_ms"]
            n = self.metrics["hits"] + self.metrics["misses"]
            self.metrics["avg_latency_ms"] = ((prev_avg * (n - 1)) + latency_ms) / max(n, 1)

            final_payload = {"source": "CALC", **payload, "last_update": now.isoformat()}

            # Historial y persistencia solo para cálculos nuevos
            self._register_history(final_payload)
            self._persist_safe(final_payload)

            return final_payload

        except Exception as e:  # pragma: no cover
            self.metrics["errors"] += 1
            self.metrics["last_error"] = str(e)
            self._log("error", f"Error detección Order Blocks: {e}", "detection")
            if entry:
                # fallback con advertencia
                return {
                    "source": "STALE_CACHE_ERROR",
                    "error": str(e),
                    "last_update": entry.created.isoformat(),
                    **entry.data,
                }
            return {"error": str(e), "symbol": symbol, "timeframe": timeframe, "order_blocks": [], "last_update": now.isoformat()}

    def get_metrics(self) -> Dict[str, Any]:
        return {**self.metrics, "cache_size": len(self._cache), "ttl_seconds": self.ttl.total_seconds(), "history_len": len(self.history)}

    # ---------------- Persistence / History -----------------
    def _register_history(self, payload: Dict[str, Any]):
        try:
            self.history.append({
                "ts": payload.get("last_update"),
                "symbol": payload.get("symbol"),
                "timeframe": payload.get("timeframe"),
                "count": payload.get("count"),
                "latency_ms": payload.get("latency_ms"),
                "source": payload.get("source"),
            })
        except Exception:  # pragma: no cover
            pass

    def _persist_safe(self, payload: Dict[str, Any]):
        try:
            data = {
                "last_snapshot": payload,
                "history": list(self.history)
            }
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:  # pragma: no cover
            self.metrics["last_error"] = f"persist: {e}"
            if self.logger:
                self.logger.error(f"Persistencia fallo: {e}", "persist")

__all__ = ["OrderBlocksRealtimeService"]
