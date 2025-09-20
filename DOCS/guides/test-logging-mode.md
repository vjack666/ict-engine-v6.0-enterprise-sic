# Modo de Logging para Tests (seguro en Windows)

- Variable de entorno: `ICT_DISABLE_LOG_ROTATION=1`
- Propósito: Evitar errores de bloqueo de archivos en Windows por `RotatingFileHandler` durante las pruebas.
- Alcance: Solo tests (se establece en `tests/conftest.py` mediante `pytest_configure`).

Cuando esta variable está activa, los loggers usan `logging.FileHandler` en lugar de rotación:
- `01-CORE/protocols/logging_protocol.py`
- `01-CORE/smart_trading_logger.py` (archivos .log diarios y .ndjson opcional)
- `09-DASHBOARD/utils/dashboard_logger.py`

Sugerencia para CI:
- Define `ICT_DISABLE_LOG_ROTATION=1` en el entorno de CI para obtener ejecuciones estables en Windows.

Comandos locales:
```powershell
python -m pytest -q
```
