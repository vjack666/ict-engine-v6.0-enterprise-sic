#!/usr/bin/env python3
"""
📊 GESTOR DE SÍMBOLOS ICT - MULTI-SYMBOL MANAGER
==============================================

Gestor centralizado para el manejo de múltiples símbolos de trading.
Proporciona configuración, priorización y análisis de correlaciones.

Características:
- Carga dinámica desde configuración JSON
- Priorización automática de símbolos
- Gestión de correlaciones
- Optimización por sesiones
- Compatible con ICT patterns

Autor: ICT Engine v6.0 Enterprise Team
Versión: 1.0.0
Fecha: 2025-09-02
"""

from protocols.unified_logging import get_unified_logger
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class SymbolPriority(Enum):
    """Prioridades de símbolos para análisis"""
    CRITICAL = 1
    IMPORTANT = 2
    EXTENDED = 3
    EXOTIC = 4


class TradingSession(Enum):
    """Sesiones de trading"""
    ASIAN = "Asian"
    LONDON = "London"
    NEW_YORK = "New_York"
    OVERLAP = "Overlap"


@dataclass
class SymbolConfig:
    """Configuración de un símbolo específico"""
    symbol: str
    pip_value: float
    spread_typical: float
    volatility: str
    best_sessions: List[str]
    ict_priority: int
    priority_level: SymbolPriority


class ICTSymbolManager:
    """
    📊 GESTOR DE SÍMBOLOS ICT ENTERPRISE
    
    Maneja configuración y análisis de múltiples símbolos para trading ICT:
    - Carga configuración desde JSON
    - Prioriza símbolos por importancia
    - Gestiona correlaciones
    - Optimiza por sesiones de trading
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Inicializar Symbol Manager
        
        Args:
            config_path: Ruta al archivo de configuración (opcional)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = {}
        self.symbol_configs = {}
        self.priority_groups = {}
        
        # Cargar configuración
        self._load_configuration()
        self._build_symbol_configs()
        self._organize_by_priority()
        
        print(f"✅ ICT Symbol Manager inicializado")
        print(f"   📊 Símbolos configurados: {len(self.symbol_configs)}")
        print(f"   🎯 Grupos de prioridad: {len(self.priority_groups)}")
    
    def _get_default_config_path(self) -> Path:
        """Obtener ruta por defecto del archivo de configuración"""
        current_dir = Path(__file__).parent
        return current_dir.parent / "config" / "trading_symbols_config.json"
    
    def _load_configuration(self):
        """Cargar configuración desde archivo JSON"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ Configuración cargada desde: {self.config_path}")
            else:
                print(f"⚠️ Archivo de configuración no encontrado: {self.config_path}")
                self._create_default_config()
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Crear configuración por defecto"""
        self.config = {
            "trading_symbols": {
                "critical_symbols": {
                    "symbols": ["EURUSD", "GBPUSD"],
                    "priority": 1
                },
                "important_symbols": {
                    "symbols": ["USDJPY", "XAUUSD"],
                    "priority": 2
                }
            },
            "symbol_configurations": {
                "EURUSD": {
                    "pip_value": 0.0001,
                    "spread_typical": 0.8,
                    "volatility": "medium",
                    "best_sessions": ["London", "New_York"],
                    "ict_priority": 1
                }
            }
        }
        print("📝 Configuración por defecto creada")
    
    def _build_symbol_configs(self):
        """Construir configuraciones de símbolos"""
        symbol_data = self.config.get("symbol_configurations", {})
        trading_symbols = self.config.get("trading_symbols", {})
        
        # Mapear símbolos a grupos de prioridad
        symbol_to_priority = {}
        for group_name, group_data in trading_symbols.items():
            priority_level = self._get_priority_from_group(group_name)
            for symbol in group_data.get("symbols", []):
                symbol_to_priority[symbol] = priority_level
        
        # Crear configuraciones
        for symbol, config_data in symbol_data.items():
            priority = symbol_to_priority.get(symbol, SymbolPriority.EXTENDED)
            
            self.symbol_configs[symbol] = SymbolConfig(
                symbol=symbol,
                pip_value=config_data.get("pip_value", 0.0001),
                spread_typical=config_data.get("spread_typical", 1.0),
                volatility=config_data.get("volatility", "medium"),
                best_sessions=config_data.get("best_sessions", ["London"]),
                ict_priority=config_data.get("ict_priority", 5),
                priority_level=priority
            )
    
    def _get_priority_from_group(self, group_name: str) -> SymbolPriority:
        """Convertir nombre de grupo a prioridad"""
        if "critical" in group_name.lower():
            return SymbolPriority.CRITICAL
        elif "important" in group_name.lower():
            return SymbolPriority.IMPORTANT
        elif "extended" in group_name.lower():
            return SymbolPriority.EXTENDED
        else:
            return SymbolPriority.EXOTIC
    
    def _organize_by_priority(self):
        """Organizar símbolos por grupos de prioridad"""
        for priority in SymbolPriority:
            self.priority_groups[priority] = []
        
        for symbol, config in self.symbol_configs.items():
            self.priority_groups[config.priority_level].append(symbol)
        
        # Ordenar cada grupo por ict_priority
        for priority in SymbolPriority:
            self.priority_groups[priority].sort(
                key=lambda s: self.symbol_configs[s].ict_priority
            )
    
    def get_symbols_by_priority(self, priority: SymbolPriority) -> List[str]:
        """
        Obtener símbolos por nivel de prioridad
        
        Args:
            priority: Nivel de prioridad deseado
            
        Returns:
            Lista de símbolos ordenados por importancia
        """
        return self.priority_groups.get(priority, [])
    
    def get_critical_symbols(self) -> List[str]:
        """Obtener símbolos críticos para análisis inmediato"""
        return self.get_symbols_by_priority(SymbolPriority.CRITICAL)
    
    def get_important_symbols(self) -> List[str]:
        """Obtener símbolos importantes"""
        return self.get_symbols_by_priority(SymbolPriority.IMPORTANT)
    
    def get_all_trading_symbols(self) -> List[str]:
        """Obtener todos los símbolos configurados ordenados por prioridad"""
        all_symbols = []
        for priority in [SymbolPriority.CRITICAL, SymbolPriority.IMPORTANT, 
                        SymbolPriority.EXTENDED, SymbolPriority.EXOTIC]:
            all_symbols.extend(self.get_symbols_by_priority(priority))
        return all_symbols
    
    def get_symbols_for_session(self, session: TradingSession) -> List[str]:
        """
        Obtener símbolos optimizados para una sesión específica
        
        Args:
            session: Sesión de trading
            
        Returns:
            Lista de símbolos recomendados para la sesión
        """
        session_symbols = []
        session_name = session.value
        
        for symbol, config in self.symbol_configs.items():
            if session_name in config.best_sessions:
                session_symbols.append(symbol)
        
        # Ordenar por prioridad ICT
        session_symbols.sort(key=lambda s: self.symbol_configs[s].ict_priority)
        
        return session_symbols
    
    def get_symbol_config(self, symbol: str) -> Optional[SymbolConfig]:
        """
        Obtener configuración de un símbolo específico
        
        Args:
            symbol: Símbolo a consultar
            
        Returns:
            Configuración del símbolo o None si no existe
        """
        return self.symbol_configs.get(symbol)
    
    def get_analysis_batch(self, max_symbols: int = 6) -> List[str]:
        """
        Obtener lote optimizado de símbolos para análisis
        
        Args:
            max_symbols: Número máximo de símbolos a retornar
            
        Returns:
            Lista optimizada de símbolos para análisis
        """
        # Priorizar críticos e importantes
        batch = []
        batch.extend(self.get_critical_symbols())
        
        remaining = max_symbols - len(batch)
        if remaining > 0:
            important = self.get_important_symbols()
            batch.extend(important[:remaining])
        
        remaining = max_symbols - len(batch)
        if remaining > 0:
            extended = self.get_symbols_by_priority(SymbolPriority.EXTENDED)
            batch.extend(extended[:remaining])
        
        return batch[:max_symbols]
    
    def calculate_correlation_risk(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Calcular riesgo de correlación entre símbolos
        
        Args:
            symbols: Lista de símbolos a analizar
            
        Returns:
            Diccionario con análisis de correlación
        """
        # Análisis básico de correlación basado en pares base
        correlations = {}
        
        # Definir correlaciones conocidas (simplificado)
        correlation_map = {
            ("EURUSD", "GBPUSD"): 0.7,
            ("EURUSD", "USDCHF"): -0.8,
            ("GBPUSD", "USDCHF"): -0.6,
            ("AUDUSD", "NZDUSD"): 0.8,
            ("USDJPY", "USDCHF"): 0.6
        }
        
        high_correlations = []
        for i, symbol1 in enumerate(symbols):
            for symbol2 in symbols[i+1:]:
                pair = (symbol1, symbol2) if symbol1 < symbol2 else (symbol2, symbol1)
                correlation = correlation_map.get(pair, 0.0)
                
                if abs(correlation) > 0.7:
                    high_correlations.append({
                        'pair': pair,
                        'correlation': correlation,
                        'risk_level': 'HIGH' if abs(correlation) > 0.8 else 'MEDIUM'
                    })
        
        return {
            'symbols_analyzed': symbols,
            'high_correlations': high_correlations,
            'correlation_risk': 'HIGH' if len(high_correlations) > 2 else 'LOW',
            'recommended_max_positions': max(1, 6 - len(high_correlations))
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema de símbolos"""
        return {
            'total_symbols': len(self.symbol_configs),
            'critical_symbols': len(self.get_critical_symbols()),
            'important_symbols': len(self.get_important_symbols()),
            'extended_symbols': len(self.get_symbols_by_priority(SymbolPriority.EXTENDED)),
            'exotic_symbols': len(self.get_symbols_by_priority(SymbolPriority.EXOTIC)),
            'config_loaded': bool(self.config),
            'config_path': str(self.config_path)
        }


# Factory functions para fácil uso
def get_ict_symbol_manager() -> ICTSymbolManager:
    """Factory function para crear Symbol Manager"""
    return ICTSymbolManager()


def get_critical_trading_symbols() -> List[str]:
    """Función rápida para obtener símbolos críticos"""
    manager = get_ict_symbol_manager()
    return manager.get_critical_symbols()


def get_important_trading_symbols() -> List[str]:
    """Función rápida para obtener símbolos importantes"""
    manager = get_ict_symbol_manager()
    return manager.get_important_symbols()


def get_all_ict_symbols() -> List[str]:
    """Función rápida para obtener todos los símbolos ICT"""
    manager = get_ict_symbol_manager()
    return manager.get_all_trading_symbols()


def get_analysis_ready_symbols(max_count: int = 6) -> List[str]:
    """Función rápida para obtener símbolos listos para análisis"""
    manager = get_ict_symbol_manager()
    return manager.get_analysis_batch(max_count)


if __name__ == "__main__":
    # Test del Symbol Manager
    print("🎯 ICT Symbol Manager v6.0 Enterprise - Test")
    print("=" * 50)
    
    manager = get_ict_symbol_manager()
    
    print(f"\n📊 Símbolos críticos: {manager.get_critical_symbols()}")
    print(f"📈 Símbolos importantes: {manager.get_important_symbols()}")
    print(f"🌐 Todos los símbolos: {manager.get_all_trading_symbols()}")
    
    print(f"\n🏙️ Símbolos para sesión London: {manager.get_symbols_for_session(TradingSession.LONDON)}")
    print(f"🇺🇸 Símbolos para sesión New York: {manager.get_symbols_for_session(TradingSession.NEW_YORK)}")
    
    batch = manager.get_analysis_batch(4)
    print(f"\n🎯 Lote de análisis (4 símbolos): {batch}")
    
    correlation_analysis = manager.calculate_correlation_risk(batch)
    print(f"\n🔗 Análisis de correlación:")
    print(f"   Riesgo general: {correlation_analysis['correlation_risk']}")
    print(f"   Posiciones máximas recomendadas: {correlation_analysis['recommended_max_positions']}")
    
    status = manager.get_system_status()
    print(f"\n📊 Estado del sistema:")
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print(f"\n✅ Test completado exitosamente!")
