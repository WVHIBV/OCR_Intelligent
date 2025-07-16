"""
Module OCR EasyOCR avec modèles locaux et configuration automatique
Priorité aux modèles locaux, fallback vers installation système
Optimisé pour fonctionnement offline-first
"""
import os
import glob
import shutil
import warnings
warnings.filterwarnings("ignore")

# Variables globales pour la configuration
EASYOCR_READER = None
USING_LOCAL_MODELS = False
LOCAL_MODEL_PATH = None


def get_local_model_path():
    """
    Retourne le chemin vers les modèles EasyOCR locaux
    Priorité: models/easyocr dans le projet
    """
    # Chemin vers les modèles locaux dans le projet
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_model_dir = os.path.join(project_root, 'models', 'easyocr')

    if os.path.exists(local_model_dir):
        # Vérifier qu'il y a des modèles (.pth)
        model_files = glob.glob(os.path.join(local_model_dir, '*.pth'))
        if model_files:
            return local_model_dir

    return None


def get_available_model_files(model_path):
    """
    Retourne la liste des fichiers de modèles disponibles dans le dossier
    """
    if not model_path or not os.path.exists(model_path):
        return []

    model_files = glob.glob(os.path.join(model_path, '*.pth'))
    return [os.path.basename(f) for f in model_files]


def detect_supported_languages(model_path):
    """
    Détecte les langues supportées basées sur les modèles disponibles
    """
    if not model_path:
        return ['en']  # Fallback par défaut

    model_files = get_available_model_files(model_path)
    supported_languages = []

    # Mapping des fichiers de modèles vers les codes de langue
    language_mapping = {
        'english_g2.pth': 'en',
        'latin_g2.pth': 'fr',  # Latin couvre le français
        'craft_mlt_25k.pth': None  # Modèle de détection de texte
    }

    for model_file in model_files:
        if model_file in language_mapping:
            lang = language_mapping[model_file]
            if lang and lang not in supported_languages:
                supported_languages.append(lang)

    # Si aucune langue détectée, utiliser anglais par défaut
    if not supported_languages:
        supported_languages = ['en']

    return sorted(supported_languages)


def configure_easyocr():
    """
    Configure EasyOCR avec priorité aux modèles locaux
    1. Modèles locaux dans models/easyocr/
    2. Installation système comme fallback
    """
    global EASYOCR_READER, USING_LOCAL_MODELS, LOCAL_MODEL_PATH

    print("[CONFIG] Configuration EasyOCR...")

    # Étape 1: Vérifier les modèles locaux
    local_model_path = get_local_model_path()

    if local_model_path:
        print(f"[FOLDER] Modèles locaux trouvés: {local_model_path}")

        # Lister les modèles disponibles localement
        local_models = get_available_model_files(local_model_path)
        if local_models:
            print(f"[MODEL] Modèles locaux disponibles: {', '.join(local_models)}")

            # Détecter les langues supportées
            supported_languages = detect_supported_languages(local_model_path)
            print(f"[LANG] Langues supportées localement: {', '.join(supported_languages)}")

            try:
                # Essayer de créer le reader avec modèles locaux
                import easyocr

                # Configurer le chemin des modèles locaux
                print(f"[OK] Configuration modèles locaux: {local_model_path}")

                # Créer le reader avec le chemin personnalisé
                EASYOCR_READER = easyocr.Reader(
                    supported_languages,
                    model_storage_directory=local_model_path,
                    download_enabled=False  # Désactiver les téléchargements
                )

                USING_LOCAL_MODELS = True
                LOCAL_MODEL_PATH = local_model_path
                print("[OK] EasyOCR configuré avec modèles locaux")
                return True, True

            except Exception as e:
                print(f"[WARNING] Erreur configuration modèles locaux: {e}")
                print("[PROCESS] Tentative fallback vers modèles système...")
                local_model_path = None
        else:
            print("[WARNING] Aucun modèle .pth trouvé dans le dossier local")
            local_model_path = None
    else:
        print("[FOLDER] Aucun modèle local trouvé dans models/easyocr/")

    # Étape 2: Fallback vers installation système
    try:
        import easyocr
        print("[SEARCH] Tentative configuration EasyOCR système...")

        # Utiliser la configuration par défaut du système
        # Commencer avec français et anglais si possible
        default_languages = ['fr', 'en']

        print(f"[LANG] Langues par défaut: {', '.join(default_languages)}")

        EASYOCR_READER = easyocr.Reader(
            default_languages,
            download_enabled=True  # Permettre téléchargements pour système
        )

        USING_LOCAL_MODELS = False
        LOCAL_MODEL_PATH = None
        print("[OK] EasyOCR configuré avec modèles système")
        return True, False

    except Exception as e:
        print(f"[ERROR] Erreur configuration EasyOCR système: {e}")
        print("[INFO] Vérifiez l'installation: pip install easyocr")

        EASYOCR_READER = None
        USING_LOCAL_MODELS = False
        LOCAL_MODEL_PATH = None
        return False, False


# Configurer EasyOCR au chargement du module
EASYOCR_AVAILABLE, USING_LOCAL_MODELS = configure_easyocr()


def get_easyocr_info():
    """
    Retourne des informations sur la configuration EasyOCR actuelle
    """
    info = {
        'available': EASYOCR_AVAILABLE,
        'using_local_models': USING_LOCAL_MODELS,
        'local_model_path': LOCAL_MODEL_PATH,
        'model_files': [],
        'supported_languages': []
    }

    if LOCAL_MODEL_PATH:
        info['model_files'] = get_available_model_files(LOCAL_MODEL_PATH)
        info['supported_languages'] = detect_supported_languages(LOCAL_MODEL_PATH)
    elif EASYOCR_READER:
        # Pour les modèles système, on peut essayer de détecter les langues
        try:
            # EasyOCR stocke les langues dans reader.lang_list
            if hasattr(EASYOCR_READER, 'lang_list'):
                info['supported_languages'] = EASYOCR_READER.lang_list
        except:
            info['supported_languages'] = ['fr', 'en']  # Fallback

    return info


def ocr_easyocr(image_path, return_conf=True, verbose=False):
    """
    Effectue l'OCR avec EasyOCR en utilisant les modèles locaux en priorité

    Args:
        image_path: Chemin vers l'image à traiter (ou objet PIL Image)
        return_conf: Si True, retourne aussi les scores de confiance
        verbose: Active les logs détaillés

    Returns:
        tuple: (lignes, confidences) si return_conf=True, sinon lignes seulement
    """
    if not EASYOCR_AVAILABLE or EASYOCR_READER is None:
        error_msg = "[ERROR] EasyOCR non disponible"
        print(error_msg)
        if return_conf:
            return [error_msg], [0]
        return [error_msg]

    try:
        if verbose:
            info = get_easyocr_info()
            print(f"[CONFIG] Configuration EasyOCR:")
            print(f"   [FOLDER] Modèles locaux: {'[OK]' if info['using_local_models'] else '[ERROR]'}")
            print(f"   [LANG] Langues: {', '.join(info['supported_languages'])}")
            if info['local_model_path']:
                print(f"   [FOLDER] Chemin modèles: {info['local_model_path']}")
                print(f"   [MODEL] Fichiers modèles: {', '.join(info['model_files'])}")

        # Exécuter l'OCR
        if verbose:
            print(f"[PROCESS] Exécution EasyOCR...")

        results = EASYOCR_READER.readtext(image_path)

        # Traiter les résultats
        lines = []
        confidences = []

        for detection in results:
            # EasyOCR retourne (bbox, text, confidence)
            text = detection[1].strip()
            confidence = detection[2] * 100  # Convertir en pourcentage

            # Filtrer les détections avec très faible confiance ou texte vide
            if text and confidence > 10:  # Seuil minimum de confiance
                lines.append(text)
                confidences.append(confidence)

        if verbose:
            avg_conf = sum(confidences) / len(confidences) if confidences else 0
            print(f"[OK] EasyOCR terminé:")
            print(f"   [STATS] Détections: {len(results)} → {len(lines)} filtrées")
            print(f"   [STATS] Confiance moyenne: {avg_conf:.1f}%")
            if USING_LOCAL_MODELS:
                print(f"   [LOCAL] Modèles locaux utilisés")
            else:
                print(f"   [SYSTEM] Modèles système utilisés")

        # Retourner les résultats selon le format demandé
        if not lines:
            lines = ["Aucun texte détecté"]
            confidences = [0]

        if return_conf:
            return lines, confidences
        else:
            return lines

    except Exception as e:
        error_msg = f"Erreur EasyOCR: {str(e)}"
        print(f"[ERROR] {error_msg}")

        # Diagnostic en cas d'erreur
        if verbose or "model" in str(e).lower():
            print("[DIAG] Diagnostic:")
            print(f"   Modèles locaux: {'[OK]' if USING_LOCAL_MODELS else '[ERROR]'}")
            print(f"   Chemin modèles: {LOCAL_MODEL_PATH}")

            if LOCAL_MODEL_PATH:
                available_models = get_available_model_files(LOCAL_MODEL_PATH)
                print(f"   Modèles disponibles: {available_models}")

        if return_conf:
            return [error_msg], [0]
        else:
            return [error_msg]


def test_easyocr_configuration():
    """
    Teste la configuration EasyOCR et affiche des informations détaillées
    Utile pour le debug et la validation de l'installation
    """
    print("[TEST] TEST DE LA CONFIGURATION EASYOCR")
    print("="*50)

    # Informations générales
    info = get_easyocr_info()

    print(f"[INFO] État général:")
    print(f"   Disponible: {'[OK]' if info['available'] else '[ERROR]'}")
    print(f"   Modèles locaux: {'[OK]' if info['using_local_models'] else '[ERROR]'}")
    print(f"   Chemin modèles: {info['local_model_path'] or 'Système'}")

    if info['supported_languages']:
        print(f"   Langues: {', '.join(info['supported_languages'])}")
    else:
        print(f"   Langues: Aucune détectée")

    # Test des modèles locaux
    local_model_path = get_local_model_path()
    if local_model_path:
        print(f"\n[FOLDER] Modèles locaux:")
        print(f"   Chemin: {local_model_path}")
        local_models = get_available_model_files(local_model_path)
        print(f"   Fichiers: {', '.join(local_models) if local_models else 'Aucun'}")

        # Lister les fichiers de modèles avec tailles
        model_files = glob.glob(os.path.join(local_model_path, '*.pth'))
        for model_file in model_files:
            size = os.path.getsize(model_file)
            print(f"   [FILE] {os.path.basename(model_file)} ({size:,} bytes)")
    else:
        print(f"\n[FOLDER] Modèles locaux: Non trouvés")

    # Test basique si EasyOCR est disponible
    if info['available'] and EASYOCR_READER:
        print(f"\n[TEST] Test basique:")
        try:
            # Créer une image de test simple
            from PIL import Image, ImageDraw, ImageFont
            import tempfile

            # Image de test avec du texte
            test_image = Image.new('RGB', (300, 100), color='white')
            draw = ImageDraw.Draw(test_image)

            try:
                # Essayer d'utiliser une police par défaut
                font = ImageFont.load_default()
            except:
                font = None

            draw.text((10, 30), "Test EasyOCR 123", fill='black', font=font)

            # Sauvegarder temporairement
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                test_image.save(tmp_file.name)
                tmp_path = tmp_file.name

            try:
                # Test OCR
                lines, confidences = ocr_easyocr(tmp_path, return_conf=True, verbose=True)

                if lines and any("Test" in line or "EasyOCR" in line or "123" in line for line in lines):
                    print(f"   [OK] Test réussi: {lines}")
                else:
                    print(f"   [WARNING] Test partiel: {lines}")

            finally:
                # Nettoyer le fichier temporaire
                try:
                    os.unlink(tmp_path)
                except:
                    pass

        except Exception as e:
            print(f"   [ERROR] Test échoué: {e}")

    print("\n" + "="*50)

    return info['available']