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

# ThreadSafe pandas import
try:
    from data_management.advanced_candle_downloader import _pandas_manager
    pd = _pandas_manager.get_pandas()
except ImportError:
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
        
        if len(data) < self.lookback_period:
            return []
            
        basic_blocks = []
        
        # 🔍 BUSCAR SWING HIGHS/LOWS EN ÚLTIMAS VELAS
        start_idx = max(5, len(data) - self.lookback_period)
        end_idx = len(data) - 5
        
        for i in range(start_idx, end_idx):
            
            # 📈 DEMAND ZONE: Swing Low con rechazo hacia arriba
            if self._is_swing_low(data, i):
                block = self._create_demand_zone(data, i, current_price, symbol, timeframe)
                if block and self._is_relevant_block(block, current_price):
                    basic_blocks.append(block)
            
            # 📉 SUPPLY ZONE: Swing High con rechazo hacia abajo  
            if self._is_swing_high(data, i):
                block = self._create_supply_zone(data, i, current_price, symbol, timeframe)
                if block and self._is_relevant_block(block, current_price):
                    basic_blocks.append(block)
        
        # 🏆 ORDENAR POR RELEVANCIA (distancia + confidence)
        basic_blocks.sort(key=lambda x: (x.distance_pips, -x.confidence))
        
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
        
        # 📊 CALCULAR MÉTRICAS BÁSICAS
        distance_pips = abs(current_price - candle['low']) * 10000
        
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
        
        confidence = min(90, 40 + (wick_ratio * 20) + (10 if volume_conf else 0) + 
                        max(0, 20 - distance_pips))
        
        # 📈 NIVELES DE TRADING BÁSICOS
        entry_price = candle['low'] + (candle['high'] - candle['low']) * 0.25
        stop_loss = candle['low'] - (candle['high'] - candle['low']) * 0.1
        take_profit = entry_price + (entry_price - stop_loss) * 2.0
        
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
        
        # 📊 CALCULAR MÉTRICAS BÁSICAS
        distance_pips = abs(current_price - candle['high']) * 10000
        
        # Volume confirmation básico
        avg_volume = data['volume'].iloc[max(0, idx-10):idx].mean() if 'volume' in data.columns else 1
        volume_conf = (candle.get('volume', avg_volume) / avg_volume) >= self.volume_threshold
        
        # Confidence básico
        wick_size = candle['high'] - candle['close']
        body_size = abs(candle['close'] - candle['open'])
        wick_ratio = wick_size / (body_size + 0.0001)
        
        confidence = min(90, 40 + (wick_ratio * 20) + (10 if volume_conf else 0) + 
                        max(0, 20 - distance_pips))
        
        # 📉 NIVELES DE TRADING BÁSICOS
        entry_price = candle['high'] - (candle['high'] - candle['low']) * 0.25
        stop_loss = candle['high'] + (candle['high'] - candle['low']) * 0.1
        take_profit = entry_price - (stop_loss - entry_price) * 2.0
        
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
