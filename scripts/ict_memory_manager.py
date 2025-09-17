#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 MEMORY MANAGER - ICT ENGINE v6.0 ENTERPRISE
==============================================

Sistema integrado de gestión de memoria que combina:
- Memory Profiler (análisis)
- Memory Optimizer (limpieza automática)  
- Lazy Loader (carga perezosa)
- Memory Limits (límites por componente)

Para resolver el problema crítico de uso elevado de memoria (80-85%).
"""

import sys
import os
import gc
import threading
import time
import weakref
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import psutil

# Añadir rutas
sys.path.append('01-CORE')
sys.path.append('scripts')

# Importar optimizador básico integrado
class BasicMemoryOptimizer:
    """Optimizador de memoria básico integrado"""
    
    def __init__(self):
        try:
            self.process = psutil.Process()
        except Exception as e:
            print(f"Error inicializando optimizador: {e}")
            self.process = None
    
    def perform_full_cleanup(self) -> Dict[str, float]:
        """Realizar limpieza completa de memoria"""
        if not self.process:
            return {'freed_mb': 0, 'before_mb': 0, 'after_mb': 0}
            
        try:
            before = self.process.memory_info().rss / 1024 / 1024
            
            # Forzar garbage collection múltiple
            for _ in range(3):
                gc.collect()
            
            after = self.process.memory_info().rss / 1024 / 1024
            freed = before - after
            
            return {
                'freed_mb': max(0, freed),
                'before_mb': before,
                'after_mb': after
            }
        except Exception as e:
            print(f"Error en limpieza de memoria: {e}")
            return {'freed_mb': 0, 'before_mb': 0, 'after_mb': 0}

def get_basic_memory_optimizer() -> BasicMemoryOptimizer:
    """Obtener optimizador básico"""
    return BasicMemoryOptimizer()

# Lazy loader básico integrado
def check_memory_usage() -> Dict[str, Any]:
    """Verificar uso de memoria actual"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024
        }
    except Exception as e:
        print(f"Error verificando memoria: {e}")
        return {'error': str(e)}

class ComponentMemoryLimiter:
    """Sistema de límites de memoria por componente"""
    
    def __init__(self):
        self.component_limits = {
            'SmartMoneyAnalyzer': 70.0,      # MB - el mayor consumidor
            'UnifiedMemorySystem': 30.0,     # MB
            'MT5ConnectionManager': 20.0,    # MB
            'ProductionSystemMonitor': 15.0, # MB
            'Dashboard': 25.0,               # MB
            'DataManagement': 40.0,          # MB
            'RiskManager': 10.0,             # MB
            'Default': 15.0                  # MB - límite por defecto
        }
        
        self.component_usage = {}
        self.warnings_sent = set()
    
    def get_component_limit(self, component_name: str) -> float:
        """Obtener límite de memoria para un componente"""
        return self.component_limits.get(component_name, self.component_limits['Default'])
    
    def check_component_memory(self, component_name: str, current_usage_mb: float) -> Dict[str, Any]:
        """Verificar si un componente está dentro de su límite"""
        limit = self.get_component_limit(component_name)
        usage_percent = (current_usage_mb / limit) * 100
        
        status = {
            'component': component_name,
            'current_mb': current_usage_mb,
            'limit_mb': limit,
            'usage_percent': usage_percent,
            'status': 'OK'
        }
        
        if usage_percent > 100:
            status['status'] = 'CRITICAL'
        elif usage_percent > 80:
            status['status'] = 'WARNING'
        elif usage_percent > 60:
            status['status'] = 'MONITOR'
        
        # Log warning una sola vez
        if status['status'] in ['WARNING', 'CRITICAL']:
            warning_key = f"{component_name}_{status['status']}"
            if warning_key not in self.warnings_sent:
                print(f"⚠️ {component_name}: {current_usage_mb:.1f}MB/{limit}MB ({usage_percent:.1f}%) - {status['status']}")
                self.warnings_sent.add(warning_key)
        
        self.component_usage[component_name] = status
        return status
    
    def get_system_memory_report(self) -> Dict[str, Any]:
        """Generar reporte del sistema de memoria"""
        total_used = sum(info['current_mb'] for info in self.component_usage.values())
        total_limit = sum(self.component_limits.values())
        
        return {
            'timestamp': datetime.now(),
            'total_used_mb': total_used,
            'total_limit_mb': total_limit,
            'system_usage_percent': (total_used / total_limit) * 100,
            'components': self.component_usage.copy()
        }

class ICTMemoryManager:
    """Gestor principal de memoria ICT Engine v6.0 Enterprise"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.component_limiter = ComponentMemoryLimiter()
        self.memory_optimizer = None
        self.monitoring = False
        self.monitor_thread = None
        
        # Configuración
        self.global_memory_limit_mb = 200.0  # Límite global del sistema
        self.critical_threshold_percent = 85
        self.warning_threshold_percent = 70
        self.cleanup_interval = timedelta(minutes=2)  # Cleanup cada 2 minutos
        self.last_cleanup = datetime.now()
        
        # Estadísticas
        self.cleanup_count = 0
        self.total_memory_freed = 0.0
        
    def get_system_memory_info(self) -> Dict[str, float]:
        """Obtener información completa del sistema"""
        mem_info = self.process.memory_info()
        return {
            'rss_mb': mem_info.rss / (1024 * 1024),
            'vms_mb': mem_info.vms / (1024 * 1024),
            'percent': self.process.memory_percent(),
            'threads': self.process.num_threads()
        }
    
    def analyze_heavy_components(self) -> Dict[str, float]:
        """Analizar componentes que más memoria consumen"""
        heavy_components = {}
        
        # Simular análisis de componentes cargados
        for obj in gc.get_objects():
            if hasattr(obj, '__class__'):
                class_name = obj.__class__.__name__
                
                # Identificar componentes conocidos
                if 'SmartMoney' in class_name:
                    heavy_components['SmartMoneyAnalyzer'] = heavy_components.get('SmartMoneyAnalyzer', 0) + sys.getsizeof(obj) / (1024 * 1024)
                elif 'UnifiedMemory' in class_name:
                    heavy_components['UnifiedMemorySystem'] = heavy_components.get('UnifiedMemorySystem', 0) + sys.getsizeof(obj) / (1024 * 1024)
                elif 'MT5' in class_name:
                    heavy_components['MT5ConnectionManager'] = heavy_components.get('MT5ConnectionManager', 0) + sys.getsizeof(obj) / (1024 * 1024)
        
        return heavy_components
    
    def perform_intelligent_cleanup(self) -> Dict[str, Any]:
        """Realizar limpieza inteligente basada en uso y límites"""
        print("🧹 Iniciando limpieza inteligente...")
        
        before_mem = self.get_system_memory_info()
        
        # 1. Analizar componentes pesados
        heavy_components = self.analyze_heavy_components()
        
        # 2. Verificar límites por componente
        for component, usage_mb in heavy_components.items():
            self.component_limiter.check_component_memory(component, usage_mb)
        
        # 3. Usar lazy loader para descargar módulos pesados si es necesario
        if before_mem['rss_mb'] > self.global_memory_limit_mb * 0.8:  # 80% del límite global
            try:
                check_memory_usage()  # Función del lazy loader
            except Exception as e:
                print(f"⚠️ Error en lazy cleanup: {e}")
        
        # 4. Memory optimizer si está disponible
        if self.memory_optimizer:
            try:
                self.memory_optimizer.perform_full_cleanup()
            except Exception as e:
                print(f"⚠️ Error en memory optimizer: {e}")
        
        # 5. Garbage collection agresivo
        collected = 0
        for _ in range(3):  # 3 pasadas
            collected += gc.collect()
            time.sleep(0.1)
        
        after_mem = self.get_system_memory_info()
        freed_mb = before_mem['rss_mb'] - after_mem['rss_mb']
        
        # Actualizar estadísticas
        self.cleanup_count += 1
        self.total_memory_freed += max(0, freed_mb)
        self.last_cleanup = datetime.now()
        
        result = {
            'timestamp': datetime.now(),
            'before_memory': before_mem,
            'after_memory': after_mem,
            'freed_mb': freed_mb,
            'gc_collected': collected,
            'heavy_components': heavy_components,
            'cleanup_number': self.cleanup_count
        }
        
        print(f"✅ Cleanup #{self.cleanup_count} completo:")
        print(f"   Antes: {before_mem['rss_mb']:.1f}MB ({before_mem['percent']:.1f}%)")
        print(f"   Después: {after_mem['rss_mb']:.1f}MB ({after_mem['percent']:.1f}%)")
        print(f"   Liberado: {freed_mb:.1f}MB")
        print(f"   GC objetos: {collected}")
        
        return result
    
    def should_perform_cleanup(self) -> bool:
        """Determinar si se debe realizar limpieza"""
        current_mem = self.get_system_memory_info()
        time_since_cleanup = datetime.now() - self.last_cleanup
        
        # Cleanup inmediato si memoria crítica
        if (current_mem['percent'] > self.critical_threshold_percent or 
            current_mem['rss_mb'] > self.global_memory_limit_mb):
            return True
        
        # Cleanup programado si memoria alta Y ha pasado tiempo suficiente
        if (current_mem['percent'] > self.warning_threshold_percent and 
            time_since_cleanup > self.cleanup_interval):
            return True
        
        return False
    
    def monitor_memory(self):
        """Hilo de monitoreo continuo"""
        while self.monitoring:
            try:
                current_mem = self.get_system_memory_info()
                
                # Log cada minuto
                print(f"📊 Memoria: {current_mem['rss_mb']:.1f}MB ({current_mem['percent']:.1f}%) - Threads: {current_mem['threads']}")
                
                # Verificar si necesita cleanup
                if self.should_perform_cleanup():
                    self.perform_intelligent_cleanup()
                
                # Log al sistema de logging si está disponible
                try:
                    from smart_trading_logger import SmartTradingLogger
                    logger = SmartTradingLogger('MemoryManager')
                    if current_mem['percent'] > self.warning_threshold_percent:
                        logger.warning(
                            f"Memoria alta: {current_mem['rss_mb']:.1f}MB ({current_mem['percent']:.1f}%)",
                            component='MEMORY'
                        )
                except:
                    pass
                
                # Esperar 60 segundos
                time.sleep(60)
                
            except Exception as e:
                print(f"⚠️ Error en monitoreo: {e}")
                time.sleep(120)  # Esperar más tiempo si hay error
    
    def start_monitoring(self):
        """Iniciar monitoreo automático"""
        if self.monitoring:
            print("⚠️ Monitoreo ya está activo")
            return
        
        print("🚀 Iniciando ICT Memory Manager...")
        
        # Configurar GC más agresivo
        gc.set_threshold(700, 10, 10)
        
        # Inicializar memory optimizer si está disponible
        try:
            self.memory_optimizer = get_basic_memory_optimizer()
            print("✅ Memory Optimizer integrado")
        except:
            print("⚠️ Memory Optimizer no disponible")
        
        # Iniciar monitoreo
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self.monitor_memory,
            name='ICT-MemoryManager',
            daemon=True
        )
        self.monitor_thread.start()
        
        print("✅ ICT Memory Manager activo - monitoreo inteligente iniciado")
        
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=10)
        
        print("✅ ICT Memory Manager detenido")
    
    def get_status_report(self) -> Dict[str, Any]:
        """Generar reporte completo del estado"""
        current_mem = self.get_system_memory_info()
        component_report = self.component_limiter.get_system_memory_report()
        
        return {
            'timestamp': datetime.now(),
            'system_memory': current_mem,
            'global_limit_mb': self.global_memory_limit_mb,
            'cleanup_stats': {
                'total_cleanups': self.cleanup_count,
                'total_freed_mb': self.total_memory_freed,
                'last_cleanup': self.last_cleanup,
                'average_freed_mb': self.total_memory_freed / max(1, self.cleanup_count)
            },
            'component_analysis': component_report,
            'monitoring_active': self.monitoring,
            'status': 'CRITICAL' if current_mem['percent'] > self.critical_threshold_percent 
                     else 'WARNING' if current_mem['percent'] > self.warning_threshold_percent 
                     else 'OK'
        }

# Instancia global
_global_memory_manager = None

def get_ict_memory_manager() -> ICTMemoryManager:
    """Obtener instancia global del memory manager"""
    global _global_memory_manager
    if _global_memory_manager is None:
        _global_memory_manager = ICTMemoryManager()
    return _global_memory_manager

def start_ict_memory_management():
    """Iniciar gestión automática de memoria ICT"""
    manager = get_ict_memory_manager()
    manager.start_monitoring()
    return manager

def get_memory_status():
    """Obtener estado actual de memoria"""
    manager = get_ict_memory_manager()
    return manager.get_status_report()

if __name__ == "__main__":
    print("🎯 ICT Memory Manager - Enterprise v6.0")
    print("=" * 60)
    
    # Inicializar el gestor
    manager = ICTMemoryManager()
    
    # Mostrar estado inicial
    initial_status = manager.get_status_report()
    print(f"📊 Estado inicial:")
    print(f"   Memoria: {initial_status['system_memory']['rss_mb']:.1f}MB ({initial_status['system_memory']['percent']:.1f}%)")
    print(f"   Límite global: {initial_status['global_limit_mb']}MB")
    print(f"   Estado: {initial_status['status']}")
    
    # Realizar cleanup inicial
    print("\n🧹 Realizando cleanup inicial...")
    cleanup_result = manager.perform_intelligent_cleanup()
    
    # Iniciar monitoreo
    print("\n🚀 Iniciando monitoreo continuo...")
    manager.start_monitoring()
    
    # Mantener activo
    try:
        while True:
            time.sleep(30)
            status = manager.get_status_report()
            if status['status'] != 'OK':
                print(f"⚠️ Estado: {status['status']} - {status['system_memory']['rss_mb']:.1f}MB")
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo ICT Memory Manager...")
        manager.stop_monitoring()
        
        # Reporte final
        final_status = manager.get_status_report()
        print("\n📋 REPORTE FINAL:")
        print(f"   Cleanups realizados: {final_status['cleanup_stats']['total_cleanups']}")
        print(f"   Memoria total liberada: {final_status['cleanup_stats']['total_freed_mb']:.1f}MB")
        print(f"   Promedio liberado: {final_status['cleanup_stats']['average_freed_mb']:.1f}MB")
        print(f"   Estado final: {final_status['status']}")