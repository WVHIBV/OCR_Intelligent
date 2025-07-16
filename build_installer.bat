@echo off
setlocal enabledelayedexpansion

title Construction Installateur OCR Intelligent

echo ================================================================
echo CONSTRUCTION INSTALLATEUR OCR INTELLIGENT
echo ================================================================
echo Creation d'un fichier .exe unique pour la distribution
echo ================================================================
echo.

:: Verification d'Inno Setup
echo [ETAPE] Verification d'Inno Setup...
set "INNO_PATH="

if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    echo [OK] Inno Setup 6 trouve: C:\Program Files (x86)\Inno Setup 6\
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
    echo [OK] Inno Setup 6 trouve: C:\Program Files\Inno Setup 6\
) else if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set "INNO_PATH=C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    echo [OK] Inno Setup 5 trouve: C:\Program Files (x86)\Inno Setup 5\
) else (
    echo [ERREUR] Inno Setup n'est pas installe
    echo.
    echo Pour creer l'installateur, vous devez installer Inno Setup:
    echo 1. Telechargez depuis: https://jrsoftware.org/isdl.php
    echo 2. Installez Inno Setup 6
    echo 3. Relancez ce script
    echo.
    pause
    exit /b 1
)

:: Verification du script Inno Setup
echo [ETAPE] Verification du script Inno Setup...
if not exist "OCR_Intelligent_Setup.iss" (
    echo [ERREUR] Le fichier OCR_Intelligent_Setup.iss n'existe pas
    echo Assurez-vous que le script Inno Setup est present
    pause
    exit /b 1
)
echo [OK] Script Inno Setup trouve

:: Creation du dossier de distribution
echo [ETAPE] Preparation de l'environnement...
if not exist "dist" mkdir dist

:: Verification des fichiers necessaires
echo [ETAPE] Verification des fichiers source...
set "MISSING_FILES="

if not exist "main.py" (
    echo [WARNING] main.py manquant
    set "MISSING_FILES=1"
)

if not exist "Lancer_OCR_Intelligent.bat" (
    echo [WARNING] Lancer_OCR_Intelligent.bat manquant
    set "MISSING_FILES=1"
)

if not exist "frontend\app.py" (
    echo [WARNING] frontend\app.py manquant
    set "MISSING_FILES=1"
)

if not exist "backend\main.py" (
    echo [WARNING] backend\main.py manquant
    set "MISSING_FILES=1"
)

if defined MISSING_FILES (
    echo [WARNING] Certains fichiers sont manquants
    echo L'installateur sera cree mais pourrait ne pas fonctionner
    echo.
    choice /C ON /M "Voulez-vous continuer malgre tout"
    if errorlevel 2 exit /b 1
)

:: Construction de l'installateur
echo.
echo [ETAPE] Construction de l'installateur...
echo Cela peut prendre quelques minutes...
echo.

"%INNO_PATH%" "OCR_Intelligent_Setup.iss"

if errorlevel 1 (
    echo.
    echo [ERREUR] Echec de la construction de l'installateur
    echo Verifiez les erreurs ci-dessus
    pause
    exit /b 1
)

:: Verification que l'installateur a ete cree
if exist "dist\OCR_Intelligent_Setup_v2.0.0.exe" (
    echo.
    echo ================================================================
    echo CONSTRUCTION REUSSIE !
    echo ================================================================
    echo L'installateur a ete cree avec succes:
    echo Fichier: dist\OCR_Intelligent_Setup_v2.0.0.exe
    echo.
    echo Taille du fichier:
    for %%F in ("dist\OCR_Intelligent_Setup_v2.0.0.exe") do echo %%~zF octets
    echo.
    echo Cet installateur .exe unique contient:
    echo - Tous les fichiers de l'application
    echo - Verification automatique de Python
    echo - Installation des dependances
    echo - Creation des raccourcis
    echo - Desinstallateur integre
    echo.
    echo Vous pouvez maintenant distribuer ce fichier .exe unique !
    echo.
    choice /C ON /M "Voulez-vous ouvrir le dossier de destination"
    if not errorlevel 2 explorer "dist"
) else (
    echo.
    echo [ERREUR] L'installateur n'a pas ete trouve dans le dossier dist
    echo Verifiez les erreurs de compilation
)

echo.
echo ================================================================
echo CONSTRUCTION TERMINEE
echo ================================================================
pause
