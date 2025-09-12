#!/usr/bin/env python3
"""
🎯 ORDER BLOCKS PATTERN INTEGRATION v6.0 - MAIN SYSTEM CONNECTOR
================================================================

Integración del sistema híbrido de Order Blocks con el motor principal ICT v6.0:
- Conexión con PatternDetector principal
- Integración con main.py orchestrator
- Compatible con arquitectura SIC/SLUC
- Optimizado para datos reales MT5

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 6 Septiembre 2025
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import time

# ThreadSafe pandas import
try:
    # Intentar usar el manager threadsafe primero
    from data_management.advanced_candle_downloader import _pandas_manager
    if hasattr(_pandas_manager, 'get_safe_pandas_instance'):
        pd = _pandas_manager.get_safe_pandas_instance()
    else:
        # Si el manager no tiene el método esperado, usar pandas directamente
        import pandas as pd
    
    if pd is None:
        import pandas as pd
        
except (ImportError, AttributeError):
    import pandas as pd

# Import del sistema híbrido
try:
    from .hybrid_order_block_analyzer import HybridOrderBlockAnalyzer, HybridOrderBlockResult
    HYBRID_AVAILABLE = True
except ImportError:
    HYBRID_AVAILABLE = False

# Imports del sistema principal
try:
    from ict_engine.unified_logging import (
        log_info, log_warning, log_error, log_debug,
        UnifiedLoggingSystem, create_unified_logger
    )
    from analysis.unified_memory_system import get_unified_memory_system
    CORE_AVAILABLE = True
    SmartTradingLogger = UnifiedLoggingSystem  # Para compatibilidad
except ImportError:
    CORE_AVAILABLE = False
    # Fallback logging functions
    def log_info(message, component="CORE"): print(f"[{component}] INFO: {message}")
    def log_warning(message, component="CORE"): print(f"[{component}] WARNING: {message}") 
    def log_error(message, component="CORE"): print(f"[{component}] ERROR: {message}")
    def log_debug(message, component="CORE"): print(f"[{component}] DEBUG: {message}")
    def get_unified_memory_system(): return None
    class SmartTradingLogger:
        def __init__(self, name): 
            self.name = name
        def info(self, msg): print(f"[{self.name}] INFO: {msg}")
        def warning(self, msg): print(f"[{self.name}] WARNING: {msg}")


class OrderBlocksPatternDetector:
    """
    🎯 DETECTOR DE PATRONES ORDER BLOCKS v6.0
    =========================================
    
    Detector principal que integra el sistema híbrido con el motor ICT:
    ✅ Compatible con PatternDetector framework
    ✅ Integración con UnifiedMemorySystem
    ✅ Optimizado para datos reales MT5
    ✅ Logging empresarial completo
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.pattern_name = "order_blocks"
        
        # Inicializar sistema híbrido
        if HYBRID_AVAILABLE:
            self.hybrid_analyzer = HybridOrderBlockAnalyzer(config)
        else:
            self.hybrid_analyzer = None
            
        # Sistema de memoria unificada
        self.memory_system = get_unified_memory_system() if CORE_AVAILABLE else None
        
        # Logger empresarial
        if CORE_AVAILABLE:
            self.logger = SmartTradingLogger("OrderBlocksDetector")
        else:
            self.logger = None
            
        # Estadísticas de performance
        self.stats = {
            'total_detections': 0,
            'successful_detections': 0,
            'avg_detection_time': 0.0,
            'patterns_found': 0
        }
    
    def detect_patterns(self, 
                       data: Any, 
                       symbol: str, 
                       timeframe: str, 
                       current_price: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        🎯 DETECCIÓN PRINCIPAL DE PATRONES ORDER BLOCKS
        ==============================================
        
        Args:
            data: DataFrame con datos OHLCV
            symbol: Símbolo de trading (ej. EURUSD)
            timeframe: Marco temporal (ej. H1, M15)
            current_price: Precio actual (opcional)
            
        Returns:
            Lista de patrones detectados en formato estándar
        """
        
        start_time = time.time()
        self.stats['total_detections'] += 1
        
        if not self.hybrid_analyzer:
            if self.logger:
                log_warning(f"Hybrid analyzer not available for {symbol}")
            return []
            
        # Obtener precio actual si no se proporciona
        if current_price is None:
            current_price = float(data.iloc[-1]['close'])
            
        try:
            # 🚀 ANÁLISIS HÍBRIDO
            results = self.hybrid_analyzer.analyze_order_blocks(
                data, current_price, symbol, timeframe
            )
            
            # 📊 CONVERTIR A FORMATO ESTÁNDAR
            patterns = []
            for result in results:
                pattern = self._convert_to_standard_format(result, symbol, timeframe)
                patterns.append(pattern)
                
            # 💾 GUARDAR EN MEMORIA UNIFICADA
            if self.memory_system and patterns:
                self._save_to_memory(patterns, symbol, timeframe)
                
            # 📈 ACTUALIZAR ESTADÍSTICAS
            detection_time = time.time() - start_time
            self.stats['successful_detections'] += 1
            self.stats['patterns_found'] += len(patterns)
            self.stats['avg_detection_time'] = (
                (self.stats['avg_detection_time'] * (self.stats['successful_detections'] - 1) + detection_time) /
                self.stats['successful_detections']
            )
            
            # 📝 LOG SUCCESS
            if self.logger:
                log_info(f"Order Blocks detected: {len(patterns)} patterns for {symbol} {timeframe} in {detection_time:.3f}s")
                
            return patterns
            
        except Exception as e:
            if self.logger:
                log_warning(f"Order Blocks detection failed for {symbol}: {e}")
            return []
    
    def _convert_to_standard_format(self, 
                                   result: HybridOrderBlockResult, 
                                   symbol: str, 
                                   timeframe: str) -> Dict[str, Any]:
        """Convertir resultado híbrido a formato estándar del sistema"""
        
        basic = result.basic_block
        
        # Formato estándar compatible con PatternDetector framework
        pattern = {
            # Información básica del patrón
            'pattern_type': 'order_block',
            'sub_type': basic.type,  # demand_zone o supply_zone
            'symbol': symbol,
            'timeframe': timeframe,
            'timestamp': basic.timestamp,
            
            # Métricas de confidence
            'confidence': result.hybrid_confidence,
            'basic_confidence': basic.confidence,
            'enterprise_validated': result.enterprise_validated,
            'recommendation': result.recommendation,
            
            # Niveles de precios
            'price': basic.price,
            'entry_price': result.optimized_entry or basic.entry_price,
            'stop_loss': result.optimized_stop or basic.stop_loss,
            'take_profit': result.optimized_target or basic.take_profit,
            
            # Métricas de trading
            'risk_reward': basic.risk_reward,
            'distance_pips': basic.distance_pips,
            'volume_confirmation': basic.volume_confirmation,
            
            # Información técnica
            'candle_index': basic.candle_index,
            'detection_time_ms': result.detection_time_ms,
            'validation_time_ms': result.validation_time_ms,
            
            # Contexto del mercado
            'session_context': self._get_session_context(),
            
            # Metadatos para el sistema
            'detector': 'hybrid_order_blocks_v6',
            'analysis_id': f"{symbol}_{timeframe}_{int(time.time())}",
            
            # Información enterprise (si disponible)
            'enterprise_data': result.enterprise_result if result.enterprise_validated else None
        }
        
        return pattern
    
    def _save_to_memory(self, patterns: List[Dict], symbol: str, timeframe: str):
        """Guardar patrones en el sistema de memoria unificada"""
        
        if not self.memory_system:
            return
            
        try:
            for pattern in patterns:
                # Guardar cada patrón en la memoria
                memory_data = {
                    'pattern_type': pattern['pattern_type'],
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'confidence': pattern['confidence'],
                    'timestamp': pattern['timestamp'],
                    'entry_price': pattern['entry_price'],
                    'metadata': {
                        'detector': pattern['detector'],
                        'recommendation': pattern['recommendation'],
                        'enterprise_validated': pattern['enterprise_validated']
                    }
                }
                
                # 🎯 GUARDAR EN MEMORIA UNIFICADA CON FALLBACK ROBUSTO
                # ===================================================
                # Este método maneja la integración con el sistema de memoria unificada
                # del ICT Engine v6.0. Incluye múltiples estrategias de fallback para
                # garantizar que los patrones se guarden correctamente incluso si 
                # el sistema de memoria no está completamente disponible.
                
                success = self._store_pattern_with_fallback(
                    symbol=symbol,
                    pattern_data=memory_data,
                    pattern_full=pattern
                )
                
        except Exception as e:
            if self.logger:
                log_warning(f"Failed to save patterns to memory: {e}")
    
    def _get_session_context(self) -> Dict[str, Any]:
        """Obtener contexto de la sesión actual"""
        
        now = datetime.now()
        hour = now.hour
        
        # Determinar sesión de trading
        if 0 <= hour < 8:
            session = "Asian"
        elif 8 <= hour < 16:
            session = "London"
        elif 16 <= hour < 24:
            session = "New_York"
        else:
            session = "Transition"
            
        return {
            'session': session,
            'hour': hour,
            'day_of_week': now.weekday(),
            'is_major_session': session in ['London', 'New_York']
        }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de performance del detector"""
        
        base_stats = self.stats.copy()
        
        # Agregar estadísticas del sistema híbrido
        if self.hybrid_analyzer:
            hybrid_stats = self.hybrid_analyzer.get_performance_stats()
            base_stats.update({
                'hybrid_stats': hybrid_stats
            })
            
        # Calcular métricas adicionales
        total = base_stats['total_detections']
        if total > 0:
            base_stats['success_rate'] = (base_stats['successful_detections'] / total) * 100
            base_stats['avg_patterns_per_detection'] = base_stats['patterns_found'] / max(1, base_stats['successful_detections'])
            
        return base_stats
    
    def _store_pattern_with_fallback(self, 
                                   symbol: str, 
                                   pattern_data: Dict[str, Any], 
                                   pattern_full: Dict[str, Any]) -> bool:
        """
        🎯 MÉTODO DE ALMACENAMIENTO CON FALLBACK ROBUSTO v6.0
        ====================================================
        
        Este método implementa múltiples estrategias para guardar patrones
        en el sistema de memoria unificada, con fallbacks robustos para
        garantizar que los datos no se pierdan.
        
        ESTRATEGIAS DE FALLBACK:
        1. 🏆 Método store_pattern_memory (preferido)
        2. 🥈 Método store_pattern (alternativo)
        3. 🥉 Método add_pattern (básico)
        4. 📁 Almacenamiento local como último recurso
        
        Args:
            symbol: Símbolo del instrumento (ej. EURUSD)
            pattern_data: Datos del patrón en formato memoria
            pattern_full: Patrón completo con todos los datos
            
        Returns:
            bool: True si el almacenamiento fue exitoso
        """
        
        if not self.memory_system:
            if self.logger:
                log_warning(f"Memory system not available for {symbol}")
            return False
            
        try:
            # 🏆 ESTRATEGIA 1: store_pattern_memory (método preferido)
            # Nota: Este método puede no existir, por eso usamos hasattr()
            if hasattr(self.memory_system, 'store_pattern_memory'):
                # type: ignore - Método verificado dinámicamente con hasattr()
                self.memory_system.store_pattern_memory(  # type: ignore
                    symbol=symbol,
                    pattern_data=pattern_data
                )
                if self.logger:
                    log_info(f"Pattern stored using store_pattern_memory for {symbol}")
                return True
                
        except Exception as e:
            if self.logger:
                log_warning(f"store_pattern_memory failed for {symbol}: {e}")
                
        try:
            # 🥈 ESTRATEGIA 2: store_pattern (método alternativo)
            # Nota: Este método puede no existir, por eso usamos hasattr()
            if hasattr(self.memory_system, 'store_pattern'):
                # type: ignore - Método verificado dinámicamente con hasattr()
                self.memory_system.store_pattern(  # type: ignore
                    pattern_type=pattern_data['pattern_type'],
                    symbol=symbol,
                    data=pattern_data
                )
                if self.logger:
                    log_info(f"Pattern stored using store_pattern for {symbol}")
                return True
                
        except Exception as e:
            if self.logger:
                log_warning(f"store_pattern failed for {symbol}: {e}")
                
        try:
            # 🥉 ESTRATEGIA 3: add_pattern (método básico)
            # Nota: Este método puede no existir, por eso usamos hasattr()
            if hasattr(self.memory_system, 'add_pattern'):
                # type: ignore - Método verificado dinámicamente con hasattr()
                self.memory_system.add_pattern(pattern_data)  # type: ignore
                if self.logger:
                    log_info(f"Pattern stored using add_pattern for {symbol}")
                return True
                
        except Exception as e:
            if self.logger:
                log_warning(f"add_pattern failed for {symbol}: {e}")
                
        try:
            # 📁 ESTRATEGIA 4: Almacenamiento local (último recurso)
            self._store_pattern_locally(symbol, pattern_full)
            if self.logger:
                log_info(f"Pattern stored locally as fallback for {symbol}")
            return True
            
        except Exception as e:
            if self.logger:
                log_warning(f"Local storage fallback failed for {symbol}: {e}")
                
        return False
    
    def _store_pattern_locally(self, symbol: str, pattern: Dict[str, Any]):
        """
        📁 ALMACENAMIENTO LOCAL COMO ÚLTIMO RECURSO
        ==========================================
        
        Guarda el patrón en un archivo local cuando el sistema
        de memoria unificada no está disponible.
        """
        
        try:
            import json
            from pathlib import Path
            
            # Crear directorio de respaldo si no existe
            backup_dir = Path("04-DATA/patterns_backup")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Archivo por símbolo y fecha
            date_str = datetime.now().strftime("%Y%m%d")
            backup_file = backup_dir / f"{symbol}_{date_str}_order_blocks.json"
            
            # Cargar patrones existentes o crear lista nueva
            patterns = []
            if backup_file.exists():
                with open(backup_file, 'r', encoding='utf-8') as f:
                    patterns = json.load(f)
                    
            # Agregar nuevo patrón
            patterns.append({
                'timestamp': pattern['timestamp'].isoformat() if isinstance(pattern['timestamp'], datetime) else str(pattern['timestamp']),
                'pattern': pattern
            })
            
            # Guardar actualizado
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(patterns, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            if self.logger:
                log_warning(f"Local backup storage failed: {e}")
    
    def reset_stats(self):
        """Resetear estadísticas de performance"""
        self.stats = {
            'total_detections': 0,
            'successful_detections': 0,
            'avg_detection_time': 0.0,
            'patterns_found': 0
        }
        
        if self.hybrid_analyzer:
            self.hybrid_analyzer.stats = {
                'total_analyses': 0,
                'basic_only': 0,
                'enterprise_validations': 0,
                'avg_detection_time': 0.0
            }


# Factory function para compatibilidad con el sistema principal
def create_order_blocks_detector(config: Optional[Dict] = None) -> OrderBlocksPatternDetector:
    """
    Factory function para crear detector de Order Blocks
    Compatible con PatternDetector framework
    """
    return OrderBlocksPatternDetector(config)
