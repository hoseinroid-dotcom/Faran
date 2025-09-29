@echo off
chcp 65001
echo Starting Faran Payroll System in debug mode...
echo.
python -u main.py
echo.
echo Program exited with code: %errorlevel%
pause