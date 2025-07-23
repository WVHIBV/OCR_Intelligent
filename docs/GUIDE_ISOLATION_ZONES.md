# 🎯 Guide d'utilisation - Isolation des zones de texte

## 📋 Vue d'ensemble

La fonctionnalité d'isolation des zones de texte permet de détecter automatiquement et d'extraire les différentes zones contenant du texte dans une image. Cette fonctionnalité est particulièrement utile pour :

- **Documents complexes** : Factures, formulaires, rapports avec plusieurs sections
- **Mise en page structurée** : Journaux, magazines, brochures
- **Analyse ciblée** : Traitement OCR spécialisé par zone
- **Extraction sélective** : Récupération de sections spécifiques

## 🚀 Comment utiliser la fonctionnalité

### 1. Accès à la fonctionnalité

1. Lancez l'application OCR Intelligent
2. Téléversez votre image ou PDF
3. Localisez la section **"🔍 Isolation des zones de texte"**

### 2. Détection des zones

1. Cliquez sur le bouton **"🎯 Détecter les zones de texte"**
2. L'application analyse automatiquement l'image
3. Les zones détectées sont affichées avec des annotations colorées

### 3. Résultats de la détection

#### Image annotée
- Chaque zone est entourée d'un rectangle coloré
- Les zones sont numérotées pour faciliter l'identification
- L'image annotée peut être téléchargée

#### Informations détaillées
Pour chaque zone détectée, vous obtenez :
- **Coordonnées** : Position (x, y) dans l'image
- **Dimensions** : Largeur et hauteur en pixels
- **Surface** : Aire totale de la zone
- **Aperçu** : Miniature de la zone extraite

### 4. Téléchargement des zones

#### Téléchargement groupé
- **Fichier ZIP** : Toutes les zones + image annotée
- Contient chaque zone comme fichier PNG séparé
- Nomenclature : `nom_image_zone_01.png`, `nom_image_zone_02.png`, etc.

#### Téléchargement individuel
- Bouton de téléchargement pour chaque zone
- Format PNG haute qualité
- Marges automatiques pour une meilleure lisibilité

## 🔍 OCR sur zones isolées

### Analyse ciblée

1. Après la détection des zones, cliquez sur **"🔍 Analyser les zones avec OCR"**
2. Chaque zone est traitée individuellement par les 3 moteurs OCR
3. Les résultats sont affichés zone par zone

### Avantages de l'OCR par zone

- **Précision améliorée** : Chaque zone est optimisée individuellement
- **Moins de bruit** : Élimination des éléments parasites
- **Traitement spécialisé** : Paramètres adaptés à chaque type de contenu
- **Édition facilitée** : Modification du texte zone par zone

### Édition et sauvegarde

- **Texte éditable** : Chaque résultat OCR peut être modifié
- **Sauvegarde individuelle** : Enregistrement par zone et par moteur
- **Format texte** : Fichiers .txt pour une utilisation ultérieure

## ⚙️ Paramètres de détection

### Critères de filtrage automatique

La détection utilise plusieurs critères pour identifier les zones de texte pertinentes :

#### Taille minimale
- **Surface** : Au moins 0.1% de l'image totale
- **Dimensions** : Minimum 50px de largeur et 20px de hauteur

#### Taille maximale
- **Surface** : Maximum 80% de l'image totale
- Évite la sélection de l'image entière

#### Ratio d'aspect
- **Largeur/Hauteur** : Entre 0.1 et 20
- Élimine les zones trop étroites ou trop larges

### Préprocessing spécialisé

#### Amélioration du contraste
- **CLAHE** : Égalisation adaptative de l'histogramme
- **Paramètres** : clipLimit=3.0, tileGridSize=(8,8)

#### Débruitage
- **Filtre bilatéral** : Préservation des contours
- **Paramètres** : d=9, sigmaColor=75, sigmaSpace=75

#### Morphologie
- **Connexion horizontale** : Regroupement des mots (kernel 25x1)
- **Connexion verticale** : Regroupement des lignes (kernel 1x15)
- **Dilatation finale** : Création de zones cohérentes (kernel 3x3)

## 📁 Structure des fichiers de sortie

```
output/
└── text_zones/
    ├── nom_image_zone_01.png          # Zone 1 extraite
    ├── nom_image_zone_02.png          # Zone 2 extraite
    ├── nom_image_zones_annotees.png   # Image avec annotations
    ├── zones_texte.zip                # Archive complète
    └── zone_texts/                    # Textes OCR par zone
        ├── zone_1_tesseract.txt
        ├── zone_1_easyocr.txt
        ├── zone_1_doctr.txt
        └── ...
```

## 🎯 Cas d'usage recommandés

### Documents administratifs
- **Factures** : Séparation en-tête, corps, totaux
- **Formulaires** : Extraction champ par champ
- **Contrats** : Isolation des clauses importantes

### Publications
- **Journaux** : Séparation articles, titres, légendes
- **Magazines** : Extraction texte principal vs encadrés
- **Brochures** : Distinction contenu principal/secondaire

### Documents techniques
- **Rapports** : Séparation chapitres, tableaux, notes
- **Manuels** : Extraction procédures, avertissements
- **Schémas** : Isolation des annotations textuelles

## 🔧 Dépannage

### Aucune zone détectée
- Vérifiez la qualité de l'image (résolution, contraste)
- Assurez-vous que le texte est suffisamment contrasté
- Essayez avec une image de meilleure qualité

### Trop de zones détectées
- L'algorithme peut détecter du bruit comme des zones de texte
- Utilisez les filtres de taille pour éliminer les petites zones
- Préprocessez l'image pour réduire le bruit

### Zones mal délimitées
- Augmentez la résolution de l'image source
- Vérifiez l'orientation du document (rotation nécessaire ?)
- Assurez-vous que le texte n'est pas trop incliné

## 📞 Support

Pour toute question ou problème avec la fonctionnalité d'isolation des zones :

1. Consultez les logs dans le dossier `logs/`
2. Vérifiez les fichiers de sortie dans `output/text_zones/`
3. Testez avec l'image d'exemple fournie
4. Contactez le support technique si nécessaire

---

*Cette fonctionnalité utilise des algorithmes avancés de vision par ordinateur pour une détection automatique optimale des zones de texte.*
