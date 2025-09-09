#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧹 LIMPIADOR AUTOMÁTICO ICT_SIGNALS
==================================

Utilidad para limpiar automáticamente archivos de patrones ICT después de 30 días.
Se ejecuta automáticamente o manualmente para mantener el sistema limpio.

Autor: ICT Engine v6.0 Team
Fecha: 2025-09-09
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Agregar ruta para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "01-CORE"))

try:
    from smart_trading_logger import SmartTradingLogger, cleanup_old_logs
except ImportError:
    print("⚠️ No se pudo importar smart_trading_logger. Ejecutando limpieza manual.")
    cleanup_old_logs = None
    SmartTradingLogger = None

class ICTSignalsCleanup:
    """🧹 Limpiador automático de archivos ICT_SIGNALS"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.signals_dir = self.project_root / "05-LOGS" / "ict_signals"
        self.retention_days = 30
        
        # Inicializar logger para el proceso de limpieza
        self.logger = None
        if SmartTradingLogger is not None:
            try:
                self.logger = SmartTradingLogger("SYSTEM")
                self.logger.info("🧹 ICT Signals Cleanup iniciado")
            except Exception as e:
                print(f"⚠️ Error inicializando logger: {e}")
    
    def cleanup_old_signals(self, dry_run: bool = False) -> Dict[str, Any]:
        """🧹 Limpiar archivos de señales antiguos (>30 días)"""
        print("🧹 LIMPIEZA AUTOMÁTICA ICT_SIGNALS")
        print("=" * 50)
        
        cleanup_stats = {
            'total_files_checked': 0,
            'files_to_delete': 0,
            'files_deleted': 0,
            'space_freed_mb': 0.0,
            'errors': [],
            'retention_days': self.retention_days
        }
        
        if not self.signals_dir.exists():
            print(f"📁 Directorio ICT_SIGNALS no existe: {self.signals_dir}")
            return cleanup_stats
        
        # Calcular fecha límite (30 días atrás)
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        print(f"📅 Eliminando archivos anteriores a: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Buscar archivos antiguos
        old_files = []
        for log_file in self.signals_dir.glob("*.log"):
            try:
                file_stat = log_file.stat()
                file_modified = datetime.fromtimestamp(file_stat.st_mtime)
                file_size_mb = file_stat.st_size / (1024 * 1024)
                
                cleanup_stats['total_files_checked'] += 1
                
                if file_modified < cutoff_date:
                    old_files.append({
                        'path': log_file,
                        'modified': file_modified,
                        'size_mb': file_size_mb
                    })
                    cleanup_stats['files_to_delete'] += 1
                    cleanup_stats['space_freed_mb'] += file_size_mb
                    
            except Exception as e:
                error_msg = f"Error procesando {log_file}: {e}"
                cleanup_stats['errors'].append(error_msg)
                print(f"   ⚠️ {error_msg}")
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   📁 Archivos revisados: {cleanup_stats['total_files_checked']}")
        print(f"   🗑️ Archivos a eliminar: {cleanup_stats['files_to_delete']}")
        print(f"   💾 Espacio a liberar: {cleanup_stats['space_freed_mb']:.2f} MB")
        
        if old_files:
            print(f"\n📋 ARCHIVOS ANTIGUOS ENCONTRADOS:")
            for file_info in old_files:
                age_days = (datetime.now() - file_info['modified']).days
                print(f"   🗑️ {file_info['path'].name} - {age_days} días - {file_info['size_mb']:.2f} MB")
            
            if not dry_run:
                print(f"\n🗑️ ELIMINANDO ARCHIVOS...")
                for file_info in old_files:
                    try:
                        file_info['path'].unlink()
                        cleanup_stats['files_deleted'] += 1
                        print(f"   ✅ Eliminado: {file_info['path'].name}")
                        
                        if self.logger:
                            self.logger.info(f"🗑️ Archivo ICT_SIGNALS eliminado: {file_info['path'].name} (edad: {(datetime.now() - file_info['modified']).days} días)")
                            
                    except Exception as e:
                        error_msg = f"Error eliminando {file_info['path']}: {e}"
                        cleanup_stats['errors'].append(error_msg)
                        print(f"   ❌ {error_msg}")
            else:
                print(f"\n🔍 MODO DRY-RUN: No se eliminaron archivos")
        else:
            print(f"\n✅ No hay archivos antiguos que eliminar")
        
        return cleanup_stats
    
    def cleanup_using_central_system(self) -> Dict[str, Any]:
        """🧹 Usar sistema central de limpieza si está disponible"""
        print("\n🔧 INTENTANDO USAR SISTEMA CENTRAL DE LIMPIEZA")
        print("=" * 55)
        
        if cleanup_old_logs is None:
            print("❌ Sistema central de limpieza no disponible")
            return self.cleanup_old_signals()
        
        try:
            # Usar sistema central para limpiar ICT_SIGNALS específicamente
            result = cleanup_old_logs(days_to_keep=self.retention_days)
            
            if result.get('status') == 'success':
                print("✅ Limpieza central ejecutada exitosamente")
                print(f"📊 Archivos eliminados: {result.get('files_deleted', 0)}")
                print(f"💾 Espacio liberado: {result.get('space_freed_mb', 0):.2f} MB")
                
                if self.logger:
                    self.logger.info(f"🧹 Limpieza central ICT_SIGNALS: {result.get('files_deleted', 0)} archivos eliminados")
                
                return {
                    'central_cleanup': True,
                    'files_deleted': result.get('files_deleted', 0),
                    'space_freed_mb': result.get('space_freed_mb', 0),
                    'retention_days': self.retention_days
                }
            else:
                print(f"⚠️ Error en limpieza central: {result.get('message', 'Unknown error')}")
                return self.cleanup_old_signals()
                
        except Exception as e:
            print(f"❌ Error usando sistema central: {e}")
            return self.cleanup_old_signals()
    
    def get_signals_statistics(self) -> Dict[str, Any]:
        """📊 Obtener estadísticas de archivos ICT_SIGNALS"""
        stats = {
            'total_files': 0,
            'total_size_mb': 0.0,
            'oldest_file': None,
            'newest_file': None,
            'files_by_date': {},
            'directory_exists': self.signals_dir.exists()
        }
        
        if not self.signals_dir.exists():
            return stats
        
        file_dates = []
        for log_file in self.signals_dir.glob("*.log"):
            try:
                file_stat = log_file.stat()
                file_modified = datetime.fromtimestamp(file_stat.st_mtime)
                file_size_mb = file_stat.st_size / (1024 * 1024)
                
                stats['total_files'] += 1
                stats['total_size_mb'] += file_size_mb
                file_dates.append(file_modified)
                
                # Agrupar por fecha
                date_str = file_modified.strftime('%Y-%m-%d')
                if date_str not in stats['files_by_date']:
                    stats['files_by_date'][date_str] = {'count': 0, 'size_mb': 0.0}
                
                stats['files_by_date'][date_str]['count'] += 1
                stats['files_by_date'][date_str]['size_mb'] += file_size_mb
                
            except Exception as e:
                print(f"⚠️ Error procesando estadísticas de {log_file}: {e}")
        
        if file_dates:
            stats['oldest_file'] = min(file_dates)
            stats['newest_file'] = max(file_dates)
        
        return stats

def main():
    """🚀 Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='🧹 Limpiador ICT_SIGNALS')
    parser.add_argument('--dry-run', action='store_true', help='Mostrar qué se eliminaría sin hacerlo')
    parser.add_argument('--stats', action='store_true', help='Mostrar solo estadísticas')
    parser.add_argument('--use-central', action='store_true', help='Usar sistema central de limpieza')
    
    args = parser.parse_args()
    
    cleaner = ICTSignalsCleanup()
    
    if args.stats:
        print("📊 ESTADÍSTICAS ICT_SIGNALS")
        print("=" * 35)
        stats = cleaner.get_signals_statistics()
        
        if stats['directory_exists']:
            print(f"📁 Total archivos: {stats['total_files']}")
            print(f"💾 Tamaño total: {stats['total_size_mb']:.2f} MB")
            
            if stats['oldest_file']:
                age_days = (datetime.now() - stats['oldest_file']).days
                print(f"📅 Archivo más antiguo: {stats['oldest_file'].strftime('%Y-%m-%d')} ({age_days} días)")
            
            if stats['newest_file']:
                print(f"📅 Archivo más reciente: {stats['newest_file'].strftime('%Y-%m-%d')}")
            
            print(f"\n📋 Archivos por fecha:")
            for date_str, date_stats in sorted(stats['files_by_date'].items()):
                print(f"   {date_str}: {date_stats['count']} archivos, {date_stats['size_mb']:.2f} MB")
        else:
            print("❌ Directorio ICT_SIGNALS no existe")
    
    elif args.use_central:
        result = cleaner.cleanup_using_central_system()
        print(f"\n✅ Limpieza completada: {result.get('files_deleted', 0)} archivos eliminados")
    
    else:
        result = cleaner.cleanup_old_signals(dry_run=args.dry_run)
        if not args.dry_run:
            print(f"\n✅ Limpieza completada: {result['files_deleted']} archivos eliminados")

if __name__ == "__main__":
    main()
