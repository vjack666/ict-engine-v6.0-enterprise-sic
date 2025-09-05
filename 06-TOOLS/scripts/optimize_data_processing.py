#!/usr/bin/env python3
"""
🚀 OPTIMIZACIÓN DE PROCESAMIENTO DE DATOS ICT ENGINE v6.0
Análisis y mejoras de rendimiento para procesamiento óptimo
"""

import time
import sys
import os

# Agregar el path para imports desde la raíz del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
core_path = os.path.join(project_root, '01-CORE')

# Añadir el core path al sys.path para imports directos
sys.path.insert(0, core_path)

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import cpu_count
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import json
from datetime import datetime

# Imports del sistema - rutas corregidas basadas en tree /F
from analysis.pattern_detector import PatternDetector as ICTPatternDetector
from data_management.advanced_candle_downloader import AdvancedCandleDownloader
from analysis.unified_memory_system import get_unified_memory_system

# Importar módulos de optimización avanzada - rutas corregidas
from optimization.detector_pool_manager import (
    EnhancedDetectorPoolManager, AnalysisTask, AnalysisResult
)
from optimization.shared_memory_optimizer import SharedMemoryOptimizer
from optimization.work_distribution_engine import WorkDistributionEngine

class DataProcessingOptimizer:
    """Optimizador de procesamiento de datos ICT Engine v6.0"""
    
    def __init__(self):
        self.optimization_report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'cpu_cores': cpu_count(),
                'optimization_mode': 'ENTERPRISE_MAXIMUM'
            },
            'tests': {},
            'recommendations': []
        }
        # Pool de detectores reutilizables para optimizar paralelismo
        self._detector_pool = []
        self._memory_system = None
        
    def analyze_current_performance(self):
        """Analiza el rendimiento actual del sistema"""
        print("🔬 ANÁLISIS DE RENDIMIENTO ACTUAL")
        print("=" * 50)
        
        # Test 1: Velocidad de generación de datos
        print("📊 Test 1: Generación de datos sintéticos")
        start_time = time.time()
        test_data = self._generate_real_trading_dataset(1000, "EURUSD")
        gen_time = time.time() - start_time
        
        self.optimization_report['tests']['data_generation'] = {
            'time_seconds': gen_time,
            'velas_per_second': 1000 / gen_time,
            'memory_usage_kb': test_data.memory_usage(deep=True).sum() / 1024
        }
        
        print(f"   ⏱️  Tiempo: {gen_time:.3f}s ({1000/gen_time:.0f} velas/s)")
        print(f"   💾 Memoria: {test_data.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        # Test 2: Detección de patrones
        print("📊 Test 2: Detección de patrones")
        detector = ICTPatternDetector()
        start_time = time.time()
        patterns = detector.detect_patterns(test_data, 'M15')
        detect_time = time.time() - start_time
        
        self.optimization_report['tests']['pattern_detection'] = {
            'time_seconds': detect_time,
            'velas_per_second': 1000 / detect_time,
            'patterns_found': len(patterns)
        }
        
        print(f"   ⏱️  Tiempo: {detect_time:.3f}s ({1000/detect_time:.0f} velas/s)")
        print(f"   🎯 Patrones: {len(patterns)}")
        
        # Test 3: Sistema de memoria
        print("📊 Test 3: Sistema de memoria unificada")
        start_time = time.time()
        memory_system = get_unified_memory_system()
        memory_time = time.time() - start_time
        
        self.optimization_report['tests']['memory_system'] = {
            'initialization_time_ms': memory_time * 1000,
            'components_loaded': 3
        }
        
        print(f"   ⏱️  Inicialización: {memory_time*1000:.1f}ms")
        
    def test_parallel_processing(self):
        """Prueba el procesamiento en paralelo"""
        print("\n🚀 TEST DE PROCESAMIENTO PARALELO")
        print("=" * 50)
        
        symbols = ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY']
        timeframes = ['M15', 'H1']
        
        # Procesamiento secuencial
        print("📊 Procesamiento SECUENCIAL")
        start_time = time.time()
        sequential_results = []
        for symbol in symbols:
            for tf in timeframes:
                result = self._process_symbol_timeframe_sync(symbol, tf)
                sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        print(f"   ⏱️  Tiempo total: {sequential_time:.3f}s")
        print(f"   🎯 Combinaciones procesadas: {len(sequential_results)}")
        
        # Inicializar pool de detectores para optimizar paralelismo
        print("📊 Procesamiento PARALELO OPTIMIZADO (Detector Pool)")
        self._initialize_detector_pool(4)
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=4) as executor:
            tasks = []
            for i, (symbol, tf) in enumerate([(s, t) for s in symbols for t in timeframes]):
                task = executor.submit(self._process_symbol_timeframe_optimized, symbol, tf, i % 4)
                tasks.append(task)
            parallel_results = [task.result() for task in tasks]
        parallel_time = time.time() - start_time
        
        print(f"   ⏱️  Tiempo total: {parallel_time:.3f}s")
        print(f"   🎯 Combinaciones procesadas: {len(parallel_results)}")
        
        # Comparar con método original no optimizado
        print("📊 Procesamiento PARALELO (ThreadPool No Optimizado)")
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=4) as executor:
            tasks = []
            for symbol in symbols:
                for tf in timeframes:
                    task = executor.submit(self._process_symbol_timeframe_sync, symbol, tf)
                    tasks.append(task)
            parallel_results_old = [task.result() for task in tasks]
        parallel_time_old = time.time() - start_time
        
        print(f"   ⏱️  Tiempo total: {parallel_time_old:.3f}s")
        print(f"   🎯 Combinaciones procesadas: {len(parallel_results_old)}")
        
        # Calcular mejoras
        speedup_optimized = sequential_time / parallel_time if parallel_time > 0 else 0
        speedup_old = sequential_time / parallel_time_old if parallel_time_old > 0 else 0
        
        print(f"   📈 Mejora Optimizada: {speedup_optimized:.1f}x más rápido")
        print(f"   📈 Mejora Original: {speedup_old:.1f}x más rápido")
        print(f"   🚀 Optimización vs Original: {parallel_time_old/parallel_time:.1f}x mejor")
        
        self.optimization_report['tests']['parallel_processing'] = {
            'sequential_time': sequential_time,
            'parallel_time_optimized': parallel_time,
            'parallel_time_original': parallel_time_old,
            'speedup_factor_optimized': speedup_optimized,
            'speedup_factor_original': speedup_old,
            'optimization_improvement': parallel_time_old / parallel_time if parallel_time > 0 else 1,
            'combinations_processed': len(parallel_results)
        }
        
    def analyze_memory_optimization(self):
        """Analiza optimizaciones de memoria"""
        print("\n💾 ANÁLISIS DE OPTIMIZACIÓN DE MEMORIA")
        print("=" * 50)
        
        # Test con diferentes tamaños de dataset
        sizes = [100, 500, 1000, 2000]
        memory_usage = []
        processing_times = []
        
        for size in sizes:
            print(f"📊 Probando con {size} velas...")
            
            # Generar datos
            start_time = time.time()
            data = self._generate_real_trading_dataset(size, "EURUSD")
            gen_time = time.time() - start_time
            
            # Medir memoria
            memory_kb = data.memory_usage(deep=True).sum() / 1024
            memory_usage.append(memory_kb)
            
            # Procesar patrones
            detector = ICTPatternDetector()
            start_time = time.time()
            patterns = detector.detect_patterns(data, 'M15')
            process_time = time.time() - start_time
            processing_times.append(process_time)
            
            print(f"   💾 Memoria: {memory_kb:.1f} KB")
            print(f"   ⏱️  Tiempo: {process_time:.3f}s")
            print(f"   📈 Eficiencia: {size/process_time:.0f} velas/s")
        
        self.optimization_report['tests']['memory_scaling'] = {
            'dataset_sizes': sizes,
            'memory_usage_kb': memory_usage,
            'processing_times': processing_times,
            'efficiency_trend': 'linear' if max(processing_times) < min(processing_times) * 5 else 'degrading'
        }
        
    def generate_optimization_recommendations(self):
        """Genera recomendaciones de optimización"""
        print("\n💡 RECOMENDACIONES DE OPTIMIZACIÓN")
        print("=" * 50)
        
        recommendations = []
        
        # Análisis de velocidad de detección
        pattern_speed = self.optimization_report['tests']['pattern_detection']['velas_per_second']
        if pattern_speed < 100000:
            recommendations.append({
                'category': 'Pattern Detection',
                'issue': 'Velocidad de detección de patrones subóptima',
                'recommendation': 'Implementar vectorización NumPy y caching inteligente',
                'priority': 'HIGH',
                'expected_improvement': '2-3x speedup'
            })
        
        # Análisis de memoria
        memory_init = self.optimization_report['tests']['memory_system']['initialization_time_ms']
        if memory_init > 50:
            recommendations.append({
                'category': 'Memory System',
                'issue': 'Inicialización del sistema de memoria lenta',
                'recommendation': 'Implementar lazy loading y cache persistente',
                'priority': 'MEDIUM',
                'expected_improvement': '50-70% reducción en tiempo de inicialización'
            })
        
        # Análisis de procesamiento paralelo
        if 'parallel_processing' in self.optimization_report['tests']:
            speedup_optimized = self.optimization_report['tests']['parallel_processing']['speedup_factor_optimized']
            speedup_original = self.optimization_report['tests']['parallel_processing']['speedup_factor_original']
            optimization_improvement = self.optimization_report['tests']['parallel_processing']['optimization_improvement']
            
            if speedup_original < 1.5:
                recommendations.append({
                    'category': 'Parallel Processing - Original Method',
                    'issue': f'Método original tiene overhead excesivo (speedup: {speedup_original:.1f}x)',
                    'recommendation': 'Usar detector pooling en lugar de crear instancias nuevas por thread',
                    'priority': 'HIGH',
                    'expected_improvement': f'Demostrado: {optimization_improvement:.1f}x mejora con pooling'
                })
            
            if speedup_optimized < 2.0:
                recommendations.append({
                    'category': 'Parallel Processing - Advanced',
                    'issue': f'Pooling básico aún subóptimo (speedup: {speedup_optimized:.1f}x)',
                    'recommendation': 'Implementar shared memory, batch processing y trabajo asíncrono',
                    'priority': 'MEDIUM',
                    'expected_improvement': 'Target: 3-4x speedup con optimizaciones avanzadas'
                })
        
        # Recomendaciones específicas
        recommendations.extend([
            {
                'category': 'Data Storage',
                'issue': 'I/O frecuente en almacenamiento',
                'recommendation': 'Implementar batch writing y compresión inteligente',
                'priority': 'MEDIUM',
                'expected_improvement': '30-40% reducción en tiempo de I/O'
            },
            {
                'category': 'Cache Strategy',
                'issue': 'Cache no persistente entre sesiones',
                'recommendation': 'Implementar cache persistente con TTL inteligente',
                'priority': 'MEDIUM',
                'expected_improvement': '60-80% reducción en cold starts'
            },
            {
                'category': 'Algorithm Optimization',
                'issue': 'Algoritmos de detección pueden ser más eficientes',
                'recommendation': 'Implementar early exit conditions y pre-filtering',
                'priority': 'LOW',
                'expected_improvement': '15-25% mejora en casos específicos'
            }
        ])
        
        self.optimization_report['recommendations'] = recommendations
        
        for i, rec in enumerate(recommendations, 1):
            print(f"🔧 {i}. {rec['category']} - {rec['priority']}")
            print(f"   ❌ Problema: {rec['issue']}")
            print(f"   ✅ Solución: {rec['recommendation']}")
            print(f"   📈 Mejora esperada: {rec['expected_improvement']}")
            print()
        
    def save_optimization_report(self):
        """Guarda el reporte de optimización"""
        # Crear directorio de reportes si no existe
        reports_dir = os.path.join(project_root, "04-DATA", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        report_path = os.path.join(reports_dir, "optimization_analysis_report.json")
        
        # Calcular métricas finales
        self.optimization_report['summary'] = {
            'current_performance_rating': self._calculate_performance_rating(),
            'optimization_potential': 'HIGH' if len(self.optimization_report['recommendations']) > 3 else 'MEDIUM',
            'priority_optimizations': len([r for r in self.optimization_report['recommendations'] if r['priority'] == 'HIGH']),
            'estimated_improvement_range': '50-200% overall performance gain'
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Reporte guardado en: {report_path}")
        
    def _generate_real_trading_dataset(self, num_candles: int, symbol: str = "EURUSD") -> pd.DataFrame:
        """Genera dataset de trading realista con validaciones estrictas"""
        print(f"📊 Generando {num_candles} velas de {symbol} para trading real...")
        
        # Usar datos históricos reales si están disponibles
        try:
            downloader = AdvancedCandleDownloader()
            real_data = downloader.download_ohlc_data(
                symbol=symbol,
                timeframe='M15',
                num_candles=num_candles
            )
            
            if real_data is not None and not real_data.empty:
                print(f"✅ Datos reales obtenidos: {len(real_data)} velas de {symbol}")
                return self._validate_trading_data(real_data, symbol)
                
        except Exception as e:
            print(f"⚠️ No se pudieron obtener datos reales de {symbol}: {e}")
        
        # Generar datos sintéticos REALISTAS para testing si no hay datos reales
        print(f"🔄 Generando datos sintéticos realistas para {symbol}...")
        
        dates = pd.date_range(start='2025-01-01', periods=num_candles, freq='15min')
        
        # Precios base realistas para EURUSD
        base_price = 1.0850 if symbol == "EURUSD" else 1.2500
        
        # Simulación de movimiento de precio realista
        np.random.seed(42)  # Para reproducibilidad
        returns = np.random.normal(0, 0.0001, num_candles)  # Volatilidad realista
        
        prices = [base_price]
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(0.5, min(2.0, new_price)))  # Límites realistas
        
        # Generar OHLC con spreads y volatilidad realistas
        spread = 0.00015  # Spread típico de EURUSD
        data = []
        
        for i, (date, close) in enumerate(zip(dates, prices)):
            # Volatilidad intracandle realista
            volatility = np.random.normal(0, 0.00005)
            
            high = close + abs(volatility) + spread/2
            low = close - abs(volatility) - spread/2
            open_price = prices[i-1] if i > 0 else close
            
            data.append({
                'datetime': date,
                'open': round(open_price, 5),
                'high': round(high, 5),
                'low': round(low, 5),
                'close': round(close, 5),
                'volume': np.random.randint(100, 1000)  # Volumen simulado
            })
        
        df = pd.DataFrame(data)
        print(f"✅ Dataset sintético generado: {len(df)} velas con precios realistas")
        
        return self._validate_trading_data(df, symbol)
    
    def _validate_trading_data(self, data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Validaciones estrictas para datos de trading real"""
        if data is None or data.empty:
            raise ValueError(f"❌ TRADING CRITICAL: Dataset vacío para {symbol}")
        
        required_cols = ['open', 'high', 'low', 'close']
        missing = [col for col in required_cols if col not in data.columns]
        if missing:
            raise ValueError(f"❌ TRADING CRITICAL: Faltan columnas OHLC: {missing}")
        
        # Verificar datos None o NaN
        null_counts = data[required_cols].isnull().sum()
        if null_counts.any():
            raise ValueError(f"❌ TRADING CRITICAL: Valores nulos en OHLC: {null_counts.to_dict()}")
        
        # Validar lógica de precios
        invalid_high_low = (data['high'] < data['low']).sum()
        if invalid_high_low > 0:
            raise ValueError(f"❌ TRADING CRITICAL: {invalid_high_low} velas con High < Low")
        
        invalid_close = ((data['close'] > data['high']) | (data['close'] < data['low'])).sum()
        if invalid_close > 0:
            raise ValueError(f"❌ TRADING CRITICAL: {invalid_close} velas con Close fuera de rango")
        
        # Verificar precios realistas (no ceros, negativos o extremos)
        for col in required_cols:
            if (data[col] <= 0).any():
                raise ValueError(f"❌ TRADING CRITICAL: Precios <= 0 detectados en {col}")
            if (data[col] > 1000).any():  # Límite superior realista
                raise ValueError(f"❌ TRADING CRITICAL: Precios irrealmente altos en {col}")
        
        print(f"✅ TRADING VALIDATION: {symbol} - {len(data)} velas validadas sin errores")
        return data
    
    def _process_symbol_timeframe_sync(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Procesa un símbolo y timeframe de forma síncrona"""
        data = self._generate_real_trading_dataset(500, symbol)
        detector = ICTPatternDetector()
        patterns = detector.detect_patterns(data, timeframe)
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'patterns': len(patterns),
            'processed': True
        }
    
    def _initialize_detector_pool(self, pool_size: int):
        """Inicializa pool de detectores reutilizables"""
        print(f"   🔧 Inicializando pool de {pool_size} detectores...")
        self._detector_pool = []
        
        # Inicializar memoria una sola vez
        if self._memory_system is None:
            self._memory_system = get_unified_memory_system()
        
        # Crear pool de detectores pre-inicializados
        for i in range(pool_size):
            detector = ICTPatternDetector()
            self._detector_pool.append(detector)
            
        print(f"   ✅ Pool inicializado con {len(self._detector_pool)} detectores")
    
    def _process_symbol_timeframe_optimized(self, symbol: str, timeframe: str, detector_index: int) -> Dict[str, Any]:
        """Procesa usando detector del pool para evitar overhead de inicialización"""
        data = self._generate_real_trading_dataset(500, symbol)
        
        # Usar detector del pool (thread-safe)
        detector = self._detector_pool[detector_index]
        patterns = detector.detect_patterns(data, timeframe)
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'patterns': len(patterns),
            'processed': True,
            'optimized': True
        }
    
    def _calculate_performance_rating(self) -> str:
        """Calcula rating de rendimiento actual"""
        pattern_speed = self.optimization_report['tests']['pattern_detection']['velas_per_second']
        
        if pattern_speed > 500000:
            return 'EXCELLENT'
        elif pattern_speed > 200000:
            return 'GOOD'
        elif pattern_speed > 100000:
            return 'FAIR'
        else:
            return 'NEEDS_IMPROVEMENT'

class AdvancedParallelOptimizer:
    """Optimizador paralelo avanzado que integra todos los módulos de optimización"""
    
    def __init__(self, pool_size: Optional[int] = None):
        self.pool_size = pool_size or cpu_count()
        self.detector_pool: Optional[EnhancedDetectorPoolManager] = None
        self.shared_memory: Optional[SharedMemoryOptimizer] = None
        self.work_engine: Optional[WorkDistributionEngine] = None
        self.performance_stats = {
            'baseline_time': 0.0,
            'optimized_time': 0.0,
            'speedup_factor': 0.0,
            'memory_savings': 0.0,
            'efficiency_score': 0.0
        }
        
    def initialize_advanced_optimization(self):
        """Inicializa todos los componentes de optimización avanzada"""
        print("🔧 Inicializando optimización avanzada...")
        
        # Inicializar pool de detectores
        self.detector_pool = EnhancedDetectorPoolManager(pool_size=self.pool_size)
        print(f"   ✅ Pool de detectores: {self.pool_size} workers")
        
        # Inicializar memoria compartida
        self.shared_memory = SharedMemoryOptimizer()
        print("   ✅ Optimizador de memoria compartida")
        
        # Inicializar motor de distribución de trabajo
        self.work_engine = WorkDistributionEngine(pool_size=self.pool_size)
        print("   ✅ Motor de distribución de trabajo")
        
    def run_advanced_benchmark(self, test_data: pd.DataFrame) -> Dict[str, Any]:
        """Ejecuta benchmark con optimización avanzada"""
        print("\n🚀 EJECUTANDO BENCHMARK AVANZADO")
        print("=" * 50)
        
        results = {}
        
        # Benchmark sin optimización (baseline)
        print("📊 Baseline (sin optimización):")
        start_time = time.time()
        baseline_results = self._run_baseline_analysis(test_data)
        baseline_time = time.time() - start_time
        results['baseline'] = {
            'time': baseline_time,
            'patterns_found': len(baseline_results),
            'memory_peak': self._get_memory_usage()
        }
        print(f"   ⏱️  Tiempo: {baseline_time:.3f}s")
        print(f"   🎯 Patrones: {len(baseline_results)}")
        
        # Benchmark con optimización avanzada
        print("\n📊 Optimizado (pool + memoria compartida + distribución):")
        start_time = time.time()
        optimized_results = self._run_optimized_analysis(test_data)
        optimized_time = time.time() - start_time
        results['optimized'] = {
            'time': optimized_time,
            'patterns_found': len(optimized_results),
            'memory_peak': self._get_memory_usage()
        }
        print(f"   ⏱️  Tiempo: {optimized_time:.3f}s")
        print(f"   🎯 Patrones: {len(optimized_results)}")
        
        # Calcular mejoras
        speedup = baseline_time / optimized_time if optimized_time > 0 else 0
        efficiency = (speedup / self.pool_size) * 100
        memory_savings = ((results['baseline']['memory_peak'] - results['optimized']['memory_peak']) / 
                         results['baseline']['memory_peak']) * 100
        
        results['performance'] = {
            'speedup_factor': speedup,
            'efficiency_percent': efficiency,
            'memory_savings_percent': memory_savings,
            'optimal_threads': self._calculate_optimal_threads()
        }
        
        print(f"\n🎯 RESULTADOS:")
        print(f"   🚀 Speedup: {speedup:.2f}x")
        print(f"   📈 Eficiencia: {efficiency:.1f}%")
        print(f"   💾 Ahorro memoria: {memory_savings:.1f}%")
        
        return results
        
    def _run_baseline_analysis(self, data: pd.DataFrame) -> List[Dict]:
        """Ejecuta análisis secuencial como baseline"""
        detector = ICTPatternDetector()
        return detector.detect_patterns(data, 'M15')
        
    def _run_optimized_analysis(self, data: pd.DataFrame) -> List[Dict]:
        """Ejecuta análisis optimizado con todos los componentes"""
        symbol = "EURUSD"  # Símbolo para trading real
        
        # Dividir datos en chunks para procesamiento paralelo
        chunk_size = max(50, len(data) // self.pool_size)  # Mínimo 50 velas por chunk
        chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        
        # Crear tareas de análisis con validación para trading real
        tasks = []
        for i, chunk in enumerate(chunks):
            try:
                task = AnalysisTask(
                    task_id=f"trading_chunk_{symbol}_{i}",
                    data=chunk,
                    timeframe='M15',
                    symbol=symbol,
                    analysis_type='pattern_detection',
                    priority=1
                )
                tasks.append(task)
                
            except ValueError as e:
                print(f"⚠️ Chunk {i} descartado por datos inválidos: {e}")
                continue
        
        if not tasks:
            print("❌ TRADING CRITICAL: No hay chunks válidos para procesar")
            return []
        
        print(f"✅ TRADING READY: {len(tasks)} chunks válidos para análisis paralelo")
        
        # Procesar con pool optimizado
        all_results = []
        if self.detector_pool:
            results = self.detector_pool.process_batch(tasks)
            
            for result in results:
                if result.success and result.patterns:
                    all_results.extend(result.patterns)
                elif not result.success:
                    print(f"⚠️ Task {result.task_id} falló: {result.error_msg}")
        else:
            # Fallback sin pool - no debe ocurrir en trading real
            print("⚠️ TRADING WARNING: Usando fallback sin pool")
            detector = ICTPatternDetector()
            for task in tasks:
                try:
                    patterns = detector.detect_patterns(task.data, task.timeframe)
                    all_results.extend(patterns)
                except Exception as e:
                    print(f"❌ Error procesando task {task.task_id}: {e}")
                    
        return all_results
        
    def _get_memory_usage(self) -> float:
        """Obtiene el uso actual de memoria en MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            print("⚠️ psutil no disponible, usando estimación de memoria")
            return 100.0  # Estimación base
        
    def _calculate_optimal_threads(self) -> int:
        """Calcula el número óptimo de threads basado en resultados"""
        # Lógica simple: usar 75% de cores disponibles para análisis de trading
        return max(1, int(cpu_count() * 0.75))
        
    def cleanup(self):
        """Limpia recursos de optimización"""
        if self.detector_pool:
            self.detector_pool.shutdown()
        if self.work_engine:
            self.work_engine.shutdown()
        print("🧹 Recursos de optimización liberados")


def main():
    """Función principal de optimización"""
    print("🚀 ICT ENGINE v6.0 - ANÁLISIS DE OPTIMIZACIÓN DE DATOS")
    print("=" * 65)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🖥️  CPU Cores: {cpu_count()}")
    print()
    
    optimizer = DataProcessingOptimizer()
    
    try:
        # Ejecutar análisis
        optimizer.analyze_current_performance()
        optimizer.test_parallel_processing()
        optimizer.analyze_memory_optimization()
        optimizer.generate_optimization_recommendations()
        optimizer.save_optimization_report()
        
        print("\n🎯 RESUMEN EJECUTIVO:")
        rating = optimizer.optimization_report['summary']['current_performance_rating']
        potential = optimizer.optimization_report['summary']['optimization_potential']
        high_priority = optimizer.optimization_report['summary']['priority_optimizations']
        
        print(f"   📊 Rating actual: {rating}")
        print(f"   🚀 Potencial de optimización: {potential}")
        print(f"   🔧 Optimizaciones prioritarias: {high_priority}")
        print(f"   📈 Mejora estimada: {optimizer.optimization_report['summary']['estimated_improvement_range']}")
        
        # Ejecutar benchmark avanzado
        print("\n" + "="*60)
        print("🔥 BENCHMARK AVANZADO CON OPTIMIZACIÓN PARALELA")
        print("="*60)
        
        advanced_optimizer = AdvancedParallelOptimizer()
        advanced_optimizer.initialize_advanced_optimization()
        
        # Generar datos de test más grandes para el benchmark avanzado
        test_data = optimizer._generate_real_trading_dataset(5000, "EURUSD")  # Dataset más grande
        
        # Ejecutar benchmark avanzado
        advanced_results = advanced_optimizer.run_advanced_benchmark(test_data)
        
        # Guardar resultados avanzados
        advanced_reports_dir = os.path.join(project_root, "04-DATA", "reports")
        os.makedirs(advanced_reports_dir, exist_ok=True)
        
        advanced_report_path = os.path.join(advanced_reports_dir, "advanced_optimization_report.json")
        
        with open(advanced_report_path, 'w') as f:
            json.dump(advanced_results, f, indent=2, default=str)
        
        print(f"\n📊 Reporte avanzado guardado en: {advanced_report_path}")
        
        # Cleanup
        advanced_optimizer.cleanup()
        
        print("\n✅ ANÁLISIS COMPLETADO")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
