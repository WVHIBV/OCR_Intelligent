"""
Configuration avancée pour le système de détection intelligente des zones
"""

from typing import Dict, List, Any
from backend.intelligent_zone_detector import ZoneType

# Configuration par défaut pour la détection intelligente
INTELLIGENT_DETECTION_CONFIG = {
    # Paramètres de détection des zones candidates
    "candidate_detection": {
        "min_area_ratio": 0.0003,      # Minimum 0.03% de l'image
        "max_area_ratio": 0.7,         # Maximum 70% de l'image
        "min_width": 15,               # Largeur minimale en pixels
        "min_height": 8,               # Hauteur minimale en pixels
        "min_aspect_ratio": 0.02,      # Ratio largeur/hauteur minimum
        "max_aspect_ratio": 50,        # Ratio largeur/hauteur maximum
        
        # Paramètres de binarisation multi-échelle
        "fine_block_size": 11,         # Taille de bloc pour texte fin
        "standard_block_size": 15,     # Taille de bloc standard
        "large_block_size": 21,        # Taille de bloc pour gros texte
        "fine_c": 8,                   # Constante pour texte fin
        "standard_c": 10,              # Constante standard
        "large_c": 12,                 # Constante pour gros texte
        
        # Morphologie
        "horizontal_kernel": (15, 1),  # Kernel horizontal pour connecter les mots
        "vertical_kernel": (1, 8),     # Kernel vertical pour connecter les lignes
    },
    
    # Paramètres de filtrage des formes géométriques
    "geometric_filtering": {
        "min_density": 0.1,            # Densité minimale de pixels
        "max_density": 0.7,            # Densité maximale de pixels
        "min_std_dev": 20,             # Variation d'intensité minimale
        "max_straight_lines": 3,       # Nombre maximum de lignes droites
        "min_transitions_ratio": 0.1,  # Ratio minimum de transitions horizontales
        "max_regular_shape_area": 0.3, # Aire maximale pour formes régulières
    },
    
    # Paramètres de classification sémantique
    "semantic_classification": {
        "confidence_threshold": 0.2,   # Seuil de confiance minimum
        "ocr_confidence_weight": 0.4,  # Poids de la confiance OCR
        "type_bonus_weight": 0.3,      # Poids du bonus de type
        "text_length_weight": 0.2,     # Poids de la longueur du texte
        "size_bonus_weight": 0.1,      # Poids du bonus de taille
    },
    
    # Paramètres de fusion des zones
    "zone_merging": {
        "max_merge_distance_ratio": 0.8,  # Distance maximale pour fusion (ratio de taille moyenne)
        "max_confidence_diff": 0.3,       # Différence maximale de confiance
        "enable_type_compatibility": True, # Vérifier la compatibilité des types
    },
    
    # Paramètres de validation finale
    "final_validation": {
        "min_confidence": 0.2,         # Confiance minimale pour garder une zone
        "min_area_ratio": 0.0003,      # Aire minimale (ratio de l'image)
        "max_area_ratio": 0.8,         # Aire maximale (ratio de l'image)
        "min_content_length": 2,       # Longueur minimale du contenu
    }
}

# Configurations spécialisées par type de document
DOCUMENT_SPECIFIC_CONFIGS = {
    "facture": {
        **INTELLIGENT_DETECTION_CONFIG,
        "candidate_detection": {
            **INTELLIGENT_DETECTION_CONFIG["candidate_detection"],
            "min_area_ratio": 0.0002,      # Plus sensible pour les petits éléments
            "min_width": 12,               # Accepter des zones plus petites
            "min_height": 6,               # Accepter des lignes plus fines
        },
        "semantic_classification": {
            **INTELLIGENT_DETECTION_CONFIG["semantic_classification"],
            "confidence_threshold": 0.15,  # Plus permissif pour les factures
        }
    },
    
    "formulaire": {
        **INTELLIGENT_DETECTION_CONFIG,
        "candidate_detection": {
            **INTELLIGENT_DETECTION_CONFIG["candidate_detection"],
            "min_area_ratio": 0.0001,      # Très sensible pour les champs
            "min_width": 10,               # Champs très petits
            "min_height": 5,               # Lignes très fines
            "horizontal_kernel": (10, 1),  # Préserver les champs séparés
        },
        "zone_merging": {
            **INTELLIGENT_DETECTION_CONFIG["zone_merging"],
            "max_merge_distance_ratio": 0.5,  # Fusion plus restrictive
        }
    },
    
    "journal": {
        **INTELLIGENT_DETECTION_CONFIG,
        "candidate_detection": {
            **INTELLIGENT_DETECTION_CONFIG["candidate_detection"],
            "min_aspect_ratio": 0.3,       # Éviter les colonnes trop étroites
            "max_aspect_ratio": 15,        # Permettre les colonnes longues
            "vertical_kernel": (1, 12),    # Mieux connecter les paragraphes
        }
    },
    
    "manuscrit": {
        **INTELLIGENT_DETECTION_CONFIG,
        "candidate_detection": {
            **INTELLIGENT_DETECTION_CONFIG["candidate_detection"],
            "fine_block_size": 17,         # Bloc plus large pour écriture irrégulière
            "standard_block_size": 21,     # Adaptation à l'écriture manuscrite
            "horizontal_kernel": (20, 1),  # Connecter les mots manuscrits
        },
        "geometric_filtering": {
            **INTELLIGENT_DETECTION_CONFIG["geometric_filtering"],
            "min_std_dev": 15,             # Plus tolérant pour l'écriture manuscrite
        }
    },
    
    "tableau": {
        **INTELLIGENT_DETECTION_CONFIG,
        "candidate_detection": {
            **INTELLIGENT_DETECTION_CONFIG["candidate_detection"],
            "min_aspect_ratio": 0.1,       # Accepter des cellules rectangulaires
            "max_aspect_ratio": 20,        # Cellules allongées
            "horizontal_kernel": (8, 1),   # Préserver la structure des cellules
            "vertical_kernel": (1, 4),     # Éviter de fusionner les lignes
        },
        "zone_merging": {
            **INTELLIGENT_DETECTION_CONFIG["zone_merging"],
            "max_merge_distance_ratio": 0.3,  # Fusion très restrictive pour tableaux
        }
    },
    
    "photo": {
        **INTELLIGENT_DETECTION_CONFIG,
        "candidate_detection": {
            **INTELLIGENT_DETECTION_CONFIG["candidate_detection"],
            "min_area_ratio": 0.001,       # Zones plus grandes pour éviter le bruit
            "fine_block_size": 15,         # Adaptation aux variations d'éclairage
            "standard_block_size": 19,     # Blocs plus larges
            "large_block_size": 25,        # Très larges pour photos
        },
        "geometric_filtering": {
            **INTELLIGENT_DETECTION_CONFIG["geometric_filtering"],
            "min_density": 0.15,           # Plus strict pour éviter le bruit
            "min_std_dev": 25,             # Plus de variation requise
        }
    }
}

# Patterns sémantiques étendus par langue
SEMANTIC_PATTERNS_EXTENDED = {
    "french": {
        ZoneType.HEADER: [
            r'facture|devis|bon de commande|commande|order',
            r'société|company|entreprise|sarl|sas|sa\b|eurl',
            r'n°\s*\d+|numero|numéro|ref\s*:',
            r'siret|siren|tva|rcs'
        ],
        ZoneType.DATE: [
            r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}',
            r'\d{1,2}\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)',
            r'date\s*:?\s*',
            r'le\s+\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}'
        ],
        ZoneType.PRICE: [
            r'\d+[,\.]\d{2}\s*€',
            r'€\s*\d+[,\.]\d{2}',
            r'total|montant|prix|price|amount|somme',
            r'tva|ht|ttc|tax|hors\s+taxe|toutes\s+taxes',
            r'\d+\s*%'
        ],
        ZoneType.ADDRESS: [
            r'\d+\s+(rue|avenue|boulevard|place|chemin|allée|impasse)',
            r'\d{5}\s+[a-zA-ZÀ-ÿ\s]+',
            r'adresse|address',
            r'france|paris|lyon|marseille|toulouse|nice|nantes|strasbourg|montpellier|bordeaux'
        ],
        ZoneType.REFERENCE: [
            r'ref\s*:?\s*\w+',
            r'référence|reference',
            r'n°|num|number|commande\s+n°',
            r'code\s+client|client\s+n°'
        ],
        ZoneType.SIGNATURE: [
            r'signature|signé|signed',
            r'cachet|stamp|tampon',
            r'lu\s+et\s+approuvé',
            r'bon\s+pour\s+accord'
        ],
        ZoneType.FOOTER: [
            r'page\s+\d+',
            r'siège\s+social',
            r'capital\s+social',
            r'mentions\s+légales'
        ]
    },
    
    "english": {
        ZoneType.HEADER: [
            r'invoice|quote|order|receipt|bill',
            r'company|corporation|inc\.|ltd\.|llc',
            r'invoice\s*#\s*\d+|order\s*#\s*\d+'
        ],
        ZoneType.DATE: [
            r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}',
            r'date\s*:?'
        ],
        ZoneType.PRICE: [
            r'\$\d+[,\.]\d{2}',
            r'\d+[,\.]\d{2}\s*\$',
            r'total|amount|price|cost|sum',
            r'tax|vat|net|gross'
        ],
        ZoneType.ADDRESS: [
            r'\d+\s+(street|avenue|boulevard|road|lane|drive)',
            r'\d{5}(-\d{4})?\s+[a-zA-Z\s]+',
            r'address|street\s+address'
        ]
    }
}

def get_intelligent_config(document_type: str = "default", language: str = "french") -> Dict[str, Any]:
    """
    Récupère la configuration intelligente pour un type de document
    
    Args:
        document_type: Type de document
        language: Langue du document
        
    Returns:
        Configuration complète pour la détection intelligente
    """
    
    # Configuration de base
    if document_type in DOCUMENT_SPECIFIC_CONFIGS:
        config = DOCUMENT_SPECIFIC_CONFIGS[document_type].copy()
    else:
        config = INTELLIGENT_DETECTION_CONFIG.copy()
    
    # Ajouter les patterns sémantiques selon la langue
    if language in SEMANTIC_PATTERNS_EXTENDED:
        config["semantic_patterns"] = SEMANTIC_PATTERNS_EXTENDED[language]
    else:
        config["semantic_patterns"] = SEMANTIC_PATTERNS_EXTENDED["french"]  # Fallback
    
    return config

def get_available_document_types() -> List[str]:
    """Retourne la liste des types de documents supportés"""
    return list(DOCUMENT_SPECIFIC_CONFIGS.keys()) + ["default"]

def get_available_languages() -> List[str]:
    """Retourne la liste des langues supportées"""
    return list(SEMANTIC_PATTERNS_EXTENDED.keys())

# Exemple d'utilisation
if __name__ == "__main__":
    print("🧠 Configuration de détection intelligente")
    print("=" * 50)
    
    print("\n📋 Types de documents disponibles:")
    for doc_type in get_available_document_types():
        print(f"   - {doc_type}")
    
    print("\n🌍 Langues supportées:")
    for lang in get_available_languages():
        print(f"   - {lang}")
    
    print("\n⚙️ Configuration pour facture française:")
    config = get_intelligent_config("facture", "french")
    print(f"   Seuil de confiance: {config['semantic_classification']['confidence_threshold']}")
    print(f"   Aire minimale: {config['candidate_detection']['min_area_ratio']}")
    print(f"   Patterns header: {len(config['semantic_patterns'][ZoneType.HEADER])}")
