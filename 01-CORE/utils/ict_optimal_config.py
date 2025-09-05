#!/usr/bin/env python3
"""
🎯 CONFIGURACIÓN ÓPTIMA ICT - LEYES DE MERCADO
==============================================

Configuración basada en las leyes ICT para funcionamiento óptimo
del sistema de análisis institucional.

Autor: ICT Engine v6.1.0 Enterprise Team
Fecha: Agosto 2025
"""

# ===============================
# CONFIGURACIÓN ÓPTIMA ICT
# ===============================

ICT_OPTIMAL_CONFIG = {
    "timeframes": {
        # TIMEFRAMES ALTOS - ESTRUCTURA MACRO
        "MN1": {
            "min_bars": 24,      # 2 años mínimo
            "optimal_bars": 60,  # 5 años óptimo
            "use_case": "Macro trend, yearly cycles",
            "priority": "HIGH"
        },
        "W1": {
            "min_bars": 104,     # 2 años mínimo  
            "optimal_bars": 260, # 5 años óptimo
            "use_case": "Weekly ranges, institutional positioning",
            "priority": "HIGH"
        },
        "D1": {
            "min_bars": 730,     # 2 años mínimo
            "optimal_bars": 1825, # 5 años óptimo
            "use_case": "Daily bias, market structure",
            "priority": "CRITICAL"
        },
        
        # TIMEFRAMES MEDIOS - ESTRUCTURA INTERMEDIA
        "H4": {
            "min_bars": 2920,    # 6 meses mínimo (4 * 24 * 30 * 6)
            "optimal_bars": 8760, # 2 años óptimo (4 * 24 * 365 * 2)
            "use_case": "Session analysis, order blocks",
            "priority": "CRITICAL"
        },
        "H1": {
            "min_bars": 8760,    # 1 año mínimo (24 * 365)
            "optimal_bars": 17520, # 2 años óptimo (24 * 365 * 2)
            "use_case": "Killzones, liquidity runs", 
            "priority": "CRITICAL"
        },
        
        # TIMEFRAMES BAJOS - EJECUCIÓN
        "M15": {
            "min_bars": 35040,   # 1 año mínimo (4 * 24 * 365)
            "optimal_bars": 70080, # 2 años óptimo (4 * 24 * 365 * 2)
            "use_case": "Entry triggers, FVG precision",
            "priority": "HIGH"
        },
        "M5": {
            "min_bars": 105120,  # 1 año mínimo (12 * 24 * 365)
            "optimal_bars": 210240, # 2 años óptimo (12 * 24 * 365 * 2)
            "use_case": "Precise entries, scalping",
            "priority": "MEDIUM"
        },
        "M1": {
            "min_bars": 525600,  # 1 año mínimo (60 * 24 * 365)
            "optimal_bars": 1051200, # 2 años óptimo (60 * 24 * 365 * 2)
            "use_case": "Ultra-precise entries, debugging",
            "priority": "LOW"
        }
    },
    
    # ANÁLISIS ICT POR TIMEFRAME
    "ict_analysis": {
        "market_structure": ["MN1", "W1", "D1", "H4"],
        "order_blocks": ["D1", "H4", "H1", "M15"],
        "fair_value_gaps": ["H4", "H1", "M15", "M5"],
        "liquidity_pools": ["D1", "H4", "H1"],
        "killzones": ["H1", "M15", "M5"],
        "sessions": ["H4", "H1", "M15"],
        "fibonacci": ["W1", "D1", "H4", "H1"]
    },
    
    # PRIORIDADES DE DESCARGA
    "download_priority": {
        1: ["D1", "H4", "H1"],  # CRÍTICOS PRIMERO
        2: ["W1", "M15"],       # IMPORTANTES SEGUNDO  
        3: ["MN1", "M5"],       # COMPLEMENTARIOS TERCERO
        4: ["M1"]               # OPCIONALES ÚLTIMO
    },
    
    # CONFIGURACIÓN DE MEMORIA Y PERFORMANCE
    "performance": {
        "max_concurrent_downloads": 2,  # No sobrecargar MT5
        "batch_size_by_timeframe": {
            "MN1": 100,    # Pocas velas, batch grande
            "W1": 500,     # Pocas velas, batch grande
            "D1": 1000,    # Balance
            "H4": 2000,    # Balance
            "H1": 5000,    # Muchas velas, batch mediano
            "M15": 10000,  # Muchas velas, batch grande
            "M5": 15000,   # Muchas velas, batch muy grande
            "M1": 20000    # Muchísimas velas, batch máximo
        },
        "memory_limit_mb": 2048,  # 2GB límite para datos
        "cache_enabled": True,
        "lazy_loading": True
    }
}

# ===============================
# LEYES ICT FUNDAMENTALES
# ===============================

ICT_LAWS = {
    "market_structure": {
        "law": "El mercado se mueve en ondas institucionalmente programadas",
        "timeframes": ["MN1", "W1", "D1", "H4"],
        "min_history": "2 años para identificar patrones macro",
        "application": "Identificar HH/HL/LH/LL en múltiples timeframes"
    },
    
    "liquidity_concept": {
        "law": "El precio se mueve para cazar liquidez antes de continuar la tendencia",
        "timeframes": ["D1", "H4", "H1"],
        "min_history": "6 meses para ver patrones de liquidez",
        "application": "Identificar zonas donde se acumula liquidez retail"
    },
    
    "order_blocks": {
        "law": "Los bancos dejan order blocks antes de movimientos institucionales",
        "timeframes": ["D1", "H4", "H1", "M15"],
        "min_history": "3 meses para validar order blocks",
        "application": "Detectar la última vela antes de impulso institucional"
    },
    
    "fair_value_gaps": {
        "law": "Los gaps de precio deben ser rellenados por el mercado",
        "timeframes": ["H4", "H1", "M15", "M5"],
        "min_history": "1 mes para timeframes bajos, 6 meses para altos",
        "application": "Identificar zonas de rebalance de precio"
    },
    
    "session_bias": {
        "law": "Cada sesión (London, NY, Asian) tiene características específicas",
        "timeframes": ["H1", "M15", "M5"],
        "min_history": "6 meses para entender patrones de sesión",
        "application": "Adaptar estrategia según horario de trading"
    },
    
    "killzones": {
        "law": "Hay horarios específicos donde ocurren movimientos institucionales",
        "timeframes": ["H1", "M15", "M5"],
        "min_history": "3 meses para identificar killzones efectivas",
        "application": "Operar solo en horarios de alta probabilidad"
    }
}

# ===============================
# FUNCIONES DE VALIDACIÓN
# ===============================

def validate_ict_compliance(current_data: dict) -> dict:
    """🎯 Valida si los datos actuales cumplen las leyes ICT"""
    
    compliance_report = {
        "overall_status": "CHECKING",
        "critical_missing": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Verificar timeframes críticos
    critical_tf = ["D1", "H4", "H1"]
    for tf in critical_tf:
        if tf not in current_data:
            compliance_report["critical_missing"].append(f"Timeframe {tf} no disponible")
        else:
            min_required = ICT_OPTIMAL_CONFIG["timeframes"][tf]["min_bars"]
            current_bars = len(current_data[tf])
            
            if current_bars < min_required:
                compliance_report["critical_missing"].append(
                    f"{tf}: {current_bars} velas (necesarias: {min_required})"
                )
    
    # Verificar timeframes importantes
    important_tf = ["W1", "M15"]
    for tf in important_tf:
        if tf not in current_data:
            compliance_report["warnings"].append(f"Timeframe {tf} recomendado no disponible")
        else:
            min_required = ICT_OPTIMAL_CONFIG["timeframes"][tf]["min_bars"]
            current_bars = len(current_data[tf])
            
            if current_bars < min_required:
                compliance_report["warnings"].append(
                    f"{tf}: {current_bars} velas (recomendadas: {min_required})"
                )
    
    # Estado general
    if compliance_report["critical_missing"]:
        compliance_report["overall_status"] = "NON_COMPLIANT"
        compliance_report["recommendations"].append(
            "🚨 CRÍTICO: Descargar más historia para timeframes altos"
        )
    elif compliance_report["warnings"]:
        compliance_report["overall_status"] = "PARTIALLY_COMPLIANT"
        compliance_report["recommendations"].append(
            "⚠️ MEJORAR: Ampliar historia para análisis completo"
        )
    else:
        compliance_report["overall_status"] = "FULLY_COMPLIANT"
        compliance_report["recommendations"].append(
            "✅ ÓPTIMO: Datos suficientes para análisis ICT completo"
        )
    
    return compliance_report

def get_optimal_download_plan() -> dict:
    """📋 Genera plan de descarga óptimo según leyes ICT"""
    
    download_plan = {
        "phase_1_critical": {
            "description": "Timeframes críticos para análisis básico",
            "timeframes": ["D1", "H4", "H1"],
            "priority": 1,
            "estimated_time": "10-15 minutos",
            "data_size": "~50MB"
        },
        "phase_2_important": {
            "description": "Timeframes importantes para análisis completo", 
            "timeframes": ["W1", "M15"],
            "priority": 2,
            "estimated_time": "15-20 minutos",
            "data_size": "~200MB"
        },
        "phase_3_complementary": {
            "description": "Timeframes complementarios para análisis avanzado",
            "timeframes": ["MN1", "M5"],
            "priority": 3,
            "estimated_time": "20-30 minutos", 
            "data_size": "~500MB"
        },
        "phase_4_optional": {
            "description": "Timeframes opcionales para trading de alta frecuencia",
            "timeframes": ["M1"],
            "priority": 4,
            "estimated_time": "30-45 minutos",
            "data_size": "~2GB"
        }
    }
    
    return download_plan

if __name__ == "__main__":
    print("🎯 ICT OPTIMAL CONFIG v6.0 Enterprise")
    print("=" * 50)
    
    # Mostrar configuración crítica
    critical_tf = ["D1", "H4", "H1"]
    print("\n🚨 TIMEFRAMES CRÍTICOS (OBLIGATORIOS):")
    for tf in critical_tf:
        config = ICT_OPTIMAL_CONFIG["timeframes"][tf]
        print(f"   {tf}: {config['min_bars']:,} velas mínimo | {config['use_case']}")
    
    # Mostrar plan de descarga
    print("\n📋 PLAN DE DESCARGA ÓPTIMO:")
    plan = get_optimal_download_plan()
    for phase, details in plan.items():
        print(f"   {phase}: {details['timeframes']} ({details['estimated_time']})")
    
    print("\n✅ Configuración lista para implementar")
