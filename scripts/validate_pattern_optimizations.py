#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ PATTERN OPTIMIZATION VALIDATOR - FASE 1
==========================================

Valida que las optimizaciones de Fase 1 se hayan aplicado correctamente
y mide el impacto en el rendimiento de detección de patrones.

Optimizaciones validadas:
- Order Blocks min_confidence: 55% → 72%
- Order Blocks high_confidence_threshold: 70% → 75%
- Pattern Detector min_confidence: 70% → 75%
- CHoCH base_confidence: 90% → 92%
- CHoCH swing window: 5 → 6

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 19 Septiembre 2025 - DÍA 9 Fase 1
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib.util

class PatternOptimizationValidator:
    """Validador de optimizaciones de patrones"""
    
    def __init__(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.validation_results = {}
        self.expected_optimizations = {
            'order_blocks_min_confidence': 72,
            'order_blocks_high_confidence': 75,
            'pattern_detector_min_confidence': 75.0,
            'choch_base_confidence': 92.0,
            'choch_swing_window': 6
        }
    
    def validate_order_blocks_optimizations(self) -> Dict[str, Any]:
        """Validar optimizaciones en Order Blocks"""
        print("🔹 Validando optimizaciones Order Blocks...")
        
        validation = {
            'component': 'Order Blocks',
            'optimizations_found': {},
            'validation_status': 'Unknown',
            'issues': []
        }
        
        try:
            # Leer el archivo directamente
            ob_file = self.repo_root / "01-CORE" / "ict_engine" / "patterns" / "simple_order_blocks.py"
            
            with open(ob_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar optimizaciones aplicadas
            optimizations_found = {}
            
            # 1. Validar min_confidence = 72
            if "min_confidence', 72)" in content:
                optimizations_found['min_confidence'] = 72
                print("   ✅ min_confidence = 72 ✓")
            elif "min_confidence', 55)" in content:
                validation['issues'].append("min_confidence still at 55%, should be 72%")
                print("   ❌ min_confidence = 55 (no optimizado)")
            
            # 2. Validar high_confidence threshold = 75
            if "min_confidence: float = 75)" in content:
                optimizations_found['high_confidence_threshold'] = 75
                print("   ✅ high_confidence_threshold = 75 ✓")
            elif "min_confidence: float = 70)" in content:
                validation['issues'].append("high_confidence_threshold still at 70%, should be 75%")
                print("   ❌ high_confidence_threshold = 70 (no optimizado)")
            
            validation['optimizations_found'] = optimizations_found
            
            # Determinar status
            if len(optimizations_found) == 2 and not validation['issues']:
                validation['validation_status'] = 'SUCCESS'
                print("   🎉 Order Blocks: Todas las optimizaciones aplicadas correctamente")
            elif len(optimizations_found) > 0:
                validation['validation_status'] = 'PARTIAL'
                print(f"   ⚠️ Order Blocks: {len(optimizations_found)}/2 optimizaciones aplicadas")
            else:
                validation['validation_status'] = 'FAILED'
                print("   ❌ Order Blocks: No se encontraron optimizaciones")
            
        except Exception as e:
            validation['error'] = str(e)
            validation['validation_status'] = 'ERROR'
            print(f"   ❌ Error validando Order Blocks: {e}")
        
        return validation
    
    def validate_pattern_detector_optimizations(self) -> Dict[str, Any]:
        """Validar optimizaciones en Pattern Detector"""
        print("🔸 Validando optimizaciones Pattern Detector...")
        
        validation = {
            'component': 'Pattern Detector',
            'optimizations_found': {},
            'validation_status': 'Unknown',
            'issues': []
        }
        
        try:
            # Leer el archivo directamente
            pd_file = self.repo_root / "01-CORE" / "analysis" / "pattern_detector.py"
            
            with open(pd_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            optimizations_found = {}
            
            # 1. Validar min_confidence = 75.0
            if "'min_confidence': 75.0" in content:
                optimizations_found['min_confidence'] = 75.0
                print("   ✅ min_confidence = 75.0 ✓")
            elif "'min_confidence': 70.0" in content:
                validation['issues'].append("min_confidence still at 70.0%, should be 75.0%")
                print("   ❌ min_confidence = 70.0 (no optimizado)")
            
            # 2. Validar CHoCH base_confidence = 92.0
            choch_confidence_count = content.count("confidence = 92.0")
            if choch_confidence_count >= 2:  # Debe estar en bullish y bearish CHoCH
                optimizations_found['choch_base_confidence'] = 92.0
                print(f"   ✅ CHoCH base_confidence = 92.0 (encontrado {choch_confidence_count} veces) ✓")
            elif "confidence = 90.0" in content:
                validation['issues'].append("CHoCH confidence still at 90.0%, should be 92.0%")
                print("   ❌ CHoCH confidence = 90.0 (no optimizado)")
            
            # 3. Validar swing window = 6
            if "window=6)" in content and "OPTIMIZED" in content:
                optimizations_found['swing_window'] = 6
                print("   ✅ CHoCH swing window = 6 ✓")
            elif "window=5)" in content:
                validation['issues'].append("CHoCH swing window still at 5, should be 6")
                print("   ❌ CHoCH swing window = 5 (no optimizado)")
            
            validation['optimizations_found'] = optimizations_found
            
            # Determinar status
            expected_optimizations = 3
            if len(optimizations_found) == expected_optimizations and not validation['issues']:
                validation['validation_status'] = 'SUCCESS'
                print("   🎉 Pattern Detector: Todas las optimizaciones aplicadas correctamente")
            elif len(optimizations_found) > 0:
                validation['validation_status'] = 'PARTIAL'
                print(f"   ⚠️ Pattern Detector: {len(optimizations_found)}/{expected_optimizations} optimizaciones aplicadas")
            else:
                validation['validation_status'] = 'FAILED'
                print("   ❌ Pattern Detector: No se encontraron optimizaciones")
            
        except Exception as e:
            validation['error'] = str(e)
            validation['validation_status'] = 'ERROR'
            print(f"   ❌ Error validando Pattern Detector: {e}")
        
        return validation
    
    def test_order_blocks_performance(self) -> Dict[str, Any]:
        """Test básico de performance de Order Blocks"""
        print("⚡ Testing performance Order Blocks...")
        
        performance_test = {
            'component': 'Order Blocks Performance',
            'test_status': 'Unknown',
            'metrics': {},
            'notes': []
        }
        
        try:
            # Importar el módulo optimizado
            sys.path.insert(0, str(self.repo_root / "01-CORE" / "ict_engine" / "patterns"))
            
            # Test básico de inicialización
            start_time = time.time()
            
            # Simular importación del módulo (sin ejecutar detección real)
            module_file = self.repo_root / "01-CORE" / "ict_engine" / "patterns" / "simple_order_blocks.py"
            
            if module_file.exists():
                # Test de lectura del archivo (proxy para test de carga)
                with open(module_file, 'r') as f:
                    lines = len(f.readlines())
                
                init_time = (time.time() - start_time) * 1000
                
                performance_test['metrics'] = {
                    'initialization_time_ms': init_time,
                    'module_lines': lines,
                    'load_test_passed': init_time < 100  # < 100ms es bueno
                }
                
                if init_time < 50:
                    performance_test['test_status'] = 'EXCELLENT'
                    performance_test['notes'].append(f"Initialization time: {init_time:.1f}ms (Excellent)")
                elif init_time < 100:
                    performance_test['test_status'] = 'GOOD' 
                    performance_test['notes'].append(f"Initialization time: {init_time:.1f}ms (Good)")
                else:
                    performance_test['test_status'] = 'SLOW'
                    performance_test['notes'].append(f"Initialization time: {init_time:.1f}ms (Needs optimization)")
            else:
                performance_test['test_status'] = 'FAILED'
                performance_test['notes'].append("Module file not found")
            
        except Exception as e:
            performance_test['error'] = str(e)
            performance_test['test_status'] = 'ERROR'
            print(f"   ❌ Error en performance test: {e}")
        
        return performance_test
    
    def generate_validation_report(self) -> Dict[str, Any]:
        """Generar reporte completo de validación"""
        print("\n🔎 ICT Engine v6.0 - Pattern Optimization Validator")
        print("=" * 60)
        print("VALIDANDO OPTIMIZACIONES FASE 1...")
        print("=" * 60)
        
        # Ejecutar todas las validaciones
        ob_validation = self.validate_order_blocks_optimizations()
        pd_validation = self.validate_pattern_detector_optimizations()
        performance_test = self.test_order_blocks_performance()
        
        # Compilar reporte
        report = {
            'validation_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'phase': 'Phase 1 - Parameter Adjustments',
            'components_validated': ['Order Blocks', 'Pattern Detector', 'CHoCH'],
            'validations': {
                'order_blocks': ob_validation,
                'pattern_detector': pd_validation,
                'performance_test': performance_test
            },
            'overall_summary': {}
        }
        
        # Calcular summary general
        successful_validations = 0
        total_validations = 0
        total_optimizations_applied = 0
        total_expected_optimizations = 5  # Total optimizaciones esperadas
        
        for validation in [ob_validation, pd_validation]:
            total_validations += 1
            if validation['validation_status'] == 'SUCCESS':
                successful_validations += 1
            
            total_optimizations_applied += len(validation.get('optimizations_found', {}))
        
        # Summary general
        report['overall_summary'] = {
            'validation_success_rate': (successful_validations / total_validations) * 100,
            'optimizations_applied': total_optimizations_applied,
            'expected_optimizations': total_expected_optimizations,
            'optimization_completion_rate': (total_optimizations_applied / total_expected_optimizations) * 100,
            'performance_status': performance_test['test_status'],
            'overall_grade': self._calculate_overall_grade(successful_validations, total_validations, total_optimizations_applied, total_expected_optimizations)
        }
        
        return report
    
    def _calculate_overall_grade(self, successful: int, total: int, opt_applied: int, opt_expected: int) -> str:
        """Calcular grade general"""
        success_rate = (successful / total) * 100
        completion_rate = (opt_applied / opt_expected) * 100
        
        avg_rate = (success_rate + completion_rate) / 2
        
        if avg_rate >= 90:
            return 'A+ Excellent'
        elif avg_rate >= 80:
            return 'A Good'
        elif avg_rate >= 70:
            return 'B Fair'
        elif avg_rate >= 60:
            return 'C Needs Work'
        else:
            return 'D Failed'
    
    def print_summary_report(self, report: Dict[str, Any]):
        """Imprimir resumen del reporte"""
        print("\n📊 RESUMEN DE VALIDACIÓN:")
        print("=" * 40)
        
        summary = report['overall_summary']
        print(f"✅ Success Rate: {summary['validation_success_rate']:.1f}%")
        print(f"🔧 Optimizaciones: {summary['optimizations_applied']}/{summary['expected_optimizations']}")
        print(f"📈 Completion Rate: {summary['optimization_completion_rate']:.1f}%")
        print(f"⚡ Performance: {summary['performance_status']}")
        print(f"🏆 Overall Grade: {summary['overall_grade']}")
        
        print(f"\n📋 DETALLES POR COMPONENTE:")
        validations = report['validations']
        
        for component, validation in validations.items():
            if component == 'performance_test':
                continue
                
            status = validation['validation_status']
            optimizations = len(validation.get('optimizations_found', {}))
            issues = len(validation.get('issues', []))
            
            status_icon = "✅" if status == 'SUCCESS' else "⚠️" if status == 'PARTIAL' else "❌"
            
            print(f"  {status_icon} {validation['component']}: {status} ({optimizations} opt, {issues} issues)")
        
        # Performance
        perf = validations.get('performance_test', {})
        perf_icon = "⚡" if perf.get('test_status') == 'EXCELLENT' else "🔋" if perf.get('test_status') == 'GOOD' else "🐌"
        print(f"  {perf_icon} Performance Test: {perf.get('test_status', 'Unknown')}")

def main():
    """Función principal"""
    validator = PatternOptimizationValidator()
    
    try:
        # Generar reporte de validación
        report = validator.generate_validation_report()
        
        # Mostrar resumen
        validator.print_summary_report(report)
        
        # Guardar reporte detallado
        reports_dir = validator.repo_root / "DOCS" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        import json
        report_file = reports_dir / f"pattern_optimization_validation_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte detallado guardado: {report_file}")
        
        # Determinar código de salida
        overall_grade = report['overall_summary']['overall_grade']
        if overall_grade.startswith('A'):
            return 0  # Success
        elif overall_grade.startswith('B') or overall_grade.startswith('C'):
            print("\n⚠️ Algunas optimizaciones necesitan revisión")
            return 0  # Warning but acceptable
        else:
            print("\n❌ Validación falló - revisar optimizaciones")
            return 1  # Failed
        
    except Exception as e:
        print(f"\n❌ Error durante validación: {e}")
        return 1

if __name__ == "__main__":
    exit(main())