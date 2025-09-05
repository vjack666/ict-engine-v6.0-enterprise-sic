#!/usr/bin/env python3
"""
⚙️ WORK DISTRIBUTION ENGINE
Motor de distribución inteligente de análisis para máxima eficiencia
"""

import os
import time
import threading
import statistics
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
from queue import PriorityQueue, Queue, Empty

from optimization.detector_pool_manager import AnalysisTask, AnalysisResult


class TaskComplexity(Enum):
    """Niveles de complejidad de tareas"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class CPULoadLevel(Enum):
    """Niveles de carga de CPU"""
    IDLE = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


@dataclass
class WorkerCapability:
    """Capacidades de un worker/detector"""
    worker_id: int
    max_concurrent_tasks: int = 1
    current_load: float = 0.0
    total_tasks_completed: int = 0
    avg_task_time: float = 0.0
    specialty_patterns: List[str] = field(default_factory=list)
    performance_score: float = 1.0


@dataclass
class SmartTask(AnalysisTask):
    """Tarea inteligente con información de distribución"""
    complexity: TaskComplexity = TaskComplexity.MEDIUM
    estimated_time: float = 0.0
    required_memory_mb: float = 0.0
    preferred_worker_id: Optional[int] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __lt__(self, other):
        """Comparación para cola de prioridad"""
        # Prioridad mayor = valor menor en PriorityQueue
        return (self.priority, self.complexity.value) < (other.priority, other.complexity.value)


class WorkDistributionEngine:
    """Motor de distribución inteligente de análisis"""
    
    def __init__(self, pool_size: Optional[int] = None):
        # Lógica robusta para determinación de pool size - Trading Enterprise
        cpu_cores = os.cpu_count() or 8  # Fallback a 8 cores para sistemas enterprise
        
        if pool_size is not None:
            # Validar pool_size proporcionado
            if pool_size <= 0:
                raise ValueError(f"❌ TRADING CRITICAL: pool_size debe ser > 0, recibido: {pool_size}")
            # Limitar al número de cores disponibles para evitar overcommit
            self.pool_size = min(pool_size, cpu_cores)
        else:
            # Usar configuración óptima para trading: 75% de cores disponibles
            self.pool_size = max(1, int(cpu_cores * 0.75))
        
        # Validación final de tipo y rango
        assert isinstance(self.pool_size, int) and self.pool_size > 0, \
            f"❌ TRADING CRITICAL: pool_size inválido: {self.pool_size}"
        
        self.worker_capabilities = {}
        self.task_queue = PriorityQueue()
        self.completed_tasks = Queue()
        self.failed_tasks = Queue()
        
        # Estadísticas del motor
        self.distribution_stats = {
            'tasks_distributed': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'avg_distribution_time': 0.0,
            'load_balance_score': 1.0,
            'total_processing_time': 0.0
        }
        
        self._lock = threading.RLock()
        self._initialized = False
        
        print(f"⚙️ Work Distribution Engine inicializado")
        print(f"   📊 Pool size: {self.pool_size} workers")
    
    def initialize_workers(self) -> bool:
        """Inicializar información de capacidades de workers"""
        if self._initialized:
            return True
        
        try:
            print("   🔧 Inicializando capacidades de workers...")
            
            for worker_id in range(self.pool_size):
                # Crear capacidades base para cada worker
                capability = WorkerCapability(
                    worker_id=worker_id,
                    max_concurrent_tasks=1,
                    current_load=0.0,
                    specialty_patterns=self._assign_worker_specialties(worker_id)
                )
                self.worker_capabilities[worker_id] = capability
            
            self._initialized = True
            print(f"   ✅ Workers inicializados: {len(self.worker_capabilities)}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error inicializando workers: {e}")
            return False
    
    def _assign_worker_specialties(self, worker_id: int) -> List[str]:
        """Asignar especialidades a workers para optimización"""
        # Distribuir especialidades de forma balanceada
        all_patterns = ['BOS', 'CHoCH', 'FVG', 'OB', 'Displacement', 'SilverBullet']
        
        # Worker 0: BOS, CHoCH
        # Worker 1: FVG, OB  
        # Worker 2: Displacement, SilverBullet
        # Worker 3+: Round robin
        
        patterns_per_worker = 2
        start_index = (worker_id * patterns_per_worker) % len(all_patterns)
        
        specialties = []
        for i in range(patterns_per_worker):
            pattern_index = (start_index + i) % len(all_patterns)
            specialties.append(all_patterns[pattern_index])
        
        return specialties
    
    def analyze_task_complexity(self, task: AnalysisTask) -> SmartTask:
        """Analizar complejidad de tarea y convertir a SmartTask"""
        # Estimar complejidad basada en datos y timeframe
        data_size = len(task.data) if hasattr(task, 'data') and task.data is not None else 0
        
        # Determinar complejidad
        if data_size < 100:
            complexity = TaskComplexity.LOW
            estimated_time = 0.01
        elif data_size < 500:
            complexity = TaskComplexity.MEDIUM  
            estimated_time = 0.05
        elif data_size < 1000:
            complexity = TaskComplexity.HIGH
            estimated_time = 0.1
        else:
            complexity = TaskComplexity.CRITICAL
            estimated_time = 0.2
        
        # Ajustar por timeframe
        timeframe_multipliers = {
            'M5': 1.0,
            'M15': 1.2,
            'M30': 1.5,
            'H1': 2.0,
            'H4': 2.5,
            'D1': 3.0
        }
        
        multiplier = timeframe_multipliers.get(task.timeframe, 1.0)
        estimated_time *= multiplier
        
        # Estimar memoria requerida
        estimated_memory = data_size * 0.01  # ~10KB por 1000 rows
        
        smart_task = SmartTask(
            task_id=task.task_id,
            symbol=task.symbol,
            timeframe=task.timeframe,
            data=task.data,
            priority=task.priority,
            complexity=complexity,
            estimated_time=estimated_time,
            required_memory_mb=estimated_memory
        )
        
        return smart_task
    
    def find_optimal_worker(self, task: SmartTask) -> int:
        """Encontrar el worker óptimo para una tarea"""
        if not self._initialized:
            self.initialize_workers()
        
        best_worker_id = 0
        best_score = float('inf')
        
        with self._lock:
            for worker_id, capability in self.worker_capabilities.items():
                # Calcular score de asignación
                score = self._calculate_assignment_score(task, capability)
                
                if score < best_score:
                    best_score = score
                    best_worker_id = worker_id
        
        return best_worker_id
    
    def _calculate_assignment_score(self, task: SmartTask, capability: WorkerCapability) -> float:
        """Calcular score de asignación worker-task (menor = mejor)"""
        score = 0.0
        
        # Factor 1: Carga actual del worker (peso: 40%)
        load_factor = capability.current_load * 0.4
        score += load_factor
        
        # Factor 2: Especialidad del worker (peso: 30%)
        specialty_bonus = 0.0
        if hasattr(task, 'data') and task.data is not None:
            # Simular detección de pattern type basado en symbol/timeframe
            pattern_type = self._guess_pattern_type(task.symbol, task.timeframe)
            if pattern_type in capability.specialty_patterns:
                specialty_bonus = -0.3  # Bonus (reduce score)
        
        score += specialty_bonus
        
        # Factor 3: Performance histórica (peso: 20%)
        performance_factor = (2.0 - capability.performance_score) * 0.2
        score += performance_factor
        
        # Factor 4: Tiempo estimado vs capacidad (peso: 10%)
        time_factor = task.estimated_time / (capability.avg_task_time + 0.001) * 0.1
        score += time_factor
        
        return score
    
    def _guess_pattern_type(self, symbol: str, timeframe: str) -> str:
        """Adivinar tipo de pattern basado en símbolo y timeframe"""
        # Heurística simple para asignar patterns
        if 'EUR' in symbol:
            return 'BOS'
        elif 'GBP' in symbol:
            return 'CHoCH'
        elif 'USD' in symbol:
            return 'FVG'
        elif 'XAU' in symbol:
            return 'OB'
        else:
            return 'Displacement'
    
    def distribute_analysis_tasks(self, tasks: List[AnalysisTask]) -> List[Tuple[SmartTask, int]]:
        """Distribuir tareas según complejidad y capacidad CPU"""
        if not self._initialized:
            self.initialize_workers()
        
        print(f"⚙️ Distribuyendo {len(tasks)} tareas...")
        start_time = time.time()
        
        distributed_tasks = []
        
        # Convertir tareas a SmartTasks y analizar complejidad
        smart_tasks = []
        for task in tasks:
            smart_task = self.analyze_task_complexity(task)
            smart_tasks.append(smart_task)
        
        # Ordenar por prioridad y complejidad
        smart_tasks.sort()
        
        # Distribuir tareas
        for task in smart_tasks:
            optimal_worker = self.find_optimal_worker(task)
            task.preferred_worker_id = optimal_worker
            
            # Actualizar carga del worker
            with self._lock:
                if optimal_worker in self.worker_capabilities:
                    self.worker_capabilities[optimal_worker].current_load += task.estimated_time
            
            distributed_tasks.append((task, optimal_worker))
        
        distribution_time = time.time() - start_time
        
        # Actualizar estadísticas
        with self._lock:
            self.distribution_stats['tasks_distributed'] += len(tasks)
            self.distribution_stats['avg_distribution_time'] = (
                (self.distribution_stats['avg_distribution_time'] * 
                 (self.distribution_stats['tasks_distributed'] - len(tasks)) +
                 distribution_time) / self.distribution_stats['tasks_distributed']
            )
            
            # Calcular score de balance de carga
            loads = [cap.current_load for cap in self.worker_capabilities.values()]
            if loads and max(loads) > 0:
                load_variance = statistics.variance(loads) if len(loads) > 1 else 0
                self.distribution_stats['load_balance_score'] = 1.0 / (1.0 + load_variance)
        
        print(f"   ✅ Distribución completada en {distribution_time:.3f}s")
        print(f"   📊 Balance de carga score: {self.distribution_stats['load_balance_score']:.3f}")
        
        return distributed_tasks
    
    def update_worker_performance(self, worker_id: int, task_result: AnalysisResult):
        """Actualizar rendimiento del worker basado en resultados"""
        with self._lock:
            if worker_id in self.worker_capabilities:
                capability = self.worker_capabilities[worker_id]
                
                # Actualizar estadísticas
                capability.total_tasks_completed += 1
                
                # Actualizar tiempo promedio
                if capability.avg_task_time == 0:
                    capability.avg_task_time = task_result.processing_time
                else:
                    capability.avg_task_time = (
                        (capability.avg_task_time * (capability.total_tasks_completed - 1) +
                         task_result.processing_time) / capability.total_tasks_completed
                    )
                
                # Actualizar performance score basado en éxito/velocidad
                if task_result.success:
                    # Bonus por éxito y velocidad
                    speed_factor = 1.0 / (task_result.processing_time + 0.001)
                    capability.performance_score = (capability.performance_score * 0.9 + 
                                                   speed_factor * 0.1)
                else:
                    # Penalización por fallo
                    capability.performance_score *= 0.95
                
                # Reducir carga actual
                estimated_time = getattr(task_result, 'estimated_time', task_result.processing_time)
                capability.current_load = max(0.0, capability.current_load - estimated_time)
    
    def balance_load_dynamically(self):
        """Balance dinámico de carga durante ejecución"""
        with self._lock:
            # Identificar workers sobrecargados y sub-utilizados
            loads = [(wid, cap.current_load) for wid, cap in self.worker_capabilities.items()]
            loads.sort(key=lambda x: x[1])
            
            underutilized = loads[:len(loads)//2]
            overloaded = loads[len(loads)//2:]
            
            # Redistribuir carga si es necesario
            redistributions = 0
            for over_worker_id, over_load in overloaded:
                for under_worker_id, under_load in underutilized:
                    if over_load > under_load * 1.5:  # Threshold 50% diferencia
                        # Mover algo de carga
                        transfer_amount = (over_load - under_load) * 0.1
                        self.worker_capabilities[over_worker_id].current_load -= transfer_amount
                        self.worker_capabilities[under_worker_id].current_load += transfer_amount
                        redistributions += 1
                        break
            
            if redistributions > 0:
                print(f"   🔄 Balance dinámico: {redistributions} redistribuciones")
    
    def get_distribution_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del motor de distribución"""
        with self._lock:
            worker_stats = {}
            for worker_id, capability in self.worker_capabilities.items():
                worker_stats[f'worker_{worker_id}'] = {
                    'current_load': capability.current_load,
                    'tasks_completed': capability.total_tasks_completed,
                    'avg_task_time': capability.avg_task_time,
                    'performance_score': capability.performance_score,
                    'specialties': capability.specialty_patterns
                }
            
            return {
                'engine_stats': self.distribution_stats.copy(),
                'worker_stats': worker_stats,
                'total_workers': len(self.worker_capabilities),
                'initialized': self._initialized
            }
    
    def reset_worker_loads(self):
        """Reset cargas de workers (útil para testing)"""
        with self._lock:
            for capability in self.worker_capabilities.values():
                capability.current_load = 0.0
        print("🔄 Worker loads reset")
    
    def shutdown(self, wait=True):
        """Cerrar el motor de distribución de trabajo"""
        try:
            with self._lock:
                # Limpiar queues
                while not self.task_queue.empty():
                    try:
                        self.task_queue.get_nowait()
                    except:
                        break
                
                while not self.completed_tasks.empty():
                    try:
                        self.completed_tasks.get_nowait()
                    except:
                        break
                
                while not self.failed_tasks.empty():
                    try:
                        self.failed_tasks.get_nowait()
                    except:
                        break
                
                # Reset stats
                self.distribution_stats = {
                    'tasks_distributed': 0,
                    'tasks_completed': 0,
                    'tasks_failed': 0,
                    'avg_distribution_time': 0.0,
                    'load_balance_score': 1.0,
                    'total_processing_time': 0.0
                }
                
                self._initialized = False
                print("   ✅ Work Distribution Engine cerrado exitosamente")
        except Exception as e:
            print(f"   ⚠️ Error cerrando Work Distribution Engine: {e}")


# Instancia global del motor de distribución
_distribution_engine_instance = None
_distribution_engine_lock = threading.Lock()


def get_work_distribution_engine(pool_size: Optional[int] = None) -> WorkDistributionEngine:
    """Obtener instancia singleton del motor de distribución"""
    global _distribution_engine_instance
    
    with _distribution_engine_lock:
        if _distribution_engine_instance is None:
            _distribution_engine_instance = WorkDistributionEngine(pool_size)
        return _distribution_engine_instance


def shutdown_distribution_engine():
    """Shutdown del motor de distribución global"""
    global _distribution_engine_instance
    
    with _distribution_engine_lock:
        if _distribution_engine_instance is not None:
            _distribution_engine_instance.shutdown()
            _distribution_engine_instance = None
            print("🔄 Work Distribution Engine shutdown")


# Funciones de utilidad adicionales para optimización enterprise

def validate_trading_task_data(task: AnalysisTask) -> bool:
    """
    Validación robusta de datos de tarea para trading
    
    Args:
        task: Tarea de análisis a validar
        
    Returns:
        bool: True si los datos son válidos para trading
    """
    try:
        if not hasattr(task, 'data') or task.data is None or task.data.empty:
            print(f"❌ TRADING VALIDATION: Datos vacíos o None para {task.task_id}")
            return False
        
        # Verificar columnas OHLC requeridas
        required_columns = ['open', 'high', 'low', 'close']
        missing_cols = [col for col in required_columns if col not in task.data.columns]
        if missing_cols:
            print(f"❌ TRADING VALIDATION: Faltan columnas OHLC: {missing_cols}")
            return False
        
        # Verificar valores None en datos críticos
        null_counts = task.data[required_columns].isnull().sum()
        if null_counts.any():
            print(f"❌ TRADING VALIDATION: Valores None en OHLC: {null_counts.to_dict()}")
            return False
        
        # Verificar lógica de precios
        invalid_highs = (task.data['high'] < task.data['low']).sum()
        if invalid_highs > 0:
            print(f"❌ TRADING VALIDATION: {invalid_highs} velas con High < Low")
            return False
        
        invalid_closes = ((task.data['close'] > task.data['high']) | 
                         (task.data['close'] < task.data['low'])).sum()
        if invalid_closes > 0:
            print(f"❌ TRADING VALIDATION: {invalid_closes} velas con Close fuera de rango H-L")
            return False
        
        # Verificar tamaño mínimo para análisis
        if len(task.data) < 50:
            print(f"⚠️ TRADING VALIDATION: Solo {len(task.data)} velas, mínimo recomendado 50")
            return False
        
        # Verificar que no hay datos futuros
        if hasattr(task.data, 'timestamp'):
            max_timestamp = task.data['timestamp'].max()
            current_time = pd.Timestamp.now()
            if max_timestamp > current_time:
                print(f"❌ TRADING VALIDATION: Datos futuros detectados: {max_timestamp}")
                return False
        
        print(f"✅ TRADING VALIDATION: {task.task_id} - {len(task.data)} velas válidas")
        return True
        
    except Exception as e:
        print(f"❌ TRADING VALIDATION: Error validando {task.task_id}: {e}")
        return False


def create_optimized_task_batches(tasks: List[AnalysisTask], 
                                 max_batch_size: int = 10) -> List[List[AnalysisTask]]:
    """
    Crear lotes optimizados de tareas para procesamiento paralelo eficiente
    
    Args:
        tasks: Lista de tareas de análisis
        max_batch_size: Tamaño máximo de lote
        
    Returns:
        Lista de lotes de tareas optimizados
    """
    if not tasks:
        return []
    
    # Validar todas las tareas primero
    valid_tasks = [task for task in tasks if validate_trading_task_data(task)]
    
    if not valid_tasks:
        print("❌ TRADING CRITICAL: No hay tareas válidas para procesar")
        return []
    
    # Ordenar por prioridad y complejidad estimada
    def task_priority_key(task):
        complexity = len(task.data) if hasattr(task, 'data') and task.data is not None else 0
        return (task.priority, complexity)
    
    sorted_tasks = sorted(valid_tasks, key=task_priority_key)
    
    # Crear lotes balanceados
    batches = []
    current_batch = []
    current_batch_complexity = 0
    max_complexity_per_batch = 10000  # Máximo de registros por lote
    
    for task in sorted_tasks:
        task_complexity = len(task.data) if hasattr(task, 'data') and task.data is not None else 0
        
        # Si agregar esta tarea excede los límites, crear nuevo lote
        if (len(current_batch) >= max_batch_size or 
            current_batch_complexity + task_complexity > max_complexity_per_batch):
            
            if current_batch:
                batches.append(current_batch)
                current_batch = []
                current_batch_complexity = 0
        
        current_batch.append(task)
        current_batch_complexity += task_complexity
    
    # Agregar último lote si no está vacío
    if current_batch:
        batches.append(current_batch)
    
    print(f"📦 BATCH OPTIMIZATION: {len(valid_tasks)} tareas → {len(batches)} lotes óptimos")
    return batches


def monitor_system_resources() -> Dict[str, Any]:
    """
    Monitorear recursos del sistema para optimización dinámica
    
    Returns:
        Diccionario con métricas de recursos del sistema
    """
    try:
        import psutil
        
        # CPU metrics con manejo robusto de None
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count() or 4  # Fallback a 4 cores físicos
        cpu_count_logical = psutil.cpu_count(logical=True) or cpu_count  # Fallback a cores físicos
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)
        
        # Determinar nivel de carga del sistema con valores seguros
        if cpu_percent < 25:
            load_level = "IDLE"
            optimal_workers = cpu_count_logical
        elif cpu_percent < 50:
            load_level = "LOW"
            optimal_workers = max(1, int(cpu_count_logical * 0.8))
        elif cpu_percent < 75:
            load_level = "MEDIUM"
            optimal_workers = max(1, int(cpu_count_logical * 0.6))
        elif cpu_percent < 90:
            load_level = "HIGH"
            optimal_workers = max(1, int(cpu_count_logical * 0.4))
        else:
            load_level = "CRITICAL"
            optimal_workers = max(1, int(cpu_count_logical * 0.2))
        
        # Recomendaciones de optimización
        recommendations = []
        
        if memory_percent > 85:
            recommendations.append("REDUCE_BATCH_SIZE")
        if cpu_percent > 90:
            recommendations.append("REDUCE_WORKERS")
        if memory_available_gb < 1.0:
            recommendations.append("URGENT_MEMORY_CLEANUP")
        
        return {
            'cpu_percent': cpu_percent,
            'cpu_count_physical': cpu_count,
            'cpu_count_logical': cpu_count_logical,
            'memory_percent': memory_percent,
            'memory_available_gb': round(memory_available_gb, 2),
            'load_level': load_level,
            'optimal_workers': optimal_workers,
            'recommendations': recommendations,
            'trading_safe': cpu_percent < 80 and memory_percent < 80
        }
        
    except ImportError:
        # Fallback si psutil no está disponible
        cpu_count = os.cpu_count() or 4
        return {
            'cpu_percent': 50.0,  # Estimación conservadora
            'cpu_count_physical': cpu_count,
            'cpu_count_logical': cpu_count,
            'memory_percent': 50.0,  # Estimación conservadora
            'memory_available_gb': 4.0,  # Estimación conservadora
            'load_level': "MEDIUM",
            'optimal_workers': max(1, int(cpu_count * 0.75)),
            'recommendations': [],
            'trading_safe': True
        }
    except Exception as e:
        print(f"⚠️ Error monitoreando recursos: {e}")
        return {
            'cpu_percent': 0.0,
            'cpu_count_physical': 1,
            'cpu_count_logical': 1,
            'memory_percent': 0.0,
            'memory_available_gb': 1.0,
            'load_level': "UNKNOWN",
            'optimal_workers': 1,
            'recommendations': ["MONITORING_ERROR"],
            'trading_safe': False
        }


# Testing y validación
if __name__ == "__main__":
    print("🧪 Testing Work Distribution Engine...")
    
    # Test 1: Inicialización
    engine = WorkDistributionEngine()
    print(f"   Pool size inicializado: {engine.pool_size}")
    
    # Test 2: Inicialización de workers
    success = engine.initialize_workers()
    print(f"   Workers inicializados: {success}")
    
    # Test 3: Estadísticas
    stats = engine.get_distribution_statistics()
    print(f"   Workers totales: {stats['total_workers']}")
    
    # Test 4: Monitoreo de recursos
    resources = monitor_system_resources()
    print(f"   CPU: {resources['cpu_percent']}%, Memoria: {resources['memory_percent']}%")
    print(f"   Nivel de carga: {resources['load_level']}")
    print(f"   Workers óptimos: {resources['optimal_workers']}")
    print(f"   Trading safe: {resources['trading_safe']}")
    
    # Test 5: Shutdown
    engine.shutdown()
    print("   ✅ Testing completado exitosamente")
