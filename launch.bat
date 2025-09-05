@echo off
REM ============================================
REM ICT ENGINE v6.0 ENTERPRISE - LAUNCHER BAT
REM ============================================

title ICT Engine v6.0 Enterprise SIC

echo.
echo =============================================
echo   ICT ENGINE v6.0 ENTERPRISE SIC
echo =============================================
echo.
echo Iniciando sistema...
echo.

REM Verificar que Python esté disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instala Python 3.8+ y agregalo al PATH.
    pause
    exit /b 1
)

REM Ejecutar el main launcher
python main.py

echo.
echo Sistema finalizado.
pause
