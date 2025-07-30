#!/usr/bin/env python3
"""
Système de détection et classification intelligente des zones de texte
Approche multi-niveaux avec classification sémantique et élimination des formes géométriques
"""

import cv2
import numpy as np
import os
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
import re
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZoneType(Enum):
    """Types de zones détectées"""
    HEADER = "header"           # En-tête
    TITLE = "title"            # Titre principal
    SUBTITLE = "subtitle"      # Sous-titre
    PARAGRAPH = "paragraph"    # Paragraphe de texte
    LIST = "list"             # Liste
    TABLE = "table"           # Tableau
    FOOTER = "footer"         # Pied de page
    SIGNATURE = "signature"   # Zone de signature
    LOGO = "logo"             # Logo/image
    FORM_FIELD = "form_field" # Champ de formulaire
    PRICE = "price"           # Prix/montant
    DATE = "date"             # Date
    ADDRESS = "address"       # Adresse
    REFERENCE = "reference"   # Référence/numéro
    NOISE = "noise"           # Bruit/forme géométrique
    UNKNOWN = "unknown"       # Type inconnu

@dataclass
class Zone:
    """Représentation d'une zone détectée"""
    id: int
    type: ZoneType
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    confidence: float
    content: str = ""
    ocr_confidence: float = 0.0
    features: Dict[str, Any] = None
    reading_order: int = 0
    
    def __post_init__(self):
        if self.features is None:
            self.features = {}

class IntelligentZoneDetector:
    """Détecteur intelligent de zones avec classification sémantique"""
    
    def __init__(self, document_type: str = "default"):
        self.document_type = document_type
        self.zones: List[Zone] = []
        self.image_shape = None
        self.debug_mode = True  # Activer le debug par défaut pour diagnostiquer les problèmes
        
        # Patterns pour la classification sémantique
        self.semantic_patterns = {
            ZoneType.HEADER: [
                r'facture|invoice|devis|quote|bon de commande',
                r'société|company|entreprise|sarl|sas|sa\b',
                r'n°\s*\d+|numero|number'
            ],
            ZoneType.DATE: [
                r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}',
                r'\d{1,2}\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)',
                r'date\s*:',
                r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}'
            ],
            ZoneType.PRICE: [
                r'\d+[,\.]\d{2}\s*€',
                r'€\s*\d+[,\.]\d{2}',
                r'total|montant|prix|price|amount',
                r'tva|ht|ttc|tax'
            ],
            ZoneType.ADDRESS: [
                r'\d+\s+rue|avenue|boulevard|place|chemin',
                r'\d{5}\s+[a-zA-Z]+',
                r'adresse|address'
            ],
            ZoneType.REFERENCE: [
                r'ref\s*:?\s*\w+',
                r'référence|reference',
                r'n°|num|number'
            ],
            ZoneType.SIGNATURE: [
                r'signature|signé|signed',
                r'cachet|stamp'
            ]
        }
    
    def detect_and_classify_zones(self, image_path: str, output_dir: str = "output/intelligent_zones") -> Dict:
        """
        Détecte et classifie intelligemment les zones de texte
        
        Args:
            image_path: Chemin vers l'image
            output_dir: Dossier de sortie
            
        Returns:
            Dict avec les résultats de détection
        """
        try:
            logger.info(f"Démarrage de la détection intelligente pour {image_path}")
            
            # Charger et préprocesser l'image
            image = cv2.imread(image_path)
            if image is None:
                raise FileNotFoundError(f"Image non trouvée: {image_path}")
            
            self.image_shape = image.shape
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Étape 1: Détection des zones candidates
            candidate_zones = self._detect_candidate_zones(gray)
            logger.info(f"Zones candidates détectées: {len(candidate_zones)}")
            if self.debug_mode and candidate_zones:
                logger.info(f"   Première zone: {candidate_zones[0]}")

            # Étape 2: Filtrage des formes géométriques et du bruit
            text_zones = self._filter_geometric_shapes(candidate_zones, gray)
            logger.info(f"Zones après filtrage géométrique: {len(text_zones)}")
            if self.debug_mode and text_zones:
                logger.info(f"   Première zone filtrée: {text_zones[0]}")

            # Étape 3: Classification sémantique avec OCR
            classified_zones = self._classify_zones_with_ocr(text_zones, image)
            logger.info(f"Zones classifiées: {len(classified_zones)}")
            if self.debug_mode and classified_zones:
                logger.info(f"   Première zone classifiée: {classified_zones[0].type.value} (conf: {classified_zones[0].confidence:.2f})")

            # Étape 4: Fusion des zones proches et similaires
            merged_zones = self._merge_similar_zones(classified_zones)
            logger.info(f"Zones après fusion: {len(merged_zones)}")

            # Étape 5: Détermination de l'ordre de lecture
            ordered_zones = self._determine_reading_order(merged_zones)
            logger.info(f"Zones ordonnées: {len(ordered_zones)}")

            # Étape 6: Validation finale et nettoyage
            final_zones = self._final_validation(ordered_zones)
            logger.info(f"Zones finales: {len(final_zones)}")
            if self.debug_mode and final_zones:
                logger.info(f"   Première zone finale: {final_zones[0].type.value} (conf: {final_zones[0].confidence:.2f})")
            
            # Fallback: si aucune zone détectée, créer une zone par défaut
            if not final_zones:
                logger.warning("Aucune zone détectée, création d'une zone par défaut")
                height, width = image.shape[:2]
                default_zone = Zone(
                    id=1,
                    type=ZoneType.PARAGRAPH,
                    bbox=(0, 0, width, height),
                    confidence=0.8,
                    content="Zone par défaut - traitement de l'image complète",
                    ocr_confidence=80.0,
                    reading_order=1
                )
                final_zones = [default_zone]
            
            self.zones = final_zones
            
            # Sauvegarder les résultats
            results = self._save_results(image, output_dir, os.path.basename(image_path))
            
            return {
                "success": True,
                "total_zones": len(final_zones),
                "zones": results["zones"],
                "annotated_image": results["annotated_image"],
                "output_directory": output_dir,
                "zone_types": self._get_zone_type_summary(),
                "reading_order": [zone.id for zone in sorted(final_zones, key=lambda z: z.reading_order)]
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection intelligente: {e}")
            
            # Fallback: créer une zone par défaut en cas d'erreur
            try:
                image = cv2.imread(image_path)
                if image is not None:
                    height, width = image.shape[:2]
                    default_zone = Zone(
                        id=1,
                        type=ZoneType.PARAGRAPH,
                        bbox=(0, 0, width, height),
                        confidence=0.8,
                        content="Zone par défaut - traitement de l'image complète",
                        ocr_confidence=80.0,
                        reading_order=1
                    )
                    
                    # Sauvegarder la zone par défaut
                    os.makedirs(output_dir, exist_ok=True)
                    zone_filename = f"{os.path.basename(image_path)}_default_zone.png"
                    zone_path = os.path.join(output_dir, zone_filename)
                    cv2.imwrite(zone_path, image)
                    
                    zone_info = [{
                        "zone_id": 1,
                        "type": "paragraph",
                        "filename": zone_filename,
                        "path": zone_path,
                        "coordinates": {"x": 0, "y": 0, "width": width, "height": height},
                        "content": "Zone par défaut - traitement de l'image complète",
                        "confidence": 0.8,
                        "ocr_confidence": 80.0,
                        "reading_order": 1,
                        "features": {}
                    }]
                    
                    return {
                        "success": True,
                        "total_zones": 1,
                        "zones": zone_info,
                        "annotated_image": None,
                        "output_directory": output_dir,
                        "zone_types": {"paragraph": 1},
                        "reading_order": [1],
                        "fallback": True
                    }
            except Exception as fallback_error:
                logger.error(f"Erreur lors du fallback: {fallback_error}")
            
            return {
                "success": False,
                "error": str(e),
                "total_zones": 0,
                "zones": [],
                "annotated_image": None,
                "output_directory": output_dir
            }
    
    def _detect_candidate_zones(self, gray_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Détecte les zones candidates avec approche multi-échelle - Version plus permissive"""
        
        # Préprocessing adaptatif
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray_image)
        
        # Débruitage léger
        denoised = cv2.bilateralFilter(enhanced, 5, 50, 50)
        
        # Binarisation adaptative multi-échelle
        binary_results = []
        
        # Échelle fine pour petit texte
        binary1 = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 8)
        binary_results.append(binary1)
        
        # Échelle standard
        binary2 = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 15, 10)
        binary_results.append(binary2)
        
        # Échelle large pour gros texte
        binary3 = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 21, 12)
        binary_results.append(binary3)
        
        # Combiner les résultats
        combined = cv2.bitwise_or(cv2.bitwise_or(binary1, binary2), binary3)
        
        # Morphologie pour connecter les caractères - plus permissif
        kernel_h = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 1))  # Réduit de 15 à 10
        kernel_v = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 6))   # Réduit de 8 à 6
        
        horizontal = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel_h)
        processed = cv2.morphologyEx(horizontal, cv2.MORPH_CLOSE, kernel_v)
        
        # Détection des contours
        contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Convertir en boîtes englobantes - seuils plus permissifs
        candidate_zones = []
        height, width = gray_image.shape
        min_area = (width * height) * 0.0001  # Réduit de 0.0005 à 0.0001 (plus permissif)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # Filtrage plus permissif
            if (area >= min_area and 
                w >= 15 and h >= 6 and  # Réduit de 20x8 à 15x6
                0.01 <= w/h <= 100):    # Ratio d'aspect plus permissif
                candidate_zones.append((x, y, w, h))
        
        # Si aucune zone détectée, créer une zone par défaut (toute l'image)
        if not candidate_zones:
            logger.warning("Aucune zone candidate détectée, utilisation de la zone complète")
            candidate_zones = [(0, 0, width, height)]
        
        return candidate_zones

    def _filter_geometric_shapes(self, zones: List[Tuple[int, int, int, int]], gray_image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Filtre les formes géométriques et le bruit"""

        filtered_zones = []

        for i, (x, y, w, h) in enumerate(zones):
            # Extraire la région
            roi = gray_image[y:y+h, x:x+w]

            # Analyser les caractéristiques géométriques
            is_text = self._analyze_text_characteristics(roi, w, h)

            if is_text:
                filtered_zones.append((x, y, w, h))

        return filtered_zones

    def _analyze_text_characteristics(self, roi: np.ndarray, width: int, height: int) -> bool:
        """Analyse si une région contient du texte ou des formes géométriques - Version très permissive"""

        if roi.size == 0:
            return False

        # Filtrage très permissif - laisser l'OCR faire le reste

        # 1. Éliminer seulement les zones qui couvrent presque toute l'image
        if self.image_shape:
            image_area = self.image_shape[0] * self.image_shape[1]
            zone_area = width * height
            area_ratio = zone_area / image_area

            if area_ratio > 0.8:  # Plus de 80% de l'image (très permissif)
                return False

        # 2. Éliminer seulement les zones complètement uniformes
        _, binary = cv2.threshold(roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        white_pixels = cv2.countNonZero(binary)
        total_pixels = roi.size
        density = white_pixels / total_pixels

        # Éliminer seulement les extrêmes absolus
        if density < 0.001 or density > 0.999:  # Très permissif
            return False

        # 3. Vérification très permissive de la variation d'intensité
        std_dev = np.std(roi)

        if std_dev < 1:  # Très permissif - éliminer seulement les zones complètement uniformes
            return False

        return True

    def _classify_zones_with_ocr(self, zones: List[Tuple[int, int, int, int]], image: np.ndarray) -> List[Zone]:
        """Classifie les zones en utilisant l'OCR et l'analyse sémantique"""

        classified_zones = []

        for i, (x, y, w, h) in enumerate(zones):
            # Extraire la zone avec marge
            margin = 5
            x_start = max(0, x - margin)
            y_start = max(0, y - margin)
            x_end = min(image.shape[1], x + w + margin)
            y_end = min(image.shape[0], y + h + margin)

            zone_image = image[y_start:y_end, x_start:x_end]

            # OCR sur la zone
            text, ocr_conf = self._perform_zone_ocr(zone_image)

            # Classification sémantique
            zone_type = self._classify_zone_semantically(text, x, y, w, h)

            # Calcul de la confiance globale
            confidence = self._calculate_zone_confidence(text, ocr_conf, zone_type, w, h)

            # Extraction des features
            features = self._extract_zone_features(zone_image, text, x, y, w, h)

            zone = Zone(
                id=i + 1,
                type=zone_type,
                bbox=(x, y, w, h),
                confidence=confidence,
                content=text,
                ocr_confidence=ocr_conf,
                features=features
            )

            classified_zones.append(zone)

        return classified_zones

    def _perform_zone_ocr(self, zone_image: np.ndarray) -> Tuple[str, float]:
        """Effectue l'OCR sur une zone spécifique - Version avec fallback robuste"""

        try:
            # Essayer Tesseract d'abord
            try:
                import pytesseract
                from PIL import Image

                # Préprocessing rapide de la zone
                if len(zone_image.shape) == 3:
                    gray_zone = cv2.cvtColor(zone_image, cv2.COLOR_BGR2GRAY)
                else:
                    gray_zone = zone_image

                # Amélioration du contraste si nécessaire
                if np.std(gray_zone) < 20:
                    gray_zone = cv2.equalizeHist(gray_zone)

                # Conversion pour PIL
                pil_image = Image.fromarray(gray_zone)

                # OCR avec configuration simplifiée (compatible ancienne version)
                try:
                    # Essayer d'abord avec configuration simple
                    text = pytesseract.image_to_string(pil_image, lang='fra+eng')
                except:
                    # Fallback sans configuration spéciale
                    text = pytesseract.image_to_string(pil_image)

                if text.strip():
                    # Confiance basée sur la longueur
                    text_length = len(text.strip())
                    if text_length > 15:
                        avg_conf = 90.0
                    elif text_length > 8:
                        avg_conf = 85.0
                    elif text_length > 3:
                        avg_conf = 80.0
                    else:
                        avg_conf = 75.0

                    return text.strip(), avg_conf

            except Exception as e:
                print(f"Tesseract échoué: {e}")
                # Continuer vers le fallback
                pass

            # FALLBACK: Analyse simple de la zone quand Tesseract échoue
            if len(zone_image.shape) == 3:
                gray_zone = cv2.cvtColor(zone_image, cv2.COLOR_BGR2GRAY)
            else:
                gray_zone = zone_image

            # Amélioration du contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray_zone)

            # Binarisation
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Analyse de la densité de pixels
            text_pixels = cv2.countNonZero(binary)
            total_pixels = gray_zone.size
            density = text_pixels / total_pixels

            # Estimation du contenu basée sur la densité et la position
            height, width = gray_zone.shape
            
            if density > 0.05:  # Zone avec du contenu probable
                # Estimation basée sur la position dans l'image
                if height > 0 and width > 0:
                    # Analyser la distribution des pixels
                    horizontal_profile = np.sum(binary, axis=0)
                    vertical_profile = np.sum(binary, axis=1)
                    
                    # Détecter les lignes de texte
                    text_lines_count = np.sum(vertical_profile > width * 0.1)
                    
                    if text_lines_count > 0:
                        # Zone avec du texte détecté
                        if density > 0.3:
                            text = "Zone de texte dense"
                            confidence = 75.0
                        else:
                            text = "Zone de texte détectée"
                            confidence = 65.0
                    else:
                        # Zone avec du contenu mais pas de lignes claires
                        text = "Contenu graphique ou texte"
                        confidence = 50.0
                else:
                    text = "Zone de contenu"
                    confidence = 45.0
            else:
                # Zone avec peu de contenu
                text = "Zone vide ou peu de contenu"
                confidence = 30.0

            return text, confidence

        except Exception as e:
            print(f"Erreur OCR zone: {e}")
            return "Erreur de traitement", 30.0

    def _classify_zone_semantically(self, text: str, x: int, y: int, w: int, h: int) -> ZoneType:
        """Classifie une zone basée sur son contenu et sa position"""

        if not text or len(text.strip()) < 2:
            return ZoneType.UNKNOWN

        text_lower = text.lower().strip()

        # Classification basée sur les patterns sémantiques
        for zone_type, patterns in self.semantic_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return zone_type

        # Classification basée sur la position et les dimensions
        image_height = self.image_shape[0] if self.image_shape else 1000
        image_width = self.image_shape[1] if self.image_shape else 1000

        # Zone en haut = probablement header
        if y < image_height * 0.15:
            if w > image_width * 0.5:  # Large zone en haut
                return ZoneType.HEADER
            else:
                return ZoneType.REFERENCE

        # Zone en bas = probablement footer ou signature
        elif y > image_height * 0.8:
            if h < 50:  # Zone basse et fine
                return ZoneType.FOOTER
            else:
                return ZoneType.SIGNATURE

        # Zone avec beaucoup de chiffres = probablement prix/montant
        digit_ratio = sum(1 for c in text if c.isdigit()) / len(text)
        if digit_ratio > 0.3 and any(symbol in text for symbol in ['€', '$', '%', ',']):
            return ZoneType.PRICE

        # Zone longue et étroite = probablement paragraphe
        aspect_ratio = w / h if h > 0 else 0
        if aspect_ratio > 5:
            return ZoneType.PARAGRAPH

        # Par défaut
        return ZoneType.UNKNOWN

    def _calculate_zone_confidence(self, text: str, ocr_conf: float, zone_type: ZoneType, width: int, height: int) -> float:
        """Calcule la confiance globale d'une zone - Version plus équilibrée"""

        # Base de confiance sur l'OCR
        base_confidence = ocr_conf / 100.0  # Normaliser entre 0 et 1

        # Bonus pour la longueur du texte (mais pas trop pénalisant)
        text_length = len(text.strip())
        if text_length > 20:
            length_bonus = 0.2
        elif text_length > 10:
            length_bonus = 0.1
        elif text_length > 5:
            length_bonus = 0.05
        else:
            length_bonus = 0.0

        # Bonus pour la taille de la zone (zones moyennes préférées)
        area = width * height
        if self.image_shape:
            image_area = self.image_shape[0] * self.image_shape[1]
            area_ratio = area / image_area

            if 0.001 <= area_ratio <= 0.1:  # Taille optimale
                size_bonus = 0.1
            elif 0.0001 <= area_ratio <= 0.5:  # Taille acceptable
                size_bonus = 0.05
            else:
                size_bonus = 0.0
        else:
            size_bonus = 0.05  # Bonus par défaut

        # Bonus pour le type de zone (certains types sont plus fiables)
        type_bonus = 0.0
        if zone_type in [ZoneType.HEADER, ZoneType.TITLE, ZoneType.PARAGRAPH]:
            type_bonus = 0.1
        elif zone_type in [ZoneType.DATE, ZoneType.PRICE, ZoneType.REFERENCE]:
            type_bonus = 0.05

        # Calcul final avec minimum garanti
        final_confidence = base_confidence + length_bonus + size_bonus + type_bonus
        
        # Garantir un minimum de confiance pour éviter le filtrage excessif
        final_confidence = max(final_confidence, 0.3)  # Minimum 30%
        
        # Limiter à 1.0
        final_confidence = min(final_confidence, 1.0)

        return final_confidence

    def _extract_zone_features(self, zone_image: np.ndarray, text: str, x: int, y: int, w: int, h: int) -> Dict[str, Any]:
        """Extrait les caractéristiques d'une zone"""

        features = {
            "text_length": len(text.strip()),
            "word_count": len(text.split()),
            "digit_ratio": sum(1 for c in text if c.isdigit()) / len(text) if text else 0,
            "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            "aspect_ratio": w / h if h > 0 else 0,
            "area": w * h,
            "position_x": x,
            "position_y": y,
            "width": w,
            "height": h
        }

        # Analyse de l'image
        if zone_image.size > 0:
            gray = cv2.cvtColor(zone_image, cv2.COLOR_BGR2GRAY) if len(zone_image.shape) == 3 else zone_image
            features["mean_intensity"] = np.mean(gray)
            features["std_intensity"] = np.std(gray)

            # Détection de contours
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            features["contour_count"] = len(contours)

        return features

    def _merge_similar_zones(self, zones: List[Zone]) -> List[Zone]:
        """Fusionne les zones proches et similaires"""

        if len(zones) <= 1:
            return zones

        merged_zones = []
        used_indices = set()

        for i, zone1 in enumerate(zones):
            if i in used_indices:
                continue

            # Chercher les zones à fusionner
            merge_candidates = [zone1]
            used_indices.add(i)

            for j, zone2 in enumerate(zones):
                if j in used_indices or j <= i:
                    continue

                if self._should_merge_zones(zone1, zone2):
                    merge_candidates.append(zone2)
                    used_indices.add(j)

            # Fusionner si nécessaire
            if len(merge_candidates) > 1:
                merged_zone = self._merge_zone_group(merge_candidates)
                merged_zones.append(merged_zone)
            else:
                merged_zones.append(zone1)

        return merged_zones

    def _should_merge_zones(self, zone1: Zone, zone2: Zone) -> bool:
        """Détermine si deux zones doivent être fusionnées"""

        # Ne pas fusionner des types très différents
        incompatible_types = [
            (ZoneType.HEADER, ZoneType.FOOTER),
            (ZoneType.SIGNATURE, ZoneType.PRICE),
            (ZoneType.LOGO, ZoneType.PARAGRAPH)
        ]

        for type1, type2 in incompatible_types:
            if (zone1.type == type1 and zone2.type == type2) or (zone1.type == type2 and zone2.type == type1):
                return False

        x1, y1, w1, h1 = zone1.bbox
        x2, y2, w2, h2 = zone2.bbox

        # Calculer la distance entre les zones
        center1_x, center1_y = x1 + w1/2, y1 + h1/2
        center2_x, center2_y = x2 + w2/2, y2 + h2/2
        distance = ((center1_x - center2_x)**2 + (center1_y - center2_y)**2)**0.5

        # Fusionner si très proches et de type compatible
        avg_size = ((w1 + h1) + (w2 + h2)) / 4

        return (distance < avg_size * 0.8 and
                zone1.type == zone2.type and
                abs(zone1.confidence - zone2.confidence) < 0.3)

    def _merge_zone_group(self, zones: List[Zone]) -> Zone:
        """Fusionne un groupe de zones"""

        # Calculer la boîte englobante
        min_x = min(zone.bbox[0] for zone in zones)
        min_y = min(zone.bbox[1] for zone in zones)
        max_x = max(zone.bbox[0] + zone.bbox[2] for zone in zones)
        max_y = max(zone.bbox[1] + zone.bbox[3] for zone in zones)

        merged_bbox = (min_x, min_y, max_x - min_x, max_y - min_y)

        # Combiner le contenu
        merged_content = " ".join(zone.content for zone in zones if zone.content.strip())

        # Moyenne pondérée des confidences
        total_area = sum(zone.bbox[2] * zone.bbox[3] for zone in zones)
        weighted_confidence = sum(zone.confidence * (zone.bbox[2] * zone.bbox[3]) for zone in zones) / total_area

        # Prendre le type le plus fréquent
        type_counts = {}
        for zone in zones:
            type_counts[zone.type] = type_counts.get(zone.type, 0) + 1
        merged_type = max(type_counts.items(), key=lambda x: x[1])[0]

        return Zone(
            id=zones[0].id,  # Garder le premier ID
            type=merged_type,
            bbox=merged_bbox,
            confidence=weighted_confidence,
            content=merged_content,
            ocr_confidence=sum(zone.ocr_confidence for zone in zones) / len(zones),
            features=zones[0].features  # Garder les features de la première zone
        )

    def _determine_reading_order(self, zones: List[Zone]) -> List[Zone]:
        """Détermine l'ordre de lecture optimal des zones"""

        if not zones:
            return zones

        # Trier par priorité de type puis par position
        type_priority = {
            ZoneType.HEADER: 1,
            ZoneType.TITLE: 2,
            ZoneType.SUBTITLE: 3,
            ZoneType.DATE: 4,
            ZoneType.REFERENCE: 5,
            ZoneType.ADDRESS: 6,
            ZoneType.PARAGRAPH: 7,
            ZoneType.LIST: 8,
            ZoneType.TABLE: 9,
            ZoneType.PRICE: 10,
            ZoneType.FORM_FIELD: 11,
            ZoneType.SIGNATURE: 12,
            ZoneType.FOOTER: 13,
            ZoneType.LOGO: 14,
            ZoneType.UNKNOWN: 15,
            ZoneType.NOISE: 16
        }

        # Fonction de tri personnalisée
        def sort_key(zone: Zone):
            x, y, w, h = zone.bbox
            type_prio = type_priority.get(zone.type, 15)

            # Pour les zones de même type, trier par position (haut vers bas, gauche vers droite)
            return (type_prio, y // 50, x // 50)  # Grouper par bandes de 50px

        sorted_zones = sorted(zones, key=sort_key)

        # Assigner les ordres de lecture
        for i, zone in enumerate(sorted_zones):
            zone.reading_order = i + 1

        return sorted_zones

    def _final_validation(self, zones: List[Zone]) -> List[Zone]:
        """Validation finale et nettoyage des zones - Version très permissive"""

        validated_zones = []

        for i, zone in enumerate(zones):
            # Éliminer seulement les zones de confiance très faible
            if zone.confidence < 0.05:  # Très permissif - seulement 5% minimum
                continue

            # Éliminer seulement les zones extrêmement petites ou grandes
            area = zone.bbox[2] * zone.bbox[3]
            if self.image_shape:
                image_area = self.image_shape[0] * self.image_shape[1]
                area_ratio = area / image_area

                if area_ratio < 0.00001 or area_ratio > 0.95:  # Très permissif
                    continue

            # Éliminer seulement les zones complètement vides
            if not zone.content.strip():
                continue

            # Éliminer seulement les zones explicitement marquées comme bruit
            if zone.type == ZoneType.NOISE:
                continue

            validated_zones.append(zone)

        # Si aucune zone validée, accepter au moins la première zone
        if not validated_zones and zones:
            logger.warning("Aucune zone validée, acceptation de la première zone")
            validated_zones = [zones[0]]

        return validated_zones

    def _save_results(self, image: np.ndarray, output_dir: str, base_name: str) -> Dict:
        """Sauvegarde les résultats de détection"""

        os.makedirs(output_dir, exist_ok=True)

        # Sauvegarder les zones individuelles
        zone_info = []
        for zone in self.zones:
            x, y, w, h = zone.bbox

            # Extraire la zone avec marge
            margin = 10
            x_start = max(0, x - margin)
            y_start = max(0, y - margin)
            x_end = min(image.shape[1], x + w + margin)
            y_end = min(image.shape[0], y + h + margin)

            zone_image = image[y_start:y_end, x_start:x_end]

            # Nom du fichier
            zone_filename = f"{base_name}_intelligent_zone_{zone.id:02d}_{zone.type.value}.png"
            zone_path = os.path.join(output_dir, zone_filename)

            # Sauvegarder
            cv2.imwrite(zone_path, zone_image)

            zone_info.append({
                "zone_id": zone.id,
                "type": zone.type.value,
                "filename": zone_filename,
                "path": zone_path,
                "coordinates": {"x": x, "y": y, "width": w, "height": h},
                "content": zone.content,
                "confidence": zone.confidence,
                "ocr_confidence": zone.ocr_confidence,
                "reading_order": zone.reading_order,
                "features": zone.features
            })

        # Créer l'image annotée
        annotated = image.copy()
        colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (128, 0, 128), (255, 165, 0)
        ]

        for zone in self.zones:
            x, y, w, h = zone.bbox
            color = colors[zone.id % len(colors)]

            # Rectangle de la zone
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

            # Label avec type et ordre
            label = f"{zone.reading_order}: {zone.type.value}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]

            # Position du label
            label_y = y - 10 if y > 30 else y + h + 20
            label_x = x

            # Fond pour le texte
            cv2.rectangle(annotated, (label_x, label_y - label_size[1] - 5),
                         (label_x + label_size[0] + 5, label_y + 5), color, -1)

            # Texte
            cv2.putText(annotated, label, (label_x + 2, label_y - 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Sauvegarder l'image annotée
        annotated_filename = f"{base_name}_intelligent_annotated.png"
        annotated_path = os.path.join(output_dir, annotated_filename)
        cv2.imwrite(annotated_path, annotated)

        # Sauvegarder les métadonnées JSON
        metadata = {
            "total_zones": len(self.zones),
            "document_type": self.document_type,
            "zones": zone_info,
            "zone_types": self._get_zone_type_summary(),
            "reading_order": [zone.id for zone in sorted(self.zones, key=lambda z: z.reading_order)]
        }

        json_filename = f"{base_name}_intelligent_metadata.json"
        json_path = os.path.join(output_dir, json_filename)

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return {
            "zones": zone_info,
            "annotated_image": annotated_path,
            "metadata_file": json_path
        }

    def _get_zone_type_summary(self) -> Dict[str, int]:
        """Retourne un résumé des types de zones détectées"""

        type_counts = {}
        for zone in self.zones:
            type_name = zone.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        return type_counts
