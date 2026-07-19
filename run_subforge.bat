@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

rem Optional: set this to the remote repository URL you want to push to.
rem If empty, the script will push to the existing 'origin' remote.
set "GIT_REMOTE_URL=https://github.com/rb360full/SubForge.git"

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

rem Ask whether to commit and push changes (default: Y). Only 'N' or 'n' means No; Enter or anything else means Yes.
set "GIT_CONFIRM="
set /p GIT_CONFIRM=Do you want to commit and push changes? [Y/n] (default Y): 
set "GIT_FIRSTCHAR=%GIT_CONFIRM:~0,1%"
if "%GIT_FIRSTCHAR%"=="" set "GIT_FIRSTCHAR=Y"

if /I "%GIT_FIRSTCHAR%"=="N" (
    echo Skipping commit and push.
) else (
    git --version >nul 2>&1
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
            rem Push directly to the configured remote URL if provided; otherwise push to origin.
            rem Prefer pushing to 'origin' remote if it exists, otherwise push to configured URL if provided.
            git remote get-url origin >nul 2>&1
            if %ERRORLEVEL% EQU 0 (
                rem origin exists — push to origin
                rem Determine current branch
                set "CURRENT_BRANCH="
                for /f "delims=" %%B in ('git rev-parse --abbrev-ref HEAD') do set "CURRENT_BRANCH=%%B"
                if "!CURRENT_BRANCH!"=="" (
                    echo Could not determine current branch; pushing HEAD to origin...
                    git push origin HEAD
                ) else (
                    echo Pushing to origin on branch !CURRENT_BRANCH!...
                    git push origin HEAD:refs/heads/!CURRENT_BRANCH!
                )
                if %ERRORLEVEL% NEQ 0 (
                    echo Push to origin failed. Trying configured URL if available.
                    if not "%GIT_REMOTE_URL%"=="" (
                        git push "%GIT_REMOTE_URL%" HEAD:refs/heads/!CURRENT_BRANCH!
                    )
                )
            ) else (
                if not "%GIT_REMOTE_URL%"=="" (
                    rem Determine current branch
                    set "CURRENT_BRANCH="
                    for /f "delims=" %%B in ('git rev-parse --abbrev-ref HEAD') do set "CURRENT_BRANCH=%%B"
                    if "!CURRENT_BRANCH!"=="" (
                        echo Could not determine current branch; pushing HEAD to URL without branch name...
                        git push "%GIT_REMOTE_URL%" HEAD
                    ) else (
                        echo Pushing to %GIT_REMOTE_URL% on branch !CURRENT_BRANCH!...
                        git push "%GIT_REMOTE_URL%" HEAD:refs/heads/!CURRENT_BRANCH!
                    )
                    if %ERRORLEVEL% NEQ 0 (
                        echo Push failed. Please check your remote URL and access rights.
                    )
                ) else (
                    echo No 'origin' remote and no configured URL; attempting default push...
                    git push
                )
            )
        ) else (
            echo No changes to commit.
        )
    )
)

echo.
echo Press any key to close this window...
pause >nul
exit /b 0
