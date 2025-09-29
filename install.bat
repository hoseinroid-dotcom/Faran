@echo off
chcp 65001
echo ========================================
echo    Faran Payroll System Installer
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from python.org
    pause
    exit /b 1
)

echo Python found!
echo.

echo Installing dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Installation Completed Successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure PostgreSQL is installed and running
echo 2. Create a database named 'faran_payroll'
echo 3. Update database settings in config/settings.json
echo 4. Run the program using run.bat
echo.
pause