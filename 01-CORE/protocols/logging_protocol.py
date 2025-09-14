"""Central Logging Protocol
===========================

Define una interfaz mínima para logging centralizado reutilizable
por motores de backtest, trading y otros subsistemas sin acoplarse
al logger concreto (SmartTradingLogger u otros futuros).

Objetivos:
- Evitar dependencias circulares
- Permitir degradación graciosa si el logger enterprise no está disponible
- Un punto único de extensión futura (handlers externos, dashboards, etc.)
"""
from __future__ import annotations

from typing import Protocol, Any, Optional, Dict
import logging

class CentralLogger(Protocol):  # pragma: no cover - contract
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None: ...


def get_central_logger(name: str = "EnterpriseCore") -> CentralLogger:
    """Obtiene el logger central si SmartTradingLogger existe, con fallback.

    Fallback: logging.getLogger(name) nivel INFO.
    """
    try:
        from smart_trading_logger import SmartTradingLogger  # type: ignore
        return SmartTradingLogger(name)  # type: ignore
    except Exception:
        logger = logging.getLogger(name)
        if not logger.handlers:
            logging.basicConfig(level=logging.INFO)
        return logger  # type: ignore[return-value]

__all__ = ["CentralLogger", "get_central_logger"]
