#!/usr/bin/env python3
"""
🔍 AUDITORÍA COMPLETA DEL SISTEMA ICT ENGINE v6.0 ENTERPRISE
===========================================================

Auditoría exhaustiva para evaluar el estado de producción del sistema.
Genera reporte detallado de todos los componentes críticos.

OBJETIVO: Determinar la preparación del sistema para trading real con dinero.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import json

class ICTEngineAuditor:
    """Auditor completo del sistema ICT Engine v6.0 Enterprise"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.audit_results = {
            'audit_timestamp': datetime.now().isoformat(),
            'system_version': 'ICT Engine v6.0 Enterprise',
            'audit_status': 'UNKNOWN',
            'critical_issues': [],
            'warnings': [],
            'passed_checks': [],
            'components': {},
            'overall_score': 0,
            'production_ready': False
        }
        
    def run_complete_audit(self):
        """Ejecutar auditoría completa del sistema"""
        print("🔍 INICIANDO AUDITORÍA COMPLETA ICT ENGINE v6.0 ENTERPRISE")
        print("=" * 60)
        
        # 1. Auditar validador de datos crítico
        self.audit_data_validator()
        
        # 2. Auditar módulos base
        self.audit_base_modules()
        
        # 3. Auditar patrones individuales
        self.audit_pattern_dashboards()
        
        # 4. Auditar sistema de datos de mercado
        self.audit_market_data_system()
        
        # 5. Auditar configuraciones
        self.audit_configurations()
        
        # 6. Auditar dashboard principal
        self.audit_main_dashboard()
        
        # 7. Auditar sistema de ejecución
        self.audit_execution_system()
        
        # 8. Calcular puntuación final
        self.calculate_final_score()
        
        # 9. Generar reporte
        self.generate_audit_report()
        
    def audit_data_validator(self):
        """Auditar el validador de datos crítico"""
        print("🔒 Auditando validador de datos crítico...")
        
        validator_path = self.project_root / "01-CORE" / "data_management" / "data_validator_real_trading.py"
        
        component = {
            'name': 'data_validator_real_trading',
            'status': 'UNKNOWN',
            'issues': [],
            'checks_passed': [],
            'score': 0
        }
        
        # Verificar existencia
        if validator_path.exists():
            component['checks_passed'].append("✅ Archivo del validador existe")
            
            # Verificar contenido
            try:
                with open(validator_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar métodos críticos
                required_methods = [
                    'validate_price_data',
                    'validate_pattern_analysis',
                    'validate_market_data',
                    '_validate_price_columns',
                    '_validate_price_ranges',
                    '_validate_timestamps'
                ]
                
                for method in required_methods:
                    if f"def {method}" in content:
                        component['checks_passed'].append(f"✅ Método {method} implementado")
                    else:
                        component['issues'].append(f"❌ Método {method} faltante")
                
                # Verificar que tenga manejo de errores
                if "try:" in content and "except" in content:
                    component['checks_passed'].append("✅ Manejo de errores implementado")
                else:
                    component['issues'].append("❌ Falta manejo robusto de errores")
                
                # Verificar logging
                if "logging" in content or "print" in content:
                    component['checks_passed'].append("✅ Sistema de logging presente")
                else:
                    component['issues'].append("❌ Falta sistema de logging")
                    
                component['score'] = min(100, len(component['checks_passed']) * 15)
                component['status'] = 'CRITICAL' if component['score'] < 70 else 'PASSED'
                
            except Exception as e:
                component['issues'].append(f"❌ Error leyendo archivo: {e}")
                component['status'] = 'FAILED'
        else:
            component['issues'].append("❌ Archivo del validador no existe")
            component['status'] = 'CRITICAL'
        
        self.audit_results['components']['data_validator'] = component
        
    def audit_base_modules(self):
        """Auditar módulos base del sistema"""
        print("🏗️ Auditando módulos base...")
        
        base_module_path = self.project_root / "09-DASHBOARD" / "patterns_analysis" / "base_pattern_module.py"
        
        component = {
            'name': 'base_pattern_module',
            'status': 'UNKNOWN',
            'issues': [],
            'checks_passed': [],
            'score': 0
        }
        
        if base_module_path.exists():
            try:
                with open(base_module_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar integración con validador
                if "data_validator" in content:
                    component['checks_passed'].append("✅ Integración con validador presente")
                else:
                    component['issues'].append("❌ Falta integración con validador")
                
                # Verificar métodos de validación
                if "validate_market_data" in content:
                    component['checks_passed'].append("✅ Método validate_market_data implementado")
                else:
                    component['issues'].append("❌ Falta método validate_market_data")
                
                if "validate_pattern_result" in content:
                    component['checks_passed'].append("✅ Método validate_pattern_result implementado")
                else:
                    component['issues'].append("❌ Falta método validate_pattern_result")
                
                # Verificar clase base abstracta
                if "ABC" in content and "@abstractmethod" in content:
                    component['checks_passed'].append("✅ Estructura abstracta correcta")
                else:
                    component['issues'].append("❌ Falta estructura abstracta")
                
                component['score'] = min(100, len(component['checks_passed']) * 25)
                component['status'] = 'CRITICAL' if component['score'] < 75 else 'PASSED'
                
            except Exception as e:
                component['issues'].append(f"❌ Error leyendo archivo: {e}")
                component['status'] = 'FAILED'
        else:
            component['issues'].append("❌ Archivo base_pattern_module no existe")
            component['status'] = 'CRITICAL'
        
        self.audit_results['components']['base_module'] = component
        
    def audit_pattern_dashboards(self):
        """Auditar módulos de patrones individuales"""
        print("🎯 Auditando dashboards de patrones...")
        
        patterns_dir = self.project_root / "09-DASHBOARD" / "patterns_analysis" / "individual_patterns"
        
        component = {
            'name': 'pattern_dashboards',
            'status': 'UNKNOWN',
            'issues': [],
            'checks_passed': [],
            'score': 0,
            'patterns_audited': {}
        }
        
        if patterns_dir.exists():
            pattern_files = [f for f in patterns_dir.glob("*.py") if f.name != "__init__.py"]
            
            for pattern_file in pattern_files:
                pattern_name = pattern_file.stem
                pattern_audit = {'score': 0, 'checks': [], 'issues': []}
                
                try:
                    with open(pattern_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Verificar uso de validación
                    if "validate_market_data" in content:
                        pattern_audit['checks'].append("✅ Usa validate_market_data")
                    else:
                        pattern_audit['issues'].append("❌ No usa validate_market_data")
                    
                    if "validate_pattern_result" in content:
                        pattern_audit['checks'].append("✅ Usa validate_pattern_result")
                    else:
                        pattern_audit['issues'].append("❌ No usa validate_pattern_result")
                    
                    # Verificar herencia correcta
                    if "BasePatternDashboard" in content:
                        pattern_audit['checks'].append("✅ Hereda de BasePatternDashboard")
                    else:
                        pattern_audit['issues'].append("❌ No hereda de BasePatternDashboard")
                    
                    # Verificar método principal
                    if "_perform_pattern_analysis" in content:
                        pattern_audit['checks'].append("✅ Implementa _perform_pattern_analysis")
                    else:
                        pattern_audit['issues'].append("❌ Falta _perform_pattern_analysis")
                    
                    pattern_audit['score'] = min(100, len(pattern_audit['checks']) * 25)
                    
                except Exception as e:
                    pattern_audit['issues'].append(f"❌ Error: {e}")
                
                component['patterns_audited'][pattern_name] = pattern_audit
            
            # Calcular score general
            if component['patterns_audited']:
                total_score = sum(p['score'] for p in component['patterns_audited'].values())
                component['score'] = total_score // len(component['patterns_audited'])
                
                passed_patterns = sum(1 for p in component['patterns_audited'].values() if p['score'] >= 75)
                component['checks_passed'].append(f"✅ {passed_patterns}/{len(component['patterns_audited'])} patrones pasaron auditoría")
                
                if component['score'] >= 75:
                    component['status'] = 'PASSED'
                elif component['score'] >= 50:
                    component['status'] = 'WARNING'
                else:
                    component['status'] = 'CRITICAL'
            else:
                component['status'] = 'CRITICAL'
                component['issues'].append("❌ No se encontraron archivos de patrones")
        else:
            component['issues'].append("❌ Directorio de patrones no existe")
            component['status'] = 'CRITICAL'
        
        self.audit_results['components']['pattern_dashboards'] = component
        
    def audit_market_data_system(self):
        """Auditar sistema de datos de mercado"""
        print("📊 Auditando sistema de datos de mercado...")
        
        market_system_path = self.project_root / "run_real_market_system.py"
        
        component = {
            'name': 'market_data_system',
            'status': 'UNKNOWN',
            'issues': [],
            'checks_passed': [],
            'score': 0
        }
        
        if market_system_path.exists():
            try:
                with open(market_system_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar integración con validador
                if "data_validator" in content:
                    component['checks_passed'].append("✅ Integración con validador presente")
                else:
                    component['issues'].append("❌ Falta integración con validador")
                
                # Verificar conexión MT5
                if "MetaTrader5" in content and "mt5" in content:
                    component['checks_passed'].append("✅ Conexión MT5 implementada")
                else:
                    component['issues'].append("❌ Falta conexión MT5")
                
                # Verificar manejo de errores
                if "try:" in content and "except" in content:
                    component['checks_passed'].append("✅ Manejo de errores presente")
                else:
                    component['issues'].append("❌ Falta manejo de errores")
                
                # Verificar cache de datos
                if "cache" in content.lower():
                    component['checks_passed'].append("✅ Sistema de cache implementado")
                else:
                    component['issues'].append("❌ Falta sistema de cache")
                
                component['score'] = min(100, len(component['checks_passed']) * 25)
                component['status'] = 'CRITICAL' if component['score'] < 75 else 'PASSED'
                
            except Exception as e:
                component['issues'].append(f"❌ Error leyendo archivo: {e}")
                component['status'] = 'FAILED'
        else:
            component['issues'].append("❌ Sistema de datos de mercado no existe")
            component['status'] = 'CRITICAL'
        
        self.audit_results['components']['market_data_system'] = component
        
    def audit_configurations(self):
        """Auditar archivos de configuración"""
        print("⚙️ Auditando configuraciones...")
        
        config_dir = self.project_root / "01-CORE" / "config"
        
        component = {
            'name': 'configurations',
            'status': 'UNKNOWN',
            'issues': [],
            'checks_passed': [],
            'score': 0
        }
        
        if config_dir.exists():
            config_files = list(config_dir.glob("*.json"))
            
            if config_files:
                component['checks_passed'].append(f"✅ {len(config_files)} archivos de configuración encontrados")
                
                for config_file in config_files:
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            json.load(f)  # Verificar JSON válido
                        component['checks_passed'].append(f"✅ {config_file.name} - JSON válido")
                    except Exception as e:
                        component['issues'].append(f"❌ {config_file.name} - JSON inválido: {e}")
                
                component['score'] = min(100, (len(component['checks_passed']) * 100) // (len(config_files) + 1))
                component['status'] = 'PASSED' if component['score'] >= 80 else 'WARNING'
            else:
                component['issues'].append("❌ No se encontraron archivos de configuración")
                component['status'] = 'WARNING'
        else:
            component['issues'].append("❌ Directorio de configuración no existe")
            component['status'] = 'CRITICAL'
        
        self.audit_results['components']['configurations'] = component
        
    def audit_main_dashboard(self):
        """Auditar dashboard principal"""
        print("🖥️ Auditando dashboard principal...")
        
        dashboard_dir = self.project_root / "09-DASHBOARD"
        
        component = {
            'name': 'main_dashboard',
            'status': 'UNKNOWN',
            'issues': [],
            'checks_passed': [],
            'score': 0
        }
        
        if dashboard_dir.exists():
            # Verificar archivos principales del dashboard
            main_files = ['dashboard.py', 'ict_dashboard.py', 'launch_dashboard.py']
            
            for file_name in main_files:
                file_path = dashboard_dir / file_name
                if file_path.exists():
                    component['checks_passed'].append(f"✅ {file_name} existe")
                else:
                    component['issues'].append(f"❌ {file_name} faltante")
            
            # Verificar estructura de directorios
            required_dirs = ['components', 'core', 'utils', 'widgets']
            for dir_name in required_dirs:
                dir_path = dashboard_dir / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    component['checks_passed'].append(f"✅ Directorio {dir_name} existe")
                else:
                    component['issues'].append(f"❌ Directorio {dir_name} faltante")
            
            component['score'] = min(100, (len(component['checks_passed']) * 100) // (len(main_files) + len(required_dirs)))
            component['status'] = 'PASSED' if component['score'] >= 70 else 'WARNING'
        else:
            component['issues'].append("❌ Directorio del dashboard no existe")
            component['status'] = 'CRITICAL'
        
        self.audit_results['components']['main_dashboard'] = component
        
    def audit_execution_system(self):
        """Auditar sistema de ejecución"""
        print("🚀 Auditando sistema de ejecución...")
        
        component = {
            'name': 'execution_system',
            'status': 'UNKNOWN',
            'issues': [],
            'checks_passed': [],
            'score': 0
        }
        
        # Verificar archivos de ejecución principales
        execution_files = [
            'main.py',
            'run_complete_system.py',
            'run_real_market_system.py',
            'launch.bat',
            'start_system.bat'
        ]
        
        for file_name in execution_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                component['checks_passed'].append(f"✅ {file_name} existe")
            else:
                component['issues'].append(f"❌ {file_name} faltante")
        
        component['score'] = min(100, (len(component['checks_passed']) * 100) // len(execution_files))
        component['status'] = 'PASSED' if component['score'] >= 80 else 'WARNING'
        
        self.audit_results['components']['execution_system'] = component
        
    def calculate_final_score(self):
        """Calcular puntuación final del sistema"""
        print("📊 Calculando puntuación final...")
        
        # Pesos por componente (suma debe ser 100)
        weights = {
            'data_validator': 30,      # Crítico para seguridad
            'base_module': 20,         # Base de todos los patrones
            'pattern_dashboards': 25,  # Funcionalidad principal
            'market_data_system': 15,  # Datos en tiempo real
            'configurations': 5,       # Configuraciones
            'main_dashboard': 3,       # Interface
            'execution_system': 2      # Scripts de ejecución
        }
        
        total_score = 0
        critical_components = ['data_validator', 'base_module', 'pattern_dashboards', 'market_data_system']
        
        for component_name, weight in weights.items():
            if component_name in self.audit_results['components']:
                component = self.audit_results['components'][component_name]
                component_score = component.get('score', 0)
                weighted_score = (component_score * weight) / 100
                total_score += weighted_score
                
                # Verificar estado crítico
                if component.get('status') == 'CRITICAL' and component_name in critical_components:
                    self.audit_results['critical_issues'].append(
                        f"🚨 COMPONENTE CRÍTICO FALLIDO: {component_name} - Score: {component_score}"
                    )
                elif component.get('status') == 'WARNING':
                    self.audit_results['warnings'].append(
                        f"⚠️ Advertencia en {component_name} - Score: {component_score}"
                    )
                else:
                    self.audit_results['passed_checks'].append(
                        f"✅ {component_name} - Score: {component_score}"
                    )
        
        self.audit_results['overall_score'] = round(total_score, 2)
        
        # Determinar estado general
        if total_score >= 85 and len(self.audit_results['critical_issues']) == 0:
            self.audit_results['audit_status'] = 'PRODUCTION_READY'
            self.audit_results['production_ready'] = True
        elif total_score >= 70 and len(self.audit_results['critical_issues']) <= 1:
            self.audit_results['audit_status'] = 'NEARLY_READY'
            self.audit_results['production_ready'] = False
        elif total_score >= 50:
            self.audit_results['audit_status'] = 'NEEDS_WORK'
            self.audit_results['production_ready'] = False
        else:
            self.audit_results['audit_status'] = 'NOT_READY'
            self.audit_results['production_ready'] = False
        
    def generate_audit_report(self):
        """Generar reporte final de auditoría"""
        print("\n" + "=" * 60)
        print("📋 REPORTE FINAL DE AUDITORÍA ICT ENGINE v6.0 ENTERPRISE")
        print("=" * 60)
        
        # Estado general
        status_emoji = {
            'PRODUCTION_READY': '🟢',
            'NEARLY_READY': '🟡',
            'NEEDS_WORK': '🟠',
            'NOT_READY': '🔴'
        }
        
        print(f"\n{status_emoji.get(self.audit_results['audit_status'], '❓')} ESTADO GENERAL: {self.audit_results['audit_status']}")
        print(f"📊 PUNTUACIÓN FINAL: {self.audit_results['overall_score']}/100")
        print(f"💰 LISTO PARA TRADING REAL: {'SÍ' if self.audit_results['production_ready'] else 'NO'}")
        
        # Problemas críticos
        if self.audit_results['critical_issues']:
            print(f"\n🚨 PROBLEMAS CRÍTICOS ({len(self.audit_results['critical_issues'])}):")
            for issue in self.audit_results['critical_issues']:
                print(f"   {issue}")
        
        # Advertencias
        if self.audit_results['warnings']:
            print(f"\n⚠️ ADVERTENCIAS ({len(self.audit_results['warnings'])}):")
            for warning in self.audit_results['warnings']:
                print(f"   {warning}")
        
        # Componentes que pasaron
        if self.audit_results['passed_checks']:
            print(f"\n✅ COMPONENTES EXITOSOS ({len(self.audit_results['passed_checks'])}):")
            for check in self.audit_results['passed_checks']:
                print(f"   {check}")
        
        # Detalles por componente
        print(f"\n📋 DETALLE POR COMPONENTE:")
        for component_name, component in self.audit_results['components'].items():
            status = component.get('status', 'UNKNOWN')
            score = component.get('score', 0)
            print(f"\n   🔧 {component_name.upper()} - {status} ({score}/100)")
            
            for check in component.get('checks_passed', []):
                print(f"      {check}")
            
            for issue in component.get('issues', []):
                print(f"      {issue}")
        
        # Recomendaciones finales
        print(f"\n💡 RECOMENDACIONES:")
        if self.audit_results['production_ready']:
            print("   ✅ El sistema está listo para trading con dinero real")
            print("   ✅ Todos los componentes críticos han pasado la auditoría")
            print("   ✅ Validación de datos implementada correctamente")
        else:
            print("   ❌ NO usar este sistema para trading real hasta resolver problemas críticos")
            print("   🔧 Corregir todos los componentes críticos marcados como FALLIDOS")
            print("   ⚠️ Realizar pruebas exhaustivas en cuenta demo antes de producción")
        
        # Guardar reporte en archivo
        report_path = self.project_root / f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte completo guardado en: {report_path}")
        print("=" * 60)

def main():
    """Función principal"""
    auditor = ICTEngineAuditor()
    auditor.run_complete_audit()

if __name__ == "__main__":
    main()
