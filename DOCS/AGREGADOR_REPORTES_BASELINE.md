# Agregador de Reportes Baseline

Este utilitario consolida los reportes `baseline_*.json` generados por `scripts/baseline_pattern_scan.py` en un resumen único.

## Uso (PowerShell / Windows)

```powershell
python -X utf8 .\scripts\aggregate_baseline_reports.py -i .\04-DATA\reports -o .\04-DATA\reports\baseline_summary.json
```

- `-i/--in-dir`: Directorio donde están los JSON de baseline.
- `-o/--out-file`: Ruta del archivo resumen a generar.

## Salida

Se genera `04-DATA/reports/baseline_summary.json` con:

- by_symbol_timeframe: Para cada símbolo + timeframe, métricas por detector
  - files_count: cantidad de archivos considerados
  - total_signals: cantidad total de señales
  - avg_confidence: confianza promedio (promedio de promedios por archivo)
  - max_confidence: máxima confianza observada
  - error_files: cantidad de archivos con error para ese detector
- global: Resumen global por detector y lista de errores de parseo

## Ejemplo de salida (resumido)

```json
{
  "meta": { "reports_dir": "04-DATA\\reports", "files_found": 6 },
  "by_symbol_timeframe": { "EURUSD": { "M5": { "silver_bullet": { "files_count": 1, "total_signals": 1 }}}},
  "global": { "detectors": { "silver_bullet": { "total_signals": 2 }}, "errors": [] }
}
```

## Notas

- Los archivos con clave `error` se listan en `global.errors` y no aportan métricas.
- El promedio de confianza global se calcula promediando la confianza media de cada archivo (no ponderado por número de señales).