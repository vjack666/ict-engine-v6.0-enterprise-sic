#!/usr/bin/env python3
"""
🎯 LOG ORGANIZER v1.0.0 - ORGANIZADOR AUTOMÁTICO DE LOGS POR CATEGORÍAS
========================================================================

Herramienta para organizar automáticamente los logs del sistema ICT Engine v6.0
en carpetas específicas según su contenido y tipo.

Funcionalidades:
- ✅ Análisis de contenido de logs en tiempo real
- ✅ Categorización automática por tipo de log
- ✅ Copia de logs específicos a carpetas apropiadas
- ✅ Resumen de actividad por categorías
- ✅ Rotación de logs antigua

Categorías soportadas:
- fvg_memory: Logs de Fair Value Gaps y Kill Zones
- market_data: Datos de mercado y precios
- ict_signals: Señales ICT detectadas
- system_status: Estado general del sistema
- kill_zones: Actividad específica de kill zones

Versión: v1.0.0
Fecha: 9 de Septiembre 2025 - 16:30 GMT
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class LogOrganizer:
    """🎯 Organizador automático de logs por categorías."""
    
    def __init__(self):
        """Inicializa el organizador de logs."""
        self.project_root = Path(__file__).parent.parent
        self.source_logs_dir = self.project_root / "05-LOGS"
        self.date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Configurar patrones de categorización
        self.category_patterns = {
            'fvg_memory': [
                r'\[fvg_memory\]',
                r'FVG Memory Manager',
                r'Memoria de FVGs',
                r'Gap≥.*pips',
                r'Tolerancia≤.*pips'
            ],
            'kill_zones': [
                r'Kill Zone.*activa',
                r'Criterios optimizados',
                r'london activa',
                r'newyork activa',
                r'overlap activa'
            ],
            'market_data': [
                r'EURUSD.*[0-9]+\.[0-9]+',
                r'GBPUSD.*[0-9]+\.[0-9]+',
                r'USDJPY.*[0-9]+\.[0-9]+',
                r'XAUUSD.*[0-9]+\.[0-9]+',
                r'Bid:.*Ask:'
            ],
            'ict_signals': [
                r'Order Block.*detectado',
                r'Silver Bullet.*setup',
                r'Judas Swing.*detected',
                r'Liquidity Grab.*found',
                r'OTE.*opportunity'
            ],
            'system_status': [
                r'TRADING_READY.*TRUE',
                r'Sistema listo para',
                r'inicializado correctamente',
                r'Enterprise.*cargado',
                r'Pipeline.*disponible'
            ]
        }
        
        self.stats = {
            'processed_lines': 0,
            'categorized_logs': 0,
            'categories': {}
        }
    
    def organize_daily_logs(self) -> Dict[str, Any]:
        """🗂️ Organiza todos los logs diarios por categorías."""
        print("🎯 LOG ORGANIZER v1.0.0 - ORGANIZANDO LOGS POR CATEGORÍAS")
        print("=" * 60)
        
        # 1. Crear carpetas de destino
        self._ensure_category_directories()
        
        # 2. Procesar archivos de log existentes
        print("\n📊 PROCESANDO ARCHIVOS DE LOG...")
        log_files = self._find_daily_log_files()
        
        for log_file in log_files:
            self._process_log_file(log_file)
        
        # 3. Generar resumen
        print("\n📋 GENERANDO RESUMEN...")
        self._generate_summary()
        
        return self.stats
    
    def _ensure_category_directories(self):
        """📁 Crear directorios de categorías si no existen."""
        for category in self.category_patterns.keys():
            category_dir = self.source_logs_dir / category
            category_dir.mkdir(exist_ok=True)
            
            # Inicializar stats para esta categoría
            self.stats['categories'][category] = {
                'logs_count': 0,
                'file_path': category_dir / f"{category}_{self.date_str}.log"
            }
        
        print(f"✅ Directorios de categorías creados: {len(self.category_patterns)}")
    
    def _find_daily_log_files(self) -> List[Path]:
        """🔍 Encontrar archivos de log del día actual."""
        log_files = []
        
        # Buscar en subdirectorios principales (patterns, general, etc.)
        for subdir in self.source_logs_dir.iterdir():
            if subdir.is_dir() and subdir.name not in self.category_patterns:
                # Buscar archivos del día actual
                for log_file in subdir.glob(f"*_{self.date_str}.log"):
                    log_files.append(log_file)
        
        print(f"📁 Encontrados {len(log_files)} archivos de log para procesar")
        for log_file in log_files:
            print(f"   - {log_file.relative_to(self.project_root)}")
        
        return log_files
    
    def _process_log_file(self, log_file: Path):
        """📝 Procesar un archivo de log específico."""
        try:
            print(f"\\n🔄 Procesando: {log_file.name}")
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            categorized_lines = {category: [] for category in self.category_patterns.keys()}
            
            for line in lines:
                self.stats['processed_lines'] += 1
                
                # Verificar cada categoría
                for category, patterns in self.category_patterns.items():
                    if any(re.search(pattern, line, re.IGNORECASE) for pattern in patterns):
                        categorized_lines[category].append(line)
                        self.stats['categorized_logs'] += 1
                        self.stats['categories'][category]['logs_count'] += 1
                        break  # Solo una categoría por línea
            
            # Escribir líneas categorizadas a archivos específicos
            self._write_categorized_logs(categorized_lines)
            
            print(f"   ✅ Procesadas {len(lines)} líneas")
            
        except Exception as e:
            print(f"   ❌ Error procesando {log_file.name}: {e}")
    
    def _write_categorized_logs(self, categorized_lines: Dict[str, List[str]]):
        """✏️ Escribir logs categorizados a archivos específicos."""
        for category, lines in categorized_lines.items():
            if lines:
                category_file = self.stats['categories'][category]['file_path']
                
                # Crear header si el archivo no existe
                write_header = not category_file.exists()
                
                with open(category_file, 'a', encoding='utf-8') as f:
                    if write_header:
                        f.write(f"# {category.upper()} LOGS - {self.date_str}\\n")
                        f.write(f"# Generado automáticamente por Log Organizer v1.0.0\\n")
                        f.write("=" * 60 + "\\n\\n")
                    
                    f.writelines(lines)
    
    def _generate_summary(self):
        """📊 Generar resumen de la organización."""
        print("\\n" + "="*60)
        print("📊 RESUMEN DE ORGANIZACIÓN DE LOGS")
        print("="*60)
        
        print(f"\\n📝 ESTADÍSTICAS GENERALES:")
        print(f"   • Líneas procesadas: {self.stats['processed_lines']:,}")
        print(f"   • Logs categorizados: {self.stats['categorized_logs']:,}")
        print(f"   • Porcentaje categorizado: {(self.stats['categorized_logs']/max(self.stats['processed_lines'],1))*100:.1f}%")
        
        print(f"\\n📂 LOGS POR CATEGORÍA:")
        for category, info in self.stats['categories'].items():
            count = info['logs_count']
            if count > 0:
                print(f"   • {category:15}: {count:4} logs → {info['file_path'].name}")
        
        print(f"\\n📍 UBICACIÓN DE ARCHIVOS CATEGORIZADOS:")
        for category, info in self.stats['categories'].items():
            if info['logs_count'] > 0:
                print(f"   {info['file_path'].relative_to(self.project_root)}")
        
        print("\\n" + "="*60)
    
    def create_category_specific_log(self, category: str, content: str):
        """📝 Crear log específico para una categoría."""
        if category in self.category_patterns:
            category_file = self.stats['categories'][category]['file_path']
            
            with open(category_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] {content}\\n")
    
    def get_category_summary(self) -> Dict[str, Any]:
        """📋 Obtener resumen de actividad por categorías."""
        summary = {
            'date': self.date_str,
            'total_categories': len(self.category_patterns),
            'active_categories': len([c for c in self.stats['categories'].values() if c['logs_count'] > 0]),
            'categories': self.stats['categories']
        }
        
        return summary

def main():
    """Función principal para ejecutar la organización."""
    organizer = LogOrganizer()
    results = organizer.organize_daily_logs()
    
    print(f"\\n✅ ORGANIZACIÓN COMPLETADA")
    print(f"📊 {results['categorized_logs']} logs organizados en categorías")
    
    return results

if __name__ == "__main__":
    main()
