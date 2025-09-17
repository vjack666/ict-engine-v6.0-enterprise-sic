# Guía de Data Management - ICT Engine v6.0 Enterprise

## 1. Propósito
Establecer la arquitectura, estándares operativos y prácticas de gestión de datos para garantizar: disponibilidad consistente, integridad verificable, trazabilidad, eficiencia de recursos y extensibilidad controlada en el ecosistema ICT Engine v6.0 Enterprise.

## 2. Alcance
Incluye módulos de ingesta (MT5, descarga histórica), orquestación híbrida (warm-up + enhancement), validación, persistencia en memoria y disco (cache, snapshots, exports), monitoreo de salud y puente hacia trading en vivo.

## 3. Arquitectura Lógica
Capas:
1. Source Layer (MT5 / Fallback Interfaces)
2. Ingestion & Downloaders (`mt5_data_manager`, `advanced_candle_downloader`)
3. Orchestration (`ict_data_manager` híbrido)
4. Validation & Quality (`data_validator_real_trading`)
5. Normalization & Context (context cache, unified market memory si disponible)
6. Persistence (volátil: memory_persistence / duradera: json, exports, reports)
7. Bridging (`real_trading_bridge`) y Consumers (analyzers, dashboard, trading engine)
8. Monitoring & Audit (health monitor, black box logger, metrics baselines)

Flujo general: Source -> Ingestion -> Orchestration -> Validation -> Normalization -> Persistence -> Bridge -> Consumers -> Feedback (metrics & health) -> Ajustes.

## 4. Flujos Clave
### 4.1 Warm-Up Híbrido
- Objetivo: disponibilidad mínima operativa < 30s.
- Criterios: símbolos críticos + timeframes críticos + barras mínimas.
- Resultado: cache inicial + readiness flag.

### 4.2 Enhancement Background
- Expande símbolos/timeframes y rellena bars_optimal.
- Controlado por hilo dedicado, baja prioridad de CPU.

### 4.3 Validación Continua
- Gaps, completitud, límites de spread, coherencia temporal.
- Flags de severidad: INFO/WARN/CRITICAL.

### 4.4 Persistencia de Estado Contextual
- Snapshots JSON (`market_context_state.json`).
- Historias históricas en `historical_analysis/` con rotación.

### 4.5 Bridge a Trading
- Normaliza payload estructurado (símbolo, timeframe, contexto, latencia origen).
- Garantiza no bloquear pipeline de ingestión.

## 5. Persistencia
Tipos:
- Volátil regenerable: `data/memory_persistence/` (TTL corto, no versionado).
- Semipersistente analítica: exports CSV/JSON bajo demanda.
- Auditoría y salud: `04-DATA/reports/`, `04-DATA/logs/`.
- Estado de sistema: `data/system_status.json` consolidado.

Políticas:
- No almacenar datos duplicados si pueden recalcularse (< 2s costo).
- JSON para snapshots estructurados; CSV para datasets tabulares externos.
- Rotación logs: tamaño o ventana temporal (pendiente de parametrizar UI).
 
TTL recomendados:
- Snapshots contexto: 1 por ciclo de análisis (sobrescritura incremental).
- Estados históricos (`historical_analysis/`): retenidos 7-14 días (luego compactar o purgar).
- Cache OHLC crítico: refresh cada 15 min (configurable `cache_refresh_minutes`).
- Métricas base: persistir sólo baseline y últimos N=50 agregados.

Formato JSON estándar:
{
  "version": 1,
  "generated_at": "ISO8601",
  "source": "<módulo origen>",
  "payload": { ... },
  "meta": { "latency_ms": <int>, "completeness": <float> }
}

## 6. Estándares y Convenciones
- Naming módulos: snake_case descriptivo; sufijos: `_manager`, `_monitor`, `_bridge`, `_singleton`.
- Columnas CSV inventario: `module,path,component_type,responsibility,...` (ver `data_management_inventory.csv`).
- Timeframes soportados enumerados en config central (`ICT_DATA_CONFIG`).
- Separar fallback vs mock: Fallback nunca inventa datos, sólo retorna None/estado controlado.
- Config inmutable en runtime salvo rutas y thresholds (mediante capa de adaptación futura).

## 7. Métricas Clave
- warm_up_time (s), coverage (% símbolos/timeframes con completeness >= threshold), failed_downloads, enhancement_cycles, validation_fail_rate, bridge_latency_ms.
- Baselines iniciales en `performance_initial.json`.
- Métricas deben exponer: valor actual, delta vs baseline, tendencia (↑ ↓ →).

## 8. Calidad y Validación
Checklist ingestión:
1. Timestamp monotónico.
2. No gaps > max_gap_minutes.
3. Completeness >= minimum_completeness (warn si < optimal_completeness).
4. Spread dentro de tolerance.
5. Orden cronológico estable.

Niveles de severidad:
- INFO: desviación menor dentro de tolerancias.
- WARN: riesgo potencial (seguir procesando, marcar para revisión).
- CRITICAL: detener ingestión parcial y aislar símbolo/timeframe.

Acciones automáticas:
- Gap detectado: marcar para refetch en enhancement cycle.
- Completeness baja: incrementar prioridad en cola de enhancement.
- Spread anómalo: descartar última barra y esperar siguiente confirmación.

## 9. Gestión de Errores
- Retrys exponenciales en conexión MT5 (máx 3).
- Fallback silencioso sólo si no afecta trading (registrar WARNING).
- CRITICAL: pérdida de conexión prolongada, corrupción JSON, latencia > SLA.

## 10. Seguridad y Aislamiento
- Nunca exponer credenciales MT5 en logs.
- Paths normalizados mediante `Path` y control de existencia.
- Evitar escritura concurrente no atómica (usar write temp + rename para futuros snapshots críticos).

## 11. Roadmap Evolutivo
Short-term (≤2 semanas):
- UI métricas cobertura.
- Parametrizar rotación snapshots.
- Export incremental diferido.

Hardening adicional propuesto:
- Lock de escritura atómica (tmp -> rename) para evitar corrupción concurrente.
- Firma hash (SHA256) de snapshots críticos para verificar integridad.
- Registro de latencia por etapa (ingestión, validación, persistencia) en trace compacto.

Mid-term (≤2 meses):
- Catalogación automática + firma integridad.
- Compresión histórica LZ4/ZSTD.
- Storage tiered (rápido vs frío).

Long-term:
- Data lineage grafado.
- Observabilidad con tracing distribuido.
- Política adaptativa de retención basada en frecuencia de acceso.

## 12. Operaciones (Runbook Resumido)
Warm-up manual: invocar `ICTDataManager.initialize()`.
Forzar enhancement: método público `start_enhancement_cycle()` (si disponible) o trigger planificado.
Verificar salud: monitor + estado consolidado en `system_status.json`.

## 13. Glosario
- Warm-up: Carga mínima viable.
- Enhancement: Enriquecimiento progresivo no bloqueante.
- Completeness: % de barras presentes vs objetivo.
- Snapshot: Estado puntual serializado.
- Bridge: Adaptador último tramo hacia consumidor.

## 14. Referencias
- Inventario: `DOCS/data_management_inventory.csv`
- Config central: `ict_data_manager.py` (`ICT_DATA_CONFIG`)
- Métricas base: `04-DATA/performance_initial.json`

## 15. Checklist de Revisión Data Release
- [ ] Warm-up < objetivo (<= 30s)
- [ ] Coverage símbolos críticos >= 95%
- [ ] Gaps críticos = 0
- [ ] Latencia bridge < 250 ms
- [ ] Sin CRITICAL abiertos en validación
- [ ] Hash snapshots verificado (si implementado)
- [ ] Logs sin credenciales ni datos sensibles

## 16. Anexos
### 16.1 Esquema Campos Métricas (Propuesto)
metric_name,scope,type,unit,description
warm_up_time,system,gauge,seconds,Duración última inicialización mínima
coverage_ratio,data,gauge,percent,Cobertura global símbolos*timeframes
failed_downloads,data,counter,count,Descargas fallidas acumuladas
validation_fail_rate,quality,gauge,percent,Porcentaje fallos validación sobre total
bridge_latency_ms,bridge,histogram,ms,Latencia generación payload -> disponibilidad

### 16.2 Plantilla Registro de Evento Crítico
{
  "ts": "ISO8601",
  "level": "CRITICAL|WARN",
  "module": "<nombre>",
  "symbol": "EURUSD",
  "timeframe": "M15",
  "event": "data_gap_detected",
  "details": { "missing_bars": 12 },
  "action": "scheduled_refetch"
}

### 16.3 Estrategia de Compactación Histórica (Draft)
1. Agrupar snapshots > 7 días en paquetes semanales.
2. Comprimir con ZSTD nivel 6.
3. Generar índice (manifest.json) con offsets y hash.
4. Eliminar archivos individuales tras verificación.

### 16.4 Políticas de Retención (Propuesta Inicial)
- Logs crudos: 14 días.
- Snapshots contexto: 7 días (rotación diaria).
- Métricas baseline: sólo versión vigente + histórico mínimo.
- Exports manuales: permanentes hasta auditoría (taggear).

---
Versión inicial de la guía. Completar en iteraciones con detalles de métricas runtime y esquema de serialización formal.
# Guía de Data Management (DM)

> Estado: Versión inicial (v0.1) – enfocada en entendimiento operativo y extensibilidad.

## 1. Objetivos del Subsistema
- Garantizar captura consistente de datos de mercado y derivados analíticos.
- Mantener persistencia eficiente (memoria + disco) con degradación controlada.
- Proveer datos limpios y estructurados a: análisis histórico, módulos SMC, trading, dashboard y validaciones.
- Asegurar trazabilidad (lineage) desde fuentes hasta outputs en reportes y señales.

## 2. Alcance
Incluye: cache de velas, snapshots analíticos, memoria temporal, exportaciones, reportes y estado del sistema. Excluye: lógica de estrategia, ejecución de órdenes, motor de riesgo (solo consumen outputs).

## 3. Arquitectura Lógica
```
[FUENTES] --> [INGESTION] --> [NORMALIZATION] --> [CACHE/MEMORIA] --> [TRANSFORMERS/ANALYTICS] --> [PERSISTENCIA] --> [CONSUMIDORES]
```
Componentes clave:
- Ingestion: adaptadores de feeds (ej. MT5 / archivos locales / APIs).
- Normalization: conversión a formato interno (OHLCV extendido + metadatos).
- Cache Layer: acceso rápido (en memoria) con TTL y política de reemplazo ligera.
- Persistence Layer: JSON estructurado + exports (CSV/JSON) + logs especializados.
- Analytics Snapshot: outputs modularizados (order blocks, patrones, estructura mercado, contexto multi-timeframe).
- Consumers: dashboard, validadores, motor de trading, optimizaciones.

## 4. Estructura Relevante de Carpetas
```
04-DATA/
  cache/                # Caches volátiles o semi-persistentes
  memory_persistence/   # Estados recientes (ej. order blocks live)
  exports/              # Datos listos para análisis externo
  reports/              # Reportes generados (rendimiento, auditoría)
  logs/                 # Logs específicos de data ops
  performance_initial.json

09-DASHBOARD/
  data/                 # Data helpers para visualización

00-ROOT/requirements.txt (dependencias)
```

## 5. Flujo de Datos (Ejemplo Order Blocks)
1. Solicitud desde dashboard → servicio reutiliza caché si dentro de TTL.
2. Si expira: invoca analizador real (SMC/estructura) → genera bloques.
3. Se actualiza `deque` histórico en memoria y se persiste snapshot a `04-DATA/memory_persistence/order_blocks_live.json`.
4. Métricas se actualizan (latencia, hits/misses, tamaño caché, historial).
5. Dashboard renderiza tabla + gráfico + métricas.

## 6. Persistencia: Patrones y Convenciones
| Tipo | Formato | Ubicación | Política | Ejemplos |
|------|---------|----------|----------|----------|
| Snapshot volátil | JSON | `memory_persistence/` | overwrite incremental | `order_blocks_live.json` |
| Export analítico | CSV/JSON | `exports/` | append controlado | series históricas |
| Reporte | Markdown/JSON | `reports/` | versionado por timestamp | auditoría |
| Cache técnica | JSON/lru/in-memory | `cache/` | TTL / size-bounded | velas, contexto |
| Estado sistema | JSON | `system_status.json` | overwrite | health global |

Convenciones:
- Timestamps en ISO 8601 (UTC preferido) o con zona clara.
- Claves snake_case.
- Campos mínimos para velas: `timestamp, open, high, low, close, volume`.
- Para snapshots analíticos incluir: `symbol, timeframe, generated_at, source, payload`.

## 7. Estándares de Calidad de Datos
- Validación mínima: rango lógico OHLC (low <= open/close/high).
- Verificación de gaps si periodicidad fija (alerta si > 1 intervalo faltante).
- Sanitización de duplicados por `(symbol,timeframe,timestamp)` → mantener último.
- Métricas de integridad (error rate ingestión) opcional futura.

## 8. Métricas Recomendadas (Actual y Futuras)
| Métrica | Descripción | Fuente | Uso |
|---------|-------------|--------|-----|
| cache_hits | Número de respuestas servidas desde caché | servicio realtime | tuning TTL |
| cache_misses | Re-cálculos obligados | servicio realtime | ajuste refresh |
| avg_latency_ms | Promedio de cálculo | servicio realtime | optimización CPU |
| last_calculation_at | Último cálculo real | snapshot | monitoreo frescura |
| history_length | Número de snapshots retenidos | deque | dimensionamiento |
| export_events | Conteo de exportaciones | pipeline export | auditoría |
| data_gaps_detected | Gaps en series | validador futuro | alertas |

## 9. Lineage / Trazabilidad (Modelo Simplificado)
```
(symbol,timeframe) -> raw_candles -> normalized_frame -> analytics_context -> detectors -> snapshot(order_blocks)
```
Recomendado mantener (futuro):
- ID hash derivado de `symbol|timeframe|first_ts|last_ts|rows` para reproducibilidad.
- Registro de versión del analizador (ej. `order_blocks_algo_version`).

## 10. Buenas Prácticas Operativas
- No mezclar datos simulados en rutas reales de producción.
- Limitar tamaño de historial en memoria (ej. 100–500 snapshots) para evitar presión GC.
- Evitar flush simultáneo de múltiples heavy analytics (escalar por ventanas). 
- Implementar backoff progresivo si errores consecutivos > N.
- Rotar exports masivos por día (`YYYYMMDD` en nombre archivo).

## 11. Estrategia de Retención (Sugerida)
| Tipo | Retención | Acción |
|------|-----------|--------|
| Cache memoria | Minutos | Descartar al expirar |
| Snapshots volátiles | Horas | Rotar por timestamp si > límite |
| Exports analíticos | Meses | Archivar comprimido (zip) |
| Logs | 30-90 días | Compactar/archivar |
| Reports auditoría | >= 1 año | Evidencia cumplimiento |

## 12. Riesgos y Mitigaciones
| Riesgo | Impacto | Mitigación |
|--------|---------|-----------|
| Cache staleness | Decisiones basadas en datos viejos | TTL + métricas frescura |
| Corrupción JSON | Fallo parsing | Escritura atómica (tmp + move) futura |
| Crecimiento sin control | Uso excesivo disco | Políticas retención |
| Bloqueos IO | Latencia en dashboard | Asincronía / colas futuras |

## 13. Extensión Inmediata Recomendada
- Añadir script `data_audit.py` para: detectar duplicados, gaps y exportar reporte.
- Automatizar inventario (ver CSV incluido) generando hash y clasificación de cada módulo.
- Añadir bandera `algo_version` en cada snapshot analítico.

## 14. Formato CSV Inventario (Adjunto)
Archivo: `DOCS/data_management_inventory.csv`
Columnas:
```
module,path,component_type,responsibility,inputs,outputs,persistence,update_frequency,owner,status
```

## 15. Roadmap Breve
| Fase | Feature | Prioridad |
|------|---------|-----------|
| F1 | Auditor de calidad (gaps/duplicados) | Alta |
| F2 | Export incremental consolidado | Media |
| F3 | Lineage hash y versionado | Alta |
| F4 | Compresión / rotación automática | Media |
| F5 | API interna de metadatos | Baja |

## 16. Glosario Rápido
- Snapshot: Estado puntual calculado (no streaming continuo).
- TTL: Tiempo máximo de vida antes de invalidarse.
- Lineage: Trazabilidad de derivación de datos.
- Persistencia volátil: Estado que puede regenerarse sin pérdida funcional.

---
Fin versión 0.1 – Ajustes y ampliaciones bienvenidos.
