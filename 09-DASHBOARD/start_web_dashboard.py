"""Deprecated starter script: web dashboard removed.

This file intentionally kept as a no-op placeholder to avoid
breakage in environments where old automation might still call it.
"""

def main():  # pragma: no cover
    raise RuntimeError("start_web_dashboard deprecated and removed. Use terminal dashboard tooling.")

if __name__ == "__main__":  # pragma: no cover
    main()

for path in paths_to_add:
    if path not in sys.path:
        sys.path.append(path)

print("🎯 ICT ENGINE v6.0 ENTERPRISE - WEB DASHBOARD STARTER")
print("=" * 55)
print(f"📁 Project root: {project_root}")
print(f"🗂️ Dashboard root: {current_dir}")
print(f"⚙️ Python: {sys.version}")
print()


def check_dependencies():
    """Verificar dependencias requeridas"""
    missing_deps = []
    
    # Check Dash framework
    try:
        import dash
        import plotly
        import pandas as pd
        print("✅ Dash framework available")
    except ImportError:
        missing_deps.append("dash plotly pandas")
        print("❌ Dash framework missing")
    
    # Check core components
    try:
        from core.tabs.order_blocks_tab import OrderBlocksTab
        print("✅ Order Blocks Tab available")
    except ImportError as e:
        print(f"⚠️ Order Blocks Tab issue: {e}")
    
    if missing_deps:
        print(f"\n💡 Install missing dependencies:")
        print(f"   pip install {' '.join(missing_deps)}")
        return False
    
    return True


def start_dashboard(config=None):
    """Iniciar el dashboard web"""
    
    # Default configuration
    default_config = {
        'refresh_interval': 500,  # ms
        'host': '127.0.0.1',
        'port': 8050,
        'debug': True,
        'default_tab': 'order_blocks'
    }
    
    if config:
        default_config.update(config)
    
    try:
        # Import and create dashboard
        from web_dashboard import create_web_dashboard
        
        print("🏗️ Creating web dashboard...")
        dashboard = create_web_dashboard(default_config)
        
        print("🔧 Configuring components...")
        print(f"   Refresh interval: {default_config['refresh_interval']}ms")
        print(f"   Default tab: {default_config['default_tab']}")
        print(f"   Debug mode: {default_config['debug']}")
        
        print("\n🚀 Starting web server...")
        print(f"   URL: http://{default_config['host']}:{default_config['port']}")
        print("   Press Ctrl+C to stop")
        print()
        
        # Start the dashboard
        dashboard.run()
        
    except KeyboardInterrupt:
        print("\n⏹️ Dashboard stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all files are in place and dependencies installed")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Función principal"""
    print("🔍 Checking system requirements...")
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install them first.")
        return
    
    print("\n✅ All requirements met!")
    print("\n" + "=" * 50)
    
    # Optional: Custom configuration
    custom_config = {
        'refresh_interval': 500,  # Fast refresh for real-time data
        'debug': True,           # Enable debug mode
        'port': 8050            # Default port
    }
    
    # Check if port is in use
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((custom_config['host'] if 'host' in custom_config else '127.0.0.1', 
                                 custom_config['port']))
        sock.close()
        if result == 0:
            print(f"⚠️ Port {custom_config['port']} is in use, trying port 8051...")
            custom_config['port'] = 8051
    except:
        pass
    
    # Start dashboard
    start_dashboard(custom_config)


if __name__ == "__main__":
    main()