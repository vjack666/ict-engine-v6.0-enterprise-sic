#!/usr/bin/env python3
"""
🎼 PATTERNS ORCHESTRATOR
=======================

Orchestrator principal para gestionar todos los módulos de patrones.
Coordina descubrimiento, carga, updates y consolidación de análisis.

Autor: ICT Engine v6.0 Enterprise Team
Fecha: Septiembre 6, 2025
Versión: v1.0.0-modular
"""

import sys
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

# Configurar rutas
dashboard_root = Path(__file__).parent.parent
project_root = dashboard_root.parent
sys.path.insert(0, str(project_root / "01-CORE"))
sys.path.insert(0, str(dashboard_root))
sys.path.insert(0, str(project_root))  # Para acceder a run_real_market_system

from patterns_analysis.pattern_factory import PatternFactory
from patterns_analysis.base_pattern_module import BasePatternDashboard, PatternAnalysisResult

# Importar sistema de datos reales
try:
    from run_real_market_system import get_real_market_data, get_market_status
    REAL_DATA_AVAILABLE = True
    print("✅ Sistema de datos reales conectado")
except ImportError as e:
    print(f"⚠️ Sistema de datos reales no disponible: {e}")
    REAL_DATA_AVAILABLE = False


@dataclass
class PatternsConsolidatedView:
    """Vista consolidada de todos los patrones analizados"""
    symbol: str
    timeframes_analyzed: List[str]
    timestamp: datetime
    
    # Resumen por patrón
    patterns_summary: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Mejores setups
    best_scalping_setup: Optional[PatternAnalysisResult] = None
    best_intraday_setup: Optional[PatternAnalysisResult] = None
    best_overall_setup: Optional[PatternAnalysisResult] = None
    
    # Métricas consolidadas
    total_patterns_detected: int = 0
    high_confidence_patterns: int = 0
    scalping_opportunities: int = 0
    intraday_opportunities: int = 0
    
    # Recomendaciones consolidadas
    overall_bias: str = "NEUTRAL"  # BUY/SELL/NEUTRAL
    confidence_score: float = 0.0
    risk_level: str = "MEDIUM"  # LOW/MEDIUM/HIGH
    
    # Confluencias globales
    global_confluences: List[str] = field(default_factory=list)
    key_levels: Dict[str, float] = field(default_factory=dict)


class PatternsOrchestrator:
    """
    🎼 Orchestrator principal para gestión de patrones
    
    Funcionalidades:
    - Auto-discovery de patrones disponibles
    - Carga dinámica de módulos
    - Updates simultáneos y asíncronos
    - Consolidación de análisis
    - Gestión de cache y performance
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.factory = PatternFactory()  # Crear instancia de la factory
        
        # Estado del orchestrator
        self.loaded_patterns: Dict[str, BasePatternDashboard] = {}
        self.last_update_time: Dict[str, datetime] = {}
        self.update_frequencies: Dict[str, int] = {}  # seconds
        self.priority_patterns: Set[str] = set()
        self.enabled_patterns: Set[str] = set()
        
        # Performance tracking
        self.performance_stats: Dict[str, Dict[str, float]] = {}
        self.error_counts: Dict[str, int] = {}
        
        # Threading
        self.max_workers = self.config.get('max_workers', 4)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Cache consolidado
        self.consolidated_cache: Dict[str, PatternsConsolidatedView] = {}
        self.cache_ttl = self.config.get('cache_ttl_seconds', 180)  # 3 minutos
        
        # Sistema de datos reales
        self.real_data_available = REAL_DATA_AVAILABLE
        self.last_data_check: Optional[datetime] = None
        self.connection_status = {"connected": False, "last_check": None}
        
        # Inicialización
        self._initialize_orchestrator()
    
    def _initialize_orchestrator(self):
        """Inicializar el orchestrator"""
        print("🎼 Inicializando Patterns Orchestrator...")
        
        # Auto-descubrir y generar módulos faltantes
        self.factory.auto_discover_and_generate()
        
        # Verificar conexión de datos reales
        self._check_real_data_connection()
        
        # Cargar configuración de patrones
        self._load_patterns_config()
        
        # Cargar módulos de patrones
        self._load_pattern_modules()
        
        # Si no se cargaron patrones, forzar configuración por defecto
        if len(self.loaded_patterns) == 0:
            print("⚠️ No se cargaron patrones, forzando configuración por defecto...")
            self._create_default_config()
            self._load_pattern_modules()
        
        print(f"✅ Orchestrator inicializado con {len(self.loaded_patterns)} patrones")
    
    def _check_real_data_connection(self):
        """Verificar conexión con datos reales"""
        if not self.real_data_available:
            print("⚠️ Sistema de datos reales no disponible")
            return False
        
        try:
            status = get_market_status()
            self.connection_status = {
                "connected": status.get('connected', False),
                "last_check": datetime.now(),
                "provider": status.get('provider', 'Unknown'),
                "cache_size": status.get('cache_size', 0)
            }
            
            if self.connection_status["connected"]:
                print(f"✅ Conexión de datos reales verificada: {status.get('provider', 'Unknown')}")
            else:
                print("❌ Datos reales no conectados")
                
            return self.connection_status["connected"]
            
        except Exception as e:
            print(f"❌ Error verificando conexión de datos reales: {e}")
            self.connection_status["connected"] = False
            return False
    
    def is_connected_to_real_data(self) -> bool:
        """Verificar si estamos conectados a datos reales"""
        return self.connection_status.get("connected", False)
    
    def get_real_data(self, symbol: str = "EURUSD", timeframe: str = "H1") -> Optional[Dict[str, Any]]:
        """Obtener datos de mercado reales"""
        if not self.real_data_available or not self.is_connected_to_real_data():
            print(f"⚠️ Datos reales no disponibles para {symbol} {timeframe}")
            return None
        
        try:
            return get_real_market_data(symbol, timeframe)
        except Exception as e:
            print(f"❌ Error obteniendo datos reales: {e}")
            return None
    
    def reconnect_real_data(self):
        """Intentar reconectar al sistema de datos reales"""
        print("🔄 Intentando reconectar datos reales...")
        return self._check_real_data_connection()
    
    def get_real_market_data(self, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        """Obtener datos reales del mercado"""
        if not self.real_data_available:
            return None
        
        try:
            # Verificar conexión periódicamente
            now = datetime.now()
            if (self.last_data_check is None or 
                (now - self.last_data_check).total_seconds() > 300):  # 5 minutos
                self._check_real_data_connection()
                self.last_data_check = now
            
            if not self.connection_status["connected"]:
                print(f"⚠️ Datos reales no disponibles para {symbol} {timeframe}")
                return None
            
            # Obtener datos reales
            data = get_real_market_data(symbol, timeframe)
            if data:
                print(f"✅ Datos reales obtenidos para {symbol} {timeframe}")
                return data
            else:
                print(f"❌ No se obtuvieron datos para {symbol} {timeframe}")
                return None
                
        except Exception as e:
            print(f"❌ Error obteniendo datos reales {symbol} {timeframe}: {e}")
            return None
    
    def is_real_data_connected(self) -> bool:
        """Verificar si los datos reales están conectados"""
        return self.real_data_available and self.connection_status.get("connected", False)
    
    def force_reconnect_real_data(self) -> bool:
        """Forzar reconexión a datos reales"""
        print("🔄 Forzando reconexión a datos reales...")
        return self._check_real_data_connection()
        
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado completo del sistema"""
        return {
            "real_data_available": self.real_data_available,
            "connection_status": self.connection_status.copy(),
            "loaded_patterns": len(self.loaded_patterns),
            "cache_entries": len(self.consolidated_cache),
            "last_update": self.last_data_check.isoformat() if self.last_data_check else None,
            "orchestrator_ready": len(self.loaded_patterns) > 0
        }
    
    def _load_patterns_config(self):
        """Cargar configuración de patrones"""
        try:
            config_path = Path(__file__).parent / "config" / "patterns_orchestrator_config.json"
            if config_path.exists():
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    patterns_config = json.load(f)
                    
                    self.priority_patterns = set(patterns_config.get('priority_patterns', []))
                    self.enabled_patterns = set(patterns_config.get('enabled_patterns', []))
                    self.update_frequencies = patterns_config.get('update_frequencies', {})
            else:
                # Configuración por defecto
                self._create_default_config()
                
        except Exception as e:
            print(f"⚠️ Error cargando configuración de patrones: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Crear configuración por defecto"""
        print("🔧 Creando configuración por defecto...")
        
        # Patrones prioritarios (basado en PatternType enum)
        self.priority_patterns = {
            'silver_bullet', 'judas_swing', 'liquidity_grab', 
            'optimal_trade_entry', 'order_block', 'fair_value_gap'
        }
        
        # Habilitar todos los patrones disponibles
        available_patterns = self.factory.get_available_patterns()
        self.enabled_patterns = set(available_patterns)
        print(f"✅ Habilitados {len(self.enabled_patterns)} patrones por defecto: {list(self.enabled_patterns)[:5]}...")
        
        # Frecuencias por defecto (segundos)
        self.update_frequencies = {
            'silver_bullet': 60,      # 1 minuto
            'judas_swing': 120,       # 2 minutos
            'liquidity_grab': 90,     # 1.5 minutos
            'optimal_trade_entry': 180, # 3 minutos
            'order_block': 240,       # 4 minutos
            'fair_value_gap': 180,    # 3 minutos
            'power_of_three': 300,    # 5 minutos
            'morning_reversal': 240,  # 4 minutos
            'mitigation_block': 300   # 5 minutos
        }
        
        # Guardar configuración por defecto
        self._save_patterns_config()
    
    def _save_patterns_config(self):
        """Guardar configuración actual"""
        try:
            import json
            config_dir = Path(__file__).parent / "config"
            config_dir.mkdir(exist_ok=True)
            
            config_data = {
                'priority_patterns': list(self.priority_patterns),
                'enabled_patterns': list(self.enabled_patterns),
                'update_frequencies': self.update_frequencies,
                'last_updated': datetime.now().isoformat()
            }
            
            config_path = config_dir / "patterns_orchestrator_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Error guardando configuración: {e}")
    
    def _load_pattern_modules(self):
        """Cargar todos los módulos de patrones habilitados"""
        available_patterns = self.factory.get_available_patterns()
        
        for pattern_name in available_patterns:
            if pattern_name in self.enabled_patterns:
                try:
                    pattern_instance = self.factory.create_pattern_dashboard(pattern_name)
                    if pattern_instance:
                        self.loaded_patterns[pattern_name] = pattern_instance
                        self.performance_stats[pattern_name] = {
                            'total_calls': 0,
                            'total_time': 0.0,
                            'avg_time': 0.0,
                            'success_rate': 100.0
                        }
                        print(f"✅ Patrón cargado: {pattern_name}")
                    else:
                        print(f"⚠️ No se pudo cargar patrón: {pattern_name}")
                        
                except Exception as e:
                    print(f"⚠️ Error cargando patrón {pattern_name}: {e}")
                    self.error_counts[pattern_name] = self.error_counts.get(pattern_name, 0) + 1
    
    def discover_available_patterns(self) -> List[str]:
        """Escanear y descubrir patrones disponibles"""
        return self.factory.get_available_patterns()
    
    def reload_pattern_module(self, pattern_name: str) -> bool:
        """Recargar módulo específico (hot-reload)"""
        try:
            # Recargar en factory
            if self.factory.reload_module(pattern_name):
                # Recrear instancia
                pattern_instance = self.factory.create_pattern_dashboard(pattern_name)
                if pattern_instance:
                    self.loaded_patterns[pattern_name] = pattern_instance
                    print(f"✅ Patrón recargado: {pattern_name}")
                    return True
            return False
        except Exception as e:
            print(f"⚠️ Error recargando patrón {pattern_name}: {e}")
            return False
    
    def update_single_pattern(self, pattern_name: str, symbol: str, timeframe: str, 
                            force_refresh: bool = False) -> Optional[PatternAnalysisResult]:
        """Actualizar un patrón específico"""
        if pattern_name not in self.loaded_patterns:
            return None
        
        start_time = time.time()
        try:
            pattern_module = self.loaded_patterns[pattern_name]
            result = pattern_module.analyze_pattern(symbol, timeframe, force_refresh)
            
            # Actualizar estadísticas de performance
            execution_time = time.time() - start_time
            stats = self.performance_stats[pattern_name]
            stats['total_calls'] += 1
            stats['total_time'] += execution_time
            stats['avg_time'] = stats['total_time'] / stats['total_calls']
            
            # Actualizar tiempo de última actualización
            self.last_update_time[f"{pattern_name}_{symbol}_{timeframe}"] = datetime.now()
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"⚠️ Error actualizando patrón {pattern_name}: {e}")
            
            # Actualizar estadísticas de error
            self.error_counts[pattern_name] = self.error_counts.get(pattern_name, 0) + 1
            stats = self.performance_stats[pattern_name]
            if stats['total_calls'] > 0:
                stats['success_rate'] = ((stats['total_calls'] - self.error_counts[pattern_name]) / 
                                       stats['total_calls']) * 100
            
            return None
    
    def update_all_patterns(self, symbol: str, timeframes: List[str], 
                          priority_only: bool = False) -> Dict[str, Dict[str, PatternAnalysisResult]]:
        """
        Actualizar todos los patrones para múltiples timeframes
        
        Args:
            symbol: Símbolo a analizar
            timeframes: Lista de timeframes
            priority_only: Solo patrones prioritarios
        
        Returns:
            Dict[pattern_name][timeframe] = PatternAnalysisResult
        """
        patterns_to_update = (self.priority_patterns if priority_only 
                            else set(self.loaded_patterns.keys()))
        
        results = {}
        futures = []
        
        # Lanzar análisis en paralelo
        for pattern_name in patterns_to_update:
            if pattern_name in self.loaded_patterns:
                results[pattern_name] = {}
                
                for timeframe in timeframes:
                    # Verificar si necesita actualización
                    if self._needs_update(pattern_name, symbol, timeframe):
                        future = self.executor.submit(
                            self.update_single_pattern,
                            pattern_name, symbol, timeframe
                        )
                        futures.append((future, pattern_name, timeframe))
        
        # Recopilar resultados
        for future, pattern_name, timeframe in futures:
            try:
                result = future.result(timeout=30)  # 30 segundos timeout
                if result:
                    results[pattern_name][timeframe] = result
            except Exception as e:
                print(f"⚠️ Timeout o error en {pattern_name} {timeframe}: {e}")
        
        return results
    
    def _needs_update(self, pattern_name: str, symbol: str, timeframe: str) -> bool:
        """Verificar si un patrón necesita actualización"""
        cache_key = f"{pattern_name}_{symbol}_{timeframe}"
        
        if cache_key not in self.last_update_time:
            return True
        
        last_update = self.last_update_time[cache_key]
        frequency = self.update_frequencies.get(pattern_name, 300)  # 5 min default
        
        time_since_update = (datetime.now() - last_update).total_seconds()
        return time_since_update >= frequency
    
    def get_consolidated_view(self, symbol: str, timeframes: List[str], 
                            force_refresh: bool = False) -> PatternsConsolidatedView:
        """
        Crear vista consolidada de todos los patrones
        
        Args:
            symbol: Símbolo a analizar
            timeframes: Timeframes a incluir
            force_refresh: Forzar análisis completo
        
        Returns:
            Vista consolidada con mejores setups y recomendaciones
        """
        cache_key = f"{symbol}_{'_'.join(timeframes)}"
        
        # Verificar cache
        if not force_refresh and cache_key in self.consolidated_cache:
            cached_view = self.consolidated_cache[cache_key]
            age = (datetime.now() - cached_view.timestamp).total_seconds()
            if age < self.cache_ttl:
                return cached_view
        
        # Actualizar todos los patrones
        all_results = self.update_all_patterns(symbol, timeframes)
        
        # Crear vista consolidada
        consolidated_view = PatternsConsolidatedView(
            symbol=symbol,
            timeframes_analyzed=timeframes,
            timestamp=datetime.now()
        )
        
        # Procesar resultados
        all_pattern_results = []
        
        for pattern_name, timeframe_results in all_results.items():
            pattern_summary = {
                'patterns_detected': len(timeframe_results),
                'best_confidence': 0.0,
                'best_timeframe': None,
                'direction_consensus': 'NEUTRAL',
                'scalping_viable': False,
                'intraday_viable': False
            }
            
            # Analizar resultados por timeframe
            buy_votes = 0
            sell_votes = 0
            
            for tf, result in timeframe_results.items():
                all_pattern_results.append(result)
                
                # Actualizar mejor confianza
                if result.confidence > pattern_summary['best_confidence']:
                    pattern_summary['best_confidence'] = result.confidence
                    pattern_summary['best_timeframe'] = tf
                
                # Contar votos direccionales
                if result.direction == 'BUY' and result.confidence >= 60:
                    buy_votes += 1
                elif result.direction == 'SELL' and result.confidence >= 60:
                    sell_votes += 1
                
                # Verificar viabilidad de trading
                if result.scalping_viability in ['HIGH', 'MEDIUM']:
                    pattern_summary['scalping_viable'] = True
                if result.intraday_viability in ['HIGH', 'MEDIUM']:
                    pattern_summary['intraday_viable'] = True
            
            # Determinar consenso direccional
            if buy_votes > sell_votes:
                pattern_summary['direction_consensus'] = 'BUY'
            elif sell_votes > buy_votes:
                pattern_summary['direction_consensus'] = 'SELL'
            
            consolidated_view.patterns_summary[pattern_name] = pattern_summary
        
        # Encontrar mejores setups
        if all_pattern_results:
            # Mejor setup de scalping
            scalping_results = [r for r in all_pattern_results 
                              if r.scalping_viability in ['HIGH', 'MEDIUM']]
            if scalping_results:
                consolidated_view.best_scalping_setup = max(scalping_results, 
                                                          key=lambda x: x.confidence)
            
            # Mejor setup intraday
            intraday_results = [r for r in all_pattern_results 
                              if r.intraday_viability in ['HIGH', 'MEDIUM']]
            if intraday_results:
                consolidated_view.best_intraday_setup = max(intraday_results, 
                                                          key=lambda x: x.risk_reward_ratio)
            
            # Mejor setup general
            consolidated_view.best_overall_setup = max(all_pattern_results, 
                                                     key=lambda x: x.confidence)
        
        # Calcular métricas consolidadas
        consolidated_view.total_patterns_detected = len(all_pattern_results)
        consolidated_view.high_confidence_patterns = len([r for r in all_pattern_results 
                                                        if r.confidence >= 70])
        consolidated_view.scalping_opportunities = len([r for r in all_pattern_results 
                                                      if r.scalping_viability in ['HIGH', 'MEDIUM']])
        consolidated_view.intraday_opportunities = len([r for r in all_pattern_results 
                                                      if r.intraday_viability in ['HIGH', 'MEDIUM']])
        
        # Determinar bias general
        total_buy_votes = sum(1 for summary in consolidated_view.patterns_summary.values()
                            if summary['direction_consensus'] == 'BUY')
        total_sell_votes = sum(1 for summary in consolidated_view.patterns_summary.values()
                             if summary['direction_consensus'] == 'SELL')
        
        if total_buy_votes > total_sell_votes:
            consolidated_view.overall_bias = 'BUY'
        elif total_sell_votes > total_buy_votes:
            consolidated_view.overall_bias = 'SELL'
        else:
            consolidated_view.overall_bias = 'NEUTRAL'
        
        # Confidence score consolidado
        if all_pattern_results:
            consolidated_view.confidence_score = sum(r.confidence for r in all_pattern_results) / len(all_pattern_results)
        
        # Determinar nivel de riesgo
        if consolidated_view.confidence_score >= 80:
            consolidated_view.risk_level = 'LOW'
        elif consolidated_view.confidence_score >= 60:
            consolidated_view.risk_level = 'MEDIUM'
        else:
            consolidated_view.risk_level = 'HIGH'
        
        # Extraer confluencias globales
        all_confluences = []
        for result in all_pattern_results:
            all_confluences.extend(result.confluences)
        
        # Contar confluencias y tomar las más comunes
        from collections import Counter
        confluence_counts = Counter(all_confluences)
        consolidated_view.global_confluences = [conf for conf, count in confluence_counts.most_common(5)]
        
        # Guardar en cache
        self.consolidated_cache[cache_key] = consolidated_view
        
        return consolidated_view
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de performance del orchestrator"""
        return {
            'loaded_patterns': len(self.loaded_patterns),
            'enabled_patterns': len(self.enabled_patterns),
            'priority_patterns': len(self.priority_patterns),
            'performance_stats': self.performance_stats,
            'error_counts': self.error_counts,
            'cache_size': len(self.consolidated_cache),
            'last_update': max(self.last_update_time.values()) if self.last_update_time else None
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Verificar salud del orchestrator y módulos"""
        health_status = {
            'overall_status': 'HEALTHY',
            'timestamp': datetime.now(),
            'patterns_status': {},
            'issues': []
        }
        
        for pattern_name in self.loaded_patterns:
            pattern_status = {
                'loaded': True,
                'error_rate': 0.0,
                'avg_response_time': 0.0,
                'status': 'HEALTHY'
            }
            
            # Calcular tasa de error
            if pattern_name in self.error_counts:
                stats = self.performance_stats.get(pattern_name, {})
                total_calls = stats.get('total_calls', 1)
                error_rate = (self.error_counts[pattern_name] / total_calls) * 100
                pattern_status['error_rate'] = error_rate
                pattern_status['avg_response_time'] = stats.get('avg_time', 0.0)
                
                # Determinar estado
                if error_rate > 50:
                    pattern_status['status'] = 'CRITICAL'
                    health_status['issues'].append(f"Patrón {pattern_name} tiene {error_rate:.1f}% de errores")
                elif error_rate > 20:
                    pattern_status['status'] = 'WARNING'
                elif stats.get('avg_time', 0) > 10:  # Más de 10 segundos
                    pattern_status['status'] = 'SLOW'
                    health_status['issues'].append(f"Patrón {pattern_name} es lento ({stats['avg_time']:.2f}s)")
            
            health_status['patterns_status'][pattern_name] = pattern_status
        
        # Determinar estado general
        critical_patterns = [p for p, s in health_status['patterns_status'].items() 
                           if s['status'] == 'CRITICAL']
        if critical_patterns:
            health_status['overall_status'] = 'CRITICAL'
        elif health_status['issues']:
            health_status['overall_status'] = 'WARNING'
        
        return health_status
    
    def cleanup(self):
        """Limpiar recursos del orchestrator"""
        try:
            self.executor.shutdown(wait=True)
            self.consolidated_cache.clear()
            print("✅ Orchestrator limpiado exitosamente")
        except Exception as e:
            print(f"⚠️ Error limpiando orchestrator: {e}")


# Instancia global del orchestrator
patterns_orchestrator = PatternsOrchestrator()
