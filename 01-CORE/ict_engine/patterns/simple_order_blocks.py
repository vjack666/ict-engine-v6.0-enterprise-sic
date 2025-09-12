#!/usr/bin/env python3
"""
🎯 SIMPLE ORDER BLOCK DETECTOR v6.0 - HYBRID APPROACH
====================================================

Detector básico ultra-rápido para Order Blocks con enfoque híbrido:
- Detección básica < 0.1s (90% de los casos)
- Pre-filtrado inteligente para validación enterprise
- Optimizado para datos reales MT5
- Sin sacrificar oportunidades críticas

ESTRATEGIA HÍBRIDA:
1. Detección rápida básica (swing highs/lows + proximity)
2. Pre-filtrado por confidence y distance
3. Validación enterprise solo para candidatos prometedores

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 6 Septiembre 2025
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
import sys
import os
import json
from pathlib import Path

# Importar el sistema de logging central
try:
    # Agregar ruta al core si es necesario
    current_dir = os.path.dirname(os.path.abspath(__file__))
    core_path = os.path.join(current_dir, "..", "..", "..")
    if core_path not in sys.path:
        sys.path.insert(0, core_path)
    
    from smart_trading_logger import get_smart_logger, log_info, log_warning, log_error
except ImportError:
    # Fallback si no está disponible el sistema central
    class FallbackLogger:
        def info(self, msg, component="ORDER_BLOCKS"): 
            print(f"📊 [ORDER_BLOCKS] {msg}")
        def warning(self, msg, component="ORDER_BLOCKS"): 
            print(f"⚠️ [ORDER_BLOCKS] {msg}")
        def error(self, msg, component="ORDER_BLOCKS"): 
            print(f"❌ [ORDER_BLOCKS] {msg}")
        def log_order_blocks(self, blocks_data, symbol="UNKNOWN"):
            blocks_count = blocks_data.get('blocks_count', 0)
            print(f"📦 [ORDER_BLOCKS] {blocks_count} blocks detected for {symbol}")
        def log_trading_session_summary(self, session_data):
            patterns = session_data.get('total_patterns', 0)
            symbols = session_data.get('symbols', ['UNKNOWN'])
            print(f"📈 [SESSION] Session completed: {patterns} blocks for {', '.join(symbols)}")
    
    _fallback = FallbackLogger()
    get_smart_logger = lambda: _fallback
    log_info = lambda msg, component="ORDER_BLOCKS": _fallback.info(msg, component)
    log_warning = lambda msg, component="ORDER_BLOCKS": _fallback.warning(msg, component)
    log_error = lambda msg, component="ORDER_BLOCKS": _fallback.error(msg, component)

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

@dataclass
class BasicOrderBlock:
    """Estructura básica para Order Block simple"""
    type: str  # 'demand_zone', 'supply_zone'
    price: float
    confidence: float
    distance_pips: float
    candle_index: int
    volume_confirmation: bool
    timestamp: datetime
    symbol: str
    timeframe: str
    
    # Niveles de trading básicos
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward: float


class SimpleOrderBlockDetector:
    """
    🚀 DETECTOR BÁSICO ULTRA-RÁPIDO v6.0
    ====================================
    
    Detector optimizado para análisis diario rápido:
    ✅ Detección < 0.1s
    ✅ Solo patrones de alta probabilidad
    ✅ Enfoque en zonas cercanas al precio actual
    ✅ Pre-filtrado inteligente
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.lookback_period = self.config.get('lookback_period', 20)
        self.max_distance_pips = self.config.get('max_distance_pips', 30)
        self.min_confidence = self.config.get('min_confidence', 55)
        self.volume_threshold = self.config.get('volume_threshold', 1.2)
        
        # Configurar logger para Order Blocks
        self.logger = get_smart_logger()
        
        # ⚡ Estadísticas de performance
        self.stats = {
            'total_detections': 0,
            'total_detection_time': 0.0,
            'high_confidence_blocks_last': 0,
            'symbols_processed': set(),
            'avg_blocks_per_symbol': 0.0
        }
        
        # Configurar rutas para archivos organizados usando estructura existente
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.order_blocks_logs_dir = self.project_root / "01-CORE" / "data" / "logs" / "ict"
        self.order_blocks_data_dir = self.project_root / "04-DATA" / "reports" / "production"
        self.order_blocks_structured_dir = self.project_root / "04-DATA" / "logs" / "structured"
        
        # Crear directorios si no existen
        self.order_blocks_logs_dir.mkdir(parents=True, exist_ok=True)
        self.order_blocks_data_dir.mkdir(parents=True, exist_ok=True)
        self.order_blocks_structured_dir.mkdir(parents=True, exist_ok=True)
        
        log_info("📦 Order Blocks Detector v6.0 initialized", "ORDER_BLOCKS")
        log_info(f"📁 Output organized: logs→{self.order_blocks_logs_dir.name}, data→{self.order_blocks_data_dir.name}", "ORDER_BLOCKS")
        
    def detect_basic_order_blocks(self, 
                                 data: Any, 
                                 current_price: float,
                                 symbol: str = "UNKNOWN",
                                 timeframe: str = "UNKNOWN") -> List[BasicOrderBlock]:
        """
        🎯 DETECCIÓN BÁSICA ULTRA-RÁPIDA
        ===============================
        
        Args:
            data: DataFrame con OHLCV
            current_price: Precio actual del símbolo
            symbol: Símbolo de trading
            timeframe: Marco temporal
            
        Returns:
            Lista de BasicOrderBlock detectados
        """
        
        # ⚡ Medir tiempo de detección
        import time
        start_time = time.time()
        
        if len(data) < self.lookback_period:
            return []
            
        basic_blocks = []
        self.stats['symbols_processed'].add(symbol)
        
        # 🔍 BUSCAR SWING HIGHS/LOWS EN ÚLTIMAS VELAS
        start_idx = max(5, len(data) - self.lookback_period)
        end_idx = len(data) - 5
        
        for i in range(start_idx, end_idx):
            
            # 📈 DEMAND ZONE: Swing Low con rechazo hacia arriba
            if self._is_swing_low(data, i):
                block = self._create_demand_zone(data, i, current_price, symbol, timeframe)
                if block and self._is_relevant_block(block, current_price):
                    basic_blocks.append(block)
                    
                    # 🔍 LOGGING DETALLADO DEL ORDER BLOCK DETECTADO
                    candle_time = data.index[i].strftime('%Y-%m-%d %H:%M:%S') if hasattr(data.index[i], 'strftime') else str(data.index[i])
                    
                    # Usar sistema de logging central
                    log_info(f"DEMAND ZONE ({symbol} {timeframe}): Precio: {block.price:.5f} | "
                            f"Entry: {block.entry_price:.5f} | SL: {block.stop_loss:.5f} | TP: {block.take_profit:.5f} | "
                            f"Distancia: {block.distance_pips:.1f} pips | Confianza: {block.confidence:.1f}% | "
                            f"R:R: {block.risk_reward:.2f} | Precio actual: {current_price:.5f} | Tiempo: {candle_time}", "ORDER_BLOCKS")
                    
                    # También mantener el print visible para el usuario
                    print(f"📈 DEMAND ZONE ({symbol} {timeframe}): "
                          f"Precio: {block.price:.5f} | "
                          f"Entry: {block.entry_price:.5f} | "
                          f"SL: {block.stop_loss:.5f} | "
                          f"TP: {block.take_profit:.5f} | "
                          f"Distancia: {block.distance_pips:.1f} pips | "
                          f"Confianza: {block.confidence:.1f}% | "
                          f"R:R: {block.risk_reward:.2f} | "
                          f"Precio actual: {current_price:.5f} | "
                          f"Tiempo: {candle_time}")
            
            # 📉 SUPPLY ZONE: Swing High con rechazo hacia abajo  
            if self._is_swing_high(data, i):
                block = self._create_supply_zone(data, i, current_price, symbol, timeframe)
                if block and self._is_relevant_block(block, current_price):
                    basic_blocks.append(block)
                    
                    # 🔍 LOGGING DETALLADO DEL ORDER BLOCK DETECTADO
                    candle_time = data.index[i].strftime('%Y-%m-%d %H:%M:%S') if hasattr(data.index[i], 'strftime') else str(data.index[i])
                    
                    # Usar sistema de logging central
                    log_info(f"SUPPLY ZONE ({symbol} {timeframe}): Precio: {block.price:.5f} | "
                            f"Entry: {block.entry_price:.5f} | SL: {block.stop_loss:.5f} | TP: {block.take_profit:.5f} | "
                            f"Distancia: {block.distance_pips:.1f} pips | Confianza: {block.confidence:.1f}% | "
                            f"R:R: {block.risk_reward:.2f} | Precio actual: {current_price:.5f} | Tiempo: {candle_time}", "ORDER_BLOCKS")
                    
                    # También mantener el print visible para el usuario
                    print(f"📉 SUPPLY ZONE ({symbol} {timeframe}): "
                          f"Precio: {block.price:.5f} | "
                          f"Entry: {block.entry_price:.5f} | "
                          f"SL: {block.stop_loss:.5f} | "
                          f"TP: {block.take_profit:.5f} | "
                          f"Distancia: {block.distance_pips:.1f} pips | "
                          f"Confianza: {block.confidence:.1f}% | "
                          f"R:R: {block.risk_reward:.2f} | "
                          f"Precio actual: {current_price:.5f} | "
                          f"Tiempo: {candle_time}")
        
        # 🏆 ORDENAR POR RELEVANCIA (distancia + confidence)
        basic_blocks.sort(key=lambda x: (x.distance_pips, -x.confidence))
        
        # 📊 RESUMEN DE DETECCIÓN
        if basic_blocks:
            demand_zones = [b for b in basic_blocks if b.type == 'demand_zone']
            supply_zones = [b for b in basic_blocks if b.type == 'supply_zone']
            avg_confidence = sum(b.confidence for b in basic_blocks) / len(basic_blocks)
            
            # Log resumen con sistema central
            summary_msg = (f"{len(basic_blocks)} Order Blocks detectados "
                          f"({len(demand_zones)} Demand, {len(supply_zones)} Supply) | "
                          f"Confianza promedio: {avg_confidence:.1f}%")
            log_info(f"RESUMEN {symbol} {timeframe}: {summary_msg}", "ORDER_BLOCKS")
            
            print(f"📊 RESUMEN {symbol} {timeframe}: {summary_msg}")
            
            # 💾 GUARDAR DATOS ORGANIZADOS usando estructura existente
            self._save_organized_results(basic_blocks, symbol, timeframe, current_price)
            
            # 📈 GENERAR RESUMEN DE SESIÓN usando logging centralizado
            self._generate_session_summary(basic_blocks, symbol, timeframe, current_price)
        
        # ⚡ Actualizar estadísticas de performance
        detection_time = time.time() - start_time
        self.stats['total_detections'] += 1
        self.stats['total_detection_time'] += detection_time
        self.stats['high_confidence_blocks_last'] = len([b for b in basic_blocks if b.confidence >= 70])
        self.stats['avg_blocks_per_symbol'] = len(basic_blocks)
        
        return basic_blocks[:5]  # Top 5 más relevantes
    
    def _is_swing_low(self, data: Any, idx: int, lookback: int = 3) -> bool:
        """Detectar swing low básico"""
        if idx < lookback or idx >= len(data) - lookback:
            return False
            
        current_low = data.iloc[idx]['low']
        
        # Verificar que sea el mínimo local
        for i in range(idx - lookback, idx + lookback + 1):
            if i != idx and data.iloc[i]['low'] <= current_low:
                return False
                
        return True
    
    def _is_swing_high(self, data: Any, idx: int, lookback: int = 3) -> bool:
        """Detectar swing high básico"""
        if idx < lookback or idx >= len(data) - lookback:
            return False
            
        current_high = data.iloc[idx]['high']
        
        # Verificar que sea el máximo local
        for i in range(idx - lookback, idx + lookback + 1):
            if i != idx and data.iloc[i]['high'] >= current_high:
                return False
                
        return True
    
    def _create_demand_zone(self, data: Any, idx: int, current_price: float, 
                           symbol: str, timeframe: str) -> Optional[BasicOrderBlock]:
        """Crear zona de demanda básica"""
        
        candle = data.iloc[idx]
        
        # Asegurar que current_price es numérico
        try:
            current_price = float(current_price)
        except (ValueError, TypeError):
            current_price = float(candle['close'])  # Fallback al precio de cierre
        
        # 📊 CALCULAR MÉTRICAS BÁSICAS
        distance_pips = abs(current_price - float(candle['low'])) * 10000
        
        # Volume confirmation básico
        avg_volume = data['volume'].iloc[max(0, idx-10):idx].mean() if 'volume' in data.columns else 1
        volume_conf = (candle.get('volume', avg_volume) / avg_volume) >= self.volume_threshold
        
        # Confidence básico basado en:
        # - Distancia al precio actual
        # - Fortaleza del rechazo (tamaño de mecha)
        # - Volume confirmation
        
        wick_size = candle['close'] - candle['low']
        body_size = abs(candle['close'] - candle['open'])
        wick_ratio = wick_size / (body_size + 0.0001)  # Evitar división por 0
        
        # Confidence dinámico basado en configuración - DEMAND ZONE
        max_confidence = self.config.get('max_confidence', 90)
        base_confidence = self.config.get('base_confidence', 40)
        wick_multiplier = self.config.get('wick_confidence_multiplier', 20)
        volume_bonus = self.config.get('volume_confidence_bonus', 10)
        distance_penalty_threshold = self.config.get('distance_penalty_threshold', 20)
        
        confidence = min(max_confidence, base_confidence + (wick_ratio * wick_multiplier) + 
                        (volume_bonus if volume_conf else 0) + 
                        max(0, distance_penalty_threshold - distance_pips))
        
        # 📈 NIVELES DE TRADING DINÁMICOS
        entry_offset = self.config.get('demand_entry_offset', 0.25)
        stop_offset = self.config.get('demand_stop_offset', 0.1)
        risk_reward_ratio = self.config.get('risk_reward_ratio', 2.0)
        
        entry_price = candle['low'] + (candle['high'] - candle['low']) * entry_offset
        stop_loss = candle['low'] - (candle['high'] - candle['low']) * stop_offset
        take_profit = entry_price + (entry_price - stop_loss) * risk_reward_ratio
        
        risk_reward = abs(take_profit - entry_price) / abs(entry_price - stop_loss) if entry_price != stop_loss else 0
        
        return BasicOrderBlock(
            type='demand_zone',
            price=candle['low'],
            confidence=confidence,
            distance_pips=distance_pips,
            candle_index=idx,
            volume_confirmation=volume_conf,
            timestamp=data.index[idx] if hasattr(data.index[idx], 'to_pydatetime') else datetime.now(),
            symbol=symbol,
            timeframe=timeframe,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward=risk_reward
        )
    
    def _create_supply_zone(self, data: Any, idx: int, current_price: float,
                           symbol: str, timeframe: str) -> Optional[BasicOrderBlock]:
        """Crear zona de oferta básica"""
        
        candle = data.iloc[idx]
        
        # Asegurar que current_price es numérico
        try:
            current_price = float(current_price)
        except (ValueError, TypeError):
            current_price = float(candle['close'])  # Fallback al precio de cierre
        
        # 📊 CALCULAR MÉTRICAS BÁSICAS
        distance_pips = abs(current_price - float(candle['high'])) * 10000
        
        # Volume confirmation básico
        avg_volume = data['volume'].iloc[max(0, idx-10):idx].mean() if 'volume' in data.columns else 1
        volume_conf = (candle.get('volume', avg_volume) / avg_volume) >= self.volume_threshold
        
        # Confidence básico
        wick_size = candle['high'] - candle['close']
        body_size = abs(candle['close'] - candle['open'])
        wick_ratio = wick_size / (body_size + 0.0001)
        
        # Confidence dinámico basado en configuración - SUPPLY ZONE
        max_confidence = self.config.get('max_confidence', 90)
        base_confidence = self.config.get('base_confidence', 40)
        wick_multiplier = self.config.get('wick_confidence_multiplier', 20)
        volume_bonus = self.config.get('volume_confidence_bonus', 10)
        distance_penalty_threshold = self.config.get('distance_penalty_threshold', 20)
        
        confidence = min(max_confidence, base_confidence + (wick_ratio * wick_multiplier) + 
                        (volume_bonus if volume_conf else 0) + 
                        max(0, distance_penalty_threshold - distance_pips))
        
        # 📉 NIVELES DE TRADING DINÁMICOS
        entry_offset = self.config.get('supply_entry_offset', 0.25)
        stop_offset = self.config.get('supply_stop_offset', 0.1)
        risk_reward_ratio = self.config.get('risk_reward_ratio', 2.0)
        
        entry_price = candle['high'] - (candle['high'] - candle['low']) * entry_offset
        stop_loss = candle['high'] + (candle['high'] - candle['low']) * stop_offset
        take_profit = entry_price - (stop_loss - entry_price) * risk_reward_ratio
        
        risk_reward = abs(take_profit - entry_price) / abs(entry_price - stop_loss) if entry_price != stop_loss else 0
        
        return BasicOrderBlock(
            type='supply_zone',
            price=candle['high'],
            confidence=confidence,
            distance_pips=distance_pips,
            candle_index=idx,
            volume_confirmation=volume_conf,
            timestamp=data.index[idx] if hasattr(data.index[idx], 'to_pydatetime') else datetime.now(),
            symbol=symbol,
            timeframe=timeframe,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_reward=risk_reward
        )
    
    def _is_relevant_block(self, block: BasicOrderBlock, current_price: float) -> bool:
        """Verificar si el block es relevante para trading"""
        
        # Filtros básicos de relevancia
        if block.distance_pips > self.max_distance_pips:
            return False
            
        if block.confidence < self.min_confidence:
            return False
            
        if block.risk_reward < 1.5:  # RR mínimo
            return False
            
        return True
    
    def get_nearest_blocks(self, blocks: List[BasicOrderBlock], 
                          current_price: float, limit: int = 3) -> List[BasicOrderBlock]:
        """Obtener los blocks más cercanos al precio actual"""
        
        if not blocks:
            return []
            
        # Ordenar por distancia
        sorted_blocks = sorted(blocks, key=lambda x: x.distance_pips)
        return sorted_blocks[:limit]
    
    def filter_high_confidence(self, blocks: List[BasicOrderBlock], 
                              min_confidence: float = 70) -> List[BasicOrderBlock]:
        """Filtrar solo blocks de alta confidence para validación enterprise"""
        
        return [block for block in blocks if block.confidence >= min_confidence]

    def _save_organized_results(self, blocks: List[BasicOrderBlock], 
                               symbol: str, timeframe: str, current_price: float) -> None:
        """💾 Guardar resultados en estructura organizada existente"""
        import json
        from datetime import datetime
        
        # Usar carpetas existentes en lugar de crear nuevas
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Estructura de datos para guardar
        results_data = {
            "timestamp": timestamp,
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "total_blocks": len(blocks),
            "demand_zones": len([b for b in blocks if b.type == 'demand_zone']),
            "supply_zones": len([b for b in blocks if b.type == 'supply_zone']),
            "avg_confidence": sum(b.confidence for b in blocks) / len(blocks) if blocks else 0,
            "blocks": []
        }
        
        # Guardar en carpeta existente 04-DATA/reports usando logging centralizado
        try:
            # Usar el sistema de logging centralizado para Order Blocks
            blocks_data = {
                "symbol": symbol,
                "timeframe": timeframe,
                "blocks_count": len(blocks),
                "bullish_count": len([b for b in blocks if b.type == 'demand_zone']),
                "bearish_count": len([b for b in blocks if b.type == 'supply_zone']),
                "blocks": [],
                "confidence": sum(b.confidence for b in blocks) / len(blocks) if blocks else 0
            }
            
            # Agregar detalles de cada block para logging estructurado
            for block in blocks:
                block_data = {
                    "type": block.type,
                    "price": float(block.price),
                    "confidence": float(block.confidence),
                    "distance_pips": float(block.distance_pips),
                    "candle_index": int(block.candle_index),
                    "volume_confirmation": bool(block.volume_confirmation),
                    "timestamp": block.timestamp.isoformat() if hasattr(block.timestamp, 'isoformat') else str(block.timestamp),
                    "entry_price": float(block.entry_price),
                    "stop_loss": float(block.stop_loss),
                    "take_profit": float(block.take_profit),
                    "risk_reward": float(block.risk_reward)
                }
                blocks_data["blocks"].append(block_data)
            
            # Usar el sistema de logging centralizado
            self.logger.log_order_blocks(blocks_data, symbol)
            
            # También guardar archivo detallado en reports para análisis posterior
            filename = f"order_blocks_{symbol}_{timeframe}_{timestamp}.json"
            filepath = self.order_blocks_data_dir / filename
            
            results_data = {
                "timestamp": timestamp,
                "symbol": symbol,
                "timeframe": timeframe,
                "current_price": current_price,
                "total_blocks": len(blocks),
                "demand_zones": len([b for b in blocks if b.type == 'demand_zone']),
                "supply_zones": len([b for b in blocks if b.type == 'supply_zone']),
                "avg_confidence": sum(b.confidence for b in blocks) / len(blocks) if blocks else 0,
                "blocks": blocks_data["blocks"]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            
            log_info(f"💾 Resultados guardados: {filepath.name}", "ORDER_BLOCKS")
            
        except Exception as e:
            log_error(f"Error guardando resultados: {e}", "ORDER_BLOCKS")
            
    def _generate_session_summary(self, blocks: List[BasicOrderBlock], 
                                symbol: str, timeframe: str, current_price: float):
        """📈 Generar resumen de sesión usando logging centralizado"""
        try:
            # Calcular estadísticas de la sesión
            demand_zones = [b for b in blocks if b.type == 'demand_zone']
            supply_zones = [b for b in blocks if b.type == 'supply_zone']
            avg_confidence = sum(b.confidence for b in blocks) / len(blocks) if blocks else 0
            high_conf_blocks = [b for b in blocks if b.confidence >= 70]
            
            # Preparar datos para logging centralizado
            session_data = {
                "symbols": [symbol],
                "total_patterns": len(blocks),
                "execution_time": 0.1,  # Tiempo estimado
                "performance": {
                    "demand_zones": len(demand_zones),
                    "supply_zones": len(supply_zones),
                    "avg_confidence": avg_confidence,
                    "high_confidence_blocks": len(high_conf_blocks),
                    "current_price": current_price,
                    "timeframe": timeframe
                },
                "memory_stats": {
                    "blocks_analyzed": len(blocks),
                    "blocks_relevant": len([b for b in blocks if self._is_relevant_block(b, current_price)])
                },
                "errors": 0
            }
            
            # Usar sistema de logging centralizado para resumen de sesión
            self.logger.log_trading_session_summary(session_data)
            
        except Exception as e:
            log_error(f"Error generando resumen de sesión: {e}", "ORDER_BLOCKS")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """⚡ Obtener estadísticas de performance del detector"""
        
        if self.stats['total_detections'] == 0:
            return {
                'total_detections': 0,
                'avg_detection_time_ms': 0.0,
                'high_confidence_blocks_last': 0,
                'symbols_processed': 0,
                'avg_blocks_per_symbol': 0.0
            }
        
        return {
            'total_detections': self.stats['total_detections'],
            'avg_detection_time_ms': (self.stats['total_detection_time'] / self.stats['total_detections']) * 1000,
            'high_confidence_blocks_last': self.stats['high_confidence_blocks_last'],
            'symbols_processed': len(self.stats['symbols_processed']),
            'avg_blocks_per_symbol': self.stats['avg_blocks_per_symbol']
        }
