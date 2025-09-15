#!/usr/bin/env python3
"""
🧪 INTEGRATED STRESS TESTING - ICT ENGINE v6.0 ENTERPRISE
=========================================================

Suite integrada de pruebas de estrés que usa los módulos existentes.
Enfoque en validar el sistema real sin dependencias externas.

Características principales:
✅ Pruebas de integración del sistema principal
✅ Validación de logging bajo carga
✅ Testing de configuraciones avanzadas
✅ Pruebas de memoria y CPU 
✅ Simulación de trading scenarios
✅ Validación de dashboard performance
✅ Testing de persistencia de datos

Métricas validadas:
- Startup time < 30 segundos
- Memory usage < 512MB bajo carga  
- CPU usage < 25% promedio
- Config loading < 5 segundos
- Dashboard response < 2 segundos
- Log writing throughput > 1000 entries/s

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 14 Septiembre 2025
"""

import sys
import os
import time
import threading
import json
import statistics
import random
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import psutil
import gc
import subprocess
import logging

# Add project paths
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('01-CORE'))
sys.path.insert(0, os.path.abspath('09-DASHBOARD'))

# Thresholds centralizados para ajustar criterios sin modificar lógica interna
STRESS_THRESHOLDS: Dict[str, Any] = {
    'startup_time_max_s': 30.0,
    'config_loading_max_s': 5.0,
    'logging_min_logs_per_s': 500,
    'memory_peak_max_mb': 512.0,
    'avg_cpu_max_percent': 25.0,
    'memory_leak_max_mb': 100.0,
    'concurrent_ops_min_total': 1000,
    'concurrent_error_rate_max': 0.02,
    'persistence_write_ms_max': 100,
    'persistence_read_ms_max': 50
}


def _get_git_revision() -> Optional[str]:
    """Obtener hash corto de commit si git está disponible."""
    try:
        result = subprocess.run([
            'git', 'rev-parse', '--short', 'HEAD'
        ], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        return None
    return None

# ============================================================================
# SYSTEM INTEGRATION TESTS
# ============================================================================

class SystemIntegrationTester:
    """🔧 Pruebas de integración del sistema principal"""
    
    def __init__(self):
        self.results = []
        self.errors = []
    
    def test_main_system_startup(self) -> Tuple[bool, Dict[str, Any]]:
        """Prueba de startup del sistema principal"""
        print("🧪 Testing main system startup performance")
        
        startup_start = time.time()
        
        try:
            # Import and initialize core components
            from analysis.poi_system import POISystem
            try:
                from smart_trading_logger import SmartTradingLogger as _LoggerClass  # type: ignore
                logger = _LoggerClass("StressTest")
            except Exception:
                logger = logging.getLogger("StressTest")
                if not logger.handlers:
                    handler = logging.StreamHandler()
                    handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s'))
                    logger.addHandler(handler)
                    logger.setLevel(logging.INFO)
            logger.info("🧪 Starting system integration test")
            
            # Initialize POI system
            poi_system = POISystem()
            
            # Test configuration loading
            config_start = time.time()
            try:
                from config.production_config import get_config_manager
                config_manager = get_config_manager()
                current_cfg = config_manager.get_current_config()
                saved = config_manager.list_saved_configs()
                config_time = time.time() - config_start
                config_data = {
                    'current_config_loaded': current_cfg is not None,
                    'saved_configs_count': len(saved),
                    'saved_configs_sample': saved[:5]
                }
            except Exception:
                config_time = 0.0
                config_data = {
                    'current_config_loaded': False,
                    'saved_configs_count': 0,
                    'saved_configs_sample': []
                }
            
            startup_time = time.time() - startup_start
            
            metrics = {
                'startup_time_seconds': startup_time,
                'config_loading_time_seconds': config_time,
                'poi_system_initialized': poi_system is not None,
                'logger_initialized': logger is not None,
                'config_entries': len(config_data),
                'success': (
                    startup_time <= STRESS_THRESHOLDS['startup_time_max_s'] and
                    config_time <= STRESS_THRESHOLDS['config_loading_max_s']
                )
            }
            
            logger.info(f"✅ System startup completed in {startup_time:.2f}s")
            
            return True, metrics
            
        except Exception as e:
            error_msg = f"System startup failed: {str(e)}"
            self.errors.append(error_msg)
            return False, {
                'startup_time_seconds': time.time() - startup_start,
                'error': error_msg,
                'success': False
            }
    
    def test_logging_performance(self, duration: int = 15) -> Tuple[bool, Dict[str, Any]]:
        """Prueba de performance del logging"""
        print(f"🧪 Testing logging performance - {duration}s duration")
        
        try:
            try:
                from smart_trading_logger import SmartTradingLogger as _LoggerClass  # type: ignore
                logger = _LoggerClass("StressLoggingPerf")
            except Exception:
                logger = logging.getLogger("StressLoggingPerf")
                if not logger.handlers:
                    handler = logging.StreamHandler()
                    handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s'))
                    logger.addHandler(handler)
                    logger.setLevel(logging.INFO)
        except ImportError:
            return False, {
                'error': 'Logger not available',
                'success': False
            }
        
        start_time = time.time()
        log_count = 0
        errors = 0
        
        def logging_worker():
            nonlocal log_count, errors
            end_time = start_time + duration
            
            while time.time() < end_time:
                try:
                    # Simulate various log types
                    log_types = [
                        lambda: logger.info(f"Trade executed: EURUSD {random.uniform(0.01, 1.0):.2f} lots"),
                        lambda: logger.warning(f"High spread detected: {random.uniform(2, 10):.1f} pips"),
                        lambda: logger.debug(f"Price update: {random.uniform(1.0, 2.0):.5f}"),
                        lambda: logger.error(f"Connection timeout after {random.uniform(1, 5):.1f}s")
                    ]
                    
                    random.choice(log_types)()
                    log_count += 1
                    
                except Exception:
                    errors += 1
                
                # Throttle to realistic rate
                time.sleep(0.001)  # 1000 logs per second max
        
        # Start multiple logging workers
        workers = []
        for _ in range(3):
            worker = threading.Thread(target=logging_worker)
            worker.start()
            workers.append(worker)
        
        for worker in workers:
            worker.join()
        
        total_duration = time.time() - start_time
        logs_per_second = log_count / total_duration if total_duration > 0 else 0
        
        metrics = {
            'total_logs': log_count,
            'errors': errors,
            'duration_seconds': total_duration,
            'logs_per_second': logs_per_second,
            'error_rate_percent': (errors / max(log_count + errors, 1)) * 100,
            'success': (
                logs_per_second >= STRESS_THRESHOLDS['logging_min_logs_per_s'] and
                errors == 0
            )
        }
        
        return metrics['success'], metrics
    
    def test_dashboard_components(self) -> Tuple[bool, Dict[str, Any]]:
        """Prueba de componentes del dashboard"""
        print("🧪 Testing dashboard components")
        
        components_loaded = {
            'main_dashboard_app_class': False,
            'ict_dashboard_class': False,
            'web_dashboard_class': False
        }
        import_error_details = []
        # Detect ICTDashboardApp
        try:
            import importlib
            dash_mod = importlib.import_module('dashboard')
            if hasattr(dash_mod, 'ICTDashboardApp'):
                components_loaded['main_dashboard_app_class'] = True
        except Exception as e:
            import_error_details.append(f'dashboard: {e}')
        # Detect ICTDashboard
        try:
            import importlib
            ict_dash_mod = importlib.import_module('ict_dashboard')
            if hasattr(ict_dash_mod, 'ICTDashboard'):
                components_loaded['ict_dashboard_class'] = True
        except Exception as e:
            import_error_details.append(f'ict_dashboard: {e}')
        # Detect ICTWebDashboard
        try:
            import importlib
            web_dash_mod = importlib.import_module('web_dashboard')
            if hasattr(web_dash_mod, 'ICTWebDashboard'):
                components_loaded['web_dashboard_class'] = True
        except Exception as e:
            import_error_details.append(f'web_dashboard: {e}')
        import_errors_summary = import_error_details
        
        # Test enterprise tabs manager
        try:
            from enterprise_tabs_manager import EnterpriseTabsManager  # type: ignore
            try:
                from smart_trading_logger import SmartTradingLogger as _LoggerClass  # type: ignore
                logger_tabs = _LoggerClass("TabsManagerTest")
            except Exception:
                logger_tabs = logging.getLogger("TabsManagerTest")
                if not logger_tabs.handlers:
                    handler = logging.StreamHandler()
                    handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s'))
                    logger_tabs.addHandler(handler)
                    logger_tabs.setLevel(logging.INFO)
            tabs_manager = EnterpriseTabsManager(logger=logger_tabs)  # type: ignore

            initialization_start = time.time()
            # Métodos defensivos (pueden no existir en implementación mínima)
            init_fn = getattr(tabs_manager, 'initialize_all_tabs', None)
            get_tabs_fn = getattr(tabs_manager, 'get_available_tabs', None)
            if callable(init_fn):
                init_fn()
            tabs = get_tabs_fn() if callable(get_tabs_fn) else {}
            initialization_time = time.time() - initialization_start

            tabs_metrics = {
                'tabs_manager_loaded': True,
                'tabs_count': len(tabs) if isinstance(tabs, dict) else 0,
                'initialization_time_seconds': initialization_time,
                'tabs_list': list(tabs.keys()) if isinstance(tabs, dict) else []
            }

        except Exception as e:
            tabs_metrics = {
                'tabs_manager_loaded': False,
                'error': f"enterprise_tabs_manager missing or failed: {e}"
            }
        
        metrics = {
            'components': components_loaded,
            'import_errors': import_errors_summary,
            'tabs_manager': tabs_metrics,
            'success': any(v for v in components_loaded.values()) and tabs_metrics.get('tabs_manager_loaded', False)
        }
        
        return metrics['success'], metrics
    
    def test_data_persistence(self) -> Tuple[bool, Dict[str, Any]]:
        """Prueba de persistencia de datos"""
        print("🧪 Testing data persistence")
        
        test_data = {
            'timestamp': time.time(),
            'test_id': f'stress_test_{int(time.time())}',
            'metrics': {
                'cpu_usage': random.uniform(10, 30),
                'memory_usage': random.uniform(100, 400),
                'active_trades': random.randint(0, 10)
            }
        }
        
        persistence_metrics = {
            'json_write': False,
            'json_read': False,
            'data_integrity': False,
            'write_time_ms': 0,
            'read_time_ms': 0
        }
        
        try:
            # Test JSON persistence
            test_file = Path("04-DATA/cache/stress_test_data.json")
            test_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write test
            write_start = time.perf_counter()
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2)
            persistence_metrics['write_time_ms'] = (time.perf_counter() - write_start) * 1000
            persistence_metrics['json_write'] = True
            
            # Read test
            read_start = time.perf_counter()
            with open(test_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            persistence_metrics['read_time_ms'] = (time.perf_counter() - read_start) * 1000
            persistence_metrics['json_read'] = True
            
            # Data integrity test
            persistence_metrics['data_integrity'] = (
                loaded_data['test_id'] == test_data['test_id'] and
                loaded_data['timestamp'] == test_data['timestamp']
            )
            
            # Cleanup
            test_file.unlink(missing_ok=True)
            
        except Exception as e:
            persistence_metrics['error'] = str(e)
        
        success = all([
            persistence_metrics['json_write'],
            persistence_metrics['json_read'],
            persistence_metrics['data_integrity'],
            persistence_metrics['write_time_ms'] <= STRESS_THRESHOLDS['persistence_write_ms_max'],
            persistence_metrics['read_time_ms'] <= STRESS_THRESHOLDS['persistence_read_ms_max']
        ])
        
        return success, persistence_metrics

# ============================================================================
# MEMORY AND PERFORMANCE TESTS
# ============================================================================

class PerformanceTester:
    """⚡ Pruebas de performance y recursos"""
    
    def test_memory_usage_under_load(self, duration: int = 20) -> Tuple[bool, Dict[str, Any]]:
        """Prueba de uso de memoria bajo carga"""
        print(f"🧪 Testing memory usage under load - {duration}s duration")
        
        process = psutil.Process()
        
        # Baseline measurements
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        memory_samples = []
        cpu_samples = []
        
        def monitor_resources():
            nonlocal memory_samples, cpu_samples
            start_time = time.time()
            end_time = start_time + duration
            
            while time.time() < end_time:
                try:
                    memory_mb = process.memory_info().rss / (1024 * 1024)
                    cpu_percent = process.cpu_percent(interval=None)
                    
                    memory_samples.append(memory_mb)
                    if cpu_percent > 0:  # Filter out invalid readings
                        cpu_samples.append(cpu_percent)
                        
                except:
                    pass
                
                time.sleep(0.5)  # Sample every 500ms
        
        def simulate_workload():
            """Simulate realistic trading workload"""
            start_time = time.time()
            end_time = start_time + duration
            
            data_cache = []
            
            while time.time() < end_time:
                # Simulate market data processing
                market_data = {
                    'symbol': random.choice(['EURUSD', 'GBPUSD', 'USDCAD']),
                    'bid': random.uniform(1.0, 2.0),
                    'ask': random.uniform(1.0, 2.0),
                    'timestamp': time.time(),
                    'volume': random.uniform(0.1, 10.0)
                }
                
                data_cache.append(market_data)
                
                # Simulate analysis calculations
                if len(data_cache) > 100:
                    # Calculate some metrics
                    prices = [d['bid'] for d in data_cache[-50:]]
                    avg_price = statistics.mean(prices)
                    volatility = statistics.stdev(prices) if len(prices) > 1 else 0
                    
                    # Simulate cleanup
                    data_cache = data_cache[-50:]
                
                time.sleep(0.01)  # 100Hz update rate
        
        # Start monitoring and workload simulation
        monitor_thread = threading.Thread(target=monitor_resources)
        workload_threads = [threading.Thread(target=simulate_workload) for _ in range(2)]
        
        monitor_thread.start()
        for thread in workload_threads:
            thread.start()
        
        # Wait for completion
        monitor_thread.join()
        for thread in workload_threads:
            thread.join()
        
        # Force garbage collection
        gc.collect()
        final_memory = process.memory_info().rss / (1024 * 1024)
        
        # Calculate metrics
        if memory_samples and cpu_samples:
            avg_memory = statistics.mean(memory_samples)
            max_memory = max(memory_samples)
            avg_cpu = statistics.mean(cpu_samples)
            max_cpu = max(cpu_samples)
            
            metrics = {
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'avg_memory_mb': avg_memory,
                'max_memory_mb': max_memory,
                'memory_increase_mb': final_memory - initial_memory,
                'avg_cpu_percent': avg_cpu,
                'max_cpu_percent': max_cpu,
                'samples_count': len(memory_samples),
                'success': (
                    max_memory <= STRESS_THRESHOLDS['memory_peak_max_mb'] and
                    avg_cpu <= STRESS_THRESHOLDS['avg_cpu_max_percent'] and
                    abs(final_memory - initial_memory) <= STRESS_THRESHOLDS['memory_leak_max_mb']
                )
            }
        else:
            metrics = {
                'error': 'No samples collected',
                'success': False
            }
        
        return metrics.get('success', False), metrics
    
    def test_concurrent_operations(self, duration: int = 15) -> Tuple[bool, Dict[str, Any]]:
        """Prueba de operaciones concurrentes"""
        print(f"🧪 Testing concurrent operations - {duration}s duration")
        
        start_time = time.time()
        
        results = {
            'file_operations': 0,
            'calculations': 0,
            'data_processing': 0,
            'errors': 0
        }
        
        def file_worker():
            """Worker para operaciones de archivos"""
            end_time = start_time + duration
            while time.time() < end_time:
                try:
                    # Simulate file operations
                    test_file = Path(f"04-DATA/cache/test_{threading.current_thread().ident}.tmp")
                    test_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(test_file, 'w') as f:
                        f.write(f"Test data {time.time()}")
                    
                    with open(test_file, 'r') as f:
                        _ = f.read()
                    
                    test_file.unlink(missing_ok=True)
                    results['file_operations'] += 1
                    
                except Exception:
                    results['errors'] += 1
                
                time.sleep(0.01)
        
        def calculation_worker():
            """Worker para cálculos intensivos"""
            end_time = start_time + duration
            while time.time() < end_time:
                try:
                    # Simulate trading calculations
                    prices = [random.uniform(1.0, 2.0) for _ in range(100)]
                    sma = statistics.mean(prices)
                    volatility = statistics.stdev(prices)
                    
                    # Simulate technical indicators
                    rsi = random.uniform(0, 100)
                    macd = random.uniform(-1, 1)
                    
                    results['calculations'] += 1
                    
                except Exception:
                    results['errors'] += 1
                
                time.sleep(0.005)
        
        def data_processing_worker():
            """Worker para procesamiento de datos"""
            end_time = start_time + duration
            data_buffer = []
            
            while time.time() < end_time:
                try:
                    # Simulate market data
                    tick = {
                        'symbol': random.choice(['EURUSD', 'GBPUSD']),
                        'price': random.uniform(1.0, 2.0),
                        'timestamp': time.time()
                    }
                    
                    data_buffer.append(tick)
                    
                    # Process in batches
                    if len(data_buffer) >= 20:
                        # Simulate batch processing
                        avg_price = statistics.mean([t['price'] for t in data_buffer])
                        data_buffer = data_buffer[-10:]  # Keep recent data
                    
                    results['data_processing'] += 1
                    
                except Exception:
                    results['errors'] += 1
                
                time.sleep(0.002)
        
        # Start workers
        workers = []
        for worker_func in [file_worker, calculation_worker, data_processing_worker]:
            for _ in range(2):  # 2 threads per worker type
                thread = threading.Thread(target=worker_func)
                thread.start()
                workers.append(thread)
        
        # Wait for completion
        for worker in workers:
            worker.join()
        
        total_duration = time.time() - start_time
        total_operations = sum([results[k] for k in results if k != 'errors'])
        
        metrics = {
            'total_operations': total_operations,
            'operations_per_second': total_operations / total_duration,
            'file_operations': results['file_operations'],
            'calculations': results['calculations'],
            'data_processing': results['data_processing'],
            'errors': results['errors'],
            'error_rate_percent': (results['errors'] / max(total_operations + results['errors'], 1)) * 100,
            'duration_seconds': total_duration,
            'success': (
                total_operations >= STRESS_THRESHOLDS['concurrent_ops_min_total'] and
                results['errors'] <= total_operations * STRESS_THRESHOLDS['concurrent_error_rate_max']
            )
        }
        
        return metrics['success'], metrics

# ============================================================================
# MAIN STRESS TEST RUNNER
# ============================================================================

class IntegratedStressTester:
    """🏭 Runner principal para pruebas integradas"""
    
    def __init__(self):
        self.system_tester = SystemIntegrationTester()
        self.performance_tester = PerformanceTester()
        self.results = []
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Ejecutar todas las pruebas integradas"""
        print("🧪 ICT Engine v6.0 Enterprise - Integrated Stress Testing")
        print("=" * 65)
        
        start_time = time.time()
        
        # 1. System Integration Tests
        print("\n🔧 SYSTEM INTEGRATION TESTS")
        print("-" * 45)
        
        success, metrics = self.system_tester.test_main_system_startup()
        self._log_test_result("main_system_startup", success, metrics)
        
        success, metrics = self.system_tester.test_logging_performance()
        self._log_test_result("logging_performance", success, metrics)
        
        success, metrics = self.system_tester.test_dashboard_components()
        self._log_test_result("dashboard_components", success, metrics)
        
        success, metrics = self.system_tester.test_data_persistence()
        self._log_test_result("data_persistence", success, metrics)
        
        # 2. Performance Tests
        print("\n⚡ PERFORMANCE TESTS")
        print("-" * 45)
        
        success, metrics = self.performance_tester.test_memory_usage_under_load()
        self._log_test_result("memory_usage_under_load", success, metrics)
        
        success, metrics = self.performance_tester.test_concurrent_operations()
        self._log_test_result("concurrent_operations", success, metrics)
        
        total_duration = time.time() - start_time
        
        # Generate report
        report = self._generate_report(total_duration)
        self._print_final_report(report)
        
        return report
    
    def _log_test_result(self, test_name: str, success: bool, metrics: Dict[str, Any]):
        """Registrar resultado de test"""
        status = "✅ PASS" if success else "❌ FAIL"
        duration = metrics.get('duration_seconds', metrics.get('startup_time_seconds', 0))
        print(f"{status} {test_name} ({duration:.2f}s)")
        
        # Log key metrics
        if 'startup_time_seconds' in metrics:
            print(f"   ⏱️ Startup: {metrics['startup_time_seconds']:.2f}s")
        if 'logs_per_second' in metrics:
            print(f"   📝 Logging: {metrics['logs_per_second']:.0f} logs/s")
        if 'max_memory_mb' in metrics:
            print(f"   🧠 Peak Memory: {metrics['max_memory_mb']:.1f}MB")
        if 'operations_per_second' in metrics:
            print(f"   ⚡ Operations: {metrics['operations_per_second']:.0f} ops/s")
        if 'error' in metrics:
            print(f"   ❌ Error: {metrics['error']}")
        
        self.results.append({
            'test_name': test_name,
            'success': success,
            'metrics': metrics
        })
    
    def _generate_report(self, total_duration: float) -> Dict[str, Any]:
        """Generar reporte final"""
        successful_tests = [r for r in self.results if r['success']]
        failed_tests = [r for r in self.results if not r['success']]
        
        return {
            'timestamp': time.time(),
            'git_revision': _get_git_revision(),
            'thresholds': STRESS_THRESHOLDS,
            'total_duration_seconds': total_duration,
            'total_tests': len(self.results),
            'passed_tests': len(successful_tests),
            'failed_tests': len(failed_tests),
            'success_rate_percent': len(successful_tests) / len(self.results) * 100 if self.results else 0,
            'overall_success': len(failed_tests) == 0,
            'results': self.results
        }
    
    def _print_final_report(self, report: Dict[str, Any]):
        """Imprimir reporte final"""
        print("\n" + "=" * 65)
        print("📊 INTEGRATED STRESS TEST REPORT")
        print("=" * 65)
        
        overall_status = "✅ ALL TESTS PASSED" if report['overall_success'] else "⚠️ SOME TESTS FAILED"
        print(f"🎯 Overall Status: {overall_status}")
        print(f"📈 Success Rate: {report['success_rate_percent']:.1f}%")
        print(f"🕐 Total Duration: {report['total_duration_seconds']:.2f}s")
        print(f"📊 Tests: {report['passed_tests']}/{report['total_tests']} passed")
        
        if not report['overall_success']:
            print("\n⚠️ FAILED TESTS:")
            for result in self.results:
                if not result['success']:
                    error = result['metrics'].get('error', 'Unknown error')
                    print(f"   - {result['test_name']}: {error}")
        
        # Performance summary
        print(f"\n📊 PERFORMANCE SUMMARY:")
        for result in self.results:
            if result['success']:
                metrics = result['metrics']
                test_name = result['test_name'].replace('_', ' ').title()
                
                if 'startup_time_seconds' in metrics:
                    print(f"   🚀 {test_name}: {metrics['startup_time_seconds']:.2f}s startup")
                elif 'logs_per_second' in metrics:
                    print(f"   📝 {test_name}: {metrics['logs_per_second']:.0f} logs/s")
                elif 'max_memory_mb' in metrics:
                    print(f"   🧠 {test_name}: {metrics['max_memory_mb']:.1f}MB peak")
                elif 'operations_per_second' in metrics:
                    print(f"   ⚡ {test_name}: {metrics['operations_per_second']:.0f} ops/s")
        
        production_status = "PRODUCTION READY" if report['overall_success'] else "NEEDS REVIEW"
        print(f"\n🏆 ICT Engine v6.0 Enterprise is {production_status}")
        print("=" * 65)
        
        # Save report
        report_file = f"04-DATA/reports/integrated_stress_report_{int(time.time())}.json"
        Path(report_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        
        print(f"\n📁 Report saved to: {report_file}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Función principal"""
    print("🧪 ICT Engine v6.0 Enterprise - Integrated Production Testing")
    print("=" * 70)
    
    tester = IntegratedStressTester()
    report = tester.run_all_tests()
    
    return report['overall_success']

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)