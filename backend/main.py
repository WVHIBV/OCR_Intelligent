"""
Module principal pour l'orchestration des différents moteurs OCR
"""
import os
import glob
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Configuration de l'environnement
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import warnings
warnings.filterwarnings("ignore")

# Imports des modules OCR
from backend.preprocessing import preprocess_image
from backend.ocr_tesseract import ocr_tesseract
from backend.ocr_easyocr import ocr_easyocr
from backend.ocr_doctr import ocr_doctr
from backend.export import export_to_word
from backend.corrector import correct_text

# Configuration du logging
logger = logging.getLogger(__name__)


def clear_output_directory() -> None:
    """
    Nettoie le dossier output des fichiers générés précédemment
    Appelé automatiquement au début du pipeline OCR
    """
    output_dir = Path("output")

    if output_dir.exists():
        try:
            # Trouver tous les fichiers .docx dans le dossier output
            docx_files = list(output_dir.glob("*.docx"))

            if docx_files:
                cleaned_count = 0
                for file_path in docx_files:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                    except Exception as e:
                        logger.warning(f"Impossible de supprimer {file_path}: {e}")

                if cleaned_count > 0:
                    logger.info(f"Dossier output nettoyé: {cleaned_count} fichier(s) supprimé(s)")
            else:
                logger.info("Dossier output déjà propre")

        except Exception as e:
            logger.error(f"Erreur lors du nettoyage: {e}")
    else:
        # Créer le dossier s'il n'existe pas
        output_dir.mkdir(exist_ok=True)
        logger.info("Dossier output créé")

def run_all_ocr_methods(image_paths):
    # [CLEAN] Nettoyage automatique du dossier output
    clear_output_directory()

    results = {"tesseract": {"lines": [], "confs": []},
               "easyocr": {"lines": [], "confs": []},
               "doctr": {"lines": [], "confs": []}}

    # Mémoire exacte : si une correction existe déjà pour la première image, on l'utilise directement
    base_name = os.path.splitext(os.path.basename(image_paths[0]))[0]
    corrected_path = os.path.join("corrected", base_name + "_corrige.txt")
    if os.path.exists(corrected_path):
        with open(corrected_path, "r", encoding="utf-8") as f:
            corrected_lines = f.read().splitlines()
        # On remplit les résultats avec la correction pour toutes les méthodes (pour l'affichage)
        for method in results:
            results[method]["lines"] = corrected_lines
            results[method]["confs"] = [100] * len(corrected_lines)
            results[method]["avg_conf"] = 100
        best_method = "doctr"  # ou autre, ici arbitraire car c'est la correction qui compte
        os.makedirs("output", exist_ok=True)
        output_path = os.path.join("output", f"result_{best_method}.docx")
        export_to_word(corrected_lines, [100]*len(corrected_lines), output_path, image_path=image_paths[0], method=best_method)
        return results, best_method, output_path

    # Sinon, pipeline normal OCR + correction automatique
    for image_path in image_paths:
        # Tesseract avec préprocessing optimisé
        image_tess = preprocess_image(image_path, method="tesseract_optimized")
        lines_tess, confs_tess = ocr_tesseract(image_tess, return_conf=True)
        results["tesseract"]["lines"].extend(lines_tess)
        results["tesseract"]["confs"].extend(confs_tess)

        # EasyOCR avec image originale (il fait son propre préprocessing)
        lines_easy, confs_easy = ocr_easyocr(image_path)
        results["easyocr"]["lines"].extend(lines_easy)
        results["easyocr"]["confs"].extend(confs_easy)

        # DocTR avec wrapper local
        lines_doctr, confs_doctr = ocr_doctr(image_path)
        results["doctr"]["lines"].extend(lines_doctr)
        results["doctr"]["confs"].extend(confs_doctr)

    for method in results:
        confs = results[method]["confs"]
        results[method]["avg_conf"] = sum(confs) / len(confs) if confs else 0

    best_method = max(results.items(), key=lambda x: x[1]["avg_conf"])[0]
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", f"result_{best_method}.docx")
    export_to_word(results[best_method]["lines"], results[best_method]["confs"], output_path, image_path=image_paths[0], method=best_method)

    # Correction automatique après OCR
    ocr_text = "\n".join(results[best_method]["lines"])
    corrected_text = correct_text(ocr_text)
    results[best_method]["lines"] = corrected_text.split("\n")

    return results, best_method, output_path
