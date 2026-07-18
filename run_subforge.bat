@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=py -3"
) else (
    set "PYTHON_CMD=python"
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
)

call ".venv\Scripts\activate.bat"

python -m pip install --upgrade pip >nul 2>&1
python -m pip install -e . >nul 2>&1
python -m pip install -r requirements.txt >nul 2>&1

echo Running SubForge...
python src\runner.py

if errorlevel 1 (
    echo.
    echo SubForge exited with an error.
    pause
)

exit /b %ERRORLEVEL%
