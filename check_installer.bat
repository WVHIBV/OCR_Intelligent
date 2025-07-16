@echo off
title OCR Intelligent Installer Verification

echo ================================================================
echo OCR INTELLIGENT INSTALLER VERIFICATION
echo ================================================================
echo.

echo [STEP] Checking Inno Setup installation...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo [OK] Inno Setup 6 found
    set INNO_OK=1
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    echo [OK] Inno Setup 6 found
    set INNO_OK=1
) else (
    echo [MISSING] Inno Setup not installed
    set INNO_OK=0
)

echo.
echo [STEP] Checking project files...
set FILES_OK=1

if exist "main.py" (
    echo [OK] main.py
) else (
    echo [MISSING] main.py
    set FILES_OK=0
)

if exist "Lancer_OCR_Intelligent.bat" (
    echo [OK] Lancer_OCR_Intelligent.bat
) else (
    echo [MISSING] Lancer_OCR_Intelligent.bat
    set FILES_OK=0
)

if exist "OCR_Intelligent_Setup.iss" (
    echo [OK] OCR_Intelligent_Setup.iss
) else (
    echo [MISSING] OCR_Intelligent_Setup.iss
    set FILES_OK=0
)

if exist "frontend\app.py" (
    echo [OK] frontend\app.py
) else (
    echo [MISSING] frontend\app.py
    set FILES_OK=0
)

if exist "requirements.txt" (
    echo [OK] requirements.txt
) else (
    echo [MISSING] requirements.txt
    set FILES_OK=0
)

echo.
echo [STEP] Checking Python and dependencies...
python --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python not found in PATH
    echo Make sure Python 3.8+ is installed
) else (
    echo [OK] Python is available
    python --version
)

echo.
echo ================================================================
echo SUMMARY
echo ================================================================

if %INNO_OK%==1 (
    echo Inno Setup: INSTALLED
) else (
    echo Inno Setup: NOT INSTALLED
)

if %FILES_OK%==1 (
    echo Project Files: COMPLETE
) else (
    echo Project Files: INCOMPLETE
)

echo.

if %INNO_OK%==1 (
    if %FILES_OK%==1 (
        echo READY TO CREATE INSTALLER!
        echo.
        echo To create the installer:
        echo 1. Run build_installer.bat
        echo 2. Wait for compilation
        echo 3. Find installer in dist\ folder
        echo.
        echo Optional: Run verify_dependencies.py first to check Python setup
    ) else (
        echo Missing files - check project structure
    )
) else (
    echo INNO SETUP INSTALLATION REQUIRED
    echo.
    echo Steps:
    echo 1. Go to: https://jrsoftware.org/isdl.php
    echo 2. Download Inno Setup 6
    echo 3. Install with default options
    echo 4. Run this script again
    echo.
    echo Do you want to open the download page? (Y/N)
    set /p choice=
    if /i "%choice%"=="Y" start https://jrsoftware.org/isdl.php
)

echo.
pause
