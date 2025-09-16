# Sistema de Alertas Avanzado (Advanced Alerting Subsystem)

## Objetivo
Proveer un subsistema de alertas extensible, deduplicado, con control de tasa y fan-out multi canal que complemente y eleve las capacidades del `alert_dispatcher` existente, sirviendo de capa estratégica para correlación y análisis.

## Checklist de Implementación
- [x] Crear carpeta `01-CORE/alerting/`
- [x] Definir modelos base (`models.py`)
- [x] Definir canales base (`channels.py`)
- [x] Implementar `AdvancedAlertManager` (`manager.py`)
- [x] Exponer API pública en `__init__.py`
- [ ] Integrar con `real_trading/alert_dispatcher.py`
- [ ] Integrar métricas (contador duplicados, tasa, severidades)
- [ ] Añadir documentación de uso en `QUICK_START.md`
- [ ] Añadir pruebas unitarias básicas
- [ ] Añadir canal opcional para Web/Dashboard (WebSocket / API)
- [ ] Persistencia avanzada (rotación, compresión, TTL)
- [ ] Correlación multi-evento (futuro)

## Arquitectura
```
[Producers] --> AdvancedAlertManager --> [Dedup] --> [RateLimit] --> [FanOut]
                                                    |              |-- ConsoleChannel
                                                    |              |-- FileChannel
                                                    |              |-- MemoryChannel
                                                    |              |-- CallbackChannel(s)
                                                    |              \-- (Futuros: WebSocket, Email, etc.)
```

### Componentes Clave
- `AdvancedAlert`: Dataclass ligera con timestamp, categoría, severidad, mensaje y metadatos.
- `AlertDedupPolicy`: Enum de políticas de deduplicación (NONE, MESSAGE_WINDOW, CATEGORY_SYMBOL_WINDOW).
- `AdvancedAlertManager`: Núcleo coordinador (rate limit, deduplicación ventana, fan-out canales, agregación duplicados críticos).
- Canales: Implementaciones simples con interfaz uniforme (`send(alert)`).

### Deduplicación
Se genera clave según la política configurada. Ventana configurable (`dedup_window_seconds`). Duplicados incrementan contador y actualizan metadatos, reenviando sólo si son de severidad alta o crítica.

### Rate Limiting
Ventana móvil de 60s, configurable `rate_limit_per_60s`. Rechazos registrados vía logger.

### Fan-Out
Cada canal implementa `send(alert)`. Fallos son aislados y loggeados sin detener el flujo.

## Uso Rápido
```python
from alerting import get_advanced_alert_manager
mgr = get_advanced_alert_manager()
# Registrar alerta
mgr.record_alert(
    category="risk",
    severity="high",
    message="Drawdown > 5% en sesión",
    symbol="EURUSD",
    meta={"dd": 0.051}
)
# Obtener recientes (para dashboard o depuración)
recientes = mgr.get_recent(50)
```

## Integración con Dispatcher Existente (Plan)
1. En `real_trading/alert_dispatcher.py` identificar puntos de emisión.
2. En cada emisión clave, añadir espejo hacia `AdvancedAlertManager` (mapping de severidades si difieren nomenclaturas).
3. Evitar duplicidad excesiva aplicando categorías sistemáticas: `trading`, `risk`, `data`, `infra`, `latency`, `pattern`.
4. Exponer hook para Dashboard: `mgr.get_recent()` + endpoint ligero.

## Métricas (Pendiente)
- Total alertas procesadas.
- Alertas deduplicadas (conteo por clave y severidad).
- Alertas descartadas por rate limit.
- Distribución de severidades por minuto.

## Estrategia de Pruebas (Pendiente)
- Deduplicación: Enviar mismo mensaje varias veces y validar contador.
- Rate limit: Forzar > N en 60s y validar rechazo.
- Fan-out: Mock canales y verificar invocaciones.
- Persistencia: Validar escritura JSONL.

## Futuras Extensiones
- Canal WebSocket en vivo.
- Reglas correlativas multi-evento (ej: 3 fallos de latencia + 1 error data => alerta compuesta).
- Persistencia con TTL + índice para búsqueda.
- Exportación a Prometheus / OpenTelemetry.

## Consideraciones de Rendimiento
Bloqueos mínimos (lock sólo en secciones críticas). Estructuras listas para reemplazo por colas asíncronas si se requiere throughput mayor.

## Seguridad / Robustez
- Canales aislados ante excepciones.
- Fallback logger si falla inicialización principal.
- Diseño idempotente en deduplicación.

---
Última actualización: (pendiente de actualizar al finalizar integración)
