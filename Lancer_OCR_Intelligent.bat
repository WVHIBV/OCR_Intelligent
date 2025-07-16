@echo off
setlocal enabledelayedexpansion

title OCR Intelligent

echo ================================================================
echo OCR INTELLIGENT - Application de Reconnaissance Optique
echo ================================================================
echo Moteurs OCR: Tesseract, EasyOCR, DocTR
echo Version: Portable et Autonome
echo ================================================================
echo.

:: Verification de Python
echo [ETAPE] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou accessible
    echo.
    echo Solutions:
    echo 1. Installez Python 3.8+ depuis https://python.org
    echo 2. Cochez "Add Python to PATH" lors de l'installation
    echo 3. Redemarrez votre ordinateur apres installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python detecte
python --version
echo.

:: Configuration proxy Safran
set PIP_INDEX_URL=https://artifacts.cloud.safran/repository/pypi-group/simple
set PIP_TRUSTED_HOST=artifacts.cloud.safran
set SAFRAN_PIP_ARGS=--index-url %PIP_INDEX_URL% --trusted-host %PIP_TRUSTED_HOST%
echo [INFO] Utilisation du proxy Safran pour l'installation des packages

:: Verification et installation de Streamlit
echo [ETAPE] Verification de Streamlit...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installation de Streamlit...
    python -m pip install streamlit --quiet %SAFRAN_PIP_ARGS%
    if errorlevel 1 (
        echo [ERREUR] Impossible d'installer Streamlit
        echo Tentative d'installation utilisateur...
        python -m pip install streamlit --user --quiet %SAFRAN_PIP_ARGS%
        if errorlevel 1 (
            echo [ERREUR] Installation de Streamlit echouee
            pause
            exit /b 1
        )
    )
    echo [OK] Streamlit installe avec succes
) else (
    echo [OK] Streamlit disponible
)

:: Installation des dependances
if exist requirements.txt (
    echo [ETAPE] Installation des dependances...
    python -m pip install -r requirements.txt --quiet %SAFRAN_PIP_ARGS%
    if errorlevel 1 (
        echo [WARNING] Certaines dependances n'ont pas pu etre installees
        echo L'application peut fonctionner avec des fonctionnalites limitees
    ) else (
        echo [OK] Dependances installees avec succes
    )
)

:: Creation des dossiers necessaires
if not exist output mkdir output
if not exist logs mkdir logs
if not exist corrected mkdir corrected

:: Verification finale
echo [ETAPE] Verification finale...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Streamlit n'est pas disponible
    pause
    exit /b 1
)

:: Lancement de l'application
echo.
echo ================================================================
echo LANCEMENT DE L'APPLICATION
echo ================================================================
echo [INFO] Demarrage de l'application OCR Intelligent...
echo [INFO] Le navigateur s'ouvrira automatiquement
echo [INFO] Appuyez sur Ctrl+C pour arreter l'application
echo.

python main.py

:: Verification du code de sortie
if errorlevel 1 (
    echo.
    echo [ERREUR] L'application s'est fermee avec une erreur
    echo.
    echo Solutions possibles:
    echo 1. Fermez tous les onglets Streamlit dans votre navigateur
    echo 2. Redemarrez cette application
    echo 3. Verifiez que tous les fichiers sont presents
    echo 4. Redemarrez votre ordinateur si le probleme persiste
    echo.
)

echo.
echo ================================================================
echo APPLICATION FERMEE
echo ================================================================
echo Merci d'avoir utilise OCR Intelligent !
echo.
pause

:cleanup_and_exit
echo.
echo [INFO] Cleaning up and exiting...
echo Press any key to close...
pause >nul
exit /b 0
