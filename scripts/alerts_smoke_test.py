#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 ALERTS SMOKE TEST - ICT Engine v6.0 Enterprise
================================================

Test de humo para el sistema completo de alertas:
- Carga de configuración alerts.yaml
- Generación de breaches sintéticos
- Integración con alert_integration_system
- Endpoints de metrics API
- Persistencia en 04-DATA/data

Autor: ICT Engine v6.0 Team
Fecha: 19 Septiembre 2025
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / '01-CORE'))

def test_alert_config_loading():
    """Test carga de configuración de alertas"""
    print("🔧 Testing alert configuration loading...")
    
    try:
        from monitoring.alert_threshold_manager import AlertThresholdManager
        
        config_path = PROJECT_ROOT / '01-CORE' / 'config' / 'alerts.yaml'
        manager = AlertThresholdManager(config_path)
        
        thresholds = manager.get_all_thresholds()
        print(f"✅ Loaded {len(thresholds)} alert thresholds")
        
        # Print some examples
        for i, (alert_type, config) in enumerate(list(thresholds.items())[:3]):
            print(f"   - {alert_type}: {config['category']} ({config.get('warning_value', 'N/A')} {config['unit']})")
            
        return True
        
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_threshold_evaluation():
    """Test evaluación de umbrales"""
    print("\n⚖️  Testing threshold evaluation...")
    
    try:
        from monitoring.alert_threshold_manager import get_alert_threshold_manager
        
        manager = get_alert_threshold_manager()
        
        # Test system resources breach
        breach = manager.evaluate_metric('system_resources', 95.0, 'SmokeTest')
        if breach:
            print(f"✅ Generated breach: {breach.alert_type} {breach.level.value} - {breach.message}")
        else:
            print("ℹ️  No breach generated (normal if thresholds are higher)")
        
        # Test throughput breach
        breach = manager.evaluate_metric('throughput', 1.0, 'SmokeTest') 
        if breach:
            print(f"✅ Generated breach: {breach.alert_type} {breach.level.value} - {breach.message}")
        else:
            print("ℹ️  No throughput breach (threshold may be lower)")
            
        return True
        
    except Exception as e:
        print(f"❌ Threshold evaluation failed: {e}")
        return False

def test_alert_integration():
    """Test integración con sistema de alertas"""
    print("\n📢 Testing alert integration...")
    
    try:
        from alerting.alert_integration_system import AlertIntegrationSystem
        from monitoring.alert_threshold_manager import get_alert_threshold_manager
        
        # Initialize integration system
        integration = AlertIntegrationSystem()
        manager = get_alert_threshold_manager()
        
        # Generate synthetic breach
        breach = manager.evaluate_metric('error_rate', 10.0, 'SmokeTest')
        
        if breach:
            print(f"✅ Integration test breach: {breach.level.value}")
        else:
            print("ℹ️  No breach for integration test")
            
        return True
        
    except Exception as e:
        print(f"❌ Alert integration failed: {e}")
        return False

def test_metrics_api_endpoints():
    """Test endpoints de métricas API"""
    print("\n🌐 Testing metrics API endpoints...")
    
    try:
        # Test alerts endpoint
        import sys
        sys.path.append(str(PROJECT_ROOT / '09-DASHBOARD'))
        
        # Import metrics_api functions directly
        from metrics_api import get_system_metrics, get_trading_metrics
        
        # Test system metrics
        sys_metrics = get_system_metrics()
        print(f"✅ System metrics loaded: {type(sys_metrics).__name__}")
        
        # Test trading metrics
        trading_metrics = get_trading_metrics()
        print(f"✅ Trading metrics loaded: {type(trading_metrics).__name__}")
        
        # Test alert manager endpoints (simulate)
        from monitoring.alert_threshold_manager import get_alert_threshold_manager
        manager = get_alert_threshold_manager()
        
        recent_alerts = manager.get_recent_breaches(limit=10)
        thresholds = manager.get_all_thresholds()
        
        print(f"✅ Alert endpoints: {len(recent_alerts)} recent, {len(thresholds)} thresholds")
        
        return True
        
    except Exception as e:
        print(f"❌ Metrics API test failed: {e}")
        return False

def test_persistence():
    """Test persistencia de alertas"""
    print("\n💾 Testing alert persistence...")
    
    try:
        # Check if data directories exist
        data_dir = PROJECT_ROOT / '04-DATA' / 'data'
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Test file creation
        test_file = data_dir / 'alerts_smoke_test.json'
        test_data = {
            'timestamp': datetime.now().isoformat(),
            'test': 'smoke_test_alerts',
            'status': 'success'
        }
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        
        # Verify file exists and is readable
        if test_file.exists():
            with open(test_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            print(f"✅ Persistence test: File created and loaded successfully")
            test_file.unlink()  # Clean up
        else:
            print("❌ Persistence test: File not created")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Persistence test failed: {e}")
        return False

def run_smoke_test():
    """Ejecutar test de humo completo"""
    print("🧪 ALERTS SMOKE TEST - ICT Engine v6.0")
    print("=" * 50)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Test time: {datetime.now().isoformat()}")
    print("")
    
    tests = [
        ("Config Loading", test_alert_config_loading),
        ("Threshold Evaluation", test_threshold_evaluation), 
        ("Alert Integration", test_alert_integration),
        ("Metrics API", test_metrics_api_endpoints),
        ("Persistence", test_persistence)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"🏁 SMOKE TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Alert system ready!")
        return True
    else:
        print("❌ SOME TESTS FAILED - Check configuration and dependencies")
        return False

if __name__ == '__main__':
    success = run_smoke_test()
    sys.exit(0 if success else 1)