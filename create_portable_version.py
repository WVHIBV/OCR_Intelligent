#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de création d'une version portable d'OCR Intelligent
Génère un ZIP autonome que tout le monde peut utiliser sans installation
"""

import os
import shutil
import zipfile
from pathlib import Path
import sys
import urllib.request
import subprocess

def create_portable_structure():
    """Crée la structure de l'application portable"""
    
    portable_dir = Path("OCR_Intelligent_Portable")
    
    # Créer le dossier principal
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir()
    
    print("🚀 Création de la version portable OCR Intelligent...")
    
    # Structure de l'application portable
    structure = {
        "app": "Application principale",
        "python": "Python embarqué", 
        "models": "Modèles IA",
        "tesseract": "Tesseract portable",
        "config": "Configuration",
        "data": "Données utilisateur"
    }
    
    for folder, desc in structure.items():
        (portable_dir / folder).mkdir()
        print(f"✅ Dossier '{folder}' créé - {desc}")
    
    return portable_dir

def copy_application_files(portable_dir):
    """Copie tous les fichiers de l'application"""
    
    print("\n📁 Copie des fichiers de l'application...")
    
    # Dossiers à copier
    folders_to_copy = [
        "backend",
        "frontend", 
        "config",
        "models",
        "corrected",
        "correction_model"
    ]
    
    for folder in folders_to_copy:
        if Path(folder).exists():
            shutil.copytree(folder, portable_dir / "app" / folder)
            print(f"✅ Copié: {folder}")
    
    # Fichiers racine à copier
    files_to_copy = [
        "main.py",
        "requirements.txt",
        "README.md",
        "ocr_icon.ico",
        "generate_correction_csv.py",
        "train_t5_correction.py"
    ]
    
    for file in files_to_copy:
        if Path(file).exists():
            shutil.copy2(file, portable_dir / "app" / file)
            print(f"✅ Copié: {file}")

def create_launcher_scripts(portable_dir):
    """Crée les scripts de lancement"""
    
    print("\n🚀 Création des scripts de lancement...")
    
    # Script principal de lancement Windows
    launcher_bat = f"""@echo off
title OCR Intelligent - Démarrage
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                  OCR INTELLIGENT v2.0                   ║
echo ║            Solution OCR avec IA et apprentissage        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo 🔍 Vérification de l'environnement...

REM Vérifier si Python embarqué existe
if exist "python\\python.exe" (
    echo ✅ Python embarqué détecté
    set PYTHON_PATH=python\\python.exe
) else (
    echo ⚠️  Python embarqué non trouvé, utilisation du Python système
    set PYTHON_PATH=python
)

echo 🚀 Lancement d'OCR Intelligent...
echo.

REM Aller dans le dossier app
cd app

REM Lancer l'application
%PYTHON_PATH% -m streamlit run frontend/app.py --server.port 8501 --server.headless true

echo.
echo 📱 L'application s'ouvre dans votre navigateur à l'adresse:
echo    http://localhost:8501
echo.
echo 💡 Pour arrêter l'application, fermez cette fenêtre
echo.
pause
"""
    
    with open(portable_dir / "LANCER_OCR_INTELLIGENT.bat", "w", encoding="utf-8") as f:
        f.write(launcher_bat)
    
    # Script de configuration initiale
    setup_bat = f"""@echo off
title OCR Intelligent - Configuration initiale
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║              CONFIGURATION OCR INTELLIGENT              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo 🔧 Installation des dépendances Python...
cd app

REM Installer les dépendances
if exist "..\\python\\python.exe" (
    ..\\python\\python.exe -m pip install -r requirements.txt --no-warn-script-location
) else (
    python -m pip install -r requirements.txt
)

echo.
echo ✅ Configuration terminée !
echo 💡 Vous pouvez maintenant lancer OCR Intelligent avec LANCER_OCR_INTELLIGENT.bat
echo.
pause
"""
    
    with open(portable_dir / "CONFIGURER.bat", "w", encoding="utf-8") as f:
        f.write(setup_bat)
    
    print("✅ Scripts de lancement créés")

def create_readme_portable(portable_dir):
    """Crée le guide d'utilisation portable"""
    
    readme_content = """# 📱 OCR Intelligent - Version Portable

## 🚀 Démarrage rapide

### 1️⃣ Première utilisation
1. **Décompressez** ce dossier où vous voulez
2. **Double-cliquez** sur `CONFIGURER.bat` (une seule fois)
3. **Lancez** avec `LANCER_OCR_INTELLIGENT.bat`

### 2️⃣ Utilisation quotidienne
- **Double-cliquez** sur `LANCER_OCR_INTELLIGENT.bat`
- L'application s'ouvre dans votre navigateur
- Glissez-déposez vos documents à analyser

## 📁 Structure du dossier

```
OCR_Intelligent_Portable/
├── 🚀 LANCER_OCR_INTELLIGENT.bat    # Lance l'application
├── 🔧 CONFIGURER.bat                # Configuration initiale (1 fois)
├── 📖 GUIDE_UTILISATION.txt         # Ce fichier
├── app/                             # Application OCR
├── python/                          # Python embarqué (optionnel)
├── models/                          # Modèles IA
└── data/                           # Vos données
```

## ✨ Fonctionnalités

- 🧠 **OCR Intelligent** avec 3 moteurs (Tesseract, EasyOCR, DocTR)
- 🎯 **Détection de zones** automatique (16 types)
- 🤖 **Correction automatique** avec IA
- 📚 **Apprentissage continu** de vos corrections
- 📄 **Export Word** structuré
- 🔒 **100% offline** - aucune donnée envoyée sur internet

## 🆘 Problèmes courants

### L'application ne se lance pas
1. Vérifiez que Python est installé sur votre PC
2. Relancez `CONFIGURER.bat`
3. Redémarrez votre PC

### Erreur de port
- Fermez tous les navigateurs
- Relancez l'application

### Performance lente
- Fermez les autres applications
- Utilisez des images de moins de 10MB

## 📞 Support
- Documentation complète dans `app/README.md`
- Issues GitHub: https://github.com/WVHIBV/OCR_Intelligent

---
**OCR Intelligent v2.0** - Solution OCR avec IA et apprentissage automatique
"""
    
    with open(portable_dir / "GUIDE_UTILISATION.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ Guide d'utilisation créé")

def download_python_embedded(portable_dir):
    """Télécharge Python embarqué (optionnel)"""
    
    print("\n🐍 Voulez-vous inclure Python embarqué ? (recommandé)")
    choice = input("Tapez 'o' pour oui, 'n' pour non: ").lower()
    
    if choice == 'o':
        print("📥 Téléchargement de Python embarqué...")
        
        # URL Python 3.11 embedded
        python_url = "https://www.python.org/ftp/python/3.11.0/python-3.11.0-embed-amd64.zip"
        python_zip = portable_dir / "python-embed.zip"
        
        try:
            urllib.request.urlretrieve(python_url, python_zip)
            
            # Extraire
            with zipfile.ZipFile(python_zip, 'r') as zip_ref:
                zip_ref.extractall(portable_dir / "python")
            
            # Supprimer le zip
            python_zip.unlink()
            
            print("✅ Python embarqué installé")
            
        except Exception as e:
            print(f"⚠️  Erreur téléchargement Python: {e}")
            print("💡 L'application utilisera le Python système")

def create_zip_package(portable_dir):
    """Crée le fichier ZIP final"""
    
    print(f"\n📦 Création du package ZIP...")
    
    zip_name = "OCR_Intelligent_Portable_v2.0.zip"
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(portable_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(portable_dir.parent)
                zipf.write(file_path, arcname)
    
    size_mb = Path(zip_name).stat().st_size / (1024 * 1024)
    print(f"✅ Package créé: {zip_name} ({size_mb:.1f} MB)")
    
    return zip_name

def main():
    """Fonction principale"""
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║          CRÉATION VERSION PORTABLE OCR INTELLIGENT      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    try:
        # Créer la structure
        portable_dir = create_portable_structure()
        
        # Copier les fichiers
        copy_application_files(portable_dir)
        
        # Créer les scripts
        create_launcher_scripts(portable_dir)
        
        # Créer le guide
        create_readme_portable(portable_dir)
        
        # Python embarqué (optionnel)
        download_python_embedded(portable_dir)
        
        # Créer le ZIP
        zip_file = create_zip_package(portable_dir)
        
        print("\n🎉 VERSION PORTABLE CRÉÉE AVEC SUCCÈS !")
        print(f"📁 Fichier: {zip_file}")
        print("\n💡 Instructions:")
        print("   1. Partagez ce fichier ZIP")
        print("   2. L'utilisateur décompresse")
        print("   3. Lance CONFIGURER.bat (1 fois)")
        print("   4. Lance LANCER_OCR_INTELLIGENT.bat")
        print("\n✨ L'application fonctionne sans installation !")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
