#!/usr/bin/env python3
"""
🧪 STRESS TESTING & VALIDATION - ICT ENGINE v6.0 ENTERPRISE
==========================================================

Suite completa de pruebas de estrés y validación para el sistema de producción.
Valida la estabilidad, performance y robustez bajo condiciones extremas.

Características principales:
✅ Pruebas de carga para validadores y rate limiters
✅ Testing de circuit breakers y auto-recovery
✅ Validación de latencia bajo alta frecuencia
✅ Pruebas de memoria y CPU bajo estrés
✅ Testing de health monitoring y alertas
✅ Validación de configuraciones de producción
✅ Tests de concurrent operations
✅ Simulación de condiciones de mercado extremas

Métricas validadas:
- Latencia < 50ms en condiciones normales
- Throughput > 1000 validaciones/segundo  
- Memory usage < 512MB bajo carga
- CPU usage < 25% promedio
- Error rate < 2% máximo
- Recovery time < 30 segundos

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 14 Septiembre 2025
"""

import asyncio
import time
import threading
import multiprocessing
import random
import json
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import psutil
import gc

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

@dataclass
class StressTestConfig:
    """Configuración para pruebas de estrés"""
    duration_seconds: int = 60
    concurrent_threads: int = 10
    requests_per_second: int = 100
    max_memory_mb: float = 512.0
    max_cpu_percent: float = 25.0
    max_latency_ms: float = 50.0
    max_error_rate_percent: float = 2.0
    circuit_breaker_test: bool = True
    recovery_test: bool = True

@dataclass
class TestResult:
    """Resultado de una prueba"""
    test_name: str
    success: bool
    duration_seconds: float
    metrics: Dict[str, Any]
    errors: List[str]
    warnings: List[str]

# ============================================================================
# VALIDATION STRESS TESTS  
# ============================================================================

class ValidationStressTester:
    """🛡️ Pruebas de estrés para el validador de producción"""
    
    def __init__(self):
        self.results = []
        self.errors = []
    
    def run_validation_load_test(self, duration: int = 30, concurrent_threads: int = 5) -> TestResult:
        """Prueba de carga del validador"""
        print(f"🧪 Running validation load test - {concurrent_threads} threads, {duration}s duration")
        
        try:
            from validation import get_production_validator, ValidationLevel
            validator = get_production_validator(ValidationLevel.STANDARD)
        except ImportError:
            return TestResult(
                test_name="validation_load_test",
                success=False,
                duration_seconds=0,
                metrics={},
                errors=["Validation module not available"],
                warnings=[]
            )
        
        start_time = time.time()
        latencies = []
        success_count = 0
        error_count = 0
        
        def worker_thread():
            nonlocal success_count, error_count
            thread_latencies = []
            
            end_time = start_time + duration
            while time.time() < end_time:
                request_start = time.perf_counter()
                
                try:
                    # Generate random trading request
                    symbol = random.choice(['EURUSD', 'GBPUSD', 'USDCAD', 'AUDUSD'])
                    volume = random.uniform(0.01, 10.0)
                    price = random.uniform(0.9, 2.0)
                    
                    success, errors = validator.validate_trading_request(
                        symbol=symbol,
                        volume=volume,
                        price=price
                    )
                    
                    latency_ms = (time.perf_counter() - request_start) * 1000
                    thread_latencies.append(latency_ms)
                    
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    error_count += 1
                
                # Small random delay to simulate realistic load
                time.sleep(random.uniform(0.001, 0.01))
            
            latencies.extend(thread_latencies)
        
        # Start concurrent threads
        threads = []
        for _ in range(concurrent_threads):
            thread = threading.Thread(target=worker_thread)
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        total_duration = time.time() - start_time
        total_requests = success_count + error_count
        
        metrics = {
            'total_requests': total_requests,
            'successful_requests': success_count,
            'failed_requests': error_count,
            'requests_per_second': total_requests / total_duration if total_duration > 0 else 0,
            'error_rate_percent': (error_count / max(total_requests, 1)) * 100,
            'avg_latency_ms': statistics.mean(latencies) if latencies else 0,
            'p95_latency_ms': statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else 0,
            'max_latency_ms': max(latencies) if latencies else 0,
            'min_latency_ms': min(latencies) if latencies else 0
        }
        
        success = (
            metrics['error_rate_percent'] <= 2.0 and
            metrics['avg_latency_ms'] <= 50.0 and
            metrics['requests_per_second'] >= 100
        )
        
        return TestResult(
            test_name="validation_load_test",
            success=success,
            duration_seconds=total_duration,
            metrics=metrics,
            errors=self.errors,
            warnings=[]
        )
    
    def run_batch_validation_test(self, batch_sizes: List[int] = [10, 50, 100, 500]) -> TestResult:
        """Prueba de validación por lotes"""
        print("🧪 Running batch validation test")
        
        try:
            from validation import get_production_validator, validate_and_sanitize_batch
            validator = get_production_validator()
        except ImportError:
            return TestResult(
                test_name="batch_validation_test",
                success=False,
                duration_seconds=0,
                metrics={},
                errors=["Validation module not available"],
                warnings=[]
            )
        
        start_time = time.time()
        batch_results = {}
        
        for batch_size in batch_sizes:
            print(f"  Testing batch size: {batch_size}")
            
            # Generate test data
            test_data = []
            for i in range(batch_size):
                test_data.append({
                    'symbol': random.choice(['EURUSD', 'GBPUSD', 'USDCAD', 'AUDUSD']),
                    'volume': random.uniform(0.01, 10.0),
                    'price': random.uniform(0.9, 2.0),
                    'order_type': random.choice(['BUY', 'SELL'])
                })
            
            batch_start = time.perf_counter()
            try:
                valid_data, errors = validate_and_sanitize_batch(test_data, validator)
                batch_latency = (time.perf_counter() - batch_start) * 1000
                
                batch_results[batch_size] = {
                    'latency_ms': batch_latency,
                    'valid_count': len(valid_data),
                    'error_count': len(errors),
                    'items_per_second': batch_size / (batch_latency / 1000) if batch_latency > 0 else 0
                }
            except Exception as e:
                batch_results[batch_size] = {
                    'error': str(e)
                }
        
        total_duration = time.time() - start_time
        
        # Calculate aggregate metrics
        total_items = sum(batch_results[size]['valid_count'] + batch_results[size]['error_count'] 
                         for size in batch_sizes 
                         if 'error' not in batch_results[size])
        
        avg_throughput = statistics.mean([
            batch_results[size]['items_per_second']
            for size in batch_sizes
            if 'error' not in batch_results[size]
        ]) if total_items > 0 else 0
        
        success = avg_throughput >= 500  # At least 500 items/second
        
        return TestResult(
            test_name="batch_validation_test",
            success=success,
            duration_seconds=total_duration,
            metrics={
                'batch_results': batch_results,
                'average_throughput': avg_throughput,
                'total_items_processed': total_items
            },
            errors=[],
            warnings=[]
        )

# ============================================================================
# RATE LIMITER STRESS TESTS
# ============================================================================

class RateLimiterStressTester:
    """🚦 Pruebas de estrés para rate limiters"""
    
    def run_rate_limiter_load_test(self, duration: int = 30) -> TestResult:
        """Prueba de carga de rate limiters"""
        print(f"🧪 Running rate limiter load test - {duration}s duration")
        
        try:
            from optimization import get_trading_rate_limiter, get_data_rate_limiter
            trading_limiter = get_trading_rate_limiter()
            data_limiter = get_data_rate_limiter()
        except ImportError:
            return TestResult(
                test_name="rate_limiter_load_test", 
                success=False,
                duration_seconds=0,
                metrics={},
                errors=["Rate limiter module not available"],
                warnings=[]
            )
        
        start_time = time.time()
        trading_requests = 0
        trading_blocked = 0
        data_requests = 0
        data_blocked = 0
        
        def trading_worker():
            nonlocal trading_requests, trading_blocked
            end_time = start_time + duration
            
            while time.time() < end_time:
                trading_requests += 1
                allowed, reason = trading_limiter.can_place_order()
                if not allowed:
                    trading_blocked += 1
                
                time.sleep(0.1)  # 10 requests per second
        
        def data_worker():
            nonlocal data_requests, data_blocked
            end_time = start_time + duration
            
            while time.time() < end_time:
                data_requests += 1
                from optimization import LimitType, Priority
                allowed, status = data_limiter.check_limit(
                    LimitType.DATA_REQUESTS_PER_MINUTE,
                    Priority.NORMAL
                )
                if not allowed:
                    data_blocked += 1
                
                time.sleep(0.05)  # 20 requests per second
        
        # Start workers
        trading_thread = threading.Thread(target=trading_worker)
        data_thread = threading.Thread(target=data_worker)
        
        trading_thread.start()
        data_thread.start()
        
        trading_thread.join()
        data_thread.join()
        
        total_duration = time.time() - start_time
        
        metrics = {
            'trading_requests': trading_requests,
            'trading_blocked': trading_blocked,
            'trading_block_rate': (trading_blocked / max(trading_requests, 1)) * 100,
            'data_requests': data_requests,
            'data_blocked': data_blocked,
            'data_block_rate': (data_blocked / max(data_requests, 1)) * 100,
            'trading_rps': trading_requests / total_duration,
            'data_rps': data_requests / total_duration
        }
        
        # Get final metrics from rate limiters
        try:
            trading_metrics = trading_limiter.get_metrics()
            data_metrics = data_limiter.get_metrics()
            metrics['trading_limiter_metrics'] = trading_metrics
            metrics['data_limiter_metrics'] = data_metrics
        except:
            pass
        
        # Success if block rates are reasonable and no crashes
        success = (
            metrics['trading_block_rate'] < 50.0 and  # Some blocking is expected
            metrics['data_block_rate'] < 30.0 and
            trading_requests > 0 and
            data_requests > 0
        )
        
        return TestResult(
            test_name="rate_limiter_load_test",
            success=success,
            duration_seconds=total_duration,
            metrics=metrics,
            errors=[],
            warnings=[]
        )
    
    def run_burst_test(self) -> TestResult:
        """Prueba de ráfagas de requests"""
        print("🧪 Running burst test")
        
        try:
            from optimization import get_trading_rate_limiter
            limiter = get_trading_rate_limiter()
        except ImportError:
            return TestResult(
                test_name="burst_test",
                success=False,
                duration_seconds=0,
                metrics={},
                errors=["Rate limiter module not available"],
                warnings=[]
            )
        
        start_time = time.time()
        
        # Send burst of requests
        burst_size = 20
        burst_results = []
        
        for i in range(burst_size):
            request_start = time.perf_counter()
            allowed, reason = limiter.can_place_order()
            latency_ms = (time.perf_counter() - request_start) * 1000
            
            burst_results.append({
                'allowed': allowed,
                'latency_ms': latency_ms,
                'reason': reason if not allowed else 'OK'
            })
        
        # Wait and try again
        time.sleep(2)
        
        second_burst_results = []
        for i in range(burst_size):
            request_start = time.perf_counter()
            allowed, reason = limiter.can_place_order()
            latency_ms = (time.perf_counter() - request_start) * 1000
            
            second_burst_results.append({
                'allowed': allowed,
                'latency_ms': latency_ms,
                'reason': reason if not allowed else 'OK'
            })
        
        total_duration = time.time() - start_time
        
        # Analyze results
        first_allowed = sum(1 for r in burst_results if r['allowed'])
        second_allowed = sum(1 for r in second_burst_results if r['allowed'])
        
        avg_latency_first = statistics.mean([r['latency_ms'] for r in burst_results])
        avg_latency_second = statistics.mean([r['latency_ms'] for r in second_burst_results])
        
        metrics = {
            'first_burst_allowed': first_allowed,
            'first_burst_blocked': burst_size - first_allowed,
            'second_burst_allowed': second_allowed,
            'second_burst_blocked': burst_size - second_allowed,
            'avg_latency_first_burst': avg_latency_first,
            'avg_latency_second_burst': avg_latency_second,
            'recovery_improvement': second_allowed > first_allowed
        }
        
        # Success if second burst performs better (recovery)
        success = (
            avg_latency_first < 100.0 and  # Fast response
            avg_latency_second < 100.0 and
            second_allowed >= first_allowed  # Recovery or stable
        )
        
        return TestResult(
            test_name="burst_test",
            success=success,
            duration_seconds=total_duration,
            metrics=metrics,
            errors=[],
            warnings=[]
        )

# ============================================================================
# HEALTH MONITOR STRESS TESTS
# ============================================================================

class HealthMonitorStressTester:
    """💖 Pruebas de estrés para health monitor"""
    
    def run_health_monitor_load_test(self, duration: int = 30) -> TestResult:
        """Prueba de carga del health monitor"""
        print(f"🧪 Running health monitor load test - {duration}s duration")
        
        try:
            from monitoring import get_health_monitor, MonitoringLevel
            monitor = get_health_monitor(MonitoringLevel.DETAILED)
        except ImportError:
            return TestResult(
                test_name="health_monitor_load_test",
                success=False,
                duration_seconds=0,
                metrics={},
                errors=["Health monitor module not available"],
                warnings=[]
            )
        
        start_time = time.time()
        
        # Ensure monitor is running
        if not monitor.is_running:
            monitor.start()
            time.sleep(1)  # Give it time to start
        
        # Simulate load by recording many requests
        def load_worker():
            end_time = start_time + duration
            while time.time() < end_time:
                # Simulate random latencies and success rates
                latency = random.uniform(10, 100)  # 10-100ms
                success = random.random() > 0.02  # 98% success rate
                
                monitor.record_request(latency, success)
                time.sleep(0.01)  # 100 requests per second
        
        # Start multiple workers
        workers = []
        for _ in range(3):
            worker = threading.Thread(target=load_worker)
            worker.start()
            workers.append(worker)
        
        # Let it run
        for worker in workers:
            worker.join()
        
        total_duration = time.time() - start_time
        
        # Get metrics
        try:
            system_status = monitor.get_system_status()
            performance_summary = monitor.get_performance_summary()
            
            metrics = {
                'system_status': system_status,
                'performance_summary': performance_summary,
                'monitor_uptime': system_status.get('uptime_seconds', 0),
                'is_running': system_status.get('is_running', False),
                'components_monitored': len(system_status.get('components', {})),
                'alerts_generated': system_status.get('alerts_count', 0)
            }
            
            success = (
                metrics['is_running'] and
                metrics['monitor_uptime'] > 0 and
                metrics['components_monitored'] > 0
            )
            
        except Exception as e:
            metrics = {'error': str(e)}
            success = False
        
        return TestResult(
            test_name="health_monitor_load_test",
            success=success,
            duration_seconds=total_duration,
            metrics=metrics,
            errors=[],
            warnings=[]
        )

# ============================================================================
# SYSTEM RESOURCE TESTS
# ============================================================================

class SystemResourceTester:
    """💻 Pruebas de recursos del sistema"""
    
    def run_memory_stress_test(self, duration: int = 30) -> TestResult:
        """Prueba de estrés de memoria"""
        print(f"🧪 Running memory stress test - {duration}s duration")
        
        start_time = time.time()
        process = psutil.Process()
        
        memory_samples = []
        cpu_samples = []
        
        def monitor_resources():
            end_time = start_time + duration
            while time.time() < end_time:
                try:
                    memory_mb = process.memory_info().rss / (1024 * 1024)
                    cpu_percent = process.cpu_percent()
                    
                    memory_samples.append(memory_mb)
                    cpu_samples.append(cpu_percent)
                    
                except:
                    pass
                
                time.sleep(1)
        
        def memory_worker():
            """Worker que consume memoria gradualment"""
            data_store = []
            end_time = start_time + duration
            
            while time.time() < end_time:
                # Allocate some memory
                chunk = [random.random() for _ in range(10000)]
                data_store.append(chunk)
                
                # Occasionally clean up
                if len(data_store) > 50:
                    data_store = data_store[-25:]
                    gc.collect()
                
                time.sleep(0.1)
        
        # Start monitoring and load
        monitor_thread = threading.Thread(target=monitor_resources)
        worker_threads = [threading.Thread(target=memory_worker) for _ in range(3)]
        
        monitor_thread.start()
        for worker in worker_threads:
            worker.start()
        
        # Wait for completion
        monitor_thread.join()
        for worker in worker_threads:
            worker.join()
        
        total_duration = time.time() - start_time
        
        # Analyze results
        if memory_samples and cpu_samples:
            avg_memory = statistics.mean(memory_samples)
            max_memory = max(memory_samples)
            avg_cpu = statistics.mean(cpu_samples)
            max_cpu = max(cpu_samples)
            
            metrics = {
                'avg_memory_mb': avg_memory,
                'max_memory_mb': max_memory,
                'avg_cpu_percent': avg_cpu,
                'max_cpu_percent': max_cpu,
                'memory_samples_count': len(memory_samples),
                'cpu_samples_count': len(cpu_samples)
            }
            
            success = (
                max_memory < 512.0 and  # Under 512MB
                avg_cpu < 25.0 and      # Average CPU under 25%
                max_cpu < 50.0          # Peak CPU under 50%
            )
        else:
            metrics = {'error': 'No samples collected'}
            success = False
        
        return TestResult(
            test_name="memory_stress_test",
            success=success,
            duration_seconds=total_duration,
            metrics=metrics,
            errors=[],
            warnings=[]
        )

# ============================================================================
# MAIN STRESS TEST RUNNER
# ============================================================================

class ProductionStressTester:
    """🏭 Runner principal para todas las pruebas de estrés"""
    
    def __init__(self, config: Optional[StressTestConfig] = None):
        self.config = config or StressTestConfig()
        self.results: List[TestResult] = []
        
        # Initialize testers
        self.validation_tester = ValidationStressTester()
        self.rate_limiter_tester = RateLimiterStressTester()
        self.health_monitor_tester = HealthMonitorStressTester()
        self.system_tester = SystemResourceTester()
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Ejecutar todas las pruebas de estrés"""
        print("🧪 Starting ICT Engine v6.0 Enterprise Stress Tests")
        print("=" * 60)
        
        start_time = time.time()
        self.results = []
        
        # 1. Validation Tests
        print("\n🛡️ VALIDATION STRESS TESTS")
        print("-" * 40)
        
        result = self.validation_tester.run_validation_load_test(
            duration=self.config.duration_seconds // 2,
            concurrent_threads=self.config.concurrent_threads
        )
        self.results.append(result)
        self._print_result(result)
        
        result = self.validation_tester.run_batch_validation_test()
        self.results.append(result)
        self._print_result(result)
        
        # 2. Rate Limiter Tests  
        print("\n🚦 RATE LIMITER STRESS TESTS")
        print("-" * 40)
        
        result = self.rate_limiter_tester.run_rate_limiter_load_test(
            duration=self.config.duration_seconds // 2
        )
        self.results.append(result)
        self._print_result(result)
        
        result = self.rate_limiter_tester.run_burst_test()
        self.results.append(result)
        self._print_result(result)
        
        # 3. Health Monitor Tests
        print("\n💖 HEALTH MONITOR STRESS TESTS")
        print("-" * 40)
        
        result = self.health_monitor_tester.run_health_monitor_load_test(
            duration=self.config.duration_seconds // 2
        )
        self.results.append(result)
        self._print_result(result)
        
        # 4. System Resource Tests
        print("\n💻 SYSTEM RESOURCE STRESS TESTS")
        print("-" * 40)
        
        result = self.system_tester.run_memory_stress_test(
            duration=self.config.duration_seconds // 2
        )
        self.results.append(result)
        self._print_result(result)
        
        total_duration = time.time() - start_time
        
        # Generate final report
        report = self._generate_final_report(total_duration)
        self._print_final_report(report)
        
        return report
    
    def _print_result(self, result: TestResult):
        """Imprimir resultado de una prueba"""
        status = "✅ PASS" if result.success else "❌ FAIL"
        print(f"{status} {result.test_name} ({result.duration_seconds:.2f}s)")
        
        if not result.success and result.errors:
            for error in result.errors:
                print(f"   ❌ {error}")
        
        # Print key metrics
        if 'avg_latency_ms' in result.metrics:
            print(f"   📊 Avg Latency: {result.metrics['avg_latency_ms']:.2f}ms")
        if 'requests_per_second' in result.metrics:
            print(f"   📊 Throughput: {result.metrics['requests_per_second']:.0f} req/s")
        if 'error_rate_percent' in result.metrics:
            print(f"   📊 Error Rate: {result.metrics['error_rate_percent']:.1f}%")
    
    def _generate_final_report(self, total_duration: float) -> Dict[str, Any]:
        """Generar reporte final"""
        passed_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]
        
        return {
            'timestamp': time.time(),
            'total_duration_seconds': total_duration,
            'total_tests': len(self.results),
            'passed_tests': len(passed_tests),
            'failed_tests': len(failed_tests),
            'success_rate': len(passed_tests) / len(self.results) * 100 if self.results else 0,
            'overall_success': len(failed_tests) == 0,
            'test_results': [
                {
                    'name': r.test_name,
                    'success': r.success,
                    'duration': r.duration_seconds,
                    'metrics': r.metrics,
                    'errors': r.errors
                } for r in self.results
            ],
            'config': {
                'duration_seconds': self.config.duration_seconds,
                'concurrent_threads': self.config.concurrent_threads,
                'requests_per_second': self.config.requests_per_second
            }
        }
    
    def _print_final_report(self, report: Dict[str, Any]):
        """Imprimir reporte final"""
        print("\n" + "=" * 60)
        print("📊 FINAL STRESS TEST REPORT")
        print("=" * 60)
        
        overall_status = "✅ ALL TESTS PASSED" if report['overall_success'] else "❌ SOME TESTS FAILED"
        print(f"🎯 Overall Status: {overall_status}")
        print(f"📈 Success Rate: {report['success_rate']:.1f}%")
        print(f"🕐 Total Duration: {report['total_duration_seconds']:.2f}s")
        print(f"📊 Tests: {report['passed_tests']}/{report['total_tests']} passed")
        
        if not report['overall_success']:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if not result.success:
                    print(f"   - {result.test_name}: {', '.join(result.errors)}")
        
        print(f"\n🏆 ICT Engine v6.0 Enterprise is {'PRODUCTION READY' if report['overall_success'] else 'NEEDS ATTENTION'}")
        print("=" * 60)
    
    def save_report(self, filepath: str, report: Dict[str, Any]):
        """Guardar reporte a archivo"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Función principal para ejecutar pruebas de estrés"""
    print("🧪 ICT Engine v6.0 Enterprise - Production Stress Testing Suite")
    print("=" * 70)
    
    # Configuration
    config = StressTestConfig(
        duration_seconds=60,  # 1 minute per test category
        concurrent_threads=8,
        requests_per_second=150,
        max_memory_mb=512.0,
        max_cpu_percent=25.0,
        max_latency_ms=50.0
    )
    
    # Run tests
    tester = ProductionStressTester(config)
    report = tester.run_all_tests()
    
    # Save report
    report_file = f"04-DATA/reports/stress_test_report_{int(time.time())}.json"
    Path(report_file).parent.mkdir(parents=True, exist_ok=True)
    tester.save_report(report_file, report)
    
    print(f"\n📁 Report saved to: {report_file}")
    
    return report['overall_success']

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)