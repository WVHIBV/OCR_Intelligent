"""
Module d'évaluation de la qualité OCR
Fournit des métriques avancées pour évaluer et améliorer la fiabilité des résultats OCR
"""
import re
import logging
from typing import List, Tuple, Dict
from collections import Counter

logger = logging.getLogger(__name__)


def evaluate_text_quality(lines: List[str], confidences: List[float]) -> Dict[str, float]:
    """
    Évalue la qualité du texte OCR selon plusieurs critères
    
    Args:
        lines: Liste des lignes de texte détectées
        confidences: Liste des scores de confiance correspondants
    
    Returns:
        Dict contenant les métriques de qualité
    """
    if not lines or not confidences:
        return {"overall_quality": 0.0, "confidence_adjusted": 0.0}
    
    metrics = {}
    
    # 1. Analyse de la cohérence des caractères
    metrics["character_consistency"] = _evaluate_character_consistency(lines)
    
    # 2. Analyse de la structure du document
    metrics["document_structure"] = _evaluate_document_structure(lines)
    
    # 3. Analyse de la densité d'information
    metrics["information_density"] = _evaluate_information_density(lines)
    
    # 4. Analyse des erreurs typiques OCR
    metrics["ocr_error_penalty"] = _evaluate_ocr_errors(lines)
    
    # 5. Confiance ajustée basée sur la qualité
    base_confidence = sum(confidences) / len(confidences)
    quality_factor = (
        metrics["character_consistency"] * 0.3 +
        metrics["document_structure"] * 0.25 +
        metrics["information_density"] * 0.25 +
        (1 - metrics["ocr_error_penalty"]) * 0.2
    )
    
    metrics["confidence_adjusted"] = base_confidence * quality_factor
    metrics["overall_quality"] = quality_factor * 100
    
    return metrics


def _evaluate_character_consistency(lines: List[str]) -> float:
    """Évalue la cohérence des caractères détectés"""
    if not lines:
        return 0.0
    
    total_chars = 0
    valid_chars = 0
    
    for line in lines:
        for char in line:
            total_chars += 1
            # Caractères valides : lettres, chiffres, ponctuation courante, espaces
            if char.isalnum() or char in " .,;:!?-()[]{}\"'€$%/\\@#&*+=<>":
                valid_chars += 1
    
    return valid_chars / total_chars if total_chars > 0 else 0.0


def _evaluate_document_structure(lines: List[str]) -> float:
    """Évalue la structure logique du document"""
    if not lines:
        return 0.0
    
    structure_score = 0.0
    total_weight = 0.0
    
    # Recherche de patterns de document structuré
    patterns = {
        "dates": r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        "amounts": r'\b\d+[.,]\d{2}\s*[€$]\b',
        "references": r'\b[A-Z]{2,}\d+\b',
        "emails": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phones": r'\b\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}\b'
    }
    
    text = " ".join(lines)
    
    for pattern_name, pattern in patterns.items():
        matches = len(re.findall(pattern, text, re.IGNORECASE))
        if matches > 0:
            structure_score += matches * 0.2
            total_weight += 0.2
    
    # Bonus pour la présence de mots-clés de documents
    keywords = ['facture', 'invoice', 'total', 'date', 'montant', 'prix', 'tva']
    keyword_count = sum(1 for line in lines for keyword in keywords if keyword.lower() in line.lower())
    
    if keyword_count > 0:
        structure_score += keyword_count * 0.1
        total_weight += 0.1
    
    return min(1.0, structure_score / max(1.0, total_weight))


def _evaluate_information_density(lines: List[str]) -> float:
    """Évalue la densité d'information utile"""
    if not lines:
        return 0.0
    
    total_chars = sum(len(line) for line in lines)
    meaningful_chars = 0
    
    for line in lines:
        # Compter les caractères significatifs (pas juste des espaces ou caractères isolés)
        clean_line = line.strip()
        if len(clean_line) > 2:  # Lignes avec au moins 3 caractères
            meaningful_chars += len(clean_line)
    
    density = meaningful_chars / total_chars if total_chars > 0 else 0.0
    
    # Bonus pour les lignes de longueur raisonnable (ni trop courtes ni trop longues)
    reasonable_lines = sum(1 for line in lines if 5 <= len(line.strip()) <= 100)
    line_quality = reasonable_lines / len(lines) if lines else 0.0
    
    return (density + line_quality) / 2


def _evaluate_ocr_errors(lines: List[str]) -> float:
    """Évalue la présence d'erreurs typiques OCR (retourne un score de pénalité)"""
    if not lines:
        return 0.0
    
    error_count = 0
    total_words = 0
    
    # Patterns d'erreurs OCR courantes
    error_patterns = [
        r'\b[Il1|]{2,}\b',  # Confusion I/l/1/|
        r'\b[O0]{2,}\b',    # Confusion O/0
        r'\b[rn]{2,}m\b',   # Confusion rn/m
        r'\b[cl]{2,}\b',    # Confusion c/l
        r'[^\w\s.,;:!?()-]', # Caractères étranges
    ]
    
    text = " ".join(lines)
    words = text.split()
    total_words = len(words)
    
    for pattern in error_patterns:
        matches = len(re.findall(pattern, text, re.IGNORECASE))
        error_count += matches
    
    # Recherche de mots avec trop de caractères répétés
    for word in words:
        if len(word) > 3:
            # Compter les caractères consécutifs identiques
            consecutive_count = 1
            max_consecutive = 1
            for i in range(1, len(word)):
                if word[i] == word[i-1]:
                    consecutive_count += 1
                    max_consecutive = max(max_consecutive, consecutive_count)
                else:
                    consecutive_count = 1
            
            if max_consecutive > 3:  # Plus de 3 caractères identiques consécutifs
                error_count += 1
    
    return min(1.0, error_count / max(1, total_words))


def adjust_confidence_with_quality(lines: List[str], confidences: List[float]) -> List[float]:
    """
    Ajuste les scores de confiance en fonction de la qualité évaluée
    
    Args:
        lines: Liste des lignes de texte
        confidences: Liste des scores de confiance originaux
    
    Returns:
        Liste des scores de confiance ajustés
    """
    if not lines or not confidences or len(lines) != len(confidences):
        return confidences
    
    quality_metrics = evaluate_text_quality(lines, confidences)
    quality_factor = quality_metrics["overall_quality"] / 100
    
    adjusted_confidences = []
    
    for i, (line, conf) in enumerate(zip(lines, confidences)):
        # Ajustement individuel par ligne
        line_quality = 1.0
        
        # Pénalité pour les lignes très courtes
        if len(line.strip()) <= 2:
            line_quality *= 0.7
        
        # Bonus pour les lignes avec contenu structuré
        if any(keyword in line.lower() for keyword in ['facture', 'total', 'date', 'montant']):
            line_quality *= 1.1
        elif re.search(r'\d+[.,]\d{2}', line):  # Montants
            line_quality *= 1.05
        
        # Appliquer l'ajustement global et individuel
        adjusted_conf = conf * quality_factor * line_quality
        adjusted_conf = max(0.0, min(99.0, adjusted_conf))  # Borner entre 0 et 99%
        
        adjusted_confidences.append(adjusted_conf)
    
    return adjusted_confidences


def get_quality_report(lines: List[str], confidences: List[float]) -> str:
    """
    Génère un rapport de qualité détaillé
    
    Args:
        lines: Liste des lignes de texte
        confidences: Liste des scores de confiance
    
    Returns:
        Rapport de qualité formaté
    """
    if not lines or not confidences:
        return "Aucune donnée à analyser"
    
    metrics = evaluate_text_quality(lines, confidences)
    
    report = f"""
📊 RAPPORT DE QUALITÉ OCR
========================

🎯 Qualité Globale: {metrics['overall_quality']:.1f}%
📈 Confiance Ajustée: {metrics['confidence_adjusted']:.1f}%

📋 Métriques Détaillées:
• Cohérence des caractères: {metrics['character_consistency']*100:.1f}%
• Structure du document: {metrics['document_structure']*100:.1f}%
• Densité d'information: {metrics['information_density']*100:.1f}%
• Erreurs OCR détectées: {metrics['ocr_error_penalty']*100:.1f}%

📝 Statistiques:
• Nombre de lignes: {len(lines)}
• Caractères totaux: {sum(len(line) for line in lines)}
• Confiance moyenne originale: {sum(confidences)/len(confidences):.1f}%
"""
    
    return report
