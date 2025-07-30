@echo off
echo ========================================
echo  OCR INTELLIGENT - Tesseract 5.x
echo ========================================
echo.

REM Configuration Tesseract 5.x
set "PATH=C:\Program Files\Tesseract-OCR;%PATH%"

REM Vérification
echo Configuration Tesseract:
tesseract --version
echo.

REM Test OCR rapide
echo Test OCR rapide...
echo "Test" > test.txt
tesseract test.txt stdout
del test.txt
echo.

REM Lancement du logiciel
echo Lancement du logiciel OCR...
python main.py

pause 