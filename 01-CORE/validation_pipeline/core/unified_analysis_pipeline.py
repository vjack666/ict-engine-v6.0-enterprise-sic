"""
🎯 UNIFIED ANALYSIS PIPELINE - ICT ENGINE v6.0 ENTERPRISE
========================================================

Pipeline unificado que conecta dashboard tiempo real con backtesting histórico
usando EXACTAMENTE los mismos componentes centrales del sistema.

Módulos Centrales Integrados:
- Smart Trading Logger (SLUC v2.0+) 
- MT5DataManager + MT5 Connection
- SmartMoneyAnalyzer
- POI System + Pattern Detection
- UnifiedMemorySystem
- ICT Engine Components
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path

# Agregar paths del sistema
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# IMPORTACIONES CENTRALES DEL SISTEMA
try:
    # 📊 Dashboard Components (mismo que está funcionando)
    from data.data_collector import RealDataCollector
    from core.dashboard_engine import DashboardEngine
    
    # 🏦 MT5 Central System
    from utils.mt5_data_manager import get_mt5_manager, MT5DataManager
    
    # 💰 Smart Money & Pattern Detection
    from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
    from ict_engine.pattern_detector import ICTPatternDetector
    from poi_system import POISystem
    
    # 🧠 Memory & Core Systems
    from data_management.unified_memory_system import UnifiedMemorySystem
    
    # 📝 Logging Central (SLUC)
    from smart_trading_logger import SmartTradingLogger
    
    print("✅ [PIPELINE] Todos los módulos centrales importados correctamente")
    
except ImportError as e:
    print(f"⚠️ [PIPELINE] Error importando módulos: {e}")
    print("🔧 [PIPELINE] Continuando con imports alternativos...")


class UnifiedAnalysisPipeline:
    """
    🔄 Pipeline Unificado Dashboard ↔ Backtesting
    
    Garantiza uso de EXACTAMENTE los mismos componentes
    entre análisis tiempo real (dashboard) y análisis histórico (backtesting).
    
    Componentes Centrales Unificados:
    - MT5DataManager: Datos reales MT5
    - SmartMoneyAnalyzer: Análisis institucional
    - ICTPatternDetector: Patrones ICT
    - POISystem: Points of Interest
    - UnifiedMemorySystem: Memoria de trader
    - SmartTradingLogger: Logging centralizado
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializar pipeline con componentes centrales del sistema
        """
        self.config = config or self._default_config()
        self.logger = SmartTradingLogger()
        
        # Log inicio
        self.logger.log("INFO", "🚀 Inicializando UnifiedAnalysisPipeline", 
                       module="validation_pipeline", category="system")
        
        # Inicializar componentes centrales
        self._initialize_core_components()
        self._initialize_dashboard_components()
        self._initialize_analysis_components()
        
        # Estado del pipeline
        self.pipeline_state = {
            'initialized': datetime.now(),
            'live_analyses': [],
            'historical_analyses': [],
            'comparisons': []
        }
        
        self.logger.log("INFO", "✅ UnifiedAnalysisPipeline inicializado correctamente", 
                       module="validation_pipeline", category="system")
    
    def _default_config(self) -> Dict:
        """Configuración por defecto del pipeline"""
        return {
            'symbols': ['EURUSD', 'GBPUSD', 'XAUUSD'],
            'timeframes': ['M15', 'H1', 'H4'],
            'validation_periods': {
                'short': 7,    # días
                'medium': 30,  # días  
                'long': 90     # días
            },
            'accuracy_threshold': 0.95,  # 95% accuracy requerida
            'timing_threshold': 30,      # 30s max diferencia timing
            'confidence_threshold': 0.9   # 90% correlación confidence
        }
    
    def _initialize_core_components(self):
        """
        🏗️ Inicializar componentes centrales del sistema
        MISMOS que usa el dashboard funcionando
        """
        try:
            # 🏦 MT5 Manager Central
            self.mt5_manager = get_mt5_manager()
            self.logger.log("INFO", "✅ MT5DataManager inicializado", 
                           module="validation_pipeline", category="mt5")
            
            # 🧠 Memory System Central
            self.memory_system = UnifiedMemorySystem()
            self.logger.log("INFO", "✅ UnifiedMemorySystem inicializado", 
                           module="validation_pipeline", category="memory")
            
        except Exception as e:
            self.logger.log("ERROR", f"❌ Error inicializando componentes centrales: {e}", 
                           module="validation_pipeline", category="system")
            raise
    
    def _initialize_dashboard_components(self):
        """
        📊 Inicializar componentes del dashboard
        EXACTAMENTE los mismos que están funcionando
        """
        try:
            # 📊 Dashboard Data Collector (MISMO que funciona)
            self.data_collector = RealDataCollector()
            self.dashboard_engine = DashboardEngine()
            
            self.logger.log("INFO", "✅ Dashboard components inicializados", 
                           module="validation_pipeline", category="dashboard")
            
            # Acceso directo a componentes dashboard
            if hasattr(self.data_collector, 'components'):
                self.smart_money_dashboard = self.data_collector.components.get('smart_money')
                self.pattern_detector_dashboard = getattr(self.data_collector, 'pattern_detector', None)
                
                self.logger.log("INFO", f"✅ Dashboard components accesibles: {list(self.data_collector.components.keys())}", 
                               module="validation_pipeline", category="dashboard")
            
        except Exception as e:
            self.logger.log("ERROR", f"❌ Error inicializando dashboard components: {e}", 
                           module="validation_pipeline", category="dashboard")
            # Continuar sin dashboard components
            self.data_collector = None
            self.dashboard_engine = None
    
    def _initialize_analysis_components(self):
        """
        🔍 Inicializar componentes de análisis
        Para backtesting histórico usando MISMOS componentes
        """
        try:
            # 💰 Smart Money Analyzer (MISMO que dashboard)
            if self.smart_money_dashboard:
                self.smart_money_historical = self.smart_money_dashboard
            else:
                self.smart_money_historical = SmartMoneyAnalyzer()
            
            # 🎯 Pattern Detector (MISMO que dashboard)  
            if self.pattern_detector_dashboard:
                self.pattern_detector_historical = self.pattern_detector_dashboard
            else:
                self.pattern_detector_historical = ICTPatternDetector()
            
            # 📍 POI System
            self.poi_system = POISystem()
            
            self.logger.log("INFO", "✅ Analysis components inicializados", 
                           module="validation_pipeline", category="analysis")
            
        except Exception as e:
            self.logger.log("ERROR", f"❌ Error inicializando analysis components: {e}", 
                           module="validation_pipeline", category="analysis")
            raise
    
    def analyze_live(self, symbol: str, timeframe: str, candles: int = 100) -> Dict[str, Any]:
        """
        📈 Análisis en tiempo real
        USA EXACTAMENTE los mismos componentes que el dashboard
        """
        self.logger.log("INFO", f"🔄 Iniciando análisis LIVE: {symbol} {timeframe}", 
                       module="validation_pipeline", category="live_analysis")
        
        try:
            # Obtener datos en tiempo real (MISMO método que dashboard)
            if self.data_collector and hasattr(self.data_collector, 'get_real_market_data'):
                market_data = self.data_collector.get_real_market_data(symbol, timeframe, candles)
            else:
                # Fallback directo a MT5
                market_data = self.mt5_manager.get_historical_data(
                    symbol=symbol,
                    timeframe=timeframe,
                    count=candles
                )
            
            if market_data is None or len(market_data) == 0:
                self.logger.log("WARNING", f"⚠️ No hay datos para {symbol} {timeframe}", 
                               module="validation_pipeline", category="live_analysis")
                return self._empty_analysis_result('live', symbol, timeframe)
            
            # Análisis usando componentes dashboard
            live_results = self._unified_analysis(
                market_data, symbol, timeframe, mode='live'
            )
            
            # Guardar en estado pipeline
            self.pipeline_state['live_analyses'].append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'timeframe': timeframe,
                'results': live_results
            })
            
            self.logger.log("INFO", f"✅ Análisis LIVE completado: {symbol} {timeframe}", 
                           module="validation_pipeline", category="live_analysis")
            
            return live_results
            
        except Exception as e:
            self.logger.log("ERROR", f"❌ Error en análisis LIVE: {e}", 
                           module="validation_pipeline", category="live_analysis")
            return self._empty_analysis_result('live', symbol, timeframe, error=str(e))
    
    def analyze_historical(self, symbol: str, timeframe: str, 
                         start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        📊 Análisis histórico
        USA EXACTAMENTE los mismos componentes que el análisis live
        """
        self.logger.log("INFO", f"🔄 Iniciando análisis HISTÓRICO: {symbol} {timeframe} ({start_date} - {end_date})", 
                       module="validation_pipeline", category="historical_analysis")
        
        try:
            # Obtener datos históricos (MISMO MT5Manager que live)
            historical_data = self.mt5_manager.get_historical_data(
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date
            )
            
            if historical_data is None or len(historical_data) == 0:
                self.logger.log("WARNING", f"⚠️ No hay datos históricos para {symbol} {timeframe}", 
                               module="validation_pipeline", category="historical_analysis")
                return self._empty_analysis_result('historical', symbol, timeframe)
            
            # Análisis usando MISMOS componentes que live
            historical_results = self._unified_analysis(
                historical_data, symbol, timeframe, mode='historical'
            )
            
            # Guardar en estado pipeline
            self.pipeline_state['historical_analyses'].append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'timeframe': timeframe,
                'period': f"{start_date} - {end_date}",
                'results': historical_results
            })
            
            self.logger.log("INFO", f"✅ Análisis HISTÓRICO completado: {symbol} {timeframe}", 
                           module="validation_pipeline", category="historical_analysis")
            
            return historical_results
            
        except Exception as e:
            self.logger.log("ERROR", f"❌ Error en análisis HISTÓRICO: {e}", 
                           module="validation_pipeline", category="historical_analysis")
            return self._empty_analysis_result('historical', symbol, timeframe, error=str(e))
    
    def _unified_analysis(self, market_data: Any, symbol: str, timeframe: str, mode: str) -> Dict[str, Any]:
        """
        🔄 Análisis unificado usando EXACTAMENTE los mismos componentes
        para ambos modos (live y historical)
        """
        analysis_start = datetime.now()
        
        # Preparar datos (formato consistente)
        if hasattr(market_data, 'df'):
            df = market_data.df
        elif isinstance(market_data, pd.DataFrame):
            df = market_data
        else:
            df = pd.DataFrame(market_data)
        
        results = {
            'mode': mode,
            'symbol': symbol,
            'timeframe': timeframe,
            'analysis_timestamp': analysis_start,
            'data_points': len(df),
            'smart_money': {},
            'order_blocks': {},
            'fvg': {},
            'poi_analysis': {},
            'performance_metrics': {}
        }
        
        try:
            # 💰 SMART MONEY ANALYSIS (MISMO componente que dashboard)
            if self.smart_money_dashboard or self.smart_money_historical:
                analyzer = self.smart_money_dashboard or self.smart_money_historical
                
                # Stop Hunts (MISMO método que dashboard)
                stop_hunts = analyzer.detect_stop_hunts(df)
                results['smart_money']['stop_hunts'] = {
                    'count': len(stop_hunts) if isinstance(stop_hunts, list) else 0,
                    'data': stop_hunts
                }
                
                # Kill Zones (MISMO método que dashboard)
                killzones = analyzer.analyze_killzones(symbol)
                results['smart_money']['killzones'] = {
                    'active_zones': len(killzones.get('optimal_zones', [])) if isinstance(killzones, dict) else 0,
                    'data': killzones
                }
                
                # Breaker Blocks (MISMO método que dashboard)
                breakers = analyzer.find_breaker_blocks(df)
                results['smart_money']['breaker_blocks'] = {
                    'count': len(breakers.get('breaker_blocks', [])) if isinstance(breakers, dict) else 0,
                    'data': breakers
                }
            
            # 📦 ORDER BLOCKS ANALYSIS (MISMO componente que dashboard)
            if hasattr(analyzer, 'find_order_blocks'):
                order_blocks = analyzer.find_order_blocks(df)
                results['order_blocks'] = {
                    'total_blocks': len(order_blocks.get('order_blocks', [])) if isinstance(order_blocks, dict) else 0,
                    'bullish_blocks': len([ob for ob in order_blocks.get('order_blocks', []) if ob.get('type') == 'bullish']),
                    'bearish_blocks': len([ob for ob in order_blocks.get('order_blocks', []) if ob.get('type') == 'bearish']),
                    'data': order_blocks
                }
            
            # 💎 FVG ANALYSIS (MISMO componente que dashboard)
            if hasattr(analyzer, 'detect_fvg'):
                fvg_analysis = analyzer.detect_fvg(df)
                results['fvg'] = {
                    'total_fvgs': len(fvg_analysis.get('fvgs', [])) if isinstance(fvg_analysis, dict) else 0,
                    'bullish_fvgs': len([fvg for fvg in fvg_analysis.get('fvgs', []) if fvg.get('direction') == 'bullish']),
                    'bearish_fvgs': len([fvg for fvg in fvg_analysis.get('fvgs', []) if fvg.get('direction') == 'bearish']),
                    'data': fvg_analysis
                }
            
            # ⏱️ Performance Metrics
            analysis_end = datetime.now()
            results['performance_metrics'] = {
                'analysis_duration': (analysis_end - analysis_start).total_seconds(),
                'analysis_mode': mode,
                'components_used': ['smart_money', 'order_blocks', 'fvg'],
                'data_quality': 'REAL_MT5_DATA'
            }
            
            self.logger.log("INFO", f"✅ Unified analysis completado ({mode}): {symbol} {timeframe} en {results['performance_metrics']['analysis_duration']:.2f}s", 
                           module="validation_pipeline", category="analysis")
            
        except Exception as e:
            self.logger.log("ERROR", f"❌ Error en unified analysis: {e}", 
                           module="validation_pipeline", category="analysis")
            results['error'] = str(e)
        
        return results
    
    def _empty_analysis_result(self, mode: str, symbol: str, timeframe: str, error: str = None) -> Dict[str, Any]:
        """Resultado vacío para casos de error"""
        return {
            'mode': mode,
            'symbol': symbol,
            'timeframe': timeframe,
            'analysis_timestamp': datetime.now(),
            'data_points': 0,
            'smart_money': {'stop_hunts': {'count': 0}, 'killzones': {'active_zones': 0}, 'breaker_blocks': {'count': 0}},
            'order_blocks': {'total_blocks': 0, 'bullish_blocks': 0, 'bearish_blocks': 0},
            'fvg': {'total_fvgs': 0, 'bullish_fvgs': 0, 'bearish_fvgs': 0},
            'poi_analysis': {},
            'performance_metrics': {'analysis_duration': 0, 'data_quality': 'ERROR'},
            'error': error
        }
    
    def compare_analyses(self, live_result: Dict, historical_result: Dict) -> Dict[str, Any]:
        """
        🔍 Comparar resultados entre análisis live y histórico
        Generar métricas de accuracy y correlación
        """
        self.logger.log("INFO", "🔄 Iniciando comparación live vs historical", 
                       module="validation_pipeline", category="comparison")
        
        comparison_start = datetime.now()
        
        comparison = {
            'comparison_timestamp': comparison_start,
            'live_analysis': live_result.get('analysis_timestamp'),
            'historical_analysis': historical_result.get('analysis_timestamp'),
            'symbol': live_result.get('symbol'),
            'timeframe': live_result.get('timeframe'),
            'smart_money_comparison': {},
            'order_blocks_comparison': {},
            'fvg_comparison': {},
            'overall_metrics': {}
        }
        
        try:
            # 💰 Smart Money Comparison
            comparison['smart_money_comparison'] = self._compare_smart_money(
                live_result.get('smart_money', {}),
                historical_result.get('smart_money', {})
            )
            
            # 📦 Order Blocks Comparison
            comparison['order_blocks_comparison'] = self._compare_order_blocks(
                live_result.get('order_blocks', {}),
                historical_result.get('order_blocks', {})
            )
            
            # 💎 FVG Comparison
            comparison['fvg_comparison'] = self._compare_fvg(
                live_result.get('fvg', {}),
                historical_result.get('fvg', {})
            )
            
            # 📊 Overall Metrics
            comparison['overall_metrics'] = self._calculate_overall_metrics(comparison)
            
            # Guardar comparación
            self.pipeline_state['comparisons'].append(comparison)
            
            comparison_end = datetime.now()
            comparison['comparison_duration'] = (comparison_end - comparison_start).total_seconds()
            
            self.logger.log("INFO", f"✅ Comparación completada en {comparison['comparison_duration']:.2f}s", 
                           module="validation_pipeline", category="comparison")
            
        except Exception as e:
            self.logger.log("ERROR", f"❌ Error en comparación: {e}", 
                           module="validation_pipeline", category="comparison")
            comparison['error'] = str(e)
        
        return comparison
    
    def _compare_smart_money(self, live_sm: Dict, historical_sm: Dict) -> Dict[str, Any]:
        """Comparar resultados Smart Money"""
        return {
            'stop_hunts': {
                'live_count': live_sm.get('stop_hunts', {}).get('count', 0),
                'historical_count': historical_sm.get('stop_hunts', {}).get('count', 0),
                'accuracy': self._calculate_accuracy(
                    live_sm.get('stop_hunts', {}).get('count', 0),
                    historical_sm.get('stop_hunts', {}).get('count', 0)
                )
            },
            'killzones': {
                'live_zones': live_sm.get('killzones', {}).get('active_zones', 0),
                'historical_zones': historical_sm.get('killzones', {}).get('active_zones', 0),
                'accuracy': self._calculate_accuracy(
                    live_sm.get('killzones', {}).get('active_zones', 0),
                    historical_sm.get('killzones', {}).get('active_zones', 0)
                )
            },
            'breaker_blocks': {
                'live_count': live_sm.get('breaker_blocks', {}).get('count', 0),
                'historical_count': historical_sm.get('breaker_blocks', {}).get('count', 0),
                'accuracy': self._calculate_accuracy(
                    live_sm.get('breaker_blocks', {}).get('count', 0),
                    historical_sm.get('breaker_blocks', {}).get('count', 0)
                )
            }
        }
    
    def _compare_order_blocks(self, live_ob: Dict, historical_ob: Dict) -> Dict[str, Any]:
        """Comparar resultados Order Blocks"""
        return {
            'total_blocks': {
                'live_count': live_ob.get('total_blocks', 0),
                'historical_count': historical_ob.get('total_blocks', 0),
                'accuracy': self._calculate_accuracy(
                    live_ob.get('total_blocks', 0),
                    historical_ob.get('total_blocks', 0)
                )
            },
            'bullish_blocks': {
                'live_count': live_ob.get('bullish_blocks', 0),
                'historical_count': historical_ob.get('bullish_blocks', 0),
                'accuracy': self._calculate_accuracy(
                    live_ob.get('bullish_blocks', 0),
                    historical_ob.get('bullish_blocks', 0)
                )
            },
            'bearish_blocks': {
                'live_count': live_ob.get('bearish_blocks', 0),
                'historical_count': historical_ob.get('bearish_blocks', 0),
                'accuracy': self._calculate_accuracy(
                    live_ob.get('bearish_blocks', 0),
                    historical_ob.get('bearish_blocks', 0)
                )
            }
        }
    
    def _compare_fvg(self, live_fvg: Dict, historical_fvg: Dict) -> Dict[str, Any]:
        """Comparar resultados FVG"""
        return {
            'total_fvgs': {
                'live_count': live_fvg.get('total_fvgs', 0),
                'historical_count': historical_fvg.get('total_fvgs', 0),
                'accuracy': self._calculate_accuracy(
                    live_fvg.get('total_fvgs', 0),
                    historical_fvg.get('total_fvgs', 0)
                )
            },
            'bullish_fvgs': {
                'live_count': live_fvg.get('bullish_fvgs', 0),
                'historical_count': historical_fvg.get('bullish_fvgs', 0),
                'accuracy': self._calculate_accuracy(
                    live_fvg.get('bullish_fvgs', 0),
                    historical_fvg.get('bullish_fvgs', 0)
                )
            },
            'bearish_fvgs': {
                'live_count': live_fvg.get('bearish_fvgs', 0),
                'historical_count': historical_fvg.get('bearish_fvgs', 0),
                'accuracy': self._calculate_accuracy(
                    live_fvg.get('bearish_fvgs', 0),
                    historical_fvg.get('bearish_fvgs', 0)
                )
            }
        }
    
    def _calculate_accuracy(self, live_value: int, historical_value: int) -> float:
        """Calcular accuracy entre valores live y historical"""
        if historical_value == 0:
            return 1.0 if live_value == 0 else 0.0
        
        difference = abs(live_value - historical_value)
        accuracy = max(0.0, 1.0 - (difference / historical_value))
        return round(accuracy, 3)
    
    def _calculate_overall_metrics(self, comparison: Dict) -> Dict[str, float]:
        """Calcular métricas generales de la comparación"""
        accuracies = []
        
        # Recopilar todas las accuracies
        for category in ['smart_money_comparison', 'order_blocks_comparison', 'fvg_comparison']:
            if category in comparison:
                for subcategory, data in comparison[category].items():
                    if isinstance(data, dict) and 'accuracy' in data:
                        accuracies.append(data['accuracy'])
        
        if not accuracies:
            return {'overall_accuracy': 0.0, 'categories_analyzed': 0}
        
        return {
            'overall_accuracy': round(np.mean(accuracies), 3),
            'categories_analyzed': len(accuracies),
            'min_accuracy': round(min(accuracies), 3),
            'max_accuracy': round(max(accuracies), 3),
            'accuracy_std': round(np.std(accuracies), 3)
        }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Obtener estado actual del pipeline"""
        return {
            'initialized': self.pipeline_state['initialized'],
            'live_analyses_count': len(self.pipeline_state['live_analyses']),
            'historical_analyses_count': len(self.pipeline_state['historical_analyses']),
            'comparisons_count': len(self.pipeline_state['comparisons']),
            'components_status': {
                'mt5_manager': self.mt5_manager is not None,
                'data_collector': self.data_collector is not None,
                'smart_money_analyzer': self.smart_money_dashboard is not None,
                'pattern_detector': self.pattern_detector_dashboard is not None,
                'memory_system': self.memory_system is not None
            },
            'last_update': datetime.now()
        }


# Función de utilidad para crear instancia global
_pipeline_instance = None

def get_unified_pipeline(config: Optional[Dict] = None) -> UnifiedAnalysisPipeline:
    """
    Obtener instancia global del pipeline unificado
    """
    global _pipeline_instance
    
    if _pipeline_instance is None:
        _pipeline_instance = UnifiedAnalysisPipeline(config)
    
    return _pipeline_instance


if __name__ == "__main__":
    # Test básico del pipeline
    print("🚀 Testing UnifiedAnalysisPipeline...")
    
    try:
        pipeline = UnifiedAnalysisPipeline()
        status = pipeline.get_pipeline_status()
        
        print(f"✅ Pipeline inicializado correctamente")
        print(f"📊 Estado: {status['components_status']}")
        
        # Test análisis live
        live_result = pipeline.analyze_live('EURUSD', 'H1', 50)
        print(f"📈 Análisis live completado: {live_result.get('data_points', 0)} puntos de datos")
        
    except Exception as e:
        print(f"❌ Error en testing: {e}")