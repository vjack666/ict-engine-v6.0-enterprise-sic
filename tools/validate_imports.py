#!/usr/bin/env python3
"""
🔧 VALIDADOR DE IMPORTS - ICT ENGINE v6.0 ENTERPRISE
====================================================

Script para validar que todos los imports funcionen correctamente
y que el sistema esté configurado adecuadamente.
"""

import sys
import os
from pathlib import Path

# Agregar paths del proyecto
project_root = Path(__file__).parent
core_path = project_root / "01-CORE"
sys.path.insert(0, str(core_path))

def test_import(module_name: str, import_path: str) -> bool:
    """Probar un import específico"""
    try:
        exec(f"from {import_path} import *")
        print(f"✅ {module_name}: OK")
        return True
    except ImportError as e:
        print(f"❌ {module_name}: {e}")
        return False
    except Exception as e:
        print(f"⚠️ {module_name}: {e}")
        return False

def main():
    """Validar todos los imports críticos"""
    print("🧪 VALIDANDO IMPORTS DEL SISTEMA ICT ENGINE v6.0")
    print("=" * 60)
    
    imports_to_test = [
        ("Protocols Unified Logging", "protocols.unified_logging"),
        ("Utils Import Center", "utils.import_center"),
        ("Smart Trading Logger", "smart_trading_logger"),
        ("Advanced Candle Downloader", "data_management.advanced_candle_downloader"),
        ("Smart Money Analyzer", "smart_money_concepts.smart_money_analyzer"),
        ("Multi Timeframe Analyzer", "analysis.multi_timeframe_analyzer"),
        ("ICT Data Manager", "data_management.ict_data_manager"),
        ("ICT Symbol Manager", "utils.ict_symbol_manager"),
        ("Pattern Detector", "ict_engine.pattern_detector"),
    ]
    
    successful_imports = 0
    total_imports = len(imports_to_test)
    
    for module_name, import_path in imports_to_test:
        if test_import(module_name, import_path):
            successful_imports += 1
    
    print("=" * 60)
    print(f"📊 RESULTADOS: {successful_imports}/{total_imports} imports exitosos")
    
    if successful_imports == total_imports:
        print("✅ TODOS LOS IMPORTS FUNCIONAN CORRECTAMENTE")
        print("🎯 El problema es solo de configuración de Pylance")
    else:
        print("❌ HAY PROBLEMAS DE IMPORTS QUE NECESITAN RESOLVERSE")
    
    return successful_imports == total_imports

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)