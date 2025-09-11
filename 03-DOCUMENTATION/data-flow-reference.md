# 📊 ICT ENGINE v6.0 - DATA FLOW REFERENCE

**🔄 Flujo completo de datos desde MT5 hasta Dashboard verificado**
**📈 Pipeline de datos en tiempo real documentado**

---

## 🔄 **FLUJO PRINCIPAL DE DATOS**

### **📈 Pipeline Overview:**
```
MT5 Terminal → MT5DataManager → RealDataCollector → PatternDetector → SmartMoneyAnalyzer → Dashboard
     ↓              ↓              ↓                ↓               ↓                   ↓
[Real Market] → [Raw Data] → [Processed] → [Patterns] → [Signals] → [Visualization]
```

---

## 🏗️ **STAGE 1: MT5 TERMINAL → RAW DATA**

### **📡 Componente: MT5DataManager**
**Archivo:** `01-CORE/data_management/mt5_data_manager.py`

```python
# Data flow input:
MT5 Terminal (live market data) 
  ↓
MetaTrader5.copy_rates_from()
  ↓
Raw OHLCV data arrays
```

**⚙️ Configuración:**
```json
{
  "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
  "timeframes": ["H4", "H1", "M15", "M5"],
  "max_bars": {
    "H4": 3000,
    "H1": 5000, 
    "M15": 5000,
    "M5": 2000
  },
  "update_frequency": "real-time"
}
```

**📊 Output Format:**
```python
{
  "symbol": "EURUSD",
  "timeframe": "H1", 
  "data": pandas.DataFrame({
    "time": [datetime objects],
    "open": [float values],
    "high": [float values], 
    "low": [float values],
    "close": [float values],
    "volume": [int values]
  }),
  "last_update": "2025-09-11T14:30:00",
  "bars_count": 5000
}
```

---

## 🔧 **STAGE 2: RAW DATA → PROCESSED DATA**

### **🛠️ Componente: RealDataCollector**
**Archivo:** `01-CORE/utils/real_data_collector.py`

```python
# Data flow transformation:
Raw MT5 data arrays
  ↓
Data validation & cleaning  
  ↓  
Pandas DataFrame standardization
  ↓
Multi-timeframe alignment
  ↓
Cache storage (04-DATA/cache/)
```

**🔄 Processing Steps:**
1. **Data Validation:**
   - Remove invalid bars (gaps, errors)
   - Validate OHLC relationships  
   - Check for missing timestamps

2. **Data Standardization:**
   - Convert to pandas DataFrame
   - Standardize column names
   - Add calculated fields (typical_price, etc.)

3. **Multi-timeframe Sync:**
   - Align timestamps across timeframes
   - Ensure data consistency
   - Handle timezone conversions

**📊 Output Format:**
```python
{
  "EURUSD": {
    "H4": DataFrame(5000 rows × 8 columns),
    "H1": DataFrame(5000 rows × 8 columns),
    "M15": DataFrame(5000 rows × 8 columns),
    "M5": DataFrame(2000 rows × 8 columns)
  },
  "metadata": {
    "last_update": "2025-09-11T14:30:00",
    "data_quality_score": 0.98,
    "gaps_filled": 3,
    "total_bars": 22000
  }
}
```

---

## 🎯 **STAGE 3: PROCESSED DATA → PATTERN DETECTION**

### **🔍 Componente: PatternDetector**
**Archivo:** `01-CORE/analysis/pattern_detector.py`

```python
# Data flow analysis:
Clean multi-timeframe data
  ↓
Pattern detection algorithms
  ↓
ICT patterns identified
  ↓
Pattern confluence analysis
  ↓
Scored pattern results
```

**🎯 Pattern Detection Pipeline:**
1. **Order Blocks Detection:**
   ```python
   def detect_order_blocks(df_h1, df_m15):
       # Identify bearish/bullish order blocks
       # Validate with volume confirmation
       # Return scored order blocks
   ```

2. **Fair Value Gaps:**
   ```python  
   def detect_fvg(df):
       # Find price gaps in candle structure
       # Validate gap significance
       # Track gap fill behavior
   ```

3. **Liquidity Grabs:**
   ```python
   def detect_liquidity_grab(df):
       # Identify sweep of highs/lows
       # Confirm with volume spike  
       # Measure reaction strength
   ```

**📊 Output Format:**
```python
{
  "symbol": "EURUSD",
  "patterns_detected": [
    {
      "type": "order_block",
      "subtype": "bearish_ob",
      "timeframe": "H1",
      "start_time": "2025-09-11T12:00:00",
      "price_level": 1.16850,
      "strength": 0.85,
      "confluence": 3,
      "status": "active"
    },
    {
      "type": "fair_value_gap", 
      "timeframe": "M15",
      "gap_high": 1.16920,
      "gap_low": 1.16880,
      "strength": 0.72,
      "filled_percentage": 0.0
    }
  ],
  "pattern_summary": {
    "total_patterns": 12,
    "high_confidence": 4,
    "active_patterns": 8
  }
}
```

---

## 💰 **STAGE 4: PATTERNS → SMART MONEY ANALYSIS**

### **🧠 Componente: SmartMoneyAnalyzer**  
**Archivo:** `01-CORE/smart_money_concepts/smart_money_analyzer.py`

```python
# Data flow enhancement:
ICT patterns + clean price data
  ↓
Smart Money concepts analysis
  ↓
Liquidity pools detection
  ↓
Institutional flow analysis
  ↓
Market maker behavior detection
  ↓
Enhanced trading signals
```

**💡 Smart Money Pipeline:**
1. **Liquidity Pools:**
   - Detect equal highs/lows
   - Identify old highs/lows
   - Daily/weekly levels
   - Institutional interest scoring

2. **Institutional Flow:**
   - Order block activity analysis
   - Volume profile examination
   - Smart money signature detection
   - Flow direction calculation

3. **Market Maker Analysis:**
   - Manipulation detection
   - Stop hunt identification
   - Fake breakout analysis
   - Accumulation/distribution phases

**📊 Output Format:**
```python
{
  "symbol": "EURUSD",
  "smart_money_analysis": {
    "current_session": "london_killzone",
    "liquidity_pools": [
      {
        "type": "equal_highs",
        "price_level": 1.16950,
        "strength": 0.78,
        "institutional_interest": 0.82,
        "expected_reaction": "strong_rejection"
      }
    ],
    "institutional_flow": {
      "direction": "bearish",
      "strength": 0.74,
      "confidence": 0.68
    },
    "market_maker_model": "london_manipulation",
    "manipulation_evidence": 0.71
  }
}
```

---

## 📱 **STAGE 5: SIGNALS → DASHBOARD VISUALIZATION**

### **🎨 Componente: Dashboard Engine**
**Archivo:** `09-DASHBOARD/start_dashboard.py`

```python
# Data flow presentation:
Enhanced trading signals
  ↓
Dashboard data aggregation
  ↓
Real-time UI updates
  ↓
Interactive visualizations
  ↓
User interface (http://localhost:8050)
```

**🎯 Dashboard Data Pipeline:**
1. **Data Aggregation:**
   - Collect all analysis results
   - Format for dashboard widgets
   - Calculate summary metrics
   - Prepare real-time updates

2. **Widget Updates:**
   - Market overview widget
   - Pattern detection widget  
   - Smart money analysis widget
   - Performance metrics widget

3. **Real-time Refresh:**
   - WebSocket connections
   - Automatic data refresh
   - Interactive chart updates
   - Alert notifications

**📊 Dashboard Data Format:**
```python
{
  "market_overview": {
    "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
    "last_update": "2025-09-11T14:30:15",
    "data_status": "live",
    "total_patterns": 24
  },
  "pattern_widgets": {
    "EURUSD": {
      "active_patterns": 8,
      "high_confidence": 3,
      "recent_signals": [...]
    }
  },
  "smart_money_widgets": {
    "session_analysis": "london_killzone",
    "liquidity_levels": [...],
    "institutional_sentiment": "bearish"
  }
}
```

---

## ⚡ **DATA FLOW TIMING & PERFORMANCE**

### **📊 Latency Benchmarks:**
| Stage | Component | Typical Latency | Max Acceptable |
|-------|-----------|----------------|----------------|
| **MT5 → Raw** | MT5DataManager | 50-200ms | 500ms |
| **Raw → Processed** | RealDataCollector | 100-300ms | 1000ms |
| **Processed → Patterns** | PatternDetector | 200-800ms | 2000ms |
| **Patterns → SmartMoney** | SmartMoneyAnalyzer | 100-400ms | 1000ms |
| **Signals → Dashboard** | Dashboard | 50-150ms | 300ms |
| **Total Pipeline** | End-to-End | 500-1850ms | 4800ms |

### **🔄 Update Frequencies:**
- **MT5 Data:** Real-time (tick-by-tick)
- **Pattern Analysis:** Every completed candle
- **Smart Money:** Every 5 minutes or on significant price moves
- **Dashboard UI:** Every 1-2 seconds
- **Cache Persistence:** Every 15 minutes

---

## 🛠️ **DATA FLOW MONITORING**

### **📊 Health Check Commands:**
```bash
# 1. Verificar pipeline completo
python -c "
import sys
sys.path.insert(0, '01-CORE')
sys.path.insert(0, '09-DASHBOARD')

# Test MT5 connection
from data_management.mt5_data_manager import MT5DataManager
mt5_manager = MT5DataManager()
print(f'✅ MT5: {mt5_manager.test_connection()}')

# Test data collection
from utils.real_data_collector import RealDataCollector
collector = RealDataCollector()
print(f'✅ DataCollector: {collector.validate_mt5_connection()}')

# Test pattern detection
from analysis.pattern_detector import PatternDetector
detector = PatternDetector()
print(f'✅ PatternDetector: {detector.get_system_status()[\"operational\"]}')

# Test dashboard data
import requests
try:
    response = requests.get('http://localhost:8050', timeout=5)
    print(f'✅ Dashboard: {response.status_code == 200}')
except:
    print('❌ Dashboard: Not accessible')
"

# 2. Verificar latencias
python -c "
import time
import sys
sys.path.insert(0, '01-CORE')

# Time full pipeline
start = time.time()

# Simulate data flow
from utils.real_data_collector import RealDataCollector
collector = RealDataCollector()
data = collector.get_market_data('EURUSD', ['H1'])

from analysis.pattern_detector import PatternDetector  
detector = PatternDetector()
patterns = detector.detect_patterns('EURUSD', data)

end = time.time()
print(f'Pipeline latency: {(end-start)*1000:.0f}ms')
"

# 3. Verificar calidad de datos
python -c "
import sys
sys.path.insert(0, '01-CORE')
from utils.data_quality_checker import check_data_quality
quality = check_data_quality()
print(f'Data quality score: {quality[\"overall_score\"]:.2f}')
for issue in quality.get('issues', []):
    print(f'⚠️ {issue}')
"
```

---

## 🚨 **TROUBLESHOOTING DATA FLOW**

### **❌ Issue: "No data flowing"**
```bash
# Diagnóstico paso a paso:
# 1. MT5 connection
python -c "import MetaTrader5 as mt5; print('MT5 OK' if mt5.initialize() else 'MT5 FAIL')"

# 2. Data retrieval  
python -c "
import MetaTrader5 as mt5
mt5.initialize()
rates = mt5.copy_rates_from_pos('EURUSD', mt5.TIMEFRAME_H1, 0, 10)
print(f'Data bars: {len(rates) if rates is not None else 0}')
"

# 3. Pipeline flow
python -c "
import sys
sys.path.insert(0, '01-CORE')
from utils.pipeline_diagnostics import test_full_pipeline
test_full_pipeline()
"
```

### **❌ Issue: "High latency"**
```bash
# Check system resources
python -c "
import psutil
print(f'CPU: {psutil.cpu_percent()}%')
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'Disk: {psutil.disk_usage(\".\").percent}%')
"

# Check cache performance
python -c "
import os
cache_files = len(os.listdir('04-DATA/cache'))
print(f'Cache files: {cache_files}')
"
```

### **❌ Issue: "Data inconsistencies"**
```bash
# Validate data integrity
python -c "
import sys
sys.path.insert(0, '01-CORE')
from utils.data_validator import validate_data_integrity
validator = validate_data_integrity()
if validator['valid']:
    print('✅ Data integrity OK')
else:
    for error in validator['errors']:
        print(f'❌ {error}')
"
```

---

## 📋 **DATA FLOW CHECKLIST**

### **✅ Pre-Trading Data Flow Verification:**
```
□ MT5 Terminal connected and authorized
□ MT5DataManager retrieving data successfully  
□ RealDataCollector processing without errors
□ PatternDetector finding patterns (>0 patterns)
□ SmartMoneyAnalyzer providing analysis
□ Dashboard displaying live data updates
□ End-to-end latency < 5 seconds
□ Data quality score > 90%
□ No critical errors in pipeline logs
□ Cache system functioning
```

### **🔄 Runtime Monitoring:**
```bash
# Ejecutar cada 30 minutos durante trading
python -c "
import sys
sys.path.insert(0, '01-CORE')
from utils.pipeline_monitor import runtime_health_check
health = runtime_health_check()
print(f'Pipeline Health: {health[\"status\"]}')
for warning in health.get('warnings', []):
    print(f'⚠️ {warning}')
"
```

---

*📊 Última actualización: 11 Septiembre 2025*  
*⚡ Pipeline latency objetivo: <2 segundos*  
*🎯 Data quality objetivo: >95%*
