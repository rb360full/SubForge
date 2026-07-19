@echo off
setlocal
cd /d "%~dp0"

rem Optional: set this to the remote repository URL you want to push to.
rem If empty, the script will push to the existing 'origin' remote.
set "GIT_REMOTE_URL="

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
    echo Press any key to close this window...
    pause >nul
    exit /b %ERRORLEVEL%
)

echo.
echo SubForge finished successfully.

rem Ask whether to commit and push changes (default: Y)
set "GIT_CONFIRM="
set /p GIT_CONFIRM=Do you want to commit and push changes? [Y/n] (default Y): 
if "%GIT_CONFIRM%"=="" set "GIT_CONFIRM=Y"

if /I "%GIT_CONFIRM:~0,1%"=="Y" (
    where git >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Git not found in PATH; skipping commit/push.
    ) else (
        echo Staging changes...
        git add -A
        set "CHANGES="
        for /f "delims=" %%A in ('git status --porcelain') do set "CHANGES=1"
        if defined CHANGES (
            echo Committing changes...
            git commit -m "Automated commit after running SubForge"
            echo Pushing to remote...
            git push
        ) else (
            echo No changes to commit.
        )
    )
) else (
    echo Skipping commit and push.
)

echo.
echo Press any key to close this window...
pause >nul
exit /b 0
