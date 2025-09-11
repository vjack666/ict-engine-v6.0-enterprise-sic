# 🛡️ RISK CONFIGURATION GUIDE  
## ICT Engine v6.0 Enterprise - Real Trading

**Guía completa configuración risk management para cuenta real**

---

## 🎯 **NIVELES DE RIESGO PREDEFINIDOS**

### **🟢 CONSERVATIVE (Recomendado para principiantes):**
```json
{
  "risk_percent": 0.5,           // 0.5% balance por trade
  "max_position_size": 5.0,      // Máximo 5 lots
  "max_daily_trades": 3,         // 3 trades máximo por día
  "max_drawdown": 3.0,          // 3% drawdown máximo
  "max_consecutive_losses": 3,   // 3 pérdidas consecutivas
  "profit_target": 2.0          // 2% profit mensual objetivo
}
```
**📊 PROFILE:** Cuentas $1K-$5K, nuevos en ICT, enfoque preservation capital

### **🟡 MODERATE (Recomendado para FTMO):**
```json
{
  "risk_percent": 1.0,           // 1% balance por trade
  "max_position_size": 10.0,     // Máximo 10 lots  
  "max_daily_trades": 5,         // 5 trades máximo por día
  "max_drawdown": 5.0,          // 5% drawdown máximo
  "max_consecutive_losses": 5,   // 5 pérdidas consecutivas
  "profit_target": 5.0          // 5% profit mensual objetivo
}
```
**📊 PROFILE:** Cuentas $10K-$50K, experiencia ICT intermedia, prop firms

### **🔴 AGGRESSIVE (Sólo traders experimentados):**
```json
{
  "risk_percent": 2.0,           // 2% balance por trade
  "max_position_size": 20.0,     // Máximo 20 lots
  "max_daily_trades": 8,         // 8 trades máximo por día
  "max_drawdown": 8.0,          // 8% drawdown máximo
  "max_consecutive_losses": 7,   // 7 pérdidas consecutivas
  "profit_target": 10.0         // 10% profit mensual objetivo
}
```
**📊 PROFILE:** Cuentas $100K+, expertos ICT, high performance trading

---

## ⚙️ **CONFIGURACIÓN PERSONALIZADA**

### **🔧 CUSTOM RISK SETUP:**
```python
from 01_CORE.real_trading import AutoPositionSizer, EmergencyConfig

# Configuración personalizada basada en tu cuenta
custom_config = {
    # ACCOUNT SPECIFICS
    'account_size': 25000.0,           # $25K account
    'base_currency': 'USD',            # Account currency
    'broker': 'FTMO',                  # Broker name
    
    # RISK PARAMETERS
    'risk_per_trade': 0.75,            # 0.75% per trade
    'max_portfolio_risk': 4.0,         # 4% maximum drawdown
    'max_correlation_exposure': 3.0,    # Max 3% in correlated pairs
    
    # POSITION SIZING
    'min_position_size': 0.01,         # Minimum 0.01 lots
    'max_position_size': 15.0,         # Maximum 15 lots
    'position_size_step': 0.01,        # 0.01 lot increments
    
    # DAILY LIMITS  
    'max_daily_loss': 400.0,           # $400 daily loss limit
    'max_daily_trades': 6,             # 6 trades per day maximum
    'max_news_exposure': 1.0,          # 1% during high impact news
    
    # TIME RESTRICTIONS
    'trading_hours': {
        'start': '06:00',              # London pre-market
        'end': '20:00',                # NY close
        'timezone': 'UTC'
    },
    'avoid_weekends': True,            # No weekend trading
    'avoid_holidays': True,            # No holiday trading
    
    # EMERGENCY STOPS
    'emergency_triggers': {
        'consecutive_losses': 4,        # 4 losses in a row
        'daily_loss_percent': 2.0,     # 2% daily loss
        'technical_failure': True,     # Stop on tech issues
        'connection_loss': True        # Stop if MT5 disconnects
    }
}
```

### **📊 IMPLEMENTAR CONFIGURACIÓN:**
```python
# Crear position sizer personalizado
sizer = AutoPositionSizer(
    risk_level=RiskLevel.CUSTOM,
    custom_risk_percent=custom_config['risk_per_trade'],
    max_position_size=custom_config['max_position_size'],
    correlation_threshold=0.7
)

# Crear emergency system personalizado
emergency_config = EmergencyConfig(
    max_drawdown_percent=custom_config['max_portfolio_risk'],
    max_consecutive_losses=custom_config['emergency_triggers']['consecutive_losses'],
    daily_loss_limit=custom_config['max_daily_loss'],
    monitoring_interval=15,  # Check every 15 seconds
    recovery_cooldown=1800   # 30 minute cooldown
)

emergency_system = EmergencyStopSystem(emergency_config)
```

---

## 🎯 **RISK SCENARIOS & RESPONSES**

### **📈 SCENARIO 1: Normal Trading Day**
```python
# Account: $10,000
# Risk per trade: 1% = $100
# Trade: EURUSD BUY @ 1.1000, SL @ 1.0950 (50 pips)

position_size = sizer.calculate_position_size(
    symbol="EURUSD",
    entry_price=1.1000,
    stop_loss=1.0950,
    account_balance=10000.0
)

print(f"Position Size: {position_size.position_size:.2f} lots")
# Expected: ~2.0 lots ($10 per pip * 50 pips * 2 lots = $100 risk)
```

### **📉 SCENARIO 2: High Drawdown Situation**
```python
# Account dropped to $9,200 (-8% from peak $10,000)
# Emergency system activates at 5% configured drawdown

emergency_status = emergency_system.get_health_report()
if not emergency_status['trading_enabled']:
    print("🚨 EMERGENCY STOP ACTIVE")
    print(f"Reason: {emergency_status['stop_reason']}")
    print("All trading suspended until manual reset")
```

### **⚡ SCENARIO 3: Volatile Market Conditions**
```python
# During high impact news or extreme volatility
# Reduce risk automatically

volatility_adjusted_risk = base_risk * volatility_factor
# volatility_factor = 0.5 during high impact news
# Reduces 1% risk to 0.5% automatically
```

---

## 🔧 **ADVANCED RISK CONFIGURATIONS**

### **🎯 PAIR-SPECIFIC RISK:**
```python
pair_risk_config = {
    'EURUSD': {'risk_multiplier': 1.0, 'max_size': 10.0},
    'GBPUSD': {'risk_multiplier': 0.8, 'max_size': 8.0},   # Reduce for GBP volatility
    'USDJPY': {'risk_multiplier': 0.9, 'max_size': 9.0},
    'XAUUSD': {'risk_multiplier': 0.6, 'max_size': 5.0},   # Reduce for Gold volatility
    'BTCUSD': {'risk_multiplier': 0.4, 'max_size': 2.0}    # Crypto requires lower risk
}
```

### **⏰ TIME-BASED RISK:**
```python
time_risk_config = {
    'london_session': {'risk_multiplier': 1.0},     # Full risk during London
    'new_york_session': {'risk_multiplier': 1.0},   # Full risk during NY
    'asian_session': {'risk_multiplier': 0.7},      # Reduced risk during Asian
    'overlap_sessions': {'risk_multiplier': 1.2},   # Increase during overlaps
    'weekend_gaps': {'risk_multiplier': 0.3},       # Very low risk near weekends
    'news_events': {'risk_multiplier': 0.5}         # Reduced risk during news
}
```

### **📊 CORRELATION-BASED RISK:**
```python
correlation_config = {
    'max_correlated_pairs': 2,           # Max 2 highly correlated positions
    'correlation_threshold': 0.7,        # 0.7+ considered highly correlated
    'correlation_risk_reduction': 0.6,   # Reduce risk by 40% for correlated
    'monitor_baskets': {
        'EUR_basket': ['EURUSD', 'EURGBP', 'EURJPY'],
        'USD_basket': ['EURUSD', 'GBPUSD', 'USDJPY'],
        'GBP_basket': ['GBPUSD', 'EURGBP', 'GBPJPY']
    }
}
```

---

## 📊 **RISK MONITORING & ALERTS**

### **🚨 REAL-TIME ALERTS:**
```python
alert_config = {
    'drawdown_warnings': {
        'yellow_alert': 2.0,    # 2% drawdown warning
        'orange_alert': 3.5,    # 3.5% drawdown critical
        'red_alert': 5.0        # 5% drawdown emergency stop
    },
    'loss_streak_warnings': {
        'yellow_alert': 3,      # 3 consecutive losses
        'orange_alert': 4,      # 4 consecutive losses
        'red_alert': 5          # 5 consecutive losses - STOP
    },
    'daily_loss_warnings': {
        'yellow_alert': 200,    # $200 daily loss warning
        'orange_alert': 350,    # $350 daily loss critical
        'red_alert': 500        # $500 daily loss - STOP
    }
}
```

### **📈 PERFORMANCE TRACKING:**
```python
# Daily risk metrics
daily_metrics = {
    'trades_taken': 3,
    'risk_per_trade': 1.0,
    'total_risk_exposure': 3.0,
    'realized_pnl': 150.0,
    'unrealized_pnl': -50.0,
    'current_drawdown': 1.2,
    'max_drawdown_today': 2.1,
    'risk_adjusted_return': 0.15,
    'sharpe_ratio': 1.8
}
```

---

## 🔄 **RISK ADJUSTMENT AUTOMATION**

### **📊 DYNAMIC RISK SCALING:**
```python
class DynamicRiskManager:
    def __init__(self):
        self.base_risk = 1.0
        self.performance_window = 20  # Last 20 trades
        
    def calculate_dynamic_risk(self, recent_performance):
        """Ajusta riesgo basado en performance reciente"""
        win_rate = recent_performance['win_rate']
        profit_factor = recent_performance['profit_factor']
        max_drawdown = recent_performance['max_drawdown']
        
        # Increase risk if performing well
        if win_rate > 0.6 and profit_factor > 1.5 and max_drawdown < 2.0:
            return self.base_risk * 1.2  # 20% increase
        
        # Decrease risk if struggling
        elif win_rate < 0.4 or profit_factor < 1.0 or max_drawdown > 4.0:
            return self.base_risk * 0.7  # 30% decrease
        
        return self.base_risk  # Normal risk
```

---

## ✅ **RISK VALIDATION CHECKLIST**

### **📋 PRE-LIVE CHECKLIST:**
```
□ Risk per trade configurado (0.5%-2% recomendado)
□ Maximum drawdown definido (3%-8% según perfil)
□ Position size limits establecidos
□ Emergency stop triggers configurados
□ Correlation limits implementados
□ Time-based restrictions aplicadas
□ News event handling configurado
□ Alert thresholds definidos
□ Recovery procedures documentados
□ Monitoring dashboard activo
```

### **🧪 RISK TESTING:**
```python
# Test risk scenarios
def test_risk_scenarios():
    # Test normal scenario
    assert calculate_risk(balance=10000, risk_pct=1.0) == 100.0
    
    # Test emergency scenario  
    assert emergency_system.check_drawdown(current=5.5, max=5.0) == True
    
    # Test position limits
    assert validate_position_size(25.0, max_allowed=20.0) == 20.0
    
    print("✅ All risk scenarios tested successfully")
```

---

## 🎯 **RECOMMENDED CONFIGURATIONS BY ACCOUNT SIZE**

### **💰 $1K - $5K ACCOUNTS:**
```json
{
  "risk_level": "conservative",
  "risk_percent": 0.5,
  "max_drawdown": 3.0,
  "max_daily_trades": 2,
  "focus": "Capital preservation"
}
```

### **💰 $10K - $50K ACCOUNTS (FTMO):**
```json
{
  "risk_level": "moderate", 
  "risk_percent": 1.0,
  "max_drawdown": 5.0,
  "max_daily_trades": 5,
  "focus": "Consistent growth"
}
```

### **💰 $100K+ ACCOUNTS:**
```json
{
  "risk_level": "aggressive",
  "risk_percent": 1.5,
  "max_drawdown": 7.0, 
  "max_daily_trades": 8,
  "focus": "Maximum returns"
}
```

---

**🛡️ RISK MANAGEMENT IS YOUR EDGE**  
**⚡ Configure once, protected forever**  
**📊 Let the system handle the math, you focus on the signals**
