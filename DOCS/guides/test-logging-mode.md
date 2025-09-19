# Test Logging Mode (Windows-safe)

- Env flag: `ICT_DISABLE_LOG_ROTATION=1`
- Purpose: Avoid Windows file-lock errors from `RotatingFileHandler` during tests.
- Scope: Tests only (set in `tests/conftest.py` via `pytest_configure`).

When this flag is set, loggers use `logging.FileHandler` instead of rotation:
- `01-CORE/protocols/logging_protocol.py`
- `01-CORE/smart_trading_logger.py` (daily .log and optional .ndjson)
- `09-DASHBOARD/utils/dashboard_logger.py`

CI tip:
- Set `ICT_DISABLE_LOG_ROTATION=1` in CI environment for stable Windows runners.

Local commands:
```powershell
python -m pytest -q
```
