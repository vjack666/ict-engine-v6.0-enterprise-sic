# Shutdown Log De-duplication Guide

This project includes a global shutdown/stop log de-duplication mechanism to keep logs clean during shutdown sequences where multiple components may emit similar messages.

## What it does
- Collapses duplicate shutdown/stop messages across different adapters (SmartTradingLogger, standard logging, minimal prints).
- Operates on normalized message text (lowercased, trimmed) independent of level/component.
- Applies both inside unified logging adapters and at the root logger via a filter.

## Where it lives
- Core implementation: `01-CORE/protocols/unified_logging.py`
  - Function: `_global_should_emit(level, component, message)`
  - Root filter: `_ShutdownDedupFilter` installed via `_ensure_root_filter_installed()` when creating any unified logger

## Keywords (triggers)
The filter only de-duplicates messages that include one of these keywords (case-insensitive):
- "shutdown", "stopped", "stopping alert integration system", "shutting down", "shutting down production system"
- "system monitoring stopped", "real-time data processing stopped", "alert integration system stopped"
- "production system shutdown complete", "shutdown successfully"
- Spanish: "shutdown completado", "iniciando cierre del sistema", "monitoreo del sistema detenido", "desconectado de mt5", "forzando cierre inmediato"

You can extend this list in `unified_logging.py` (`_DEDUP_KEYWORDS`).

## Time window
- Controlled by env var `ICT_LOG_DEDUP_WINDOW_SEC` (default `1.0`).
- Duplicates within this window for the same normalized message are suppressed.

## Best practices to avoid duplicates
- Prefer component-internal logs over orchestrator echoes. For example, let `RealTimeDataProcessor` emit its own "stopped" log; in `main.shutdown()` we keep such echoes at `debug`.
- Avoid logging the same shutdown line from multiple layers (adapter + manager + orchestrator).
- Use unified logging APIs so the global de-dup filter sees messages consistently.

## Known limitations
- Only messages containing the listed keywords are de-duplicated.
- Messages with varying text won’t be collapsed (by design).
- If external code logs before any unified logger is created, the root filter might not be installed yet. Create a unified logger early in process startup if needed.

## Tuning
- Add/remove keywords in `_DEDUP_KEYWORDS` to match your components.
- Adjust the time window via `ICT_LOG_DEDUP_WINDOW_SEC` for slower/faster shutdown sequences.

## Quick verification
Run a quick smoke test:

```powershell
# Windows PowerShell
cd C:\Users\v_jac\Desktop\ict-engine-v6.0-enterprise-sic
$env:ICT_LOG_DEDUP_WINDOW_SEC = '1.0'; echo q | python .\main.py
```

You should see at most a single instance for typical shutdown lines and the farewell message only once.
