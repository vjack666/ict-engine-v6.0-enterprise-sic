#!/usr/bin/env python3
"""
🎯 CHOCH TRADING ANALYZER - ICT ENGINE v6.0 ENTERPRISE
=====================================================

Módulo de análisis CHoCH (Change of Character) para trading en tiempo real.
Convierte la funcionalidad de test en componente de producción que integra 
con el sistema de memoria unificada y proporciona análisis CHoCH para trading.

CARACTERÍSTICAS:
✅ Análisis CHoCH en tiempo real
✅ Integración con unified_market_memory
✅ Validación temporal de CHoCH
✅ Niveles de trading automáticos
✅ Filtros de confianza
✅ Optimizado para producción

INTEGRACIÓN:
- Se conecta con market_context_v6.py
- Usa unified_market_memory.py
- Proporciona datos para silver_bullet_trader.py
- Logging centralizado vía protocols

Author: ICT Engine v6.0 Enterprise Team
Date: September 2025
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json

# Setup paths
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
core_path = current_dir.parent
sys.path.insert(0, str(core_path))

# Import logging with proper type handling  
def get_unified_logger(name: str):
    """Factory function for logger with fallback"""
    try:
        from protocols.unified_logging import get_unified_logger as real_logger
        return real_logger(name)
    except ImportError:
        # Fallback logger
        class FallbackLogger:
            def __init__(self, logger_name: str):
                self.name = logger_name
            def info(self, msg, component=""): print(f"[INFO][{self.name}][{component}] {msg}")
            def warning(self, msg, component=""): print(f"[WARN][{self.name}][{component}] {msg}")
            def error(self, msg, component=""): print(f"[ERROR][{self.name}][{component}] {msg}")
            def debug(self, msg, component=""): print(f"[DEBUG][{self.name}][{component}] {msg}")
        return FallbackLogger(name)

# Import core modules
try:
    from analysis.unified_market_memory import get_unified_market_memory, get_last_choch_for_trading, get_choch_trading_levels
    MEMORY_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Memory system not available: {e}")
    MEMORY_AVAILABLE = False

try:
    from analysis.market_context_v6 import MarketContextV6
    MARKET_CONTEXT_AVAILABLE = True
except ImportError:
    MARKET_CONTEXT_AVAILABLE = False

try:
    from analysis.pattern_detector import PatternDetector
    PATTERN_DETECTOR_AVAILABLE = True
except ImportError:
    PATTERN_DETECTOR_AVAILABLE = False

class CHoCHAnalysisResult:
    """Resultado de análisis CHoCH estandarizado"""
    
    def __init__(self, 
                 symbol: str,
                 has_valid_choch: bool = False,
                 direction: str = "NEUTRAL",
                 confidence: float = 0.0,
                 break_level: float = 0.0,
                 target_level: float = 0.0,
                 timeframe: str = "M15",
                 age_minutes: int = 0,
                 strength: str = "WEAK",
                 trading_bias: str = "NEUTRAL",
                 timestamp: Optional[datetime] = None):
        
        self.symbol = symbol
        self.has_valid_choch = has_valid_choch
        self.direction = direction
        self.confidence = confidence
        self.break_level = break_level
        self.target_level = target_level
        self.timeframe = timeframe
        self.age_minutes = age_minutes
        self.strength = strength
        self.trading_bias = trading_bias
        self.timestamp = timestamp or datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        return {
            'symbol': self.symbol,
            'has_valid_choch': self.has_valid_choch,
            'direction': self.direction,
            'confidence': self.confidence,
            'break_level': self.break_level,
            'target_level': self.target_level,
            'timeframe': self.timeframe,
            'age_minutes': self.age_minutes,
            'strength': self.strength,
            'trading_bias': self.trading_bias,
            'timestamp': self.timestamp.isoformat(),
            'is_valid_for_trading': self.has_valid_choch and self.age_minutes <= 240  # 4 horas max
        }

class CHoCHTradingAnalyzer:
    """
    🎯 Analizador CHoCH para trading en tiempo real
    
    Responsabilidades:
    - Analizar CHoCH detectados en memoria
    - Validar vigencia temporal
    - Proporcionar niveles de trading
    - Filtrar por confianza
    - Integrar con sistema de memoria
    """
    
    def __init__(self):
        """Inicializar analizador CHoCH"""
        self.logger = get_unified_logger("CHoCHTradingAnalyzer")
        self.logger.info("🎯 Inicializando CHoCH Trading Analyzer v6.0", "CHOCH_ANALYZER")
        
        # Configuración
        self.min_confidence = 70.0  # Confianza mínima para trading
        self.max_age_minutes = 240  # Máximo 4 horas de vigencia
        self.min_strength_level = "MEDIUM"  # Fuerza mínima
        
        # Estado
        self.last_analysis_time = datetime.now()
        self.analysis_cache: Dict[str, CHoCHAnalysisResult] = {}
        
        # Verificar disponibilidad de componentes
        self._check_component_availability()
        
    def _check_component_availability(self):
        """Verificar disponibilidad de componentes críticos"""
        components = {
            "Memory System": MEMORY_AVAILABLE,
            "Market Context": MARKET_CONTEXT_AVAILABLE,
            "Pattern Detector": PATTERN_DETECTOR_AVAILABLE
        }
        
        available = sum(components.values())
        total = len(components)
        
        self.logger.info(f"📊 Componentes disponibles: {available}/{total}", "INIT")
        
        for component, status in components.items():
            status_icon = "✅" if status else "❌"
            self.logger.info(f"   {status_icon} {component}", "INIT")
            
        if available < 1:
            self.logger.warning("⚠️ Pocos componentes disponibles - funcionalidad limitada", "INIT")
    
    def analyze_choch_for_symbol(self, symbol: str) -> CHoCHAnalysisResult:
        """
        🎯 MÉTODO PRINCIPAL: Analizar CHoCH para símbolo específico
        
        Args:
            symbol: Símbolo a analizar (ej: "EURUSD")
            
        Returns:
            CHoCHAnalysisResult con análisis completo
        """
        try:
            # Verificar cache reciente ANTES de loggear para evitar spam
            if symbol in self.analysis_cache:
                cached = self.analysis_cache[symbol]
                cache_age = (datetime.now() - cached.timestamp).total_seconds() / 60
                if cache_age < 5:  # Cache válido por 5 minutos
                    self.logger.debug(f"📋 Usando análisis cached para {symbol} (edad: {cache_age:.1f}m)", "CACHE")
                    return cached

            # Solo loggear cuando realmente se hará análisis
            self.logger.info(f"🔍 Analizando CHoCH para {symbol}", "ANALYSIS")
            
            # Análisis completo
            result = self._perform_full_analysis(symbol)
            
            # Guardar en cache
            self.analysis_cache[symbol] = result
            
            # Log resultado
            self._log_analysis_result(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analizando CHoCH para {symbol}: {e}", "ANALYSIS")
            return CHoCHAnalysisResult(symbol=symbol)
    
    def _perform_full_analysis(self, symbol: str) -> CHoCHAnalysisResult:
        """Realizar análisis completo de CHoCH"""
        
        # Intentar obtener último CHoCH de memoria
        if MEMORY_AVAILABLE:
            try:
                last_choch = get_last_choch_for_trading(symbol)
                if last_choch:
                    return self._convert_memory_choch_to_result(symbol, last_choch)
            except Exception as e:
                self.logger.warning(f"Error accediendo memoria CHoCH: {e}", "MEMORY")
        
        # Fallback: análisis directo si hay detector de patrones
        if PATTERN_DETECTOR_AVAILABLE:
            try:
                return self._analyze_with_pattern_detector(symbol)
            except Exception as e:
                self.logger.warning(f"Error con detector de patrones: {e}", "DETECTOR")
        
        # Sin datos disponibles
        self.logger.warning(f"No hay datos CHoCH disponibles para {symbol}", "NO_DATA")
        return CHoCHAnalysisResult(symbol=symbol)
    
    def _convert_memory_choch_to_result(self, symbol: str, choch_data: Dict[str, Any]) -> CHoCHAnalysisResult:
        """Convertir datos de memoria a resultado estandarizado"""
        
        # Calcular edad
        timestamp = choch_data.get('timestamp')
        age_minutes = 0
        if timestamp:
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    timestamp = datetime.now()
            age_minutes = int((datetime.now() - timestamp).total_seconds() / 60)
        
        # Validar vigencia
        is_valid = (
            age_minutes <= self.max_age_minutes and
            choch_data.get('confidence', 0) >= self.min_confidence
        )
        
        # Determinar bias de trading
        trading_bias = "NEUTRAL"
        if is_valid:
            direction = choch_data.get('direction', 'NEUTRAL').upper()
            if direction == 'BULLISH':
                trading_bias = "LONG"
            elif direction == 'BEARISH':
                trading_bias = "SHORT"
        
        return CHoCHAnalysisResult(
            symbol=symbol,
            has_valid_choch=is_valid,
            direction=choch_data.get('direction', 'NEUTRAL'),
            confidence=choch_data.get('confidence', 0.0),
            break_level=choch_data.get('price', 0.0),
            target_level=choch_data.get('target_level', 0.0),
            timeframe=choch_data.get('timeframe', 'M15'),
            age_minutes=age_minutes,
            strength=choch_data.get('strength', 'WEAK'),
            trading_bias=trading_bias,
            timestamp=timestamp if isinstance(timestamp, datetime) else datetime.now()
        )
    
    def _analyze_with_pattern_detector(self, symbol: str) -> CHoCHAnalysisResult:
        """Análisis directo usando PatternDetector"""
        try:
            detector = PatternDetector()
            choch_result = detector.detect_choch(symbol, mode='live_ready')
            
            if choch_result and choch_result.get('detected'):
                signals = choch_result.get('signals', [])
                if signals:
                    signal = signals[0]  # Usar primera señal
                    
                    return CHoCHAnalysisResult(
                        symbol=symbol,
                        has_valid_choch=True,
                        direction=signal.get('direction', 'NEUTRAL'),
                        confidence=signal.get('confidence', 0.0),
                        break_level=signal.get('price', 0.0),
                        timeframe=signal.get('timeframe', 'M15'),
                        strength="DETECTED"
                    )
            
            return CHoCHAnalysisResult(symbol=symbol)
            
        except Exception as e:
            self.logger.error(f"Error en análisis directo: {e}", "DIRECT_ANALYSIS")
            return CHoCHAnalysisResult(symbol=symbol)
    
    def _log_analysis_result(self, result: CHoCHAnalysisResult):
        """Loggear resultado de análisis"""
        if result.has_valid_choch:
            self.logger.info(
                f"✅ CHoCH VÁLIDO {result.symbol}: {result.direction} "
                f"Conf:{result.confidence:.1f}% Edad:{result.age_minutes}m "
                f"Bias:{result.trading_bias}", "RESULT"
            )
        else:
            self.logger.debug(f"❌ Sin CHoCH válido para {result.symbol}", "RESULT")
    
    def get_trading_recommendation(self, symbol: str) -> Dict[str, Any]:
        """
        📈 OBTENER RECOMENDACIÓN DE TRADING
        
        Args:
            symbol: Símbolo para análisis
            
        Returns:
            Dict con recomendación completa
        """
        analysis = self.analyze_choch_for_symbol(symbol)

        recommendation = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'action': 'NONE',
            'confidence': 0.0,
            'entry_zone': None,
            'stop_loss': None,
            'take_profit': None,
            'risk_reward': 0.0,
            'choch_analysis': analysis.to_dict(),
            'reasoning': []
        }

        if analysis.has_valid_choch:
            if analysis.confidence >= self.min_confidence:
                if analysis.trading_bias == "LONG":
                    recommendation['action'] = 'BUY'
                    recommendation['reasoning'].append(f"CHoCH BULLISH detectado con {analysis.confidence:.1f}% confianza")
                elif analysis.trading_bias == "SHORT":
                    recommendation['action'] = 'SELL'
                    recommendation['reasoning'].append(f"CHoCH BEARISH detectado con {analysis.confidence:.1f}% confianza")

                recommendation['confidence'] = analysis.confidence
                recommendation['entry_zone'] = analysis.break_level

                # Calcular niveles básicos
                if analysis.break_level > 0:
                    if recommendation['action'] == 'BUY':
                        recommendation['stop_loss'] = analysis.break_level * 0.999  # 10 pips aprox
                        recommendation['take_profit'] = analysis.break_level * 1.002  # 20 pips aprox
                    else:
                        recommendation['stop_loss'] = analysis.break_level * 1.001
                        recommendation['take_profit'] = analysis.break_level * 0.998

                    # Risk:Reward básico
                    if recommendation['stop_loss'] and recommendation['take_profit']:
                        risk = abs(recommendation['entry_zone'] - recommendation['stop_loss'])
                        reward = abs(recommendation['take_profit'] - recommendation['entry_zone'])
                        recommendation['risk_reward'] = reward / risk if risk > 0 else 0
            else:
                recommendation['reasoning'].append(f"Confianza insuficiente: {analysis.confidence:.1f}% < {self.min_confidence}%")
        else:
            recommendation['reasoning'].append("No hay CHoCH válido disponible")

        return recommendation
    
    def get_recommendation_from_analysis(self, analysis: CHoCHAnalysisResult) -> Dict[str, Any]:
        """Construir recomendación sin re-analizar (evita logs duplicados)"""
        symbol = analysis.symbol
        recommendation = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'action': 'NONE',
            'confidence': 0.0,
            'entry_zone': None,
            'stop_loss': None,
            'take_profit': None,
            'risk_reward': 0.0,
            'choch_analysis': analysis.to_dict(),
            'reasoning': []
        }
        if analysis.has_valid_choch and analysis.confidence >= self.min_confidence:
            if analysis.trading_bias == "LONG":
                recommendation['action'] = 'BUY'
                recommendation['reasoning'].append(f"CHoCH BULLISH detectado con {analysis.confidence:.1f}% confianza")
            elif analysis.trading_bias == "SHORT":
                recommendation['action'] = 'SELL'
                recommendation['reasoning'].append(f"CHoCH BEARISH detectado con {analysis.confidence:.1f}% confianza")
            recommendation['confidence'] = analysis.confidence
            recommendation['entry_zone'] = analysis.break_level
            if analysis.break_level > 0:
                if recommendation['action'] == 'BUY':
                    recommendation['stop_loss'] = analysis.break_level * 0.999
                    recommendation['take_profit'] = analysis.break_level * 1.002
                else:
                    recommendation['stop_loss'] = analysis.break_level * 1.001
                    recommendation['take_profit'] = analysis.break_level * 0.998
                risk = abs((recommendation['entry_zone'] or 0) - (recommendation['stop_loss'] or 0))
                reward = abs((recommendation['take_profit'] or 0) - (recommendation['entry_zone'] or 0))
                recommendation['risk_reward'] = (reward / risk) if risk > 0 else 0
        else:
            if not analysis.has_valid_choch:
                recommendation['reasoning'].append("No hay CHoCH válido disponible")
            else:
                recommendation['reasoning'].append(f"Confianza insuficiente: {analysis.confidence:.1f}% < {self.min_confidence}%")
        return recommendation
    
    def analyze_multiple_symbols(self, symbols: List[str]) -> Dict[str, CHoCHAnalysisResult]:
        """Analizar múltiples símbolos eficientemente"""
        results = {}
        
        self.logger.info(f"🔍 Analizando {len(symbols)} símbolos", "MULTI_ANALYSIS")
        
        for symbol in symbols:
            try:
                results[symbol] = self.analyze_choch_for_symbol(symbol)
            except Exception as e:
                self.logger.error(f"Error analizando {symbol}: {e}", "MULTI_ANALYSIS")
                results[symbol] = CHoCHAnalysisResult(symbol=symbol)
        
        # Estadísticas
        valid_chochs = sum(1 for r in results.values() if r.has_valid_choch)
        self.logger.info(f"📊 Análisis completado: {valid_chochs}/{len(symbols)} con CHoCH válidos", "MULTI_ANALYSIS")
        
        return results
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema de análisis"""
        return {
            'component': 'CHoCHTradingAnalyzer',
            'version': '6.0',
            'timestamp': datetime.now().isoformat(),
            'memory_available': MEMORY_AVAILABLE,
            'market_context_available': MARKET_CONTEXT_AVAILABLE,
            'pattern_detector_available': PATTERN_DETECTOR_AVAILABLE,
            'configuration': {
                'min_confidence': self.min_confidence,
                'max_age_minutes': self.max_age_minutes,
                'min_strength_level': self.min_strength_level
            },
            'cache_size': len(self.analysis_cache),
            'last_analysis': self.last_analysis_time.isoformat()
        }


# ============================================================================
# FUNCIONES DE CONVENIENCIA PARA INTEGRACIÓN
# ============================================================================

_choch_analyzer_instance = None

def get_choch_analyzer() -> CHoCHTradingAnalyzer:
    """Obtener instancia singleton del analizador CHoCH"""
    global _choch_analyzer_instance
    if _choch_analyzer_instance is None:
        _choch_analyzer_instance = CHoCHTradingAnalyzer()
    return _choch_analyzer_instance

def analyze_choch_for_trading(symbol: str) -> Dict[str, Any]:
    """
    🎯 FUNCIÓN PRINCIPAL: Análisis CHoCH para trading
    
    Esta función reemplaza la lógica del test eliminado
    """
    analyzer = get_choch_analyzer()
    return analyzer.get_trading_recommendation(symbol)

def get_current_choch_status(symbol: str) -> Dict[str, Any]:
    """Obtener estado actual CHoCH para símbolo"""
    analyzer = get_choch_analyzer()
    analysis = analyzer.analyze_choch_for_symbol(symbol)
    return analysis.to_dict()

def check_choch_trading_readiness() -> Dict[str, Any]:
    """Verificar si el sistema CHoCH está listo para trading"""
    analyzer = get_choch_analyzer()
    return analyzer.get_system_status()

# ============================================================================
# DEMO Y TESTING
# ============================================================================

def demo_choch_analysis():
    """Demostración del análisis CHoCH"""
    print("\n" + "="*60)
    print("🎯 DEMO CHoCH TRADING ANALYZER v6.0")
    print("="*60)
    
    analyzer = CHoCHTradingAnalyzer()
    
    # Test con símbolos principales
    symbols = ["EURUSD", "GBPUSD", "USDCAD", "AUDUSD"]
    
    print(f"\n🔍 Analizando {len(symbols)} símbolos principales...")
    results = analyzer.analyze_multiple_symbols(symbols)
    
    print("\n📊 RESULTADOS ANÁLISIS CHoCH:")
    print("-" * 60)
    
    for symbol, result in results.items():
        status = "✅ VÁLIDO" if result.has_valid_choch else "❌ NO VÁLIDO"
        print(f"{symbol:8} | {status:12} | {result.direction:8} | {result.confidence:5.1f}% | {result.trading_bias}")
    
    # Recomendaciones de trading
    print(f"\n🎯 RECOMENDACIONES DE TRADING:")
    print("-" * 60)
    
    for symbol in symbols:
        # Usar resultado ya calculado para evitar re-análisis y logs duplicados
        recommendation = analyzer.get_recommendation_from_analysis(results.get(symbol, CHoCHAnalysisResult(symbol)))
        action = recommendation['action']
        confidence = recommendation['confidence']
        
        if action != 'NONE':
            print(f"💰 {symbol}: {action} | Conf: {confidence:.1f}% | RR: {recommendation['risk_reward']:.2f}")
        else:
            print(f"⏸️ {symbol}: ESPERAR - {', '.join(recommendation['reasoning'][:1])}")
    
    # Estado del sistema
    print(f"\n🔧 ESTADO DEL SISTEMA:")
    status = analyzer.get_system_status()
    print(f"   Componentes: Memory:{status['memory_available']} Context:{status['market_context_available']} Detector:{status['pattern_detector_available']}")
    print(f"   Cache: {status['cache_size']} entradas")
    print(f"   Configuración: Min conf: {status['configuration']['min_confidence']}%, Max edad: {status['configuration']['max_age_minutes']}min")
    
    # GARANTIZAR TERMINACIÓN
    print(f"\n{'='*60}")
    print("✅ DEMO COMPLETADO EXITOSAMENTE")
    print("🔚 Terminando análisis CHoCH...")
    print(f"{'='*60}")
    
    return True  # Indicar finalización exitosa

if __name__ == "__main__":
    # Ejecutar demo con terminación garantizada
    try:
        print("🚀 Iniciando CHoCH Trading Analyzer Demo...")
        success = demo_choch_analysis()
        
        if success:
            print("\n✅ Demo ejecutado exitosamente")
        else:
            print("\n❌ Demo falló")
            
    except Exception as e:
        print(f"\n❌ Error en demo: {e}")
        
    finally:
        print("\n🔚 TERMINANDO PROGRAMA...")
        import sys
        sys.exit(0)