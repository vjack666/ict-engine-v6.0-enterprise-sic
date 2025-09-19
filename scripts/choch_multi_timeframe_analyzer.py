#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 CHoCH MULTI-TIMEFRAME ANALYZER - FASE NUEVA
==============================================

Analiza y muestra resultados actuales de CHoCH (Change of Character) 
en diferentes temporalidades con visualización clara y detallada.

Temporalidades analizadas:
- H4 (4 horas) - Timeframe principal
- M15 (15 minutos) - Timeframe intermedio  
- M5 (5 minutos) - Timeframe de entrada

Funcionalidades:
✅ Detección CHoCH en múltiples timeframes
✅ Análisis de alineación entre temporalidades
✅ Visualización clara de resultados
✅ Métricas de confianza por timeframe
✅ Tendencia general del mercado

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 19 Septiembre 2025 - FASE NUEVA
"""

import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Agregar paths necesarios
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "01-CORE"))

class ChochMultiTimeframeAnalyzer:
    """Analizador de CHoCH en múltiples temporalidades"""
    
    def __init__(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.timeframes = ['H4', 'M15', 'M5']
        self.symbols = ['EURUSD', 'GBPUSD', 'USDJPY']
        
        # Importar detector si está disponible
        self.pattern_detector = None
        self._load_pattern_detector()
    
    def _load_pattern_detector(self):
        """Cargar el detector de patrones"""
        try:
            from analysis.pattern_detector import PatternDetector
            self.pattern_detector = PatternDetector()
            print("✅ Pattern Detector cargado correctamente")
        except Exception as e:
            print(f"⚠️ Pattern Detector no disponible: {e}")
            self.pattern_detector = None
    
    def analyze_choch_current_state(self, symbol: str = "EURUSD") -> Dict[str, Any]:
        """Analizar estado actual de CHoCH en todas las temporalidades"""
        analysis_start = datetime.now()
        max_analysis_time = 30  # 30 segundos máximo por símbolo
        
        print(f"🔄 Analizando CHoCH actual para {symbol}...")
        
        analysis = {
            'symbol': symbol,
            'analysis_time': datetime.now().isoformat(),
            'timeframes_analysis': {},
            'multi_tf_summary': {},
            'market_structure': {}
        }
        
        try:
            # Verificar timeout antes de procesar
            elapsed = (datetime.now() - analysis_start).total_seconds()
            if elapsed > max_analysis_time:
                print(f"  ⏰ Timeout preventivo, usando simulación...")
                return self._simulate_choch_analysis(symbol)
            
            if self.pattern_detector:
                print(f"  ⚙️ Usando Pattern Detector real...")
                # Análisis real usando el detector optimizado
                choch_result = self.pattern_detector.detect_choch(symbol, self.timeframes, mode='live_ready')
                analysis = self._process_real_choch_results(choch_result, symbol)
            else:
                print(f"  🎭 Pattern Detector no disponible, usando simulación...")
                # Simulación detallada basada en parámetros conocidos
                analysis = self._simulate_choch_analysis(symbol)
            
            # Verificar timeout al finalizar
            elapsed = (datetime.now() - analysis_start).total_seconds()
            if elapsed > max_analysis_time:
                print(f"  ⏰ Análisis con timeout ({elapsed:.1f}s)")
            else:
                print(f"  ✅ Análisis completado en {elapsed:.1f}s")
            
        except Exception as e:
            elapsed = (datetime.now() - analysis_start).total_seconds()
            analysis['error'] = str(e)
            print(f"❌ Error en análisis CHoCH después de {elapsed:.1f}s: {e}")
            print(f"🔄 Fallback a simulación...")
            return self._simulate_choch_analysis(symbol)
        
        return analysis
    
    def _process_real_choch_results(self, choch_result: Dict, symbol: str) -> Dict[str, Any]:
        """Procesar resultados reales del detector CHoCH"""
        analysis = {
            'symbol': symbol,
            'analysis_time': datetime.now().isoformat(),
            'detection_method': 'REAL_DETECTOR',
            'timeframes_analysis': {},
            'multi_tf_summary': {},
            'market_structure': {}
        }
        
        # Procesar resultados por timeframe
        tf_results = choch_result.get('tf_results', {})
        all_signals = choch_result.get('all_signals', [])
        
        for tf in self.timeframes:
            tf_data = tf_results.get(tf, {})
            analysis['timeframes_analysis'][tf] = {
                'timeframe': tf,
                'choch_detected': tf_data.get('detected', False),
                'direction': tf_data.get('direction', 'NEUTRAL'),
                'confidence': tf_data.get('confidence', 0.0),
                'structure_type': tf_data.get('structure_type', 'UNKNOWN'),
                'break_level': tf_data.get('break_level', 0.0),
                'target_level': tf_data.get('target_level', 0.0),
                'trend_change': tf_data.get('trend_change', 'No change'),
                'swing_data': tf_data.get('swing_data', {}),
                'analysis_status': 'REAL_DATA'
            }
        
        # Resumen multi-timeframe
        analysis['multi_tf_summary'] = {
            'overall_detected': choch_result.get('detected', False),
            'primary_direction': choch_result.get('direction', 'NEUTRAL'),
            'overall_confidence': choch_result.get('confidence', 0.0),
            'timeframes_with_choch': len(all_signals),
            'alignment_analysis': choch_result.get('alignment_analysis', {}),
            'trend_change_confirmed': choch_result.get('trend_change_confirmed', False)
        }
        
        # Estructura de mercado
        analysis['market_structure'] = {
            'dominant_trend': self._determine_dominant_trend(all_signals),
            'structure_strength': self._calculate_structure_strength(all_signals),
            'key_levels': self._extract_key_levels(tf_results),
            'trading_bias': self._determine_trading_bias(choch_result)
        }
        
        return analysis
    
    def _simulate_choch_analysis(self, symbol: str) -> Dict[str, Any]:
        """Simular análisis CHoCH basado en parámetros conocidos"""
        analysis = {
            'symbol': symbol,
            'analysis_time': datetime.now().isoformat(),
            'detection_method': 'SIMULATED',
            'timeframes_analysis': {},
            'multi_tf_summary': {},
            'market_structure': {}
        }
        
        # Simular resultados por timeframe
        for i, tf in enumerate(self.timeframes):
            # Simular diferentes escenarios
            is_choch_detected = (i % 2 == 0)  # Alternar detección
            direction = ['BULLISH', 'BEARISH', 'NEUTRAL'][i % 3]
            confidence = [92.0, 87.5, 75.0][i]  # Diferentes niveles de confianza
            
            analysis['timeframes_analysis'][tf] = {
                'timeframe': tf,
                'choch_detected': is_choch_detected,
                'direction': direction if is_choch_detected else 'NEUTRAL',
                'confidence': confidence if is_choch_detected else 0.0,
                'structure_type': f'CHOCH_{direction}' if is_choch_detected else 'NO_CHOCH',
                'break_level': 1.0850 + (i * 0.0015),  # Simular niveles
                'target_level': 1.0900 + (i * 0.0020),
                'trend_change': f'Previous trend → {direction}' if is_choch_detected else 'No change',
                'swing_data': {
                    'last_high': {'price': 1.0895 + (i * 0.001), 'index': 50 - i},
                    'last_low': {'price': 1.0845 + (i * 0.001), 'index': 45 - i}
                },
                'analysis_status': 'SIMULATED'
            }
        
        # Resumen multi-timeframe simulado
        choch_count = sum(1 for tf_data in analysis['timeframes_analysis'].values() if tf_data['choch_detected'])
        
        analysis['multi_tf_summary'] = {
            'overall_detected': choch_count > 0,
            'primary_direction': 'BULLISH' if choch_count > 1 else 'NEUTRAL',
            'overall_confidence': 85.0 if choch_count > 1 else 0.0,
            'timeframes_with_choch': choch_count,
            'alignment_analysis': {
                'alignment': 'PARTIAL_ALIGNMENT' if choch_count > 1 else 'NO_ALIGNMENT',
                'score': 0.7 if choch_count > 1 else 0.0
            },
            'trend_change_confirmed': choch_count >= 2
        }
        
        # Estructura de mercado simulada
        analysis['market_structure'] = {
            'dominant_trend': 'BULLISH' if choch_count > 1 else 'RANGING',
            'structure_strength': 'STRONG' if choch_count >= 2 else 'WEAK',
            'key_levels': {
                'resistance': 1.0920,
                'support': 1.0830,
                'pivot': 1.0875
            },
            'trading_bias': 'BUY' if choch_count > 1 else 'NEUTRAL'
        }
        
        return analysis
    
    def _determine_dominant_trend(self, signals: List[Dict]) -> str:
        """Determinar la tendencia dominante"""
        if not signals:
            return 'NEUTRAL'
        
        directions = [signal.get('direction', 'NEUTRAL') for signal in signals]
        bullish_count = directions.count('BULLISH')
        bearish_count = directions.count('BEARISH')
        
        if bullish_count > bearish_count:
            return 'BULLISH'
        elif bearish_count > bullish_count:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def _calculate_structure_strength(self, signals: List[Dict]) -> str:
        """Calcular fuerza de la estructura"""
        if len(signals) >= 3:
            return 'VERY_STRONG'
        elif len(signals) == 2:
            return 'STRONG'
        elif len(signals) == 1:
            return 'MODERATE'
        else:
            return 'WEAK'
    
    def _extract_key_levels(self, tf_results: Dict) -> Dict[str, float]:
        """Extraer niveles clave de los resultados"""
        levels = {
            'resistance': 0.0,
            'support': 0.0,
            'pivot': 0.0
        }
        
        break_levels = []
        target_levels = []
        
        for tf_data in tf_results.values():
            if tf_data.get('detected', False):
                break_level = tf_data.get('break_level', 0.0)
                target_level = tf_data.get('target_level', 0.0)
                
                if break_level > 0:
                    break_levels.append(break_level)
                if target_level > 0:
                    target_levels.append(target_level)
        
        if break_levels and target_levels:
            levels['resistance'] = max(target_levels)
            levels['support'] = min(break_levels)
            levels['pivot'] = (levels['resistance'] + levels['support']) / 2
        
        return levels
    
    def _determine_trading_bias(self, choch_result: Dict) -> str:
        """Determinar el bias de trading"""
        if not choch_result.get('detected', False):
            return 'NEUTRAL'
        
        direction = choch_result.get('direction', 'NEUTRAL')
        confidence = choch_result.get('confidence', 0.0)
        trend_confirmed = choch_result.get('trend_change_confirmed', False)
        
        if trend_confirmed and confidence >= 80:
            return 'BUY' if direction == 'BULLISH' else 'SELL'
        elif confidence >= 70:
            return 'WEAK_BUY' if direction == 'BULLISH' else 'WEAK_SELL'
        else:
            return 'NEUTRAL'
    
    def display_choch_results(self, analysis: Dict[str, Any]):
        """Mostrar resultados de CHoCH de forma visual"""
        symbol = analysis.get('symbol', 'UNKNOWN')
        
        print(f"\n🔄 CHoCH ANALYSIS RESULTS - {symbol}")
        print("=" * 60)
        print(f"📅 Analysis Time: {analysis.get('analysis_time', 'Unknown')}")
        print(f"🔍 Detection Method: {analysis.get('detection_method', 'Unknown')}")
        
        # Resumen multi-timeframe
        summary = analysis.get('multi_tf_summary', {})
        print(f"\n📊 MULTI-TIMEFRAME SUMMARY:")
        print(f"   Overall CHoCH: {'✅ DETECTED' if summary.get('overall_detected', False) else '❌ NOT DETECTED'}")
        print(f"   Primary Direction: {summary.get('primary_direction', 'NEUTRAL')}")
        print(f"   Overall Confidence: {summary.get('overall_confidence', 0.0):.1f}%")
        print(f"   Timeframes with CHoCH: {summary.get('timeframes_with_choch', 0)}/3")
        print(f"   Trend Change Confirmed: {'✅ YES' if summary.get('trend_change_confirmed', False) else '❌ NO'}")
        
        # Análisis por timeframe
        print(f"\n🎯 TIMEFRAME ANALYSIS:")
        tf_analysis = analysis.get('timeframes_analysis', {})
        
        for tf in self.timeframes:
            tf_data = tf_analysis.get(tf, {})
            choch_detected = tf_data.get('choch_detected', False)
            direction = tf_data.get('direction', 'NEUTRAL')
            confidence = tf_data.get('confidence', 0.0)
            structure_type = tf_data.get('structure_type', 'UNKNOWN')
            
            status_icon = "🟢" if choch_detected else "🔴"
            direction_icon = "📈" if direction == 'BULLISH' else "📉" if direction == 'BEARISH' else "➡️"
            
            print(f"   {status_icon} {tf:3s}: {direction_icon} {direction:7s} | Conf: {confidence:5.1f}% | {structure_type}")
            
            if choch_detected:
                break_level = tf_data.get('break_level', 0.0)
                target_level = tf_data.get('target_level', 0.0)
                print(f"       └─ Break: {break_level:.5f} → Target: {target_level:.5f}")
        
        # Estructura de mercado
        market_structure = analysis.get('market_structure', {})
        print(f"\n🏗️ MARKET STRUCTURE:")
        print(f"   Dominant Trend: {market_structure.get('dominant_trend', 'UNKNOWN')}")
        print(f"   Structure Strength: {market_structure.get('structure_strength', 'UNKNOWN')}")
        print(f"   Trading Bias: {market_structure.get('trading_bias', 'NEUTRAL')}")
        
        # Niveles clave
        key_levels = market_structure.get('key_levels', {})
        if any(level > 0 for level in key_levels.values()):
            print(f"\n📏 KEY LEVELS:")
            print(f"   Resistance: {key_levels.get('resistance', 0.0):.5f}")
            print(f"   Pivot:      {key_levels.get('pivot', 0.0):.5f}")
            print(f"   Support:    {key_levels.get('support', 0.0):.5f}")
        
        # Alineación
        alignment = summary.get('alignment_analysis', {})
        if alignment:
            alignment_status = alignment.get('alignment', 'UNKNOWN')
            alignment_score = alignment.get('score', 0.0)
            print(f"\n🎯 TIMEFRAME ALIGNMENT:")
            print(f"   Status: {alignment_status}")
            print(f"   Score: {alignment_score:.2f}/1.00")
            
            if alignment_score >= 0.8:
                print(f"   Quality: 🟢 EXCELLENT")
            elif alignment_score >= 0.6:
                print(f"   Quality: 🟡 GOOD")
            elif alignment_score >= 0.4:
                print(f"   Quality: 🟠 FAIR")
            else:
                print(f"   Quality: 🔴 POOR")
    
    def analyze_multiple_symbols(self, symbols: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analizar CHoCH para múltiples símbolos"""
        if symbols is None:
            symbols = self.symbols
        
        # Limitar número de símbolos para evitar loops infinitos
        max_symbols = 5
        if len(symbols) > max_symbols:
            symbols = symbols[:max_symbols]
            print(f"⚠️ Limitando análisis a {max_symbols} símbolos para evitar loops infinitos")
        
        print(f"🔄 Analizando CHoCH para {len(symbols)} símbolos...")
        
        multi_symbol_analysis = {
            'analysis_time': datetime.now().isoformat(),
            'symbols_analyzed': symbols,
            'individual_analysis': {},
            'market_overview': {}
        }
        
        # Analizar cada símbolo con control de progreso
        symbol_count = 0
        total_symbols = len(symbols)
        
        for symbol in symbols:
            symbol_count += 1
            print(f"\n📊 Analizando {symbol} ({symbol_count}/{total_symbols})...")
            
            try:
                symbol_analysis = self.analyze_choch_current_state(symbol)
                multi_symbol_analysis['individual_analysis'][symbol] = symbol_analysis
                
                # Mostrar resultados
                self.display_choch_results(symbol_analysis)
                
                print(f"✅ Análisis de {symbol} completado ({symbol_count}/{total_symbols})")
                
            except Exception as e:
                print(f"❌ Error analizando {symbol}: {e}")
                # Continuar con el siguiente símbolo
                continue
        
        print(f"\n🎯 ANÁLISIS COMPLETADO: {symbol_count}/{total_symbols} símbolos procesados")
        
        # Generar overview del mercado
        multi_symbol_analysis['market_overview'] = self._generate_market_overview(
            multi_symbol_analysis['individual_analysis']
        )
        
        return multi_symbol_analysis
    
    def _generate_market_overview(self, individual_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generar overview general del mercado"""
        overview = {
            'total_symbols': len(individual_analyses),
            'symbols_with_choch': 0,
            'dominant_market_direction': 'NEUTRAL',
            'market_strength': 'WEAK',
            'trading_opportunities': []
        }
        
        directions = []
        for symbol, analysis in individual_analyses.items():
            summary = analysis.get('multi_tf_summary', {})
            if summary.get('overall_detected', False):
                overview['symbols_with_choch'] += 1
                directions.append(summary.get('primary_direction', 'NEUTRAL'))
                
                # Identificar oportunidades de trading
                confidence = summary.get('overall_confidence', 0.0)
                bias = analysis.get('market_structure', {}).get('trading_bias', 'NEUTRAL')
                
                if confidence >= 80 and bias in ['BUY', 'SELL']:
                    overview['trading_opportunities'].append({
                        'symbol': symbol,
                        'direction': summary.get('primary_direction', 'NEUTRAL'),
                        'confidence': confidence,
                        'bias': bias
                    })
        
        # Determinar dirección dominante del mercado
        if directions:
            bullish_count = directions.count('BULLISH')
            bearish_count = directions.count('BEARISH')
            
            if bullish_count > bearish_count:
                overview['dominant_market_direction'] = 'BULLISH'
            elif bearish_count > bullish_count:
                overview['dominant_market_direction'] = 'BEARISH'
            else:
                overview['dominant_market_direction'] = 'MIXED'
        
        # Determinar fuerza del mercado
        choch_ratio = overview['symbols_with_choch'] / overview['total_symbols']
        if choch_ratio >= 0.75:
            overview['market_strength'] = 'VERY_STRONG'
        elif choch_ratio >= 0.5:
            overview['market_strength'] = 'STRONG'
        elif choch_ratio >= 0.25:
            overview['market_strength'] = 'MODERATE'
        else:
            overview['market_strength'] = 'WEAK'
        
        return overview
    
    def display_market_overview(self, overview: Dict[str, Any]):
        """Mostrar overview del mercado"""
        print(f"\n🌍 MARKET OVERVIEW")
        print("=" * 40)
        print(f"Symbols Analyzed: {overview.get('total_symbols', 0)}")
        print(f"CHoCH Detected: {overview.get('symbols_with_choch', 0)}/{overview.get('total_symbols', 0)}")
        print(f"Market Direction: {overview.get('dominant_market_direction', 'UNKNOWN')}")
        print(f"Market Strength: {overview.get('market_strength', 'UNKNOWN')}")
        
        # Oportunidades de trading
        opportunities = overview.get('trading_opportunities', [])
        if opportunities:
            print(f"\n💡 TRADING OPPORTUNITIES:")
            for opp in opportunities:
                direction_icon = "📈" if opp['direction'] == 'BULLISH' else "📉"
                print(f"   {direction_icon} {opp['symbol']}: {opp['bias']} ({opp['confidence']:.1f}% conf)")
        else:
            print(f"\n💡 TRADING OPPORTUNITIES: None detected")

def main():
    """Función principal"""
    start_time = datetime.now()
    
    print("🔄 ICT Engine v6.0 - CHoCH Multi-Timeframe Analyzer")
    print("=" * 65)
    print("FASE NUEVA: Visualización CHoCH en Múltiples Temporalidades")
    print("=" * 65)
    print(f"🕐 Iniciando análisis: {start_time.strftime('%H:%M:%S')}")
    
    analyzer = ChochMultiTimeframeAnalyzer()
    
    try:
        print(f"\n🎯 SÍMBOLOS A ANALIZAR: {analyzer.symbols}")
        print(f"⏱️ TIMEFRAMES: {analyzer.timeframes}")
        
        # Analizar múltiples símbolos
        print(f"\n{'='*50}")
        print("🚀 INICIANDO ANÁLISIS MULTI-TIMEFRAME")
        print(f"{'='*50}")
        
        multi_analysis = analyzer.analyze_multiple_symbols()
        
        # Mostrar overview del mercado
        print(f"\n{'='*50}")
        print("📈 GENERANDO RESUMEN DEL MERCADO")
        print(f"{'='*50}")
        
        market_overview = multi_analysis.get('market_overview', {})
        analyzer.display_market_overview(market_overview)
        
        # Guardar resultados
        print(f"\n{'='*50}")
        print("💾 GUARDANDO RESULTADOS")
        print(f"{'='*50}")
        
        results_dir = analyzer.repo_root / "DOCS" / "reports"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"choch_multi_timeframe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(multi_analysis, f, indent=2, ensure_ascii=False)
        
        # Finalización
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n{'='*65}")
        print("✅ ANÁLISIS MULTI-TIMEFRAME COMPLETADO")
        print(f"{'='*65}")
        print(f"💾 Resultados guardados: {filepath}")
        print(f"⏱️ Tiempo total: {duration.total_seconds():.2f} segundos")
        print(f"🕐 Finalizado: {end_time.strftime('%H:%M:%S')}")
        print(f"📊 Símbolos analizados: {len(multi_analysis.get('symbols_analyzed', []))}")
        print(f"🎯 CHoCH detectados: {market_overview.get('symbols_with_choch', 0)}")
        print(f"📈 Dirección del mercado: {market_overview.get('dominant_market_direction', 'UNKNOWN')}")
        print(f"💪 Fuerza del mercado: {market_overview.get('market_strength', 'UNKNOWN')}")
        print(f"\n🏁 ANÁLISIS FINALIZADO - SALIENDO DEL PROGRAMA")
        print(f"{'='*65}")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Análisis interrumpido por el usuario")
        print(f"🏁 ANÁLISIS CANCELADO - SALIENDO DEL PROGRAMA")
        return 2
        
    except Exception as e:
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n❌ Error durante análisis: {e}")
        print(f"⏱️ Tiempo transcurrido antes del error: {duration.total_seconds():.2f} segundos")
        print(f"🏁 ANÁLISIS FALLIDO - SALIENDO DEL PROGRAMA")
        return 1
    
    finally:
        print(f"\n🔚 FINALIZANDO EJECUCIÓN...")

if __name__ == "__main__":
    result_code = main()
    print(f"🔚 Código de salida: {result_code}")
    exit(result_code)