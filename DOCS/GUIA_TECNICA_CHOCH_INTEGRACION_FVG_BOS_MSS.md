# Guía Técnica: Integración CHoCH en FVG, BOS y MSS

## Objetivo
Dejar operativa la integración de memoria histórica CHoCH para enriquecer la confianza y el contexto de los patrones FVG, BOS y MSS, de forma consistente con el resto de patrones.

## Módulos Modificados
- `01-CORE/ict_engine/pattern_detector.py`: FVG con bonus histórico CHoCH.
- `01-CORE/analysis/pattern_detector.py`: BOS con ajuste de confianza + narrativa CHoCH.
- `01-CORE/ict_engine/displacement_detector_enterprise.py`: MSS/Displacement con enriquecimiento suave CHoCH.

## API CHoCH utilizada
- `compute_historical_bonus(symbol, timeframe, break_level) -> {historical_bonus, samples}`
- `calculate_historical_success_rate(symbol, timeframe, direction=None) -> float`
- `adjust_confidence_with_memory(base_confidence, symbol, timeframe, break_level) -> float`

## Parámetros y Heurísticas
- FVG: Base `confidence=0.72`. Se suma `historical_bonus` en rango [-20,+20] y se satura a [0,100].
- BOS: `strength` tras momentum se ajusta con `adjust_confidence_with_memory`. Narrativa añade `CHOCH+{bonus}`.
- MSS: `target_estimation` se multiplica por `1 + (bonus/500)`. Se registran `choch_bonus` y `choch_success_rate` en `sic_stats`.

## Metadatos añadidos
- FVG: `choch_historical_bonus`, `choch_samples`, `choch_success_rate`, `confidence_original_pre_choch`.
- BOS: `metadata.choch_historical_bonus`, `metadata.choch_success_rate` + narrativa extendida.
- MSS: `sic_stats.choch_bonus`, `sic_stats.choch_success_rate`.

## Logging
- Eventos: `FVG_CHOCH_MEMORY_APPLIED`, `FVG_CHOCH_MEMORY_ERROR`, uso de `_logger`/fallback en BOS y `self.logger` en MSS.

## Validación Rápida
1) Ejecutar escaneo baseline para un símbolo/timeframe:
```powershell
python -X utf8 .\scripts\baseline_pattern_scan.py -s AUDUSD -t M5 -n 600 -o .\04-DATA\reports
```
2) Confirmar que no hay errores en consola y que se generan reportes en `04-DATA/reports`.
3) Revisar logs en `05-LOGS/ict_signals/` y `05-LOGS/ict_signals/*.log` para ver metadatos CHoCH.

## Próximos pasos
- Sustituir placeholders de detección (FVG/BOS locales) por lógica completa de cada patrón.
- Añadir cache en consultas CHoCH si se usa en bucles intensivos.
- Crear pruebas unitarias focalizadas por módulo.
