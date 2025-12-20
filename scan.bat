@echo off
setlocal enabledelayedexpansion

:: Start Ubuntu WSL with a short keep-alive so it stays running
echo Starting Ubuntu WSL (Ubuntu distro)...
wsl -d Ubuntu bash -c "sleep 30"

echo Attaching scanner to WSL...
powershell -Command "usbipd attach --wsl --busid 2-1"

:: Ensure config file exists
if not exist scan_settings.txt (
    echo --resolution 75 --mode Color --format=jpeg > scan_settings.txt
)

:SCAN_LOOP
for /f "tokens=* delims=" %%i in (scan_settings.txt) do set SCANSETTINGS=%%i
for /f %%t in ('powershell -command "Get-Date -Format yyyy.MM.dd_HH.mm.ss"') do set DATETIME=%%t

echo Running scan with settings: %SCANSETTINGS%
wsl -d Ubuntu bash -c "lsusb && scanimage -L && scanimage %SCANSETTINGS% > /mnt/c/Users/Admin/Pictures/scan_%DATETIME%.jpg"

echo.
echo Scan complete. Saved to Pictures\scan_%DATETIME%.jpg
echo.

choice /c SN /m "Do you want to (S)can another or (N)exit?"
if errorlevel 2 goto END
if errorlevel 1 goto SCAN_LOOP

:END
echo Shutting down WSL...
wsl --shutdown
echo Exiting scanner script.
pause