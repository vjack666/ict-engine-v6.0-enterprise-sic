# Implementación FVG Real + CHoCH – Checklist y Plan

## 🎯 Objetivo
Reemplazar gradualmente la lógica placeholder en `ICTPatternDetector._detect_fvg_patterns()` por la detección real basada en `smart_money_concepts.fair_value_gaps.FairValueGapDetector`, manteniendo el enriquecimiento CHoCH y garantizando compatibilidad con tests.

## ✅ Recomendación de Implementación
- Mantener el uso principal de `FairValueGapDetector` para FVG.
- Reemplazo gradual del placeholder:
  - Fase A: Mantener fallback solo si no hay FVGs y el entorno es de test (control por `self.config.get('allow_fvg_placeholder_for_tests', True)`). Por defecto: `True` en tests, `False` en producción.
  - Fase B: Actualizar `tests/test_choch_integration_patterns.py` para generar un FVG real (3 velas con gap) y desactivar el placeholder por defecto.
- Añadir configuración mínima CHOCH al constructor de `ICTPatternDetector`:
  - `self.choch_config = config.get('choch_config', { 'enabled': True, 'min_historical_periods': 20, 'confidence_boost_factor': 0.15 })`
- Mejorar metadata del patrón FVG mapeado:
  - `status`, `fill_percentage`, `score`, `confidence_source: 'smc_fvg_detector'`, `candle_index` (si viene del FVG SMC).
- Evaluar integración opcional con `FVGMemoryManager` para thresholds adaptativos (no bloquear ahora).

## 📐 Contratos y Compatibilidad
- `ICTPattern` requiere: `pattern_type`, `timeframe`, `symbol`, `entry_price`, `confidence`, `timestamp`, `metadata`. Se cumple.
- `test_choch_integration_patterns.py` exige: al menos 1 FVG y presencia de metadatos CHOCH (`choch_historical_bonus`, `choch_success_rate`). Se cumple con FVG real o placeholder.
- No hay tests que aserten `gap_pips` o `direction` → se puede enriquecer metadata sin romper.

## 🗺️ Plan por Fases

### Fase A — Control del Placeholder
- [ ] Agregar flag `allow_fvg_placeholder_for_tests` en `ICTPatternDetector.__init__`.
- [ ] Modificar `_detect_fvg_patterns()` para usar el flag y solo activar placeholder si `True`.
- [ ] Documentar comportamiento por defecto (prod: False, tests: True).

### Fase B — Tests con FVG Real
- [ ] Actualizar `tests/test_choch_integration_patterns.py` para construir 3 velas con gap real (i-1 y i+1 no solapan) y verificar metadata CHOCH.
- [ ] Desactivar placeholder por defecto (`allow_fvg_placeholder_for_tests = False`).
- [ ] Ejecutar suite de tests y validar compatibilidad.

### Enriquecimiento Metadata FVG
- [ ] Añadir en el mapeo a `ICTPattern.metadata` los campos: `status`, `fill_percentage`, `score`, `confidence_source`, `candle_index`.
- [ ] Mantener `gap_pips`, `direction`, `fvg_id`, `memory_enhanced` si existe.

### Configuración CHOCH en Detector
- [ ] Añadir `self.choch_config` en `ICTPatternDetector.__init__`.
- [ ] (Opcional) Inicializar `self.choch_memory` si se migra a objeto; por ahora, mantener funciones libres.

### (Opcional) Integración FVGMemoryManager
- [ ] Evaluar importar `analysis.fvg_memory_manager.FVGMemoryManager` para thresholds adaptativos.
- [ ] No bloquear el pipeline si falla (opt-in, lazy import).

## 🧪 Criterios de Aceptación
- [ ] `_detect_fvg_patterns()` usa detector real y respeta el flag del placeholder.
- [ ] CHOCH boost aplicado y metadata CHOCH presente en FVGs reales.
- [ ] Tests de integración pasan con DF que crea FVG real.
- [ ] Sin regresión en BOS/MSS/otros smoke tests.

## 🚀 Pasos Siguientes (ejecutables)
1) Implementar flag `allow_fvg_placeholder_for_tests` y condicionamiento del fallback.
2) Enriquecer metadata FVG desde objeto SMC al `ICTPattern`.
3) Actualizar test para generar FVG real y retirar dependencia del `len % 4`.
4) Correr `pytest -q` y revisar logs/outputs.

## 🧹 Eliminación de Duplicados

### Duplicados de Tipos y Modelos
- [x] Unificar dataclasses `FairValueGap`: usar la de `smart_money_concepts.fair_value_gaps` como fuente de verdad. (Legacy docstrings actualizados)
- [x] Crear adapter ligero cuando se necesite mapear a `ICTPattern` (mantener `metadata` enriquecida). Integrado en `_detect_fvg_patterns`.
- [ ] Documentar y deprecar el uso de `ict_engine.ict_types.FairValueGap` donde no sea imprescindible.

### Detección y Pipelines
- [ ] Asegurar que `ICTPatternDetector._detect_fvg_patterns()` usa solo `FairValueGapDetector` (SMC).
- [ ] Mantener `_find_fair_value_gaps` de `analysis.pattern_detector` exclusivamente como utilidad de confluencia/dashboard (marcar como legacy en docstrings).
- [ ] Añadir deduplicación de patrones en `_detect_fvg_patterns()` por clave `(symbol, timeframe, fvg_id)` o por rango de precios y `timestamp` cuando `fvg_id` no esté disponible.

### Imports y Logging
- [ ] Consolidar imports FVG/CHOCH para evitar duplicados y rutas redundantes.
- [ ] Usar un único origen de logging para eventos FVG+CHoCH (mantener `log_trading_decision_smart_v6`).

### Memoria y Persistencia
- [x] Evitar duplicados en `FVGMemoryManager`: clave única `(symbol, timeframe, fvg_id)`; si falta id, usar hash `(direction, high_price, low_price, timestamp)`. Pruebas: `tests/test_fvg_memory_dedup.py`.
- [x] Integrar `FVGMemoryManager` en `_detect_fvg_patterns()` como opt-in (`enable_fvg_memory_persistence`). Prueba: `tests/test_detector_fvg_memory_integration.py`.
- [ ] Asegurar limpieza de FVGs expirados/mitigados antes de insertar nuevos.

### Criterios de Aceptación (Deduplicación)
- [ ] La salida de `ICTPatternDetector.detect_patterns()` no contiene FVGs duplicados para el mismo `symbol/timeframe` en una ejecución.
- [ ] No hay conflictos de tipos homónimos en Pylance/linters relacionados con `FairValueGap`.
- [ ] Los logs y la memoria no guardan entradas duplicadas del mismo FVG.

## 📎 Notas
- Mantener los cambios acotados a `ICTPatternDetector` y tests de integración.
- Evitar modificaciones en la lógica interna de `FairValueGapDetector` salvo bugs críticos.
- Documentar en `PLAN_INTEGRACION_CHOCH_FVG_MSS_BOS.md` el estado de cada checkbox.
