#!/usr/bin/env python3
"""
🚀 LAUNCH RISK MONITOR - ICT Engine v6.0 Enterprise
================================================

Script de lanzamiento del dashboard de monitoreo de riesgo.
Detecta automáticamente si streamlit está disponible o usa modo fallback.

Uso:
    python launch_risk_monitor.py [--install-deps]
    
Opciones:
    --install-deps    Instala dependencias automáticamente
"""

import sys
import subprocess
from pathlib import Path
import argparse
import importlib.util

def check_dependencies():
    """Verificar dependencias necesarias"""
    dependencies = {
        'streamlit': 'streamlit>=1.28.0',
        'plotly': 'plotly>=5.15.0',
        'pandas': 'pandas>=2.0.0'
    }
    
    missing = []
    for dep, package in dependencies.items():
        try:
            __import__(dep)
            print(f"✅ {dep} - Available")
        except ImportError:
            print(f"❌ {dep} - Missing")
            missing.append(package)
    
    return missing

def install_dependencies(packages):
    """Instalar dependencias faltantes"""
    if not packages:
        return True
    
    print(f"📦 Installing {len(packages)} dependencies...")
    try:
        for package in packages:
            print(f"   Installing {package}...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ {package} installed")
            else:
                print(f"   ❌ Failed to install {package}")
                print(f"   Error: {result.stderr}")
                return False
        return True
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def run_dashboard():
    """Ejecutar dashboard"""
    print("🚀 Launching ICT Risk Monitor...")
    
    # Verificar si streamlit está disponible usando importlib
    streamlit_spec = importlib.util.find_spec('streamlit')
    streamlit_available = streamlit_spec is not None
    
    dashboard_path = Path(__file__).parent / "risk_monitor.py"
    
    if streamlit_available:
        # Ejecutar con streamlit web UI
        print("✅ Streamlit available - launching web UI")
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", str(dashboard_path),
                "--server.port", "8501",
                "--server.headless", "true",
                "--server.address", "localhost"
            ])
        except Exception as e:
            print(f"❌ Error launching streamlit: {e}")
            print("🔄 Falling back to console mode...")
            subprocess.run([sys.executable, str(dashboard_path)])
    else:
        # Ejecutar en modo fallback console
        print("⚠️ Streamlit not available - running in console mode")
        subprocess.run([sys.executable, str(dashboard_path)])

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Launch ICT Risk Monitor Dashboard")
    parser.add_argument('--install-deps', action='store_true', 
                       help='Install missing dependencies automatically')
    args = parser.parse_args()
    
    print("🛡️ ICT Engine v6.0 Enterprise - Risk Monitor Launcher")
    print("=" * 60)
    
    # Verificar dependencias
    missing = check_dependencies()
    
    if missing:
        if args.install_deps:
            success = install_dependencies(missing)
            if not success:
                print("❌ Failed to install dependencies")
                return 1
        else:
            print(f"\n⚠️ Missing dependencies: {len(missing)}")
            print("   Run with --install-deps to install automatically")
            print("   Or install manually:")
            for package in missing:
                print(f"     pip install {package}")
            print("\n   Dashboard will run in fallback mode")
    
    # Ejecutar dashboard
    run_dashboard()
    return 0

if __name__ == "__main__":
    sys.exit(main())
