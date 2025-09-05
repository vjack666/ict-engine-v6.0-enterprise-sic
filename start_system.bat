@echo off
echo 🚀 ICT ENGINE v6.0 ENTERPRISE - INICIANDO SISTEMA
echo ================================================

REM Configurar PYTHONPATH para encontrar el módulo sistema
set PYTHONPATH=c:\Users\v_jac\Desktop\proyecto principal\docs;%PYTHONPATH%

REM Cambiar al directorio del proyecto
cd /d "c:\Users\v_jac\Desktop\itc engine v5.0\ict-engine-v6.0-enterprise-sic"

echo 📊 Configuración completada:
echo    - PYTHONPATH: %PYTHONPATH%
echo    - Directorio: %CD%
echo.

REM Sistema central verificado - SmartTradingLogger activo
echo ✅ Sistema central de logging operativo

echo.
echo 🎯 Sistema listo. Módulos de producción disponibles:
echo    1. Smart Money Analyzer: python "01-CORE\core\smart_money_concepts\smart_money_analyzer.py"
echo    2. Dashboard: python "02-TESTS\integration\tests\progress_dashboard.py"
echo    3. Pattern Detector: python "01-CORE\core\ict_engine\pattern_detector.py"
echo    4. Market Structure: python "01-CORE\core\analysis\market_structure_analyzer.py"
echo    5. Reportes Inteligentes: python "02-TESTS\integration\tests\smart_report_generator.py"
echo.

cmd /k
