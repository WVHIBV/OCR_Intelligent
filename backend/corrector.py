from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import os

# Variables globales pour le modèle de correction
_correction_model = None
_correction_tokenizer = None
_correction_available = None

def _initialize_correction_model():
    """Initialise le modèle de correction une seule fois"""
    global _correction_model, _correction_tokenizer, _correction_available

    if _correction_available is not None:
        return _correction_available

    # Chemins possibles pour le modèle de correction
    possible_paths = [
        "correction_model",
        "./correction_model",
        "modele/correction",
        "./modele/correction"
    ]

    model_path = None
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            # Vérifier si le dossier contient les fichiers nécessaires
            config_file = os.path.join(path, "config.json")
            if os.path.exists(config_file):
                model_path = path
                break

    if model_path:
        try:
            print(f"Chargement du modèle de correction depuis: {model_path}")
            _correction_model = T5ForConditionalGeneration.from_pretrained(model_path)
            _correction_tokenizer = T5Tokenizer.from_pretrained(model_path)
            _correction_available = True
            print("[OK] Modèle de correction chargé avec succès")
            return True
        except Exception as e:
            print(f"[ERROR] Erreur lors du chargement du modèle de correction: {e}")
            _correction_available = False
            return False
    else:
        print("Modèle de correction non trouvé. La correction automatique sera désactivée.")
        _correction_available = False
        return False

def correct_text(ocr_text):
    """Corrige le texte OCR si le modèle est disponible"""

    if not _initialize_correction_model():
        print("Correction automatique non disponible - retour du texte original.")
        return ocr_text

    try:
        input_text = "ocr: " + ocr_text
        input_ids = _correction_tokenizer(input_text, return_tensors="pt").input_ids
        outputs = _correction_model.generate(input_ids, max_length=256)
        corrected_text = _correction_tokenizer.decode(outputs[0], skip_special_tokens=True)
        return corrected_text
    except Exception as e:
        print(f"Erreur lors de la correction: {e}")
        return ocr_text