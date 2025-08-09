"""
Module pour corriger et valider les coordonnées des zones OCR
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple
import os

def validate_and_fix_coordinates(zone_ocr_results: Dict, image_path: str) -> Dict:
    """
    Valide et corrige les coordonnées des zones par rapport à l'image
    
    Args:
        zone_ocr_results: Résultats OCR avec zones
        image_path: Chemin vers l'image source
        
    Returns:
        Résultats avec coordonnées corrigées
    """
    
    if not os.path.exists(image_path):
        print(f"⚠️ Image non trouvée: {image_path}")
        return zone_ocr_results
    
    # Charger l'image pour obtenir ses dimensions
    image = cv2.imread(image_path)
    if image is None:
        print(f"⚠️ Impossible de charger l'image: {image_path}")
        return zone_ocr_results
    
    img_height, img_width = image.shape[:2]
    print(f"📐 Dimensions de l'image: {img_width}x{img_height}")
    
    corrected_results = {}
    
    for zone_id, zone_data in zone_ocr_results.items():
        if not isinstance(zone_data, dict) or "zone_info" not in zone_data:
            corrected_results[zone_id] = zone_data
            continue
            
        zone_info = zone_data["zone_info"]
        coords = zone_info.get("coordinates", {})
        
        # Coordonnées originales
        x = coords.get("x", 0)
        y = coords.get("y", 0)
        w = coords.get("width", 0)
        h = coords.get("height", 0)
        
        # Validation et correction
        corrected_x = max(0, min(x, img_width - 1))
        corrected_y = max(0, min(y, img_height - 1))
        corrected_w = max(1, min(w, img_width - corrected_x))
        corrected_h = max(1, min(h, img_height - corrected_y))
        
        # Vérifier si une correction était nécessaire
        needs_correction = (x != corrected_x or y != corrected_y or 
                           w != corrected_w or h != corrected_h)
        
        if needs_correction:
            print(f"🔧 Zone {zone_id} corrigée:")
            print(f"   Avant: x={x}, y={y}, w={w}, h={h}")
            print(f"   Après: x={corrected_x}, y={corrected_y}, w={corrected_w}, h={corrected_h}")
        
        # Créer une copie avec les coordonnées corrigées
        corrected_zone_data = zone_data.copy()
        corrected_zone_info = zone_info.copy()
        corrected_coords = coords.copy()
        
        corrected_coords.update({
            "x": corrected_x,
            "y": corrected_y,
            "width": corrected_w,
            "height": corrected_h
        })
        
        corrected_zone_info["coordinates"] = corrected_coords
        corrected_zone_data["zone_info"] = corrected_zone_info
        
        corrected_results[zone_id] = corrected_zone_data
    
    return corrected_results

def check_zone_text_correspondence(zone_ocr_results: Dict) -> List[Dict]:
    """
    Vérifie la correspondance entre les zones et leur texte OCR
    
    Args:
        zone_ocr_results: Résultats OCR avec zones
        
    Returns:
        Liste des problèmes trouvés
    """
    
    issues = []
    
    for zone_id, zone_data in zone_ocr_results.items():
        if not isinstance(zone_data, dict) or "zone_info" not in zone_data:
            continue
            
        zone_info = zone_data["zone_info"]
        best_text = zone_data.get("best_text", "")
        confidence = zone_data.get("confidence", 0)
        coords = zone_info.get("coordinates", {})
        zone_type = zone_info.get("type", "unknown")
        
        # Vérifications
        if not best_text.strip():
            issues.append({
                "zone_id": zone_id,
                "type": "empty_text",
                "message": f"Zone {zone_id} ({zone_type}) n'a pas de texte"
            })
        
        if confidence < 0.3:
            issues.append({
                "zone_id": zone_id,
                "type": "low_confidence",
                "message": f"Zone {zone_id} a une confiance très faible ({confidence:.1%})"
            })
        
        # Vérifier la cohérence type/contenu
        if zone_type == "price" and not any(char in best_text for char in "€$0123456789"):
            issues.append({
                "zone_id": zone_id,
                "type": "type_mismatch",
                "message": f"Zone {zone_id} classée 'price' mais contient: '{best_text[:30]}...'"
            })
        
        if zone_type == "date" and not any(char in best_text for char in "0123456789/-"):
            issues.append({
                "zone_id": zone_id,
                "type": "type_mismatch",
                "message": f"Zone {zone_id} classée 'date' mais contient: '{best_text[:30]}...'"
            })
    
    return issues

def debug_zone_positions(zone_ocr_results: Dict, image_path: str) -> None:
    """
    Affiche des informations de debug sur les positions des zones
    """
    
    print("\n🔍 DEBUG - Positions des zones:")
    print("=" * 50)
    
    if not zone_ocr_results:
        print("Aucune donnée de zone disponible")
        return
    
    # Charger l'image pour le contexte
    if os.path.exists(image_path):
        image = cv2.imread(image_path)
        if image is not None:
            img_height, img_width = image.shape[:2]
            print(f"📐 Image: {img_width}x{img_height}")
        else:
            img_width = img_height = "?"
    else:
        img_width = img_height = "?"
    
    # Analyser chaque zone
    successful_zones = [z for z in zone_ocr_results.values() 
                       if isinstance(z, dict) and "error" not in z and "zone_info" in z]
    
    print(f"📊 Zones analysées: {len(successful_zones)}")
    
    for i, zone_data in enumerate(successful_zones):
        zone_info = zone_data["zone_info"]
        coords = zone_info.get("coordinates", {})
        
        x = coords.get("x", 0)
        y = coords.get("y", 0)
        w = coords.get("width", 0)
        h = coords.get("height", 0)
        
        zone_type = zone_info.get("type", "unknown")
        text = zone_data.get("best_text", "")[:30]
        confidence = zone_data.get("confidence", 0)
        
        print(f"\n🎯 Zone {zone_info['zone_id']} ({zone_type}):")
        print(f"   Position: ({x}, {y}) → ({x+w}, {y+h})")
        print(f"   Taille: {w}x{h}")
        print(f"   Texte: '{text}{'...' if len(zone_data.get('best_text', '')) > 30 else ''}' ")
        print(f"   Confiance: {confidence:.1%}")
        
        # Vérifier si les coordonnées sont dans les limites
        if isinstance(img_width, int) and isinstance(img_height, int):
            out_of_bounds = (x < 0 or y < 0 or x + w > img_width or y + h > img_height)
            if out_of_bounds:
                print(f"   ⚠️  HORS LIMITES!")

def create_debug_image(zone_ocr_results: Dict, image_path: str, output_path: str = None) -> str:
    """
    Crée une image de debug avec les zones annotées et numérotées
    
    Args:
        zone_ocr_results: Résultats OCR avec zones
        image_path: Chemin vers l'image source
        output_path: Chemin de sortie (optionnel)
        
    Returns:
        Chemin vers l'image de debug créée
    """
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image non trouvée: {image_path}")
    
    # Charger l'image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Impossible de charger l'image: {image_path}")
    
    debug_image = image.copy()
    
    # Couleurs pour différents types
    colors = {
        "header": (0, 255, 0),      # Vert
        "price": (0, 165, 255),     # Orange
        "date": (255, 0, 0),        # Bleu
        "address": (255, 255, 0),   # Cyan
        "paragraph": (128, 0, 128), # Violet
        "signature": (255, 0, 255), # Magenta
        "reference": (0, 255, 255), # Jaune
        "unknown": (128, 128, 128)  # Gris
    }
    
    successful_zones = [z for z in zone_ocr_results.values() 
                       if isinstance(z, dict) and "error" not in z and "zone_info" in z]
    
    for i, zone_data in enumerate(successful_zones):
        zone_info = zone_data["zone_info"]
        coords = zone_info.get("coordinates", {})
        
        x = coords.get("x", 0)
        y = coords.get("y", 0)
        w = coords.get("width", 0)
        h = coords.get("height", 0)
        
        zone_type = zone_info.get("type", "unknown")
        zone_id = zone_info.get("zone_id", i+1)
        
        # Couleur selon le type
        color = colors.get(zone_type, colors["unknown"])
        
        # Dessiner le rectangle
        cv2.rectangle(debug_image, (x, y), (x + w, y + h), color, 2)
        
        # Ajouter le numéro de zone
        cv2.putText(debug_image, str(zone_id), (x + 5, y + 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Ajouter le type
        cv2.putText(debug_image, zone_type[:8], (x + 5, y + h - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    # Sauvegarder l'image de debug
    if output_path is None:
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_path = f"debug_zones_{base_name}.png"
    
    cv2.imwrite(output_path, debug_image)
    print(f"📷 Image de debug sauvegardée: {output_path}")
    
    return output_path
