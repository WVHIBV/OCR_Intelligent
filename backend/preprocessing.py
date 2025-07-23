"""
Module de préprocessing d'images pour l'OCR
Fournit différentes méthodes d'optimisation selon le moteur OCR utilisé
Inclut la détection et l'isolation des zones de texte
"""
import cv2
import numpy as np
import os
from typing import List, Tuple, Dict, Optional

# Importer la configuration si disponible
try:
    from config.config_zone_detection import get_config, DEFAULT_ZONE_CONFIG
except ImportError:
    # Configuration par défaut si le fichier de config n'est pas disponible
    DEFAULT_ZONE_CONFIG = {
        "min_area_ratio": 0.001,
        "max_area_ratio": 0.8,
        "min_width": 50,
        "min_height": 20,
        "min_aspect_ratio": 0.1,
        "max_aspect_ratio": 20,
        "clahe_clip_limit": 3.0,
        "clahe_tile_size": (8, 8),
        "bilateral_d": 9,
        "bilateral_sigma_color": 75,
        "bilateral_sigma_space": 75,
        "adaptive_block_size": 15,
        "adaptive_c": 10,
        "morph_horizontal_kernel": (25, 1),
        "morph_vertical_kernel": (1, 15),
        "final_kernel": (3, 3),
        "final_iterations": 2,
        "extraction_margin": 10,
    }

    def get_config(document_type="default"):
        return DEFAULT_ZONE_CONFIG.copy()

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


def detect_text_zones(image_path: str, output_dir: str = "output/text_zones",
                     document_type: str = "default", use_intelligent_detection: bool = True) -> Dict:
    """
    Détecte et isole les zones de texte dans une image

    Args:
        image_path (str): Chemin vers l'image à analyser
        output_dir (str): Dossier de sortie pour les zones isolées
        document_type (str): Type de document pour optimiser la détection
        use_intelligent_detection (bool): Utiliser le nouveau système intelligent

    Returns:
        Dict: Informations sur les zones détectées et chemins des images isolées
    """

    # Utiliser le nouveau système intelligent si demandé
    if use_intelligent_detection:
        try:
            from backend.intelligent_zone_detector import IntelligentZoneDetector

            detector = IntelligentZoneDetector(document_type)
            return detector.detect_and_classify_zones(image_path, output_dir)

        except Exception as e:
            # Fallback vers l'ancien système en cas d'erreur
            print(f"Erreur système intelligent, fallback vers système classique: {e}")
            pass
    try:
        # Récupérer la configuration pour le type de document
        config = get_config(document_type)

        # Créer le dossier de sortie
        os.makedirs(output_dir, exist_ok=True)

        # Charger l'image
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image introuvable : {image_path}")

        original_image = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Préprocessing pour la détection de zones avec configuration
        processed = _preprocess_for_zone_detection(gray, config)

        # Détecter les contours des zones de texte
        contours = _find_text_contours(processed)

        # Filtrer et regrouper les contours avec configuration
        text_zones = _filter_and_group_contours(contours, gray.shape, config)

        # Extraire et sauvegarder les zones avec configuration
        zone_info = _extract_and_save_zones(original_image, text_zones, output_dir,
                                           os.path.basename(image_path), config)

        # Créer une image avec les zones annotées
        annotated_path = _create_annotated_image(original_image, text_zones, output_dir,
                                                os.path.basename(image_path))

        return {
            "success": True,
            "total_zones": len(text_zones),
            "zones": zone_info,
            "annotated_image": annotated_path,
            "output_directory": output_dir
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "total_zones": 0,
            "zones": [],
            "annotated_image": None,
            "output_directory": output_dir
        }


def _preprocess_for_zone_detection(gray_image: np.ndarray, config: Dict) -> np.ndarray:
    """
    Préprocessing optimisé pour la détection de zones de texte
    """
    # Améliorer le contraste avec paramètres configurables
    clahe = cv2.createCLAHE(
        clipLimit=config.get("clahe_clip_limit", 3.0),
        tileGridSize=config.get("clahe_tile_size", (8, 8))
    )
    enhanced = clahe.apply(gray_image)

    # Débruitage adaptatif selon le type de document
    bilateral_d = config.get("bilateral_d", 7)
    if bilateral_d > 0:
        denoised = cv2.bilateralFilter(
            enhanced,
            bilateral_d,
            config.get("bilateral_sigma_color", 80),
            config.get("bilateral_sigma_space", 80)
        )
    else:
        denoised = enhanced

    # Binarisation adaptative avec paramètres configurables
    binary = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        config.get("adaptive_block_size", 15),
        config.get("adaptive_c", 10)
    )

    # Morphologie pour connecter les caractères selon le type de document
    h_kernel_size = config.get("morph_horizontal_kernel", (15, 1))
    v_kernel_size = config.get("morph_vertical_kernel", (1, 8))

    kernel_horizontal = cv2.getStructuringElement(cv2.MORPH_RECT, h_kernel_size)
    kernel_vertical = cv2.getStructuringElement(cv2.MORPH_RECT, v_kernel_size)

    # Connecter horizontalement (mots)
    horizontal = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_horizontal)

    # Connecter verticalement (lignes) si nécessaire
    if v_kernel_size[1] > 1:
        vertical = cv2.morphologyEx(horizontal, cv2.MORPH_CLOSE, kernel_vertical)
    else:
        vertical = horizontal

    # Dilatation finale configurable
    final_kernel_size = config.get("final_kernel", (2, 2))
    final_iterations = config.get("final_iterations", 1)

    if final_iterations > 0:
        kernel_final = cv2.getStructuringElement(cv2.MORPH_RECT, final_kernel_size)
        final = cv2.dilate(vertical, kernel_final, iterations=final_iterations)
    else:
        final = vertical

    return final


def _find_text_contours(processed_image: np.ndarray) -> List:
    """
    Trouve les contours des zones de texte potentielles avec approche multi-méthode
    """
    all_contours = []

    # Méthode 1: Contours externes (standard)
    contours1, _ = cv2.findContours(processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    all_contours.extend(contours1)

    # Méthode 2: Contours avec hiérarchie pour capturer les zones internes
    contours2, hierarchy = cv2.findContours(processed_image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is not None:
        # Ajouter les contours de niveau 0 et 1 (externes et premiers internes)
        for i, h in enumerate(hierarchy[0]):
            if h[3] == -1 or (h[3] != -1 and hierarchy[0][h[3]][3] == -1):  # Niveau 0 ou 1
                all_contours.append(contours2[i])

    # Méthode 3: Détection avec érosion pour capturer les zones fines
    kernel_erode = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    eroded = cv2.erode(processed_image, kernel_erode, iterations=1)
    contours3, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    all_contours.extend(contours3)

    # Méthode 4: Détection avec dilatation pour capturer les zones fragmentées
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    dilated = cv2.dilate(processed_image, kernel_dilate, iterations=1)
    contours4, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    all_contours.extend(contours4)

    # Éliminer les doublons en comparant les boîtes englobantes
    unique_contours = []
    bounding_rects = []

    for contour in all_contours:
        rect = cv2.boundingRect(contour)

        # Vérifier si cette boîte englobante est similaire à une existante
        is_duplicate = False
        for existing_rect in bounding_rects:
            if _rects_overlap_significantly(rect, existing_rect):
                is_duplicate = True
                break

        if not is_duplicate:
            unique_contours.append(contour)
            bounding_rects.append(rect)

    return unique_contours


def _rects_overlap_significantly(rect1, rect2, threshold=0.7):
    """
    Vérifie si deux rectangles se chevauchent significativement
    """
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2

    # Calculer l'intersection
    x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
    y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))

    if x_overlap == 0 or y_overlap == 0:
        return False

    intersection_area = x_overlap * y_overlap
    area1 = w1 * h1
    area2 = w2 * h2

    # Calculer le ratio de chevauchement par rapport à la plus petite zone
    min_area = min(area1, area2)
    overlap_ratio = intersection_area / min_area if min_area > 0 else 0

    return overlap_ratio > threshold


def _filter_and_group_contours(contours: List, image_shape: Tuple, config: Dict) -> List[Tuple[int, int, int, int]]:
    """
    Filtre et regroupe les contours pour former des zones de texte cohérentes (anti-superposition)
    """
    height, width = image_shape
    min_area = (width * height) * config["min_area_ratio"]
    max_area = (width * height) * config["max_area_ratio"]

    # Première passe: collecter toutes les zones potentielles avec filtrage plus strict
    potential_zones = []

    for contour in contours:
        # Calculer la boîte englobante
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h

        # Filtrer par taille avec seuils plus stricts pour éviter trop de zones
        min_area_threshold = min_area * 0.8  # Plus strict qu'avant
        if area < min_area_threshold or area > max_area:
            continue

        # Filtrer par ratio d'aspect avec seuils resserrés
        aspect_ratio = w / h if h > 0 else 0
        min_ratio = max(0.1, config["min_aspect_ratio"])     # Plus strict
        max_ratio = min(25, config["max_aspect_ratio"])      # Plus strict
        if aspect_ratio < min_ratio or aspect_ratio > max_ratio:
            continue

        # Filtrer par dimensions minimales plus strictes
        min_w = max(25, config["min_width"] * 0.8)   # Plus strict
        min_h = max(12, config["min_height"] * 0.8)  # Plus strict
        if w < min_w or h < min_h:
            continue

        # Calculer la densité de pixels pour éliminer les zones vides
        roi = cv2.boundingRect(contour)
        contour_area = cv2.contourArea(contour)
        if contour_area > 0:
            density = contour_area / area
            if density < 0.1:  # Éliminer les zones trop vides
                continue

        potential_zones.append((x, y, w, h, area, aspect_ratio))

    # Deuxième passe: regroupement intelligent avec anti-superposition
    grouped_zones = []
    used_zones = set()

    # Trier les zones par taille décroissante pour traiter les grandes zones en premier
    potential_zones_sorted = sorted(enumerate(potential_zones),
                                   key=lambda x: x[1][4], reverse=True)  # Trier par area

    for original_idx, (x1, y1, w1, h1, area1, ratio1) in potential_zones_sorted:
        if original_idx in used_zones:
            continue

        # Chercher les zones à fusionner (seulement les petites zones proches)
        group = [(x1, y1, w1, h1)]
        used_zones.add(original_idx)

        for other_idx, (x2, y2, w2, h2, area2, ratio2) in potential_zones_sorted:
            if other_idx in used_zones or other_idx == original_idx:
                continue

            # Fusionner seulement si la zone est significativement plus petite
            if area2 < area1 * 0.3 and _should_merge_zones(x1, y1, w1, h1, x2, y2, w2, h2, config):
                group.append((x2, y2, w2, h2))
                used_zones.add(other_idx)

        # Si on a plusieurs zones à fusionner, créer une zone englobante
        if len(group) > 1:
            min_x = min(x for x, y, w, h in group)
            min_y = min(y for x, y, w, h in group)
            max_x = max(x + w for x, y, w, h in group)
            max_y = max(y + h for x, y, w, h in group)

            merged_w = max_x - min_x
            merged_h = max_y - min_y
            merged_area = merged_w * merged_h

            # Vérifier que la zone fusionnée n'est pas trop grande
            if merged_area <= max_area and merged_area <= area1 * 2:  # Pas plus de 2x la zone principale
                grouped_zones.append((min_x, min_y, merged_w, merged_h))
            else:
                # Garder seulement la zone principale si la fusion est trop grande
                grouped_zones.append((x1, y1, w1, h1))
        else:
            grouped_zones.append((x1, y1, w1, h1))

    # Troisième passe: élimination agressive des superpositions et redondances
    final_zones = []

    # Trier par taille décroissante pour traiter les grandes zones en premier
    grouped_zones_sorted = sorted(grouped_zones, key=lambda z: z[2] * z[3], reverse=True)

    for i, (x1, y1, w1, h1) in enumerate(grouped_zones_sorted):
        is_redundant = False
        area1 = w1 * h1

        for j, (x2, y2, w2, h2) in enumerate(final_zones):
            area2 = w2 * h2

            # Calculer le chevauchement
            overlap_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
            overlap_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
            overlap_area = overlap_x * overlap_y

            if overlap_area > 0:
                # Calculer le pourcentage de chevauchement
                overlap_ratio1 = overlap_area / area1  # Chevauchement par rapport à la zone courante
                overlap_ratio2 = overlap_area / area2  # Chevauchement par rapport à la zone existante

                # Éliminer si chevauchement significatif (>50%)
                if overlap_ratio1 > 0.5 or overlap_ratio2 > 0.5:
                    is_redundant = True
                    break

                # Éliminer si une zone est complètement incluse dans l'autre
                if (x2 <= x1 and y2 <= y1 and x2 + w2 >= x1 + w1 and y2 + h2 >= y1 + h1):
                    is_redundant = True  # Zone courante incluse dans zone existante
                    break
                elif (x1 <= x2 and y1 <= y2 and x1 + w1 >= x2 + w2 and y1 + h1 >= y2 + h2):
                    # Zone existante incluse dans zone courante - remplacer
                    final_zones[j] = (x1, y1, w1, h1)
                    is_redundant = True
                    break

        if not is_redundant:
            final_zones.append((x1, y1, w1, h1))

    # Quatrième passe: élimination finale des zones trop petites ou aberrantes
    filtered_zones = []
    total_image_area = width * height

    for x, y, w, h in final_zones:
        area = w * h

        # Éliminer les zones trop petites par rapport à l'image
        if area < total_image_area * 0.0008:  # Moins de 0.08% de l'image
            continue

        # Éliminer les zones avec des ratios extrêmes
        aspect_ratio = w / h if h > 0 else 0
        if aspect_ratio < 0.05 or aspect_ratio > 50:
            continue

        filtered_zones.append((x, y, w, h))

    # Trier par position (de haut en bas, puis de gauche à droite)
    filtered_zones.sort(key=lambda zone: (zone[1], zone[0]))

    return filtered_zones


def _should_merge_zones(x1, y1, w1, h1, x2, y2, w2, h2, config):
    """
    Détermine si deux zones doivent être fusionnées (plus restrictif pour éviter les superpositions)
    """
    # Calculer les chevauchements
    h_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
    v_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))

    # Si les zones se chevauchent déjà, ne pas fusionner (éviter les superpositions)
    if h_overlap > 0 and v_overlap > 0:
        return False

    # Calculer les distances entre les zones
    if h_overlap > 0:  # Alignement horizontal
        vertical_gap = min(abs(y1 + h1 - y2), abs(y2 + h2 - y1))
        avg_height = (h1 + h2) / 2
        # Fusionner seulement si très proches verticalement
        return vertical_gap < avg_height * 0.3

    elif v_overlap > 0:  # Alignement vertical
        horizontal_gap = min(abs(x1 + w1 - x2), abs(x2 + w2 - x1))
        avg_width = (w1 + w2) / 2
        # Fusionner seulement si très proches horizontalement
        return horizontal_gap < avg_width * 0.2

    else:  # Aucun chevauchement
        # Calculer la distance euclidienne entre les centres
        center1_x, center1_y = x1 + w1/2, y1 + h1/2
        center2_x, center2_y = x2 + w2/2, y2 + h2/2
        distance = ((center1_x - center2_x)**2 + (center1_y - center2_y)**2)**0.5

        # Fusionner seulement si très proches et de taille similaire
        avg_size = ((w1 + h1) + (w2 + h2)) / 4
        size_ratio = min(w1*h1, w2*h2) / max(w1*h1, w2*h2)

        return distance < avg_size * 0.5 and size_ratio > 0.3


def _extract_and_save_zones(image: np.ndarray, zones: List[Tuple], output_dir: str,
                           base_filename: str, config: Dict) -> List[Dict]:
    """
    Extrait et sauvegarde chaque zone de texte comme image séparée
    """
    zone_info = []
    base_name = os.path.splitext(base_filename)[0]

    for i, (x, y, w, h) in enumerate(zones):
        # Extraire la zone avec une marge configurable
        margin = config["extraction_margin"]
        x_start = max(0, x - margin)
        y_start = max(0, y - margin)
        x_end = min(image.shape[1], x + w + margin)
        y_end = min(image.shape[0], y + h + margin)

        zone_image = image[y_start:y_end, x_start:x_end]

        # Nom du fichier pour cette zone
        zone_filename = f"{base_name}_zone_{i+1:02d}.png"
        zone_path = os.path.join(output_dir, zone_filename)

        # Sauvegarder la zone
        cv2.imwrite(zone_path, zone_image)

        zone_info.append({
            "zone_id": i + 1,
            "filename": zone_filename,
            "path": zone_path,
            "coordinates": {"x": x, "y": y, "width": w, "height": h},
            "area": w * h,
            "dimensions": {"width": x_end - x_start, "height": y_end - y_start}
        })

    return zone_info


def _create_annotated_image(image: np.ndarray, zones: List[Tuple], output_dir: str,
                           base_filename: str) -> str:
    """
    Crée une image annotée avec les zones de texte marquées
    """
    annotated = image.copy()
    base_name = os.path.splitext(base_filename)[0]

    # Couleurs pour les annotations
    colors = [
        (0, 255, 0),    # Vert
        (255, 0, 0),    # Bleu
        (0, 0, 255),    # Rouge
        (255, 255, 0),  # Cyan
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Jaune
    ]

    for i, (x, y, w, h) in enumerate(zones):
        color = colors[i % len(colors)]

        # Dessiner le rectangle
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)

        # Ajouter le numéro de zone
        label = f"Zone {i+1}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]

        # Position du label (au-dessus du rectangle si possible)
        label_y = y - 10 if y > 30 else y + h + 25
        label_x = x

        # Fond pour le texte
        cv2.rectangle(annotated, (label_x, label_y - label_size[1] - 5),
                     (label_x + label_size[0] + 5, label_y + 5), color, -1)

        # Texte
        cv2.putText(annotated, label, (label_x + 2, label_y - 2),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Sauvegarder l'image annotée
    annotated_filename = f"{base_name}_zones_annotees.png"
    annotated_path = os.path.join(output_dir, annotated_filename)
    cv2.imwrite(annotated_path, annotated)

    return annotated_path