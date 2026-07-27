@echo off
:: Set console window to the smallest practical size (approx 20 columns by 2 lines)
mode con: cols=40 lines=5

:: Set the working directory
cd /d "%~dp0"

:: Check if the script exists
if not exist "build_exe\auto_build_exe.py" (
    echo Error: File not found.
    pause
    exit /b 1
)

:: Run the script
py -3 build_exe\auto_build_exe.py --windowed

echo Process complete.
pause