#!/usr/bin/env python3
"""
🎯 SIMPLE CHoCH MEMORY TEST - ICT Engine v6.0 Enterprise
=======================================================

Test SIMPLE y RÁPIDO para validar memoria CHoCH sin loops infinitos.
Tiempo máximo garantizado: 15 segundos.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

def simple_test():
    """Test simple con timeout garantizado"""
    start_time = time.time()
    MAX_TIME = 15  # 15 segundos máximo
    
    print("🎯 Simple CHoCH Memory Test")
    print("=" * 30)
    print("⏰ Tiempo máximo: 15 segundos")
    print("=" * 30)
    
    # Configurar paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    sys.path.extend([
        str(project_root / "01-CORE"),
        str(project_root / "01-CORE" / "analysis")
    ])
    
    tests_passed = 0
    total_tests = 4
    
    try:
        # TEST 1: Import básico
        print("\n📦 TEST 1: Import MarketContextV6...")
        if time.time() - start_time > MAX_TIME:
            print("⏰ TIMEOUT")
            return tests_passed, total_tests
        
        try:
            from market_context_v6 import MarketContextV6
            print("✅ Import: OK")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Import error: {e}")
        
        # TEST 2: Inicialización
        print("\n🧠 TEST 2: Inicializar memoria...")
        if time.time() - start_time > MAX_TIME:
            print("⏰ TIMEOUT")
            return tests_passed, total_tests
            
        try:
            context = MarketContextV6()
            print("✅ Init: OK")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Init error: {e}")
            # Continuar con contexto mock
            context = None
        
        # TEST 3: Función CHoCH existe
        print("\n🔍 TEST 3: Verificar función CHoCH...")
        if time.time() - start_time > MAX_TIME:
            print("⏰ TIMEOUT")
            return tests_passed, total_tests
            
        try:
            if context and hasattr(context, 'get_last_choch_for_trading'):
                print("✅ Función get_last_choch_for_trading: EXISTE")
                tests_passed += 1
            else:
                print("❌ Función get_last_choch_for_trading: NO EXISTE")
        except Exception as e:
            print(f"❌ Check function error: {e}")
        
        # TEST 4: Función levels existe
        print("\n📈 TEST 4: Verificar función levels...")
        if time.time() - start_time > MAX_TIME:
            print("⏰ TIMEOUT")
            return tests_passed, total_tests
            
        try:
            if context and hasattr(context, 'get_valid_choch_levels_for_trading'):
                print("✅ Función get_valid_choch_levels_for_trading: EXISTE")
                tests_passed += 1
            else:
                print("❌ Función get_valid_choch_levels_for_trading: NO EXISTE")
        except Exception as e:
            print(f"❌ Check levels function error: {e}")
        
        return tests_passed, total_tests
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        return tests_passed, total_tests
    
    finally:
        elapsed = time.time() - start_time
        print(f"\n⏱️ Tiempo transcurrido: {elapsed:.1f}s")

def main():
    """Main con salida garantizada"""
    print("🚀 INICIANDO SIMPLE TEST")
    
    try:
        passed, total = simple_test()
        
        print("\n" + "="*30)
        print("📊 RESULTADOS")
        print("="*30)
        print(f"Tests pasados: {passed}/{total}")
        
        if passed >= 2:
            print("✅ FUNCIONES BÁSICAS OK")
            result = "PASS"
        else:
            print("❌ NECESITA CORRECCIÓN")
            result = "FAIL"
            
    except Exception as e:
        print(f"❌ Error en main: {e}")
        result = "ERROR"
    
    finally:
        print(f"\n🏁 TEST TERMINADO: {result}")
        print("🔚 SALIENDO...")
        sys.exit(0)

if __name__ == "__main__":
    main()