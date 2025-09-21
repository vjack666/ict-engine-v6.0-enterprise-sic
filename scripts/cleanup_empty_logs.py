#!/usr/bin/env python3
"""
Script para limpiar carpetas vacías de logs y prevenir su recreación.

Este script:
1. Identifica y elimina carpetas de logs completamente vacías
2. Busca código que pueda estar creando carpetas innecesarias
3. Proporciona un reporte de limpieza
"""

import os
import sys
from pathlib import Path
from typing import List, Set
import shutil

def find_empty_log_directories(root_path: Path) -> List[Path]:
    """Encontrar todas las carpetas de logs completamente vacías."""
    empty_dirs = []
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        dir_path = Path(dirpath)
        
        # Verificar si es una carpeta de logs vacía
        if ('logs' in str(dir_path).lower() and 
            len(filenames) == 0 and 
            all(len(os.listdir(dir_path / dirname)) == 0 for dirname in dirnames if (dir_path / dirname).exists())):
            empty_dirs.append(dir_path)
    
    # Filtrar para obtener solo las carpetas realmente vacías
    truly_empty = []
    for empty_dir in empty_dirs:
        try:
            if not any(empty_dir.iterdir()):  # Completamente vacía
                truly_empty.append(empty_dir)
        except Exception:
            pass
    
    return truly_empty

def remove_empty_directories(empty_dirs: List[Path], dry_run: bool = True) -> List[str]:
    """Eliminar carpetas vacías."""
    results = []
    
    for empty_dir in empty_dirs:
        try:
            if dry_run:
                results.append(f"[DRY-RUN] Would remove: {empty_dir}")
            else:
                empty_dir.rmdir()
                results.append(f"[REMOVED] {empty_dir}")
        except OSError as e:
            results.append(f"[ERROR] Could not remove {empty_dir}: {e}")
    
    return results

def find_problematic_log_patterns() -> List[str]:
    """Buscar patrones problemáticos en el código que puedan crear carpetas innecesarias."""
    problematic_patterns = []
    
    # Buscar archivos Python que contengan creación de logs
    root = Path(".")
    python_files = list(root.rglob("*.py"))
    
    suspicious_patterns = [
        "data/logs",
        "logs/daily", "logs/dashboard", "logs/debug", "logs/errors", 
        "logs/ict", "logs/metrics", "logs/mt5", "logs/poi", 
        "logs/structured", "logs/tct", "logs/terminal_capture", "logs/trading"
    ]
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for pattern in suspicious_patterns:
                if pattern in content and "mkdir" in content:
                    problematic_patterns.append(f"File: {py_file}, Pattern: {pattern}")
                    
        except Exception:
            continue
    
    return problematic_patterns

def main():
    """Función principal del script de limpieza."""
    print("🧹 Log Directory Cleanup Script")
    print("=" * 50)
    
    root_path = Path(".")
    
    # 1. Encontrar carpetas vacías
    print("📁 Finding empty log directories...")
    empty_dirs = find_empty_log_directories(root_path)
    
    if empty_dirs:
        print(f"Found {len(empty_dirs)} empty log directories:")
        for empty_dir in empty_dirs[:20]:  # Mostrar solo las primeras 20
            print(f"  - {empty_dir}")
        if len(empty_dirs) > 20:
            print(f"  ... and {len(empty_dirs) - 20} more")
    else:
        print("✅ No empty log directories found")
    
    # 2. Buscar patrones problemáticos
    print("\n🔍 Searching for problematic patterns...")
    problems = find_problematic_log_patterns()
    
    if problems:
        print(f"Found {len(problems)} potential issues:")
        for problem in problems[:10]:  # Mostrar solo los primeros 10
            print(f"  - {problem}")
        if len(problems) > 10:
            print(f"  ... and {len(problems) - 10} more")
    else:
        print("✅ No problematic patterns found")
    
    # 3. Opciones de limpieza
    if empty_dirs:
        print(f"\n🗑️ Cleanup Options:")
        print("1. Dry run (show what would be removed)")
        print("2. Actually remove empty directories")
        print("3. Exit without changes")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            results = remove_empty_directories(empty_dirs, dry_run=True)
            for result in results:
                print(result)
        elif choice == "2":
            results = remove_empty_directories(empty_dirs, dry_run=False)
            for result in results:
                print(result)
            print(f"✅ Cleanup completed. Removed {len([r for r in results if 'REMOVED' in r])} directories")
        else:
            print("👋 Exiting without changes")
    
    print("\n📋 Cleanup Report Complete")

if __name__ == "__main__":
    main()