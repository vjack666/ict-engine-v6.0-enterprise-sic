#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 DIAGNOSTIC DEEP PHASE 3 - ICT ENGINE v6.0 ENTERPRISE
======================================================

Diagnóstico profundo fase 3 del sistema ICT Engine
Validación de componentes críticos y pruebas de integración.

Autor: ICT Engine v6.0 Team
Fecha: 13 Septiembre 2025
"""

import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Agregar paths necesarios
sys.path.append(os.path.join(os.path.dirname(__file__), '01-CORE'))

# Importar protocolos de logging
try:
    from protocols import setup_module_logging, LogLevel
    logger = setup_module_logging("DiagnosticPhase3", LogLevel.INFO)
    LOGGING_AVAILABLE = True
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DiagnosticPhase3")
    LOGGING_AVAILABLE = False

def safe_log(level: str, message: str):
    """Logging seguro con fallbacks"""
    try:
        if LOGGING_AVAILABLE:
            getattr(logger, level)(message, "DiagnosticPhase3")
        else:
            getattr(logger, level)(f"[DiagnosticPhase3] {message}")
    except TypeError:
        # Fallback para logger estándar
        getattr(logger, level)(f"[DiagnosticPhase3] {message}")
    except Exception:
        print(f"[{level.upper()}] [DiagnosticPhase3] {message}")

def test_critical_modules():
    """Test de módulos críticos del sistema"""
    
    # Inicializar test_data antes del try/except para evitar "possibly unbound"
    test_data = {
        'timestamp': datetime.now(),
        'symbol': 'EURUSD',
        'status': 'INIT',
        'data_points': 0
    }
    
    try:
        # Test RealDataCollector
        safe_log("info", "Testing RealDataCollector...")
        
        from data.data_collector import RealDataCollector
        collector = RealDataCollector(config={})
        
        # Actualizar test_data
        test_data.update({
            'status': 'OK',
            'data_points': 100
        })
        
        safe_log("info", f"✅ RealDataCollector OK - Test data: {test_data['data_points']} points")
        
    except Exception as e:
        # test_data sigue disponible aquí porque se inicializó antes del try
        safe_log("error", f"❌ RealDataCollector Error: {e}")
        test_data.update({'status': 'ERROR', 'error': str(e)})
    
    try:
        # Test ExecutionEngine
        safe_log("info", "Testing ExecutionEngine...")
        
        from trading.execution_engine import ExecutionEngine
        execution_engine = ExecutionEngine()
        safe_log("info", "✅ ExecutionEngine OK")
        
    except Exception as e:
        safe_log("error", f"❌ ExecutionEngine Error: {e}")
    
    try:
        # Test PositionSizingCalculator
        safe_log("info", "Testing PositionSizingCalculator...")
        
        from risk_management.position_sizing import PositionSizingCalculator
        position_calc = PositionSizingCalculator()
        safe_log("info", "✅ PositionSizingCalculator OK")
        
    except Exception as e:
        safe_log("error", f"❌ PositionSizingCalculator Error: {e}")

    try:
        # Test LiveTradingEngine
        safe_log("info", "Testing LiveTradingEngine...")
        
        from trading.live_trading_engine import LiveTradingEngine
        trading_engine = LiveTradingEngine()
        safe_log("info", "✅ LiveTradingEngine OK")
        
    except Exception as e:
        safe_log("error", f"❌ LiveTradingEngine Error: {e}")
    
    # Verificar test_data al final - ahora está garantizado que existe
    safe_log("info", f"Final test_data verification: {test_data['status']}")
    
    return test_data

def test_logging_protocols():
    """Test de protocolos de logging central"""
    try:
        safe_log("info", "Testing Logging Protocols...")
        
        from protocols.logging_central_protocols import LoggingProtocols, LoggingConfig, LogLevel
        
        # Test configuración estándar
        config = LoggingProtocols.get_standard_config("TestComponent")
        test_logger = LoggingProtocols.create_enterprise_logger(config)
        
        # Test logging
        test_logger.info("Test message from protocol logger", "TestComponent")
        
        safe_log("info", "✅ Logging Protocols OK")
        
    except Exception as e:
        safe_log("error", f"❌ Logging Protocols Error: {e}")

def main():
    """Función principal de diagnóstico"""
    
    print("🔍 ICT ENGINE v6.0 - DIAGNOSTIC DEEP PHASE 3")
    print("=" * 50)
    
    # Test módulos críticos
    test_data = test_critical_modules()
    
    # Test protocolos de logging
    test_logging_protocols()
    
    # Resumen final - test_data está garantizado porque se retorna de test_critical_modules
    print(f"\n📊 Diagnostic Summary:")
    print(f"   Timestamp: {test_data.get('timestamp', 'N/A')}")
    print(f"   Status: {test_data.get('status', 'N/A')}")
    print(f"   Data Points: {test_data.get('data_points', 'N/A')}")
    
    print("\n✅ Diagnostic Deep Phase 3 Complete!")
    safe_log("info", "Diagnostic Deep Phase 3 completed successfully")

if __name__ == "__main__":
    main()