# 🏦 ICT ENGINE v6.0 - MULTI-ACCOUNT MANAGEMENT

**💼 Gestión de múltiples cuentas de trading empresarial**
**⚖️ Risk management distribuido y portfolio optimization**

---

## 🎯 **MULTI-ACCOUNT OVERVIEW**

### **📊 Enterprise Account Structure:**
```
Master Account (Risk Control)
├── Account Group A: High Frequency (5 accounts)
│   ├── EU_HF_001 (EURUSD specialist)
│   ├── EU_HF_002 (GBPUSD specialist)  
│   ├── EU_HF_003 (USDJPY specialist)
│   ├── EU_HF_004 (Cross pairs)
│   └── EU_HF_005 (Emergency/backup)
├── Account Group B: Swing Trading (3 accounts)
│   ├── SW_001 (Major pairs daily)
│   ├── SW_002 (Weekly positions)
│   └── SW_003 (Monthly positions)
└── Account Group C: Research & Development (2 accounts)
    ├── RD_001 (New strategies testing)
    └── RD_002 (Paper trading/validation)
```

---

## 🏗️ **ARCHITECTURE FOR MULTI-ACCOUNT**

### **🔄 System Architecture:**
```python
# Multi-Account Manager Structure:
ICT Engine Core
├── AccountManager (master controller)
│   ├── Account Pool Manager
│   ├── Risk Distribution Engine
│   ├── Performance Aggregator
│   └── Rebalancing Controller
├── MT5 Connection Pool (10 connections)
├── Dashboard Multi-Account View
└── Unified Risk Management System
```

### **📁 Configuration Structure:**
```
01-CORE/config/accounts/
├── master_account_config.json       # Master risk settings
├── account_groups/
│   ├── high_frequency_group.json    # HF trading accounts
│   ├── swing_trading_group.json     # Swing accounts
│   └── research_group.json          # R&D accounts
├── individual_accounts/
│   ├── EU_HF_001_config.json        # Individual account settings
│   ├── EU_HF_002_config.json
│   └── [... other accounts]
└── risk_matrix.json                 # Cross-account risk rules
```

---

## ⚙️ **CONFIGURATION SETUP**

### **🎯 Master Account Configuration:**
**File:** `01-CORE/config/accounts/master_account_config.json`
```json
{
  "master_account": {
    "total_capital": 1000000,
    "currency": "USD",
    "max_total_risk": 0.15,
    "max_daily_loss": 0.05,
    "emergency_stop_threshold": 0.20,
    "rebalance_frequency": "daily"
  },
  "account_groups": {
    "high_frequency": {
      "allocation_percentage": 0.60,
      "max_group_risk": 0.08,
      "max_correlation": 0.70,
      "active_hours": ["08:00-11:00", "13:00-16:00"]
    },
    "swing_trading": {
      "allocation_percentage": 0.30,
      "max_group_risk": 0.05,
      "max_correlation": 0.40,
      "position_duration": "1-7 days"
    },
    "research": {
      "allocation_percentage": 0.10,
      "max_group_risk": 0.02,
      "live_trading": false,
      "purpose": "strategy_validation"
    }
  },
  "risk_controls": {
    "max_drawdown_per_account": 0.10,
    "correlation_monitoring": true,
    "news_based_stops": true,
    "margin_call_threshold": 0.30
  }
}
```

### **🏦 Individual Account Configuration:**
**File:** `01-CORE/config/accounts/individual_accounts/EU_HF_001_config.json`
```json
{
  "account_info": {
    "account_id": "EU_HF_001",
    "mt5_login": 123456789,
    "mt5_password": "${MT5_PASSWORD_EU_HF_001}",
    "mt5_server": "broker-server.com",
    "broker": "IC Markets",
    "account_type": "ECN Raw",
    "base_currency": "USD",
    "initial_balance": 100000
  },
  "trading_config": {
    "specialization": ["EURUSD"],
    "max_position_size": 10.0,
    "max_concurrent_trades": 5,
    "trading_sessions": ["london_killzone", "ny_killzone"],
    "risk_per_trade": 0.015,
    "max_daily_trades": 20
  },
  "strategy_allocation": {
    "ict_patterns": 0.70,
    "smart_money": 0.25,
    "market_structure": 0.05
  },
  "risk_management": {
    "stop_loss_type": "dynamic",
    "take_profit_ratio": 2.0,
    "trailing_stop": true,
    "max_slippage": 2,
    "news_filter": true
  }
}
```

---

## 🚀 **MULTI-ACCOUNT IMPLEMENTATION**

### **📱 Account Manager Core:**
**File:** `01-CORE/multi_account/account_manager.py`
```python
class MultiAccountManager:
    """
    🏦 MULTI-ACCOUNT MANAGER v6.0 ENTERPRISE
    ==========================================
    
    Gestiona múltiples cuentas MT5 con:
    - Risk distribution inteligente
    - Performance tracking agregado
    - Rebalancing automático
    - Correlation monitoring
    """
    
    def __init__(self, master_config_path: str):
        self.master_config = self._load_master_config(master_config_path)
        self.accounts = self._load_all_accounts()
        self.mt5_connections = self._initialize_connections()
        self.risk_manager = MultiAccountRiskManager(self.master_config)
        self.performance_tracker = PerformanceAggregator(self.accounts)
        
    def start_trading_session(self):
        """Iniciar sesión de trading en todas las cuentas"""
        for account_group in self.master_config['account_groups']:
            if self._is_group_active(account_group):
                accounts = self._get_group_accounts(account_group)
                for account in accounts:
                    self._start_account_trading(account)
                    
    def distribute_signal(self, signal: TradingSignal):
        """Distribuir señal a cuentas apropiadas"""
        eligible_accounts = self._filter_eligible_accounts(signal)
        for account in eligible_accounts:
            position_size = self._calculate_position_size(account, signal)
            if self.risk_manager.validate_trade(account, position_size):
                self._execute_trade(account, signal, position_size)
                
    def monitor_risk_across_accounts(self):
        """Monitorear riesgo agregado en tiempo real"""
        total_exposure = self._calculate_total_exposure()
        correlation_risk = self._calculate_correlation_risk()
        
        if total_exposure > self.master_config['master_account']['max_total_risk']:
            self._emergency_risk_reduction()
            
        if correlation_risk > 0.80:
            self._reduce_correlated_positions()
```

### **⚖️ Risk Management Multi-Account:**
**File:** `01-CORE/multi_account/risk_manager.py`
```python
class MultiAccountRiskManager:
    """Risk management across multiple accounts"""
    
    def validate_trade(self, account_id: str, signal: TradingSignal) -> bool:
        """Validate trade against multi-account risk rules"""
        
        # 1. Individual account risk check
        account_risk = self._get_account_risk(account_id)
        if account_risk > self.max_account_risk:
            return False
            
        # 2. Group risk check
        group_risk = self._get_group_risk(account_id)
        if group_risk > self.max_group_risk:
            return False
            
        # 3. Total portfolio risk check  
        total_risk = self._get_total_portfolio_risk()
        if total_risk > self.max_total_risk:
            return False
            
        # 4. Correlation check
        if self._would_increase_correlation(account_id, signal):
            return False
            
        return True
        
    def calculate_position_size(self, account_id: str, signal: TradingSignal) -> float:
        """Calculate optimal position size considering portfolio"""
        
        # Base position size from account config
        base_size = self._get_base_position_size(account_id, signal)
        
        # Adjust for portfolio correlation
        correlation_adjustment = self._get_correlation_adjustment(account_id, signal)
        
        # Adjust for account performance
        performance_adjustment = self._get_performance_adjustment(account_id)
        
        # Adjust for group allocation
        group_adjustment = self._get_group_allocation_adjustment(account_id)
        
        final_size = base_size * correlation_adjustment * performance_adjustment * group_adjustment
        
        return min(final_size, self._get_max_position_size(account_id))
```

---

## 📊 **DASHBOARD MULTI-ACCOUNT**

### **🎨 Multi-Account Dashboard Layout:**
**File:** `09-DASHBOARD/multi_account/dashboard.py`
```python
def create_multi_account_layout():
    """Create dashboard layout for multi-account management"""
    
    return html.Div([
        # Master Portfolio Overview
        html.Div([
            html.H2("🏦 Master Portfolio Overview"),
            dcc.Graph(id="portfolio-performance"),
            dcc.Graph(id="risk-distribution")
        ], className="master-overview"),
        
        # Account Groups Performance
        html.Div([
            html.H3("📊 Account Groups"),
            html.Div(id="account-groups-grid")
        ], className="groups-section"),
        
        # Individual Accounts
        html.Div([
            html.H3("💼 Individual Accounts"),
            dash_table.DataTable(
                id="accounts-table",
                columns=[
                    {"name": "Account", "id": "account_id"},
                    {"name": "Balance", "id": "balance", "type": "numeric", "format": FormatTemplate.money(2)},
                    {"name": "Equity", "id": "equity", "type": "numeric", "format": FormatTemplate.money(2)},
                    {"name": "P&L Daily", "id": "daily_pnl", "type": "numeric", "format": FormatTemplate.percentage(2)},
                    {"name": "Drawdown", "id": "drawdown", "type": "numeric", "format": FormatTemplate.percentage(2)},
                    {"name": "Risk %", "id": "risk_percent", "type": "numeric", "format": FormatTemplate.percentage(1)},
                    {"name": "Status", "id": "status"}
                ],
                style_cell={'textAlign': 'center'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{daily_pnl} > 0'},
                        'backgroundColor': '#90EE90',
                        'color': 'black',
                    },
                    {
                        'if': {'filter_query': '{daily_pnl} < 0'},
                        'backgroundColor': '#FFB6C1',
                        'color': 'black',
                    }
                ]
            )
        ], className="accounts-section"),
        
        # Risk Matrix
        html.Div([
            html.H3("⚖️ Risk Matrix"),
            dcc.Graph(id="correlation-heatmap"),
            dcc.Graph(id="risk-exposure-chart")
        ], className="risk-section")
    ])
```

---

## 🔄 **OPERATIONAL PROCEDURES**

### **🌅 Daily Startup Procedure:**
```python
# File: scripts/daily_startup.py

def daily_startup_procedure():
    """Complete daily startup for multi-account system"""
    
    print("🏦 Starting Multi-Account ICT Engine...")
    
    # 1. Initialize master account manager
    account_manager = MultiAccountManager("01-CORE/config/accounts/master_account_config.json")
    
    # 2. Verify all MT5 connections
    connection_status = account_manager.verify_all_connections()
    if not all(connection_status.values()):
        handle_connection_failures(connection_status)
    
    # 3. Load overnight positions and P&L
    overnight_summary = account_manager.get_overnight_summary()
    print(f"📊 Overnight P&L: {overnight_summary['total_pnl']:+.2f}")
    
    # 4. Check for margin calls or risk violations
    risk_violations = account_manager.check_risk_violations()
    if risk_violations:
        handle_risk_violations(risk_violations)
    
    # 5. Rebalance if needed
    if account_manager.needs_rebalancing():
        rebalancing_plan = account_manager.create_rebalancing_plan()
        execute_rebalancing(rebalancing_plan)
    
    # 6. Start trading session
    account_manager.start_trading_session()
    
    print("✅ Multi-Account system operational")

def handle_connection_failures(connection_status):
    """Handle MT5 connection failures"""
    failed_accounts = [acc for acc, status in connection_status.items() if not status]
    
    for account in failed_accounts:
        print(f"🔄 Attempting reconnection for {account}")
        # Implement reconnection logic
        
def handle_risk_violations(violations):
    """Handle risk management violations"""
    for violation in violations:
        if violation['severity'] == 'critical':
            # Stop trading on account
            account_manager.stop_trading(violation['account_id'])
        elif violation['severity'] == 'warning':
            # Reduce position sizes
            account_manager.reduce_risk(violation['account_id'], 0.5)
```

### **🌙 End of Day Procedure:**
```python
# File: scripts/end_of_day.py

def end_of_day_procedure():
    """Complete end-of-day procedures"""
    
    # 1. Close all day trading positions (if configured)
    account_manager.close_day_positions()
    
    # 2. Calculate daily performance
    daily_performance = account_manager.calculate_daily_performance()
    
    # 3. Generate daily report
    report = generate_daily_report(daily_performance)
    save_daily_report(report)
    
    # 4. Backup account states
    backup_account_states()
    
    # 5. Prepare overnight risk monitoring
    setup_overnight_monitoring()
    
    print("🌙 End of day procedures completed")
```

---

## 📈 **PERFORMANCE AGGREGATION**

### **📊 Portfolio Performance Tracking:**
```python
class PerformanceAggregator:
    """Aggregate performance across all accounts"""
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get overall portfolio performance"""
        
        total_balance = sum(acc.get_balance() for acc in self.accounts.values())
        total_equity = sum(acc.get_equity() for acc in self.accounts.values())
        total_pnl = sum(acc.get_daily_pnl() for acc in self.accounts.values())
        
        # Calculate portfolio metrics
        portfolio_return = (total_equity - total_balance) / total_balance
        max_drawdown = self._calculate_portfolio_drawdown()
        sharpe_ratio = self._calculate_portfolio_sharpe()
        
        return {
            "total_balance": total_balance,
            "total_equity": total_equity,
            "daily_pnl": total_pnl,
            "portfolio_return": portfolio_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "account_count": len(self.accounts),
            "active_accounts": len([acc for acc in self.accounts.values() if acc.is_trading()])
        }
    
    def get_group_performance(self, group_name: str) -> Dict[str, Any]:
        """Get performance for specific account group"""
        
        group_accounts = self._get_group_accounts(group_name)
        
        return {
            "group_name": group_name,
            "account_count": len(group_accounts),
            "total_balance": sum(acc.get_balance() for acc in group_accounts),
            "total_pnl": sum(acc.get_daily_pnl() for acc in group_accounts),
            "best_performer": max(group_accounts, key=lambda x: x.get_daily_pnl()).account_id,
            "worst_performer": min(group_accounts, key=lambda x: x.get_daily_pnl()).account_id,
            "avg_return": np.mean([acc.get_daily_pnl() / acc.get_balance() for acc in group_accounts])
        }
```

---

## 🚨 **EMERGENCY PROCEDURES**

### **🔴 Emergency Risk Management:**
```python
def emergency_stop_all_trading():
    """Emergency stop across all accounts"""
    
    print("🚨 EMERGENCY STOP ACTIVATED")
    
    # 1. Stop all new trades
    account_manager.halt_all_new_trades()
    
    # 2. Close all open positions (if configured)
    if EMERGENCY_CLOSE_ALL_POSITIONS:
        account_manager.close_all_positions()
    
    # 3. Send alerts
    send_emergency_alert("All trading halted - manual intervention required")
    
    # 4. Log emergency event
    log_emergency_event("EMERGENCY_STOP", "All accounts halted")
    
def emergency_rebalance():
    """Emergency portfolio rebalancing"""
    
    # 1. Calculate current risk exposure
    total_risk = account_manager.calculate_total_risk()
    
    # 2. If over threshold, reduce positions
    if total_risk > EMERGENCY_RISK_THRESHOLD:
        reduction_plan = account_manager.create_risk_reduction_plan()
        execute_risk_reduction(reduction_plan)
    
    # 3. Rebalance between accounts
    rebalancing_plan = account_manager.create_emergency_rebalancing()
    execute_emergency_rebalancing(rebalancing_plan)
```

---

## 📋 **MULTI-ACCOUNT CHECKLIST**

### **✅ Setup Checklist:**
```
□ Master account configuration defined
□ Individual account configs created
□ Account groups properly structured
□ Risk matrix configured
□ MT5 connections tested for all accounts
□ Dashboard multi-account view working
□ Performance aggregation functioning
□ Emergency procedures defined
□ Backup procedures for all accounts
□ Monitoring alerts configured
```

### **✅ Daily Operations Checklist:**
```
□ All MT5 connections active
□ No critical risk violations
□ Portfolio balance within limits
□ Correlation levels acceptable
□ Daily performance calculated
□ Rebalancing executed (if needed)
□ All accounts trading within parameters
□ Emergency stops functioning
□ Performance reports generated
□ Backup completed
```

### **🔄 Monthly Review Checklist:**
```
□ Account performance review
□ Risk parameter optimization
□ Strategy allocation adjustment
□ Broker relationship review
□ Technology stack update
□ Disaster recovery test
□ Compliance review
□ Cost analysis (spreads, commissions)
□ Portfolio rebalancing strategy review
□ Documentation updates
```

---

## 🔧 **TROUBLESHOOTING**

### **❌ Common Multi-Account Issues:**

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Account correlation too high** | Similar P&L across accounts | Adjust strategy allocation, diversify symbols |
| **Risk limits exceeded** | Emergency stops triggered | Review position sizing, adjust risk parameters |
| **MT5 connection failures** | Some accounts offline | Check network, MT5 server status, credentials |
| **Performance divergence** | Large gap between accounts | Investigate execution quality, slippage |
| **Rebalancing failures** | Uneven capital allocation | Check account balances, transfer procedures |

### **🔍 Diagnostics Commands:**
```python
# Multi-account system health check
def multi_account_diagnostics():
    """Comprehensive diagnostics for multi-account system"""
    
    # Check all connections
    connections = account_manager.test_all_connections()
    print(f"Connections: {sum(connections.values())}/{len(connections)} active")
    
    # Check risk levels
    risk_summary = account_manager.get_risk_summary()
    print(f"Total portfolio risk: {risk_summary['total_risk']:.2%}")
    
    # Check performance
    perf_summary = account_manager.get_performance_summary()
    print(f"Portfolio P&L: {perf_summary['daily_pnl']:+.2f}")
    
    # Check correlations
    correlations = account_manager.get_correlation_matrix()
    max_correlation = correlations.max().max()
    print(f"Max correlation: {max_correlation:.2f}")
```

---

*🏦 Última actualización: 11 Septiembre 2025*  
*💼 Soporte: Hasta 50 cuentas simultáneas*  
*⚖️ Risk management: Portfolio-level + individual*
