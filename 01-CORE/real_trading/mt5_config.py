from protocols.unified_logging import get_unified_logger
import subprocess
import time
import os
from typing import Any

try:
    from protocols.logging_central_protocols import create_safe_logger  # type: ignore
    _logger = get_unified_logger("MT5Gateway")
except Exception:
    class _FallbackLogger:
        def info(self, m, c=""): print(f"[INFO][MT5Gateway]{c} {m}")
        def warning(self, m, c=""): print(f"[WARN][MT5Gateway]{c} {m}")
        def error(self, m, c=""): print(f"[ERROR][MT5Gateway]{c} {m}")
        def debug(self, m, c=""): pass
    _logger = _FallbackLogger()

MT5_TERMINAL_PATH = r"C:\Program Files\FTMO Global Markets MT5 Terminal\terminal64.exe"

def _is_ftmo_terminal_running() -> bool:
    """Verifica si la terminal FTMO específica está ya en ejecución."""
    try:
        import psutil  # type: ignore
    except ImportError:
        return False  # Si no hay psutil no podemos verificar; seguiremos intentando launch
    exe_lower = MT5_TERMINAL_PATH.lower()
    for p in psutil.process_iter(attrs=["name","exe","cmdline"]):
        try:
            exe = (p.info.get("exe") or "").lower()
            if exe == exe_lower:
                _logger.debug("FTMO terminal already running", "MT5")
                return True
        except Exception:
            continue
    return False

def _launch_ftmo_terminal() -> bool:
    """Lanza la terminal FTMO si no está abierta."""
    if not os.path.isfile(MT5_TERMINAL_PATH):
        _logger.error(f"Terminal FTMO no encontrada: {MT5_TERMINAL_PATH}", "MT5")
        return False
    try:
        subprocess.Popen([MT5_TERMINAL_PATH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        _logger.info("Lanzando terminal FTMO", "MT5")
        return True
    except Exception as e:
        _logger.error(f"Error lanzando terminal FTMO: {e}", "MT5")
        return False

def mt5_initialize(**kwargs: Any) -> bool:  # type: ignore
    """Wrapper centralizado forzado a la terminal FTMO.
    Reglas:
    - Ignora cualquier 'path' distinto y usa siempre MT5_TERMINAL_PATH.
    - No intenta conectarse a otras instalaciones incluso si están presentes.
    - Si la terminal FTMO no está abierta, intenta lanzarla y espera breve.
    - Retorna False si no puede inicializar esta instancia específica.
    """
    try:
        import MetaTrader5 as mt5  # type: ignore
    except ImportError:
        return False

    # Forzar path único
    kwargs['path'] = MT5_TERMINAL_PATH

    # Asegurar terminal en ejecución (mejor para estabilidad de initialize)
    if not _is_ftmo_terminal_running():
        _logger.info("Terminal FTMO no detectada - intentando lanzamiento", "MT5")
        launched = _launch_ftmo_terminal()
        time.sleep(2)
        if not launched:
            _logger.warning("No se pudo lanzar terminal FTMO (se intentará initialize igualmente)", "MT5")
    else:
        _logger.debug("Terminal FTMO detectada en ejecución", "MT5")

    try:
        ok = mt5.initialize(**kwargs)  # type: ignore
        if ok:
            _logger.info("MT5 inicializado con terminal FTMO fija", "MT5")
        else:
            _logger.error("Fallo initialize() con terminal FTMO", "MT5")
        return ok
    except Exception as e:
        _logger.error(f"Excepción initialize(): {e}", "MT5")
        return False
