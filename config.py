"""
Configuration centralisée pour l'application OCR Intelligent
"""
from pathlib import Path
import os

# Configuration des chemins
PROJECT_ROOT = Path(__file__).parent
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUT_DIR = PROJECT_ROOT / "output"
CORRECTED_DIR = PROJECT_ROOT / "corrected"
IMAGES_DIR = PROJECT_ROOT / "images"

# Configuration des modèles OCR
OCR_MODELS = {
    "tesseract": {
        "tessdata_path": MODELS_DIR / "tesseract" / "tessdata",
        "languages": ["fra", "eng"]
    },
    "easyocr": {
        "model_storage_directory": MODELS_DIR / "easyocr",
        "languages": ["fr", "en"]
    },
    "doctr": {
        "models_dir": MODELS_DIR / "doctr",
        "det_arch": "db_mobilenet_v3_large",
        "reco_arch": "crnn_vgg16_bn"
    }
}

# Configuration de l'application
APP_CONFIG = {
    "title": "OCR Intelligent",
    "page_icon": ":page_facing_up:",
    "layout": "wide",
    "default_confidence_threshold": 30,
    "supported_formats": ["png", "jpg", "jpeg", "bmp", "tiff", "pdf"],
    "max_file_size_mb": 50
}

# Configuration de l'environnement
ENV_CONFIG = {
    "KMP_DUPLICATE_LIB_OK": "TRUE",
    "CUDA_VISIBLE_DEVICES": "",
    "TF_CPP_MIN_LOG_LEVEL": "3"
}

# Configuration du logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": PROJECT_ROOT / "logs" / "ocr_app.log"
}

def setup_environment():
    """Configure les variables d'environnement"""
    for key, value in ENV_CONFIG.items():
        os.environ[key] = value

def ensure_directories():
    """Assure que tous les répertoires nécessaires existent"""
    directories = [OUTPUT_DIR, CORRECTED_DIR, LOGGING_CONFIG["log_file"].parent]
    
    for directory in directories:
        directory.mkdir(exist_ok=True)

def get_model_path(ocr_engine: str, model_type: str = None) -> Path:
    """
    Retourne le chemin vers un modèle spécifique
    
    Args:
        ocr_engine: Le moteur OCR (tesseract, easyocr, doctr)
        model_type: Le type de modèle (optionnel)
        
    Returns:
        Path vers le modèle
    """
    if ocr_engine not in OCR_MODELS:
        raise ValueError(f"Moteur OCR non supporté: {ocr_engine}")
    
    config = OCR_MODELS[ocr_engine]
    
    if ocr_engine == "tesseract":
        return config["tessdata_path"]
    elif ocr_engine == "easyocr":
        return config["model_storage_directory"]
    elif ocr_engine == "doctr":
        return config["models_dir"]
    
    return MODELS_DIR / ocr_engine
