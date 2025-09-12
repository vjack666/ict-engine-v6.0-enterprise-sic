#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnóstico Profundo - Fase 3: Validation Pipeline  
Verificando pipeline de validación y sistema de alertas
"""

import sys
import os

# Agregar el path del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
sys.path.insert(0, os.path.join(script_dir, '01-CORE'))

print("🔍 DIAGNÓSTICO PROFUNDO - FASE 3: VALIDATION PIPELINE")
print("=" * 60)

try:
    # 1. Test MT5 Data Pipeline
    print("\n1. 📊 VERIFICANDO MT5 DATA PIPELINE")
    from data_management.mt5_data_manager import MT5DataManager
    mt5_manager = MT5DataManager()
    
    # Obtener datos de prueba
    test_data = mt5_manager.get_current_data("EURUSD", "M15", 100)
    if test_data is not None:
        print(f"✅ Datos MT5 obtenidos: {len(test_data)} barras")
        print(f"   Columnas: {list(test_data.columns)}")
        print(f"   Timestamp range: {test_data['time'].min()} → {test_data['time'].max()}")
    else:
        print("❌ Error obteniendo datos MT5")
        
except Exception as e:
    print(f"❌ Error MT5 Pipeline: {e}")

try:
    # 2. Test Pattern Detection Integration
    print("\n2. 🎯 VERIFICANDO PATTERN DETECTION INTEGRATION")
    from ict_engine.ict_pattern_detector import ICTPatternDetector
    from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
    
    # Inicializar detectores
    pattern_detector = ICTPatternDetector()
    smart_analyzer = SmartMoneyAnalyzer()
    
    print("✅ Pattern Detector: Inicializado")
    print("✅ Smart Money Analyzer: Inicializado")
    
    if test_data is not None:
        # Análisis con datos reales
        patterns = pattern_detector.detect_patterns(test_data)
        smart_analysis = smart_analyzer.analyze_smart_money_concepts(test_data, "EURUSD")
        
        print(f"📋 Patrones detectados: {len(patterns) if patterns else 0}")
        print(f"📋 Smart Money Analysis: {type(smart_analysis)} - Status: {smart_analysis.get('status', 'N/A')}")
        
except Exception as e:
    print(f"❌ Error Pattern Detection: {e}")

try:
    # 3. Test Validation Pipeline Components
    print("\n3. 🔍 VERIFICANDO VALIDATION PIPELINE COMPONENTS")
    
    # Verificar componentes del pipeline de validación
    validation_paths = [
        "01-CORE/validation_pipeline/live_signal_validator.py",
        "01-CORE/validation_pipeline/historical_validator.py", 
        "01-CORE/analysis/enterprise_comparison_dashboard.py"
    ]
    
    for path in validation_paths:
        full_path = os.path.join(script_dir, path)
        if os.path.exists(full_path):
            print(f"✅ {path}: Existe")
        else:
            print(f"❌ {path}: No encontrado")
            
except Exception as e:
    print(f"❌ Error verificando componentes: {e}")

try:
    # 4. Test Live Signal Validation
    print("\n4. ⚡ TEST LIVE SIGNAL VALIDATION")
    
    # Intentar cargar validador de señales en vivo
    try:
        from validation_pipeline.live_signal_validator import LiveSignalValidator
        live_validator = LiveSignalValidator()
        print("✅ LiveSignalValidator: Cargado")
        
        # Test con datos actuales
        if test_data is not None:
            validation_result = live_validator.validate_current_signals("EURUSD")
            print(f"📋 Validación actual: {validation_result}")
            
    except ImportError as ie:
        print(f"⚠️ LiveSignalValidator import: {ie}")
    except Exception as ve:
        print(f"❌ LiveSignalValidator error: {ve}")
        
except Exception as e:
    print(f"❌ Error Live Signal Test: {e}")

try:
    # 5. Test Enterprise Dashboard Integration
    print("\n5. 📊 TEST ENTERPRISE DASHBOARD INTEGRATION")
    
    from analysis.enterprise_comparison_dashboard import EnterpriseComparisonDashboard
    dashboard = EnterpriseComparisonDashboard()
    print("✅ Enterprise Dashboard: Cargado")
    
    # Test comparación live vs historical
    comparison_result = dashboard.compare_live_vs_historical()
    print(f"📋 Comparación Live vs Historical: {type(comparison_result)}")
    
    if hasattr(comparison_result, 'keys'):
        print(f"   Keys: {list(comparison_result.keys())}")
        
        # Verificar conteos de señales
        live_count = comparison_result.get('live_signals', {}).get('total', 0)
        historical_count = comparison_result.get('historical_signals', {}).get('total', 0)
        
        print(f"🎯 LIVE SIGNALS COUNT: {live_count}")
        print(f"🎯 HISTORICAL SIGNALS COUNT: {historical_count}")
        
        if live_count == 0:
            print("⚠️ PROBLEMA DETECTADO: Live signals = 0")
        else:
            print(f"✅ Live signals detectadas: {live_count}")
            
except Exception as e:
    print(f"❌ Error Dashboard Integration: {e}")

try:
    # 6. Memory System Integration Check
    print("\n6. 🧠 VERIFICANDO MEMORY SYSTEM INTEGRATION")
    
    from unified_memory_system import UnifiedMemorySystem
    memory = UnifiedMemorySystem()
    print("✅ UnifiedMemorySystem: Cargado")
    
    # Verificar estado del sistema
    if hasattr(memory, 'system_state'):
        system_state = memory.system_state
        print(f"📋 System State: {system_state}")
        
        # Verificar componentes críticos
        if hasattr(system_state, 'get'):
            validation_status = system_state.get('validation_pipeline', {})
            print(f"📋 Validation Pipeline Status: {validation_status}")
            
except Exception as e:
    print(f"❌ Error Memory System: {e}")

print(f"\n✅ FASE 3 COMPLETADA: Validation Pipeline")
print("🎯 Procediendo a Fase 4: Dashboard Integration")