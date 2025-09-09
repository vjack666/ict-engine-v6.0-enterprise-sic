#!/usr/bin/env python3
"""
🔍 OBTENER DATOS REALES DE MT5 - Para documentación
================================================================

Script para obtener datos reales del MT5DataManager y mostrar
la estructura exacta que devuelve get_connection_status()

Fecha: 9 Septiembre 2025
"""

import sys
from pathlib import Path

# Configurar rutas
project_root = Path(__file__).parent.parent.absolute()
core_path = project_root / "01-CORE"

sys.path.extend([
    str(project_root),
    str(core_path),
    str(core_path / "data_management")
])

def get_real_mt5_data_example():
    """Obtener datos reales del MT5 para documentación"""
    try:
        print("🔍 Obteniendo datos reales del MT5DataManager...")
        
        from data_management.mt5_data_manager import MT5DataManager
        mt5_manager = MT5DataManager()
        
        # Intentar conectar
        if mt5_manager.connect():
            print("✅ Conectado exitosamente a MT5")
            
            # Obtener estado real de la conexión
            connection_status = mt5_manager.get_connection_status()
            
            print("\n📊 DATOS REALES DEL MT5:")
            print("=" * 50)
            
            # Mostrar datos reales formateados
            for key, value in connection_status.items():
                if value is not None:
                    print(f"{key}: {value}")
                else:
                    print(f"{key}: None")
            
            print("\n🎯 EJEMPLO PARA DOCUMENTACIÓN:")
            print("=" * 50)
            print("```python")
            print("connection_status = {")
            for key, value in connection_status.items():
                if key in ['balance', 'equity', 'margin_level', 'account', 'server', 'company', 'connected', 'account_type']:
                    if isinstance(value, str):
                        print(f"    '{key}': '{value}',")
                    elif isinstance(value, (int, float)):
                        print(f"    '{key}': {value},")
                    else:
                        print(f"    '{key}': {value},")
            print("}")
            print("```")
            
            # Desconectar
            mt5_manager.disconnect()
            
        else:
            print("❌ No se pudo conectar a MT5")
            print("💡 Mostrando estructura esperada basada en código:")
            
            # Mostrar estructura basada en el código
            print("\n📊 ESTRUCTURA ESPERADA (basada en código):")
            print("=" * 50)
            print("```python")
            print("connection_status = {")
            print("    'connected': True,")
            print("    'account': 1234567,                    # ✅ REAL - número de cuenta MT5")
            print("    'server': 'FTMO-Demo',                 # ✅ REAL - servidor del broker")
            print("    'company': 'FTMO',                     # ✅ REAL - nombre del broker")
            print("    'account_type': 'DEMO',                # ✅ REAL - tipo de cuenta")
            print("    'balance': 100000.0,                   # ✅ REAL - balance de la cuenta")
            print("    'equity': 100500.0,                    # ✅ REAL - equity actual")
            print("    'margin_level': 1500.0,                # ✅ REAL - nivel de margen")
            print("    'last_connection': '2025-09-09T...',   # ✅ REAL - timestamp de conexión")
            print("    'mt5_available': True,                 # ✅ REAL - MT5 disponible")
            print("    'last_error': None,                    # ✅ REAL - último error si existe")
            print("    'connection_attempts': 1               # ✅ REAL - intentos de conexión")
            print("}")
            print("```")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Usando estructura del código como referencia...")

if __name__ == "__main__":
    get_real_mt5_data_example()
