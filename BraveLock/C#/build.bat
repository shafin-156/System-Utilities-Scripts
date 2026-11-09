@echo off
setlocal
cd /d "%~dp0"

if not exist "icon.ico" (
    echo ERROR: icon.ico not found next to build.bat
    pause & exit /b 1
)

set "CSC=%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
if not exist "%CSC%" set "CSC=%WINDIR%\Microsoft.NET\Framework\v4.0.30319\csc.exe"
if not exist "%CSC%" (
    echo ERROR: csc.exe not found. Install .NET Framework 4.x
    pause & exit /b 1
)

echo Compiling...
"%CSC%" /nologo /target:winexe /optimize+ ^
    /out:BraveService.exe ^
    /win32icon:icon.ico ^
    /resource:icon.ico,BraveService.icon.ico ^
    /r:System.Windows.Forms.dll /r:System.Drawing.dll ^
    BraveService.cs

if errorlevel 1 (
    echo.
    echo BUILD FAILED
    pause & exit /b 1
)

del /q BraveService.pdb 2>nul
echo.
echo BUILD SUCCESS : %CD%\BraveService.exe
pause