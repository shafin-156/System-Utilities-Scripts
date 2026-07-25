@echo off
:: Set console window to the smallest practical size (approx 20 columns by 2 lines)
mode con: cols=40 lines=5

:: Set the working directory
cd /d "%~dp0"

:: Run the script
py -3 github_uploader.py --windowed

echo Process complete.
pause