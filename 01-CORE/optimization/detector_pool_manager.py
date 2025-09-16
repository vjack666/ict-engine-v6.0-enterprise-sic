#!/usr/bin/env python3
"""
🚀 ENHANCED DETECTOR POOL MANAGER
Optimización avanzada para procesamiento paralelo eficiente
"""

from protocols.unified_logging import get_unified_logger
import os
import threading
import time
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from queue import Queue, Empty
import pandas as pd

# Imports del sistema
from ict_engine.pattern_detector import ICTPatternDetector
from analysis.unified_memory_system import get_unified_memory_system


@dataclass
class AnalysisTask:
    """Tarea de análisis para el pool de detectores - Trading Real"""
    task_id: str
    data: pd.DataFrame
    timeframe: str
    symbol: str = "GBPUSD"  # GBP pairs mejor para detección de patrones por volatilidad
    analysis_type: str = "pattern_detection"
    priority: int = 1  # 1=high, 2=medium, 3=low
    
    def __post_init__(self):
        """Validaciones para trading real - sin datos None o mock"""
        if self.data is None or self.data.empty:
            raise ValueError(f"❌ TRADING CRITICAL: No se permiten datos None o vacíos para {self.symbol}")
        
        required_columns = ['open', 'high', 'low', 'close']
        missing_cols = [col for col in required_columns if col not in self.data.columns]
        if missing_cols:
            raise ValueError(f"❌ TRADING CRITICAL: Faltan columnas OHLC requeridas: {missing_cols}")
        
        # Verificar que no hay valores None en datos críticos
        null_counts = self.data[required_columns].isnull().sum()
        if null_counts.any():
            raise ValueError(f"❌ TRADING CRITICAL: Valores None detectados en OHLC: {null_counts.to_dict()}")
        
        # Validar que los precios son lógicos
        if (self.data['high'] < self.data['low']).any():
            raise ValueError(f"❌ TRADING CRITICAL: Precios inválidos - High < Low detectado para {self.symbol}")
        
        if (self.data['close'] > self.data['high']).any() or (self.data['close'] < self.data['low']).any():
            raise ValueError(f"❌ TRADING CRITICAL: Close fuera del rango High-Low para {self.symbol}")
            
        print(f"✅ TRADING VALIDATION: {self.symbol} {self.timeframe} - {len(self.data)} velas validadas")


@dataclass
class AnalysisResult:
    """Resultado de análisis del pool"""
    task_id: str
    symbol: str
    timeframe: str
    patterns: List[Any]
    processing_time: float
    detector_id: int
    success: bool
    error_msg: Optional[str] = None


class EnhancedDetectorPoolManager:
    """Pool optimizado de detectores para análisis paralelo enterprise"""
    
    def __init__(self, pool_size: Optional[int] = None):
        # Garantizar que siempre tengamos un valor entero válido para el pool size
        cpu_count = os.cpu_count() or 4  # Fallback a 4 cores si os.cpu_count() retorna None
        effective_pool_size = pool_size or cpu_count
        self.pool_size = min(effective_pool_size, cpu_count)
        self.detector_pool = []
        self.shared_memory_system = None
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.active_tasks = {}
        self.statistics = {
            'tasks_completed': 0,
            'total_processing_time': 0.0,
            'avg_task_time': 0.0,
            'pool_utilization': 0.0
        }
        self._lock = threading.RLock()
        self._initialized = False
        
        print(f"🏭 Enhanced Detector Pool Manager inicializado")
        print(f"   📊 Pool size: {self.pool_size} detectores")
        print(f"   🖥️  CPU cores disponibles: {os.cpu_count()}")
        
    def initialize_pool(self) -> bool:
        """Inicializar pool con detectores pre-configurados y memoria compartida"""
        if self._initialized:
            return True
            
        try:
            print(f"   🔧 Inicializando shared memory system...")
            # Inicializar memoria compartida una sola vez
            self.shared_memory_system = get_unified_memory_system()
            
            print(f"   🔧 Creando pool de {self.pool_size} detectores pre-configurados...")
            # Crear pool de detectores reutilizables
            for i in range(self.pool_size):
                detector = ICTPatternDetector()
                # Pre-warm el detector para evitar overhead posterior
                self._prewarm_detector(detector, i)
                self.detector_pool.append({
                    'id': i,
                    'detector': detector,
                    'busy': False,
                    'last_used': time.time(),
                    'tasks_completed': 0
                })
                
            self._initialized = True
            print(f"   ✅ Pool inicializado exitosamente con {len(self.detector_pool)} detectores")
            return True
            
        except Exception as e:
            print(f"   ❌ Error inicializando pool: {e}")
            return False
    
    def _prewarm_detector(self, detector: ICTPatternDetector, detector_id: int):
        """Pre-calentar detector para evitar overhead de inicialización"""
        try:
            # Crear datos sintéticos mínimos para pre-warm
            dummy_data = pd.DataFrame({
                'timestamp': pd.date_range('2024-01-01', periods=10, freq='15min'),
                'open': [1.0500] * 10,
                'high': [1.0510] * 10,
                'low': [1.0490] * 10,
                'close': [1.0500] * 10,
                'volume': [1000] * 10
            })
            
            # Ejecutar análisis dummy para pre-warm
            detector.detect_patterns(dummy_data, 'M15')
            print(f"     🔥 Detector {detector_id} pre-warmed")
            
        except Exception as e:
            print(f"     ⚠️ Warning: Pre-warm detector {detector_id} failed: {e}")
    
    def get_available_detector(self) -> Optional[Dict[str, Any]]:
        """Obtener detector disponible del pool"""
        with self._lock:
            for detector_info in self.detector_pool:
                if not detector_info['busy']:
                    detector_info['busy'] = True
                    detector_info['last_used'] = time.time()
                    return detector_info
            return None
    
    def release_detector(self, detector_id: int):
        """Liberar detector de vuelta al pool"""
        with self._lock:
            if detector_id < len(self.detector_pool):
                self.detector_pool[detector_id]['busy'] = False
                self.detector_pool[detector_id]['tasks_completed'] += 1
    
    def process_parallel_analysis(self, tasks: List[AnalysisTask]) -> List[AnalysisResult]:
        """Análisis paralelo optimizado con pool de detectores"""
        if not self._initialized:
            if not self.initialize_pool():
                raise RuntimeError("Failed to initialize detector pool")
        
        print(f"🚀 Procesando {len(tasks)} tareas en paralelo...")
        start_time = time.time()
        results = []
        
        # Ordenar tareas por prioridad
        sorted_tasks = sorted(tasks, key=lambda t: t.priority)
        
        with ThreadPoolExecutor(max_workers=self.pool_size) as executor:
            # Enviar tareas al pool
            future_to_task = {}
            for task in sorted_tasks:
                future = executor.submit(self._process_single_task, task)
                future_to_task[future] = task
            
            # Recoger resultados conforme se completan
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Actualizar estadísticas
                    with self._lock:
                        self.statistics['tasks_completed'] += 1
                        self.statistics['total_processing_time'] += result.processing_time
                        
                except Exception as e:
                    # Crear resultado de error
                    error_result = AnalysisResult(
                        task_id=task.task_id,
                        symbol=task.symbol,
                        timeframe=task.timeframe,
                        patterns=[],
                        processing_time=0.0,
                        detector_id=-1,
                        success=False,
                        error_msg=str(e)
                    )
                    results.append(error_result)
                    print(f"   ❌ Error procesando tarea {task.task_id}: {e}")
        
        total_time = time.time() - start_time
        
        # Calcular estadísticas finales
        with self._lock:
            if self.statistics['tasks_completed'] > 0:
                self.statistics['avg_task_time'] = (
                    self.statistics['total_processing_time'] / 
                    self.statistics['tasks_completed']
                )
            self.statistics['pool_utilization'] = (
                len(tasks) / (self.pool_size * total_time) * 
                self.statistics['avg_task_time']
            )
        
        print(f"   ✅ Procesamiento completado en {total_time:.3f}s")
        print(f"   📊 Promedio por tarea: {self.statistics['avg_task_time']:.3f}s")
        print(f"   📈 Utilización del pool: {self.statistics['pool_utilization']:.1%}")
        
        return results
    
    def _process_single_task(self, task: AnalysisTask) -> AnalysisResult:
        """Procesar una tarea individual usando detector del pool"""
        task_start = time.time()
        
        # Obtener detector disponible
        detector_info = self.get_available_detector()
        max_retries = 100
        retry_count = 0
        
        while detector_info is None and retry_count < max_retries:
            time.sleep(0.001)  # Wait 1ms
            detector_info = self.get_available_detector()
            retry_count += 1
        
        if detector_info is None:
            raise RuntimeError(f"No detector available after {max_retries} retries")
        
        try:
            # Procesar usando detector del pool
            detector = detector_info['detector']
            patterns = detector.detect_patterns(task.data, task.timeframe)
            
            processing_time = time.time() - task_start
            
            result = AnalysisResult(
                task_id=task.task_id,
                symbol=task.symbol,
                timeframe=task.timeframe,
                patterns=patterns,
                processing_time=processing_time,
                detector_id=detector_info['id'],
                success=True
            )
            
            return result
            
        except Exception as e:
            processing_time = time.time() - task_start
            return AnalysisResult(
                task_id=task.task_id,
                symbol=task.symbol,
                timeframe=task.timeframe,
                patterns=[],
                processing_time=processing_time,
                detector_id=detector_info['id'],
                success=False,
                error_msg=str(e)
            )
            
        finally:
            # Liberar detector de vuelta al pool
            self.release_detector(detector_info['id'])
    
    def process_batch(self, tasks: List[AnalysisTask]) -> List[AnalysisResult]:
        """
        Procesar lote de tareas de análisis en paralelo - OPTIMIZADO PARA TRADING
        
        Args:
            tasks: Lista de tareas de análisis validadas
            
        Returns:
            Lista de resultados de análisis
        """
        if not tasks:
            print("⚠️ TRADING WARNING: Lista de tareas vacía")
            return []
            
        if not self._initialized:
            print("🔧 Pool no inicializado, inicializando...")
            if not self.initialize_pool():
                print("❌ TRADING CRITICAL: No se pudo inicializar el pool")
                return []
        
        print(f"🚀 TRADING BATCH: Procesando {len(tasks)} tareas en paralelo")
        
        # Procesar en paralelo usando ThreadPoolExecutor para máximo rendimiento
        results = []
        batch_start = time.time()
        
        # Usar ThreadPoolExecutor para gestionar el paralelismo de forma eficiente
        with ThreadPoolExecutor(max_workers=self.pool_size, thread_name_prefix="ICT_Detector") as executor:
            # Mapear tareas a futuros
            future_to_task = {
                executor.submit(self._process_single_task_batch, task): task 
                for task in tasks
            }
            
            # Recopilar resultados conforme se completan
            for future in as_completed(future_to_task):
                try:
                    result = future.result(timeout=30)  # Timeout de 30s por tarea
                    results.append(result)
                    
                    if result.success:
                        print(f"   ✅ {result.task_id}: {len(result.patterns)} patrones en {result.processing_time:.3f}s")
                    else:
                        print(f"   ❌ {result.task_id}: Error - {result.error_msg}")
                        
                except Exception as e:
                    task = future_to_task[future]
                    print(f"   💥 {task.task_id}: Exception - {e}")
                    # Crear resultado de error
                    error_result = AnalysisResult(
                        task_id=task.task_id,
                        symbol=task.symbol,
                        timeframe=task.timeframe,
                        patterns=[],
                        processing_time=0.0,
                        detector_id=-1,
                        success=False,
                        error_msg=f"Batch processing error: {e}"
                    )
                    results.append(error_result)
        
        batch_time = time.time() - batch_start
        successful_tasks = len([r for r in results if r.success])
        total_patterns = sum(len(r.patterns) for r in results if r.success)
        
        print(f"📊 TRADING BATCH COMPLETE: {successful_tasks}/{len(tasks)} exitosas, "
              f"{total_patterns} patrones, {batch_time:.3f}s total")
        
        # Actualizar estadísticas del pool
        with self._lock:
            self.statistics['tasks_completed'] += len(tasks)
            self.statistics['total_processing_time'] += batch_time
            if self.statistics['tasks_completed'] > 0:
                self.statistics['avg_task_time'] = (
                    self.statistics['total_processing_time'] / self.statistics['tasks_completed']
                )
        
        return results
    
    def _process_single_task_batch(self, task: AnalysisTask) -> AnalysisResult:
        """
        Procesar una sola tarea de análisis con detector del pool para batch processing
        
        Args:
            task: Tarea de análisis validada
            
        Returns:
            Resultado del análisis
        """
        # Obtener detector disponible del pool
        detector_info = self.get_available_detector()
        if not detector_info:
            return AnalysisResult(
                task_id=task.task_id,
                symbol=task.symbol,
                timeframe=task.timeframe,
                patterns=[],
                processing_time=0.0,
                detector_id=-1,
                success=False,
                error_msg="No hay detectores disponibles en el pool"
            )
        
        task_start = time.time()
        
        try:
            # Procesar con el detector del pool
            detector = detector_info['detector']
            patterns = detector.detect_patterns(task.data, task.timeframe)
            
            # Actualizar estadísticas del detector
            detector_info['tasks_completed'] += 1
            
            processing_time = time.time() - task_start
            
            result = AnalysisResult(
                task_id=task.task_id,
                symbol=task.symbol,
                timeframe=task.timeframe,
                patterns=patterns,
                processing_time=processing_time,
                detector_id=detector_info['id'],
                success=True
            )
            
            return result
            
        except Exception as e:
            processing_time = time.time() - task_start
            return AnalysisResult(
                task_id=task.task_id,
                symbol=task.symbol,
                timeframe=task.timeframe,
                patterns=[],
                processing_time=processing_time,
                detector_id=detector_info['id'],
                success=False,
                error_msg=str(e)
            )
            
        finally:
            # Liberar detector de vuelta al pool
            self.release_detector(detector_info['id'])
    
    def get_pool_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del pool"""
        with self._lock:
            busy_detectors = sum(1 for d in self.detector_pool if d['busy'])
            
            return {
                'pool_size': self.pool_size,
                'busy_detectors': busy_detectors,
                'available_detectors': self.pool_size - busy_detectors,
                'utilization_percent': (busy_detectors / self.pool_size) * 100,
                'tasks_completed': self.statistics['tasks_completed'],
                'avg_task_time': self.statistics['avg_task_time'],
                'total_processing_time': self.statistics['total_processing_time']
            }
    
    def shutdown(self):
        """Shutdown del pool manager"""
        print("🔄 Cerrando Enhanced Detector Pool Manager...")
        with self._lock:
            self.detector_pool.clear()
            self._initialized = False
        print("   ✅ Pool cerrado exitosamente")


# Instancia global del pool manager
_pool_manager_instance = None
_pool_manager_lock = threading.Lock()


def get_detector_pool_manager(pool_size: Optional[int] = None) -> EnhancedDetectorPoolManager:
    """Obtener instancia singleton del pool manager"""
    global _pool_manager_instance
    
    with _pool_manager_lock:
        if _pool_manager_instance is None:
            _pool_manager_instance = EnhancedDetectorPoolManager(pool_size)
        return _pool_manager_instance


def shutdown_detector_pool():
    """Shutdown del pool manager global"""
    global _pool_manager_instance
    
    with _pool_manager_lock:
        if _pool_manager_instance is not None:
            _pool_manager_instance.shutdown()
            _pool_manager_instance = None
