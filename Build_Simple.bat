@echo off
title Construction Installateur OCR - Simple

echo ================================================================
echo CONSTRUCTION INSTALLATEUR OCR INTELLIGENT - VERSION SIMPLE
echo ================================================================
echo.

:: Verification d'Inno Setup
echo Verification d'Inno Setup...
set "INNO_PATH="

if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    echo Inno Setup 6 trouve
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
    echo Inno Setup 6 trouve
) else (
    echo ERREUR: Inno Setup n'est pas installe
    echo.
    echo Telechargez Inno Setup depuis: https://jrsoftware.org/isdl.php
    echo Installez-le puis relancez ce script
    echo.
    pause
    exit /b 1
)

:: Verification du script
echo Verification du script Inno Setup...
if not exist "OCR_Intelligent_Setup.iss" (
    echo ERREUR: OCR_Intelligent_Setup.iss manquant
    pause
    exit /b 1
)
echo Script trouve

:: Creation du dossier dist
if not exist "dist" mkdir "dist"

:: Construction
echo.
echo Construction en cours...
echo Patientez...
echo.

"%INNO_PATH%" "OCR_Intelligent_Setup.iss"

if errorlevel 1 (
    echo.
    echo ERREUR: Construction echouee
    pause
    exit /b 1
)

:: Verification du resultat
if exist "dist\OCR_Intelligent_Setup_v2.0.0.exe" (
    echo.
    echo ================================================================
    echo SUCCES !
    echo ================================================================
    echo.
    echo Installateur cree: dist\OCR_Intelligent_Setup_v2.0.0.exe
    echo.
    echo Voulez-vous ouvrir le dossier ? (O/N)
    set /p choice=
    if /i "%choice%"=="O" explorer "dist"
) else (
    echo.
    echo ERREUR: Installateur non trouve
)

echo.
echo Construction terminee
pause
