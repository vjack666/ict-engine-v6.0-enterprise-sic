# Logging System Update (2025-09-17)

- Overview: Size-based rotation on per-day files, per-component directories under `05-LOGS`, optional async queue, retention and total-size limits.
- Scope: Implemented in `01-CORE/smart_trading_logger.py`. All modules using `SmartTradingLogger` or `get_unified_logger` inherit these changes.

## Configuration (env vars)
- `ICT_LOG_RETENTION_DAYS`: Days to keep logs (default: `14`).
- `ICT_LOG_MAX_BYTES`: Max bytes before rotate (default: `5242880` = 5MB).
- `ICT_LOG_BACKUP_COUNT`: Number of rotated files to retain (default: `3`).
- `ICT_LOG_USE_QUEUE`: Enable async QueueHandler/QueueListener (default: `1`).
- `ICT_LOG_MAX_TOTAL_MB`: Cap per-component folder total size in MB (default: `512`).

## Quick Test
```powershell
Set-Location "C:\Users\v_jac\Desktop\ict-engine-v6.0-enterprise-sic"
$env:ICT_LOG_RETENTION_DAYS = "1"
$env:ICT_LOG_MAX_BYTES = "10240"      # 10KB
$env:ICT_LOG_BACKUP_COUNT = "2"
$env:ICT_LOG_USE_QUEUE = "1"
$env:ICT_LOG_MAX_TOTAL_MB = "1"
python scripts/test_logging_rotation.py
```

## Notes
- Files rotate as `*_YYYY-MM-DD.log`, with backups `*.log.1`, `*.log.2`, etc.
- Retention and total-size cleanup run on startup of each logger instance.
- Console logging is suppressed in silent mode; use `SmartTradingLogger(..., silent_mode=False)` to see output.

## NDJSON Export (AI-ready)
- Enable by setting `ICT_LOG_EXPORT_JSON=1`.
- Emits per-component NDJSON at `05-LOGS/<component>/<component>_<YYYY-MM-DD>.ndjson`.
- Fields per line: `ts`, `level`, `logger`, `component`, `message`.

Quick check (PowerShell):
```powershell
$env:ICT_LOG_EXPORT_JSON = '1'
python -c "import sys,os,time; sys.path.append('01-CORE'); os.environ['ICT_LOG_EXPORT_JSON']='1'; from smart_trading_logger import SmartTradingLogger; lg=SmartTradingLogger('TestExport'); [lg.info(f'Evento de prueba {i}', component='SYSTEM') or time.sleep(0.005) for i in range(50)]"
Get-ChildItem -Recurse -Filter "*.ndjson" | Select-Object FullName, Length, LastWriteTime | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

## Daily Archiving
- Script: `scripts/archive_logs.py`
- Output: `04-DATA/exports/logs/logs_<YYYY-MM-DD>.zip`

Usage (PowerShell):
```powershell
python .\scripts\archive_logs.py --date (Get-Date -Format 'yyyy-MM-dd')
Get-ChildItem .\04-DATA\exports\logs | Select-Object Name, Length, LastWriteTime
```
