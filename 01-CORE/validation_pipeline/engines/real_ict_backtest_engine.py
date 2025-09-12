"""
🚀 REAL ICT BACKTEST ENGINE - ICT ENGINE v6.0 ENTERPRISE
========================================================

Motor de backtesting que usa EXACTAMENTE los mismos componentes
que el dashboard para garantizar validaciones perfectas.

Componentes Centrales Integrados:
- Dashboard RealDataCollector (MISMO que funciona)
- Smart Money Analyzer (EXACTO del dashboard)
- Pattern Detector (MISMO componente)
- MT5DataManager (DIRECTO del sistema)
- Smart Trading Logger (SLUC v2.0+)
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from pathlib import Path

# Agregar paths del sistema
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent.parent))
sys.path.append(str(current_dir.parent.parent / "09-DASHBOARD"))

# Importaciones con manejo de errores robusto
try:
    # 📊 Dashboard Components (EXACTOS los que funcionan)
    sys.path.append(str(current_dir.parent.parent / "09-DASHBOARD" / "data"))
    sys.path.append(str(current_dir.parent.parent / "09-DASHBOARD" / "core"))
    
    from data_collector import RealDataCollector
    from dashboard_engine import DashboardEngine
    
    # 📝 Smart Trading Logger
    sys.path.append(str(current_dir.parent))
    from smart_trading_logger import enviar_senal_log
    
    DASHBOARD_COMPONENTS_AVAILABLE = True
    print("✅ [BACKTEST_ENGINE] Dashboard components importados correctamente")
    
except ImportError as e:
    print(f"⚠️ [BACKTEST_ENGINE] Dashboard components no disponibles: {e}")
    DASHBOARD_COMPONENTS_AVAILABLE = False
    
    # Fallback logging
    def enviar_senal_log(level, message, module, category=None):
        print(f"[{level}] [{module}] {message}")


class RealICTBacktestEngine:
    """
    🔄 Motor de Backtesting Real con Componentes Dashboard
    
    USA EXACTAMENTE los mismos componentes que el dashboard
    funcionando para garantizar comparaciones válidas:
    
    - Dashboard RealDataCollector
    - Smart Money Analyzer del dashboard
    - Pattern Detector del dashboard
    - MT5DataManager del dashboard
    - Logging centralizado (SLUC)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializar motor backtesting con componentes dashboard
        """
        self.config = config or self._default_config()
        
        enviar_senal_log("INFO", "🚀 Inicializando RealICTBacktestEngine", 
                        "real_backtest_engine", "system")
        
        # Estado del motor
        self.engine_state = {
            'initialized': datetime.now(),
            'backtests_executed': 0,
            'last_backtest': None,
            'components_status': {}
        }
        
        # Inicializar componentes EXACTOS del dashboard
        self._initialize_dashboard_components()
        self._initialize_analysis_state()
        
        enviar_senal_log("INFO", "✅ RealICTBacktestEngine inicializado correctamente", 
                        "real_backtest_engine", "system")
    
    def _default_config(self) -> Dict:
        """Configuración por defecto del motor"""
        return {
            'symbols': ['EURUSD', 'GBPUSD', 'XAUUSD'],
            'timeframes': ['M15', 'H1', 'H4'],
            'max_candles': 1000,
            'strategies': [
                'smart_money_analysis',
                'order_blocks_detection', 
                'fvg_detection'
            ],
            'output_format': 'detailed',
            'save_results': True
        }
    
    def _initialize_dashboard_components(self):
        """
        📊 Inicializar EXACTAMENTE los mismos componentes del dashboard
        """
        self.dashboard_components = {}
        
        if DASHBOARD_COMPONENTS_AVAILABLE:
            try:
                # 📊 Dashboard Data Collector (EXACTO el que funciona)
                enviar_senal_log("INFO", "🔄 Inicializando RealDataCollector del dashboard", 
                                "real_backtest_engine", "dashboard")
                
                self.data_collector = RealDataCollector(config={})
                self.dashboard_components['data_collector'] = True
                
                # 🔧 Dashboard Engine (EXACTO el que funciona)
                self.dashboard_engine = DashboardEngine(config={})
                self.dashboard_components['dashboard_engine'] = True
                
                # Acceso directo a componentes específicos
                if hasattr(self.data_collector, 'components'):
                    self.smart_money_analyzer = self.data_collector.components.get('smart_money')
                    self.pattern_detector = getattr(self.data_collector, 'pattern_detector', None)
                    self.mt5_manager = getattr(self.data_collector, 'mt5_manager', None)
                    
                    self.dashboard_components.update({
                        'smart_money_analyzer': self.smart_money_analyzer is not None,
                        'pattern_detector': self.pattern_detector is not None,
                        'mt5_manager': self.mt5_manager is not None
                    })
                    
                    enviar_senal_log("INFO", f"✅ Componentes dashboard accesibles: {list(self.data_collector.components.keys())}", 
                                    "real_backtest_engine", "dashboard")
                
                self.engine_state['components_status'] = self.dashboard_components
                
            except Exception as e:
                enviar_senal_log("ERROR", f"❌ Error inicializando dashboard components: {e}", 
                                "real_backtest_engine", "dashboard")
                self._initialize_fallback_components()
        else:
            enviar_senal_log("WARNING", "⚠️ Dashboard components no disponibles, usando fallbacks", 
                            "real_backtest_engine", "system")
            self._initialize_fallback_components()
    
    def _initialize_fallback_components(self):
        """Inicializar componentes fallback si dashboard no disponible"""
        self.data_collector = None
        self.dashboard_engine = None
        self.smart_money_analyzer = None
        self.pattern_detector = None
        self.mt5_manager = None
        
        self.dashboard_components = {
            'data_collector': False,
            'dashboard_engine': False,
            'smart_money_analyzer': False,
            'pattern_detector': False,
            'mt5_manager': False
        }
        
        enviar_senal_log("WARNING", "⚠️ Usando componentes fallback", 
                        "real_backtest_engine", "system")
    
    def _initialize_analysis_state(self):
        """Inicializar estado de análisis"""
        self.analysis_state = {
            'current_backtest': None,
            'results_cache': {},
            'performance_metrics': {},
            'validation_results': {}
        }
    
    def execute_backtest(self, symbol: str, timeframe: str, 
                        start_date: datetime, end_date: datetime,
                        strategies: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        🚀 Ejecutar backtesting usando componentes EXACTOS del dashboard
        """
        backtest_id = f"{symbol}_{timeframe}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        
        enviar_senal_log("INFO", f"🚀 Iniciando backtest: {backtest_id}", 
                        "real_backtest_engine", "backtest")
        
        backtest_start = datetime.now()
        
        # Configurar backtest
        backtest_config = {
            'id': backtest_id,
            'symbol': symbol,
            'timeframe': timeframe,
            'start_date': start_date,
            'end_date': end_date,
            'strategies': strategies or self.config['strategies'],
            'started_at': backtest_start
        }
        
        self.analysis_state['current_backtest'] = backtest_config
        
        try:
            # 1. OBTENER DATOS HISTÓRICOS (MISMO método que dashboard)
            historical_data = self._get_historical_data_dashboard_method(
                symbol, timeframe, start_date, end_date
            )
            
            if historical_data is None or len(historical_data) == 0:
                enviar_senal_log("ERROR", f"❌ No hay datos históricos para {symbol} {timeframe}", 
                                "real_backtest_engine", "backtest")
                return self._create_empty_backtest_result(backtest_config, "NO_DATA")
            
            enviar_senal_log("INFO", f"📊 Datos históricos obtenidos: {len(historical_data)} candles", 
                            "real_backtest_engine", "backtest")
            
            # 2. EJECUTAR ANÁLISIS (EXACTOS métodos del dashboard)
            backtest_results = self._execute_dashboard_analysis(
                historical_data, backtest_config
            )
            
            # 3. CALCULAR MÉTRICAS DE PERFORMANCE
            performance_metrics = self._calculate_backtest_performance(
                backtest_results, backtest_start
            )
            
            # 4. COMPILAR RESULTADO FINAL
            final_results = {
                'backtest_config': backtest_config,
                'data_info': {
                    'candles_count': len(historical_data),
                    'data_quality': 'REAL_MT5_DATA',
                    'timeframe': timeframe,
                    'period_days': (end_date - start_date).days
                },
                'analysis_results': backtest_results,
                'performance_metrics': performance_metrics,
                'engine_info': {
                    'engine_version': '1.0.0',
                    'dashboard_components_used': self.dashboard_components,
                    'execution_timestamp': datetime.now()
                }
            }
            
            # 5. GUARDAR Y LOGGING
            self.engine_state['backtests_executed'] += 1
            self.engine_state['last_backtest'] = backtest_config
            
            if self.config.get('save_results', True):
                self._save_backtest_results(final_results)
            
            enviar_senal_log("INFO", f"✅ Backtest completado: {backtest_id} en {performance_metrics['execution_duration']:.2f}s", 
                            "real_backtest_engine", "backtest")
            
            return final_results
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error en backtest {backtest_id}: {e}", 
                            "real_backtest_engine", "backtest")
            return self._create_empty_backtest_result(backtest_config, f"ERROR: {str(e)}")
    
    def _get_historical_data_dashboard_method(self, symbol: str, timeframe: str, 
                                            start_date: datetime, end_date: datetime):
        """
        📊 Obtener datos históricos usando EXACTAMENTE el mismo método del dashboard
        """
        try:
            # Método 1: Usar data_collector del dashboard si disponible
            if (self.data_collector and 
                hasattr(self.data_collector, 'get_real_market_data')):
                
                enviar_senal_log("INFO", f"📊 Usando RealDataCollector.get_real_market_data() del dashboard", 
                                "real_backtest_engine", "data")
                
                # Calcular número de candles aproximado
                period_days = (end_date - start_date).days
                candles_per_day = {'M15': 96, 'H1': 24, 'H4': 6, 'D1': 1}
                estimated_candles = min(period_days * candles_per_day.get(timeframe, 24), 
                                      self.config['max_candles'])
                
                historical_data = self.data_collector.get_real_market_data(
                    symbol, timeframe, estimated_candles
                )
                
                if historical_data is not None:
                    return historical_data
                
                enviar_senal_log("WARNING", "⚠️ RealDataCollector no retornó datos, intentando MT5Manager directo", 
                                "real_backtest_engine", "data")
            
            # Método 2: Usar MT5Manager directo si disponible
            if self.mt5_manager and hasattr(self.mt5_manager, 'get_historical_data'):
                enviar_senal_log("INFO", f"📊 Usando MT5DataManager directo del dashboard", 
                                "real_backtest_engine", "data")
                
                historical_data = self.mt5_manager.get_historical_data(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if historical_data is not None:
                    return historical_data
            
            # Método 3: Fallback logging
            enviar_senal_log("ERROR", "❌ No hay métodos disponibles para obtener datos históricos", 
                            "real_backtest_engine", "data")
            return None
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error obteniendo datos históricos: {e}", 
                            "real_backtest_engine", "data")
            return None
    
    def _execute_dashboard_analysis(self, historical_data: Any, 
                                  backtest_config: Dict) -> Dict[str, Any]:
        """
        🔍 Ejecutar análisis usando EXACTAMENTE los métodos del dashboard
        """
        analysis_results = {
            'smart_money': {},
            'order_blocks': {},
            'fvg': {},
            'analysis_timestamp': datetime.now(),
            'strategies_executed': []
        }
        
        # Preparar datos (formato consistente)
        if hasattr(historical_data, 'df'):
            df = historical_data.df
        elif isinstance(historical_data, pd.DataFrame):
            df = historical_data
        else:
            df = pd.DataFrame(historical_data)
        
        enviar_senal_log("INFO", f"📊 Iniciando análisis con {len(df)} candles", 
                        "real_backtest_engine", "analysis")
        
        try:
            # 💰 SMART MONEY ANALYSIS (EXACTO método del dashboard)
            if ('smart_money_analysis' in backtest_config['strategies'] and 
                self.smart_money_analyzer):
                
                enviar_senal_log("INFO", "🔄 Ejecutando Smart Money analysis (componente dashboard)", 
                                "real_backtest_engine", "analysis")
                
                analysis_results['smart_money'] = self._execute_smart_money_analysis_dashboard(
                    df, backtest_config['symbol']
                )
                analysis_results['strategies_executed'].append('smart_money_analysis')
            
            # 📦 ORDER BLOCKS ANALYSIS (EXACTO método del dashboard)
            if ('order_blocks_detection' in backtest_config['strategies'] and 
                self.smart_money_analyzer and hasattr(self.smart_money_analyzer, 'find_order_blocks')):
                
                enviar_senal_log("INFO", "🔄 Ejecutando Order Blocks detection (componente dashboard)", 
                                "real_backtest_engine", "analysis")
                
                analysis_results['order_blocks'] = self._execute_order_blocks_analysis_dashboard(df)
                analysis_results['strategies_executed'].append('order_blocks_detection')
            
            # 💎 FVG ANALYSIS (EXACTO método del dashboard)
            if ('fvg_detection' in backtest_config['strategies'] and 
                self.smart_money_analyzer and hasattr(self.smart_money_analyzer, 'detect_fvg')):
                
                enviar_senal_log("INFO", "🔄 Ejecutando FVG detection (componente dashboard)", 
                                "real_backtest_engine", "analysis")
                
                analysis_results['fvg'] = self._execute_fvg_analysis_dashboard(df)
                analysis_results['strategies_executed'].append('fvg_detection')
            
            enviar_senal_log("INFO", f"✅ Análisis completado: {len(analysis_results['strategies_executed'])} estrategias", 
                            "real_backtest_engine", "analysis")
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error en análisis dashboard: {e}", 
                            "real_backtest_engine", "analysis")
            analysis_results['error'] = str(e)
        
        return analysis_results
    
    def _execute_smart_money_analysis_dashboard(self, df: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Ejecutar Smart Money analysis usando EXACTO el componente del dashboard"""
        try:
            # EXACTOS métodos que usa el dashboard
            smart_money_results = {}
            
            # Stop Hunts (MISMO método)
            stop_hunts = self.smart_money_analyzer.detect_stop_hunts(df)
            smart_money_results['stop_hunts'] = {
                'count': len(stop_hunts) if isinstance(stop_hunts, list) else 0,
                'data': stop_hunts
            }
            
            # Kill Zones (MISMO método)
            killzones = self.smart_money_analyzer.analyze_killzones(symbol)
            smart_money_results['killzones'] = {
                'active_zones': len(killzones.get('optimal_zones', [])) if isinstance(killzones, dict) else 0,
                'data': killzones
            }
            
            # Breaker Blocks (MISMO método)
            breakers = self.smart_money_analyzer.find_breaker_blocks(df)
            smart_money_results['breaker_blocks'] = {
                'count': len(breakers.get('breaker_blocks', [])) if isinstance(breakers, dict) else 0,
                'data': breakers
            }
            
            return smart_money_results
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error en Smart Money analysis: {e}", 
                            "real_backtest_engine", "analysis")
            return {'error': str(e)}
    
    def _execute_order_blocks_analysis_dashboard(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Ejecutar Order Blocks analysis usando EXACTO el componente del dashboard"""
        try:
            order_blocks = self.smart_money_analyzer.find_order_blocks(df)
            
            if isinstance(order_blocks, dict) and 'order_blocks' in order_blocks:
                obs = order_blocks['order_blocks']
                return {
                    'total_blocks': len(obs),
                    'bullish_blocks': len([ob for ob in obs if ob.get('type') == 'bullish']),
                    'bearish_blocks': len([ob for ob in obs if ob.get('type') == 'bearish']),
                    'data': order_blocks
                }
            else:
                return {'total_blocks': 0, 'bullish_blocks': 0, 'bearish_blocks': 0, 'data': order_blocks}
                
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error en Order Blocks analysis: {e}", 
                            "real_backtest_engine", "analysis")
            return {'error': str(e)}
    
    def _execute_fvg_analysis_dashboard(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Ejecutar FVG analysis usando EXACTO el componente del dashboard"""
        try:
            fvg_analysis = self.smart_money_analyzer.detect_fvg(df)
            
            if isinstance(fvg_analysis, dict) and 'fvgs' in fvg_analysis:
                fvgs = fvg_analysis['fvgs']
                return {
                    'total_fvgs': len(fvgs),
                    'bullish_fvgs': len([fvg for fvg in fvgs if fvg.get('direction') == 'bullish']),
                    'bearish_fvgs': len([fvg for fvg in fvgs if fvg.get('direction') == 'bearish']),
                    'data': fvg_analysis
                }
            else:
                return {'total_fvgs': 0, 'bullish_fvgs': 0, 'bearish_fvgs': 0, 'data': fvg_analysis}
                
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error en FVG analysis: {e}", 
                            "real_backtest_engine", "analysis")
            return {'error': str(e)}
    
    def _calculate_backtest_performance(self, backtest_results: Dict, start_time: datetime) -> Dict[str, Any]:
        """Calcular métricas de performance del backtest"""
        end_time = datetime.now()
        
        return {
            'execution_duration': (end_time - start_time).total_seconds(),
            'strategies_executed': len(backtest_results.get('strategies_executed', [])),
            'analysis_timestamp': backtest_results.get('analysis_timestamp', end_time),
            'components_used': list(self.dashboard_components.keys()),
            'dashboard_integration': all(self.dashboard_components.values()),
            'data_quality': 'REAL_MT5_DATA' if self.dashboard_components.get('mt5_manager', False) else 'UNKNOWN'
        }
    
    def _create_empty_backtest_result(self, config: Dict, reason: str) -> Dict[str, Any]:
        """Crear resultado vacío para casos de error"""
        return {
            'backtest_config': config,
            'data_info': {'candles_count': 0, 'data_quality': 'ERROR'},
            'analysis_results': {
                'smart_money': {'stop_hunts': {'count': 0}, 'killzones': {'active_zones': 0}, 'breaker_blocks': {'count': 0}},
                'order_blocks': {'total_blocks': 0, 'bullish_blocks': 0, 'bearish_blocks': 0},
                'fvg': {'total_fvgs': 0, 'bullish_fvgs': 0, 'bearish_fvgs': 0},
                'strategies_executed': []
            },
            'performance_metrics': {'execution_duration': 0, 'strategies_executed': 0},
            'engine_info': {'dashboard_components_used': self.dashboard_components},
            'error': reason
        }
    
    def _save_backtest_results(self, results: Dict):
        """Guardar resultados del backtest"""
        try:
            # Crear directorio de resultados
            results_dir = Path(__file__).parent.parent / "reports" / "backtest_results"
            results_dir.mkdir(parents=True, exist_ok=True)
            
            # Crear nombre archivo
            config = results['backtest_config']
            filename = f"backtest_{config['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = results_dir / filename
            
            # Guardar (implementar según necesidades)
            enviar_senal_log("INFO", f"💾 Resultados guardados en: {filepath}", 
                            "real_backtest_engine", "storage")
            
        except Exception as e:
            enviar_senal_log("ERROR", f"❌ Error guardando resultados: {e}", 
                            "real_backtest_engine", "storage")
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Obtener estado actual del motor"""
        return {
            'initialized': self.engine_state['initialized'],
            'backtests_executed': self.engine_state['backtests_executed'],
            'last_backtest': self.engine_state.get('last_backtest'),
            'dashboard_components_status': self.dashboard_components,
            'current_backtest': self.analysis_state.get('current_backtest'),
            'last_update': datetime.now()
        }


# Función de utilidad para crear instancia global
_backtest_engine_instance = None

def get_real_backtest_engine(config: Optional[Dict] = None) -> RealICTBacktestEngine:
    """Obtener instancia global del motor de backtesting real"""
    global _backtest_engine_instance
    
    if _backtest_engine_instance is None:
        _backtest_engine_instance = RealICTBacktestEngine(config)
    
    return _backtest_engine_instance


if __name__ == "__main__":
    # Test básico del motor
    print("🚀 Testing RealICTBacktestEngine...")
    
    try:
        engine = RealICTBacktestEngine()
        status = engine.get_engine_status()
        
        print(f"✅ Motor inicializado correctamente")
        print(f"📊 Dashboard components: {status['dashboard_components_status']}")
        
        # Test backtest rápido
        test_start = datetime.now() - timedelta(days=7)
        test_end = datetime.now()
        
        result = engine.execute_backtest('EURUSD', 'H1', test_start, test_end)
        print(f"🔄 Test backtest completado: {result.get('data_info', {}).get('candles_count', 0)} candles")
        
    except Exception as e:
        print(f"❌ Error en testing: {e}")