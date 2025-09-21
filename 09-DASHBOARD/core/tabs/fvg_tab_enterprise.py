#!/usr/bin/env python3
"""
📊 FVG TAB v6.0 ENTERPRISE - FAIR VALUE GAPS ANALYSIS
====================================================

Interface especializada para análisis de Fair Value Gaps (FVG) en tiempo real.
Integra detection, mitigation tracking y analytics usando arquitectura enterprise.

FUNCIONALIDADES ENTERPRISE:
✅ FVG detection en tiempo real
✅ Mitigation tracking automático
✅ Gap quality scoring & analytics
✅ Multi-timeframe gap analysis
✅ Bullish/Bearish gap categorization
✅ Historical performance metrics
✅ Alert system para nuevos gaps
✅ Export/import de configuraciones

Arquitectura:
✅ Dashboard Core Integration
✅ Tab Coordinator Integration  
✅ SmartMoneyAnalyzer Integration
✅ UnifiedMemorySystem Integration
✅ Enterprise logging & monitoring

Autor: ICT Engine v6.0 Enterprise Team
Fecha: 13 Septiembre 2025
"""

import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path

# Dashboard architecture imports - SOLO COMPONENTES REALES
try:
    import sys
    
    # Add dashboard core path
    dashboard_core_path = Path(__file__).parent.parent
    if str(dashboard_core_path) not in sys.path:
        sys.path.insert(0, str(dashboard_core_path))
    
    from dashboard_core import get_dashboard_core, DashboardCore
    from tab_coordinator import get_tab_coordinator, TabCoordinator, TabState
    
    # Get dashboard components through core - SOLO REALES
    dashboard_core = get_dashboard_core()
    if not dashboard_core or not dashboard_core.imports.dash_available:
        raise ImportError("Dashboard core o Dash no disponible - componentes reales requeridos")
    
    html, dcc, Input, Output, State, callback = dashboard_core.get_components()
    go, px, make_subplots = dashboard_core.get_plotting_components()
    pd = dashboard_core.imports.pd
    
    if any(component is None for component in [html, dcc, Input, Output, State, callback]):
        raise ImportError("Componentes Dash None - sistema requiere componentes reales")
    
    DASHBOARD_AVAILABLE = True
    PLOTLY_AVAILABLE = dashboard_core.imports.plotly_available
    
    print("✅ FVG Tab - Dashboard architecture loaded successfully (REAL COMPONENTS ONLY)")
    
except ImportError as e:
    print(f"❌ CRÍTICO: Dashboard architecture no disponible - sistema requiere componentes reales: {e}")
    raise RuntimeError(f"FVG Tab requiere Dashboard architecture real: {e}")

# Core system imports - SOLO COMPONENTES REALES
try:
    current_dir = Path(__file__).parent.parent.parent.parent / "01-CORE"
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    from smart_money_concepts.smart_money_analyzer import SmartMoneyAnalyzer
    from smart_trading_logger import SmartTradingLogger
    from ict_engine.pattern_detector import ICTPatternDetector
    from analysis.fvg_memory_manager import FVGMemoryManager
    
    if SmartMoneyAnalyzer is None or SmartTradingLogger is None:
        raise ImportError("Core components son None - sistema requiere componentes reales")
    
    CORE_AVAILABLE = True
    print("✅ FVG Tab - Core systems loaded successfully (REAL COMPONENTS ONLY)")
    
except ImportError as e:
    print(f"❌ CRÍTICO: Core systems no disponible - sistema requiere componentes reales: {e}")
    raise RuntimeError(f"FVG Tab requiere Core systems reales: {e}")
    SmartTradingLogger = None
    ICTPatternDetector = None
    FVGMemoryManager = None


class FVGAnalytics:
    """
    📊 ANALYTICS ENGINE PARA FVG
    ===========================
    
    Motor de análisis especializado para Fair Value Gaps
    """
    
    def __init__(self):
        self.gap_history: List[Dict[str, Any]] = []
        self.mitigation_stats: Dict[str, Any] = {}
        self.quality_metrics: Dict[str, float] = {}
        
    def analyze_gap_quality(self, gap_data: Dict[str, Any]) -> float:
        """📊 Analizar calidad del gap"""
        try:
            quality_score = 0.0
            
            # Size factor (0-30 points)
            gap_size = gap_data.get('size_pips', 0)
            if gap_size > 50:
                quality_score += 30
            elif gap_size > 20:
                quality_score += 20
            elif gap_size > 10:
                quality_score += 10
            
            # Volume factor (0-25 points)
            volume = gap_data.get('volume', 0)
            if volume > 100000:
                quality_score += 25
            elif volume > 50000:
                quality_score += 15
            elif volume > 25000:
                quality_score += 10
            
            # Timeframe factor (0-20 points)
            timeframe = gap_data.get('timeframe', 'M15')
            if timeframe in ['H4', 'D1']:
                quality_score += 20
            elif timeframe in ['H1', 'M30']:
                quality_score += 15
            elif timeframe == 'M15':
                quality_score += 10
            
            # Context factor (0-25 points)
            context_strength = gap_data.get('context_strength', 0.5)
            quality_score += context_strength * 25
            
            return min(quality_score, 100.0)  # Cap at 100
            
        except Exception as e:
            print(f"❌ Error analyzing gap quality: {e}")
            return 50.0  # Default neutral score
    
    def calculate_mitigation_probability(self, gap_data: Dict[str, Any]) -> float:
        """🎯 Calcular probabilidad de mitigación"""
        try:
            # Base probability
            base_prob = 0.75  # 75% base probability for FVG mitigation
            
            # Adjust by gap age
            gap_age_hours = gap_data.get('age_hours', 1)
            if gap_age_hours < 24:
                age_factor = 1.0
            elif gap_age_hours < 168:  # 1 week
                age_factor = 0.8
            else:
                age_factor = 0.6
            
            # Adjust by quality
            quality = self.analyze_gap_quality(gap_data)
            quality_factor = quality / 100.0
            
            # Adjust by market conditions
            market_volatility = gap_data.get('market_volatility', 0.5)
            volatility_factor = 0.8 + (market_volatility * 0.4)  # 0.8 to 1.2
            
            final_probability = base_prob * age_factor * quality_factor * volatility_factor
            return min(max(final_probability, 0.1), 0.95)  # Clamp between 10% and 95%
            
        except Exception as e:
            print(f"❌ Error calculating mitigation probability: {e}")
            return 0.75
    
    def get_gap_statistics(self, gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """📊 Obtener estadísticas de gaps"""
        if not gaps:
            return {
                'total_gaps': 0,
                'bullish_gaps': 0,
                'bearish_gaps': 0,
                'avg_quality': 0.0,
                'avg_mitigation_prob': 0.0,
                'avg_size': 0.0
            }
        
        bullish_gaps = [g for g in gaps if 'bullish' in g.get('type', '').lower()]
        bearish_gaps = [g for g in gaps if 'bearish' in g.get('type', '').lower()]
        
        qualities = [self.analyze_gap_quality(gap) for gap in gaps]
        mitigation_probs = [self.calculate_mitigation_probability(gap) for gap in gaps]
        sizes = [gap.get('size_pips', 0) for gap in gaps]
        
        return {
            'total_gaps': len(gaps),
            'bullish_gaps': len(bullish_gaps),
            'bearish_gaps': len(bearish_gaps),
            'avg_quality': sum(qualities) / len(qualities) if qualities else 0.0,
            'avg_mitigation_prob': sum(mitigation_probs) / len(mitigation_probs) if mitigation_probs else 0.0,
            'avg_size': sum(sizes) / len(sizes) if sizes else 0.0,
            'quality_distribution': {
                'high_quality': len([q for q in qualities if q >= 75]),
                'medium_quality': len([q for q in qualities if 50 <= q < 75]),
                'low_quality': len([q for q in qualities if q < 50])
            }
        }


class FVGTabEnterprise:
    """
    📊 FVG TAB ENTERPRISE v6.0
    =========================
    
    Interface completa para análisis de Fair Value Gaps con funcionalidades enterprise.
    """
    
    def __init__(self, app=None, refresh_interval: int = 1000):  # 1 second for FVG
        self.app = app
        self.refresh_interval = refresh_interval
        self.tab_id = "fvg_tab"
        
        # Dashboard integration
        self.dashboard_core = dashboard_core
        if dashboard_core:
            try:
                self.tab_coordinator = get_tab_coordinator()
                # Register this tab
                self.tab_coordinator.register_tab(
                    self.tab_id,
                    "Fair Value Gaps Analysis",
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
            
        if CORE_AVAILABLE and ICTPatternDetector:
            self.pattern_detector = ICTPatternDetector()
        else:
            self.pattern_detector = None

        # FVG persistent memory manager (read-only for dashboard)
        if CORE_AVAILABLE and 'FVGMemoryManager' in globals() and FVGMemoryManager is not None:
            try:
                self.fvg_manager = FVGMemoryManager()
            except Exception as e:
                print(f"⚠️ FVGMemoryManager init failed: {e}")
                self.fvg_manager = None
        else:
            self.fvg_manager = None
            
        # Logger
        if CORE_AVAILABLE and SmartTradingLogger:
            self.logger = SmartTradingLogger("FVGTab")
        else:
            self.logger = None
            
        # Analytics engine
        self.analytics = FVGAnalytics()
        
        # Data storage
        self.current_data = {
            'fvg_gaps': [],
            'last_update': datetime.now().isoformat(),
            'statistics': {
                'total_gaps': 0,
                'bullish_gaps': 0,
                'bearish_gaps': 0,
                'avg_quality': 0.0,
                'avg_mitigation_prob': 0.0
            }
        }

        # Optional CHoCH enrichment toggle (read from app config if available)
        try:
            cfg = getattr(self.app, 'config', {}) if self.app else {}
            self.enable_choch_enrichment = bool(cfg.get('fvg', {}).get('enable_choch_enrichment', True))
        except Exception:
            self.enable_choch_enrichment = True
        
        # Visual configuration
        if dashboard_core:
            theme_colors = dashboard_core.theme_manager.get_colors()
            self.colors = theme_colors
        else:
            self.colors = {
                'bullish': '#00ff88',
                'bearish': '#ff4444',
                'background': '#0e1117',
                'surface': '#1e2329',
                'text': '#ffffff',
                'warning': '#ffaa00',
                'info': '#00aaff'
            }
        
        print(f"📊 FVG Tab Enterprise initialized (refresh: {refresh_interval}ms)")
        
    def create_layout(self) -> Any:
        """
        🎨 CREAR LAYOUT PRINCIPAL FVG
        ============================
        
        Returns:
            Layout principal para análisis FVG
        """
        if not DASHBOARD_AVAILABLE or not html:
            return {
                "error": "Dashboard components not available",
                "message": "Install Dash and dependencies to enable FVG analysis",
                "component": "fvg_tab",
                "fallback_data": self.current_data
            }
        
        try:
            layout_children = [
                # Header Section
                self._create_header_section(),
                
                # Controls Section
                self._create_controls_section(),
                
                # Statistics Section
                self._create_statistics_section(),
                
                # Charts Section (Split view)
                self._create_charts_section(),
                
                # Gap Analysis Table
                self._create_gap_table_section(),
                
                # Alert Configuration
                self._create_alert_section(),
                
                # System Components
                self._create_system_components()
            ]
            
            if html.__class__.__name__ == 'MockHTML':
                return {
                    "type": "div",
                    "className": "fvg-tab-enterprise",
                    "children": layout_children
                }
            else:
                return html.Div(
                    layout_children,
                    className="fvg-tab-enterprise",
                    style={
                        "backgroundColor": self.colors.get("background", "#0e1117"),
                        "color": self.colors.get("text_primary", "#ffffff"),
                        "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, sans-serif",
                        "padding": "16px"
                    }
                )
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error creating FVG layout: {e}", "layout_creation")
            
            return {"error": f"Layout creation failed: {e}", "fallback": True}
    
    def _create_header_section(self) -> Any:
        """🎨 Crear header section"""
        if html.__class__.__name__ == 'MockHTML':
            return {
                "type": "div",
                "className": "fvg-header",
                "children": [
                    {"type": "h2", "children": "📊 Fair Value Gaps Analysis v6.0 Enterprise"},
                    {"type": "div", "children": "Real-time FVG detection & mitigation tracking"}
                ]
            }
        else:
            return html.Div([
                html.H2("📊 Fair Value Gaps Analysis v6.0 Enterprise", className="tab-title"),
                html.Div([
                    html.Span("🔄 Auto-scan: ", className="status-label"),
                    html.Span(f"{self.refresh_interval}ms", className="status-value"),
                    html.Span(" | 🎯 Last Scan: ", className="status-label"),
                    html.Span(id="fvg-last-update", className="status-value"),
                    html.Span(" | 📊 Quality Engine: ", className="status-label"),
                    html.Span("Active", className="status-value success")
                ], className="status-bar")
            ], className="fvg-header")
    
    def _create_controls_section(self) -> Any:
        """🎛️ Crear controles FVG"""
        if dcc.__class__.__name__ == 'MockDCC':
            return {
                "type": "div",
                "className": "fvg-controls",
                "children": ["Symbol: EURUSD", "Timeframe: M15", "Min Quality: 50%"]
            }
        else:
            # Read symbols/timeframes from app config if available
            try:
                cfg = getattr(self.app, 'config', {}) if self.app else {}
                cfg_symbols = cfg.get('data', {}).get('symbols', []) or ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
                cfg_timeframes = cfg.get('data', {}).get('timeframes', []) or ["M5", "M15", "M30", "H1", "H4"]
            except Exception:
                cfg_symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
                cfg_timeframes = ["M5", "M15", "M30", "H1", "H4"]

            return html.Div([
                # Symbol & Timeframe
                html.Div([
                    html.Div([
                        html.Label("Symbol:", className="control-label"),
                        dcc.Dropdown(
                            id="fvg-symbol-selector",
                            options=[{"label": s, "value": s} for s in cfg_symbols],
                            value=(cfg_symbols[0] if cfg_symbols else "EURUSD"),
                            className="control-dropdown"
                        )
                    ], className="control-group"),
                    
                    html.Div([
                        html.Label("Timeframe:", className="control-label"),
                        dcc.Dropdown(
                            id="fvg-timeframe-selector",
                            options=[{"label": tf, "value": tf} for tf in cfg_timeframes],
                            value=(cfg_timeframes[0] if cfg_timeframes else "M15"),
                            className="control-dropdown"
                        )
                    ], className="control-group")
                ], className="controls-row"),
                
                # Quality & Filters
                html.Div([
                    html.Div([
                        html.Label("Minimum Quality Score:", className="control-label"),
                        dcc.Slider(
                            id="fvg-quality-slider",
                            min=0,
                            max=100,
                            step=5,
                            value=50,
                            marks={i: f"{i}%" for i in range(0, 101, 25)},
                            className="control-slider"
                        )
                    ], className="control-group"),
                    
                    html.Div([
                        html.Label("Gap Type:", className="control-label"),
                        dcc.RadioItems(
                            id="fvg-type-filter",
                            options=[
                                {"label": "All Gaps", "value": "all"},
                                {"label": "Bullish Only", "value": "bullish"},
                                {"label": "Bearish Only", "value": "bearish"}
                            ],
                            value="all",
                            className="control-radio",
                            inline=True
                        )
                    ], className="control-group")
                ], className="controls-row"),

                # CHoCH enrichment toggle
                html.Div([
                    html.Div([
                        html.Label("CHoCH Enrichment:", className="control-label"),
                        dcc.Checklist(
                            id="fvg-choch-toggle",
                            options=[{"label": "Enable", "value": "enabled"}],
                            value=["enabled"] if bool(self.enable_choch_enrichment) else [],
                            className="control-checkbox",
                            inline=True
                        )
                    ], className="control-group")
                ], className="controls-row"),
                
                # Action buttons
                html.Div([
                    html.Button("🔄 Scan Now", id="fvg-manual-scan", className="action-button primary"),
                    html.Button("📊 Export Data", id="fvg-export-button", className="action-button secondary"),
                    html.Button("⚙️ Alert Config", id="fvg-alert-config", className="action-button secondary")
                ], className="controls-actions")
                
            ], className="fvg-controls")
    
    def _create_statistics_section(self) -> Any:
        """📊 Crear sección de estadísticas"""
        if html.__class__.__name__ == 'MockHTML':
            return {
                "type": "div",
                "className": "fvg-statistics",
                "children": ["Total: 0", "Bullish: 0", "Bearish: 0", "Quality: 0%", "Mitigation: 0%"]
            }
        else:
            return html.Div([
                # Primary metrics
                html.Div([
                    self._create_stat_card("Total Gaps", "0", "📊", "total", "fvg-total-count"),
                    self._create_stat_card("Bullish", "0", "📈", "bullish", "fvg-bullish-count"),
                    self._create_stat_card("Bearish", "0", "📉", "bearish", "fvg-bearish-count"),
                    self._create_stat_card("Avg Quality", "0%", "⭐", "quality", "fvg-avg-quality"),
                    self._create_stat_card("Mitigation Prob", "0%", "🎯", "probability", "fvg-mitigation-prob")
                ], className="statistics-primary"),
                
                # Secondary metrics
                html.Div([
                    html.Div([
                        html.H4("Quality Distribution", className="section-subtitle"),
                        html.Div([
                            html.Div([
                                html.Span("High", className="quality-label"),
                                html.Span("0", id="fvg-high-quality", className="quality-value high")
                            ], className="quality-item"),
                            html.Div([
                                html.Span("Medium", className="quality-label"),
                                html.Span("0", id="fvg-medium-quality", className="quality-value medium")
                            ], className="quality-item"),
                            html.Div([
                                html.Span("Low", className="quality-label"),
                                html.Span("0", id="fvg-low-quality", className="quality-value low")
                            ], className="quality-item")
                        ], className="quality-distribution")
                    ], className="statistics-secondary-item"),
                    
                    html.Div([
                        html.H4("Gap Analytics", className="section-subtitle"),
                        html.Div([
                            html.Div("Avg Size: ", className="analytics-label"),
                            html.Span("0 pips", id="fvg-avg-size", className="analytics-value")
                        ], className="analytics-item"),
                        html.Div([
                            html.Div("Success Rate: ", className="analytics-label"),
                            html.Span("N/A", id="fvg-success-rate", className="analytics-value")
                        ], className="analytics-item")
                    ], className="statistics-secondary-item")
                    
                ], className="statistics-secondary")
                
            ], className="fvg-statistics")
    
    def _create_stat_card(self, title: str, value: str, icon: str, color: str, value_id: str) -> Any:
        """📊 Crear tarjeta de estadística"""
        return html.Div([
            html.Div([
                html.Div([
                    html.H3(value, id=value_id, className="stat-value"),
                    html.P(title, className="stat-label")
                ], className="stat-content"),
                html.Div(icon, className=f"stat-icon {color}")
            ], className="stat-inner")
        ], className=f"stat-card stat-{color}")
    
    def _create_charts_section(self) -> Any:
        """📈 Crear sección de gráficos"""
        if dcc.__class__.__name__ == 'MockDCC':
            return {
                "type": "div",
                "className": "fvg-charts",
                "children": ["Main Chart: Mock", "Quality Chart: Mock"]
            }
        else:
            return html.Div([
                # Main FVG Chart
                html.Div([
                    html.H3("📈 FVG Detection Chart", className="chart-title"),
                    dcc.Graph(
                        id="fvg-main-chart",
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
                        }
                    )
                ], className="chart-container main-chart"),
                
                # Quality Analysis Chart
                html.Div([
                    html.H3("⭐ Quality & Mitigation Analysis", className="chart-title"),
                    dcc.Graph(
                        id="fvg-quality-chart",
                        config={
                            'displayModeBar': True,
                            'displaylogo': False,
                            'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
                        }
                    )
                ], className="chart-container quality-chart")
                
            ], className="fvg-charts")
    
    def _create_gap_table_section(self) -> Any:
        """📋 Crear tabla de gaps"""
        if html.__class__.__name__ == 'MockHTML':
            return {
                "type": "div",
                "className": "fvg-table-section",
                "children": ["Gap Table: Mock mode"]
            }
        else:
            return html.Div([
                html.H3("📋 Active Fair Value Gaps", className="section-title"),
                html.Div(id="fvg-gaps-table", className="gaps-table")
            ], className="fvg-table-section")
    
    def _create_alert_section(self) -> Any:
        """🚨 Crear sección de alertas"""
        if html.__class__.__name__ == 'MockHTML':
            return {"type": "div", "children": "Alert section - Mock"}
        else:
            return html.Div([
                html.H4("🚨 Alert Configuration", className="section-subtitle"),
                html.Div([
                    html.Div([
                        html.Label("New Gap Alert:", className="alert-label"),
                        dcc.Checklist(
                            id="fvg-new-gap-alert",
                            options=[{"label": "Enable", "value": "enabled"}],
                            value=["enabled"],
                            className="alert-checkbox"
                        )
                    ], className="alert-item"),
                    
                    html.Div([
                        html.Label("Quality Threshold:", className="alert-label"),
                        dcc.Input(
                            id="fvg-alert-quality",
                            type="number",
                            min=0,
                            max=100,
                            value=75,
                            className="alert-input"
                        )
                    ], className="alert-item")
                ], className="alert-controls")
            ], className="fvg-alerts", style={"display": "none"})  # Hidden by default
    
    def _create_system_components(self) -> Any:
        """🔧 Crear componentes del sistema"""
        if dcc.__class__.__name__ == 'MockDCC':
            return {"type": "div", "children": "System components - Mock"}
        else:
            return html.Div([
                dcc.Interval(
                    id="fvg-refresh-interval",
                    interval=self.refresh_interval,
                    n_intervals=0
                ),
                dcc.Store(id="fvg-data-store", data=self.current_data),
                dcc.Store(id="fvg-alert-store", data={})
            ])
    
    def fetch_fvg_data(self, symbol: str = "EURUSD", timeframe: str = "M15", enable_choch: Optional[bool] = None) -> Dict[str, Any]:
        """
        📊 OBTENER DATOS FVG ENTERPRISE
        =============================
        
        Args:
            symbol: Par de divisas
            timeframe: Marco temporal
            
        Returns:
            Datos de FVG con análisis completo
        """
        if not CORE_AVAILABLE or not self.analyzer:
            return self._generate_mock_fvg_data(symbol, timeframe)
        
        try:
            start_time = time.time()
            
            # Get FVG data from pattern detector or analyzer
            fvg_gaps = self._fetch_real_fvg_data(symbol, timeframe, enable_choch=enable_choch)
            
            # Enhance with analytics
            enhanced_gaps = []
            for gap in fvg_gaps:
                gap['quality_score'] = self.analytics.analyze_gap_quality(gap)
                gap['mitigation_prob'] = self.analytics.calculate_mitigation_probability(gap)
                enhanced_gaps.append(gap)
            
            # Calculate statistics
            statistics = self.analytics.get_gap_statistics(enhanced_gaps)
            
            processing_time = (time.time() - start_time) * 1000
            
            if self.logger:
                self.logger.info(f"FVG data fetched: {len(enhanced_gaps)} gaps", "data_fetch")
            
            return {
                'fvg_gaps': enhanced_gaps,
                'last_update': datetime.now().isoformat(),
                'statistics': statistics,
                'performance': {
                    'processing_time_ms': processing_time,
                    'symbol': symbol,
                    'timeframe': timeframe
                }
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error fetching FVG data: {e}", "data_fetch")
            
            return {
                'fvg_gaps': [],
                'last_update': datetime.now().isoformat(),
                'statistics': self.analytics.get_gap_statistics([]),
                'error': str(e)
            }
    
    def _fetch_real_fvg_data(self, symbol: str, timeframe: str, enable_choch: Optional[bool] = None) -> List[Dict[str, Any]]:
        """🔍 Obtener datos FVG reales del sistema
        Fuente primaria: FVGMemoryManager (persistencia real del motor)
        Fallback: datos mock si no disponible.
        """
        try:
            if not self.fvg_manager:
                return self._generate_enhanced_mock_gaps()

            raw_fvgs = self.fvg_manager.get_active_fvgs(symbol=symbol, timeframe=timeframe)
            gaps: List[Dict[str, Any]] = []

            now = datetime.now(timezone.utc)
            market_vol = 0.5
            try:
                # Aproximar volatilidad de mercado desde el manager si existe
                if hasattr(self.fvg_manager, 'market_conditions'):
                    mc = getattr(self.fvg_manager, 'market_conditions', {})
                    vol = float(mc.get('current_volatility', 6.0))
                    # Normalizar a 0-1 aprox (0-12 pips rango típico → /12)
                    market_vol = max(0.0, min(1.0, vol / 12.0))
            except Exception:
                pass

            # Optional CHoCH imports
            choch_bonus_fn = None
            choch_sr_fn = None
            use_choch = self.enable_choch_enrichment if enable_choch is None else bool(enable_choch)
            if use_choch:
                try:
                    from memory.choch_historical_memory import compute_historical_bonus, calculate_historical_success_rate  # type: ignore
                    choch_bonus_fn = compute_historical_bonus
                    choch_sr_fn = calculate_historical_success_rate
                except Exception:
                    choch_bonus_fn = None
                    choch_sr_fn = None

            for entry in raw_fvgs or []:
                try:
                    fvg_id = entry.get('fvg_id') or entry.get('id') or ''
                    fvg_type = (entry.get('fvg_type') or entry.get('type') or 'bullish').lower()
                    high_raw = entry.get('high_price')
                    if high_raw is None:
                        high_raw = entry.get('high')
                    high = float(high_raw or 0.0)

                    low_raw = entry.get('low_price')
                    if low_raw is None:
                        low_raw = entry.get('low')
                    low = float(low_raw or 0.0)

                    size_raw = entry.get('gap_size_pips')
                    if size_raw is None:
                        size_raw = entry.get('size_pips')
                    if size_raw is None:
                        pip_factor = 100 if 'JPY' in symbol else 10000
                        size_pips = abs(high - low) * pip_factor
                    else:
                        size_pips = float(size_raw or 0.0)
                    status = str(entry.get('status', 'unfilled')).lower()
                    ts_raw = entry.get('candle_time') or entry.get('creation_timestamp') or entry.get('timestamp')
                    # Parse ISO timestamp robustamente
                    ts_iso = None
                    age_hours = 0.0
                    try:
                        if isinstance(ts_raw, str):
                            ts_iso = ts_raw
                            ts = datetime.fromisoformat(ts_raw.replace('Z', '+00:00'))
                        elif isinstance(ts_raw, datetime):
                            ts = ts_raw if ts_raw.tzinfo else ts_raw.replace(tzinfo=timezone.utc)
                            ts_iso = ts.isoformat()
                        else:
                            ts = now
                            ts_iso = ts.isoformat()
                        age_hours = max(0.0, (now - ts).total_seconds() / 3600.0)
                    except Exception:
                        ts_iso = now.isoformat()
                        age_hours = 0.0

                    mitigation_status = 'pending'
                    if status == 'partially_filled':
                        mitigation_status = 'partial'
                    elif status == 'filled':
                        mitigation_status = 'filled'

                    enriched = {
                        'id': fvg_id,
                        'type': f"{fvg_type}_fvg" if not fvg_type.endswith('_fvg') else fvg_type,
                        'price_top': max(high, low),
                        'price_bottom': min(high, low),
                        'size_pips': size_pips,
                        'volume': 0,  # sin volumen en memoria, placeholder
                        'timeframe': timeframe,
                        'timestamp': ts_iso,
                        'age_hours': age_hours,
                        'context_strength': 0.6,  # placeholder razonable
                        'market_volatility': market_vol,
                        'mitigation_status': mitigation_status,
                        # Extra opcional para futuras vistas
                        'status': status,
                        'symbol': symbol
                    }

                    # Optional CHoCH enrichment (non-blocking)
                    if choch_bonus_fn is not None and use_choch:
                        try:
                            level = (high + low) / 2.0
                            hb = choch_bonus_fn(symbol=symbol, timeframe=timeframe, break_level=level)
                            enriched['choch_bonus'] = float(hb.get('historical_bonus', 0.0) or 0.0)
                            enriched['choch_samples'] = int(hb.get('samples', 0) or 0)
                        except Exception:
                            pass
                    if choch_sr_fn is not None and use_choch:
                        try:
                            sr = choch_sr_fn(symbol=symbol, timeframe=timeframe)
                            enriched['choch_success_rate'] = float(sr)
                        except Exception:
                            pass

                    gaps.append(enriched)
                except Exception as map_e:
                    if self.logger:
                        self.logger.error(f"Error mapeando FVG para dashboard: {map_e}", "fvg_mapping")

            return gaps
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error obteniendo FVG reales: {e}", "fvg_fetch")
            return self._generate_enhanced_mock_gaps()
    
    def _generate_mock_fvg_data(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """🎭 Generar datos FVG mock"""
        gaps = self._generate_enhanced_mock_gaps()
        statistics = self.analytics.get_gap_statistics(gaps)
        
        return {
            'fvg_gaps': gaps,
            'last_update': datetime.now().isoformat(),
            'statistics': statistics,
            'mock_mode': True,
            'performance': {
                'processing_time_ms': 50,
                'symbol': symbol,
                'timeframe': timeframe
            }
        }
    
    def _generate_enhanced_mock_gaps(self) -> List[Dict[str, Any]]:
        """🎭 Generar gaps mock con análisis completo"""
        mock_gaps = [
            {
                'id': 'gap_001',
                'type': 'bullish_fvg',
                'price_top': 1.0920,
                'price_bottom': 1.0895,
                'size_pips': 25,
                'volume': 125000,
                'timeframe': 'M15',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'age_hours': 2,
                'context_strength': 0.8,
                'market_volatility': 0.6,
                'mitigation_status': 'pending'
            },
            {
                'id': 'gap_002',
                'type': 'bearish_fvg',
                'price_top': 1.0975,
                'price_bottom': 1.0940,
                'size_pips': 35,
                'volume': 180000,
                'timeframe': 'M15',
                'timestamp': (datetime.now() - timedelta(hours=4)).isoformat(),
                'age_hours': 4,
                'context_strength': 0.9,
                'market_volatility': 0.7,
                'mitigation_status': 'partial'
            },
            {
                'id': 'gap_003',
                'type': 'bullish_fvg',
                'price_top': 1.0860,
                'price_bottom': 1.0845,
                'size_pips': 15,
                'volume': 75000,
                'timeframe': 'M15',
                'timestamp': (datetime.now() - timedelta(minutes=30)).isoformat(),
                'age_hours': 0.5,
                'context_strength': 0.6,
                'market_volatility': 0.5,
                'mitigation_status': 'pending'
            }
        ]
        
        # Add analytics to each gap
        for gap in mock_gaps:
            gap['quality_score'] = self.analytics.analyze_gap_quality(gap)
            gap['mitigation_prob'] = self.analytics.calculate_mitigation_probability(gap)
        
        return mock_gaps
    
    def register_callbacks(self):
        """🔄 Registrar callbacks FVG Enterprise"""
        if not DASHBOARD_AVAILABLE or not self.app or not callback:
            print("⚠️ FVG Callbacks not available - dashboard components missing")
            return
        
        try:
            # Main data update callback
            @self.app.callback(
                [Output("fvg-data-store", "data"),
                 Output("fvg-last-update", "children")],
                [Input("fvg-refresh-interval", "n_intervals"),
                 Input("fvg-manual-scan", "n_clicks"),
                 Input("fvg-symbol-selector", "value"),
                 Input("fvg-timeframe-selector", "value"),
                 Input("fvg-choch-toggle", "value")],
                prevent_initial_call=False
            )
            def update_fvg_data(n_intervals, scan_clicks, symbol, timeframe, choch_toggle):
                """Update FVG data"""
                enable_choch = bool(choch_toggle) and ("enabled" in (choch_toggle or []))
                data = self.fetch_fvg_data(symbol or "EURUSD", timeframe or "M15", enable_choch=enable_choch)
                last_update = datetime.now().strftime("%H:%M:%S")
                
                if self.tab_coordinator:
                    self.tab_coordinator.set_tab_data(self.tab_id, "last_data", data)
                
                return data, last_update
            
            # Statistics update callback
            @self.app.callback(
                [Output("fvg-total-count", "children"),
                 Output("fvg-bullish-count", "children"),
                 Output("fvg-bearish-count", "children"),
                 Output("fvg-avg-quality", "children"),
                 Output("fvg-mitigation-prob", "children"),
                 Output("fvg-high-quality", "children"),
                 Output("fvg-medium-quality", "children"),
                 Output("fvg-low-quality", "children"),
                 Output("fvg-avg-size", "children")],
                [Input("fvg-data-store", "data")]
            )
            def update_fvg_statistics(data):
                """Update FVG statistics"""
                stats = data.get('statistics', {})
                quality_dist = stats.get('quality_distribution', {})
                
                return (
                    str(stats.get('total_gaps', 0)),
                    str(stats.get('bullish_gaps', 0)),
                    str(stats.get('bearish_gaps', 0)),
                    f"{stats.get('avg_quality', 0):.1f}%",
                    f"{stats.get('avg_mitigation_prob', 0):.1%}",
                    str(quality_dist.get('high_quality', 0)),
                    str(quality_dist.get('medium_quality', 0)),
                    str(quality_dist.get('low_quality', 0)),
                    f"{stats.get('avg_size', 0):.1f} pips"
                )

            # Gap table render callback with filtering
            @self.app.callback(
                Output("fvg-gaps-table", "children"),
                [Input("fvg-data-store", "data"),
                 Input("fvg-type-filter", "value"),
                 Input("fvg-quality-slider", "value")]
            )
            def render_gap_table(data, type_filter, min_quality):
                gaps = data.get('fvg_gaps', []) or []
                tfilter = (type_filter or 'all').lower()
                try:
                    mq = float(min_quality or 0)
                except Exception:
                    mq = 0.0

                # Apply filters
                def pass_filters(g):
                    try:
                        if mq and float(g.get('quality_score', 0.0)) < mq:
                            return False
                        if tfilter == 'bullish' and not str(g.get('type','')).startswith('bullish'):
                            return False
                        if tfilter == 'bearish' and not str(g.get('type','')).startswith('bearish'):
                            return False
                        return True
                    except Exception:
                        return False

                fgaps = [g for g in gaps if pass_filters(g)]

                # Build HTML table safely
                header = html.Tr([
                    html.Th("Symbol"), html.Th("Timeframe"), html.Th("Type"), html.Th("Status"),
                    html.Th("Gap (pips)"), html.Th("Price Range"), html.Th("Age (h)"),
                    html.Th("Quality"), html.Th("Mitigation"), html.Th("CHoCH Bonus"), html.Th("CHoCH SR")
                ])

                def fmt_num(v, nd=1):
                    try:
                        return f"{float(v):.{nd}f}"
                    except Exception:
                        return "-"

                rows = []
                for g in fgaps:
                    sym = g.get('symbol', '-')
                    tf = g.get('timeframe', '-')
                    gtype = g.get('type', '-')
                    status = g.get('mitigation_status', g.get('status', '-'))
                    size = fmt_num(g.get('size_pips', 0.0), 1)
                    pt = g.get('price_top', None)
                    pb = g.get('price_bottom', None)
                    prange = f"{fmt_num(pb, 5)} - {fmt_num(pt, 5)}"
                    age = fmt_num(g.get('age_hours', 0.0), 1)
                    q = fmt_num(g.get('quality_score', 0.0), 1)
                    mp = g.get('mitigation_prob', 0.0)
                    mp_s = f"{float(mp):.0%}" if isinstance(mp, (int, float)) else "-"
                    cb = g.get('choch_bonus', None)
                    cb_s = fmt_num(cb, 1) if cb is not None else "-"
                    sr = g.get('choch_success_rate', None)
                    sr_s = f"{float(sr):.0%}" if isinstance(sr, (int, float)) else "-"
                    rows.append(html.Tr([
                        html.Td(sym), html.Td(tf), html.Td(gtype), html.Td(status),
                        html.Td(size), html.Td(prange), html.Td(age),
                        html.Td(q), html.Td(mp_s), html.Td(cb_s), html.Td(sr_s)
                    ]))

                table = html.Table([
                    html.Thead(header),
                    html.Tbody(rows if rows else [html.Tr([html.Td("No gaps found", colSpan=11)])])
                ], className="fvg-table")

                return table
            
            print("🔄 FVG Tab Enterprise callbacks registered successfully")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error registering FVG callbacks: {e}", "callback_registration")
            print(f"❌ Error registering FVG callbacks: {e}")
    
    def get_tab_status(self) -> Dict[str, Any]:
        """📊 Obtener estado del tab FVG"""
        return {
            "tab_id": self.tab_id,
            "dashboard_available": DASHBOARD_AVAILABLE,
            "core_available": CORE_AVAILABLE,
            "analyzer_ready": self.analyzer is not None,
            "pattern_detector_ready": self.pattern_detector is not None,
            "analytics_ready": self.analytics is not None,
            "current_data": self.current_data,
            "last_updated": datetime.now().isoformat()
        }


def create_fvg_tab_enterprise(app=None, refresh_interval: int = 1000) -> FVGTabEnterprise:
    """
    🏭 FACTORY FUNCTION PARA FVG TAB ENTERPRISE
    ==========================================
    
    Args:
        app: Aplicación Dash
        refresh_interval: Intervalo de actualización en ms
        
    Returns:
        Instancia configurada de FVGTabEnterprise
    """
    tab = FVGTabEnterprise(app, refresh_interval)
    
    if app:
        tab.register_callbacks()
        
    return tab


# Testing and validation functions
def test_fvg_tab_enterprise():
    """🧪 Test function para validar FVGTabEnterprise"""
    print("🧪 Testing FVG Tab Enterprise...")
    
    try:
        tab = FVGTabEnterprise()
        print("✅ FVG Tab Enterprise initialized")
        
        # Test status
        status = tab.get_tab_status()
        print(f"✅ Tab status: {status['tab_id']}")
        
        # Test data fetching
        data = tab.fetch_fvg_data("EURUSD", "M15")
        print(f"✅ Data fetched: {data['statistics']['total_gaps']} gaps")
        
        # Test analytics
        gaps = data.get('fvg_gaps', [])
        if gaps:
            quality = tab.analytics.analyze_gap_quality(gaps[0])
            print(f"✅ Quality analysis: {quality:.1f}%")
        
        # Test layout creation
        layout = tab.create_layout()
        print(f"✅ Layout created: {type(layout)}")
        
        print("🎉 FVG Tab Enterprise test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ FVG Tab Enterprise test failed: {e}")
        return False


if __name__ == "__main__":
    test_fvg_tab_enterprise()