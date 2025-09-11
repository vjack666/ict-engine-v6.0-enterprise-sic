# 🚀 ICT ENGINE v6.0 - ENTERPRISE DEPLOYMENT

**🏢 Despliegue en producción empresarial y scaling**
**⚡ De desarrollo a producción enterprise en 30 minutos**

---

## 🎯 **DEPLOYMENT OVERVIEW**

### **📊 Enterprise Specifications:**
```
Target Environment: Windows Production Servers
Concurrent Users: 1-50 traders
Data Throughput: 10,000+ ticks/minute
Uptime Requirement: 99.9% (4.3 minutes downtime/month)
Recovery Time: <2 minutes
Backup Frequency: Every 15 minutes
```

---

## 🏗️ **ARCHITECTURE DEPLOYMENT**

### **🖥️ Deployment Architecture:**
```
[Load Balancer] (Optional)
     ↓
[Primary Trading Server]
     ├── ICT Engine Core (Port 8000)
     ├── Dashboard Service (Port 8050) 
     ├── MT5 Connection Pool (Ports 8100-8110)
     └── Data Cache Service (Port 8200)
     
[Backup Trading Server] (Hot Standby)
     └── Mirror of Primary (automated sync)
     
[Database Server] (Optional - PostgreSQL)
     └── Historical data + performance metrics
     
[Monitoring Server]
     └── System health + alert management
```

---

## 📦 **PRE-DEPLOYMENT PREPARATION**

### **🔧 Server Requirements:**
```bash
# Minimum Hardware:
CPU: 4 cores, 3.0GHz+
RAM: 16GB (32GB recommended)
Storage: 500GB SSD (1TB recommended)
Network: 100Mbps stable connection
OS: Windows 10/11 Pro or Windows Server 2019+

# Software Prerequisites:
Python 3.9+ (3.11 recommended)
MetaTrader 5 Terminal
Visual C++ Redistributable
.NET Framework 4.8+
```

### **🛠️ Environment Preparation:**
```bash
# 1. Create deployment user
net user ict_engine /add /passwordreq:yes
net localgroup "Remote Desktop Users" ict_engine /add

# 2. Create directory structure
mkdir C:\ICT_Engine_Production
mkdir C:\ICT_Engine_Production\logs
mkdir C:\ICT_Engine_Production\data
mkdir C:\ICT_Engine_Production\config
mkdir C:\ICT_Engine_Production\backups

# 3. Set permissions
icacls "C:\ICT_Engine_Production" /grant "ict_engine:(OI)(CI)F"

# 4. Install Python requirements
python -m pip install --upgrade pip
pip install virtualenv
```

---

## 🚀 **DEPLOYMENT PROCESS**

### **📥 Stage 1: Code Deployment**
```bash
# 1. Clone/copy production code
cd C:\ICT_Engine_Production
git clone https://github.com/vjack666/ict-engine-v6.0-enterprise-sic.git
# OR copy from development environment

# 2. Create virtual environment
cd ict-engine-v6.0-enterprise-sic
python -m venv venv_production
venv_production\Scripts\activate

# 3. Install dependencies
pip install -r 00-ROOT/requirements.txt
pip install gunicorn waitress  # Production WSGI servers
pip install psycopg2-binary     # If using PostgreSQL

# 4. Set production environment
set ENVIRONMENT=production
set LOG_LEVEL=INFO
set DASHBOARD_HOST=0.0.0.0
set DASHBOARD_PORT=8050
```

### **⚙️ Stage 2: Configuration Setup**
```bash
# 1. Copy production configurations
copy "deployment\configs\production\*" "01-CORE\config\"
copy "deployment\configs\dashboard\*" "09-DASHBOARD\config\"

# 2. Configure production database (if using)
# Edit 01-CORE/config/database_config.json:
{
  "database": {
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "ict_engine_prod",
    "username": "ict_user",
    "password": "secure_password"
  }
}

# 3. Set production secrets
# Create 01-CORE/config/secrets.json:
{
  "mt5_accounts": [
    {
      "login": 123456789,
      "password": "account_password",
      "server": "broker_server"
    }
  ],
  "api_keys": {
    "monitoring": "monitoring_api_key",
    "alerts": "alert_service_key"
  }
}

# 4. Configure firewall
netsh advfirewall firewall add rule name="ICT Engine Core" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="ICT Dashboard" dir=in action=allow protocol=TCP localport=8050
```

### **🔄 Stage 3: Service Installation**
```bash
# 1. Install as Windows Service using NSSM
# Download NSSM (Non-Sucking Service Manager)
# https://nssm.cc/download

# 2. Install ICT Engine Core Service
nssm install "ICT Engine Core" "C:\ICT_Engine_Production\ict-engine-v6.0-enterprise-sic\venv_production\Scripts\python.exe"
nssm set "ICT Engine Core" Arguments "C:\ICT_Engine_Production\ict-engine-v6.0-enterprise-sic\main.py"
nssm set "ICT Engine Core" AppDirectory "C:\ICT_Engine_Production\ict-engine-v6.0-enterprise-sic"
nssm set "ICT Engine Core" DisplayName "ICT Engine Core v6.0"
nssm set "ICT Engine Core" Description "ICT Trading Engine Core Service"
nssm set "ICT Engine Core" Start SERVICE_AUTO_START

# 3. Install Dashboard Service
nssm install "ICT Dashboard" "C:\ICT_Engine_Production\ict-engine-v6.0-enterprise-sic\venv_production\Scripts\python.exe"
nssm set "ICT Dashboard" Arguments "C:\ICT_Engine_Production\ict-engine-v6.0-enterprise-sic\09-DASHBOARD\start_dashboard.py"
nssm set "ICT Dashboard" AppDirectory "C:\ICT_Engine_Production\ict-engine-v6.0-enterprise-sic"
nssm set "ICT Dashboard" DisplayName "ICT Dashboard v6.0"
nssm set "ICT Dashboard" Start SERVICE_AUTO_START

# 4. Start services
sc start "ICT Engine Core"
sc start "ICT Dashboard"
```

---

## 📊 **PRODUCTION MONITORING**

### **🔍 Health Monitoring Setup:**
```bash
# 1. Create monitoring script
# File: C:\ICT_Engine_Production\monitoring\health_check.py
import requests
import json
import time
from datetime import datetime

def health_check():
    checks = {
        "core_service": check_core_service(),
        "dashboard": check_dashboard(),
        "mt5_connection": check_mt5(),
        "data_flow": check_data_flow(),
        "disk_space": check_disk_space(),
        "memory_usage": check_memory()
    }
    
    # Log results
    with open("C:/ICT_Engine_Production/logs/health_check.json", "a") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "overall_health": all(checks.values())
        }, f)
    
    return checks

# 2. Schedule health checks (Task Scheduler)
schtasks /create /tn "ICT Health Check" /tr "C:\ICT_Engine_Production\venv_production\Scripts\python.exe C:\ICT_Engine_Production\monitoring\health_check.py" /sc minute /mo 5
```

### **📈 Performance Monitoring:**
```bash
# 1. Windows Performance Counters
# Create performance monitoring script
# File: C:\ICT_Engine_Production\monitoring\performance_monitor.py

import psutil
import json
from datetime import datetime

def collect_metrics():
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("C:").percent,
        "network_io": psutil.net_io_counters()._asdict(),
        "process_count": len(psutil.pids())
    }
    
    # Store in time-series format
    with open("C:/ICT_Engine_Production/logs/performance_metrics.json", "a") as f:
        json.dump(metrics, f)
        f.write("\n")

# 2. Schedule performance collection
schtasks /create /tn "ICT Performance Monitor" /tr "C:\ICT_Engine_Production\venv_production\Scripts\python.exe C:\ICT_Engine_Production\monitoring\performance_monitor.py" /sc minute /mo 1
```

---

## 🔄 **BACKUP & RECOVERY**

### **💾 Automated Backup System:**
```bash
# 1. Create backup script
# File: C:\ICT_Engine_Production\scripts\backup.bat

@echo off
set BACKUP_DIR=C:\ICT_Engine_Production\backups\%date:~6,4%-%date:~3,2%-%date:~0,2%
mkdir "%BACKUP_DIR%"

REM Backup configuration files
xcopy "C:\ICT_Engine_Production\ict-engine-v6.0-enterprise-sic\01-CORE\config" "%BACKUP_DIR%\config" /s /e /i

REM Backup data files
xcopy "C:\ICT_Engine_Production\ict-engine-v6.0-enterprise-sic\04-DATA" "%BACKUP_DIR%\data" /s /e /i

REM Backup logs (last 7 days)
forfiles /p "C:\ICT_Engine_Production\ict-engine-v6.0-enterprise-sic\05-LOGS" /m *.log /d -7 /c "cmd /c copy @path \"%BACKUP_DIR%\logs\""

REM Compress backup
powershell "Compress-Archive -Path '%BACKUP_DIR%' -DestinationPath '%BACKUP_DIR%.zip'"
rmdir /s /q "%BACKUP_DIR%"

REM Clean old backups (keep 30 days)
forfiles /p "C:\ICT_Engine_Production\backups" /m *.zip /d -30 /c "cmd /c del @path"

# 2. Schedule backup (every 4 hours)
schtasks /create /tn "ICT Backup" /tr "C:\ICT_Engine_Production\scripts\backup.bat" /sc hourly /mo 4
```

### **🚨 Disaster Recovery:**
```bash
# 1. Emergency recovery script
# File: C:\ICT_Engine_Production\scripts\emergency_recovery.bat

@echo off
echo [EMERGENCY RECOVERY] Starting system recovery...

REM Stop services
sc stop "ICT Engine Core"
sc stop "ICT Dashboard"

REM Restore from backup
set /p BACKUP_DATE="Enter backup date (YYYY-MM-DD): "
set BACKUP_FILE=C:\ICT_Engine_Production\backups\%BACKUP_DATE%.zip

if exist "%BACKUP_FILE%" (
    powershell "Expand-Archive -Path '%BACKUP_FILE%' -DestinationPath 'C:\ICT_Engine_Production\recovery'"
    
    REM Restore configuration
    xcopy "C:\ICT_Engine_Production\recovery\config" "C:\ICT_Engine_Production\ict-engine-v6.0-enterprise-sic\01-CORE\config" /s /e /y
    
    REM Restore data
    xcopy "C:\ICT_Engine_Production\recovery\data" "C:\ICT_Engine_Production\ict-engine-v6.0-enterprise-sic\04-DATA" /s /e /y
    
    REM Restart services
    sc start "ICT Engine Core"
    sc start "ICT Dashboard"
    
    echo [RECOVERY] System restored from backup %BACKUP_DATE%
) else (
    echo [ERROR] Backup file not found: %BACKUP_FILE%
)
```

---

## 🔒 **SECURITY & HARDENING**

### **🛡️ Security Hardening:**
```bash
# 1. Network Security
# Configure Windows Defender Firewall
netsh advfirewall set allprofiles state on
netsh advfirewall firewall set rule group="Remote Desktop" new enable=no

# Allow only necessary ports
netsh advfirewall firewall add rule name="ICT Core HTTPS" dir=in action=allow protocol=TCP localport=8000
netsh advfirewall firewall add rule name="ICT Dashboard" dir=in action=allow protocol=TCP localport=8050

# 2. File System Security
# Set restrictive permissions
icacls "C:\ICT_Engine_Production\ict-engine-v6.0-enterprise-sic\01-CORE\config\secrets.json" /grant "ict_engine:F" /inheritance:r

# 3. Process Security
# Run services with limited privileges
sc config "ICT Engine Core" obj= ".\ict_engine" password= "service_password"
sc config "ICT Dashboard" obj= ".\ict_engine" password= "service_password"

# 4. Audit Logging
auditpol /set /category:"Logon/Logoff" /success:enable /failure:enable
auditpol /set /category:"Object Access" /success:enable /failure:enable
```

### **🔐 SSL/TLS Configuration:**
```bash
# 1. Generate SSL certificate (if needed)
# Use Let's Encrypt or internal CA

# 2. Configure HTTPS for dashboard
# Edit 09-DASHBOARD/config/dashboard_config.json:
{
  "server": {
    "host": "0.0.0.0",
    "port": 8050,
    "ssl_context": {
      "cert_file": "C:/ICT_Engine_Production/ssl/server.crt",
      "key_file": "C:/ICT_Engine_Production/ssl/server.key"
    }
  }
}
```

---

## 📈 **SCALING & PERFORMANCE**

### **🚀 Horizontal Scaling:**
```bash
# 1. Load Balancer Configuration (NGINX)
# File: C:\nginx\conf\nginx.conf

upstream ict_dashboard {
    server 192.168.1.10:8050;
    server 192.168.1.11:8050;
    server 192.168.1.12:8050;
}

server {
    listen 80;
    server_name ict-trading.company.com;
    
    location / {
        proxy_pass http://ict_dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# 2. Database Scaling (if using PostgreSQL)
# Master-Slave replication configuration
# File: C:\PostgreSQL\13\data\postgresql.conf
wal_level = replica
max_wal_senders = 3
wal_keep_segments = 64
```

### **⚡ Performance Optimization:**
```bash
# 1. Memory Optimization
# Edit main.py startup parameters
set PYTHONOPTIMIZE=1
set MALLOC_ARENA_MAX=2

# 2. CPU Optimization  
# Set CPU affinity for core processes
start /affinity 3 python main.py  # Use cores 0,1
start /affinity 12 python 09-DASHBOARD/start_dashboard.py  # Use cores 2,3

# 3. I/O Optimization
# Move cache to SSD, logs to HDD
mklink /d "04-DATA\cache" "D:\ICT_SSD_Cache"
mklink /d "05-LOGS" "E:\ICT_HDD_Logs"
```

---

## 📋 **DEPLOYMENT CHECKLIST**

### **✅ Pre-Deployment:**
```
□ Server hardware meets requirements
□ Windows OS updated and hardened
□ Python 3.9+ installed
□ Virtual environment created
□ Dependencies installed
□ Production configuration files ready
□ SSL certificates obtained (if using HTTPS)
□ Firewall rules configured
□ Backup strategy planned
□ Monitoring scripts prepared
```

### **✅ Deployment Execution:**
```
□ Code deployed to production directory
□ Configuration files copied and customized
□ Services installed (NSSM)
□ Services started successfully
□ Health checks passing
□ Dashboard accessible from external network
□ MT5 connections established
□ Data flowing correctly
□ Backup schedule activated
□ Monitoring alerts configured
```

### **✅ Post-Deployment:**
```
□ Load testing completed
□ Performance benchmarks met
□ Security scan passed
□ Documentation updated
□ Team training completed
□ Incident response procedures defined
□ Rollback plan tested
□ 48-hour monitoring period completed
```

---

## 🚨 **TROUBLESHOOTING DEPLOYMENT**

### **❌ Common Deployment Issues:**

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **Service won't start** | Service fails immediately | Check NSSM configuration, Python path, permissions |
| **Dashboard not accessible** | External users can't connect | Verify firewall rules, Windows Defender settings |
| **MT5 connection fails** | No market data | Check MT5 account credentials, server settings |
| **High memory usage** | System becomes slow | Tune memory settings, check for memory leaks |
| **SSL certificate errors** | HTTPS warnings | Verify certificate chain, update certificate |

### **🔧 Deployment Diagnostics:**
```bash
# 1. Service Status Check
sc query "ICT Engine Core"
sc query "ICT Dashboard"

# 2. Network Connectivity
netstat -an | findstr :8050
telnet localhost 8050

# 3. Logs Analysis
type "05-LOGS\application\app_%date:~6,4%%date:~3,2%%date:~0,2%.log" | findstr ERROR
type "C:\ICT_Engine_Production\logs\health_check.json" | tail -10

# 4. Performance Check
tasklist | findstr python.exe
wmic process where "name='python.exe'" get ProcessId,WorkingSetSize
```

---

*🏢 Última actualización: 11 Septiembre 2025*  
*🚀 Deployment time: 30 minutos (sin SSL/database)*  
*⚡ Production ready: 99.9% uptime target*
