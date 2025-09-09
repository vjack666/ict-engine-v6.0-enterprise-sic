#!/usr/bin/env python3
"""
🧹 ICT Engine v6.0 Enterprise - System Cleanup
===============================================
Limpia logs y datos para simular instalación fresca
Preserva archivos de configuración y código fuente
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import glob

class SystemCleaner:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.cleaned_files = []
        self.preserved_files = []
        self.errors = []
        
    def log_action(self, action, path, status="✅"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status} {action}: {path}")
    
    def clean_logs_directory(self):
        """Limpiar directorio 05-LOGS/"""
        logs_dir = self.base_path / "05-LOGS"
        
        if not logs_dir.exists():
            self.log_action("SKIP", "05-LOGS/ no existe", "ℹ️")
            return
            
        print("\n🗂️  LIMPIANDO DIRECTORIO DE LOGS...")
        print("-" * 50)
        
        for root, dirs, files in os.walk(logs_dir):
            for file in files:
                file_path = Path(root) / file
                
                # Preservar README.md
                if file.lower() == "readme.md":
                    self.log_action("PRESERVE", file_path, "📋")
                    self.preserved_files.append(str(file_path))
                    continue
                
                # Eliminar archivos de log
                if file.endswith(('.log', '.txt', '.out', '.err')):
                    try:
                        file_path.unlink()
                        self.log_action("DELETE", file_path)
                        self.cleaned_files.append(str(file_path))
                    except Exception as e:
                        self.log_action("ERROR", f"{file_path}: {e}", "❌")
                        self.errors.append(str(file_path))
    
    def clean_data_directory(self):
        """Limpiar archivos generados en 04-DATA/"""
        data_dir = self.base_path / "04-DATA"
        
        if not data_dir.exists():
            self.log_action("SKIP", "04-DATA/ no existe", "ℹ️")
            return
            
        print("\n💾 LIMPIANDO DATOS GENERADOS...")
        print("-" * 50)
        
        # Subdirectorios a limpiar (pero no eliminar)
        subdirs_to_clean = [
            "cache", "logs", "exports", "reports", 
            "memory_persistence", "status"
        ]
        
        for subdir in subdirs_to_clean:
            subdir_path = data_dir / subdir
            if subdir_path.exists():
                for root, dirs, files in os.walk(subdir_path):
                    for file in files:
                        file_path = Path(root) / file
                        
                        # Preservar README.md y archivos .gitkeep
                        if file.lower() in ["readme.md", ".gitkeep", ".gitignore"]:
                            self.log_action("PRESERVE", file_path, "📋")
                            self.preserved_files.append(str(file_path))
                            continue
                        
                        try:
                            file_path.unlink()
                            self.log_action("DELETE", file_path)
                            self.cleaned_files.append(str(file_path))
                        except Exception as e:
                            self.log_action("ERROR", f"{file_path}: {e}", "❌")
                            self.errors.append(str(file_path))
    
    def clean_cache_files(self):
        """Limpiar archivos cache del sistema"""
        print("\n🗄️  LIMPIANDO ARCHIVOS CACHE...")
        print("-" * 50)
        
        # Patrones de archivos cache
        cache_patterns = [
            "**/__pycache__/**/*.pyc",
            "**/__pycache__/**/*.pyo", 
            "**/*.pyc",
            "**/*.pyo",
            "**/cache/**/*.json",
            "**/cache/**/*.pkl",
            "**/cache/**/*.cache"
        ]
        
        for pattern in cache_patterns:
            for file_path in self.base_path.glob(pattern):
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        self.log_action("DELETE", file_path)
                        self.cleaned_files.append(str(file_path))
                    except Exception as e:
                        self.log_action("ERROR", f"{file_path}: {e}", "❌")
                        self.errors.append(str(file_path))
    
    def clean_temp_files(self):
        """Limpiar archivos temporales"""
        print("\n🗑️  LIMPIANDO ARCHIVOS TEMPORALES...")
        print("-" * 50)
        
        # Patrones de archivos temporales
        temp_patterns = [
            "**/*.tmp",
            "**/*.temp",
            "**/temp/**/*",
            "**/.DS_Store",
            "**/Thumbs.db",
            "**/*.bak",
            "**/*~"
        ]
        
        for pattern in temp_patterns:
            for file_path in self.base_path.glob(pattern):
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        self.log_action("DELETE", file_path)
                        self.cleaned_files.append(str(file_path))
                    except Exception as e:
                        self.log_action("ERROR", f"{file_path}: {e}", "❌")
                        self.errors.append(str(file_path))
    
    def show_summary(self):
        """Mostrar resumen de limpieza"""
        print("\n" + "=" * 80)
        print("📊 RESUMEN DE LIMPIEZA DEL SISTEMA")
        print("=" * 80)
        
        print(f"🗑️  Archivos eliminados: {len(self.cleaned_files)}")
        print(f"📋 Archivos preservados: {len(self.preserved_files)}")
        print(f"❌ Errores encontrados: {len(self.errors)}")
        
        if self.cleaned_files:
            print(f"\n✅ ARCHIVOS ELIMINADOS ({len(self.cleaned_files)}):")
            for i, file_path in enumerate(self.cleaned_files[:10], 1):  # Mostrar solo primeros 10
                print(f"   {i:2d}. {Path(file_path).name}")
            if len(self.cleaned_files) > 10:
                print(f"   ... y {len(self.cleaned_files) - 10} archivos más")
        
        if self.errors:
            print(f"\n❌ ERRORES ENCONTRADOS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i:2d}. {error}")
        
        print(f"\n🎯 ESTADO FINAL: {'✅ SISTEMA LIMPIO' if not self.errors else '⚠️ LIMPIEZA CON ERRORES'}")
        print("=" * 80)
    
    def run_cleanup(self):
        """Ejecutar limpieza completa del sistema"""
        start_time = datetime.now()
        
        print("🧹 ICT ENGINE v6.0 ENTERPRISE - LIMPIEZA DEL SISTEMA")
        print("=" * 80)
        print(f"📅 Fecha: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 Directorio: {self.base_path}")
        print("=" * 80)
        
        # Ejecutar limpieza por categorías
        self.clean_logs_directory()
        self.clean_data_directory()
        self.clean_cache_files()
        self.clean_temp_files()
        
        # Mostrar resumen
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.show_summary()
        print(f"⏱️  Tiempo de limpieza: {duration:.2f} segundos")
        print("\n🚀 SISTEMA LISTO PARA REPORTE COMPLETO")
        
        return len(self.errors) == 0

def main():
    """Función principal"""
    cleaner = SystemCleaner()
    success = cleaner.run_cleanup()
    
    if success:
        print("\n✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
        print("💡 Ahora puedes ejecutar: python main.py > system_complete_report.log")
    else:
        print("\n⚠️ LIMPIEZA COMPLETADA CON ERRORES")
        print("💡 Revisa los errores antes de continuar")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
