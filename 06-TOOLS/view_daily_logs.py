#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📋 VISUALIZADOR DE LOGS DIARIOS - ICT ENGINE v6.0 ENTERPRISE
============================================================

Herramienta para visualizar y analizar logs del sistema de trading diario.

✅ FUNCIONES:
- Ver logs del día actual por componente
- Buscar logs de sesiones específicas  
- Estadísticas de logs
- Limpieza de logs antiguos

Uso:
    python view_daily_logs.py                    # Ver todos los logs de hoy
    python view_daily_logs.py DASHBOARD         # Ver logs del dashboard de hoy
    python view_daily_logs.py TRADING 20        # Ver últimas 20 líneas de trading
    python view_daily_logs.py --cleanup 30      # Limpiar logs > 30 días
    python view_daily_logs.py --stats           # Estadísticas de logs

Autor: ICT Engine v6.0 Enterprise Team  
Fecha: 2025-09-09
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# Agregar path para imports desde 06-TOOLS
sys.path.append(str(Path(__file__).parent.parent / "01-CORE"))

try:
    from smart_trading_logger import list_daily_log_files, cleanup_old_logs
except ImportError:
    print("⚠️ No se pudo importar smart_trading_logger. Ejecutando en modo standalone.")
    
    def list_daily_log_files():
        return {'status': 'error', 'message': 'smart_trading_logger no disponible'}
    
    def cleanup_old_logs(days):
        return {'status': 'error', 'message': 'smart_trading_logger no disponible'}

def view_today_logs(component: str = "all", tail_lines: int = 50):
    """📋 Ver logs del día actual por componente"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_base_dir = Path("05-LOGS")
    
    if not log_base_dir.exists():
        print("❌ Directorio de logs no encontrado: 05-LOGS/")
        return
    
    print(f"📋 LOGS DEL DÍA: {today}")
    print("=" * 60)
    
    if component.upper() == "ALL":
        # Mostrar logs de todos los componentes
        components_found = 0
        
        for comp_dir in log_base_dir.iterdir():
            if comp_dir.is_dir():
                log_file = comp_dir / f"{comp_dir.name}_{today}.log"
                if log_file.exists():
                    components_found += 1
                    print(f"\n🔍 {comp_dir.name.upper()}:")
                    print("-" * 40)
                    
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            
                        # Mostrar últimas líneas
                        for line in lines[-tail_lines:]:
                            print(f"  {line.rstrip()}")
                            
                        print(f"\n📊 Total líneas: {len(lines)} | Mostrando últimas: {min(tail_lines, len(lines))}")
                        
                    except Exception as e:
                        print(f"  ❌ Error leyendo archivo: {e}")
        
        if components_found == 0:
            print(f"ℹ️ No se encontraron logs para el día {today}")
            
    else:
        # Mostrar logs de componente específico
        component_dir = log_base_dir / component.lower()
        log_file = component_dir / f"{component.lower()}_{today}.log"
        
        if log_file.exists():
            print(f"🔍 LOGS DE {component.upper()}:")
            print("-" * 40)
            
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line in lines[-tail_lines:]:
                    print(line.rstrip())
                    
                print(f"\n📊 Total líneas: {len(lines)} | Mostrando últimas: {min(tail_lines, len(lines))}")
                
            except Exception as e:
                print(f"❌ Error leyendo archivo: {e}")
        else:
            print(f"ℹ️ No se encontró archivo de log para {component.upper()} en {today}")

def view_session_logs(component: str, session_time: str):
    """📋 Ver logs de sesión específica"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = Path("05-LOGS") / component.lower() / f"{component.lower()}_{today}.log"
    
    if not log_file.exists():
        print(f"❌ No se encontró archivo de log para {component} en {today}")
        return
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar sesión específica
        session_start_marker = f"NUEVA SESIÓN INICIADA - {session_time}"
        
        if session_start_marker in content:
            print(f"📋 SESIÓN {component.upper()} - {session_time}:")
            print("=" * 50)
            
            # Extraer contenido de la sesión
            parts = content.split(session_start_marker)
            if len(parts) > 1:
                session_content = parts[1]
                
                # Buscar el final de la sesión
                end_parts = session_content.split("SESIÓN TERMINADA")
                if len(end_parts) > 1:
                    session_only = session_start_marker + end_parts[0] + "SESIÓN TERMINADA"
                else:
                    session_only = session_start_marker + session_content
                
                print(session_only)
            else:
                print("❌ No se pudo extraer el contenido de la sesión")
        else:
            print(f"❌ No se encontró sesión iniciada a las {session_time}")
            print("ℹ️ Sesiones disponibles:")
            
            # Mostrar sesiones disponibles
            sessions = []
            for line in content.split('\n'):
                if "NUEVA SESIÓN INICIADA" in line:
                    time_part = line.split(" - ")[-1].strip()
                    sessions.append(time_part)
            
            for session in sessions:
                print(f"  - {session}")
                
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")

def show_logs_stats():
    """📊 Mostrar estadísticas de logs"""
    print("📊 ESTADÍSTICAS DE LOGS DIARIOS")
    print("=" * 50)
    
    # Usar función del smart_trading_logger si está disponible
    files_info = list_daily_log_files()
    
    if files_info['status'] == 'success':
        print(f"📁 Total archivos: {files_info['total_files']}")
        print(f"📅 Archivos de hoy: {files_info['today_files']}")
        print()
        
        # Estadísticas por componente
        components = {}
        total_size = 0
        
        for file_info in files_info['files']:
            comp = file_info['component']
            if comp not in components:
                components[comp] = {'count': 0, 'size_mb': 0, 'latest': ''}
            
            components[comp]['count'] += 1
            components[comp]['size_mb'] += file_info['size_mb']
            total_size += file_info['size_mb']
            
            if file_info['is_today']:
                components[comp]['latest'] = file_info['modified']
        
        print("📋 POR COMPONENTE:")
        for comp, stats in components.items():
            print(f"  🎯 {comp}: {stats['count']} archivos, {stats['size_mb']:.2f} MB")
            if stats['latest']:
                print(f"      Última actividad: {stats['latest']}")
        
        print(f"\n💾 Tamaño total: {total_size:.2f} MB")
        
        # Archivos más recientes
        print("\n📅 ARCHIVOS MÁS RECIENTES:")
        for file_info in files_info['files'][:5]:
            status = "📅" if file_info['is_today'] else "📄"
            print(f"  {status} {file_info['name']} ({file_info['size_mb']:.2f} MB)")
            
    else:
        print(f"❌ Error obteniendo estadísticas: {files_info.get('message', 'Unknown error')}")

def cleanup_logs(days: int):
    """🗑️ Limpiar logs antiguos"""
    print(f"🗑️ LIMPIANDO LOGS ANTERIORES A {days} DÍAS")
    print("=" * 50)
    
    result = cleanup_old_logs(days)
    
    if result['status'] == 'success':
        print(f"✅ Limpieza completada:")
        print(f"   📁 Archivos eliminados: {result['cleaned_files']}")
        print(f"   📅 Fecha límite: {result['cutoff_date']}")
        
        if result['files']:
            print("\n🗑️ Archivos eliminados:")
            for filename in result['files']:
                print(f"   - {filename}")
        else:
            print("ℹ️ No había archivos antiguos para eliminar")
            
    else:
        print(f"❌ Error en limpieza: {result.get('message', 'Unknown error')}")

def main():
    """🎯 Función principal del visualizador"""
    parser = argparse.ArgumentParser(
        description="Visualizador de logs diarios ICT Engine v6.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python view_daily_logs.py                    # Ver todos los logs de hoy
  python view_daily_logs.py DASHBOARD         # Ver logs del dashboard
  python view_daily_logs.py TRADING 20        # Ver últimas 20 líneas de trading  
  python view_daily_logs.py --session SYSTEM 09:30:15   # Ver sesión específica
  python view_daily_logs.py --stats           # Estadísticas de logs
  python view_daily_logs.py --cleanup 30      # Limpiar logs > 30 días
        """
    )
    
    parser.add_argument('component', nargs='?', default='all', 
                       help='Componente a visualizar (SYSTEM, DASHBOARD, PATTERNS, TRADING, ALL)')
    parser.add_argument('lines', nargs='?', type=int, default=50,
                       help='Número de líneas a mostrar (default: 50)')
    
    parser.add_argument('--stats', action='store_true',
                       help='Mostrar estadísticas de logs')
    parser.add_argument('--cleanup', type=int, metavar='DAYS',
                       help='Limpiar logs anteriores a N días')
    parser.add_argument('--session', nargs=2, metavar=('COMPONENT', 'TIME'),
                       help='Ver sesión específica (ej: SYSTEM 09:30:15)')
    
    args = parser.parse_args()
    
    # Procesar argumentos
    if args.stats:
        show_logs_stats()
    elif args.cleanup:
        cleanup_logs(args.cleanup)
    elif args.session:
        component, session_time = args.session
        view_session_logs(component, session_time)
    else:
        view_today_logs(args.component, args.lines)

if __name__ == "__main__":
    main()
