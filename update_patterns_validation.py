#!/usr/bin/env python3
"""
🔧 SCRIPT DE ACTUALIZACIÓN MASIVA - VALIDACIÓN EN PATRONES
=========================================================

Script para aplicar automáticamente la validación de datos crítica
a todos los módulos de patrones individuales.

FUNCIÓN: Actualizar todos los dashboards para usar validación estricta
"""

import os
import re
from pathlib import Path

def update_pattern_dashboard(file_path):
    """
    Actualizar un dashboard de patrón individual para usar validación
    
    Args:
        file_path: Ruta al archivo del dashboard
    """
    print(f"📝 Actualizando: {file_path.name}")
    
    # Leer contenido del archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Actualizar obtención de datos de mercado
    old_market_pattern = r'(\s+)# 1\. Obtener datos reales del mercado\s+market_data = self\._get_real_market_data\(symbol, timeframe\)\s+if not market_data:\s+result\.narrative = "Datos de mercado no disponibles en el sistema real"\s+return result'
    
    new_market_replacement = r'''\1# 1. Obtener datos reales del mercado
\1raw_market_data = self._get_real_market_data(symbol, timeframe)
\1if not raw_market_data:
\1    result.narrative = "Datos de mercado no disponibles en el sistema real"
\1    return result
\1
\1# 🔒 VALIDAR DATOS DE MERCADO ANTES DE USAR
\1market_data = self.validate_market_data(raw_market_data)
\1if not market_data or len(market_data) == 0:
\1    result.narrative = "Datos de mercado inválidos - falló validación de seguridad"
\1    return result'''
    
    content = re.sub(old_market_pattern, new_market_replacement, content, flags=re.MULTILINE)
    
    # 2. Actualizar procesamiento de señales
    old_signal_pattern = r'(\s+)# Extraer datos REALES de la señal\s+result\.confidence = float\(best_signal\.get\(\'confidence\', 0\.0\)\)\s+result\.strength = float\(best_signal\.get\(\'strength\', 0\.0\)\)\s+result\.direction = str\(best_signal\.get\(\'direction\', \'NEUTRAL\'\)\)\.upper\(\)'
    
    new_signal_replacement = r'''\1# 🔒 VALIDAR RESULTADO DEL PATRÓN ANTES DE USAR
\1validated_signal = self.validate_pattern_result(best_signal)
\1
\1# Extraer datos VALIDADOS de la señal
\1result.confidence = float(validated_signal.get('confidence', 0.0))
\1result.strength = float(validated_signal.get('strength', 0.0))
\1result.direction = str(validated_signal.get('direction', 'NEUTRAL')).upper()'''
    
    content = re.sub(old_signal_pattern, new_signal_replacement, content, flags=re.MULTILINE)
    
    # 3. Actualizar referencias a best_signal por validated_signal
    content = content.replace('best_signal.get(', 'validated_signal.get(')
    content = content.replace('# Niveles reales (NO hardcodeados)', '# Niveles validados (NO hardcodeados)')
    content = content.replace('# Métricas reales', '# Métricas validadas')
    content = content.replace('# Contexto real', '# Contexto validado')
    content = content.replace('# Guardar datos brutos para debugging', '# Guardar datos validados para debugging')
    content = content.replace('result.raw_data = best_signal', 'result.raw_data = validated_signal')
    
    # Escribir archivo actualizado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Actualizado: {file_path.name}")

def main():
    """Función principal del script"""
    print("🚀 INICIANDO ACTUALIZACIÓN MASIVA DE VALIDACIÓN EN PATRONES")
    print("=" * 60)
    
    # Directorio de patrones individuales
    patterns_dir = Path("C:/Users/v_jac/Desktop/ict-engine-v6.0-enterprise-sic/09-DASHBOARD/patterns_analysis/individual_patterns")
    
    # Archivos de patrones a actualizar (excluyendo los ya actualizados)
    pattern_files = [
        "choch_single_tf_dashboard.py",
        "fair_value_gaps_dashboard.py",
        "institutional_flow_dashboard.py",
        "judas_swing_dashboard.py",
        "liquidity_grab_dashboard.py",
        "optimal_trade_entry_dashboard.py",
        "order_blocks_dashboard.py",
        "recent_structure_break_dashboard.py",
        "swing_points_for_bos_dashboard.py"
    ]
    
    updated_count = 0
    
    for file_name in pattern_files:
        file_path = patterns_dir / file_name
        if file_path.exists():
            try:
                update_pattern_dashboard(file_path)
                updated_count += 1
            except Exception as e:
                print(f"❌ Error actualizando {file_name}: {e}")
        else:
            print(f"⚠️ Archivo no encontrado: {file_name}")
    
    print("\n" + "=" * 60)
    print(f"✅ ACTUALIZACIÓN COMPLETADA: {updated_count} archivos procesados")
    print("🔒 Todos los patrones ahora usan validación estricta de datos")

if __name__ == "__main__":
    main()
