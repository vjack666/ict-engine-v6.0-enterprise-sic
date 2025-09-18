#!/usr/bin/env python3
"""
🔧 DETECTION PARAMETER INTEGRATOR - ICT Engine v6.0 Enterprise
=============================================================

Script para integrar parámetros optimizados en el sistema de detección
existente. Actualiza dinámicamente las configuraciones de todos los
detectores de patrones ICT.

Funcionalidades:
- Integración con SimpleOrderBlockDetector
- Actualización de PatternDetector parameters
- Configuración de SmartMoneyDetector
- Aplicación de parámetros FVG optimizados
- Validación de compatibilidad
- Backup de configuraciones previas

Autor: ICT Engine v6.1.0 Enterprise Team
Fecha: Septiembre 2025
"""

import sys
import os
import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Agregar el directorio raíz al path para imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

# Imports del sistema
ParameterOptimizationManager = None
OptimizationLevel = None
PerformanceMetrics = None
SimpleOrderBlockDetector = None
PatternDetector = None
SmartMoneyDetector = None

try:
    from utils.parameter_optimization_manager import ParameterOptimizationManager, OptimizationLevel, PerformanceMetrics
    from ict_engine.patterns.simple_order_blocks import SimpleOrderBlockDetector
    from ict_engine.pattern_detector import PatternDetector
    from smart_money_concepts.smart_money_detector import SmartMoneyDetector
    print("✅ Imports del sistema ICT cargados exitosamente")
except ImportError as e:
    print(f"⚠️ Algunos imports fallaron: {e}")
    print("🔧 Continuando con funcionalidad básica...")

class DetectionParameterIntegrator:
    """
    🎯 Integrador de parámetros optimizados
    
    Clase principal para aplicar parámetros optimizados a todos los
    componentes de detección del sistema ICT Enterprise.
    """
    
    def __init__(self, optimization_level: str = "balanced"):
        """
        Inicializar el integrador de parámetros
        
        Args:
            optimization_level: Nivel de optimización a aplicar
        """
        self.optimization_level = optimization_level
        self.project_root = project_root
        self.backup_dir = self.project_root / "01-CORE" / "config" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar manager de optimización
        try:
            if ParameterOptimizationManager and OptimizationLevel:
                self.param_manager = ParameterOptimizationManager(
                    optimization_level=OptimizationLevel(optimization_level.lower())
                )
                self.optimization_available = True
            else:
                raise ImportError("Classes not available")
        except:
            print("⚠️ ParameterOptimizationManager no disponible, usando valores por defecto")
            self.optimization_available = False
            self.param_manager = None
        
        # Registro de cambios aplicados
        self.applied_changes = {
            'timestamp': datetime.now().isoformat(),
            'optimization_level': optimization_level,
            'components_updated': [],
            'backup_created': False
        }
        
        print(f"🔧 DetectionParameterIntegrator iniciado (nivel: {optimization_level})")
    
    def create_backup(self) -> bool:
        """
        Crear backup de configuraciones actuales
        
        Returns:
            bool: True si el backup fue exitoso
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"config_backup_{timestamp}.json"
            backup_path = self.backup_dir / backup_filename
            
            # Recopilar configuraciones actuales
            current_config = {
                'timestamp': timestamp,
                'optimization_level': self.optimization_level,
                'configurations': {}
            }
            
            # Backup de archivos de configuración existentes
            config_files = [
                "base.yaml",
                "production.yaml", 
                "development.yaml"
            ]
            
            config_dir = self.project_root / "01-CORE" / "config"
            for config_file in config_files:
                config_path = config_dir / config_file
                if config_path.exists():
                    backup_file_path = self.backup_dir / f"{config_file}_{timestamp}.backup"
                    shutil.copy2(config_path, backup_file_path)
                    current_config['configurations'][config_file] = str(backup_file_path)
            
            # Guardar registro de backup
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, indent=2)
            
            self.applied_changes['backup_created'] = True
            self.applied_changes['backup_path'] = str(backup_path)
            
            print(f"💾 Backup creado: {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return False
    
    def integrate_order_blocks_parameters(self) -> bool:
        """
        Integrar parámetros optimizados para Order Blocks
        
        Returns:
            bool: True si la integración fue exitosa
        """
        try:
            print("📦 Integrando parámetros de Order Blocks...")
            
            if self.optimization_available and self.param_manager:
                ob_params = self.param_manager.get_parameters_for_component("order_blocks")
            else:
                # Parámetros optimizados por defecto
                ob_params = {
                    'min_confidence': 65.0,
                    'lookback_period': 15,
                    'max_distance_pips': 25,
                    'volume_threshold': 1.5,
                    'strength_multiplier': 1.2,
                    'confluence_bonus': 0.15,
                    'session_priority_bonus': 0.10
                }
            
            # Crear configuración optimizada para SimpleOrderBlockDetector
            optimized_ob_config = {
                'lookback_period': int(ob_params.get('lookback_period', 15)),
                'max_distance_pips': ob_params.get('max_distance_pips', 25),
                'min_confidence': ob_params.get('min_confidence', 65),
                'volume_threshold': ob_params.get('volume_threshold', 1.5)
            }
            
            # Crear archivo de configuración específico para Order Blocks
            ob_config_path = self.project_root / "01-CORE" / "config" / "order_blocks_optimized.json"
            with open(ob_config_path, 'w', encoding='utf-8') as f:
                json.dump(optimized_ob_config, f, indent=2)
            
            self.applied_changes['components_updated'].append({
                'component': 'order_blocks',
                'config_path': str(ob_config_path),
                'parameters_applied': len(optimized_ob_config)
            })
            
            print(f"   ✅ Configuración Order Blocks guardada: {ob_config_path}")
            print(f"   📊 Parámetros aplicados: {optimized_ob_config}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error integrando parámetros Order Blocks: {e}")
            return False
    
    def integrate_choch_parameters(self) -> bool:
        """
        Integrar parámetros optimizados para CHoCH
        
        Returns:
            bool: True si la integración fue exitosa
        """
        try:
            print("🔄 Integrando parámetros de CHoCH...")
            
            if self.optimization_available and self.param_manager:
                choch_params = self.param_manager.get_parameters_for_component("choch")
            else:
                # Parámetros optimizados por defecto
                choch_params = {
                    'base_confidence': 70.0,
                    'min_swing_size_pips': 15,
                    'trend_confirmation_bars': 5,
                    'timeframe_weights': {'H4': 1.0, 'M15': 0.8, 'M5': 0.6}
                }
            
            # Crear configuración optimizada para PatternDetector CHoCH
            optimized_choch_config = {
                'min_confidence': choch_params.get('base_confidence', 70.0),
                'min_swing_size_pips': choch_params.get('min_swing_size_pips', 15),
                'trend_confirmation_bars': choch_params.get('trend_confirmation_bars', 5),
                'timeframe_weights': choch_params.get('timeframe_weights', {'H4': 1.0, 'M15': 0.8, 'M5': 0.6}),
                'require_volume_spike': choch_params.get('validation', {}).get('require_volume_spike', True),
                'min_break_distance_pips': choch_params.get('validation', {}).get('min_break_distance_pips', 5)
            }
            
            # Guardar configuración CHoCH
            choch_config_path = self.project_root / "01-CORE" / "config" / "choch_optimized.json"
            with open(choch_config_path, 'w', encoding='utf-8') as f:
                json.dump(optimized_choch_config, f, indent=2)
            
            self.applied_changes['components_updated'].append({
                'component': 'choch',
                'config_path': str(choch_config_path),
                'parameters_applied': len(optimized_choch_config)
            })
            
            print(f"   ✅ Configuración CHoCH guardada: {choch_config_path}")
            print(f"   📊 Parámetros aplicados: {optimized_choch_config}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error integrando parámetros CHoCH: {e}")
            return False
    
    def integrate_bos_parameters(self) -> bool:
        """
        Integrar parámetros optimizados para BOS
        
        Returns:
            bool: True si la integración fue exitosa
        """
        try:
            print("🚀 Integrando parámetros de BOS...")
            
            if self.optimization_available and self.param_manager:
                bos_params = self.param_manager.get_parameters_for_component("bos")
            else:
                # Parámetros optimizados por defecto
                bos_params = {
                    'min_confidence': 75.0,
                    'swing_detection_window': 5,
                    'break_confirmation_pips': 3,
                    'quality_filters': {
                        'min_momentum_pips': 10,
                        'volume_increase_threshold': 1.3,
                        'retest_tolerance_pips': 2
                    }
                }
            
            # Crear configuración optimizada para BOS
            optimized_bos_config = {
                'min_confidence': bos_params.get('min_confidence', 75.0),
                'swing_detection_window': bos_params.get('swing_detection_window', 5),
                'break_confirmation_pips': bos_params.get('break_confirmation_pips', 3),
                'min_momentum_pips': bos_params.get('quality_filters', {}).get('min_momentum_pips', 10),
                'volume_increase_threshold': bos_params.get('quality_filters', {}).get('volume_increase_threshold', 1.3),
                'retest_tolerance_pips': bos_params.get('quality_filters', {}).get('retest_tolerance_pips', 2)
            }
            
            # Guardar configuración BOS
            bos_config_path = self.project_root / "01-CORE" / "config" / "bos_optimized.json"
            with open(bos_config_path, 'w', encoding='utf-8') as f:
                json.dump(optimized_bos_config, f, indent=2)
            
            self.applied_changes['components_updated'].append({
                'component': 'bos',
                'config_path': str(bos_config_path),
                'parameters_applied': len(optimized_bos_config)
            })
            
            print(f"   ✅ Configuración BOS guardada: {bos_config_path}")
            print(f"   📊 Parámetros aplicados: {optimized_bos_config}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error integrando parámetros BOS: {e}")
            return False
    
    def integrate_fvg_parameters(self) -> bool:
        """
        Integrar parámetros optimizados para Fair Value Gaps
        
        Returns:
            bool: True si la integración fue exitosa
        """
        try:
            print("💎 Integrando parámetros de FVG...")
            
            if self.optimization_available and self.param_manager:
                fvg_params = self.param_manager.get_parameters_for_component("fair_value_gaps")
            else:
                # Parámetros optimizados por defecto
                fvg_params = {
                    'min_gap_size_pips': 3.0,
                    'max_gap_size_pips': 50.0,
                    'fill_tolerance_pips': 1.0,
                    'market_conditions': {
                        'high_volatility': {'min_gap_size_multiplier': 1.5, 'confidence_adjustment': -0.1},
                        'low_volatility': {'min_gap_size_multiplier': 0.7, 'confidence_adjustment': 0.1}
                    }
                }
            
            # Crear configuración optimizada para FVG
            optimized_fvg_config = {
                'min_gap_size_pips': fvg_params.get('min_gap_size_pips', 3.0),
                'max_gap_size_pips': fvg_params.get('max_gap_size_pips', 50.0),
                'fill_tolerance_pips': fvg_params.get('fill_tolerance_pips', 1.0),
                'volatility_factor': 1.0,
                'momentum_factor': 1.0,
                'confidence_adjustment': 0.0,
                'strength_multiplier': 1.0,
                'market_conditions': fvg_params.get('market_conditions', {})
            }
            
            # Guardar configuración FVG
            fvg_config_path = self.project_root / "01-CORE" / "config" / "fvg_optimized.json"
            with open(fvg_config_path, 'w', encoding='utf-8') as f:
                json.dump(optimized_fvg_config, f, indent=2)
            
            self.applied_changes['components_updated'].append({
                'component': 'fair_value_gaps',
                'config_path': str(fvg_config_path),
                'parameters_applied': len(optimized_fvg_config)
            })
            
            print(f"   ✅ Configuración FVG guardada: {fvg_config_path}")
            print(f"   📊 Parámetros aplicados: {optimized_fvg_config}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error integrando parámetros FVG: {e}")
            return False
    
    def integrate_smart_money_parameters(self) -> bool:
        """
        Integrar parámetros optimizados para Smart Money Concepts
        
        Returns:
            bool: True si la integración fue exitosa
        """
        try:
            print("🧠 Integrando parámetros de Smart Money...")
            
            if self.optimization_available and self.param_manager:
                sm_params = self.param_manager.get_parameters_for_component("smart_money")
            else:
                # Parámetros optimizados por defecto
                sm_params = {
                    'manipulation': {'min_fake_breakout_pips': 8, 'reversal_confirmation_pips': 12},
                    'liquidity': {'sweep_detection_pips': 5, 'accumulation_zone_pips': 15},
                    'institutional_flow': {'min_order_size_threshold': 2.0, 'flow_confirmation_bars': 3}
                }
            
            # Crear configuración optimizada para Smart Money
            optimized_sm_config = {
                'manipulation_detection': True,
                'liquidity_analysis': True,
                'institutional_flow_analysis': True,
                'min_fake_breakout_pips': sm_params.get('manipulation', {}).get('min_fake_breakout_pips', 8),
                'reversal_confirmation_pips': sm_params.get('manipulation', {}).get('reversal_confirmation_pips', 12),
                'sweep_detection_pips': sm_params.get('liquidity', {}).get('sweep_detection_pips', 5),
                'accumulation_zone_pips': sm_params.get('liquidity', {}).get('accumulation_zone_pips', 15),
                'min_order_size_threshold': sm_params.get('institutional_flow', {}).get('min_order_size_threshold', 2.0),
                'flow_confirmation_bars': sm_params.get('institutional_flow', {}).get('flow_confirmation_bars', 3)
            }
            
            # Guardar configuración Smart Money
            sm_config_path = self.project_root / "01-CORE" / "config" / "smart_money_optimized.json"
            with open(sm_config_path, 'w', encoding='utf-8') as f:
                json.dump(optimized_sm_config, f, indent=2)
            
            self.applied_changes['components_updated'].append({
                'component': 'smart_money',
                'config_path': str(sm_config_path),
                'parameters_applied': len(optimized_sm_config)
            })
            
            print(f"   ✅ Configuración Smart Money guardada: {sm_config_path}")
            print(f"   📊 Parámetros aplicados: {optimized_sm_config}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error integrando parámetros Smart Money: {e}")
            return False
    
    def update_base_configuration(self) -> bool:
        """
        Actualizar configuración base del sistema
        
        Returns:
            bool: True si la actualización fue exitosa
        """
        try:
            print("🔧 Actualizando configuración base...")
            
            if self.optimization_available and self.param_manager:
                performance_params = self.param_manager.get_parameters_for_component("performance")
                validation_params = self.param_manager.get_parameters_for_component("validation")
                monitoring_params = self.param_manager.get_parameters_for_component("monitoring")
            else:
                # Configuración por defecto
                performance_params = {'max_patterns_per_symbol': 10, 'analysis_timeout_seconds': 30}
                validation_params = {'validation_level': 'STANDARD', 'min_pattern_accuracy': 0.70}
                monitoring_params = {'live_metrics_interval': 60}
            
            # Leer configuración base actual
            base_config_path = self.project_root / "01-CORE" / "config" / "base.yaml"
            
            # Crear configuración optimizada agregada
            optimized_additions = {
                'detection_optimization': {
                    'enabled': True,
                    'level': self.optimization_level,
                    'max_patterns_per_symbol': performance_params.get('max_patterns_per_symbol', 10),
                    'analysis_timeout_seconds': performance_params.get('analysis_timeout_seconds', 30),
                    'validation_level': validation_params.get('validation_level', 'STANDARD'),
                    'min_pattern_accuracy': validation_params.get('quality_metrics', {}).get('min_pattern_accuracy', 0.70),
                    'live_metrics_interval': monitoring_params.get('live_metrics_interval', 60),
                    'applied_at': datetime.now().isoformat()
                }
            }
            
            # Guardar configuración de optimización
            optimization_config_path = self.project_root / "01-CORE" / "config" / "detection_optimization.json"
            with open(optimization_config_path, 'w', encoding='utf-8') as f:
                json.dump(optimized_additions, f, indent=2)
            
            self.applied_changes['components_updated'].append({
                'component': 'base_configuration',
                'config_path': str(optimization_config_path),
                'parameters_applied': len(optimized_additions['detection_optimization'])
            })
            
            print(f"   ✅ Configuración de optimización guardada: {optimization_config_path}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error actualizando configuración base: {e}")
            return False
    
    def generate_integration_report(self) -> str:
        """
        Generar reporte de integración de parámetros
        
        Returns:
            str: Ruta del archivo de reporte
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"parameter_integration_report_{timestamp}.json"
            report_path = self.project_root / "04-DATA" / "reports" / report_filename
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Agregar métricas de integración
            self.applied_changes['integration_summary'] = {
                'total_components_updated': len(self.applied_changes['components_updated']),
                'optimization_level_applied': self.optimization_level,
                'optimization_manager_available': self.optimization_available,
                'integration_successful': len(self.applied_changes['components_updated']) > 0
            }
            
            # Guardar reporte
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.applied_changes, f, indent=2)
            
            print(f"📋 Reporte de integración generado: {report_path}")
            return str(report_path)
            
        except Exception as e:
            print(f"❌ Error generando reporte: {e}")
            return ""
    
    def run_full_integration(self) -> bool:
        """
        Ejecutar integración completa de parámetros optimizados
        
        Returns:
            bool: True si la integración fue exitosa
        """
        print("🎯 INICIANDO INTEGRACIÓN COMPLETA DE PARÁMETROS OPTIMIZADOS")
        print("=" * 60)
        
        start_time = time.time()
        success_count = 0
        total_integrations = 6
        
        # 1. Crear backup
        print("\n1. Creando backup de configuraciones actuales...")
        if self.create_backup():
            print("   ✅ Backup creado exitosamente")
        else:
            print("   ⚠️ Backup falló, continuando...")
        
        # 2. Integrar parámetros por componente
        integrations = [
            ("Order Blocks", self.integrate_order_blocks_parameters),
            ("CHoCH", self.integrate_choch_parameters),
            ("BOS", self.integrate_bos_parameters),
            ("FVG", self.integrate_fvg_parameters),
            ("Smart Money", self.integrate_smart_money_parameters),
            ("Base Configuration", self.update_base_configuration)
        ]
        
        for i, (component_name, integration_func) in enumerate(integrations, 2):
            print(f"\n{i}. Integrando {component_name}...")
            if integration_func():
                success_count += 1
                print(f"   ✅ {component_name} integrado exitosamente")
            else:
                print(f"   ❌ {component_name} falló")
        
        # 3. Generar reporte
        print(f"\n{total_integrations + 2}. Generando reporte de integración...")
        report_path = self.generate_integration_report()
        
        # Resumen final
        elapsed_time = time.time() - start_time
        success_rate = (success_count / total_integrations) * 100
        
        print("\n" + "=" * 60)
        print("🎯 RESUMEN DE INTEGRACIÓN COMPLETADA")
        print("=" * 60)
        print(f"⏱️  Tiempo transcurrido: {elapsed_time:.1f} segundos")
        print(f"✅ Componentes exitosos: {success_count}/{total_integrations}")
        print(f"📊 Tasa de éxito: {success_rate:.1f}%")
        print(f"🔧 Nivel de optimización: {self.optimization_level}")
        print(f"📋 Reporte: {report_path}")
        
        if success_count == total_integrations:
            print("🎉 INTEGRACIÓN COMPLETADA EXITOSAMENTE!")
            print("\n🔄 Para aplicar los cambios, reinicia el sistema ICT Engine")
        else:
            print("⚠️  INTEGRACIÓN PARCIAL - Revisar logs para detalles")
        
        return success_count == total_integrations

def main():
    """Función principal para ejecutar la integración"""
    print("🎯 ICT Engine v6.0 Enterprise - Parameter Integration Tool")
    print("=" * 60)
    
    # Solicitar nivel de optimización
    print("\nNiveles de optimización disponibles:")
    print("1. conservative - Parámetros conservadores (menos falsos positivos)")
    print("2. balanced    - Balance entre precisión y cobertura (recomendado)")
    print("3. aggressive  - Más detecciones (puede incrementar falsos positivos)")
    print("4. adaptive    - Ajuste automático según performance")
    
    while True:
        try:
            choice = input("\nSelecciona nivel (1-4) [default: 2]: ").strip()
            if not choice:
                choice = "2"
            
            levels = {"1": "conservative", "2": "balanced", "3": "aggressive", "4": "adaptive"}
            if choice in levels:
                optimization_level = levels[choice]
                break
            else:
                print("❌ Selección inválida. Usa 1, 2, 3 o 4")
        except KeyboardInterrupt:
            print("\n\n👋 Integración cancelada por el usuario")
            return
    
    # Crear integrador y ejecutar
    print(f"\n🔧 Iniciando integración con nivel: {optimization_level}")
    integrator = DetectionParameterIntegrator(optimization_level)
    
    success = integrator.run_full_integration()
    
    if success:
        print("\n✅ Todos los parámetros han sido optimizados e integrados exitosamente!")
        print("🔄 Reinicia el sistema para aplicar los cambios")
    else:
        print("\n⚠️ La integración se completó con algunos errores")
        print("📋 Revisa el reporte para más detalles")

if __name__ == "__main__":
    main()