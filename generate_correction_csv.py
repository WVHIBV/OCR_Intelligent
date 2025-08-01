#!/usr/bin/env python3
"""
Script pour générer le dataset de correction à partir des documents Word corrigés
"""
import os
import pandas as pd
import docx
from pathlib import Path
import re

def extract_text_from_word(docx_path):
    """Extrait le texte d'un document Word"""
    try:
        doc = docx.Document(docx_path)
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text.strip())
        return '\n'.join(text)
    except Exception as e:
        print(f"Erreur lors de l'extraction du texte de {docx_path}: {e}")
        return ""

def find_correction_pairs():
    """Trouve les paires de documents (original + corrigé)"""
    corrected_dir = Path("corrected")
    output_dir = Path("output")
    
    if not corrected_dir.exists():
        print("❌ Dossier 'corrected' non trouvé")
        return []
    
    pairs = []
    
    # Chercher les fichiers Word corrigés
    for corrected_file in corrected_dir.glob("*.docx"):
        filename = corrected_file.stem
        
        # Chercher le fichier original correspondant
        original_file = None
        
        # Chercher dans output/
        if output_dir.exists():
            for original in output_dir.glob(f"{filename}*.docx"):
                if "corrige" not in original.name.lower():
                    original_file = original
                    break
        
        # Chercher dans images/
        if not original_file:
            images_dir = Path("images")
            if images_dir.exists():
                for img_file in images_dir.glob(f"{filename}.*"):
                    if img_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.pdf']:
                        original_file = img_file
                        break
        
        if original_file:
            pairs.append((original_file, corrected_file))
            print(f"✅ Paire trouvée: {original_file.name} → {corrected_file.name}")
        else:
            print(f"⚠️  Aucun original trouvé pour {corrected_file.name}")
    
    return pairs

def generate_correction_dataset():
    """Génère le dataset de correction"""
    print("🔄 Génération du dataset de correction...")
    
    pairs = find_correction_pairs()
    
    if not pairs:
        print("❌ Aucune paire de documents trouvée")
        return
    
    dataset = []
    
    for original_file, corrected_file in pairs:
        print(f"\n📄 Traitement de {original_file.name}...")
        
        # Extraire le texte corrigé
        corrected_text = extract_text_from_word(corrected_file)
        
        if not corrected_text:
            print(f"⚠️  Texte vide dans {corrected_file.name}")
            continue
        
        # Pour l'instant, on utilise le texte corrigé comme référence
        # Dans une version plus avancée, on pourrait extraire le texte OCR original
        # depuis les métadonnées du document Word
        
        dataset.append({
            'original_file': original_file.name,
            'corrected_file': corrected_file.name,
            'original_text': corrected_text,  # Placeholder - à améliorer
            'corrected_text': corrected_text,
            'correction_type': 'manual'
        })
    
    # Créer le DataFrame
    df = pd.DataFrame(dataset)
    
    # Sauvegarder le dataset
    output_file = "corrections.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\n✅ Dataset généré: {output_file}")
    print(f"📊 {len(dataset)} paires de corrections enregistrées")
    
    # Afficher un aperçu
    print("\n📋 Aperçu du dataset:")
    print(df.head())
    
    return output_file

if __name__ == "__main__":
    generate_correction_dataset() 