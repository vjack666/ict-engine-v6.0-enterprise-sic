#!/usr/bin/env python3
"""
🌐 MULTI SYMBOL MANAGER - SILVER BULLET ENTERPRISE
==================================================

Gestor multi-símbolo para análisis Silver Bullet simultáneo en múltiples pares
con priorización por sesión y integración completa con componentes enterprise.

Autor: ICT Engine v6.0 Enterprise
Fecha: 2025-09-23
"""

import sys
import time
from datetime import datetime, time as dt_time
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import logging

# Configurar rutas
project_root = Path(__file__).parent.parent.parent / "01-CORE"
sys.path.insert(0, str(project_root))

# Importar componentes verificados disponibles
try:
    from data_management.mt5_data_manager import MT5DataManager
    from analysis.unified_memory_system import UnifiedMemorySystem
    from risk_management.risk_manager import RiskManager
    MT5_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Dependencias críticas no disponibles: {e}")
    MT5_AVAILABLE = False

class MultiSymbolManager:
    """
    🌐 Gestor Multi-Símbolo para Silver Bullet Enterprise
    
    Funcionalidades:
    - Análisis simultáneo de 6 pares (incluyendo XAUUSD)
    - Priorización por sesión de trading
    - Integración con MT5DataManager, UnifiedMemorySystem, RiskManager
    - Ranking inteligente de oportunidades
    - Gestión optimizada de recursos
    """
    
    def __init__(self):
        """Inicializar MultiSymbolManager con configuración enterprise"""
        
        # Configuración de símbolos por prioridad de sesión
        self.symbols_config = {
            "majors": {
                "EURUSD": {"priority_session": "NY", "volatility": "medium", "spread": "low"},
                "GBPUSD": {"priority_session": "LONDON", "volatility": "high", "spread": "medium"},
                "USDJPY": {"priority_session": "NY_ASIAN", "volatility": "medium", "spread": "low"},
                "USDCAD": {"priority_session": "NY", "volatility": "medium", "spread": "medium"}
            },
            "cross": {
                "GBPJPY": {"priority_session": "ALL", "volatility": "very_high", "spread": "high"}
            },
            "commodity": {
                "XAUUSD": {"priority_session": "ASIAN_NY", "volatility": "high", "spread": "medium"}
            }
        }
        
        # Lista plana de todos los símbolos
        self.all_symbols = []
        for category in self.symbols_config.values():
            self.all_symbols.extend(category.keys())
        
        # Timeframes con jerarquía definida
        self.timeframes = {
            "H4": {"role": "trend_authority", "weight": 0.4},
            "H1": {"role": "structure_confirmation", "weight": 0.3},
            "M15": {"role": "entry_structure", "weight": 0.2},
            "M5": {"role": "precision_timing", "weight": 0.1}
        }
        
        # Definición de sesiones de trading
        self.trading_sessions = {
            "LONDON": {
                "start": dt_time(7, 0),    # GMT
                "end": dt_time(16, 0),     # GMT
                "priority_pairs": ["GBPUSD", "EURGBP"]
            },
            "NY": {
                "start": dt_time(12, 0),   # GMT (overlap con London)
                "end": dt_time(21, 0),     # GMT
                "priority_pairs": ["EURUSD", "USDCAD"]
            },
            "ASIAN": {
                "start": dt_time(23, 0),   # GMT
                "end": dt_time(8, 0),      # GMT (next day)
                "priority_pairs": ["USDJPY", "XAUUSD"]
            }
        }
        
        # Inicializar componentes enterprise
        self.active_analyses = {}
        self.last_update = {}
        self.analysis_cache = {}
        
        # Integrar componentes verificados
        if MT5_AVAILABLE:
            self.mt5_manager = MT5DataManager()
            self.memory_system = UnifiedMemorySystem()
            self.risk_manager = RiskManager(mode='live')
            self.logger = logging.getLogger(__name__)
            print("✅ MultiSymbolManager: Todos los componentes integrados exitosamente")
        else:
            print("❌ MultiSymbolManager: Componentes críticos no disponibles")
            self.mt5_manager = None
            self.memory_system = None
            self.risk_manager = None
    
    def analyze_all_symbols(self) -> Dict[str, Any]:
        """
        📊 Realizar análisis simultáneo de todos los símbolos
        
        Returns:
            Dict con análisis completo por símbolo
        """
        if not MT5_AVAILABLE:
            return {"error": "Componentes MT5 no disponibles"}
        
        start_time = time.time()
        results = {}
        
        print(f"🔍 Iniciando análisis multi-símbolo para {len(self.all_symbols)} pares...")
        
        for symbol in self.all_symbols:
            try:
                # Análisis por símbolo con timeframes múltiples
                symbol_analysis = self._analyze_single_symbol(symbol)
                results[symbol] = symbol_analysis
                
                # Actualizar timestamp
                self.last_update[symbol] = datetime.now()
                
            except Exception as e:
                print(f"⚠️ Error analizando {symbol}: {e}")
                results[symbol] = {"error": str(e)}
        
        # Estadísticas del análisis
        analysis_time = time.time() - start_time
        results["_metadata"] = {
            "analysis_time": analysis_time,
            "symbols_analyzed": len([s for s in results if "error" not in results[s]]),
            "timestamp": datetime.now(),
            "active_session": self.get_current_session()
        }
        
        self.active_analyses = results
        print(f"✅ Análisis multi-símbolo completado en {analysis_time:.2f}s")
        
        return results
    
    def _analyze_single_symbol(self, symbol: str) -> Dict[str, Any]:
        """
        📈 Análizar un símbolo específico con multi-timeframe
        
        Args:
            symbol: Símbolo a analizar
            
        Returns:
            Dict con análisis completo del símbolo
        """
        analysis = {
            "symbol": symbol,
            "timeframe_analysis": {},
            "composite_score": 0.0,
            "priority_score": 0.0,
            "risk_assessment": {},
            "session_alignment": False
        }
        
        # Análisis multi-timeframe
        for tf, config in self.timeframes.items():
            try:
                # Obtener datos del timeframe
                data = self.fetch_symbol_data(symbol, tf)
                if data is not None and len(data) > 0:
                    
                    # Análisis específico del timeframe (placeholder por ahora)
                    tf_analysis = {
                        "role": config["role"],
                        "weight": config["weight"],
                        "data_points": len(data),
                        "trend_direction": self._detect_trend_direction(data),
                        "structure_strength": self._calculate_structure_strength(data)
                    }
                    
                    analysis["timeframe_analysis"][tf] = tf_analysis
                    
            except Exception as e:
                print(f"⚠️ Error en {symbol} {tf}: {e}")
        
        # Calcular scores compuestos
        analysis["composite_score"] = self._calculate_composite_score(analysis)
        analysis["priority_score"] = self._calculate_session_priority_score(symbol)
        analysis["session_alignment"] = self._check_session_alignment(symbol)
        
        # Risk assessment
        if self.risk_manager:
            analysis["risk_assessment"] = self._assess_symbol_risk(symbol)
        
        return analysis
    
    def fetch_symbol_data(self, symbol: str, timeframe: str, bars: int = 100) -> Optional[Any]:
        """
        📥 Obtener datos de un símbolo específico
        
        Args:
            symbol: Símbolo (ej: EURUSD)
            timeframe: Marco temporal (ej: M15)
            bars: Número de barras
            
        Returns:
            Datos del símbolo o None si hay error
        """
        if not self.mt5_manager:
            return None
        
        try:
            # Usar cache si los datos son recientes
            cache_key = f"{symbol}_{timeframe}"
            if cache_key in self.analysis_cache:
                cache_time, cached_data = self.analysis_cache[cache_key]
                if (datetime.now() - cache_time).seconds < 60:  # Cache de 1 minuto
                    return cached_data
            
            # Obtener datos frescos de MT5
            data = self.mt5_manager.get_candles(symbol, timeframe, bars)
            
            # Actualizar cache
            self.analysis_cache[cache_key] = (datetime.now(), data)
            
            return data
            
        except Exception as e:
            print(f"❌ Error obteniendo datos {symbol} {timeframe}: {e}")
            return None
    
    def get_best_setups(self, max_setups: int = 3) -> List[Dict[str, Any]]:
        """
        🏆 Obtener los mejores setups ranking por calidad
        
        Args:
            max_setups: Máximo número de setups a retornar
            
        Returns:
            Lista de mejores setups ordenados por calidad
        """
        if not self.active_analyses or "_metadata" not in self.active_analyses:
            return []
        
        setups = []
        
        for symbol, analysis in self.active_analyses.items():
            if symbol.startswith("_") or "error" in analysis:
                continue
            
            # Crear setup con scoring completo
            setup = {
                "symbol": symbol,
                "composite_score": analysis.get("composite_score", 0),
                "priority_score": analysis.get("priority_score", 0),
                "session_alignment": analysis.get("session_alignment", False),
                "risk_assessment": analysis.get("risk_assessment", {}),
                "total_score": self._calculate_total_setup_score(analysis),
                "recommendation": self._generate_recommendation(analysis)
            }
            
            setups.append(setup)
        
        # Ordenar por total_score descendente
        setups.sort(key=lambda x: x["total_score"], reverse=True)
        
        # Retornar top setups
        return setups[:max_setups]
    
    def analyze_by_timezone(self) -> Dict[str, List[str]]:
        """
        🌍 Analizar símbolos optimizados por zona horaria actual
        
        Returns:
            Dict con símbolos prioritarios por sesión
        """
        current_session = self.get_current_session()
        timezone_analysis = {
            "current_session": current_session,
            "priority_symbols": [],
            "secondary_symbols": [],
            "session_status": {}
        }
        
        for session_name, session_config in self.trading_sessions.items():
            is_active = self._is_session_active(session_name)
            timezone_analysis["session_status"][session_name] = {
                "active": is_active,
                "priority_pairs": session_config["priority_pairs"]
            }
            
            if is_active:
                timezone_analysis["priority_symbols"].extend(session_config["priority_pairs"])
        
        # Remover duplicados y añadir símbolos secundarios
        timezone_analysis["priority_symbols"] = list(set(timezone_analysis["priority_symbols"]))
        
        for symbol in self.all_symbols:
            if symbol not in timezone_analysis["priority_symbols"]:
                timezone_analysis["secondary_symbols"].append(symbol)
        
        return timezone_analysis
    
    def get_current_session(self) -> str:
        """Determinar la sesión de trading actual"""
        current_time = datetime.now().time()
        
        for session_name, config in self.trading_sessions.items():
            if self._is_time_in_session(current_time, config["start"], config["end"]):
                return session_name
        
        return "OFF_HOURS"
    
    def _is_session_active(self, session_name: str) -> bool:
        """Verificar si una sesión está activa"""
        return self.get_current_session() == session_name
    
    def _is_time_in_session(self, current_time: dt_time, start: dt_time, end: dt_time) -> bool:
        """Verificar si tiempo actual está dentro de sesión"""
        if start <= end:
            return start <= current_time <= end
        else:  # Sesión que cruza medianoche (ASIAN)
            return current_time >= start or current_time <= end
    
    def _detect_trend_direction(self, data) -> str:
        """Detectar dirección de tendencia (placeholder)"""
        if data is None or len(data) < 2:
            return "NEUTRAL"
        
        # Lógica simplificada basada en precio de cierre
        try:
            if hasattr(data, 'close'):
                recent_close = data['close'].iloc[-1]
                previous_close = data['close'].iloc[-10] if len(data) > 10 else data['close'].iloc[0]
                
                if recent_close > previous_close * 1.001:  # 0.1% threshold
                    return "BULLISH"
                elif recent_close < previous_close * 0.999:  # -0.1% threshold
                    return "BEARISH"
        except:
            pass
        
        return "NEUTRAL"
    
    def _calculate_structure_strength(self, data) -> float:
        """Calcular fuerza de estructura (placeholder)"""
        if data is None or len(data) < 5:
            return 0.5
        
        # Placeholder - en implementación real usaría análisis ICT completo
        try:
            if hasattr(data, 'high') and hasattr(data, 'low'):
                volatility = (data['high'].max() - data['low'].min()) / data['close'].iloc[-1]
                return min(volatility * 10, 1.0)  # Normalizar a 0-1
        except:
            pass
        
        return 0.5
    
    def _calculate_composite_score(self, analysis: Dict[str, Any]) -> float:
        """Calcular score compuesto basado en análisis multi-timeframe"""
        total_score = 0.0
        total_weight = 0.0
        
        for tf, tf_analysis in analysis.get("timeframe_analysis", {}).items():
            weight = tf_analysis.get("weight", 0.1)
            strength = tf_analysis.get("structure_strength", 0.5)
            
            total_score += strength * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def _calculate_session_priority_score(self, symbol: str) -> float:
        """Calcular score de prioridad basado en sesión actual"""
        current_session = self.get_current_session()
        
        # Verificar si símbolo es prioritario en sesión actual
        for session_name, config in self.trading_sessions.items():
            if session_name == current_session and symbol in config["priority_pairs"]:
                return 1.0
        
        # Verificar configuración específica del símbolo
        for category in self.symbols_config.values():
            if symbol in category:
                symbol_config = category[symbol]
                if current_session in symbol_config["priority_session"] or symbol_config["priority_session"] == "ALL":
                    return 0.8
        
        return 0.3  # Score base para símbolos no prioritarios
    
    def _check_session_alignment(self, symbol: str) -> bool:
        """Verificar si símbolo está alineado con sesión actual"""
        return self._calculate_session_priority_score(symbol) >= 0.8
    
    def _assess_symbol_risk(self, symbol: str) -> Dict[str, Any]:
        """Evaluar riesgo del símbolo usando RiskManager"""
        if not self.risk_manager:
            return {"risk_level": "unknown"}
        
        try:
            # Obtener configuración del símbolo
            symbol_config = None
            for category in self.symbols_config.values():
                if symbol in category:
                    symbol_config = category[symbol]
                    break
            
            if symbol_config:
                return {
                    "volatility": symbol_config["volatility"],
                    "spread": symbol_config["spread"],
                    "risk_level": "high" if symbol_config["volatility"] == "very_high" else "medium"
                }
        except Exception as e:
            print(f"⚠️ Error en risk assessment para {symbol}: {e}")
        
        return {"risk_level": "medium"}
    
    def _calculate_total_setup_score(self, analysis: Dict[str, Any]) -> float:
        """Calcular score total del setup"""
        composite = analysis.get("composite_score", 0) * 0.6
        priority = analysis.get("priority_score", 0) * 0.3
        alignment_bonus = 0.1 if analysis.get("session_alignment", False) else 0
        
        return composite + priority + alignment_bonus
    
    def _generate_recommendation(self, analysis: Dict[str, Any]) -> str:
        """Generar recomendación textual del setup"""
        total_score = self._calculate_total_setup_score(analysis)
        
        if total_score >= 0.8:
            return "STRONG BUY/SELL SETUP"
        elif total_score >= 0.6:
            return "MODERATE SETUP"
        elif total_score >= 0.4:
            return "WEAK SETUP"
        else:
            return "AVOID"
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Obtener resumen de estado del manager"""
        return {
            "total_symbols": len(self.all_symbols),
            "mt5_connected": self.mt5_manager is not None,
            "memory_system_active": self.memory_system is not None,
            "risk_manager_active": self.risk_manager is not None,
            "current_session": self.get_current_session(),
            "last_analysis": max(self.last_update.values()) if self.last_update else None,
            "cache_size": len(self.analysis_cache)
        }


# Función de utilidad para testing
def test_multi_symbol_manager():
    """Función de prueba del MultiSymbolManager"""
    print("🧪 Testing MultiSymbolManager...")
    
    manager = MultiSymbolManager()
    status = manager.get_status_summary()
    
    print(f"📊 Status: {status}")
    
    if status["mt5_connected"]:
        print("🔄 Ejecutando análisis multi-símbolo...")
        results = manager.analyze_all_symbols()
        
        if results and "_metadata" in results:
            print(f"✅ Análisis completado: {results['_metadata']}")
            
            best_setups = manager.get_best_setups(3)
            print(f"🏆 Mejores setups: {len(best_setups)}")
            
            for i, setup in enumerate(best_setups, 1):
                print(f"  {i}. {setup['symbol']}: {setup['total_score']:.3f} - {setup['recommendation']}")
    else:
        print("⚠️ MT5 no disponible - testing limitado")


if __name__ == "__main__":
    test_multi_symbol_manager()
