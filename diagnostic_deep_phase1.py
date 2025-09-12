#!/usr/bin/env python3
"""
🔍 DIAGNÓSTICO PROFUNDO DEL PIPELINE - MT5 DATA
===============================================

Test exhaustivo para identificar dónde se rompe la cadena de detección de señales.
Fase 1: Verificar que los datos MT5 llegan correctamente.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timezone
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.join(os.path.abspath('.'), '01-CORE'))

def test_mt5_data_pipeline():
    """Test exhaustivo del pipeline de datos MT5"""
    print("\n🔍 DIAGNÓSTICO PROFUNDO - FASE 1: MT5 DATA PIPELINE")
    print("=" * 60)
    
    try:
        # 1. Test básico de conexión
        print("\n1. 📡 TEST CONEXIÓN MT5")
        from data_management.mt5_data_manager import MT5DataManager
        mt5_manager = MT5DataManager()
        
        if not mt5_manager.initialize():
            print("❌ FALLA CRÍTICA: MT5 no se puede inicializar")
            return False
        
        print("✅ MT5 inicializado correctamente")
        
        # 2. Test de obtención de datos
        print("\n2. 📊 TEST OBTENCIÓN DE DATOS")
        live_data = mt5_manager.get_direct_market_data("EURUSD", "M15", 100)
        
        if live_data is None:
            print("❌ FALLA CRÍTICA: get_direct_market_data retorna None")
            return False
        
        if len(live_data) == 0:
            print("❌ FALLA CRÍTICA: get_direct_market_data retorna datos vacíos")
            return False
            
        print(f"✅ Datos obtenidos: {len(live_data)} barras")
        
        # 3. Test estructura de datos
        print("\n3. 🔍 TEST ESTRUCTURA DE DATOS")
        print(f"📋 Tipo de datos: {type(live_data)}")
        
        if isinstance(live_data, pd.DataFrame):
            print(f"📊 DataFrame shape: {live_data.shape}")
            print(f"📊 Columnas: {list(live_data.columns)}")
            
            # Verificar columnas esenciales
            required_cols = ['time', 'open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in live_data.columns]
            
            if missing_cols:
                print(f"❌ PROBLEMA: Columnas faltantes: {missing_cols}")
            else:
                print("✅ Todas las columnas esenciales presentes")
            
            # Verificar datos recientes
            print(f"📅 Última barra: {live_data.iloc[-1]['time']}")
            print(f"💰 Último precio: {live_data.iloc[-1]['close']}")
            
            # Test de timestamps
            last_time = live_data.iloc[-1]['time']
            current_time = datetime.now()
            
            if isinstance(last_time, (pd.Timestamp, datetime)):
                time_diff = (current_time - last_time.to_pydatetime() if hasattr(last_time, 'to_pydatetime') else current_time - last_time).total_seconds()
                print(f"⏰ Diferencia temporal: {time_diff/60:.1f} minutos")
                
                if time_diff < 3600:  # Menos de 1 hora
                    print("✅ Datos son recientes (< 1 hora)")
                else:
                    print("⚠️ WARNING: Datos no son muy recientes (> 1 hora)")
            
            # Test de calidad de datos
            print(f"📊 Precio range: {live_data['low'].min():.5f} - {live_data['high'].max():.5f}")
            print(f"📊 Volumen promedio: {live_data['volume'].mean():.0f}")
            
            # Test de gaps/nulos
            null_counts = live_data.isnull().sum()
            if null_counts.sum() > 0:
                print(f"⚠️ WARNING: Datos nulos encontrados: {null_counts.to_dict()}")
            else:
                print("✅ No hay datos nulos")
            
            return True
        else:
            print(f"❌ PROBLEMA: Datos no son DataFrame, son {type(live_data)}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN FASE 1: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        try:
            if 'mt5_manager' in locals():
                mt5_manager.shutdown()
        except:
            pass

if __name__ == "__main__":
    success = test_mt5_data_pipeline()
    if success:
        print("\n✅ FASE 1 COMPLETADA: MT5 Data Pipeline FUNCIONAL")
        print("🎯 Procediendo a Fase 2: Pattern Detection")
    else:
        print("\n❌ FASE 1 FALLIDA: Problema en MT5 Data Pipeline")
        print("🛑 No se puede proceder sin datos válidos")
    
    sys.exit(0 if success else 1)