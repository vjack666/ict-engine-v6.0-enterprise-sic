
#!/usr/bin/env python3
# ---
# **🔄 ACTUALIZACIÓN POST-REORGANIZACIÓN - COMPLETADA**
# **Fecha:** 2025-08-10 12:45:21 (EJECUTADO EXITOSAMENTE)
# **Estado:** PROCESO COMPLETADO - MANTENIDO PARA AUDITORÍA
# **Proceso:** Actualización automática de rutas tras reorganización enterprise
# **Nueva estructura:** 01-CORE/, 02-TESTS/, 03-DOCUMENTATION/, 04-DATA/, 05-LOGS/, 06-TOOLS/, 07-DEPLOYMENT/, 08-ARCHIVE/
# **Script:** update_bitacoras_post_reorganization.py
# **Nota:** Este script ya cumplió su propósito. Se mantiene para trazabilidad y futuras referencias.
# ---
# **Estado:** PROCESO COMPLETADO - MANTENIDO PARA AUDITORÍA
# **Proceso:** Actualización automática de rutas tras reorganización enterprise
# **Nueva estructura:** 01-CORE/, 02-TESTS/, 03-DOCUMENTATION/, 04-DATA/, 05-LOGS/, 06-TOOLS/, 07-DEPLOYMENT/, 08-ARCHIVE/
# **Script:** update_bitacoras_post_reorganization.py
# **Nota:** Este script ya cumplió su propósito. Se mantiene para trazabilidad y futuras referencias.
# ---
"""
🔄 ACTUALIZADOR DE BITÁCORAS POST-REORGANIZACIÓN
===============================================

Script que actualiza todas las bitácoras del proyecto para reflejar 
la nueva estructura enterprise organizada en:

00-ROOT/
01-CORE/
02-TESTS/
03-DOCUMENTATION/
04-DATA/
05-LOGS/
06-TOOLS/
07-DEPLOYMENT/
08-ARCHIVE/

Fecha: 2025-08-10
Autor: GitHub Copilot
Protocolo: REGLA #11 - Actualización Post-Reorganización
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Any

# Configuración
PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKUP_SUFFIX = "_backup_pre_reorganization"

# Mapeo de rutas antiguas a nuevas
PATH_MAPPINGS = {
    # Core directories
    "01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/core/": "01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/core/",
    "01-CORE/01-CORE/01-CORE/01-CORE/utils/": "01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/utils/",
    
    # Tests
    "02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/tests/": "02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/tests/",
    "02-TESTS/": "02-TESTS/",
    
    # Documentation
    "03-DOCUMENTATION/technical/03-DOCUMENTATION/technical/03-DOCUMENTATION/technical/03-DOCUMENTATION/technical/docs/": "03-DOCUMENTATION/technical/03-DOCUMENTATION/technical/03-DOCUMENTATION/technical/03-DOCUMENTATION/technical/03-DOCUMENTATION/technical/docs/",
    "03-DOCUMENTATION/": "03-DOCUMENTATION/",
    
    # Data
    "04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/data/": "04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/data/",
    "04-DATA/04-DATA/04-DATA/04-DATA/cache/": "04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/cache/",
    "04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/data/04-DATA/data/candles/": "04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/data/04-DATA/data/candles/",
    "04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/data/04-DATA/data/backtest_results/": "04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/data/04-DATA/data/backtest_results/",
    
    # Logs
    "05-LOGS/application/05-LOGS/application/05-LOGS/application/05-LOGS/application/05-LOGS/application/logs/": "05-LOGS/application/05-LOGS/application/05-LOGS/application/05-LOGS/application/05-LOGS/application/05-LOGS/application/logs/",
    
    # Tools
    "06-TOOLS/backtest-original/": "06-TOOLS/backtest-original/",
    "06-TOOLS/scripts-original/": "06-TOOLS/scripts-original/",
    "06-TOOLS/dashboard-original/": "06-TOOLS/dashboard-original/",
    
    # Archive
    "08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/blackbox/": "08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/blackbox/",
    "08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/sistema/": "08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/sistema/",
}

# Referencias específicas que necesitan actualización
SPECIFIC_MAPPINGS = {
    # Archivos específicos
    "01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/core/ict_engine/pattern_detector.py": "01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/core/ict_engine/pattern_detector.py",
    "01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/core/ict_engine/advanced_patterns/breaker_blocks_enterprise_v62.py": "01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/core/ict_engine/advanced_patterns/breaker_blocks_enterprise_v62.py",
    "01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/utils/mt5_data_manager.py": "01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/utils/mt5_data_manager.py",
    "02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/tests/modular_ict_candidato2_updated.py": "02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/tests/modular_ict_candidato2_updated.py",
    
    # Imports específicos
    "from 01-CORE.core.": "from 01-CORE.core.",
    "from 01-CORE.utils.": "from 01-CORE.utils.",
    "import 01-CORE.core.": "import 01-CORE.core.",
    "import 01-CORE.utils.": "import 01-CORE.utils.",
}

def find_bitacora_files() -> List[Path]:
    """Encuentra todos los archivos de bitácora en el proyecto."""
    bitacora_files = []
    
    patterns = [
        "**/bitacora*",
        "**/*bitacora*",
        "**/BITACORA*",
        "**/*BITACORA*",
        "**/*.log",
    ]
    
    for pattern in patterns:
        files = list(PROJECT_ROOT.glob(pattern))
        bitacora_files.extend(files)
    
    # Filtrar solo archivos de texto/markdown/log
    valid_extensions = {'.md', '.txt', '.log', '.py'}
    bitacora_files = [f for f in bitacora_files if f.suffix.lower() in valid_extensions]
    
    # Remover duplicados
    return list(set(bitacora_files))

def backup_file(file_path: Path) -> Path:
    """Crea backup de un archivo antes de modificarlo."""
    backup_path = file_path.with_suffix(file_path.suffix + BACKUP_SUFFIX)
    
    if not backup_path.exists():
        backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
        print(f"   📁 Backup creado: {backup_path.name}")
    
    return backup_path

def update_paths_in_content(content: str) -> Tuple[str, int]:
    """Actualiza todas las referencias de rutas en el contenido."""
    updates_count = 0
    updated_content = content
    
    # Actualizar mapeos específicos primero
    for old_ref, new_ref in SPECIFIC_MAPPINGS.items():
        if old_ref in updated_content:
            updated_content = updated_content.replace(old_ref, new_ref)
            updates_count += updated_content.count(new_ref) - content.count(new_ref)
    
    # Actualizar mapeos generales
    for old_path, new_path in PATH_MAPPINGS.items():
        # Buscar referencias de archivos
        pattern = re.compile(r'\b' + re.escape(old_path) + r'([^\s\'"]*)', re.IGNORECASE)
        matches = pattern.findall(updated_content)
        
        if matches:
            for match in matches:
                old_full = old_path + match
                new_full = new_path + match
                updated_content = updated_content.replace(old_full, new_full)
                updates_count += 1
    
    return updated_content, updates_count

def add_reorganization_note(content: str, file_path: Path) -> str:
    """Agrega una nota sobre la reorganización al archivo."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    reorganization_note = f"""
---
**🔄 ACTUALIZACIÓN POST-REORGANIZACIÓN**
**Fecha:** {timestamp}
**Proceso:** Actualización automática de rutas tras reorganización enterprise
**Nueva estructura:** 01-CORE/, 02-TESTS/, 03-DOCUMENTATION/, 04-DATA/, 05-LOGS/, 06-TOOLS/, 07-DEPLOYMENT/, 08-ARCHIVE/
**Script:** {Path(__file__).name}
---

"""
    
    # Agregar al inicio del archivo
    if file_path.suffix.lower() == '.md':
        # Para Markdown, agregar después del título principal si existe
        lines = content.split('\n')
        insert_position = 0
        
        for i, line in enumerate(lines):
            if line.startswith('#') and i < 5:  # Título principal en las primeras 5 líneas
                insert_position = i + 1
                break
        
        lines.insert(insert_position, reorganization_note)
        return '\n'.join(lines)
    else:
        # Para otros archivos, agregar al inicio
        return reorganization_note + '\n' + content

def update_bitacora_file(file_path: Path) -> Dict[str, Any]:
    """Actualiza un archivo de bitácora específico."""
    result = {
        'file': str(file_path.relative_to(PROJECT_ROOT)),
        'success': False,
        'updates_count': 0,
        'backup_created': False,
        'error': None
    }
    
    try:
        print(f"\n🔍 Procesando: {file_path.relative_to(PROJECT_ROOT)}")
        
        # Leer contenido original
        original_content = file_path.read_text(encoding='utf-8')
        
        # Crear backup
        backup_path = backup_file(file_path)
        result['backup_created'] = True
        
        # Actualizar rutas
        updated_content, updates_count = update_paths_in_content(original_content)
        
        # Agregar nota de reorganización
        if updates_count > 0 or 'REORGANIZACIÓN' not in original_content:
            updated_content = add_reorganization_note(updated_content, file_path)
            updates_count += 1
        
        # Escribir archivo actualizado
        if updates_count > 0:
            file_path.write_text(updated_content, encoding='utf-8')
            print(f"   ✅ Actualizado: {updates_count} cambios aplicados")
        else:
            print(f"   ℹ️  Sin cambios necesarios")
        
        result['success'] = True
        result['updates_count'] = updates_count
        
    except Exception as e:
        result['error'] = str(e)
        print(f"   ❌ Error: {e}")
    
    return result

def generate_update_report(results: List[Dict]) -> str:
    """Genera un reporte del proceso de actualización."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    total_files = len(results)
    successful = len([r for r in results if r['success']])
    failed = total_files - successful
    total_updates = sum(r['updates_count'] for r in results)
    
    report = f"""# 📋 REPORTE DE ACTUALIZACIÓN DE BITÁCORAS POST-REORGANIZACIÓN

**Fecha:** {timestamp}
**Proceso:** Actualización automática de rutas en bitácoras
**Script:** {Path(__file__).name}

## 📊 RESUMEN EJECUTIVO

- **Total de archivos procesados:** {total_files}
- **Actualizaciones exitosas:** {successful}
- **Archivos con errores:** {failed}
- **Total de cambios aplicados:** {total_updates}
- **Tasa de éxito:** {(successful/total_files*100):.1f}%

## 🔄 NUEVA ESTRUCTURA APLICADA

```
00-ROOT/           (archivos raíz)
01-CORE/           (01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/core/, 01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/01-CORE/utils/)
02-TESTS/          (02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/02-TESTS/integration/tests/, 02-TESTS/)
03-DOCUMENTATION/  (03-DOCUMENTATION/technical/03-DOCUMENTATION/technical/03-DOCUMENTATION/technical/03-DOCUMENTATION/technical/03-DOCUMENTATION/technical/03-DOCUMENTATION/technical/docs/, 03-DOCUMENTATION/)
04-DATA/           (04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/data/, 04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/04-DATA/cache/, 04-DATA/data/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/data/04-DATA/data/candles/, 04-DATA/data/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/04-DATA/04-DATA/04-DATA/data/04-DATA/data/04-DATA/data/backtest_results/)
05-LOGS/           (05-LOGS/application/05-LOGS/application/05-LOGS/application/05-LOGS/application/05-LOGS/application/05-LOGS/application/05-LOGS/application/logs/)
06-TOOLS/          (06-TOOLS/backtest-original/, 06-TOOLS/scripts-original/, 06-TOOLS/dashboard-original/)
07-DEPLOYMENT/     (preparado para deploy)
08-ARCHIVE/        (08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/blackbox/, 08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/08-ARCHIVE/legacy/sistema/, legacy/)
```

## 📝 ARCHIVOS PROCESADOS

### ✅ Actualizaciones Exitosas
"""
    
    for result in results:
        if result['success'] and result['updates_count'] > 0:
            report += f"\n- **{result['file']}** - {result['updates_count']} cambios"
        elif result['success']:
            report += f"\n- **{result['file']}** - Sin cambios necesarios"
    
    if failed > 0:
        report += f"\n\n### ❌ Archivos con Errores\n"
        for result in results:
            if not result['success']:
                report += f"\n- **{result['file']}** - Error: {result['error']}"
    
    report += f"""

## 🎯 PRÓXIMOS PASOS

1. ✅ Verificar que todas las referencias funcionen correctamente
2. ✅ Ejecutar tests de importación para validar cambios
3. ✅ Actualizar documentación específica si es necesario
4. ✅ Commit y documentar cambios en control de versiones

## 📋 BACKUP

Todos los archivos modificados tienen backup con sufijo `{BACKUP_SUFFIX}`.
Para restaurar un archivo: `cp archivo{BACKUP_SUFFIX} archivo`

---
*Generado automáticamente por el script de actualización de bitácoras*
*Protocolo: REGLA #11 - Actualización Post-Reorganización*
"""
    
    return report

def main():
    """Función principal del actualizador de bitácoras."""
    print("🔄 ACTUALIZADOR DE BITÁCORAS POST-REORGANIZACIÓN")
    print("=" * 60)
    print(f"📂 Directorio del proyecto: {PROJECT_ROOT}")
    
    # Encontrar archivos de bitácora
    print("\n🔍 Buscando archivos de bitácora...")
    bitacora_files = find_bitacora_files()
    
    if not bitacora_files:
        print("❌ No se encontraron archivos de bitácora")
        return
    
    print(f"📋 Encontrados {len(bitacora_files)} archivos de bitácora")
    
    # Procesar cada archivo
    print("\n🔄 Iniciando proceso de actualización...")
    results = []
    
    for file_path in bitacora_files:
        result = update_bitacora_file(file_path)
        results.append(result)
    
    # Generar reporte
    print("\n📋 Generando reporte final...")
    report = generate_update_report(results)
    
    # Guardar reporte
    report_path = PROJECT_ROOT / "03-DOCUMENTATION" / "reports" / f"REPORTE_ACTUALIZACION_BITACORAS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')
    
    print(f"📄 Reporte guardado: {report_path.relative_to(PROJECT_ROOT)}")
    
    # Resumen final
    successful = len([r for r in results if r['success']])
    total_updates = sum(r['updates_count'] for r in results)
    
    print(f"\n🎉 PROCESO COMPLETADO")
    print(f"✅ {successful}/{len(results)} archivos actualizados exitosamente")
    print(f"🔄 {total_updates} cambios totales aplicados")
    
    if successful == len(results):
        print("🏆 ÉXITO TOTAL: Todas las bitácoras actualizadas correctamente")
    else:
        print("⚠️  Revisar errores en el reporte generado")

if __name__ == "__main__":
    main()
