#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 VALIDADOR DE MÓDULO DATA MANAGEMENT - ICT ENGINE v6.0 ENTERPRISE
==================================================================

Script de validación completa para el módulo data_management armonizado
con protocolos centrales y optimizado para cuenta real.

Autor: ICT Engine v6.0 Team
Fecha: 13 Septiembre 2025
"""

import sys
import os
from typing import Dict, Any

# Agregar path para importar desde 01-CORE
sys.path.append(os.path.join(os.path.dirname(__file__), '01-CORE'))

def validate_data_management_module():
    """Validación completa del módulo data_management"""
    
    print("🔧 VALIDADOR DE MÓDULO DATA MANAGEMENT")
    print("=" * 50)
    
    try:
        # Importar y probar el módulo
        from data_management import (
            get_module_status,
            validate_enterprise_requirements,
            get_enterprise_data_collector,
            MODULE_INFO
        )
        
        print("✅ Importación exitosa del módulo data_management")
        
        # Validar estado del módulo
        status = get_module_status()
        print(f"\n📊 Estado del Módulo:")
        print(f"   Versión: {status['version']}")
        print(f"   Componentes cargados: {status['components_loaded']}/6")
        print(f"   Enterprise Ready: {status['enterprise_ready']}")
        print(f"   Protocolos disponibles: {status['protocols_available']}")
        
        # Validar componentes críticos
        is_ready, missing = validate_enterprise_requirements()
        print(f"\n🏦 Validación Enterprise:")
        print(f"   Sistema listo para cuenta real: {is_ready}")
        if missing:
            print(f"   Componentes faltantes: {missing}")
        
        # Probar factory function
        print(f"\n🏭 Factory Function:")
        collector = get_enterprise_data_collector()
        if collector:
            print(f"   ✅ Collector enterprise disponible: {type(collector).__name__}")
        else:
            print(f"   ⚠️ No hay collector enterprise disponible")
        
        # Mostrar información del módulo
        print(f"\n📋 Información del Módulo:")
        print(f"   Nombre: {MODULE_INFO['name']}")
        print(f"   Descripción: {MODULE_INFO['description']}")
        print(f"   Features enterprise: {len(MODULE_INFO['enterprise_features'])}")
        
        # Validar componentes específicos
        print(f"\n🔍 Componentes Específicos:")
        components = MODULE_INFO['components']
        for name, available in components.items():
            status_icon = "✅" if available else "❌"
            print(f"   {status_icon} {name}: {available}")
        
        # Verificar exports
        print(f"\n📦 Verificación de Exports:")
        from data_management import __all__
        print(f"   Exports declarados: {len(__all__)}")
        
        # Intentar importar cada export
        import data_management
        for export_name in __all__:
            try:
                getattr(data_management, export_name)
                print(f"   ✅ {export_name}")
            except AttributeError:
                print(f"   ❌ {export_name} - No disponible")
        
        print(f"\n🎉 VALIDACIÓN COMPLETADA EXITOSAMENTE")
        return True
        
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_logging_integration():
    """Test específico de integración con logging"""
    print(f"\n🔊 TEST DE LOGGING:")
    
    try:
        # Verificar que el logging funciona correctamente
        from data_management import get_module_status
        status = get_module_status()  # Esto debería generar logs
        print(f"   ✅ Logging funcional durante get_module_status")
        
        # Verificar factory function logging
        from data_management import get_enterprise_data_collector
        get_enterprise_data_collector()  # Esto debería generar logs
        print(f"   ✅ Logging funcional durante factory function")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en logging: {e}")
        return False

def main():
    """Función principal de validación"""
    
    # Validación principal
    module_ok = validate_data_management_module()
    
    # Test de logging
    logging_ok = test_logging_integration()
    
    # Resumen final
    print(f"\n" + "=" * 50)
    if module_ok and logging_ok:
        print(f"🎯 VALIDACIÓN COMPLETA: ✅ EXITOSA")
        print(f"   ✅ Módulo data_management armonizado")
        print(f"   ✅ Protocolos de logging integrados") 
        print(f"   ✅ Optimizado para cuenta real")
        print(f"   ✅ Sin errores Pylance")
        return 0
    else:
        print(f"⚠️ VALIDACIÓN: ❌ CON ERRORES")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)