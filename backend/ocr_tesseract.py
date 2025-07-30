"""
Module OCR Tesseract avec modèles locaux et configuration automatique
Priorité aux modèles locaux, fallback vers installation système
Optimisé pour fonctionnement offline-first
"""
import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import glob
import subprocess
import os
import shutil

# Variables globales déclarées au niveau du module
USING_LOCAL_MODELS = False
TESSDATA_PREFIX = ""

def get_local_tessdata_path():
    """
    Trouve le chemin vers les modèles Tesseract locaux
    """
    # Chercher dans le dossier models/tesseract/tessdata
    local_tessdata = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'tesseract', 'tessdata')
    
    if os.path.exists(local_tessdata):
        return local_tessdata
    
    return None

def get_available_languages(tessdata_path):
    """
    Liste les langues disponibles dans un dossier tessdata
    """
    if not tessdata_path or not os.path.exists(tessdata_path):
        return []
    
    # Chercher les fichiers .traineddata
    traineddata_files = glob.glob(os.path.join(tessdata_path, '*.traineddata'))
    
    # Extraire les codes de langue
    languages = []
    for file_path in traineddata_files:
        filename = os.path.basename(file_path)
        language_code = filename.replace('.traineddata', '')
        languages.append(language_code)
    
    return sorted(languages)

def configure_tesseract():
    """
    Configure Tesseract avec priorité à la version système 5.x
    """
    global USING_LOCAL_MODELS, TESSDATA_PREFIX
    
    print("[CONFIG] Configuration Tesseract...")

    # FORCER l'utilisation de la bonne installation Tesseract 5.x
    tesseract_5x_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    tessdata_5x_path = r"C:\Program Files\Tesseract-OCR\tessdata"
    
    if os.path.exists(tesseract_5x_path):
        print(f"[FORCE] Utilisation forcée de Tesseract 5.x: {tesseract_5x_path}")
        
        # Vérifier la version
        try:
            result = subprocess.run([tesseract_5x_path, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_output = result.stdout.strip()
                print(f"[VERSION] {version_output}")
                
                if "5." in version_output:
                    print("[OK] Tesseract 5.x confirmé")
                    
                    # Configurer pytesseract pour utiliser le bon chemin
                    pytesseract.pytesseract.tesseract_cmd = tesseract_5x_path
                    
                    # Configurer TESSDATA_PREFIX pour utiliser le bon dossier
                    if os.path.exists(tessdata_5x_path):
                        os.environ['TESSDATA_PREFIX'] = tessdata_5x_path
                        TESSDATA_PREFIX = tessdata_5x_path
                        USING_LOCAL_MODELS = False
                        
                        print(f"[OK] TESSDATA_PREFIX configuré: {tessdata_5x_path}")
                        
                        # Vérifier les langues disponibles
                        try:
                            result = subprocess.run([tesseract_5x_path, '--list-langs'], 
                                                  capture_output=True, text=True, timeout=10)
                            if result.returncode == 0:
                                languages = result.stdout.strip().split('\n')[1:]
                                languages = [lang.strip() for lang in languages if lang.strip()]
                                print(f"[LANG] Langues disponibles: {', '.join(languages)}")
                                
                                if 'fra' in languages and 'eng' in languages:
                                    print("[OK] Langues français et anglais disponibles")
                                    return True
                                else:
                                    print("[WARNING] Langues manquantes")
                            else:
                                print(f"[ERROR] Erreur liste langues: {result.stderr}")
                        except Exception as e:
                            print(f"[ERROR] Erreur vérification langues: {e}")
                    else:
                        print(f"[ERROR] Dossier tessdata non trouvé: {tessdata_5x_path}")
                else:
                    print("[ERROR] Version Tesseract incorrecte")
            else:
                print(f"[ERROR] Erreur version: {result.stderr}")
        except Exception as e:
            print(f"[ERROR] Erreur vérification: {e}")
    else:
        print(f"[ERROR] Tesseract 5.x non trouvé: {tesseract_5x_path}")

    print("[WARNING] Fallback vers les modèles locaux")
    
    # Fallback vers les modèles locaux
    local_tessdata = get_local_tessdata_path()

    if local_tessdata:
        print(f"[FOLDER] Modèles locaux trouvés: {local_tessdata}")

        # Lister les langues disponibles localement
        local_languages = get_available_languages(local_tessdata)
        if local_languages:
            print(f"[LANG] Langues locales disponibles: {', '.join(local_languages)}")

            # Configurer TESSDATA_PREFIX pour utiliser les modèles locaux
            os.environ['TESSDATA_PREFIX'] = local_tessdata
            TESSDATA_PREFIX = local_tessdata
            USING_LOCAL_MODELS = True
            print(f"[OK] TESSDATA_PREFIX configuré: {local_tessdata}")
        else:
            print("[WARNING] Aucun modèle de langue trouvé dans le dossier local")
            local_tessdata = None
    else:
        print("[FOLDER] Aucun modèle local trouvé dans models/tesseract/tessdata")

    # Configurer l'exécutable Tesseract
    tesseract_path = None

    # Vérifier si tesseract est dans le PATH
    if shutil.which('tesseract'):
        tesseract_path = 'tesseract'
        print("[SEARCH] Tesseract trouvé dans le PATH système")
    else:
        # Chemins possibles pour Tesseract sur Windows
        program_files = os.environ.get('PROGRAMFILES', 'C:\\Program Files')
        program_files_x86 = os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')
        user_profile = os.environ.get('USERPROFILE', '')

        possible_paths = [
            os.path.join(program_files, 'Tesseract-OCR', 'tesseract.exe'),
            os.path.join(program_files_x86, 'Tesseract-OCR', 'tesseract.exe'),
            os.path.join(user_profile, 'AppData', 'Local', 'Programs', 'Tesseract-OCR', 'tesseract.exe'),
        ]

        # Vérifier les chemins possibles
        for path in possible_paths:
            if os.path.exists(path):
                tesseract_path = path
                print(f"[SEARCH] Tesseract trouvé à: {path}")
                break

    if tesseract_path:
        # Configurer pytesseract pour utiliser le chemin spécifique
        try:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            print(f"[OK] pytesseract configuré: {tesseract_path}")
        except Exception as e:
            print(f"[WARNING] Erreur configuration pytesseract: {e}")

        # Tester la configuration
        try:
            result = subprocess.run([tesseract_path, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"[TEST] Configuration testée: {result.stdout.strip()}")
                return True
            else:
                print(f"[ERROR] Test échoué: {result.stderr}")
                return False
        except Exception as e:
            print(f"[ERROR] Erreur test: {e}")
            return False
    else:
        print("[ERROR] Aucun exécutable Tesseract trouvé")
        return False

# Configurer Tesseract au chargement du module
TESSERACT_AVAILABLE = configure_tesseract()


def get_tesseract_info():
    """
    Retourne des informations sur la configuration Tesseract actuelle
    """
    info = {
        'available': TESSERACT_AVAILABLE,
        'using_local_models': USING_LOCAL_MODELS,
        'tessdata_prefix': os.environ.get('TESSDATA_PREFIX', 'Non défini'),
        'tesseract_cmd': pytesseract.pytesseract.tesseract_cmd,
        'languages': []
    }

    if TESSERACT_AVAILABLE:
        tessdata_path = os.environ.get('TESSDATA_PREFIX')
        if tessdata_path:
            info['languages'] = get_available_languages(tessdata_path)

    return info


def get_optimal_language_config():
    """
    Retourne la configuration de langue optimale basée sur les modèles disponibles
    Priorité: fra+eng si disponible, sinon eng, sinon premier disponible
    """
    if not TESSERACT_AVAILABLE:
        return 'eng'  # Fallback par défaut

    tessdata_path = os.environ.get('TESSDATA_PREFIX')
    if not tessdata_path:
        return 'eng'  # Fallback par défaut

    available_languages = get_available_languages(tessdata_path)

    if not available_languages:
        return 'eng'  # Fallback par défaut

    # Priorité aux langues françaises et anglaises
    if 'fra' in available_languages and 'eng' in available_languages:
        return 'fra+eng'
    elif 'fra' in available_languages:
        return 'fra'
    elif 'eng' in available_languages:
        return 'eng'
    else:
        # Utiliser la première langue disponible
        return available_languages[0]

def ocr_tesseract(image, return_conf=False, enhanced_preprocessing=True, verbose=False):
    """
    Effectue l'OCR avec Tesseract en utilisant les modèles locaux en priorité

    Args:
        image: Image à traiter
        return_conf: Si True, retourne aussi les scores de confiance
        enhanced_preprocessing: Active le préprocessing amélioré
        verbose: Active les logs détaillés

    Returns:
        str ou (list, list): Texte extrait ou (lignes, confidences)
    """
    if not TESSERACT_AVAILABLE:
        error_msg = "[ERROR] Tesseract non disponible"
        print(error_msg)
        if return_conf:
            return [error_msg], [0]
        return error_msg

    try:
        # Obtenir la configuration de langue optimale
        optimal_lang = get_optimal_language_config()

        if verbose:
            info = get_tesseract_info()
            print(f"[CONFIG] Configuration Tesseract:")
            print(f"   [FOLDER] Modèles locaux: {'[OK]' if info['using_local_models'] else '[ERROR]'}")
            print(f"   [LANG] Langues: {optimal_lang}")
            print(f"   [FOLDER] TESSDATA_PREFIX: {info['tessdata_prefix']}")

        # Configuration améliorée pour Tesseract
        # PSM 6: Assume a single uniform block of text
        # PSM 3: Fully automatic page segmentation, but no OSD
        configs = [
            '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789€°.,;:!?()[]{}+-*/=@#&%',
            '--psm 3',
            '--psm 6',
            '--psm 4'
        ]

        best_result = None
        best_confidence = 0

        # Essayer différentes configurations et garder la meilleure
        for i, config in enumerate(configs):
            try:
                if verbose:
                    print(f"   [PROCESS] Test configuration {i+1}/{len(configs)}: PSM {config.split('--psm ')[1].split(' ')[0] if '--psm' in config else 'default'}")

                data = pytesseract.image_to_data(image, lang=optimal_lang, config=config, output_type=Output.DICT)
                lines = []
                confidences = []
                current_line = ""
                current_conf = []
                last_line_num = -1

                for j, word in enumerate(data['text']):
                    if word.strip() == "" or data['conf'][j] < 30:  # Filtrer les mots avec faible confiance
                        continue
                    line_num = data['line_num'][j]
                    if line_num != last_line_num and current_line:
                        lines.append(current_line.strip())
                        avg_conf = sum(current_conf)/len(current_conf) if current_conf else 0
                        confidences.append(avg_conf)
                        current_line = word + " "
                        current_conf = [data['conf'][j]]
                        last_line_num = line_num
                    else:
                        current_line += word + " "
                        current_conf.append(data['conf'][j])
                        last_line_num = line_num

                if current_line:
                    lines.append(current_line.strip())
                    avg_conf = sum(current_conf)/len(current_conf) if current_conf else 0
                    confidences.append(avg_conf)

                # Calculer la confiance moyenne de ce résultat
                if confidences:
                    avg_confidence = sum(confidences) / len(confidences)
                    if verbose:
                        print(f"      [STATS] Confiance moyenne: {avg_confidence:.1f}% ({len(lines)} lignes)")
                    if avg_confidence > best_confidence:
                        best_confidence = avg_confidence
                        best_result = (lines, confidences)

            except Exception as e:
                if verbose:
                    print(f"      [ERROR] Configuration échouée: {str(e)}")
                continue  # Essayer la configuration suivante

        if best_result:
            lines, confidences = best_result
            # Filtrer les lignes vides ou avec très faible confiance
            filtered_lines = []
            filtered_confs = []
            for line, conf in zip(lines, confidences):
                if line.strip() and conf > 20:  # Seuil de confiance minimum
                    filtered_lines.append(line.strip())
                    filtered_confs.append(conf)

            if verbose:
                print(f"[OK] Tesseract terminé:")
                print(f"   [STATS] Meilleure confiance: {best_confidence:.1f}%")
                print(f"   [TEXT] Lignes extraites: {len(filtered_lines)}")
                if USING_LOCAL_MODELS:
                    print(f"   [LOCAL] Modèles locaux utilisés")
                else:
                    print(f"   [SYSTEM] Modèles système utilisés")

            if return_conf:
                return filtered_lines if filtered_lines else ["Aucun texte détecté"], filtered_confs if filtered_confs else [0]
            return "\n".join(filtered_lines) if filtered_lines else "Aucun texte détecté"
        else:
            error_msg = "Aucun texte détecté avec toutes les configurations"
            if verbose:
                print(f"[WARNING] {error_msg}")
            if return_conf:
                return [error_msg], [0]
            return error_msg

    except Exception as e:
        error_msg = f"Erreur Tesseract: {str(e)}"
        print(f"[ERROR] {error_msg}")

        # Diagnostic en cas d'erreur
        if "tessdata" in str(e).lower() or "language" in str(e).lower():
            print("[DIAG] Diagnostic:")
            print(f"   TESSDATA_PREFIX: {os.environ.get('TESSDATA_PREFIX', 'Non défini')}")
            print(f"   Modèles locaux: {'[OK]' if USING_LOCAL_MODELS else '[ERROR]'}")

            tessdata_path = os.environ.get('TESSDATA_PREFIX')
            if tessdata_path:
                available_langs = get_available_languages(tessdata_path)
                print(f"   Langues disponibles: {available_langs}")

        if return_conf:
            return [error_msg], [0]
        return error_msg


def test_tesseract_configuration():
    """
    Teste la configuration Tesseract et affiche des informations détaillées
    Utile pour le debug et la validation de l'installation
    """
    print("[TEST] TEST DE LA CONFIGURATION TESSERACT")
    print("="*50)

    # Informations générales
    info = get_tesseract_info()

    print(f"[INFO] État général:")
    print(f"   Disponible: {'[OK]' if info['available'] else '[ERROR]'}")
    print(f"   Modèles locaux: {'[OK]' if info['using_local_models'] else '[ERROR]'}")
    print(f"   Commande: {info['tesseract_cmd']}")
    print(f"   TESSDATA_PREFIX: {info['tessdata_prefix']}")

    if info['languages']:
        print(f"   Langues: {', '.join(info['languages'])}")
    else:
        print(f"   Langues: Aucune détectée")

    # Test des modèles locaux
    local_tessdata = get_local_tessdata_path()
    if local_tessdata:
        print(f"\n[FOLDER] Modèles locaux:")
        print(f"   Chemin: {local_tessdata}")
        local_langs = get_available_languages(local_tessdata)
        print(f"   Langues: {', '.join(local_langs) if local_langs else 'Aucune'}")

        # Lister les fichiers de modèles
        model_files = glob.glob(os.path.join(local_tessdata, '*.traineddata'))
        for model_file in model_files:
            size = os.path.getsize(model_file)
            print(f"   [FILE] {os.path.basename(model_file)} ({size:,} bytes)")
    else:
        print(f"\n[FOLDER] Modèles locaux: Non trouvés")

    # Test de la configuration optimale
    optimal_lang = get_optimal_language_config()
    print(f"\n[LANG] Configuration optimale: {optimal_lang}")

    # Test basique si Tesseract est disponible
    if info['available']:
        print(f"\n[TEST] Test basique:")
        try:
            # Créer une image de test simple
            from PIL import Image, ImageDraw, ImageFont
            import io

            # Image de test avec du texte
            test_image = Image.new('RGB', (300, 100), color='white')
            draw = ImageDraw.Draw(test_image)

            try:
                # Essayer d'utiliser une police par défaut
                font = ImageFont.load_default()
            except:
                font = None

            draw.text((10, 30), "Test OCR 123", fill='black', font=font)

            # Test OCR
            result = ocr_tesseract(test_image, verbose=True)

            if "Test" in result or "OCR" in result or "123" in result:
                print(f"   [OK] Test réussi: '{result.strip()}'")
            else:
                print(f"   [WARNING] Test partiel: '{result.strip()}'")

        except Exception as e:
            print(f"   [ERROR] Test échoué: {e}")

    print("\n" + "="*50)

    return info['available']