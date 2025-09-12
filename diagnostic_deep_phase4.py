#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico Profundo - Fase 4: Dashboard Integration
Verificando integración completa del dashboard y detección final de señales
"""

import sys
import os

# Agregar el path del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
sys.path.insert(0, os.path.join(script_dir, '01-CORE'))

print("🔍 DIAGNÓSTICO PROFUNDO - FASE 4: DASHBOARD INTEGRATION")
print("=" * 65)

try:
    # 1. Test Complete Data Flow
    print("\n1. 📊 TEST COMPLETE DATA FLOW")
    from data_management.mt5_data_manager import MT5DataManager
    from ict_engine.pattern_detector import PatternDetector
    from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
    
    mt5_manager = MT5DataManager()
    pattern_detector = PatternDetector()
    smart_analyzer = SmartMoneyAnalyzer()
    
    # Obtener datos frescos
    test_data = mt5_manager.get_current_data("EURUSD", "M15", 100)
    
    if test_data is not None and len(test_data) > 0:
        print(f"✅ Fresh MT5 Data: {len(test_data)} bars")
        print(f"   Columns: {list(test_data.columns)}")
        
        # Pattern Detection
        patterns = pattern_detector.detect_patterns(test_data)
        print(f"📋 Patterns detectados: {len(patterns) if patterns else 0}")
        
        # Smart Money Analysis
        smart_result = smart_analyzer.analyze_smart_money_concepts({"EURUSD_M15": test_data})
        print(f"📋 Smart Money Analysis: Status = {smart_result.get('status', 'N/A')}")
        
        # Store results for dashboard
        live_signals = {
            'patterns': patterns if patterns else [],
            'smart_money': smart_result,
            'total_signals': len(patterns) if patterns else 0
        }
        
        print(f"🎯 TOTAL LIVE SIGNALS PREPARADAS: {live_signals['total_signals']}")
        
    else:
        print("❌ No se pudieron obtener datos MT5")
        live_signals = {'patterns': [], 'smart_money': {}, 'total_signals': 0}
        
except Exception as e:
    print(f"❌ Error Complete Data Flow: {e}")
    live_signals = {'patterns': [], 'smart_money': {}, 'total_signals': 0}

try:
    # 2. Test Dashboard Components
    print("\n2. 📊 TEST DASHBOARD COMPONENTS")
    
    # Verificar dashboard files
    dashboard_files = [
        "09-DASHBOARD/dashboard.py",
        "09-DASHBOARD/ict_dashboard.py", 
        "09-DASHBOARD/start_dashboard.py"
    ]
    
    for file_path in dashboard_files:
        full_path = os.path.join(script_dir, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}: Existe")
        else:
            print(f"❌ {file_path}: No encontrado")
            
    # Test main dashboard
    try:
        from dashboard import ICTDashboard
        dashboard = ICTDashboard()
        print("✅ ICTDashboard: Cargado desde 09-DASHBOARD/")
        
        # Test get current signals
        if hasattr(dashboard, 'get_current_signals'):
            current_signals = dashboard.get_current_signals()
            print(f"📋 Current Signals: {current_signals}")
        else:
            print("⚠️ Método get_current_signals no disponible")
            
    except ImportError:
        print("⚠️ ICTDashboard no se pudo importar desde 09-DASHBOARD/")
        
except Exception as e:
    print(f"❌ Error Dashboard Components: {e}")

try:
    # 3. Test Enterprise Comparison Dashboard
    print("\n3. 🏢 TEST ENTERPRISE COMPARISON DASHBOARD")
    
    from validation_pipeline.enterprise_comparison_dashboard import EnterpriseComparisonDashboard
    enterprise_dashboard = EnterpriseComparisonDashboard()
    print("✅ Enterprise Dashboard: Cargado")
    
    # Ejecutar comparación live vs historical
    comparison = enterprise_dashboard.compare_live_vs_historical("EURUSD", "M15")
    print(f"📋 Comparison Type: {type(comparison)}")
    
    if comparison and hasattr(comparison, 'keys'):
        # Extraer conteos de señales de la estructura correcta
        live_signals_count = 0
        historical_signals_count = 0
        
        # Leer desde summary que es donde están los datos reales
        if 'summary' in comparison:
            summary = comparison['summary']
            live_signals_count = summary.get('live_signals', 0)
            historical_signals_count = summary.get('historical_signals', 0)
        else:
            # Fallback a la estructura antigua
            if 'live_data' in comparison:
                live_data = comparison['live_data']
                if isinstance(live_data, dict) and 'summary' in live_data:
                    live_signals_count = live_data['summary'].get('total_signals', 0)
                elif hasattr(live_data, '__len__'):
                    live_signals_count = len(live_data)
                    
            if 'historical_data' in comparison:
                historical_data = comparison['historical_data']  
                if isinstance(historical_data, dict) and 'summary' in historical_data:
                    historical_signals_count = historical_data['summary'].get('total_signals', 0)
                elif hasattr(historical_data, '__len__'):
                    historical_signals_count = len(historical_data)
        
        print(f"🎯 LIVE SIGNALS: {live_signals_count}")
        print(f"🎯 HISTORICAL SIGNALS: {historical_signals_count}")
        
        # Verificar discrepancia
        if live_signals_count == 0 and historical_signals_count > 0:
            print("⚠️ DISCREPANCIA CONFIRMADA: Live = 0, Historical > 0")
            print("🔧 CAUSA PROBABLE: Conexión MT5 perdida - sin datos live")
            print("💡 SOLUCIÓN: Restaurar conexión MT5 para habilitar señales live")
        elif live_signals_count > 0:
            print("✅ Live signals detectadas correctamente")
        else:
            print("⚠️ Ambos conteos en 0 - verificar datos/parámetros")
            
    else:
        print("❌ Error obteniendo comparison data")
        
except Exception as e:
    print(f"❌ Error Enterprise Dashboard: {e}")

try:
    # 4. Test Memory System Integration
    print("\n4. 🧠 TEST MEMORY SYSTEM INTEGRATION")
    
    from analysis.unified_memory_system import UnifiedMemorySystem
    memory = UnifiedMemorySystem()
    print("✅ Memory System: Cargado")
    
    # Verificar estado del sistema para debugging
    if hasattr(memory, 'system_state'):
        system_state = memory.system_state
        
        # Verificar componentes críticos del pipeline
        components = ['mt5_connection', 'pattern_detection', 'validation_pipeline', 'dashboard_integration']
        
        for component in components:
            if hasattr(system_state, 'get'):
                status = system_state.get(component, 'unknown')
                print(f"📋 {component}: {status}")
            else:
                print(f"📋 {component}: No disponible en system_state")
                
except Exception as e:
    print(f"❌ Error Memory System Integration: {e}")

try:
    # 5. Final Integration Test
    print("\n5. 🎯 FINAL INTEGRATION TEST")
    
    # Simular el flujo completo como lo haría el dashboard
    print("Simulando flujo completo del dashboard...")
    
    # Step 1: Get fresh data
    from data_management.mt5_data_manager import MT5DataManager
    mt5_manager = MT5DataManager()
    fresh_data = mt5_manager.get_current_data("EURUSD", "M15", 50)
    
    if fresh_data is not None:
        print(f"✅ Step 1 - Fresh Data: {len(fresh_data)} bars")
        
        # Step 2: Pattern detection
        from ict_engine.pattern_detector import PatternDetector
        detector = PatternDetector()
        detected_patterns = detector.detect_patterns(fresh_data)
        print(f"✅ Step 2 - Pattern Detection: {len(detected_patterns) if detected_patterns else 0} patterns")
        
        # Step 3: Smart Money Analysis  
        from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
        analyzer = SmartMoneyAnalyzer()
        smart_result = analyzer.analyze_smart_money_concepts({"EURUSD_M15": fresh_data})
        print(f"✅ Step 3 - Smart Analysis: Status = {smart_result.get('status', 'N/A')}")
        
        # Step 4: Final count
        final_live_signals = len(detected_patterns) if detected_patterns else 0
        print(f"🎯 FINAL LIVE SIGNALS COUNT: {final_live_signals}")
        
        if final_live_signals == 0:
            print("⚠️ PROBLEMA CONFIRMADO: Pipeline no genera señales live")
            print("🔧 Verificar configuración de algoritmos y parámetros de detección")
        else:
            print("✅ PROBLEMA RESUELTO: Pipeline genera señales live")
            
    else:
        print("❌ No se pueden obtener datos frescos para test final")
        
except Exception as e:
    print(f"❌ Error Final Integration Test: {e}")

print(f"\n✅ FASE 4 COMPLETADA: Dashboard Integration")
print("🎯 Diagnóstico completo - Generando reporte final...")