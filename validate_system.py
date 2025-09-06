#!/usr/bin/env python3
"""
VALIDACIÓN FINAL: Sistema integrado con datos reales
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Configurar paths
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir / "09-DASHBOARD"))

def validate_final_system():
    """Validación final del sistema integrado"""
    print("\n🔥 VALIDACIÓN FINAL DEL SISTEMA INTEGRADO")
    print("="*50)
    
    success_count = 0
    total_tests = 4
    
    # Test 1: Proveedor de datos reales
    print("\n1️⃣ Validando proveedor de datos reales...")
    try:
        from run_real_market_system import get_real_data_provider, get_market_status
        provider = get_real_data_provider()
        status = get_market_status()
        
        if provider.is_connected and status.get('connected', False):
            print("   ✅ Proveedor de datos reales: OK")
            success_count += 1
        else:
            print("   ❌ Proveedor de datos reales: FALLO")
    except Exception as e:
        print(f"   ❌ Error en proveedor: {e}")
    
    # Test 2: Orchestrator con patrones cargados
    print("\n2️⃣ Validando orchestrator...")
    try:
        from patterns_analysis.patterns_orchestrator import PatternsOrchestrator
        orchestrator = PatternsOrchestrator()
        
        if (len(orchestrator.loaded_patterns) > 0 and 
            orchestrator.is_connected_to_real_data()):
            print(f"   ✅ Orchestrator: {len(orchestrator.loaded_patterns)} patrones cargados")
            success_count += 1
        else:
            print(f"   ❌ Orchestrator: {len(orchestrator.loaded_patterns)} patrones, conectado: {orchestrator.is_connected_to_real_data()}")
    except Exception as e:
        print(f"   ❌ Error en orchestrator: {e}")
    
    # Test 3: Datos reales funcionando
    print("\n3️⃣ Validando obtención de datos reales...")
    try:
        real_data = orchestrator.get_real_data("EURUSD", "H1")
        if real_data and real_data.get('candles_count', 0) > 0:
            print(f"   ✅ Datos reales: {real_data['candles_count']} velas obtenidas")
            success_count += 1
        else:
            print("   ❌ No se obtuvieron datos reales")
    except Exception as e:
        print(f"   ❌ Error obteniendo datos: {e}")
    
    # Test 4: Análisis de patrones
    print("\n4️⃣ Validando análisis de patrones...")
    try:
        if orchestrator.loaded_patterns:
            pattern_name = list(orchestrator.loaded_patterns.keys())[0]
            pattern_instance = orchestrator.loaded_patterns[pattern_name]
            
            # Probar con el nuevo método analyze_market_data
            result = pattern_instance.analyze_market_data("EURUSD", "H1")
            if result:
                print(f"   ✅ Análisis de patrones: {pattern_name} analizó correctamente")
                success_count += 1
            else:
                print(f"   ⚠️ Análisis de patrones: {pattern_name} retornó None")
        else:
            print("   ❌ No hay patrones cargados para analizar")
    except Exception as e:
        print(f"   ⚠️ Error en análisis: {e}")
    
    # Resumen final
    print("\n" + "="*50)
    print(f"🎯 RESULTADO FINAL: {success_count}/{total_tests} tests pasados")
    
    if success_count == total_tests:
        print("🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("✅ La pestaña 'Patrones' está lista para mostrar datos reales MT5")
    elif success_count >= 3:
        print("👍 Sistema mayormente funcional con advertencias menores")
    else:
        print("⚠️ Sistema requiere atención adicional")
    
    print(f"🕐 Validación completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    return success_count == total_tests

if __name__ == "__main__":
    validate_final_system()
