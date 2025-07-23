"""
Configuration pour la détection des zones de texte
Paramètres personnalisables pour optimiser la détection selon le type de document
"""

# Configuration par défaut pour la détection de zones (équilibrée anti-superposition)
DEFAULT_ZONE_CONFIG = {
    # Filtres de taille (équilibrés)
    "min_area_ratio": 0.001,    # Minimum 0.1% de l'image totale (équilibré)
    "max_area_ratio": 0.8,      # Maximum 80% de l'image totale
    "min_width": 40,            # Largeur minimale en pixels (augmentée)
    "min_height": 15,           # Hauteur minimale en pixels (augmentée)

    # Filtres de forme (plus stricts)
    "min_aspect_ratio": 0.1,    # Ratio largeur/hauteur minimum (plus strict)
    "max_aspect_ratio": 25,     # Ratio largeur/hauteur maximum (plus strict)

    # Préprocessing CLAHE (équilibré)
    "clahe_clip_limit": 3.0,    # Limite de contraste (équilibrée)
    "clahe_tile_size": (8, 8),  # Taille des tuiles

    # Débruitage (équilibré)
    "bilateral_d": 7,           # Diamètre du filtre
    "bilateral_sigma_color": 75, # Sigma couleur
    "bilateral_sigma_space": 75, # Sigma spatial

    # Binarisation adaptative (équilibrée)
    "adaptive_block_size": 15,  # Taille du bloc (équilibrée)
    "adaptive_c": 10,           # Constante soustraite (équilibrée)

    # Morphologie - connexion horizontale (mots) (équilibrée)
    "morph_horizontal_kernel": (18, 1),  # Équilibrée pour éviter la sur-fusion

    # Morphologie - connexion verticale (lignes) (équilibrée)
    "morph_vertical_kernel": (1, 10),    # Équilibrée pour éviter la sur-fusion

    # Dilatation finale (réduite)
    "final_kernel": (2, 2),     # Petite pour éviter la sur-fusion
    "final_iterations": 1,      # Minimale pour préserver les détails

    # Marges pour l'extraction
    "extraction_margin": 10,    # Marge en pixels autour de chaque zone
}

# Configurations spécialisées par type de document (améliorées)
DOCUMENT_CONFIGS = {
    "facture": {
        **DEFAULT_ZONE_CONFIG,
        "min_area_ratio": 0.0008,   # Sensible mais pas excessif
        "min_width": 35,            # Zones significatives
        "min_height": 12,           # Hauteur raisonnable
        "morph_horizontal_kernel": (16, 1),  # Équilibré
        "clahe_clip_limit": 3.2,    # Contraste légèrement augmenté
        "adaptive_block_size": 13,  # Binarisation équilibrée
    },

    "formulaire": {
        **DEFAULT_ZONE_CONFIG,
        "min_area_ratio": 0.0006,   # Sensible pour les champs
        "min_width": 30,            # Zones de champs raisonnables
        "min_height": 12,           # Hauteur de champs standard
        "morph_horizontal_kernel": (14, 1),  # Préserver les champs séparés
        "morph_vertical_kernel": (1, 8),     # Éviter de fusionner les lignes
        "adaptive_block_size": 11,  # Binarisation équilibrée
        "final_iterations": 1,      # Dilatation minimale
    },

    "journal": {
        **DEFAULT_ZONE_CONFIG,
        "min_aspect_ratio": 0.3,    # Éviter les zones trop étroites mais pas trop restrictif
        "max_aspect_ratio": 15,     # Permettre les colonnes longues
        "morph_horizontal_kernel": (18, 1),  # Connecter les mots dans les colonnes
        "morph_vertical_kernel": (1, 18),    # Mieux connecter les paragraphes
        "clahe_clip_limit": 4.0,    # Contraste plus fort pour le texte imprimé
        "min_height": 15,           # Accepter les lignes de journal
    },

    "manuscrit": {
        **DEFAULT_ZONE_CONFIG,
        "min_area_ratio": 0.0004,   # Sensible pour l'écriture manuscrite
        "bilateral_d": 11,          # Débruitage modéré pour préserver les détails
        "clahe_clip_limit": 4.2,    # Contraste élevé mais pas excessif
        "adaptive_block_size": 17,  # Bloc adapté à l'écriture irrégulière
        "morph_horizontal_kernel": (25, 1),  # Connecter les mots manuscrits
        "morph_vertical_kernel": (1, 10),    # Connecter les lignes manuscrites
        "min_width": 25,            # Accepter l'écriture fine
        "min_height": 12,           # Accepter les lignes manuscrites
    },

    "tableau": {
        **DEFAULT_ZONE_CONFIG,
        "min_area_ratio": 0.0003,   # Sensible pour les cellules
        "min_aspect_ratio": 0.1,    # Accepter des cellules rectangulaires
        "max_aspect_ratio": 20,     # Permettre des cellules allongées
        "morph_horizontal_kernel": (8, 1),   # Préserver la structure des cellules
        "morph_vertical_kernel": (1, 6),     # Éviter de fusionner les lignes
        "final_iterations": 1,      # Dilatation minimale
        "min_width": 20,            # Accepter des cellules étroites
        "min_height": 10,           # Accepter des cellules basses
        "adaptive_block_size": 11,  # Binarisation fine pour les bordures
    },

    "photo": {
        **DEFAULT_ZONE_CONFIG,
        "min_area_ratio": 0.001,    # Moins restrictif que l'original
        "bilateral_d": 13,          # Débruitage fort mais pas excessif
        "bilateral_sigma_color": 90,
        "bilateral_sigma_space": 90,
        "clahe_clip_limit": 4.5,    # Contraste élevé pour les photos
        "adaptive_c": 12,           # Binarisation adaptée aux photos
        "adaptive_block_size": 15,  # Bloc adapté aux variations d'éclairage
        "morph_horizontal_kernel": (22, 1),  # Connecter malgré le bruit
        "morph_vertical_kernel": (1, 14),    # Connecter les lignes
        "min_width": 35,            # Zones plus grandes pour éviter le bruit
        "min_height": 15,           # Hauteur minimale pour la robustesse
    }
}

def get_config(document_type="default"):
    """
    Récupère la configuration pour un type de document donné
    
    Args:
        document_type (str): Type de document ('facture', 'formulaire', etc.)
        
    Returns:
        dict: Configuration optimisée pour le type de document
    """
    if document_type in DOCUMENT_CONFIGS:
        return DOCUMENT_CONFIGS[document_type].copy()
    else:
        return DEFAULT_ZONE_CONFIG.copy()

def list_available_configs():
    """
    Liste les configurations disponibles
    
    Returns:
        list: Liste des types de documents supportés
    """
    return list(DOCUMENT_CONFIGS.keys())

def create_custom_config(**kwargs):
    """
    Crée une configuration personnalisée en modifiant les paramètres par défaut
    
    Args:
        **kwargs: Paramètres à modifier
        
    Returns:
        dict: Configuration personnalisée
    """
    config = DEFAULT_ZONE_CONFIG.copy()
    config.update(kwargs)
    return config

# Exemples d'utilisation
if __name__ == "__main__":
    print("🔧 Configuration de détection des zones de texte")
    print("=" * 50)
    
    print("\n📋 Configurations disponibles:")
    for doc_type in list_available_configs():
        print(f"   - {doc_type}")
    
    print("\n⚙️ Configuration par défaut:")
    default_config = get_config()
    for key, value in default_config.items():
        print(f"   {key}: {value}")
    
    print("\n📄 Configuration pour factures:")
    facture_config = get_config("facture")
    # Afficher seulement les différences
    for key, value in facture_config.items():
        if value != default_config.get(key):
            print(f"   {key}: {value} (modifié)")
    
    print("\n🎯 Configuration personnalisée:")
    custom_config = create_custom_config(
        min_area_ratio=0.002,
        clahe_clip_limit=4.0,
        extraction_margin=15
    )
    print(f"   min_area_ratio: {custom_config['min_area_ratio']}")
    print(f"   clahe_clip_limit: {custom_config['clahe_clip_limit']}")
    print(f"   extraction_margin: {custom_config['extraction_margin']}")
