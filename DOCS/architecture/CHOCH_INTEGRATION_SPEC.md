# Especificación de Integración CHoCH (Enterprise v6.0)

Alcance: Aplicar memoria histórica CHoCH en todos los patrones SMC para mejorar la confirmación, la confianza y la selección de objetivos.

API Común
- adjust_confidence_with_memory(base_confidence, symbol, timeframe, break_level) -> 0..100
- predict_target_based_on_history(symbol, timeframe, direction, break_level, default_target=None) -> float|None
- calculate_historical_success_rate(symbol, timeframe, direction=None) -> 0..100
- find_similar_choch_in_history(symbol, timeframe, direction=None, break_level_range=None) -> List[events]

Campos de Salida Requeridos (por patrón)
- choch_target_hint: Optional[float]
- choch_bonus_applied: Optional[float]
- history_samples: Optional[int]

Flags de Configuración (por patrón)
- use_choch_memory: bool (por defecto False excepto en Silver Bullet)
- choch_confidence_max_bonus: float (por defecto 10.0)
- choch_level_lookback: int (por defecto 20)

Claves de Logging (ejemplo)
- "choch.memory.bonus": {symbol, timeframe, break_level, bonus, samples}
- "choch.memory.target_hint": {symbol, timeframe, break_level, target_hint}

Estimación del Nivel de Ruptura (Break Level)
- OB Mitigation: borde del order block (lado de entrada) o último swing.
- Liquidity Grab: nivel de la barrida de liquidez (high/low tomado) o pivote estructural inmediato.
- Judas Swing: pivote post‑sweep (pivote CHoCH).
- FVG: borde del FVG más cercano a la entrada (premium/discount edge).
- MSS/BOS: pivote que define la ruptura estructural (HTF para sesgo, LTF para entrada).

Calidad y Gating
- Gating opcional: requerir confirmación CHoCH para entradas que dependan de un reversal tras una barrida.
- Ajustar la confianza con bonus histórico (limitado por choch_confidence_max_bonus).
- Usar el target hint solo si mejora la relación riesgo/beneficio.

Rendimiento
- Añadir caché simple por (symbol,timeframe) para consultas CHoCH recientes en un tick/lote.
- Proteger llamadas con timeouts cortos; degradar de forma elegante si la memoria no está disponible.

Feedback de Resultado
- Al cerrar la operación, llamar a update_choch_outcome(id, outcome, pips, time_to_target) para mantener el aprendizaje de la memoria.

Pruebas
- Baselines por patrón; tras la integración debe mantenerse dentro de ±15% de señales salvo que el gating esté habilitado.
- Validar que los nuevos campos existan y sean válidos (sin NaN) y que los toggles desactiven la lógica según lo esperado.
