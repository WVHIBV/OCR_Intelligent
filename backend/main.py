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
from backend.quality_evaluator import adjust_confidence_with_quality, get_quality_report

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

    # Appliquer l'évaluation de qualité pour ajuster les scores de confiance
    for method in results:
        if results[method]["lines"] and results[method]["confs"]:
            # Ajuster les scores de confiance avec l'évaluateur de qualité
            adjusted_confs = adjust_confidence_with_quality(
                results[method]["lines"],
                results[method]["confs"]
            )
            results[method]["confs"] = adjusted_confs

            # Générer un rapport de qualité pour le logging
            quality_report = get_quality_report(results[method]["lines"], adjusted_confs)
            logger.info(f"Rapport qualité {method}:\n{quality_report}")

    # Calcul de confiance amélioré avec pondération
    for method in results:
        confs = results[method]["confs"]
        lines = results[method]["lines"]

        if confs and lines:
            # Calcul de confiance pondérée par la longueur des lignes
            weighted_conf = 0
            total_weight = 0

            for line, conf in zip(lines, confs):
                # Pondération basée sur la longueur de la ligne (plus de texte = plus fiable)
                weight = max(1, len(line.strip()) / 10)  # Minimum 1, augmente avec la longueur

                # Bonus pour les lignes avec contenu structuré
                if any(keyword in line.lower() for keyword in ['facture', 'total', 'date', 'montant']):
                    weight *= 1.5
                elif any(char.isdigit() for char in line) and len(line.strip()) > 3:
                    weight *= 1.2

                weighted_conf += conf * weight
                total_weight += weight

            # Confiance pondérée finale
            results[method]["avg_conf"] = weighted_conf / total_weight if total_weight > 0 else 0

            # Ajustement basé sur le nombre de lignes détectées (plus de contenu = plus fiable)
            line_count_factor = min(1.1, 1 + (len(lines) - 5) * 0.01)  # Bonus jusqu'à 10% pour beaucoup de lignes
            results[method]["avg_conf"] *= line_count_factor

            # Plafonner à 99% (jamais 100% sauf correction manuelle)
            results[method]["avg_conf"] = min(99.0, results[method]["avg_conf"])
        else:
            results[method]["avg_conf"] = 0

    # Sélection de la meilleure méthode avec critères multiples
    best_method = max(results.items(), key=lambda x: (
        x[1]["avg_conf"],  # Critère principal : confiance
        len(x[1]["lines"]),  # Critère secondaire : nombre de lignes
        sum(len(line) for line in x[1]["lines"])  # Critère tertiaire : quantité de texte
    ))[0]
    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", f"result_{best_method}.docx")
    export_to_word(results[best_method]["lines"], results[best_method]["confs"], output_path, image_path=image_paths[0], method=best_method)

    # Correction automatique après OCR
    ocr_text = "\n".join(results[best_method]["lines"])
    corrected_text = correct_text(ocr_text)
    results[best_method]["lines"] = corrected_text.split("\n")

    return results, best_method, output_path
