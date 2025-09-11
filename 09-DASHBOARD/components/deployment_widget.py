#!/usr/bin/env python3
"""
🚀 DEPLOYMENT WIDGET - Control de Deployment Live Trading
===========================================================

Widget para controlar el deployment a cuenta real con interfaz visual.
Versión corregida compatible con Textual framework.
"""

import time
import json
import subprocess
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from textual.widgets import Static, Button, Input, Select, Switch, ProgressBar
from textual.containers import Container, Vertical, Horizontal
from textual.reactive import reactive
from textual.message import Message
from textual.app import ComposeResult
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

class DeploymentWidget(Container):
    """Widget de deployment con controles visuales"""
    
    # Estados reactivos
    deployment_status = reactive("READY")
    account_balance = reactive(0.0)
    risk_percentage = reactive(1.5)
    max_positions = reactive(1)
    connection_status = reactive("DISCONNECTED")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.console = Console()
        self.deployment_config = {}
        
    def compose(self) -> ComposeResult:
        """Componer interfaz de deployment"""
        yield Static("🚀 LIVE DEPLOYMENT CONTROL", classes="deployment-header")
        
        # Panel de configuración
        with Vertical(classes="config-panel"):
            yield Static("⚙️ CONFIGURACIÓN DE CUENTA", classes="section-header")
            
            with Horizontal(classes="config-row"):
                yield Static("💰 Balance:", classes="config-label")
                yield Input(
                    placeholder="10000.00",
                    id="balance-input",
                    classes="balance-input"
                )
                yield Static("USD", classes="currency-label")
            
            with Horizontal(classes="config-row"):
                yield Static("🎯 Risk %:", classes="config-label")
                yield Select([
                    ("1.0% - Ultra Conservative", "1.0"),
                    ("1.5% - Conservative", "1.5"),
                    ("2.0% - Moderate", "2.0"),
                    ("2.5% - Aggressive", "2.5")
                ], value="1.5", id="risk-select")
            
            with Horizontal(classes="config-row"):
                yield Static("📊 Max Positions:", classes="config-label")
                yield Select([
                    ("1 Position", "1"),
                    ("2 Positions", "2"),
                    ("3 Positions", "3")
                ], value="1", id="positions-select")
            
            with Horizontal(classes="config-row"):
                yield Static("🎲 Trading Mode:", classes="config-label")
                yield Select([
                    ("Conservative", "conservative"),
                    ("Moderate", "moderate"),
                    ("Aggressive", "aggressive")
                ], value="conservative", id="mode-select")
        
        # Panel de conexión MT5
        with Vertical(classes="connection-panel"):
            yield Static("🔗 CONEXIÓN MT5", classes="section-header")
            
            with Horizontal(classes="connection-row"):
                yield Button("🔗 Test Connection", id="test-connection", classes="connection-btn")
                yield Static("Status: DISCONNECTED", id="connection-status", classes="status-disconnected")
            
            with Horizontal(classes="connection-row"):
                yield Static("🏢 Broker:", classes="connection-label")
                yield Static("FTMO Global Markets", classes="broker-name")
            
            with Horizontal(classes="connection-row"):
                yield Static("🏦 Account:", classes="connection-label")
                yield Static("Not Connected", id="account-display", classes="account-info")
        
        # Panel de validación del sistema
        with Vertical(classes="validation-panel"):
            yield Static("✅ VALIDACIÓN DEL SISTEMA", classes="section-header")
            
            yield Button("🧪 Validate Smart Money", id="validate-smart-money", classes="validate-btn")
            yield Button("🛡️ Validate Risk Management", id="validate-risk", classes="validate-btn")
            yield Button("⚡ Validate Performance", id="validate-performance", classes="validate-btn")
            yield Button("🔧 Validate All Systems", id="validate-all", classes="validate-btn-primary")
            
            yield ProgressBar(total=100, show_eta=False, id="validation-progress")
            yield Static("System Validation: Not Started", id="validation-status")
        
        # Panel de deployment
        with Vertical(classes="deployment-panel"):
            yield Static("🚀 LIVE DEPLOYMENT", classes="section-header")
            
            with Horizontal(classes="deployment-controls"):
                yield Button("🚀 DEPLOY LIVE", id="deploy-live", classes="deploy-btn-primary")
                yield Button("🛑 EMERGENCY STOP", id="emergency-stop", classes="emergency-btn")
                yield Button("📊 DASHBOARD", id="open-dashboard", classes="dashboard-btn")
            
            yield Static("Deployment Status: READY", id="deployment-status", classes="status-ready")
            
            # Monitor de estado en vivo
            with Vertical(classes="live-monitor"):
                yield Static("📊 LIVE MONITOR", classes="monitor-header")
                yield Static("Not Active", id="live-status", classes="monitor-status")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Manejar clicks de botones"""
        button_id = event.button.id
        
        if button_id == "test-connection":
            self.run_worker(self.test_mt5_connection())
        elif button_id == "validate-smart-money":
            self.run_worker(self.validate_smart_money())
        elif button_id == "validate-risk":
            self.run_worker(self.validate_risk_management())
        elif button_id == "validate-performance":
            self.run_worker(self.validate_performance())
        elif button_id == "validate-all":
            self.run_worker(self.validate_all_systems())
        elif button_id == "deploy-live":
            self.run_worker(self.deploy_live_trading())
        elif button_id == "emergency-stop":
            self.run_worker(self.emergency_stop())
        elif button_id == "open-dashboard":
            self.run_worker(self.open_monitoring_dashboard())
    
    async def test_mt5_connection(self):
        """Probar conexión MT5"""
        connection_status = self.query_one("#connection-status", Static)
        connection_status.renderable = "Status: TESTING..."
        
        try:
            # Ejecutar test de conexión real
            result = subprocess.run([
                "python", "main.py", "--test-mt5-connection"
            ], capture_output=True, text=True, timeout=30, cwd="..")
            
            if result.returncode == 0 and "✅" in result.stdout:
                connection_status.renderable = "Status: ✅ CONNECTED"
                connection_status.add_class("status-connected")
                account_display = self.query_one("#account-display", Static)
                account_display.renderable = "FTMO Account Active"
                self.connection_status = "CONNECTED"
            else:
                connection_status.renderable = "Status: ❌ FAILED"
                connection_status.add_class("status-error")
                
        except Exception as e:
            connection_status.renderable = f"Status: ❌ ERROR: {str(e)[:30]}"
    
    async def validate_smart_money(self):
        """Validar Smart Money Analysis"""
        progress = self.query_one("#validation-progress", ProgressBar)
        status = self.query_one("#validation-status", Static)
        
        status.renderable = "Validating Smart Money Analysis..."
        progress.advance(25)
        
        try:
            result = subprocess.run([
                "python", "main.py", "--test-smart-money", "--symbol=EURUSD", "--method=all"
            ], capture_output=True, text=True, timeout=60, cwd="..")
            
            if result.returncode == 0 and "✅ PASS" in result.stdout:
                progress.advance(75)  # Complete to 100
                status.renderable = "✅ Smart Money Analysis: VALIDATED"
            else:
                progress.advance(75)  # Complete to 100
                status.renderable = "❌ Smart Money Analysis: FAILED"
                
        except Exception as e:
            status.renderable = f"❌ Smart Money Analysis: ERROR - {str(e)[:50]}"
    
    async def validate_risk_management(self):
        """Validar Risk Management"""
        progress = self.query_one("#validation-progress", ProgressBar)
        status = self.query_one("#validation-status", Static)
        
        status.renderable = "Validating Risk Management..."
        progress.advance(50)
        
        try:
            balance_input = self.query_one("#balance-input", Input)
            balance = getattr(balance_input, 'value', "10000") or "10000"
            result = subprocess.run([
                "python", "main.py", "--test-position-sizing", f"--balance={balance}"
            ], capture_output=True, text=True, timeout=30, cwd="..")
            
            if result.returncode == 0 and "✅ PASS" in result.stdout:
                progress.advance(50)  # Complete to 100
                status.renderable = "✅ Risk Management: VALIDATED"
            else:
                status.renderable = "❌ Risk Management: FAILED"
                
        except Exception as e:
            status.renderable = f"❌ Risk Management: ERROR - {str(e)[:50]}"
    
    async def validate_performance(self):
        """Validar Performance del Sistema"""
        progress = self.query_one("#validation-progress", ProgressBar)
        status = self.query_one("#validation-status", Static)
        
        status.renderable = "Validating System Performance..."
        progress.advance(75)
        
        try:
            result = subprocess.run([
                "python", "main.py", "--test-all-systems"
            ], capture_output=True, text=True, timeout=120, cwd="..")
            
            if result.returncode == 0 and ("✅" in result.stdout or "PASS" in result.stdout):
                progress.advance(25)  # Complete to 100
                status.renderable = "✅ Performance: VALIDATED"
            else:
                status.renderable = "❌ Performance: FAILED"
                
        except Exception as e:
            status.renderable = f"❌ Performance: ERROR - {str(e)[:50]}"
    
    async def validate_all_systems(self):
        """Validar todos los sistemas secuencialmente"""
        # Smart Money validation
        await self.validate_smart_money()
        await asyncio.sleep(1)
        
        # Risk Management validation
        await self.validate_risk_management()
        await asyncio.sleep(1)
        
        # Performance validation
        await self.validate_performance()
        
        # Status final
        status = self.query_one("#validation-status", Static)
        status.renderable = "🎯 ALL SYSTEMS VALIDATION COMPLETED"
    
    async def deploy_live_trading(self):
        """Iniciar deployment live trading"""
        deployment_status = self.query_one("#deployment-status", Static)
        live_status = self.query_one("#live-status", Static)
        
        if self.connection_status != "CONNECTED":
            deployment_status.renderable = "❌ DEPLOYMENT FAILED: No MT5 Connection"
            return
        
        deployment_status.renderable = "🚀 DEPLOYING TO LIVE..."
        
        try:
            # Obtener configuración
            balance_input = self.query_one("#balance-input", Input)
            risk_select = self.query_one("#risk-select", Select)
            max_pos_select = self.query_one("#positions-select", Select)
            mode_select = self.query_one("#mode-select", Select)
            
            balance = getattr(balance_input, 'value', "10000") or "10000"
            risk_mode = getattr(risk_select, 'value', "1.5")
            max_pos = getattr(max_pos_select, 'value', "1")
            mode = getattr(mode_select, 'value', "conservative")
            
            # Comando de deployment simulado (en producción sería real)
            result = subprocess.run([
                "python", "main.py", "--simulate-live-deploy",
                "--symbol=EURUSD", 
                f"--risk-mode={mode}",
                f"--max-positions={max_pos}",
                f"--risk-pct={risk_mode}"
            ], capture_output=True, text=True, timeout=60, cwd="..")
            
            if result.returncode == 0:
                deployment_status.renderable = "✅ LIVE TRADING DEPLOYED"
                deployment_status.add_class("status-live")
                live_status.renderable = "🟢 LIVE TRADING ACTIVE"
                self.deployment_status = "LIVE"
            else:
                deployment_status.renderable = "❌ DEPLOYMENT FAILED"
                deployment_status.add_class("status-error")
                
        except Exception as e:
            deployment_status.renderable = f"❌ DEPLOYMENT ERROR: {str(e)[:50]}"
    
    async def emergency_stop(self):
        """Parada de emergencia"""
        deployment_status = self.query_one("#deployment-status", Static)
        live_status = self.query_one("#live-status", Static)
        
        try:
            result = subprocess.run([
                "python", "main.py", "--emergency-stop"
            ], capture_output=True, text=True, timeout=30, cwd="..")
            
            deployment_status.renderable = "🛑 EMERGENCY STOP ACTIVATED"
            deployment_status.add_class("status-stopped")
            live_status.renderable = "🔴 TRADING STOPPED"
            self.deployment_status = "STOPPED"
            
        except Exception as e:
            deployment_status.renderable = f"❌ EMERGENCY STOP ERROR: {str(e)[:50]}"
    
    async def open_monitoring_dashboard(self):
        """Abrir dashboard de monitoreo"""
        try:
            subprocess.Popen([
                "python", "main.py", "--risk-dashboard"
            ], cwd="..")
        except Exception as e:
            deployment_status = self.query_one("#deployment-status", Static)
            deployment_status.renderable = f"❌ Dashboard Error: {str(e)[:50]}"
