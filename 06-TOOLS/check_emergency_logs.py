#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VERIFICADOR DE LOGS DEL SISTEMA DE EMERGENCIAS
===============================================

Script para verificar dónde se guardan los logs del sistema de emergencias.

Autor: ICT Engine v6.0 Team
Fecha: 2025-09-09
"""

import sys
import os
from pathlib import Path

# Agregar rutas para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "01-CORE"))

def find_emergency_logs():
    """🔍 Buscar archivos de log del sistema de emergencias"""
    print("🔍 BUSCANDO LOGS DEL SISTEMA DE EMERGENCIAS")
    print("=" * 55)
    
    # Directorios posibles donde buscar logs
    search_dirs = [
        Path("04-DATA/logs"),
        Path("05-LOGS"),
        Path("09-DASHBOARD/data/logs"),
        Path("01-CORE/data/logs")
    ]
    
    today = "2025-09-09"
    found_files = []
    
    for search_dir in search_dirs:
        if search_dir.exists():
            print(f"\n📁 Buscando en: {search_dir}")
            
            # Buscar recursivamente archivos de log de hoy
            for log_file in search_dir.rglob("*.log"):
                if today in log_file.name:
                    print(f"   📄 {log_file}")
                    found_files.append(log_file)
                    
                    # Verificar si contiene logs de emergencias
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'EMERGENCY' in content or 'emergency' in content.lower():
                                print(f"      🚨 ¡Contiene logs de emergencias!")
                                
                                # Mostrar las últimas 5 líneas con emergencias
                                lines = content.split('\n')
                                emergency_lines = [line for line in lines if 'EMERGENCY' in line or 'emergency' in line.lower()]
                                print(f"      📊 {len(emergency_lines)} líneas de emergencia encontradas")
                                
                                if emergency_lines:
                                    print("      📋 Últimas 3 líneas de emergencia:")
                                    for line in emergency_lines[-3:]:
                                        print(f"         {line[:100]}...")
                    except Exception as e:
                        print(f"      ⚠️ Error leyendo archivo: {e}")
        else:
            print(f"\n❌ Directorio no existe: {search_dir}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   Total archivos de log de hoy: {len(found_files)}")
    
    # También buscar archivo específico de emergencias
    emergency_file = Path("05-LOGS/emergency/emergency_events.log")
    if emergency_file.exists():
        print(f"\n🚨 ARCHIVO ESPECÍFICO DE EMERGENCIAS ENCONTRADO:")
        print(f"   📄 {emergency_file}")
        try:
            with open(emergency_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"   📊 {len(lines)} eventos de emergencia registrados")
                if lines:
                    print("   📋 Últimos 3 eventos:")
                    for line in lines[-3:]:
                        print(f"      {line.strip()}")
        except Exception as e:
            print(f"   ⚠️ Error leyendo archivo de emergencias: {e}")
    else:
        print(f"\n❌ No se encontró archivo específico de emergencias en: {emergency_file}")

def test_direct_logging():
    """🧪 Probar logging directo"""
    print("\n🧪 PROBANDO LOGGING DIRECTO")
    print("=" * 35)
    
    try:
        from smart_trading_logger import SmartTradingLogger
        
        # Crear logger de prueba
        logger = SmartTradingLogger("TEST_EMERGENCY")
        logger.critical("🚨 PRUEBA: Mensaje crítico de emergencia")
        logger.error("⚠️ PRUEBA: Mensaje de error de emergencia")
        logger.warning("⚠️ PRUEBA: Mensaje de advertencia de emergencia")
        logger.info("ℹ️ PRUEBA: Mensaje informativo de emergencia")
        
        print("✅ Mensajes de prueba enviados al sistema central")
        
        # Verificar dónde se guardaron
        from smart_trading_logger import list_daily_log_files
        files_info = list_daily_log_files()
        
        if files_info.get('status') == 'success':
            print(f"\n📊 Sistema central reporta {files_info.get('total_files', 0)} archivos")
            for file_info in files_info.get('files', []):
                if file_info.get('component') == 'TEST_EMERGENCY':
                    print(f"   🎯 Archivo TEST_EMERGENCY: {file_info.get('name')}")
                    print(f"      📏 Tamaño: {file_info.get('size_mb', 0):.3f} MB")
        
    except ImportError as e:
        print(f"❌ Error importando SmartTradingLogger: {e}")
    except Exception as e:
        print(f"❌ Error en prueba directa: {e}")

if __name__ == "__main__":
    find_emergency_logs()
    test_direct_logging()
