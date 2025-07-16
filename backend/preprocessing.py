"""
Module de préprocessing d'images pour l'OCR
Fournit différentes méthodes d'optimisation selon le moteur OCR utilisé
"""
import cv2
import numpy as np

def preprocess_image(path, method="enhanced"):
    """
    Préprocessing d'image avec différentes méthodes optimisées

    Args:
        path (str): Chemin vers l'image à traiter
        method (str): Méthode de préprocessing
            - "basic": Conversion simple en niveaux de gris
            - "enhanced": Préprocessing avancé avec correction d'inclinaison
            - "tesseract_optimized": Optimisé spécifiquement pour Tesseract

    Returns:
        numpy.ndarray: Image préprocessée
    """
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(f"Image introuvable : {path}")

    if method == "basic":
        # Conversion simple en niveaux de gris
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    elif method == "tesseract_optimized":
        # Préprocessing optimisé pour Tesseract
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Améliorer le contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)

        # Débruitage
        gray = cv2.bilateralFilter(gray, 9, 75, 75)

        # Binarisation adaptative améliorée
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 15, 10)

        # Morphologie pour nettoyer
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        # Redimensionner si l'image est trop petite
        height, width = binary.shape
        if height < 300 or width < 300:
            scale_factor = max(300/height, 300/width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            binary = cv2.resize(binary, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        return binary

    else:  # method == "enhanced" (défaut)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Correction de l'inclinaison (deskewing)
        coords = cv2.findNonZero(cv2.bitwise_not(gray))
        if coords is not None:
            angle = cv2.minAreaRect(coords)[-1]
            angle = -(90 + angle) if angle < -45 else -angle
            (h, w) = gray.shape[:2]
            M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
            gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        # Binarisation adaptative
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)

        # Débruitage
        binary = cv2.medianBlur(binary, 3)

        # Morphologie
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        return cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)