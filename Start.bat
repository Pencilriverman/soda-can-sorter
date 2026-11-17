@echo off
setlocal
cd /d "%~dp0"
if not exist "GTA-AutoClip.exe" if exist "dist\GTA-AutoClip-Studio\GTA-AutoClip.exe" cd /d "%~dp0dist\GTA-AutoClip-Studio"
if not exist "GTA-AutoClip.exe" (
    echo Studio launcher is missing from "%~dp0".
    echo Extract the entire ZIP to a writable folder, then run Start.bat from there.
    pause
    exit /b 1
)
start "" /wait /d "%CD%\." "%CD%\GTA-AutoClip.exe" %*
if errorlevel 1 (
    echo Studio could not start. Check startup-error.log and launcher.log in this folder.
    pause
    exit /b 1
)
