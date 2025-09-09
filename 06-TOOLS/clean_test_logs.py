#!/usr/bin/env python3
"""
🧹 LIMPIADOR DE LOGS DE PRUEBA
ICT Engine v6.0 Enterprise - Elimina logs de testing y errores no críticos
"""

import re
from pathlib import Path
from datetime import datetime

def clean_test_logs():
    """Limpiar logs de prueba y errores de testing"""
    print("🧹 INICIANDO LIMPIEZA DE LOGS DE PRUEBA")
    print("=" * 50)
    
    logs_path = Path("05-LOGS")
    cleaned_files = 0
    lines_removed = 0
    
    for log_file in logs_path.rglob("*.log"):
        if log_file.stat().st_size > 0:
            print(f"📁 Procesando: {log_file.name}")
            
            lines_to_keep = []
            current_file_lines_removed = 0
            
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line_strip = line.strip()
                        
                        # Filtrar líneas de testing
                        if 'Prueba de' in line:
                            current_file_lines_removed += 1
                            continue
                        
                        # Filtrar errores de testing específicos
                        if ('Prueba de error' in line or 
                            'Test error' in line or
                            'ERROR] [ICT_SYSTEM] [CORE] Prueba' in line or
                            'ERROR] [ICT_PATTERNS] [CORE] Prueba' in line or
                            'ERROR] [ICT_DASHBOARD] [CORE] Prueba' in line or
                            'ERROR] [ICT_TRADING] [CORE] Prueba' in line):
                            current_file_lines_removed += 1
                            continue
                        
                        lines_to_keep.append(line)
                
                # Escribir archivo limpio si se removieron líneas
                if current_file_lines_removed > 0:
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.writelines(lines_to_keep)
                    
                    print(f"   ✅ Removidas {current_file_lines_removed} líneas de prueba")
                    lines_removed += current_file_lines_removed
                    cleaned_files += 1
                else:
                    print(f"   ➡️ Sin líneas de prueba encontradas")
                    
            except Exception as e:
                print(f"   ❌ Error procesando {log_file.name}: {e}")
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE LIMPIEZA")
    print("=" * 50)
    print(f"📁 Archivos procesados: {len(list(logs_path.rglob('*.log')))}")
    print(f"🧹 Archivos limpiados: {cleaned_files}")
    print(f"🗑️ Líneas removidas: {lines_removed}")
    print("✅ Limpieza completada")
    
    return {
        'files_cleaned': cleaned_files,
        'lines_removed': lines_removed,
        'success': True
    }

if __name__ == "__main__":
    result = clean_test_logs()
    print(f"\n🎯 Resultado: {result}")
