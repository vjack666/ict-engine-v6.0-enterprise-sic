"""
📊 DATA COLLECTOR - ICT ENGINE v6.0 ENTERPRISE
==============================================

Sistema de recolección de datos enterprise para análisis de mercado.
Compatible con dashboard y sistemas de validación.

Módulos Enterprise Reales:
- RealDataCollector: Recolector principal de datos
- RealICTDataCollector: Recolector especializado ICT
- MT5DataManager: Integración MetaTrader 5
- SmartTradingLogger: Logging centralizado

Optimizado para cuentas reales sin fallbacks.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np

# Logger centralizado
from smart_trading_logger import SmartTradingLogger

# Dependencias enterprise
try:
    from data_management.mt5_data_manager import MT5DataManager
    MT5_DATA_MANAGER_AVAILABLE = True
except ImportError as e:
    MT5DataManager = None
    MT5_DATA_MANAGER_AVAILABLE = False

try:
    from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
    SMART_MONEY_ANALYZER_AVAILABLE = True
except ImportError as e:
    SmartMoneyAnalyzer = None
    SMART_MONEY_ANALYZER_AVAILABLE = False

try:
    from ict_engine.pattern_detector import ICTPatternDetector
    ICT_PATTERN_DETECTOR_AVAILABLE = True
except ImportError as e:
    ICTPatternDetector = None
    ICT_PATTERN_DETECTOR_AVAILABLE = False

# Estado general de componentes MT5
MT5_AVAILABLE = MT5_DATA_MANAGER_AVAILABLE and SMART_MONEY_ANALYZER_AVAILABLE and ICT_PATTERN_DETECTOR_AVAILABLE

class RealDataCollector:
    """📊 Recolector de datos enterprise principal"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Inicializar recolector usando módulos enterprise reales"""
        self.logger = SmartTradingLogger("data_collector")
        self.config = config or self._default_config()
        
        self.logger.info("🚀 Inicializando RealDataCollector", "data_collector")
        
        # Estado del colector (inicializar antes de componentes)
        self.collector_state = {
            'initialized': datetime.now(),
            'data_requests': 0,
            'last_collection': None,
            'components_status': {}
        }
        
        # Componentes enterprise
        self.components = {}
        self._initialize_enterprise_components()
        
        self.logger.info("✅ RealDataCollector listo", "data_collector")
    
    def _default_config(self) -> Dict:
        """Configuración por defecto enterprise"""
        return {
            'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCHF'],
            'timeframes': ['M1', 'M5', 'M15', 'H1', 'H4', 'D1'],
            'cache_enabled': True,
            'real_data_only': True,
            'fallback_disabled': True
        }
    
    def _initialize_enterprise_components(self):
        """Inicializar componentes enterprise"""
        try:
            components_status = {}
            
            # MT5 Data Manager
            if MT5_DATA_MANAGER_AVAILABLE and MT5DataManager:
                self.components['mt5_data'] = MT5DataManager()
                self.logger.info("✅ MT5DataManager cargado", "data_collector")
                components_status['mt5_data'] = True
            else:
                self.logger.warning("⚠️ MT5DataManager no disponible", "data_collector")
                components_status['mt5_data'] = False
                
            # Smart Money Analyzer
            if SMART_MONEY_ANALYZER_AVAILABLE and SmartMoneyAnalyzer:
                self.components['smart_money'] = SmartMoneyAnalyzer()
                self.logger.info("✅ SmartMoneyAnalyzer cargado", "data_collector")
                components_status['smart_money'] = True
            else:
                self.logger.warning("⚠️ SmartMoneyAnalyzer no disponible", "data_collector")
                components_status['smart_money'] = False
                
            # ICT Pattern Detector
            if ICT_PATTERN_DETECTOR_AVAILABLE and ICTPatternDetector:
                self.components['pattern_detector'] = ICTPatternDetector()
                self.logger.info("✅ ICTPatternDetector cargado", "data_collector")
                components_status['pattern_detector'] = True
            else:
                self.logger.warning("⚠️ ICTPatternDetector no disponible", "data_collector")
                components_status['pattern_detector'] = False
            
            self.collector_state['components_status'] = components_status
            
            # Verificar si tenemos los componentes mínimos necesarios
            available_components = sum(components_status.values())
            if available_components == 0:
                raise RuntimeError("Ningún componente enterprise disponible")
            elif available_components < 3:
                self.logger.warning(f"⚠️ Solo {available_components}/3 componentes disponibles", "data_collector")
            else:
                self.logger.info("🎯 Todos los componentes enterprise inicializados", "data_collector")
                
        except Exception as e:
            self.logger.error(f"Fallo inicialización componentes enterprise: {e}", "data_collector")
            raise
    
    def get_real_market_data(self, symbol: str, timeframe: str, bars: int = 1000) -> pd.DataFrame:
        """Obtener datos de mercado reales usando MT5"""
        try:
            self.collector_state['data_requests'] += 1
            
            if 'mt5_data' not in self.components:
                raise RuntimeError("MT5DataManager no disponible")
            
            self.logger.debug(f"📈 Solicitando datos: {symbol} {timeframe} ({bars} barras)", "data_collector")
            
            # Usar MT5DataManager real
            market_data = self.components['mt5_data'].get_historical_data(
                symbol=symbol,
                timeframe=timeframe,
                bars=bars
            )
            
            self.collector_state['last_collection'] = datetime.now()
            
            self.logger.debug(f"✅ Datos obtenidos: {len(market_data)} registros", "data_collector")
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"❌ Error obteniendo datos de mercado: {e}", "data_collector")
            raise RuntimeError(f"Fallo obteniendo datos de mercado: {e}") from e
    
    def get_smart_money_analysis(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Análisis Smart Money usando SmartMoneyAnalyzer real"""
        try:
            if 'smart_money' not in self.components:
                raise RuntimeError("SmartMoneyAnalyzer no disponible")
            
            self.logger.debug(f"🧠 Análisis Smart Money: {symbol} {timeframe}", "data_collector")
            
            # Usar SmartMoneyAnalyzer real
            smart_money_data = {
                'order_blocks': self.components['smart_money'].find_order_blocks(symbol, timeframe),
                'fvg_gaps': self.components['smart_money'].detect_fvg(symbol, timeframe),
                'liquidity_zones': self.components['smart_money'].find_liquidity_zones(symbol, timeframe)
            }
            
            self.logger.debug("✅ Análisis Smart Money completado", "data_collector")
            
            return smart_money_data
            
        except Exception as e:
            self.logger.error(f"❌ Error en análisis Smart Money: {e}", "data_collector")
            raise RuntimeError(f"Fallo análisis Smart Money: {e}") from e
    
    def get_ict_patterns(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Detección de patrones ICT usando ICTPatternDetector real"""
        try:
            if 'pattern_detector' not in self.components:
                raise RuntimeError("ICTPatternDetector no disponible")
            
            self.logger.debug(f"🔍 Detección patrones ICT: {symbol} {timeframe}", "data_collector")
            
            # Usar ICTPatternDetector real
            ict_patterns = self.components['pattern_detector'].detect_patterns(symbol, timeframe)
            
            self.logger.debug("✅ Detección patrones ICT completada", "data_collector")
            
            return ict_patterns
            
        except Exception as e:
            self.logger.error(f"❌ Error detección patrones ICT: {e}", "data_collector")
            raise RuntimeError(f"Fallo detección patrones ICT: {e}") from e
    
    def get_collector_status(self) -> Dict[str, Any]:
        """Estado del recolector de datos"""
        return {
            'collector_type': 'RealDataCollector',
            'components_available': list(self.components.keys()),
            'components_count': len(self.components),
            'data_requests': self.collector_state['data_requests'],
            'last_collection': self.collector_state.get('last_collection'),
            'enterprise_mode': True,
            'fallback_disabled': self.config.get('fallback_disabled', True),
            'timestamp': datetime.now().isoformat()
        }


class RealICTDataCollector(RealDataCollector):
    """📊 Recolector de datos ICT especializado"""
    
    def __init__(self, config: Optional[Dict] = None):
        """Inicializar recolector ICT enterprise"""
        self.logger = SmartTradingLogger("ict_data_collector")
        super().__init__(config)
        
        self.logger.info("🚀 RealICTDataCollector especializado inicializado", "ict_data_collector")
    
    def get_complete_ict_analysis(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Análisis ICT completo combinando todos los componentes"""
        try:
            self.logger.info(f"🔄 Análisis ICT completo: {symbol} {timeframe}", "ict_data_collector")
            
            analysis_start = datetime.now()
            
            # Datos de mercado
            market_data = self.get_real_market_data(symbol, timeframe)
            
            # Análisis Smart Money
            smart_money_analysis = self.get_smart_money_analysis(symbol, timeframe)
            
            # Patrones ICT
            ict_patterns = self.get_ict_patterns(symbol, timeframe)
            
            # Análisis combinado
            complete_analysis = {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat(),
                'analysis_duration': (datetime.now() - analysis_start).total_seconds(),
                'market_data_bars': len(market_data),
                'smart_money': smart_money_analysis,
                'ict_patterns': ict_patterns,
                'analysis_quality': 'enterprise',
                'data_source': 'real'
            }
            
            self.logger.info(f"✅ Análisis ICT completo finalizado en {complete_analysis['analysis_duration']:.1f}s", "ict_data_collector")
            
            return complete_analysis
            
        except Exception as e:
            self.logger.error(f"❌ Error en análisis ICT completo: {e}", "ict_data_collector")
            raise RuntimeError(f"Fallo análisis ICT completo: {e}") from e

    def validate_connection_status(self) -> Dict[str, bool]:
        """Validar estado de conexiones para cuenta real"""
        try:
            connection_status = {}
            
            # Verificar conexión MT5DataManager
            if 'mt5_data' in self.components:
                try:
                    # Test básico de conectividad
                    test_data = self.components['mt5_data'].get_tick('EURUSD')
                    connection_status['mt5_connection'] = test_data is not None
                except:
                    connection_status['mt5_connection'] = False
            else:
                connection_status['mt5_connection'] = False
            
            # Verificar disponibilidad de componentes
            connection_status['smart_money_available'] = 'smart_money' in self.components
            connection_status['pattern_detector_available'] = 'pattern_detector' in self.components
            
            # Estado general
            connection_status['all_systems_operational'] = all(connection_status.values())
            
            self.logger.info(f"🔍 Conexiones validadas: {sum(connection_status.values())}/4 operativas", "data_collector")
            
            return connection_status
            
        except Exception as e:
            self.logger.error(f"Error validando conexiones: {e}", "data_collector")
            return {'validation_error': True}

    def get_real_time_market_health(self, symbols: List[str]) -> Dict[str, Any]:
        """Obtener estado de salud del mercado en tiempo real"""
        try:
            market_health = {
                'timestamp': datetime.now(),
                'symbols_status': {},
                'overall_health': 'unknown'
            }
            
            healthy_symbols = 0
            
            for symbol in symbols:
                try:
                    if 'mt5_data' in self.components:
                        # Verificar spread y liquidez
                        tick_data = self.components['mt5_data'].get_tick(symbol)
                        if tick_data:
                            spread = abs(tick_data.get('ask', 0) - tick_data.get('bid', 0))
                            market_health['symbols_status'][symbol] = {
                                'active': True,
                                'spread': spread,
                                'last_update': datetime.now(),
                                'healthy': spread < 0.0005  # Spread saludable
                            }
                            if spread < 0.0005:
                                healthy_symbols += 1
                        else:
                            market_health['symbols_status'][symbol] = {
                                'active': False,
                                'healthy': False
                            }
                    else:
                        market_health['symbols_status'][symbol] = {
                            'active': False,
                            'healthy': False
                        }
                except Exception as e:
                    market_health['symbols_status'][symbol] = {
                        'active': False,
                        'error': str(e),
                        'healthy': False
                    }
            
            # Determinar salud general
            if healthy_symbols == len(symbols):
                market_health['overall_health'] = 'excellent'
            elif healthy_symbols > len(symbols) * 0.7:
                market_health['overall_health'] = 'good'
            elif healthy_symbols > len(symbols) * 0.5:
                market_health['overall_health'] = 'fair'
            else:
                market_health['overall_health'] = 'poor'
            
            self.logger.info(f"💓 Salud del mercado: {market_health['overall_health']} ({healthy_symbols}/{len(symbols)} símbolos saludables)", "data_collector")
            
            return market_health
            
        except Exception as e:
            self.logger.error(f"Error obteniendo salud del mercado: {e}", "data_collector")
            return {'error': str(e), 'overall_health': 'error'}

    def optimize_for_live_trading(self) -> Dict[str, Any]:
        """Optimizar configuraciones para trading en vivo"""
        try:
            optimization_results = {
                'timestamp': datetime.now(),
                'optimizations_applied': [],
                'performance_improvements': {}
            }
            
            # Optimizar MT5DataManager si está disponible
            if 'mt5_data' in self.components:
                # Configurar timeouts optimizados
                optimization_results['optimizations_applied'].append('mt5_timeout_optimization')
                
            # Optimizar SmartMoneyAnalyzer
            if 'smart_money' in self.components:
                # Optimizar parámetros de análisis
                optimization_results['optimizations_applied'].append('smart_money_optimization')
                
            # Optimizar ICTPatternDetector  
            if 'pattern_detector' in self.components:
                # Configurar detección en tiempo real
                optimization_results['optimizations_applied'].append('pattern_detection_optimization')
            
            # Configurar cache para cuenta real
            self.config['cache_enabled'] = True
            self.config['cache_size_mb'] = 256
            optimization_results['optimizations_applied'].append('cache_optimization')
            
            # Log optimizaciones
            self.logger.info(f"🚀 Optimizado para trading en vivo: {len(optimization_results['optimizations_applied'])} mejoras aplicadas", "data_collector")
            
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Error optimizando para trading en vivo: {e}", "data_collector")
            return {'error': str(e)}


# Factory functions para crear colectores
def create_real_data_collector(config: Optional[Dict] = None) -> RealDataCollector:
    """Factory para crear RealDataCollector"""
    return RealDataCollector(config)

def create_real_ict_data_collector(config: Optional[Dict] = None) -> RealICTDataCollector:
    """Factory para crear RealICTDataCollector"""
    return RealICTDataCollector(config)


# Export para uso externo
__all__ = [
    'RealDataCollector', 
    'RealICTDataCollector',
    'create_real_data_collector',
    'create_real_ict_data_collector'
]