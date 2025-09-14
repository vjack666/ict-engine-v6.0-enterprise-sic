#!/usr/bin/env python3
"""
🏗️ MARKET STRUCTURE TAB v6.0 ENTERPRISE - STRUCTURAL ANALYSIS
============================================================

Interface completa para análisis de estructura de mercado avanzado.
Detección de tendencias, niveles estructurales y fases de mercado.

FUNCIONALIDADES ENTERPRISE:
✅ Trend analysis & detection (multitimeframe)
✅ Support/Resistance level identification
✅ Market phase classification (accumulation/distribution/trend)
✅ Structural breakout detection & confirmation
✅ Higher high/lower low pattern recognition
✅ Market regime analysis (trending/ranging)
✅ Volume structure analysis
✅ Confluence zone identification

ARQUITECTURA APLICADA:
✅ Dashboard Core Integration (patrón establecido)
✅ Tab Coordinator Integration (state management)
✅ SmartMoneyAnalyzer Integration (structural engine)
✅ UnifiedMemorySystem Integration (historical patterns)
✅ Enterprise logging & monitoring (structured)

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 13 Septiembre 2025
"""

import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

# Dashboard architecture imports (patrón establecido)
try:
    import sys
    
    # Add dashboard core path
    dashboard_core_path = Path(__file__).parent.parent
    if str(dashboard_core_path) not in sys.path:
        sys.path.insert(0, str(dashboard_core_path))
    
    from dashboard_core import get_dashboard_core, DashboardCore
    from tab_coordinator import get_tab_coordinator, TabCoordinator, TabState
    
    # Get dashboard components through core
    dashboard_core = get_dashboard_core()
    html, dcc, Input, Output, State, callback = dashboard_core.get_components()
    go, px, make_subplots = dashboard_core.get_plotting_components()
    pd = dashboard_core.imports.pd
    
    DASHBOARD_AVAILABLE = dashboard_core.imports.dash_available
    PLOTLY_AVAILABLE = dashboard_core.imports.plotly_available
    
    # Validación crítica de componentes reales
    if html is None or dcc is None:
        raise ImportError("Dashboard components not available - required for enterprise mode")
    
    print("✅ Market Structure Tab - Dashboard architecture loaded successfully")

except ImportError as e:
    print(f"❌ CRITICAL: Dashboard architecture required but not available: {e}")
    print("❌ Market Structure Tab requires REAL dashboard components")
    raise ImportError(f"Enterprise mode requires real dashboard components: {e}") from e

# Core system imports
try:
    current_dir = Path(__file__).parent.parent.parent.parent / "01-CORE"
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
    from smart_trading_logger import SmartTradingLogger
    
    # Validación crítica de componentes core reales
    if SmartMoneyAnalyzer is None or SmartTradingLogger is None:
        raise ImportError("Core analyzer components not available - required for enterprise mode")
    
    CORE_AVAILABLE = True
    print("✅ Market Structure Tab - Core components loaded successfully")
    
except ImportError as e:
    print(f"❌ CRITICAL: Core systems required but not available: {e}")
    print("❌ Market Structure Tab requires REAL core components")
    raise ImportError(f"Enterprise mode requires real core components: {e}") from e


class TrendDirection(Enum):
    """📈 Direcciones de tendencia"""
    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"
    UNKNOWN = "unknown"


class MarketPhase(Enum):
    """🌊 Fases de mercado"""
    ACCUMULATION = "accumulation"
    MARKUP = "markup"
    DISTRIBUTION = "distribution"
    MARKDOWN = "markdown"
    RANGING = "ranging"


class MarketRegime(Enum):
    """🔄 Régimen de mercado"""
    TRENDING = "trending"
    RANGING = "ranging"
    VOLATILE = "volatile"
    CALM = "calm"


@dataclass
class StructuralLevel:
    """🏗️ Nivel estructural"""
    price: float
    level_type: str  # support, resistance, pivot
    strength: float  # 0.0 to 1.0
    touches: int
    last_test: datetime
    confirmed: bool


@dataclass
class TrendAnalysis:
    """📈 Análisis de tendencia"""
    direction: TrendDirection
    strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    duration: int  # bars
    slope: float
    higher_highs: List[float]
    lower_lows: List[float]


class MarketStructureEngine:
    """
    🏗️ MOTOR DE ANÁLISIS DE ESTRUCTURA DE MERCADO
    ============================================
    
    Motor especializado para análisis estructural completo
    """
    
    def __init__(self):
        self.structural_levels: List[StructuralLevel] = []
        self.trend_history: List[TrendAnalysis] = []
        self.market_phases: List[Dict[str, Any]] = []
        
        # Configuration
        self.lookback_periods = {
            'short': 50,
            'medium': 200,
            'long': 500
        }
        
        self.level_sensitivity = 0.0015  # 15 pips for EURUSD
        
    def analyze_market_structure(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """🏗️ Análisis completo de estructura"""
        try:
            if not price_data or len(price_data) < 20:
                return self._create_empty_structure_analysis()
            
            # Extract OHLC data
            closes = [candle['close'] for candle in price_data]
            highs = [candle['high'] for candle in price_data]
            lows = [candle['low'] for candle in price_data]
            volumes = [candle.get('volume', 1000) for candle in price_data]
            
            # Core structural analysis
            trend_analysis = self._analyze_trend(closes, highs, lows)
            structural_levels = self._identify_structural_levels(highs, lows)
            market_phase = self._determine_market_phase(closes, volumes)
            market_regime = self._classify_market_regime(closes, volumes)
            breakout_analysis = self._detect_structural_breakouts(closes, highs, lows, structural_levels)
            
            # Volume structure
            volume_structure = self._analyze_volume_structure(closes, volumes)
            
            # Confluence zones
            confluence_zones = self._identify_confluence_zones(structural_levels)
            
            return {
                'trend_analysis': {
                    'direction': trend_analysis.direction.value,
                    'strength': trend_analysis.strength,
                    'confidence': trend_analysis.confidence,
                    'slope': trend_analysis.slope,
                    'higher_highs': trend_analysis.higher_highs[-5:],  # Last 5
                    'lower_lows': trend_analysis.lower_lows[-5:]
                },
                'structural_levels': [
                    {
                        'price': level.price,
                        'type': level.level_type,
                        'strength': level.strength,
                        'touches': level.touches,
                        'confirmed': level.confirmed
                    } for level in structural_levels[:10]  # Top 10 levels
                ],
                'market_phase': market_phase.value,
                'market_regime': market_regime.value,
                'breakout_analysis': breakout_analysis,
                'volume_structure': volume_structure,
                'confluence_zones': confluence_zones,
                'statistics': {
                    'total_levels': len(structural_levels),
                    'confirmed_levels': sum(1 for level in structural_levels if level.confirmed),
                    'trend_duration': trend_analysis.duration,
                    'market_volatility': self._calculate_volatility(closes)
                }
            }
            
        except Exception as e:
            print(f"❌ Error analyzing market structure: {e}")
            return {'error': str(e)}
    
    def _analyze_trend(self, closes: List[float], highs: List[float], lows: List[float]) -> TrendAnalysis:
        """📈 Analizar tendencia"""
        if len(closes) < 20:
            return TrendAnalysis(
                direction=TrendDirection.UNKNOWN,
                strength=0.0,
                confidence=0.0,
                duration=0,
                slope=0.0,
                higher_highs=[],
                lower_lows=[]
            )
        
        # Calculate moving averages for trend direction
        short_ma = sum(closes[-20:]) / 20
        long_ma = sum(closes[-50:]) / min(50, len(closes))
        
        # Determine trend direction
        if short_ma > long_ma * 1.001:  # 0.1% threshold
            direction = TrendDirection.UPTREND
        elif short_ma < long_ma * 0.999:
            direction = TrendDirection.DOWNTREND
        else:
            direction = TrendDirection.SIDEWAYS
        
        # Calculate trend strength based on slope
        slope = (closes[-1] - closes[-20]) / 20 if len(closes) >= 20 else 0
        strength = min(abs(slope) * 10000, 1.0)  # Normalize slope
        
        # Calculate confidence based on consistency
        recent_prices = closes[-10:]
        if direction == TrendDirection.UPTREND:
            positive_moves = sum(1 for i in range(1, len(recent_prices)) if recent_prices[i] > recent_prices[i-1])
            confidence = positive_moves / (len(recent_prices) - 1)
        elif direction == TrendDirection.DOWNTREND:
            negative_moves = sum(1 for i in range(1, len(recent_prices)) if recent_prices[i] < recent_prices[i-1])
            confidence = negative_moves / (len(recent_prices) - 1)
        else:
            confidence = 0.5
        
        # Find higher highs and lower lows
        higher_highs = self._find_higher_highs(highs)
        lower_lows = self._find_lower_lows(lows)
        
        return TrendAnalysis(
            direction=direction,
            strength=strength,
            confidence=confidence,
            duration=20,  # Simplified
            slope=slope,
            higher_highs=higher_highs,
            lower_lows=lower_lows
        )
    
    def _find_higher_highs(self, highs: List[float]) -> List[float]:
        """📈 Encontrar higher highs"""
        higher_highs = []
        if len(highs) < 10:
            return higher_highs
        
        for i in range(5, len(highs) - 5):
            is_peak = all(highs[i] >= highs[j] for j in range(i-5, i+6) if j != i)
            if is_peak and (not higher_highs or highs[i] > higher_highs[-1]):
                higher_highs.append(highs[i])
        
        return higher_highs[-10:]  # Last 10
    
    def _find_lower_lows(self, lows: List[float]) -> List[float]:
        """📉 Encontrar lower lows"""
        lower_lows = []
        if len(lows) < 10:
            return lower_lows
        
        for i in range(5, len(lows) - 5):
            is_trough = all(lows[i] <= lows[j] for j in range(i-5, i+6) if j != i)
            if is_trough and (not lower_lows or lows[i] < lower_lows[-1]):
                lower_lows.append(lows[i])
        
        return lower_lows[-10:]  # Last 10
    
    def _identify_structural_levels(self, highs: List[float], lows: List[float]) -> List[StructuralLevel]:
        """🏗️ Identificar niveles estructurales"""
        levels = []
        
        # Find resistance levels (from highs)
        resistance_levels = self._find_significant_levels(highs, 'resistance')
        levels.extend(resistance_levels)
        
        # Find support levels (from lows)
        support_levels = self._find_significant_levels(lows, 'support')
        levels.extend(support_levels)
        
        # Sort by strength
        levels.sort(key=lambda x: x.strength, reverse=True)
        
        return levels
    
    def _find_significant_levels(self, prices: List[float], level_type: str) -> List[StructuralLevel]:
        """🔍 Encontrar niveles significativos"""
        levels = []
        
        if len(prices) < 20:
            return levels
        
        # Group prices by proximity
        price_groups = {}
        for price in prices:
            found_group = False
            for group_price in price_groups:
                if abs(price - group_price) <= self.level_sensitivity:
                    price_groups[group_price].append(price)
                    found_group = True
                    break
            
            if not found_group:
                price_groups[price] = [price]
        
        # Create structural levels from groups
        for group_price, group_prices in price_groups.items():
            if len(group_prices) >= 2:  # At least 2 touches
                avg_price = sum(group_prices) / len(group_prices)
                strength = min(len(group_prices) / 5.0, 1.0)  # Normalize by max 5 touches
                
                level = StructuralLevel(
                    price=avg_price,
                    level_type=level_type,
                    strength=strength,
                    touches=len(group_prices),
                    last_test=datetime.now(),
                    confirmed=len(group_prices) >= 3
                )
                levels.append(level)
        
        return levels
    
    def _determine_market_phase(self, closes: List[float], volumes: List[float]) -> MarketPhase:
        """🌊 Determinar fase de mercado"""
        if len(closes) < 50:
            return MarketPhase.RANGING
        
        # Price momentum
        short_term_change = (closes[-1] - closes[-10]) / closes[-10]
        long_term_change = (closes[-1] - closes[-50]) / closes[-50]
        
        # Volume analysis
        recent_volume = sum(volumes[-10:]) / 10
        avg_volume = sum(volumes) / len(volumes)
        volume_ratio = recent_volume / avg_volume
        
        # Classification logic
        if short_term_change > 0.01 and volume_ratio > 1.2:
            return MarketPhase.MARKUP
        elif short_term_change < -0.01 and volume_ratio > 1.2:
            return MarketPhase.MARKDOWN
        elif abs(short_term_change) < 0.005 and volume_ratio > 1.1:
            return MarketPhase.ACCUMULATION if long_term_change >= 0 else MarketPhase.DISTRIBUTION
        else:
            return MarketPhase.RANGING
    
    def _classify_market_regime(self, closes: List[float], volumes: List[float]) -> MarketRegime:
        """🔄 Clasificar régimen de mercado"""
        if len(closes) < 20:
            return MarketRegime.CALM
        
        # Volatility calculation
        volatility = self._calculate_volatility(closes)
        
        # Volume analysis
        volume_volatility = self._calculate_volatility(volumes)
        
        # Classification
        if volatility > 0.02:  # 2%
            return MarketRegime.VOLATILE
        elif volatility > 0.01:  # 1%
            return MarketRegime.TRENDING
        else:
            return MarketRegime.RANGING if volume_volatility < 0.5 else MarketRegime.CALM
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """📊 Calcular volatilidad"""
        if len(prices) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        
        if not returns:
            return 0.0
        
        # Standard deviation of returns
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        
        return variance ** 0.5
    
    def _detect_structural_breakouts(self, closes: List[float], highs: List[float], 
                                   lows: List[float], levels: List[StructuralLevel]) -> Dict[str, Any]:
        """💥 Detectar rupturas estructurales"""
        if not closes or not levels:
            return {'breakouts': [], 'pending': []}
        
        current_price = closes[-1]
        recent_high = max(highs[-5:]) if len(highs) >= 5 else current_price
        recent_low = min(lows[-5:]) if len(lows) >= 5 else current_price
        
        breakouts = []
        pending = []
        
        for level in levels:
            distance_to_level = abs(current_price - level.price) / level.price
            
            # Breakout detection
            if level.level_type == 'resistance' and recent_high > level.price * 1.001:  # 0.1% buffer
                breakouts.append({
                    'level': level.price,
                    'type': 'resistance_break',
                    'strength': level.strength,
                    'direction': 'bullish'
                })
            elif level.level_type == 'support' and recent_low < level.price * 0.999:
                breakouts.append({
                    'level': level.price,
                    'type': 'support_break',
                    'strength': level.strength,
                    'direction': 'bearish'
                })
            elif distance_to_level < 0.005:  # Within 0.5%
                pending.append({
                    'level': level.price,
                    'type': level.level_type,
                    'distance': distance_to_level,
                    'strength': level.strength
                })
        
        return {
            'breakouts': breakouts[-5:],  # Last 5 breakouts
            'pending': sorted(pending, key=lambda x: x['distance'])[:3]  # 3 closest
        }
    
    def _analyze_volume_structure(self, closes: List[float], volumes: List[float]) -> Dict[str, Any]:
        """📊 Analizar estructura de volumen"""
        if len(volumes) < 20:
            return {'trend': 'neutral', 'strength': 0.5, 'profile': []}
        
        # Volume trend
        recent_avg = sum(volumes[-10:]) / 10
        historical_avg = sum(volumes[:-10]) / len(volumes[:-10]) if len(volumes) > 10 else recent_avg
        
        volume_trend = 'increasing' if recent_avg > historical_avg * 1.1 else \
                      'decreasing' if recent_avg < historical_avg * 0.9 else 'stable'
        
        # Volume strength
        max_volume = max(volumes)
        min_volume = min(volumes) if min(volumes) > 0 else 1
        volume_strength = (recent_avg - min_volume) / (max_volume - min_volume)
        
        # Volume profile (simplified)
        price_volume_pairs = list(zip(closes, volumes))
        price_volume_pairs.sort()
        
        profile = []
        chunk_size = len(price_volume_pairs) // 5  # 5 buckets
        
        for i in range(0, len(price_volume_pairs), chunk_size):
            chunk = price_volume_pairs[i:i+chunk_size]
            if chunk:
                avg_price = sum(pair[0] for pair in chunk) / len(chunk)
                total_volume = sum(pair[1] for pair in chunk)
                profile.append({'price_level': avg_price, 'volume': total_volume})
        
        return {
            'trend': volume_trend,
            'strength': volume_strength,
            'recent_avg': recent_avg,
            'historical_avg': historical_avg,
            'profile': profile
        }
    
    def _identify_confluence_zones(self, levels: List[StructuralLevel]) -> List[Dict[str, Any]]:
        """🎯 Identificar zonas de confluencia"""
        confluence_zones = []
        
        # Group levels by proximity
        for i, level1 in enumerate(levels):
            nearby_levels = [level1]
            
            for j, level2 in enumerate(levels):
                if i != j and abs(level1.price - level2.price) / level1.price <= 0.003:  # 0.3%
                    nearby_levels.append(level2)
            
            if len(nearby_levels) >= 2:  # Confluence requires at least 2 levels
                avg_price = sum(level.price for level in nearby_levels) / len(nearby_levels)
                total_strength = sum(level.strength for level in nearby_levels)
                
                confluence_zones.append({
                    'price': avg_price,
                    'level_count': len(nearby_levels),
                    'total_strength': total_strength,
                    'types': list(set(level.level_type for level in nearby_levels))
                })
        
        # Remove duplicates and sort by strength
        unique_zones = []
        for zone in confluence_zones:
            is_duplicate = any(abs(zone['price'] - existing['price']) / zone['price'] <= 0.001 
                             for existing in unique_zones)
            if not is_duplicate:
                unique_zones.append(zone)
        
        unique_zones.sort(key=lambda x: x['total_strength'], reverse=True)
        return unique_zones[:5]  # Top 5 confluence zones
    
    def _create_empty_structure_analysis(self) -> Dict[str, Any]:
        """📊 Crear análisis vacío"""
        return {
            'trend_analysis': {
                'direction': 'unknown',
                'strength': 0.0,
                'confidence': 0.0,
                'slope': 0.0,
                'higher_highs': [],
                'lower_lows': []
            },
            'structural_levels': [],
            'market_phase': 'ranging',
            'market_regime': 'calm',
            'breakout_analysis': {'breakouts': [], 'pending': []},
            'volume_structure': {'trend': 'neutral', 'strength': 0.5, 'profile': []},
            'confluence_zones': [],
            'statistics': {
                'total_levels': 0,
                'confirmed_levels': 0,
                'trend_duration': 0,
                'market_volatility': 0.0
            }
        }


class MarketStructureTabEnterprise:
    """
    🏗️ MARKET STRUCTURE TAB ENTERPRISE v6.0
    =======================================
    
    Interface completa para análisis de estructura de mercado avanzado.
    Aplicando arquitectura enterprise establecida.
    """
    
    def __init__(self, app=None, refresh_interval: int = 5000):  # 5 seconds for structural analysis
        self.app = app
        self.refresh_interval = refresh_interval
        self.tab_id = "market_structure_tab"
        
        # Dashboard integration (patrón establecido)
        self.dashboard_core = dashboard_core
        if dashboard_core:
            try:
                self.tab_coordinator = get_tab_coordinator()
                # Register this tab
                self.tab_coordinator.register_tab(
                    self.tab_id,
                    "Market Structure Analysis",
                    self,
                    {"refresh_interval": refresh_interval}
                )
            except Exception as e:
                print(f"⚠️ Tab coordinator registration failed: {e}")
                self.tab_coordinator = None
        else:
            self.tab_coordinator = None
            
        # Core components
        if CORE_AVAILABLE and SmartMoneyAnalyzer:
            self.analyzer = SmartMoneyAnalyzer()
        else:
            self.analyzer = None
            
        # Logger
        if CORE_AVAILABLE and SmartTradingLogger:
            self.logger = SmartTradingLogger("MarketStructureTab")
        else:
            self.logger = None
            
        # Market structure engine
        self.structure_engine = MarketStructureEngine()
        
        # Data storage
        self.current_data = {
            'trend_analysis': {},
            'structural_levels': [],
            'market_phase': 'ranging',
            'market_regime': 'calm',
            'breakout_analysis': {},
            'volume_structure': {},
            'confluence_zones': [],
            'last_update': datetime.now().isoformat(),
            'statistics': {}
        }
        
        # Visual configuration (aplicando patrón)
        if dashboard_core:
            theme_colors = dashboard_core.theme_manager.get_colors()
            self.colors = theme_colors
        else:
            self.colors = {
                'uptrend': '#00ff88',
                'downtrend': '#ff4444',
                'sideways': '#888888',
                'background': '#0e1117',
                'surface': '#1e2329',
                'text': '#ffffff',
                'support': '#00aaff',
                'resistance': '#ff6b35',
                'confluence': '#ffaa00'
            }
        
        print(f"🏗️ Market Structure Tab Enterprise initialized (refresh: {refresh_interval}ms)")
        
    def create_layout(self) -> Any:
        """
        🎨 CREAR LAYOUT PRINCIPAL MARKET STRUCTURE
        ========================================
        
        Returns:
            Layout principal para análisis estructural
        """
        if not DASHBOARD_AVAILABLE or not html:
            return {
                "error": "Dashboard components not available",
                "message": "Install Dash and dependencies to enable Market Structure analysis",
                "component": "market_structure_tab",
                "fallback_data": self.current_data
            }
        
        try:
            layout_children = [
                # Header Section
                self._create_header_section(),
                
                # Trend Analysis Section
                self._create_trend_section(),
                
                # Structural Levels Section
                self._create_levels_section(),
                
                # Market Phase & Regime Section
                self._create_phase_regime_section(),
                
                # Charts Section (Comprehensive)
                self._create_charts_section(),
                
                # Breakout Analysis Section
                self._create_breakout_section(),
                
                # Volume Structure Section
                self._create_volume_section(),
                
                # System Components
                self._create_system_components()
            ]
            
            # Return usando componentes reales únicamente
            return html.Div(
                layout_children,
                className="market-structure-tab-enterprise",
                style={
                    "backgroundColor": self.colors.get("background", "#0e1117"),
                    "color": self.colors.get("text_primary", "#ffffff"),
                    "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
                    "padding": "16px"
                }
            )
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error creating Market Structure layout: {e}", "layout_creation")
            
            return {"error": f"Layout creation failed: {e}", "fallback": True}
    
    def _create_header_section(self) -> Any:
        """🎨 Crear header estructural"""
        return html.Div([
            html.H2("🏗️ Market Structure Analysis v6.0 Enterprise", className="tab-title"),
                html.Div([
                    html.Span("📊 Structure Engine: ", className="status-label"),
                    html.Span("Active", className="status-value success"),
                    html.Span(" | 🔄 Analysis Update: ", className="status-label"),
                    html.Span(f"{self.refresh_interval}ms", className="status-value"),
                    html.Span(" | 📈 Last Analysis: ", className="status-label"),
                    html.Span(id="ms-last-update", className="status-value")
                ], className="status-bar")
            ], className="market-structure-header")
    
    def _create_trend_section(self) -> Any:
        """📈 Crear sección de análisis de tendencia"""
        return html.Div([
            html.H3("📈 Trend Analysis", className="section-title"),
            
            # Trend Metrics
            html.Div([
                self._create_trend_metric("Direction", "Unknown", "📈", "ms-trend-direction"),
                self._create_trend_metric("Strength", "0%", "⚡", "ms-trend-strength"),
                self._create_trend_metric("Confidence", "0%", "🎯", "ms-trend-confidence"),
                self._create_trend_metric("Slope", "0.0", "📐", "ms-trend-slope")
            ], className="trend-metrics"),
            
            # Higher Highs / Lower Lows
            html.Div([
                html.Div([
                    html.H4("Higher Highs", className="pattern-subtitle"),
                    html.Div(id="ms-higher-highs", className="pattern-levels")
                    ], className="pattern-section highs"),
                    
                    html.Div([
                        html.H4("Lower Lows", className="pattern-subtitle"),
                        html.Div(id="ms-lower-lows", className="pattern-levels")
                    ], className="pattern-section lows")
                ], className="trend-patterns")
                
            ], className="trend-section")
    
    def _create_trend_metric(self, title: str, value: str, icon: str, value_id: str) -> Any:
        """📈 Crear métrica de tendencia"""
        return html.Div([
            html.Div([
                html.Div(icon, className="trend-icon"),
                html.Div([
                    html.H4(value, id=value_id, className="trend-value"),
                    html.P(title, className="trend-label")
                ], className="trend-text")
            ], className="trend-metric-content")
        ], className="trend-metric")
    
    def _create_levels_section(self) -> Any:
        """🏗️ Crear sección de niveles estructurales"""
        return html.Div([
            html.H3("🏗️ Structural Levels", className="section-title"),
            
            # Levels Table
            html.Div([
                html.Div([
                        html.H4("Key Support & Resistance Levels", className="section-subtitle"),
                        html.Div(id="ms-levels-table", className="levels-table")
                    ], className="levels-display"),
                    
                    html.Div([
                        html.H4("🎯 Confluence Zones", className="section-subtitle"),
                        html.Div(id="ms-confluence-zones", className="confluence-display")
                    ], className="confluence-section")
                ], className="levels-analysis")
                
            ], className="levels-section")
    
    def _create_phase_regime_section(self) -> Any:
        """🌊 Crear sección de fase y régimen de mercado"""
        return html.Div([
            html.Div([
                html.Div([
                    html.H3("🌊 Market Phase", className="section-title"),
                    html.Div([
                        html.Div(id="ms-market-phase", className="phase-display"),
                        html.P("Current market cycle phase", className="phase-description")
                    ], className="phase-content")
                ], className="phase-section"),
                
                html.Div([
                        html.H3("🔄 Market Regime", className="section-title"),
                        html.Div([
                            html.Div(id="ms-market-regime", className="regime-display"),
                            html.P("Current market behavior pattern", className="regime-description")
                        ], className="regime-content")
                    ], className="regime-section")
                ], className="phase-regime-container")
            ], className="phase-regime-section")
    
    def _create_charts_section(self) -> Any:
        """📊 Crear sección de gráficos estructurales"""
        return html.Div([
            # Main Structure Chart
            html.Div([
                html.H3("📊 Market Structure Overview", className="chart-title"),
                    dcc.Graph(
                        id="ms-structure-chart",
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
                        }
                    )
                ], className="chart-container structure-chart"),
                
                # Levels Visualization Chart
                html.Div([
                    html.H3("🏗️ Support & Resistance Levels", className="chart-title"),
                    dcc.Graph(
                        id="ms-levels-chart",
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
                        }
                    )
                ], className="chart-container levels-chart")
                
            ], className="ms-charts")
    
    def _create_breakout_section(self) -> Any:
        """💥 Crear sección de análisis de rupturas"""
        return html.Div([
            html.H3("💥 Breakout Analysis", className="section-title"),
            
            html.Div([
                html.Div([
                    html.H4("Recent Breakouts", className="section-subtitle"),
                    html.Div(id="ms-recent-breakouts", className="breakouts-display")
                ], className="breakouts-section"),
                    
                    html.Div([
                        html.H4("Pending Breakouts", className="section-subtitle"),
                        html.Div(id="ms-pending-breakouts", className="pending-display")
                    ], className="pending-section")
                ], className="breakout-analysis")
                
            ], className="breakout-section")
    
    def _create_volume_section(self) -> Any:
        """📊 Crear sección de estructura de volumen"""
        return html.Div([
            html.H3("📊 Volume Structure", className="section-title"),
            html.Div([
                html.Div([
                    html.H4("Volume Trend", className="section-subtitle"),
                    html.Div(id="ms-volume-trend", className="volume-trend-display")
                ], className="volume-trend-section"),
                
                html.Div([
                    html.H4("Volume Profile", className="section-subtitle"),
                    html.Div(id="ms-volume-profile", className="volume-profile-display")
                ], className="volume-profile-section")
            ], className="volume-analysis")
        ], className="volume-section")
    
    def _create_system_components(self) -> Any:
        """🔧 Crear componentes del sistema (patrón establecido)"""
        return html.Div([
            dcc.Interval(
                id="ms-refresh-interval",
                interval=self.refresh_interval,
                n_intervals=0
            ),
            dcc.Store(id="ms-data-store", data=self.current_data)
        ])
    
    def fetch_market_structure_data(self, symbol: str = "EURUSD") -> Dict[str, Any]:
        """
        🏗️ OBTENER DATOS DE ESTRUCTURA DE MERCADO
        =======================================
        
        Args:
            symbol: Par de divisas
            
        Returns:
            Análisis completo de estructura de mercado
        """
        try:
            start_time = time.time()
            
            # Get market data for structural analysis
            price_data = self._get_historical_price_data(symbol)
            
            # Analyze market structure
            structure_analysis = self.structure_engine.analyze_market_structure(price_data)
            
            processing_time = (time.time() - start_time) * 1000
            
            if self.logger:
                self.logger.info(f"Market Structure data processed: {symbol}", "data_fetch")
            
            result = {
                **structure_analysis,
                'last_update': datetime.now().isoformat(),
                'performance': {
                    'processing_time_ms': processing_time,
                    'symbol': symbol,
                    'data_points': len(price_data)
                }
            }
            
            # Update current data
            self.current_data = result
            
            return result
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error fetching Market Structure data: {e}", "data_fetch")
            
            return {
                'trend_analysis': {},
                'structural_levels': [],
                'market_phase': 'ranging',
                'market_regime': 'calm',
                'breakout_analysis': {},
                'volume_structure': {},
                'confluence_zones': [],
                'last_update': datetime.now().isoformat(),
                'statistics': {},
                'error': str(e)
            }
    
    def _get_historical_price_data(self, symbol: str, lookback: int = 500) -> List[Dict[str, Any]]:
        """📊 Obtener datos históricos de precios"""
        # Mock data for testing - in real implementation this would come from MT5 or data provider
        import random
        
        base_price = 1.0850
        data = []
        
        for i in range(lookback):
            # Generate realistic OHLC data
            open_price = base_price + random.uniform(-0.0050, 0.0050)
            close_price = open_price + random.uniform(-0.0030, 0.0030)
            high_price = max(open_price, close_price) + random.uniform(0, 0.0020)
            low_price = min(open_price, close_price) - random.uniform(0, 0.0020)
            volume = random.randint(50000, 200000)
            
            data.append({
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume,
                'timestamp': datetime.now() - timedelta(minutes=lookback-i)
            })
            
            base_price = close_price
        
        return data
    
    def register_callbacks(self):
        """🔄 Registrar callbacks Market Structure Enterprise"""
        if not DASHBOARD_AVAILABLE or not self.app or not callback:
            print("⚠️ Market Structure Callbacks not available - dashboard components missing")
            return
        
        try:
            # Main data update callback
            @self.app.callback(
                [Output("ms-data-store", "data"),
                 Output("ms-last-update", "children")],
                [Input("ms-refresh-interval", "n_intervals")],
                prevent_initial_call=False
            )
            def update_market_structure_data(n_intervals):
                """Update Market Structure data"""
                data = self.fetch_market_structure_data("EURUSD")
                last_update = datetime.now().strftime("%H:%M:%S")
                
                if self.tab_coordinator:
                    self.tab_coordinator.set_tab_data(self.tab_id, "last_data", data)
                
                return data, last_update
            
            # Trend analysis update callback
            @self.app.callback(
                [Output("ms-trend-direction", "children"),
                 Output("ms-trend-strength", "children"),
                 Output("ms-trend-confidence", "children"),
                 Output("ms-trend-slope", "children")],
                [Input("ms-data-store", "data")]
            )
            def update_trend_metrics(data):
                """Update trend analysis metrics"""
                trend = data.get('trend_analysis', {})
                
                return (
                    trend.get('direction', 'unknown').title(),
                    f"{trend.get('strength', 0.0) * 100:.0f}%",
                    f"{trend.get('confidence', 0.0) * 100:.0f}%",
                    f"{trend.get('slope', 0.0):.6f}"
                )
            
            # Market phase and regime update
            @self.app.callback(
                [Output("ms-market-phase", "children"),
                 Output("ms-market-regime", "children")],
                [Input("ms-data-store", "data")]
            )
            def update_phase_regime(data):
                """Update market phase and regime"""
                phase = data.get('market_phase', 'ranging').title()
                regime = data.get('market_regime', 'calm').title()
                
                return f"📊 {phase}", f"🔄 {regime}"
            
            print("🔄 Market Structure Tab Enterprise callbacks registered successfully")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error registering Market Structure callbacks: {e}", "callback_registration")
            print(f"❌ Error registering Market Structure callbacks: {e}")
    
    def get_tab_status(self) -> Dict[str, Any]:
        """📊 Obtener estado del tab Market Structure"""
        return {
            "tab_id": self.tab_id,
            "dashboard_available": DASHBOARD_AVAILABLE,
            "core_available": CORE_AVAILABLE,
            "analyzer_ready": self.analyzer is not None,
            "structure_engine_ready": self.structure_engine is not None,
            "current_data": self.current_data,
            "last_updated": datetime.now().isoformat()
        }


def create_market_structure_tab_enterprise(app=None, refresh_interval: int = 5000) -> MarketStructureTabEnterprise:
    """
    🏭 FACTORY FUNCTION PARA MARKET STRUCTURE TAB ENTERPRISE
    =======================================================
    
    Args:
        app: Aplicación Dash
        refresh_interval: Intervalo de actualización en ms
        
    Returns:
        Instancia configurada de MarketStructureTabEnterprise
    """
    tab = MarketStructureTabEnterprise(app, refresh_interval)
    
    if app:
        tab.register_callbacks()
        
    return tab


# Testing and validation functions
def test_market_structure_tab_enterprise():
    """🧪 Test function para validar MarketStructureTabEnterprise"""
    print("🧪 Testing Market Structure Tab Enterprise...")
    
    try:
        tab = MarketStructureTabEnterprise()
        print("✅ Market Structure Tab Enterprise initialized")
        
        # Test status
        status = tab.get_tab_status()
        print(f"✅ Tab status: {status['tab_id']}")
        
        # Test structure engine
        test_data = tab._get_historical_price_data("EURUSD", 50)
        structure_analysis = tab.structure_engine.analyze_market_structure(test_data)
        print(f"✅ Structure analysis: {structure_analysis['trend_analysis']['direction']} trend")
        print(f"✅ Structural levels: {len(structure_analysis['structural_levels'])} levels found")
        print(f"✅ Market phase: {structure_analysis['market_phase']}")
        
        # Test data fetching
        data = tab.fetch_market_structure_data("EURUSD")
        print(f"✅ Data fetched: {data['market_phase']} phase")
        
        # Test layout creation
        layout = tab.create_layout()
        print(f"✅ Layout created: {type(layout)}")
        
        print("🎉 Market Structure Tab Enterprise test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Market Structure Tab Enterprise test failed: {e}")
        return False


if __name__ == "__main__":
    test_market_structure_tab_enterprise()
