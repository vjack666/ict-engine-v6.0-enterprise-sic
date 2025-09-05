#!/usr/bin/env python3
"""
🔗 INTEGRACIÓN FVG MEMORY MANAGER v6.1.0 - PATRÓN DETECTOR
============================================================

Integración inteligente del sistema de memoria persistente de FVGs
con el pattern_detector existente del sistema ICT.

Este archivo modifica dinámicamente el pattern_detector para:
- ✅ Guardar automáticamente todos los FVGs detectados
- ✅ Actualizar estados en tiempo real
- ✅ Proporcionar estadísticas avanzadas
- ✅ Mantener compatibilidad total con código existente

Versión: v6.1.0-enterprise-integration
Fecha: 4 de Septiembre 2025 - 15:20 GMT
"""

import sys
import os
from pathlib import Path
import importlib.util

# === AGREGAR PATHS AL SISTEMA ===
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "01-CORE" / "core"))
sys.path.insert(0, str(project_root / "01-CORE" / "core" / "analysis"))

# === IMPORTS DEL SISTEMA ===
try:
    from analysis.fvg_memory_manager import FVGMemoryManager
    from smart_trading_logger import SmartTradingLogger
except ImportError as e:
    print(f"⚠️ Error importando dependencias: {e}")
    print("Verificar que los archivos estén en las rutas correctas")

class FVGIntegrationPatch:
    """
    🔗 Parche de integración para el pattern detector.
    
    Modifica dinámicamente el comportamiento del pattern_detector
    para agregar funcionalidad de memoria persistente sin romper
    el código existente.
    """
    
    def __init__(self):
        self.logger = SmartTradingLogger()
        self.fvg_memory = FVGMemoryManager()
        
        self.logger.info("🔗 FVG Integration Patch inicializado", 
                         component="fvg_integration")
    
    def patch_pattern_detector(self, pattern_detector_instance):
        """
        Aplica el parche al pattern detector para agregar funcionalidad FVG.
        
        Args:
            pattern_detector_instance: Instancia del PatternDetector original
        """
        try:
            # === AGREGAR MEMORIA FVG AL DETECTOR ===
            pattern_detector_instance.fvg_memory = self.fvg_memory
            
            # === GUARDAR MÉTODOS ORIGINALES ===
            original_detect_fvgs = getattr(pattern_detector_instance, '_detect_fair_value_gaps', None)
            original_find_fvgs = getattr(pattern_detector_instance, '_find_fair_value_gaps', None)
            
            # === CREAR MÉTODOS MEJORADOS ===
            def enhanced_detect_fair_value_gaps(data, symbol, timeframe):
                """Versión mejorada que guarda FVGs en memoria persistente."""
                try:
                    # Llamar método original
                    patterns = []
                    if original_find_fvgs:
                        fvgs = original_find_fvgs(data)
                        
                        # Procesar y guardar cada FVG
                        for fvg in fvgs[-2:]:  # Solo los más recientes
                            
                            # === GUARDAR EN MEMORIA PERSISTENTE ===
                            fvg_id = self.fvg_memory.add_fvg(symbol, timeframe, fvg)
                            
                            # === CONTINUAR CON LÓGICA ORIGINAL ===
                            # Usar TradingDirection definido localmente para compatibilidad
                            class TradingDirection:
                                BUY = "buy"
                                SELL = "sell"
                                NEUTRAL = "neutral"
                            
                            direction = TradingDirection.BUY if fvg['type'] == 'bullish' else TradingDirection.SELL
                            
                            gap_range = abs(fvg['high'] - fvg['low'])
                            entry_price = fvg['low'] if direction == TradingDirection.BUY else fvg['high']
                            
                            # Crear patrón con información de memoria
                            pattern = {
                                'type': 'Fair Value Gap',
                                'direction': direction,
                                'confidence': 0.8,
                                'entry_price': entry_price,
                                'stop_loss': entry_price - gap_range if direction == TradingDirection.BUY else entry_price + gap_range,
                                'take_profit': entry_price + gap_range * 2 if direction == TradingDirection.BUY else entry_price - gap_range * 2,
                                'timestamp': fvg.get('timestamp'),
                                'candle_index': fvg.get('index', 0),
                                'fvg_data': fvg,
                                'fvg_id': fvg_id,  # Nuevo: ID de memoria
                                'memory_enhanced': True  # Marca que tiene memoria
                            }
                            
                            patterns.append(pattern)
                            
                            self.logger.info(f"📈 FVG detectado y guardado: {fvg_id} - {symbol} {timeframe}", 
                                             component="fvg_integration")
                    
                    return patterns
                    
                except Exception as e:
                    self.logger.error(f"Error en enhanced_detect_fair_value_gaps: {e}", 
                                      component="fvg_integration")
                    # Fallback al método original si existe
                    if original_detect_fvgs:
                        return original_detect_fvgs(data, symbol, timeframe)
                    return []
            
            def check_fvg_fills(self, current_data, symbol, timeframe):
                """
                Nuevo método para verificar si FVGs fueron llenados.
                """
                try:
                    if not hasattr(self, 'fvg_memory'):
                        return
                    
                    # Obtener FVGs activos
                    active_fvgs = self.fvg_memory.get_active_fvgs(symbol, timeframe)
                    
                    if not current_data or len(current_data) == 0:
                        return
                    
                    # Precio actual (último candle)
                    current_price = float(current_data[-1].get('close', 0))
                    current_high = float(current_data[-1].get('high', 0))
                    current_low = float(current_data[-1].get('low', 0))
                    
                    # Verificar cada FVG activo
                    for fvg in active_fvgs:
                        fvg_high = fvg['high_price']
                        fvg_low = fvg['low_price']
                        fvg_id = fvg['fvg_id']
                        
                        # Verificar si fue llenado
                        if fvg['fvg_type'] == 'bullish':
                            # FVG alcista - precio debe subir y luego bajar al gap
                            if current_low <= fvg_high and current_low >= fvg_low:
                                # Calcular porcentaje de llenado
                                fill_percentage = (fvg_high - current_low) / (fvg_high - fvg_low)
                                
                                if fill_percentage >= 0.8:
                                    self.fvg_memory.update_fvg_status(fvg_id, "filled", 1.0)
                                elif fill_percentage >= 0.3:
                                    self.fvg_memory.update_fvg_status(fvg_id, "partially_filled", fill_percentage)
                        
                        else:  # FVG bajista
                            # FVG bajista - precio debe bajar y luego subir al gap
                            if current_high >= fvg_low and current_high <= fvg_high:
                                # Calcular porcentaje de llenado
                                fill_percentage = (current_high - fvg_low) / (fvg_high - fvg_low)
                                
                                if fill_percentage >= 0.8:
                                    self.fvg_memory.update_fvg_status(fvg_id, "filled", 1.0)
                                elif fill_percentage >= 0.3:
                                    self.fvg_memory.update_fvg_status(fvg_id, "partially_filled", fill_percentage)
                
                except Exception as e:
                    self.logger.error(f"Error verificando llenado de FVGs: {e}", 
                                      component="fvg_integration")
            
            def get_fvg_statistics_for_symbol(self, symbol, timeframe=None):
                """
                Nuevo método para obtener estadísticas de FVGs.
                """
                try:
                    if hasattr(self, 'fvg_memory'):
                        return self.fvg_memory.get_fvg_statistics(symbol, timeframe)
                    return {}
                except Exception as e:
                    self.logger.error(f"Error obteniendo estadísticas FVG: {e}", 
                                      component="fvg_integration")
                    return {}
            
            def cleanup_old_fvgs(self):
                """
                Nuevo método para limpiar FVGs antiguos.
                """
                try:
                    if hasattr(self, 'fvg_memory'):
                        return self.fvg_memory.cleanup_old_fvgs()
                    return 0
                except Exception as e:
                    self.logger.error(f"Error en cleanup FVGs: {e}", 
                                      component="fvg_integration")
                    return 0
            
            # === APLICAR PARCHES ===
            
            # Reemplazar método de detección
            pattern_detector_instance._detect_fair_value_gaps = enhanced_detect_fair_value_gaps
            
            # Agregar nuevos métodos
            pattern_detector_instance.check_fvg_fills = lambda current_data, symbol, timeframe: check_fvg_fills(pattern_detector_instance, current_data, symbol, timeframe)
            pattern_detector_instance.get_fvg_statistics = lambda symbol, timeframe=None: get_fvg_statistics_for_symbol(pattern_detector_instance, symbol, timeframe)
            pattern_detector_instance.cleanup_old_fvgs = lambda: cleanup_old_fvgs(pattern_detector_instance)
            
            # Marcar como patcheado
            pattern_detector_instance._fvg_memory_enabled = True
            
            self.logger.info("✅ Pattern Detector parcheado exitosamente con FVG Memory", 
                             component="fvg_integration")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error aplicando parche FVG: {e}", 
                              component="fvg_integration")
            return False
    
    def create_usage_example(self) -> str:
        """Crea ejemplo de uso del sistema integrado."""
        
        example_code = '''
# === EJEMPLO DE USO DEL SISTEMA FVG INTEGRADO ===

# 1. Importar e inicializar
from analysis.fvg_integration_patch import FVGIntegrationPatch
from analysis.pattern_detector import PatternDetector  # Tu clase original

# 2. Crear instancias
pattern_detector = PatternDetector()
fvg_integration = FVGIntegrationPatch()

# 3. Aplicar integración
success = fvg_integration.patch_pattern_detector(pattern_detector)

if success:
    print("✅ Sistema FVG integrado correctamente")
    
    # 4. Usar como siempre, pero con memoria automática
    symbol = "EURUSD"
    timeframe = "H1"
    market_data = get_market_data(symbol, timeframe)  # Tu función
    
    # Detectar patrones (ahora guarda automáticamente en memoria)
    patterns = pattern_detector._detect_fair_value_gaps(market_data, symbol, timeframe)
    
    # 5. Verificar llenados de FVGs (nuevo)
    pattern_detector.check_fvg_fills(market_data, symbol, timeframe)
    
    # 6. Obtener estadísticas (nuevo)
    stats = pattern_detector.get_fvg_statistics(symbol, timeframe)
    print(f"Estadísticas FVG {symbol}: {stats}")
    
    # 7. Limpieza automática (nuevo)
    cleaned = pattern_detector.cleanup_old_fvgs()
    print(f"FVGs antiguos limpiados: {cleaned}")

else:
    print("❌ Error integrando sistema FVG")
    
# === VERIFICAR MEMORIA PERSISTENTE ===

# Los FVGs se guardan automáticamente en:
# 04-DATA/memory_persistence/historical_analysis/fvg_memory_persistent.json

# Acceso directo a la memoria:
fvg_memory = fvg_integration.fvg_memory

# Obtener FVGs activos
active_fvgs = fvg_memory.get_active_fvgs("EURUSD", "H1")
print(f"FVGs activos EURUSD H1: {len(active_fvgs)}")

# Estadísticas globales
global_stats = fvg_memory.get_fvg_statistics()
print(f"Estadísticas globales: {global_stats}")
'''
        
        return example_code

# === FUNCIÓN DE INTEGRACIÓN AUTOMÁTICA ===

def auto_integrate_fvg_memory(pattern_detector_instance):
    """
    Función conveniente para integrar automáticamente el sistema FVG.
    
    Args:
        pattern_detector_instance: Instancia del PatternDetector
        
    Returns:
        bool: True si la integración fue exitosa
    """
    try:
        integrator = FVGIntegrationPatch()
        return integrator.patch_pattern_detector(pattern_detector_instance)
        
    except Exception as e:
        print(f"❌ Error en auto-integración FVG: {e}")
        return False

# === TESTING Y VALIDACIÓN ===

if __name__ == "__main__":
    print("🔗 Probando integración FVG Memory Manager...")
    
    # Crear instancia de integración
    integrator = FVGIntegrationPatch()
    
    # Mostrar ejemplo de uso
    print("\n" + "="*60)
    print("📚 EJEMPLO DE USO:")
    print("="*60)
    print(integrator.create_usage_example())
    
    print("\n✅ Integración FVG lista para usar")
    print("📁 Archivo de memoria: 04-DATA/memory_persistence/historical_analysis/fvg_memory_persistent.json")
