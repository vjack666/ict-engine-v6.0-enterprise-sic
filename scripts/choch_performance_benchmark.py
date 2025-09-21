"""
CHoCH Performance Benchmark - Sistema de métricas de rendimiento
Mide el impacto de las optimizaciones CHoCH en el sistema
"""

import time
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from statistics import mean, stdev

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent / '01-CORE'))

try:
    from memory.choch_historical_memory import get_choch_historical_memory, compute_historical_bonus
    from memory.choch_cache import get_choch_cache, clear_choch_cache
    from config.choch_config import get_choch_config
except ImportError as e:
    print(f"❌ Error importing CHoCH modules: {e}")
    sys.exit(1)


class CHoCHPerformanceBenchmark:
    """Benchmark para medir performance de CHoCH Memory y Cache"""
    
    def __init__(self):
        self.results = {}
        self.test_symbols = ["EURUSD", "GBPUSD", "USDCAD", "AUDUSD"]
        self.test_timeframes = ["H4", "H1", "M15", "M5"]
        self.test_break_levels = [1.1000, 1.1050, 1.1100, 1.1150, 1.1200]
    
    def warm_up_memory_system(self):
        """Warm-up del sistema de memoria CHoCH"""
        print("🔥 Calentando sistema CHoCH Memory...")
        try:
            memory = get_choch_historical_memory()
            # Simular algunas consultas para warm-up
            for symbol in self.test_symbols[:2]:
                for tf in self.test_timeframes[:2]:
                    memory.calculate_historical_success_rate(symbol, tf)
            print("✅ Sistema calentado")
        except Exception as e:
            print(f"⚠️ Warning en warm-up: {e}")
    
    def benchmark_choch_queries_without_cache(self, iterations: int = 50) -> Dict[str, float]:
        """Benchmark consultas CHoCH sin cache"""
        print(f"📊 Benchmarking CHoCH queries SIN cache ({iterations} iteraciones)...")
        
        # Clear cache para benchmark limpio
        clear_choch_cache()
        
        times = []
        
        for i in range(iterations):
            symbol = self.test_symbols[i % len(self.test_symbols)]
            timeframe = self.test_timeframes[i % len(self.test_timeframes)]
            break_level = self.test_break_levels[i % len(self.test_break_levels)]
            
            start_time = time.perf_counter()
            result = compute_historical_bonus(symbol=symbol, timeframe=timeframe, break_level=break_level)
            end_time = time.perf_counter()
            
            query_time = (end_time - start_time) * 1000  # Convert to ms
            times.append(query_time)
            
            if i % 10 == 0:
                print(f"  Query {i+1}/{iterations}: {query_time:.2f}ms")
        
        return {
            'mean_time_ms': mean(times),
            'max_time_ms': max(times),
            'min_time_ms': min(times),
            'std_dev_ms': stdev(times) if len(times) > 1 else 0.0,
            'total_time_ms': sum(times),
            'iterations': iterations
        }
    
    def benchmark_choch_queries_with_cache(self, iterations: int = 50) -> Dict[str, float]:
        """Benchmark consultas CHoCH con cache"""
        print(f"📊 Benchmarking CHoCH queries CON cache ({iterations} iteraciones)...")
        
        # Clear cache y warm-up
        clear_choch_cache()
        cache = get_choch_cache()
        
        times = []
        cache_hits = 0
        
        for i in range(iterations):
            symbol = self.test_symbols[i % len(self.test_symbols)]
            timeframe = self.test_timeframes[i % len(self.test_timeframes)]
            break_level = self.test_break_levels[i % len(self.test_break_levels)]
            
            # Check if it would be a cache hit
            cached_result = cache.get_historical_bonus(symbol, timeframe, break_level)
            if cached_result is not None:
                cache_hits += 1
            
            start_time = time.perf_counter()
            result = compute_historical_bonus(symbol=symbol, timeframe=timeframe, break_level=break_level)
            end_time = time.perf_counter()
            
            query_time = (end_time - start_time) * 1000  # Convert to ms
            times.append(query_time)
            
            if i % 10 == 0:
                print(f"  Query {i+1}/{iterations}: {query_time:.2f}ms (Cache hits: {cache_hits})")
        
        return {
            'mean_time_ms': mean(times),
            'max_time_ms': max(times),
            'min_time_ms': min(times),
            'std_dev_ms': stdev(times) if len(times) > 1 else 0.0,
            'total_time_ms': sum(times),
            'cache_hits': cache_hits,
            'cache_hit_rate': (cache_hits / iterations) * 100.0,
            'iterations': iterations
        }
    
    def benchmark_low_memory_mode(self) -> Dict[str, Any]:
        """Benchmark modo low-memory vs normal"""
        print("🧠 Benchmarking modo Low-Memory...")
        
        results = {}
        
        # Test normal mode
        os.environ.pop('ICT_LOW_MEM', None)  # Remove if set
        
        start_time = time.perf_counter()
        normal_config = get_choch_config('FVG', low_memory=False)
        normal_time = (time.perf_counter() - start_time) * 1000
        
        # Test low-memory mode
        os.environ['ICT_LOW_MEM'] = '1'
        
        start_time = time.perf_counter()
        low_mem_config = get_choch_config('FVG', low_memory=True)
        low_mem_time = (time.perf_counter() - start_time) * 1000
        
        results = {
            'normal_mode': {
                'config_time_ms': normal_time,
                'max_records': normal_config.get('max_historical_samples', 1000),
                'ttl_seconds': normal_config.get('cache_ttl_seconds', 300)
            },
            'low_memory_mode': {
                'config_time_ms': low_mem_time,
                'max_records': low_mem_config.get('max_samples', 200),
                'ttl_seconds': low_mem_config.get('cache_ttl_seconds', 60)
            }
        }
        
        # Reset environment
        os.environ.pop('ICT_LOW_MEM', None)
        
        return results
    
    def run_full_benchmark(self) -> Dict[str, Any]:
        """Ejecutar benchmark completo"""
        print("🚀 Iniciando benchmark completo de CHoCH Performance...")
        print("=" * 60)
        
        self.warm_up_memory_system()
        
        # Benchmark sin cache
        no_cache_results = self.benchmark_choch_queries_without_cache(30)
        
        print("\n" + "─" * 40)
        
        # Benchmark con cache
        with_cache_results = self.benchmark_choch_queries_with_cache(50)  # More iterations to show cache benefit
        
        print("\n" + "─" * 40)
        
        # Benchmark low-memory mode
        memory_mode_results = self.benchmark_low_memory_mode()
        
        # Calculate improvements
        cache_improvement = ((no_cache_results['mean_time_ms'] - with_cache_results['mean_time_ms']) / no_cache_results['mean_time_ms']) * 100.0
        
        final_results = {
            'without_cache': no_cache_results,
            'with_cache': with_cache_results,
            'memory_modes': memory_mode_results,
            'performance_improvement': {
                'cache_speedup_percent': cache_improvement,
                'cache_hit_rate': with_cache_results.get('cache_hit_rate', 0.0)
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'test_configuration': {
                'symbols_tested': len(self.test_symbols),
                'timeframes_tested': len(self.test_timeframes),
                'break_levels_tested': len(self.test_break_levels)
            }
        }
        
        return final_results
    
    def print_results(self, results: Dict[str, Any]):
        """Imprimir resultados del benchmark"""
        print("\n" + "🎯 RESULTADOS DEL BENCHMARK CHoCH" + "\n" + "=" * 60)
        
        # Without cache results
        no_cache = results['without_cache']
        print(f"📊 SIN Cache:")
        print(f"  ├── Tiempo promedio: {no_cache['mean_time_ms']:.2f}ms")
        print(f"  ├── Tiempo máximo: {no_cache['max_time_ms']:.2f}ms")
        print(f"  ├── Tiempo mínimo: {no_cache['min_time_ms']:.2f}ms")
        print(f"  └── Desv. estándar: {no_cache['std_dev_ms']:.2f}ms")
        
        # With cache results  
        with_cache = results['with_cache']
        print(f"\n🚀 CON Cache:")
        print(f"  ├── Tiempo promedio: {with_cache['mean_time_ms']:.2f}ms")
        print(f"  ├── Tiempo máximo: {with_cache['max_time_ms']:.2f}ms")
        print(f"  ├── Tiempo mínimo: {with_cache['min_time_ms']:.2f}ms")
        print(f"  ├── Cache hits: {with_cache.get('cache_hits', 0)}")
        print(f"  └── Tasa de aciertos: {with_cache.get('cache_hit_rate', 0):.1f}%")
        
        # Performance improvement
        perf = results['performance_improvement']
        print(f"\n✨ MEJORAS DE RENDIMIENTO:")
        print(f"  ├── Aceleración por cache: {perf['cache_speedup_percent']:.1f}%")
        print(f"  └── Eficiencia de cache: {perf['cache_hit_rate']:.1f}%")
        
        # Memory modes
        mem_modes = results['memory_modes']
        print(f"\n🧠 MODOS DE MEMORIA:")
        print(f"  ├── Modo Normal: {mem_modes['normal_mode']['max_records']} registros máx")
        print(f"  └── Modo Low-Mem: {mem_modes['low_memory_mode']['max_records']} registros máx")
        
        print(f"\n📅 Timestamp: {results['timestamp']}")
        print("=" * 60)


def main():
    """Ejecutar benchmark de CHoCH Performance"""
    benchmark = CHoCHPerformanceBenchmark()
    
    try:
        results = benchmark.run_full_benchmark()
        benchmark.print_results(results)
        
        # Save results to file
        import json
        results_path = Path(__file__).parent.parent / '04-DATA' / 'reports' / 'choch_performance_benchmark.json'
        results_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Resultados guardados en: {results_path}")
        
    except Exception as e:
        print(f"❌ Error en benchmark: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())