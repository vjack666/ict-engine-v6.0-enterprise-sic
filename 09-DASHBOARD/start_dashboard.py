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
        
        # ===== CONFIGURAR MODO SILENCIOSO PARA LOGGING =====
        try:
            # Configurar logging silencioso para el dashboard
            dashboard_dir = Path(__file__).parent.absolute()
            project_root = dashboard_dir.parent
            core_path = project_root / "01-CORE"
            sys.path.insert(0, str(core_path))
            
            from smart_trading_logger import get_centralized_logger
            
            # Activar modo silencioso para todos los loggers centralizados
            for component in ['SYSTEM', 'DASHBOARD', 'PATTERNS', 'TRADING', 'GENERAL']:
                try:
                    logger = get_centralized_logger(component)
                    logger.set_silent_mode(True)
                except:
                    pass  # Silenciar errores de configuración de logger
            
            print("🔇 Modo silencioso activado - logs solo en archivos")
        except Exception as e:
            print(f"⚠️ Warning: No se pudo configurar modo silencioso: {e}")
        
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
