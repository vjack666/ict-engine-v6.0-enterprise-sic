#!/usr/bin/env python3
"""
🔧 OPTIMIZADOR ICT DATA MANAGER
===============================

Script para optimizar las múltiples inicializaciones de ICTDataManager
convirtiendo todas las instancias a usar el patrón singleton.

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 2025-09-10
"""

import os
import re
from pathlib import Path

def optimize_ict_data_manager_usage():
    """Optimiza el uso de ICTDataManager en todo el sistema"""
    
    project_root = Path(__file__).parent.parent
    
    # Buscar archivos que usan ICTDataManager
    patterns_dir = project_root / "09-DASHBOARD" / "patterns_analysis" / "individual_patterns"
    
    if not patterns_dir.exists():
        print(f"❌ Directorio no encontrado: {patterns_dir}")
        return False
    
    # Patrón de búsqueda y reemplazo
    search_pattern = r'from data_management\.ict_data_manager import ICTDataManager\s+self\.real_data_manager = ICTDataManager\(\)'
    
    replacement = '''from data_management.ict_data_manager_singleton import get_ict_data_manager
            self.real_data_manager = get_ict_data_manager()'''
    
    # También necesitamos actualizar el mensaje
    message_search = r'print\(f"✅ \{self\.pattern_name\}: ICTDataManager real conectado"\)'
    message_replacement = r'print(f"✅ {self.pattern_name}: ICTDataManager singleton conectado")'
    
    files_updated = 0
    files_processed = 0
    
    print("🔧 OPTIMIZANDO ICT DATA MANAGER...")
    print("="*50)
    
    # Procesar archivos en individual_patterns
    for py_file in patterns_dir.glob("*_dashboard.py"):
        files_processed += 1
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar si necesita actualización
            if 'ICTDataManager()' in content and 'singleton' not in content:
                
                print(f"📝 Actualizando: {py_file.name}")
                
                # Realizar reemplazos más específicos
                # 1. Cambiar import
                content = re.sub(
                    r'from data_management\.ict_data_manager import ICTDataManager',
                    'from data_management.ict_data_manager_singleton import get_ict_data_manager',
                    content
                )
                
                # 2. Cambiar instanciación
                content = re.sub(
                    r'self\.real_data_manager = ICTDataManager\(\)',
                    'self.real_data_manager = get_ict_data_manager()',
                    content
                )
                
                # 3. Cambiar mensaje
                content = re.sub(
                    r'ICTDataManager real conectado',
                    'ICTDataManager singleton conectado',
                    content
                )
                
                # Escribir archivo actualizado
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                files_updated += 1
                print(f"  ✅ {py_file.name} optimizado")
                
            else:
                print(f"  ⏭️ {py_file.name} ya optimizado o no necesita cambios")
                
        except Exception as e:
            print(f"  ❌ Error procesando {py_file.name}: {e}")
    
    print("\n" + "="*50)
    print(f"📊 RESUMEN DE OPTIMIZACIÓN:")
    print(f"   Archivos procesados: {files_processed}")
    print(f"   Archivos actualizados: {files_updated}")
    
    if files_updated > 0:
        print(f"\n✅ Optimización completada exitosamente!")
        print(f"🚀 El sistema ahora usará una sola instancia de ICTDataManager")
        print(f"📈 Esto debería reducir significativamente los tiempos de inicialización")
    else:
        print(f"\n✅ No se requirieron cambios - sistema ya optimizado")
    
    return files_updated > 0

if __name__ == "__main__":
    optimize_ict_data_manager_usage()
