#!/usr/bin/env python3
"""
Script d'installation des dépendances pour l'OCR Tool avec mise en page
"""
import subprocess
import sys
import os

def install_package(package):
    """Installe un package avec pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installé avec succès")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Erreur lors de l'installation de {package}")
        return False

def main():
    print("🚀 Installation des dépendances pour l'OCR Tool avec mise en page")
    print("=" * 60)
    
    # Dépendances principales
    packages = [
        "streamlit>=1.28.0",
        "opencv-python>=4.8.0", 
        "pytesseract>=0.3.10",
        "easyocr>=1.7.0",
        "python-docx>=0.8.11",
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        "PyMuPDF>=1.23.0",
        "reportlab>=4.0.0"
    ]
    
    print("📦 Installation des packages Python...")
    success_count = 0
    
    for package in packages:
        print(f"\n📥 Installation de {package}...")
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Résumé: {success_count}/{len(packages)} packages installés avec succès")
    
    if success_count == len(packages):
        print("\n🎉 Toutes les dépendances sont installées !")
        print("\n📋 Fonctionnalités disponibles:")
        print("   ✅ OCR Intelligent avec détection de zones")
        print("   ✅ Export Word classique")
        print("   ✅ Export PDF structuré (avec mise en page)")
        print("   ✅ Export HTML interactif")
        print("   ✅ Export PDF avec image originale")
        print("\n🚀 Vous pouvez maintenant lancer l'application avec:")
        print("   python -m streamlit run frontend/app.py")
    else:
        print("\n⚠️  Certaines dépendances n'ont pas pu être installées.")
        print("   Vérifiez votre connexion internet et réessayez.")

if __name__ == "__main__":
    main() 