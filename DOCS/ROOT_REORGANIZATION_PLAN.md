# Plan de Reorganización de la Raíz

Este documento describe los pasos seguros para consolidar elementos sueltos en la raíz del repositorio hacia carpetas canónicas sin romper los imports.

Estructura canónica de la raíz:
- `00-ROOT/`, `01-CORE/`, `04-DATA/`, `05-LOGS/`, `09-DASHBOARD/`
- `DOCS/`, `scripts/`, `tests/`, `test_data/`, `tools/`

Limpiezas pendientes identificadas:
- Eliminar la carpeta `monitoring/` de la raíz (es un shim) que reenvía a `01-CORE/monitoring`.
- Unificar la carpeta `data/` de la raíz dentro de `04-DATA/data/` preservando estructura y contenido.

Cómo ejecutar (Windows PowerShell):

```powershell
# Ensayo (dry-run) recomendado
python scripts/reorganize_root.py

# Aplicar solo la eliminación del shim de monitoring
python scripts/reorganize_root.py --apply --remove-monitoring-shim

# Aplicar solo la fusión de data
python scripts/reorganize_root.py --apply --merge-data

# Aplicar ambas acciones
python scripts/reorganize_root.py --apply --remove-monitoring-shim --merge-data
```

Seguridad y comportamiento:
- Dry-run por defecto: imprime el plan y guarda logs en `05-LOGS/system/reorg_*.log`.
- Los movimientos de archivos son idempotentes: si el destino ya existe con contenido idéntico, se elimina el origen.
- Los conflictos se omiten y se reportan; se recomienda revisión manual.
- No se tocan las carpetas canónicas ni el control de versiones/cachés.

Reversión (rollback):
- Los movimientos son renombres simples. Para revertir una acción aplicada:
  - Fusión de data: mover archivos de `04-DATA/data/` de vuelta a `data/` usando el log como guía.
  - Shim de monitoring: restaurar desde el historial de Git o recrear el shim si fuera necesario.

Pasos posteriores:
- Ejecutar un smoke test rápido para verificar imports y rutas de datos:
```powershell
$env:ICT_EXPORT_METRICS=1; $env:ICT_EXPORT_INTERVAL=2; `
$env:ICT_BASELINE_ENABLE=1; $env:ICT_BASELINE_INTERVAL=1; `
python .\main.py
```
Presiona `q` para salir. Revisa los logs en `05-LOGS/system/` por cualquier incidencia.

Notas:
- La carpeta `monitoring/` en la raíz es un shim y es seguro eliminarla una vez que todo el código importe desde `01-CORE/monitoring`.
- El exportador y el sistema de baseline ya leen/escriben bajo `04-DATA/metrics` y `04-DATA/data`.
