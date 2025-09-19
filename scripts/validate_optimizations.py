#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 OPTIMIZATIONS VALIDATOR - ICT ENGINE v6.0 ENTERPRISE
======================================================

Valida las optimizaciones implementadas basadas en análisis de performance.
Simula carga de memoria y verifica que las optimizaciones funcionen.

Autor: ICT Engine v6.0 Team
Fecha: 19 Septiembre 2025
"""

import sys
import time
import psutil
from datetime import datetime
from pathlib import Path

# Add project paths
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "01-CORE"))

def validate_memory_optimizations():
    """Validar optimizaciones de memoria implementadas"""
    print("🔧 Validando optimizaciones de memoria...")
    
    try:
        from monitoring.production_system_monitor import ProductionSystemMonitor, SystemMetrics, SystemHealthStatus
        
        # Crear monitor con configuración optimizada
        monitor = ProductionSystemMonitor()
        config = monitor._get_default_config()
        
        print(f"📊 Configuración optimizada:")
        print(f"   • metrics_history_size: {config['metrics_history_size']} (target: 300)")
        print(f"   • max_alerts: {config['max_alerts']} (target: 100)")
        print(f"   • cleanup_threshold: {config['aggressive_cleanup_threshold']}% (target: 80%)")
        print(f"   • cleanup_interval: {config.get('memory_cleanup_interval', 300)}s (target: 180s)")
        print(f"   • cleanup_ratio: {config['cleanup_history_ratio']} (target: 0.05)")
        print(f"   • memory_warning: {config['thresholds']['memory_warning']}% (target: 75%)")
        
        # Validar valores optimizados
        optimizations_valid = True
        
        if config['metrics_history_size'] > 300:
            print("❌ metrics_history_size no optimizado")
            optimizations_valid = False
            
        if config['max_alerts'] > 100:
            print("❌ max_alerts no optimizado")
            optimizations_valid = False
            
        if config['aggressive_cleanup_threshold'] > 80:
            print("❌ cleanup_threshold no optimizado")
            optimizations_valid = False
            
        if config['cleanup_history_ratio'] > 0.05:
            print("❌ cleanup_ratio no optimizado")
            optimizations_valid = False
            
        if config['thresholds']['memory_warning'] > 75:
            print("❌ memory_warning threshold no optimizado")
            optimizations_valid = False
            
        if optimizations_valid:
            print("✅ Todas las optimizaciones implementadas correctamente")
        else:
            print("⚠️  Algunas optimizaciones no están aplicadas")
            
        # Test de cleanup agresivo
        print("\n🧪 Testing cleanup agresivo...")
        
        # Llenar con datos de prueba
        sample_metrics = SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=50.0,
            memory_percent=85.0,  # Alto para triggear cleanup
            memory_available_gb=2.0,
            disk_usage_percent=40.0,
            network_connections=100,
            process_count=200,
            uptime_seconds=3600.0,
            health_status=SystemHealthStatus.WARNING,
        )
        
        # Simular acumulación de datos
        for i in range(500):  # Más del límite
            monitor.metrics_history.append(sample_metrics)
        
        for i in range(200):  # Más del límite
            from monitoring.production_system_monitor import Alert, AlertLevel
            alert = Alert(
                timestamp=datetime.now(),
                level=AlertLevel.WARNING,
                component="Test",
                message=f"Test alert {i}",
                metrics={}
            )
            monitor.alerts.append(alert)
        
        print(f"📈 Antes del cleanup:")
        print(f"   • Métricas: {len(monitor.metrics_history)}")
        print(f"   • Alertas: {len(monitor.alerts)}")
        
        # Ejecutar cleanup
        monitor._perform_memory_cleanup()
        
        print(f"📉 Después del cleanup:")
        print(f"   • Métricas: {len(monitor.metrics_history)} (target: ~15)")
        print(f"   • Alertas: {len(monitor.alerts)} (target: ~20)")
        
        # Validar resultados
        cleanup_effective = True
        
        expected_metrics = int(300 * 0.05)  # 5% de 300 = 15
        if len(monitor.metrics_history) > expected_metrics + 5:  # Margen de 5
            print(f"❌ Cleanup de métricas no suficientemente agresivo: {len(monitor.metrics_history)} > {expected_metrics}")
            cleanup_effective = False
            
        expected_alerts = int(100 * 0.2)  # 20% de 100 = 20
        if len(monitor.alerts) > expected_alerts + 5:  # Margen de 5
            print(f"❌ Cleanup de alertas no suficientemente agresivo: {len(monitor.alerts)} > {expected_alerts}")
            cleanup_effective = False
            
        if cleanup_effective:
            print("✅ Cleanup agresivo funcionando correctamente")
        else:
            print("⚠️  Cleanup agresivo necesita ajustes")
            
        return optimizations_valid and cleanup_effective
        
    except Exception as e:
        print(f"❌ Error durante validación: {e}")
        return False

def validate_system_performance():
    """Validar métricas de rendimiento del sistema"""
    print("\n💻 Validando rendimiento del sistema...")
    
    try:
        # Métricas actuales
        cpu_percent = psutil.cpu_percent(interval=1.0)
        memory = psutil.virtual_memory()
        
        print(f"📊 Métricas actuales:")
        print(f"   • CPU: {cpu_percent:.1f}%")
        print(f"   • Memoria: {memory.percent:.1f}%")
        print(f"   • Memoria disponible: {memory.available / (1024**3):.2f} GB")
        
        # Validar mejoras
        if memory.percent < 85:  # Target de mejora
            print("✅ Uso de memoria mejorado vs baseline (87.3%)")
        else:
            print("⚠️  Uso de memoria aún alto, optimizaciones en progreso")
            
        if cpu_percent < 60:  # Margen saludable
            print("✅ Uso de CPU dentro de rangos óptimos")
        else:
            print("⚠️  Uso de CPU elevado")
            
        return memory.percent < 85 and cpu_percent < 60
        
    except Exception as e:
        print(f"❌ Error validando rendimiento: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 ICT Engine v6.0 - Optimizations Validator")
    print("=" * 55)
    
    start_time = time.time()
    
    # Validar optimizaciones
    optimizations_ok = validate_memory_optimizations()
    performance_ok = validate_system_performance()
    
    execution_time = time.time() - start_time
    
    print(f"\n📋 RESUMEN DE VALIDACIÓN:")
    print(f"   • Optimizaciones: {'✅ OK' if optimizations_ok else '❌ FALLÓ'}")
    print(f"   • Performance: {'✅ OK' if performance_ok else '⚠️  NECESITA MEJORA'}")
    print(f"   • Tiempo de ejecución: {execution_time:.2f}s")
    
    if optimizations_ok and performance_ok:
        print("🎉 ¡Todas las optimizaciones funcionando correctamente!")
        return 0
    else:
        print("🔧 Algunas optimizaciones requieren ajustes")
        return 1

if __name__ == "__main__":
    exit(main())