#!/usr/bin/env python3
"""
🏭 PATTERN FACTORY - CONEXIÓN DIRECTA CON SISTEMA REAL
====================================================

Factory que auto-descubre patrones del sistema ICT Engine v6.0 Enterprise
y genera módulos de dashboard conectados ÚNICAMENTE con el sistema real.

NO crea datos hardcodeados ni simulados.
"""

import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Optional, Type

# Configurar rutas
dashboard_root = Path(__file__).parent.parent
project_root = dashboard_root.parent
sys.path.insert(0, str(project_root / "01-CORE"))

# Importar base
from base_pattern_module import BasePatternDashboard


class PatternFactory:
    """
    Factory para auto-descubrir y generar módulos de dashboard 
    conectados con el sistema real ICT Engine v6.0 Enterprise
    """
    
    def __init__(self):
        self.project_root = project_root
        self.dashboard_root = dashboard_root
        self.patterns_analysis_dir = dashboard_root / "patterns_analysis"
        self.individual_patterns_dir = self.patterns_analysis_dir / "individual_patterns"
        
        # Datos de patrones descubiertos
        self.core_patterns = {}
        self.dashboard_modules = {}
        
        # Crear directorio si no existe
        self.individual_patterns_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🏭 PatternFactory inicializado")
        print(f"📁 Directorio patrones: {self.individual_patterns_dir}")
    
    def auto_discover_and_generate(self):
        """Auto-descubrir patrones del sistema real y generar módulos dashboard"""
        print("\n🔍 INICIANDO AUTO-DESCUBRIMIENTO DE PATRONES REALES...")
        print("=" * 60)
        
        # 1. Descubrir patrones del sistema real
        self._discover_core_patterns()
        
        # 2. Verificar módulos dashboard existentes
        self._discover_existing_dashboard_modules()
        
        # 3. Generar módulos faltantes
        self._generate_missing_modules()
        
        # 4. Cargar todos los módulos
        self._load_all_modules()
        
        print("\n✅ AUTO-DESCUBRIMIENTO COMPLETADO")
        print(f"📊 Patrones core encontrados: {len(self.core_patterns)}")
        print(f"🎯 Módulos dashboard: {len(self.dashboard_modules)}")
    
    def _discover_core_patterns(self):
        """Descubrir patrones disponibles en el sistema real"""
        print("\n🔍 Descubriendo patrones del sistema real...")
        
        # 1. Buscar en analysis.pattern_detector
        try:
            from analysis.pattern_detector import PatternDetector
            detector = PatternDetector()
            
            # Buscar métodos _detect_*
            for method_name in dir(detector):
                if method_name.startswith('_detect_') and callable(getattr(detector, method_name)):
                    pattern_name = method_name.replace('_detect_', '')
                    self.core_patterns[pattern_name] = {
                        'detector_method': method_name,
                        'source': 'analysis.pattern_detector',
                        'detector_class': 'PatternDetector',
                        'available': True
                    }
            
            print(f"✅ PatternDetector: {len([p for p in self.core_patterns if self.core_patterns[p]['source'] == 'analysis.pattern_detector'])} patrones")
            
        except ImportError as e:
            print(f"⚠️ No se pudo cargar PatternDetector: {e}")
        
        # 2. Buscar en módulos enterprise específicos
        enterprise_patterns = {
            'silver_bullet': 'ict_engine.advanced_patterns.silver_bullet_enterprise',
            'judas_swing': 'ict_engine.advanced_patterns.judas_swing_enterprise',
            'liquidity_grab': 'ict_engine.advanced_patterns.liquidity_grab_enterprise',
            'order_block': 'ict_engine.advanced_patterns.order_block_enterprise',
            'fair_value_gap': 'ict_engine.advanced_patterns.fvg_enterprise',
            'optimal_trade_entry': 'ict_engine.advanced_patterns.ote_enterprise'
        }
        
        for pattern_name, module_path in enterprise_patterns.items():
            try:
                spec = importlib.util.find_spec(module_path)
                if spec is not None:
                    if pattern_name not in self.core_patterns:
                        self.core_patterns[pattern_name] = {
                            'detector_method': 'detect',
                            'source': module_path,
                            'detector_class': f'{pattern_name.title().replace("_", "")}Enterprise',
                            'available': True,
                            'enterprise': True
                        }
                    else:
                        # Marcar que tiene versión enterprise
                        self.core_patterns[pattern_name]['enterprise'] = True
                        self.core_patterns[pattern_name]['enterprise_source'] = module_path
            except Exception as e:
                print(f"⚠️ Error verificando {pattern_name} enterprise: {e}")
        
        # 3. Buscar en POI System
        try:
            from poi_system import POISystem
            poi_system = POISystem()
            
            # Buscar métodos relacionados con patrones
            poi_methods = [method for method in dir(poi_system) 
                          if any(pattern in method.lower() for pattern in ['detect', 'find', 'identify']) 
                          and callable(getattr(poi_system, method))
                          and not method.startswith('_')]
            
            for method in poi_methods:
                # Extraer nombre del patrón del método
                for pattern_word in ['order_block', 'fair_value_gap', 'liquidity', 'mitigation']:
                    if pattern_word in method.lower():
                        pattern_name = pattern_word
                        if pattern_name not in self.core_patterns:
                            self.core_patterns[pattern_name] = {
                                'detector_method': method,
                                'source': 'poi_system',
                                'detector_class': 'POISystem',
                                'available': True
                            }
                        break
            
            print(f"✅ POISystem: {len([p for p in self.core_patterns if self.core_patterns[p]['source'] == 'poi_system'])} patrones")
            
        except ImportError as e:
            print(f"⚠️ No se pudo cargar POISystem: {e}")
        
        print(f"📊 Total patrones descubiertos: {len(self.core_patterns)}")
        for name, info in self.core_patterns.items():
            enterprise_mark = " [ENTERPRISE]" if info.get('enterprise') else ""
            print(f"  • {name}: {info['source']}{enterprise_mark}")
    
    def _discover_existing_dashboard_modules(self):
        """Descubrir módulos de dashboard ya existentes"""
        print("\n🔍 Verificando módulos dashboard existentes...")
        
        pattern_files = list(self.individual_patterns_dir.glob("*_dashboard.py"))
        
        for file in pattern_files:
            try:
                # Extraer nombre del patrón del archivo
                pattern_name = file.stem.replace('_dashboard', '')
                
                # Verificar que el archivo contiene una clase válida
                if self._verify_dashboard_module(file):
                    self.dashboard_modules[pattern_name] = {
                        'file_path': file,
                        'module_name': file.stem,
                        'available': True
                    }
                    print(f"✅ Módulo encontrado: {pattern_name}")
                else:
                    print(f"⚠️ Módulo inválido: {pattern_name}")
            
            except Exception as e:
                print(f"⚠️ Error verificando {file.name}: {e}")
        
        print(f"📊 Módulos dashboard encontrados: {len(self.dashboard_modules)}")
    
    def _verify_dashboard_module(self, module_file: Path) -> bool:
        """Verificar que un módulo de dashboard es válido"""
        try:
            with open(module_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar elementos básicos
            required_elements = [
                'BasePatternDashboard',
                'def create_dashboard',
                '_perform_pattern_analysis',
                'create_dashboard_layout'
            ]
            
            return all(element in content for element in required_elements)
        
        except Exception:
            return False
    
    def _generate_missing_modules(self):
        """Generar módulos dashboard para patrones que no los tienen"""
        print("\n📝 Generando módulos dashboard faltantes...")
        
        # Encontrar patrones sin módulo dashboard
        missing_patterns = [
            pattern for pattern in self.core_patterns.keys()
            if pattern not in self.dashboard_modules
        ]
        
        if not missing_patterns:
            print("✅ Todos los patrones ya tienen módulos dashboard")
            return
        
        print(f"📝 Creando {len(missing_patterns)} módulos faltantes...")
        
        for pattern_name in missing_patterns:
            try:
                self._create_real_pattern_module(pattern_name)
                print(f"✅ Módulo creado: {pattern_name}")
            except Exception as e:
                print(f"⚠️ Error creando módulo {pattern_name}: {e}")
        
        # Re-descubrir módulos después de crear los faltantes
        self._discover_existing_dashboard_modules()
    
    def _create_real_pattern_module(self, pattern_name: str):
        """Crear módulo de dashboard conectado con sistema real"""
        
        # Usar el template real
        template_path = self.patterns_analysis_dir / "real_pattern_template.py"
        
        if not template_path.exists():
            print(f"⚠️ Template real no encontrado: {template_path}")
            return
        
        # Leer template
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Personalizar para el patrón específico
        class_name = ''.join(word.capitalize() for word in pattern_name.split('_')) + 'Dashboard'
        
        # Reemplazar clase base
        adapted_content = template_content.replace(
            'class RealPatternDashboard(BasePatternDashboard):',
            f'class {class_name}(BasePatternDashboard):'
        )
        
        # Personalizar constructor
        adapted_content = adapted_content.replace(
            'def __init__(self, pattern_name: str, config: Optional[Dict[str, Any]] = None):',
            f'def __init__(self, config: Optional[Dict[str, Any]] = None):'
        )
        
        adapted_content = adapted_content.replace(
            'super().__init__(pattern_name, config)',
            f'super().__init__("{pattern_name}", config)'
        )
        
        # Agregar función de creación
        adapted_content += f'''

# Función de creación para el factory
def create_dashboard(config: Optional[Dict[str, Any]] = None) -> {class_name}:
    """Crear instancia del dashboard de {pattern_name}"""
    return {class_name}(config)
'''
        
        # Crear archivo
        module_file = self.individual_patterns_dir / f"{pattern_name}_dashboard.py"
        with open(module_file, 'w', encoding='utf-8') as f:
            f.write(adapted_content)
        
        print(f"✅ Módulo real creado con imports correctos: {pattern_name} -> {module_file.name}")
    
    def _load_all_modules(self):
        """Cargar todos los módulos de dashboard disponibles"""
        print("\n📦 Cargando módulos de dashboard...")
        
        for pattern_name, module_info in self.dashboard_modules.items():
            try:
                # Cargar módulo dinámicamente
                module_file = module_info['file_path']
                spec = importlib.util.spec_from_file_location(
                    module_info['module_name'], 
                    module_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Verificar función create_dashboard
                if hasattr(module, 'create_dashboard'):
                    module_info['module'] = module
                    module_info['create_function'] = module.create_dashboard
                    print(f"✅ Módulo cargado: {pattern_name}")
                else:
                    print(f"⚠️ Módulo sin función create_dashboard: {pattern_name}")
            
            except Exception as e:
                print(f"⚠️ Error cargando módulo {pattern_name}: {e}")
                module_info['available'] = False
    
    def get_available_patterns(self) -> List[str]:
        """Obtener lista de patrones disponibles"""
        return [name for name, info in self.dashboard_modules.items() if info.get('available', False)]
    
    def create_pattern_dashboard(self, pattern_name: str, config: Optional[Dict[str, Any]] = None) -> Optional[BasePatternDashboard]:
        """Crear instancia de dashboard para un patrón específico"""
        
        if pattern_name not in self.dashboard_modules:
            print(f"⚠️ Patrón no disponible: {pattern_name}")
            return None
        
        module_info = self.dashboard_modules[pattern_name]
        
        if not module_info.get('available', False):
            print(f"⚠️ Módulo no disponible: {pattern_name}")
            return None
        
        try:
            create_function = module_info.get('create_function')
            if create_function:
                return create_function(config)
            else:
                print(f"⚠️ Función create_dashboard no encontrada para: {pattern_name}")
                return None
        
        except Exception as e:
            print(f"⚠️ Error creando instancia de {pattern_name}: {e}")
            return None
    
    def get_pattern_info(self) -> Dict[str, Any]:
        """Obtener información completa de patrones y módulos"""
        return {
            'core_patterns': self.core_patterns,
            'dashboard_modules': {name: {
                'available': info.get('available', False),
                'file_path': str(info.get('file_path', '')),
                'module_name': info.get('module_name', '')
            } for name, info in self.dashboard_modules.items()},
            'stats': {
                'total_core_patterns': len(self.core_patterns),
                'total_dashboard_modules': len(self.dashboard_modules),
                'available_dashboards': len([info for info in self.dashboard_modules.values() if info.get('available', False)]),
                'enterprise_patterns': len([info for info in self.core_patterns.values() if info.get('enterprise', False)])
            }
        }


# Función principal para ejecutar el factory
def run_factory():
    """Ejecutar el factory completo"""
    print("🏭 EJECUTANDO PATTERN FACTORY DEL SISTEMA REAL")
    print("=" * 50)
    
    try:
        factory = PatternFactory()
        factory.auto_discover_and_generate()
        
        # Mostrar resumen
        info = factory.get_pattern_info()
        print("\n📊 RESUMEN FINAL:")
        print(f"• Patrones core encontrados: {info['stats']['total_core_patterns']}")
        print(f"• Módulos dashboard: {info['stats']['total_dashboard_modules']}")
        print(f"• Dashboards disponibles: {info['stats']['available_dashboards']}")
        print(f"• Patrones enterprise: {info['stats']['enterprise_patterns']}")
        
        available_patterns = factory.get_available_patterns()
        if available_patterns:
            print(f"\n🎯 PATRONES DISPONIBLES:")
            for pattern in available_patterns:
                enterprise_mark = " [ENTERPRISE]" if factory.core_patterns.get(pattern, {}).get('enterprise') else ""
                print(f"  • {pattern}{enterprise_mark}")
        
        return factory
    
    except Exception as e:
        print(f"⚠️ Error ejecutando factory: {e}")
        return None


if __name__ == "__main__":
    run_factory()
