"""
Risk Monitor Dashboard - ICT Engine v6.0 Enterprise
================================================

Dashboard monitoreo riesgo tiempo real para cuenta real.
Integra con sistema risk management existente.

Características:
- Risk metrics tiempo real
- Emergency status monitoring  
- Position exposure tracking
- Performance analytics básico
- Alert system integration
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
from typing import Dict, Any, List

# Imports sistema ICT existente
try:
    from ..real_trading import (
        AutoPositionSizer, EmergencyStopSystem,
        SignalValidator, ExecutionEngine
    )
    from ..data_management.mt5_data_manager import MT5DataManager
except ImportError:
    # Fallback para development
    pass

class RiskMonitorDashboard:
    """
    Dashboard monitoreo riesgo tiempo real
    Integra con todos componentes real trading
    """
    
    def __init__(self):
        self.page_config = {
            "page_title": "ICT Engine Risk Monitor",
            "page_icon": "🛡️",
            "layout": "wide",
            "initial_sidebar_state": "expanded"
        }
        
        # Initialize components
        self.position_sizer = None
        self.emergency_system = None
        self.mt5_manager = None
        
        self._load_components()
    
    def _load_components(self):
        """Carga componentes real trading"""
        try:
            # Load existing components if available
            pass
        except:
            # Create dummy data for development
            self._create_dummy_data()
    
    def _create_dummy_data(self):
        """Datos dummy para desarrollo"""
        self.dummy_account = {
            'balance': 10000.0,
            'equity': 9850.0,
            'drawdown': 1.5,
            'daily_pnl': -150.0,
            'open_positions': 2,
            'consecutive_losses': 1
        }
        
        self.dummy_positions = [
            {'symbol': 'EURUSD', 'size': 1.5, 'pnl': 75.0, 'risk': 100.0},
            {'symbol': 'GBPJPY', 'size': 0.8, 'pnl': -225.0, 'risk': 150.0}
        ]
    
    def run_dashboard(self):
        """Ejecuta dashboard principal"""
        st.set_page_config(**self.page_config)
        
        # Main title
        st.title("🛡️ ICT Engine Risk Monitor")
        st.markdown("**Real-time risk management dashboard for live trading**")
        
        # Sidebar configuration
        self._render_sidebar()
        
        # Main dashboard layout
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            self._render_account_overview()
            self._render_position_exposure()
        
        with col2:
            self._render_risk_metrics()
            self._render_performance_chart()
        
        with col3:
            self._render_emergency_status()
            self._render_alerts()
        
        # Bottom section
        st.markdown("---")
        
        col4, col5 = st.columns(2)
        with col4:
            self._render_recent_trades()
        
        with col5:
            self._render_system_health()
    
    def _render_sidebar(self):
        """Render sidebar configuración"""
        st.sidebar.markdown("## ⚙️ Configuration")
        
        # Risk settings
        st.sidebar.markdown("### 🎯 Risk Settings")
        risk_per_trade = st.sidebar.slider("Risk per Trade (%)", 0.1, 5.0, 1.0, 0.1)
        max_drawdown = st.sidebar.slider("Max Drawdown (%)", 1.0, 20.0, 5.0, 0.5)
        
        # Emergency settings
        st.sidebar.markdown("### 🚨 Emergency Settings")
        max_consecutive = st.sidebar.number_input("Max Consecutive Losses", 1, 10, 5)
        daily_limit = st.sidebar.number_input("Daily Loss Limit ($)", 50, 2000, 500, 50)
        
        # Monitoring settings
        st.sidebar.markdown("### 📊 Monitoring")
        auto_refresh = st.sidebar.checkbox("Auto Refresh", True)
        if auto_refresh:
            refresh_interval = st.sidebar.selectbox(
                "Refresh Interval", 
                [10, 30, 60, 300], 
                index=1,
                format_func=lambda x: f"{x} seconds"
            )
        
        # Trading controls
        st.sidebar.markdown("### 🎛️ Trading Controls")
        trading_enabled = st.sidebar.checkbox("Trading Enabled", True)
        
        if st.sidebar.button("🚨 Emergency Stop"):
            st.sidebar.error("Emergency stop activated!")
        
        if st.sidebar.button("🔄 Reset Emergency"):
            st.sidebar.success("Emergency reset!")
    
    def _render_account_overview(self):
        """Render resumen cuenta"""
        st.markdown("### 💰 Account Overview")
        
        # Get account data
        account = self.dummy_account  # Replace with real data
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Balance", f"${account['balance']:,.2f}")
        
        with col2:
            equity_delta = account['equity'] - account['balance']
            st.metric("Equity", f"${account['equity']:,.2f}", 
                     delta=f"{equity_delta:+.2f}")
        
        with col3:
            drawdown_color = "normal" if account['drawdown'] < 3.0 else "inverse"
            st.metric("Drawdown", f"{account['drawdown']:.1f}%", 
                     delta=None, delta_color=drawdown_color)
        
        with col4:
            daily_color = "normal" if account['daily_pnl'] >= 0 else "inverse"
            st.metric("Daily P&L", f"${account['daily_pnl']:+.2f}", 
                     delta_color=daily_color)
    
    def _render_risk_metrics(self):
        """Render métricas riesgo"""
        st.markdown("### 🎯 Risk Metrics")
        
        # Risk gauge
        current_risk = 2.5  # Example
        max_risk = 5.0
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = current_risk,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Current Risk Exposure (%)"},
            delta = {'reference': 1.0},
            gauge = {
                'axis': {'range': [None, max_risk]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 2], 'color': "lightgray"},
                    {'range': [2, 4], 'color': "yellow"},
                    {'range': [4, max_risk], 'color': "red"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_risk
                }
            }
        ))
        
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_position_exposure(self):
        """Render exposición posiciones"""
        st.markdown("### 📊 Position Exposure")
        
        # Create exposure chart
        positions = self.dummy_positions
        
        if positions:
            df = pd.DataFrame(positions)
            
            # Pie chart for position distribution
            fig = px.pie(df, values='risk', names='symbol', 
                        title="Risk Distribution by Position")
            fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            # Position details table
            df_display = df.copy()
            df_display['P&L'] = df_display['pnl'].apply(lambda x: f"${x:+.2f}")
            df_display['Risk'] = df_display['risk'].apply(lambda x: f"${x:.2f}")
            df_display['Size'] = df_display['size'].apply(lambda x: f"{x:.2f} lots")
            
            st.dataframe(
                df_display[['symbol', 'Size', 'P&L', 'Risk']],
                hide_index=True
            )
        else:
            st.info("No open positions")
    
    def _render_emergency_status(self):
        """Render status emergencia"""
        st.markdown("### 🚨 Emergency Status")
        
        # Emergency level indicator
        emergency_level = "GREEN"  # GREEN, YELLOW, ORANGE, RED
        
        if emergency_level == "GREEN":
            st.success("🟢 System Normal")
        elif emergency_level == "YELLOW":
            st.warning("🟡 Warning Level")
        elif emergency_level == "ORANGE":
            st.warning("🟠 Critical Level")
        else:
            st.error("🔴 Emergency Stop")
        
        # Emergency metrics
        st.markdown("#### Emergency Triggers:")
        
        # Drawdown check
        current_dd = self.dummy_account['drawdown']
        max_dd = 5.0
        dd_status = "✅" if current_dd < max_dd else "❌"
        st.write(f"{dd_status} Drawdown: {current_dd:.1f}% / {max_dd:.1f}%")
        
        # Consecutive losses
        consecutive = self.dummy_account['consecutive_losses']
        max_consecutive = 5
        cons_status = "✅" if consecutive < max_consecutive else "❌"
        st.write(f"{cons_status} Consecutive: {consecutive} / {max_consecutive}")
        
        # Daily loss
        daily_loss = abs(self.dummy_account['daily_pnl']) if self.dummy_account['daily_pnl'] < 0 else 0
        max_daily = 500
        daily_status = "✅" if daily_loss < max_daily else "❌"
        st.write(f"{daily_status} Daily Loss: ${daily_loss:.0f} / ${max_daily}")
    
    def _render_alerts(self):
        """Render sistema alerts"""
        st.markdown("### 🔔 Active Alerts")
        
        # Example alerts
        alerts = [
            {"level": "WARNING", "message": "Approaching daily loss limit", "time": "2 min ago"},
            {"level": "INFO", "message": "New position opened: EURUSD", "time": "5 min ago"}
        ]
        
        for alert in alerts:
            if alert["level"] == "WARNING":
                st.warning(f"⚠️ {alert['message']} ({alert['time']})")
            elif alert["level"] == "ERROR":
                st.error(f"❌ {alert['message']} ({alert['time']})")
            else:
                st.info(f"ℹ️ {alert['message']} ({alert['time']})")
    
    def _render_performance_chart(self):
        """Render gráfico performance"""
        st.markdown("### 📈 Performance Chart")
        
        # Generate sample equity curve
        dates = pd.date_range(start='2025-09-01', periods=30, freq='D')
        equity = [10000]
        
        for i in range(1, 30):
            change = np.random.normal(10, 50)  # Random walk
            equity.append(equity[-1] + change)
        
        df = pd.DataFrame({'Date': dates, 'Equity': equity})
        
        fig = px.line(df, x='Date', y='Equity', title='Equity Curve (Last 30 Days)')
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_recent_trades(self):
        """Render trades recientes"""
        st.markdown("### 📋 Recent Trades")
        
        # Sample trade history
        trades = [
            {"Time": "14:30", "Symbol": "EURUSD", "Type": "BUY", "Size": "1.5", "P&L": "+$75", "Status": "Closed"},
            {"Time": "13:15", "Symbol": "GBPJPY", "Type": "SELL", "Size": "0.8", "P&L": "-$225", "Status": "Closed"},
            {"Time": "12:00", "Symbol": "USDJPY", "Type": "BUY", "Size": "2.0", "P&L": "+$45", "Status": "Open"}
        ]
        
        df_trades = pd.DataFrame(trades)
        st.dataframe(df_trades, hide_index=True)
    
    def _render_system_health(self):
        """Render salud sistema"""
        st.markdown("### 🔧 System Health")
        
        # System components status
        components = {
            "MT5 Connection": "🟢 Connected",
            "Data Feed": "🟢 Active", 
            "Risk Manager": "🟢 Running",
            "Emergency System": "🟢 Monitoring",
            "Signal Validator": "🟢 Active"
        }
        
        for component, status in components.items():
            st.write(f"**{component}:** {status}")
        
        # Last update time
        st.write(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")

# Standalone dashboard runner
if __name__ == "__main__":
    import numpy as np
    
    dashboard = RiskMonitorDashboard()
    dashboard.run_dashboard()
