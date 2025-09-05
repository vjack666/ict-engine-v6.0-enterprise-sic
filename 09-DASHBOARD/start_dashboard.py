#!/usr/bin/env python3
"""
🚀 START DASHBOARD - Iniciador del Dashboard ICT
===============================================

Script simple para iniciar el dashboard ICT Engine.
Reemplaza los tests con la aplicación real.
"""

import sys
import os
from pathlib import Path

# Configurar rutas
dashboard_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(dashboard_dir))

def main():
    """Iniciar dashboard"""
    try:
        print("🎯 Iniciando ICT Engine Dashboard...")
        print("=" * 50)
        
        # Importar aplicación principal
        from dashboard import ICTDashboardApp
        
        # Crear y ejecutar aplicación
        app = ICTDashboardApp()
        
        print("🚀 Cargando dashboard...")
        print("💡 Presiona Ctrl+C para salir")
        print()
        
        # Ejecutar sin asyncio.run para evitar conflictos
        app.run_sync()
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard cerrado por el usuario")
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Verifique que todos los componentes estén instalados")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
