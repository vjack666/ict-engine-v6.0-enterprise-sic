#!/usr/bin/env python3
"""
🧪 VALIDACIÓN RÁPIDA DE SOLUCIONES
Test inmediato de las correcciones implementadas
"""

import os
import re
import json
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def quick_validation_test():
    """🧪 Test rápido de las soluciones implementadas"""
    print("🧪 VALIDACIÓN RÁPIDA DE SOLUCIONES")
    print("=" * 50)
    
    base_path = Path(".")
    logs_path = base_path / "05-LOGS"
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'overall_score': 0,
        'recommendations': []
    }
    
    # TEST 1: Verificar volumen de logs APPLICATION
    print("📊 TEST 1: Verificando volumen de logs...")
    app_log = logs_path / "application" / "ict_engine_2025-09-09.log"
    
    if app_log.exists():
        line_count = sum(1 for _ in open(app_log, 'r', encoding='utf-8', errors='ignore'))
        results['tests']['log_volume'] = {
            'current_lines': line_count,
            'target_max': 1000,
            'status': 'PASS' if line_count < 1000 else 'FAIL',
            'severity': 'HIGH' if line_count > 2000 else 'MEDIUM'
        }
        print(f"   📈 Líneas actuales: {line_count}")
        print(f"   🎯 Estado: {'✅ PASS' if line_count < 1000 else '❌ FAIL'}")
    else:
        results['tests']['log_volume'] = {'status': 'NOT_FOUND'}
        print("   ⚠️ Archivo no encontrado")
    
    # TEST 2: Contar errores y críticos actuales
    print("\n🚨 TEST 2: Verificando errores críticos...")
    error_count = 0
    critical_count = 0
    test_errors = 0
    
    for log_file in logs_path.rglob("*.log"):
        if log_file.stat().st_size > 0:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        if 'ERROR' in line:
                            if 'Prueba de' in line:
                                test_errors += 1
                            else:
                                error_count += 1
                        if 'CRITICAL' in line:
                            critical_count += 1
            except:
                continue
    
    results['tests']['errors'] = {
        'current_errors': error_count,
        'current_criticals': critical_count,
        'test_errors': test_errors,
        'status': 'PASS' if critical_count == 0 and error_count <= 2 else 'FAIL'
    }
    
    print(f"   🔴 ERRORs: {error_count}")
    print(f"   🚨 CRITICALs: {critical_count}")
    print(f"   🧪 Test errors: {test_errors}")
    print(f"   🎯 Estado: {'✅ PASS' if critical_count == 0 and error_count <= 2 else '❌ FAIL'}")
    
    # TEST 3: Verificar consistencia de timestamps
    print("\n⏰ TEST 3: Verificando timestamps...")
    inconsistent_files = 0
    files_checked = 0
    
    for log_file in logs_path.rglob("*.log"):
        if log_file.stat().st_size > 0:
            files_checked += 1
            formats_found = set()
            
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f):
                        if i >= 10:  # Solo primeras 10 líneas
                            break
                        timestamp_match = re.search(r'^\[(.*?)\]', line)
                        if timestamp_match:
                            formats_found.add(len(timestamp_match.group(1)))
                
                if len(formats_found) > 1:
                    inconsistent_files += 1
            except:
                continue
    
    results['tests']['timestamps'] = {
        'files_checked': files_checked,
        'inconsistent_files': inconsistent_files,
        'status': 'PASS' if inconsistent_files == 0 else 'FAIL'
    }
    
    print(f"   📁 Archivos revisados: {files_checked}")
    print(f"   ⚠️ Archivos inconsistentes: {inconsistent_files}")
    print(f"   🎯 Estado: {'✅ PASS' if inconsistent_files == 0 else '❌ FAIL'}")
    
    # TEST 4: Verificar existencia de archivos de configuración
    print("\n⚙️ TEST 4: Verificando configuraciones...")
    config_files = [
        "01-CORE/config/log_throttle_config.json",
        "01-CORE/config/risk_management_config.json", 
        "01-CORE/config/timestamp_config.json",
        "01-CORE/config/log_categorization_rules.json"
    ]
    
    configs_exist = 0
    for config_file in config_files:
        if (base_path / config_file).exists():
            configs_exist += 1
            print(f"   ✅ {config_file}")
        else:
            print(f"   ❌ {config_file}")
    
    results['tests']['configurations'] = {
        'total_configs': len(config_files),
        'configs_exist': configs_exist,
        'status': 'PASS' if configs_exist >= 3 else 'FAIL'
    }
    
    print(f"   🎯 Estado: {'✅ PASS' if configs_exist >= 3 else '❌ FAIL'}")
    
    # TEST 5: Verificar utilidades creadas
    print("\n🔧 TEST 5: Verificando utilidades...")
    utils_files = [
        "01-CORE/utils/realtime_log_deduplicator.py",
        "01-CORE/utils/log_categorizer.py",
        "01-CORE/risk_management/risk_validator.py",
        "01-CORE/emergency/emergency_handler.py"
    ]
    
    utils_exist = 0
    for util_file in utils_files:
        if (base_path / util_file).exists():
            utils_exist += 1
            print(f"   ✅ {util_file}")
        else:
            print(f"   ❌ {util_file}")
    
    results['tests']['utilities'] = {
        'total_utils': len(utils_files),
        'utils_exist': utils_exist,
        'status': 'PASS' if utils_exist >= 2 else 'FAIL'
    }
    
    print(f"   🎯 Estado: {'✅ PASS' if utils_exist >= 2 else '❌ FAIL'}")
    
    # CALCULAR SCORE GENERAL
    passed_tests = sum(1 for test in results['tests'].values() 
                      if test.get('status') == 'PASS')
    total_tests = len(results['tests'])
    results['overall_score'] = (passed_tests / total_tests) * 100
    
    # GENERAR RECOMENDACIONES
    if results['tests']['log_volume']['status'] == 'FAIL':
        results['recommendations'].append("🚨 CRÍTICO: Implementar throttling de logs inmediatamente")
    
    if results['tests']['errors']['status'] == 'FAIL':
        results['recommendations'].append("🚨 CRÍTICO: Resolver errores y violaciones de riesgo")
    
    if results['tests']['timestamps']['status'] == 'FAIL':
        results['recommendations'].append("🔶 ALTO: Estandarizar formatos de timestamp")
    
    if results['tests']['configurations']['status'] == 'FAIL':
        results['recommendations'].append("🔧 MEDIO: Crear archivos de configuración faltantes")
    
    if results['tests']['utilities']['status'] == 'FAIL':
        results['recommendations'].append("🔧 MEDIO: Implementar utilidades de sistema faltantes")
    
    # MOSTRAR RESUMEN FINAL
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("=" * 50)
    print(f"✅ Tests pasados: {passed_tests}/{total_tests}")
    print(f"📈 Score general: {results['overall_score']:.1f}%")
    
    if results['overall_score'] >= 80:
        print("🎉 VALIDACIÓN EXITOSA - Sistema listo para FASE 1")
        print("✅ Puede continuar con documentación operacional")
    elif results['overall_score'] >= 60:
        print("⚠️ VALIDACIÓN PARCIAL - Requiere atención")
        print("🔧 Implementar correcciones recomendadas")
    else:
        print("🚨 VALIDACIÓN FALLIDA - Intervención requerida")
        print("⚡ Problemas críticos deben resolverse primero")
    
    if results['recommendations']:
        print("\n🎯 RECOMENDACIONES INMEDIATAS:")
        for rec in results['recommendations']:
            print(f"   {rec}")
    
    # PRÓXIMOS PASOS ESPECÍFICOS
    print("\n🚀 PRÓXIMOS PASOS:")
    if results['overall_score'] >= 80:
        print("   1. ✅ Crear quick-start.md")
        print("   2. ✅ Crear troubleshooting.md") 
        print("   3. ✅ Crear emergency-procedures.md")
        print("   4. ✅ Crear production-checklist.md")
    else:
        print("   1. 🔧 Ejecutar log_problems_solver.py")
        print("   2. 🧪 Re-ejecutar este test de validación")
        print("   3. 📋 Revisar problemas específicos")
        print("   4. ⚡ Repetir hasta score >= 80%")
    
    # Guardar resultados
    try:
        results_file = base_path / "03-DOCUMENTATION" / "reports" / f"validation_quick_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Resultados guardados: {results_file}")
    except Exception as e:
        print(f"⚠️ Error guardando resultados: {e}")
    
    return results

if __name__ == "__main__":
    print("🧪 ICT ENGINE v6.0 - VALIDACIÓN RÁPIDA")
    print("=" * 50)
    print("🎯 Validando estado actual del sistema...")
    print("⏱️ Tiempo estimado: 1-2 minutos")
    print()
    
    results = quick_validation_test()
    
    # Decisión final
    print("\n" + "=" * 70)
    print("🎯 DECISIÓN FINAL")
    print("=" * 70)
    
    if results['overall_score'] >= 80:
        print("🚀 SISTEMA LISTO PARA FASE 1 DE DOCUMENTACIÓN")
        print("✨ Comenzar con quick-start.md inmediatamente")
        print("📋 Problemas críticos resueltos satisfactoriamente")
    elif results['overall_score'] >= 60:
        print("⚡ SISTEMA REQUIERE ATENCIÓN ADICIONAL")
        print("🔧 Ejecutar log_problems_solver.py completo")
        print("🧪 Re-validar después de correcciones")
    else:
        print("🚨 SISTEMA REQUIERE INTERVENCIÓN CRÍTICA")
        print("⚠️ Problemas fundamentales deben resolverse")
        print("📞 Considerar escalación o reinicio parcial")
    
    print("\n📚 Continuando con el plan de trabajo por fases...")
    print("🎯 Objetivo: Documentación operacional crítica")
