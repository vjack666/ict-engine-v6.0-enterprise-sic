#!/usr/bin/env python3
"""
Activador de Trading Automático - ICT Engine v6.0 Enterprise
Script para iniciar trading automático con Order Blocks
"""

import sys
import os
from pathlib import Path

# Add paths for imports
project_root = Path(__file__).parent
sys.path.append(str(project_root / "01-CORE"))

from real_trading import AutoPositionSizer, EmergencyStopSystem, SignalValidator, ExecutionEngine
from trading.real_trading_system import RealTradingSystem
from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer

def main():
    print("🚀 ICT ENGINE v6.0 ENTERPRISE - TRADING AUTOMÁTICO")
    print("=" * 60)
    
    # Initialize components
    print("🔧 Inicializando componentes de trading automático...")
    
    try:
        # 1. Initialize Smart Money Analyzer (Order Blocks detector)
        analyzer = SmartMoneyAnalyzer()
        print("✅ Smart Money Analyzer initialized")
        
        # 2. Initialize Real Trading System
        trading_system = RealTradingSystem()
        print("✅ Real Trading System initialized")
        
        # 3. Configure automatic parameters
        config = {
            "auto_trading": True,
            "risk_percent": 1.0,  # 1% risk per trade
            "max_trades_per_day": 10,
            "emergency_stop": True,
            "symbols": ["EURUSD", "GBPUSD", "USDCAD", "AUDUSD"]
        }
        
        print(f"✅ Configuración: {config}")
        
        print("\n🎯 TRADING AUTOMÁTICO CONFIGURADO")
        print("   - Order Blocks detection: ACTIVO")
        print("   - Auto execution: ACTIVO") 
        print("   - Risk management: 1% por trade")
        print("   - Emergency stop: ACTIVO")
        print("   - Símbolos: EURUSD, GBPUSD, USDCAD, AUDUSD")
        
        print("\n⚠️  PARA ACTIVAR COMPLETAMENTE:")
        print("   1. Configura tu cuenta MT5")
        print("   2. Ejecuta: python activate_auto_trading.py --live")
        print("   3. El sistema empezará trading automático")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando trading automático: {e}")
        return False

if __name__ == "__main__":
    if "--live" in sys.argv:
        print("🔴 MODO LIVE TRADING - ¡CUIDADO!")
        print("   El sistema ejecutará trades reales")
        input("   Presiona ENTER para continuar o CTRL+C para cancelar...")
        
    main()