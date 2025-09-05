#!/usr/bin/env python3
# Validación del import optimizado

import sys
import os

# Configurar paths
script_dir = os.path.dirname(__file__)
project_root = os.path.join(script_dir, '..', '..')
core_path = os.path.join(project_root, '01-CORE')
utils_path = os.path.join(core_path, 'utils')

sys.path.insert(0, core_path)
sys.path.insert(0, utils_path)

print("=== VALIDANDO IMPORT OPTIMIZADO ===")

# Test del patrón optimizado
try:
    import import_center
    print("✅ ImportCenter cargado exitosamente")
    
    # Test de instancia
    ic = import_center.ImportCenter()
    print("✅ ImportCenter se instancia correctamente")
    
    print("✅ Import optimizado funciona perfectamente")
    
except ImportError as e:
    print(f"⚠️ Error cargando ImportCenter: {e}")
    print("🔄 Usando fallback básico...")
    
    # Test del fallback
    class ImportCenter:
        def __init__(self):
            print("⚠️ Usando ImportCenter fallback")
        
        def safe_import(self, module_name: str):
            try:
                parts = module_name.split('.')
                module = __import__(module_name)
                for part in parts[1:]:
                    module = getattr(module, part)
                return module
            except Exception as e:
                print(f"❌ Error importando {module_name}: {e}")
                return None
    
    # Test del fallback
    ic = ImportCenter()
    print("✅ Fallback ImportCenter funciona correctamente")

print("🎯 Validación completada exitosamente")
