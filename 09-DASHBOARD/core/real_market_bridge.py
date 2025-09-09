#!/usr/bin/env python3
"""
🌉 REAL MARKET BRIDGE - Puente de Datos Reales para Dashboard
===========================================================

Bridge modular entre componentes enterprise y dashboard.
Conecta MT5DataManager, SilverBulletEnterprise, y UnifiedMemorySystem con dashboard.

METODOLOGÍA: Estructura modular, NO modificar archivos core existentes
OBJETIVO: Eliminar mock data, conectar datos reales enterprise

Fecha: 9 Septiembre 2025
Versión: v1.0.0-modular
"""

import sys
import time
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import threading

# Configurar rutas
project_root = Path(__file__).parent.parent.parent.absolute()
core_path = project_root / "01-CORE"

sys.path.extend([
    str(project_root),
    str(core_path),
    str(core_path / "data_management"),
    str(core_path / "ict_engine" / "advanced_patterns"),
    str(core_path / "analysis")
])

class RealMarketBridge:
    """🌉 Bridge entre componentes enterprise y dashboard"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Inicializar bridge con configuración"""
        self.config = config or self._get_default_config()
        
        # Estado del bridge
        self.is_connected = False
        self.last_update = None
        self.error_count = 0
        
        # Componentes enterprise (lazy loading)
        self.mt5_manager = None
        self.silver_bullet_enterprise = None
        self.unified_memory = None
        
        # Cache para performance
        self.data_cache = {}
        self.cache_ttl = 10  # segundos
        
        print("🌉 RealMarketBridge inicializado (modular)")
    
    def initialize_mt5_manager(self):
        """🔌 Inicializar MT5DataManager"""
        try:
            if not self.mt5_manager:
                success = self._connect_mt5_manager()
                if success:
                    print("✅ MT5DataManager inicializado")
                else:
                    print("⚠️ MT5DataManager no pudo inicializarse")
            else:
                print("✅ MT5DataManager ya inicializado")
        except Exception as e:
            print(f"⚠️ Error inicializando MT5DataManager: {e}")
    
    def initialize_silver_bullet(self):
        """🎯 Inicializar SilverBulletEnterprise"""
        try:
            if not self.silver_bullet_enterprise:
                success = self._connect_silver_bullet_enterprise()
                if success:
                    print("✅ SilverBulletEnterprise inicializado")
                else:
                    print("⚠️ SilverBulletEnterprise no pudo inicializarse")
            else:
                print("✅ SilverBulletEnterprise ya inicializado")
        except Exception as e:
            print(f"⚠️ Error inicializando SilverBulletEnterprise: {e}")
    
    def initialize_unified_memory(self):
        """🧠 Inicializar UnifiedMemorySystem"""
        try:
            if not self.unified_memory:
                success = self._connect_unified_memory()
                if success:
                    print("✅ UnifiedMemorySystem inicializado")
                else:
                    print("⚠️ UnifiedMemorySystem no pudo inicializarse")
            else:
                print("✅ UnifiedMemorySystem ya inicializado")
        except Exception as e:
            print(f"⚠️ Error inicializando UnifiedMemorySystem: {e}")
    
    def get_market_data(self, symbol: str = 'EURUSD', timeframe: str = 'M15') -> Dict:
        """📊 Obtener datos de mercado (API pública para dashboard)"""
        result = self.get_real_market_data([symbol], timeframe)
        if result and 'symbols' in result and symbol in result['symbols']:
            return result['symbols'][symbol]
        return {}
    
    def get_real_market_data(self, symbols: Optional[List[str]] = None, timeframe: str = 'M15') -> Dict:
        """📊 Obtener datos de mercado reales MT5 multi-símbolo (FASE 2)"""
        try:
            # 1. CARGAR símbolos desde configuración si no se especifican
            if symbols is None:
                symbols_config = self._load_symbols_config()
                symbols = self._get_active_symbols_from_config(symbols_config)
            
            # 2. CONECTAR MT5 si es necesario
            if not self.mt5_manager:
                self._connect_mt5_manager()
            
            if not self.mt5_manager:
                print("❌ MT5DataManager no disponible para datos de mercado")
                return self._get_fallback_market_data(symbols)
            
            # 3. OBTENER datos reales para cada símbolo
            market_data = {
                'symbols': {},
                'update_time': time.time(),
                'data_source': 'REAL_MT5_DATA_MANAGER',
                'timeframe': timeframe,
                'total_symbols': 0
            }
            
            for symbol in symbols:
                try:
                    # Obtener datos directos MT5
                    symbol_data = self.mt5_manager.get_direct_market_data(
                        symbol=symbol,
                        timeframe=timeframe,
                        count=1  # Solo última vela para datos actuales
                    )
                    
                    if symbol_data is not None and len(symbol_data) > 0:
                        latest_candle = symbol_data.iloc[-1]
                        
                        market_data['symbols'][symbol] = {
                            'price': float(latest_candle['close']),
                            'open': float(latest_candle['open']),
                            'high': float(latest_candle['high']),
                            'low': float(latest_candle['low']),
                            'volume': int(latest_candle.get('tick_volume', 0)),
                            'spread': 0.0001,  # Aproximación - puede mejorarse
                            'timestamp': time.time(),  # Usar timestamp actual por ahora
                            'status': 'ACTIVE'
                        }
                        market_data['total_symbols'] += 1
                        
                    else:
                        print(f"⚠️ No hay datos para {symbol}")
                        market_data['symbols'][symbol] = {
                            'price': 0.0,
                            'status': 'NO_DATA',
                            'error': 'No data available'
                        }
                        
                except Exception as e:
                    print(f"⚠️ Error obteniendo datos para {symbol}: {e}")
                    market_data['symbols'][symbol] = {
                        'price': 0.0,
                        'status': 'ERROR',
                        'error': str(e)
                    }
                    continue
            
            print(f"✅ Datos de mercado reales obtenidos para {market_data['total_symbols']} símbolos")
            return market_data
            
        except Exception as e:
            print(f"❌ Error en get_real_market_data: {e}")
            return self._get_fallback_market_data(symbols or ['EURUSD', 'GBPUSD'])
    
    def _get_fallback_market_data(self, symbols: List[str]) -> Dict:
        """🔄 Datos de mercado fallback en caso de error MT5"""
        fallback_data = {
            'symbols': {},
            'update_time': time.time(),
            'data_source': 'FALLBACK_SIMULATION',
            'timeframe': 'M15',
            'total_symbols': len(symbols)
        }
        
        # Datos fallback básicos (mejor que hardcoded values)
        base_prices = {
            'EURUSD': 1.0847,
            'GBPUSD': 1.2653,
            'USDJPY': 149.82,
            'XAUUSD': 1920.50,
            'USDCHF': 0.9124,
            'AUDUSD': 0.6745
        }
        
        for symbol in symbols:
            base_price = base_prices.get(symbol, 1.0000)
            # Agregar variación mínima para simular movimiento
            variation = random.uniform(-0.001, 0.001)
            
            fallback_data['symbols'][symbol] = {
                'price': round(base_price + variation, 5),
                'open': round(base_price - variation, 5),
                'high': round(base_price + abs(variation), 5),
                'low': round(base_price - abs(variation), 5),
                'volume': random.randint(1000, 5000),
                'spread': 0.0001,
                'timestamp': time.time(),
                'status': 'FALLBACK'
            }
        
        return fallback_data
    
    def get_pattern_analysis(self, symbols: Optional[List[str]] = None) -> Dict:
        """🎯 Obtener análisis de patrones ICT reales multi-símbolo (FASE 2)"""
        try:
            # 1. CARGAR símbolos desde configuración si no se especifican
            if symbols is None:
                symbols_config = self._load_symbols_config()
                symbols = self._get_active_symbols_from_config(symbols_config)
            
            # 2. CONECTAR Silver Bullet Enterprise si es necesario
            if not self.silver_bullet_enterprise:
                self._connect_silver_bullet_enterprise()
            
            if not self.silver_bullet_enterprise:
                print("❌ SilverBulletEnterprise no disponible para análisis de patrones")
                return self._get_fallback_pattern_analysis(symbols)
            
            # 3. ESTRUCTURAR análisis de patrones reales
            pattern_analysis = {
                'total_patterns': 0,
                'patterns_by_type': {
                    'silver_bullet': 0,
                    'judas_swing': 0,
                    'liquidity_grab': 0,
                    'optimal_trade_entry': 0,
                    'order_blocks': 0
                },
                'recent_signals': [],
                'success_rate': 0.0,
                'data_source': 'SILVER_BULLET_ENTERPRISE',
                'symbols_analyzed': [],
                'last_update': time.time()
            }
            
            # 4. ANALIZAR cada símbolo usando Silver Bullet Enterprise
            for symbol in symbols:
                try:
                    # Obtener datos de mercado frescos para análisis
                    market_data = None
                    if self.mt5_manager:
                        market_data = self.mt5_manager.get_direct_market_data(
                            symbol=symbol,
                            timeframe='M15',
                            count=50  # Suficientes velas para análisis de patrones
                        )
                    
                    if market_data is not None and len(market_data) > 10:
                        # Usar Silver Bullet Enterprise para detectar patrones
                        pattern_result = self.silver_bullet_enterprise.detect(
                            data=market_data,
                            symbol=symbol,
                            timeframe='M15'
                        )
                        
                        if pattern_result and pattern_result.get('confidence', 0.0) > 0.0:
                            # El método detect devuelve un solo resultado, no una lista
                            pattern_analysis['total_patterns'] += 1
                            pattern_analysis['symbols_analyzed'].append(symbol)
                            
                            # Determinar tipo de patrón basado en source
                            pattern_type = 'silver_bullet'  # Es el detector Silver Bullet
                            
                            # Incrementar contador por tipo
                            if pattern_type in pattern_analysis['patterns_by_type']:
                                pattern_analysis['patterns_by_type'][pattern_type] += 1
                            
                            # Agregar a señales recientes
                            if len(pattern_analysis['recent_signals']) < 10:
                                signal = {
                                    'symbol': symbol,
                                    'pattern': pattern_type,
                                    'confidence': pattern_result.get('confidence', 0.0),
                                    'timeframe': 'M15',
                                    'time': datetime.now().strftime('%H:%M'),
                                    'type': pattern_result.get('direction', 'NEUTRAL'),
                                    'quality_score': pattern_result.get('confidence', 0.0),
                                    'narrative': pattern_result.get('narrative', 'Silver Bullet detected')
                                }
                                pattern_analysis['recent_signals'].append(signal)
                            
                            # Obtener success rate desde memoria unificada
                            if self.unified_memory:
                                try:
                                    # Usar método disponible de unified memory para stats
                                    memory_stats = getattr(self.unified_memory, 'get_system_stats', None)
                                    if memory_stats:
                                        stats = memory_stats()
                                        pattern_analysis['success_rate'] = stats.get('pattern_success_rate', 0.75)  # Default reasonable
                                except Exception as e:
                                    print(f"⚠️ Error obteniendo success rate para {symbol}: {e}")
                        
                    else:
                        print(f"⚠️ Datos insuficientes para análisis de patrones: {symbol}")
                        
                except Exception as e:
                    print(f"⚠️ Error analizando patrones para {symbol}: {e}")
                    continue
            
            # 5. CALCULAR métricas finales
            if pattern_analysis['symbols_analyzed']:
                # Calcular success rate promedio si no se obtuvo de memoria
                if pattern_analysis['success_rate'] == 0.0:
                    # Usar heurística basada en confidence promedio
                    if pattern_analysis['recent_signals']:
                        avg_confidence = sum(s['confidence'] for s in pattern_analysis['recent_signals']) / len(pattern_analysis['recent_signals'])
                        pattern_analysis['success_rate'] = min(avg_confidence * 0.8, 0.95)  # Cap at 95%
                
            print(f"✅ Análisis de patrones completado para {len(pattern_analysis['symbols_analyzed'])} símbolos")
            print(f"📊 Total patrones detectados: {pattern_analysis['total_patterns']}")
            
            return pattern_analysis
            
        except Exception as e:
            print(f"❌ Error en get_pattern_analysis: {e}")
            return self._get_fallback_pattern_analysis(symbols or ['EURUSD'])
    
    def _get_fallback_pattern_analysis(self, symbols: List[str]) -> Dict:
        """🔄 Análisis de patrones fallback en caso de error"""
        return {
            'total_patterns': 0,
            'patterns_by_type': {
                'silver_bullet': 0,
                'judas_swing': 0,
                'liquidity_grab': 0,
                'optimal_trade_entry': 0,
                'order_blocks': 0
            },
            'recent_signals': [],
            'success_rate': 0.0,
            'data_source': 'FALLBACK_NO_ENTERPRISE',
            'symbols_analyzed': symbols,
            'error': 'SilverBulletEnterprise not available',
            'last_update': time.time()
        }
    
    def get_system_health(self) -> Dict:
        """💚 Obtener estado del sistema (API pública)"""
        return {
            'bridge_connected': self.is_connected,
            'mt5_connected': self.mt5_manager is not None,
            'silver_bullet_active': self.silver_bullet_enterprise is not None,
            'unified_memory_active': self.unified_memory is not None,
            'error_count': self.error_count,
            'last_update': self.last_update
        }
    
    def get_real_fvg_stats(self) -> Dict:
        """📊 Obtener estadísticas FVG reales multi-símbolo (FASE 2)"""
        try:
            # 1. CARGAR configuración de símbolos desde config
            symbols_config = self._load_symbols_config()
            active_symbols = self._get_active_symbols_from_config(symbols_config)
            
            # 2. ESTRUCTURAR datos FVG reales por símbolo
            fvg_stats = {
                'total_active_fvgs': 0,
                'by_symbol': {},
                'by_priority': {
                    'critical': {'count': 0, 'symbols': []},
                    'important': {'count': 0, 'symbols': []},
                    'extended': {'count': 0, 'symbols': []}
                },
                'last_update': time.time(),
                'data_source': 'REAL_UNIFIED_MEMORY_SYSTEM'
            }
            
            # 3. OBTENER estadísticas reales por símbolo (máximo 6)
            for symbol in active_symbols[:6]:
                try:
                    symbol_fvg_data = self._get_symbol_fvg_stats(symbol)
                    if symbol_fvg_data:
                        fvg_stats['by_symbol'][symbol] = symbol_fvg_data
                        fvg_stats['total_active_fvgs'] += symbol_fvg_data.get('active_count', 0)
                        
                        # Clasificar por prioridad
                        priority = self._get_symbol_priority(symbol, symbols_config)
                        fvg_stats['by_priority'][priority]['count'] += symbol_fvg_data.get('active_count', 0)
                        fvg_stats['by_priority'][priority]['symbols'].append(symbol)
                        
                except Exception as e:
                    print(f"⚠️ Error obteniendo FVG stats para {symbol}: {e}")
                    continue
            
            print(f"✅ FVG Stats reales obtenidas para {len(fvg_stats['by_symbol'])} símbolos")
            return fvg_stats
            
        except Exception as e:
            print(f"❌ Error en get_real_fvg_stats: {e}")
            # Fallback a datos básicos
            return {
                'total_active_fvgs': 0,
                'by_symbol': {},
                'error': str(e),
                'data_source': 'ERROR_FALLBACK',
                'last_update': time.time()
            }
    
    def _load_symbols_config(self) -> Dict:
        """🔧 Cargar configuración de símbolos desde JSON"""
        try:
            config_path = Path(__file__).parent.parent.parent / "01-CORE" / "config" / "trading_symbols_config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando symbols config: {e}")
            # Fallback a configuración por defecto
            return {
                'trading_symbols': {
                    'critical_symbols': {'symbols': ['EURUSD', 'GBPUSD'], 'priority': 1},
                    'important_symbols': {'symbols': ['USDJPY', 'XAUUSD'], 'priority': 2}
                }
            }
    
    def _get_active_symbols_from_config(self, config: Dict) -> List[str]:
        """🎯 Obtener símbolos activos ordenados por prioridad"""
        try:
            symbols = []
            trading_symbols = config.get('trading_symbols', {})
            
            # Ordenar por prioridad: críticos → importantes → extendidos
            priorities = ['critical_symbols', 'important_symbols', 'extended_symbols']
            
            for priority_group in priorities:
                if priority_group in trading_symbols:
                    group_symbols = trading_symbols[priority_group].get('symbols', [])
                    symbols.extend(group_symbols)
            
            return symbols
            
        except Exception as e:
            print(f"⚠️ Error obteniendo símbolos activos: {e}")
            return ['EURUSD', 'GBPUSD', 'USDJPY']  # Fallback
    
    def _get_symbol_fvg_stats(self, symbol: str) -> Optional[Dict]:
        """📈 Obtener estadísticas FVG para un símbolo específico"""
        try:
            # FASE 2: Método simplificado para obtener stats FVG reales
            # Usar importación directa del FVGMemoryManager para evitar complejidad
            
            # Importar dinámicamente el FVGMemoryManager
            try:
                from analysis.fvg_memory_manager import FVGMemoryManager
                fvg_manager = FVGMemoryManager()
            except ImportError:
                print(f"⚠️ FVGMemoryManager no disponible para {symbol}")
                return self._get_fallback_fvg_stats(symbol)
                
            # Obtener FVGs activos por timeframe
            timeframes = ['M15', 'H1', 'H4']  # Timeframes principales del dashboard
            total_active = 0
            total_gap_size = 0.0
            fvg_details = []
            
            for tf in timeframes:
                try:
                    # Usar el método real del FVGMemoryManager
                    active_fvgs = fvg_manager.get_active_fvgs(symbol, tf)
                    if active_fvgs and len(active_fvgs) > 0:
                        tf_count = len(active_fvgs)
                        total_active += tf_count
                        
                        # Calcular gap size promedio para este timeframe
                        tf_gap_size = sum(fvg.get('gap_size_pips', 0) for fvg in active_fvgs)
                        total_gap_size += tf_gap_size
                        
                        fvg_details.append({
                            'timeframe': tf,
                            'count': tf_count,
                            'gap_size_total': tf_gap_size,
                            'avg_gap_size': tf_gap_size / max(1, tf_count)
                        })
                        
                except Exception as e:
                    print(f"⚠️ Error obteniendo FVGs {symbol} {tf}: {e}")
                    continue
            
            return {
                'symbol': symbol,
                'active_count': total_active,
                'total_gap_size_pips': total_gap_size,
                'avg_gap_size_pips': total_gap_size / max(1, total_active),
                'by_timeframe': fvg_details,
                'data_source': 'REAL_FVG_MEMORY_MANAGER',
                'last_update': time.time()
            }
            
        except Exception as e:
            print(f"⚠️ Error obteniendo FVG stats para {symbol}: {e}")
            # Fallback con estructura válida
            return self._get_fallback_fvg_stats(symbol)
    
    def _get_fallback_fvg_stats(self, symbol: str) -> Dict:
        """🔄 Datos FVG de fallback con estructura válida"""
        return {
            'symbol': symbol,
            'active_count': 0,
            'total_gap_size_pips': 0.0,
            'avg_gap_size_pips': 0.0,
            'by_timeframe': [],
            'data_source': 'FALLBACK',
            'last_update': time.time()
        }
    
    def _get_symbol_priority(self, symbol: str, config: Dict) -> str:
        """🎯 Obtener prioridad del símbolo"""
        try:
            trading_symbols = config.get('trading_symbols', {})
            
            if symbol in trading_symbols.get('critical_symbols', {}).get('symbols', []):
                return 'critical'
            elif symbol in trading_symbols.get('important_symbols', {}).get('symbols', []):
                return 'important'
            elif symbol in trading_symbols.get('extended_symbols', {}).get('symbols', []):
                return 'extended'
            else:
                return 'extended'  # Fallback
                
        except Exception:
            return 'extended'
    
    def _get_default_config(self) -> Dict:
        """Configuración por defecto"""
        return {
            'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD'],
            'timeframes': ['M15', 'H1', 'H4'],
            'cache_ttl': 10,
            'max_retries': 3,
            'enable_enterprise': True
        }
    
    def connect_real_components(self) -> bool:
        """🔌 Conectar con componentes enterprise del sistema"""
        try:
            print("🔌 Conectando componentes enterprise...")
            
            # 1. MT5DataManager - CRÍTICO
            success_mt5 = self._connect_mt5_manager()
            if not success_mt5:
                print("❌ Error conectando MT5DataManager")
                return False
            
            # 2. Silver Bullet Enterprise (opcional)
            self._connect_silver_bullet_enterprise()
            
            # 3. Unified Memory System (opcional)  
            self._connect_unified_memory()
            
            self.is_connected = True
            print("✅ RealMarketBridge: Componentes conectados")
            return True
            
        except Exception as e:
            print(f"❌ Error crítico en conexión: {e}")
            return False
    
    def _connect_mt5_manager(self) -> bool:
        """Conectar MT5DataManager"""
        try:
            from data_management.mt5_data_manager import MT5DataManager
            self.mt5_manager = MT5DataManager()
            
            if self.mt5_manager.connect():
                print("✅ MT5DataManager conectado")
                return True
            else:
                print("❌ MT5DataManager no pudo conectar")
                return False
        except Exception as e:
            print(f"⚠️ Error cargando MT5DataManager: {e}")
            return False
    
    def _connect_silver_bullet_enterprise(self) -> bool:
        """Conectar Silver Bullet Enterprise"""
        try:
            # Usar importlib para evitar errores de Pylance
            import importlib
            module = importlib.import_module('ict_engine.advanced_patterns.silver_bullet_enterprise')
            SilverBulletDetectorEnterprise = getattr(module, 'SilverBulletDetectorEnterprise', None)
            
            if SilverBulletDetectorEnterprise:
                self.silver_bullet_enterprise = SilverBulletDetectorEnterprise()
                print("✅ Silver Bullet Enterprise conectado")
                return True
        except Exception as e:
            print(f"⚠️ Silver Bullet Enterprise no disponible: {e}")
        return False
    
    def _connect_unified_memory(self) -> bool:
        """Conectar Unified Memory System"""
        try:
            from analysis.unified_memory_system import get_unified_memory_system
            self.unified_memory = get_unified_memory_system()
            print("✅ Unified Memory System conectado")
            return True
        except Exception as e:
            print(f"⚠️ Unified Memory System no disponible: {e}")
        return False
    
    def get_real_fvg_stats_v2(self) -> Dict[str, Any]:
        """📊 FASE 2 - Obtener estadísticas FVG reales multi-símbolo"""
        try:
            # Usar método get_real_fvg_stats implementado arriba
            return self.get_real_fvg_stats()
        except Exception as e:
            return {
                'bridge_connected': False,
                'data_source': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def disconnect(self):
        """🔌 Desconectar bridge"""
        if self.mt5_manager:
            self.mt5_manager.disconnect()
        
        self.is_connected = False
        self.data_cache.clear()
        print("✅ RealMarketBridge desconectado")
    
    def __del__(self):
        """Limpieza automática"""
        try:
            self.disconnect()
        except:
            pass
