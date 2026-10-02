@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo Syntax Sage virtual environment was not found.
    echo.
    echo Create it with:
    echo python -m venv .venv
    echo.
    echo Then install dependencies with:
    echo .venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m app.main

echo.
pause