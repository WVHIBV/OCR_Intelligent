@echo off
title OCR Intelligent Portable v2.0
color 0A
cd /d "%~dp0"

echo.
echo        ╔══════════════════════════════════════════════════════════╗
echo        ║                  OCR INTELLIGENT v2.0                   ║
echo        ║        Solution OCR avec IA et apprentissage auto       ║
echo        ║                     VERSION PORTABLE                    ║
echo        ╚══════════════════════════════════════════════════════════╝
echo.

echo 🔍 Verification de l'environnement...

REM Verifier si Python est disponible
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python detecte
) else (
    echo ❌ Python non trouve !
    echo.
    echo 💡 Solutions:
    echo    1. Installez Python depuis python.org
    echo    2. Ou utilisez la version avec Python embarque
    echo.
    pause
    exit /b 1
)

echo 🚀 Demarrage d'OCR Intelligent...
echo.
echo 📱 L'application va s'ouvrir dans votre navigateur
echo 🌐 Adresse: http://localhost:8501
echo.
echo ⏳ Patientez quelques secondes...

REM Installer les dependances si necessaire
echo 🔧 Verification des dependances...
python -m pip install streamlit opencv-python pytesseract easyocr python-doctr[torch] python-docx Pillow numpy psutil torch transformers pandas --quiet --no-warn-script-location

REM Lancer l'application
echo ▶️  Lancement en cours...
python -m streamlit run frontend/app.py --server.port 8501 --server.headless true --server.address localhost

echo.
echo 🛑 Application fermee
pause
