# Configuration Tesseract pour OCR Intelligent
# Chemin vers Tesseract 5.x
TESSERACT_PATH = "C:\Program Files\Tesseract-OCR\tesseract.exe"

# Désactiver les modèles locaux pour forcer l'utilisation de la version système
USE_LOCAL_MODELS = False
TESSDATA_PREFIX = ""

# Configuration OCR
TESSERACT_CONFIG = "--oem 3 --psm 6"
LANGUAGES = "fra+eng"
