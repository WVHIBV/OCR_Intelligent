# Guide d'Installation et d'Utilisation - Détection de Mise en Page

## Vue d'ensemble

Cette mise à jour ajoute la détection automatique de mise en page à l'outil OCR existant. Le système utilise **LayoutParser** avec le modèle **PubLayNet** pour détecter automatiquement :

- **Zones de texte** : Paragraphes et blocs de texte
- **Titres/En-têtes** : Titres et sous-titres
- **Tableaux** : Structures tabulaires
- **Listes** : Listes à puces ou numérotées
- **Figures** : Images et diagrammes avec légendes

## Installation des Dépendances

### 1. Prérequis

Assurez-vous d'avoir Python 3.8+ installé et un environnement virtuel activé.

### 2. Installation des nouvelles dépendances

```bash
# Installation de LayoutParser avec support CPU
pip install layoutparser[paddledetection]>=0.3.4

# Installation de Detectron2 (pour les modèles de détection)
pip install detectron2>=0.6

# Ou installer toutes les dépendances d'un coup
pip install -r requirements.txt
```

### 3. Installation alternative (si problèmes avec detectron2)

Si l'installation de detectron2 échoue, vous pouvez utiliser une version CPU-only :

```bash
# Pour Windows
pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.10/index.html

# Ou utiliser conda
conda install detectron2::detectron2 -c conda-forge
```

### 4. Vérification de l'installation

Lancez ce test pour vérifier que tout fonctionne :

```python
python -c "
import layoutparser as lp
print('LayoutParser installé avec succès')
try:
    model = lp.Detectron2LayoutModel('lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config')
    print('Modèle PubLayNet accessible')
except:
    print('Modèle PubLayNet non accessible (mode fallback disponible)')
"
```

## Utilisation

### 1. Interface Streamlit

1. Lancez l'application : `python main.py` ou utilisez `Lancer_OCR_Intelligent.bat`
2. Dans l'interface, cochez la case **"[BETA] Activer la détection automatique de mise en page"**
3. Téléversez votre image ou PDF
4. L'analyse se fera automatiquement avec détection de zones

### 2. Utilisation programmatique

```python
from backend.structured_ocr import process_image_structured

# Traitement d'une image avec détection de mise en page
result = process_image_structured(
    image_path="chemin/vers/image.jpg",
    layout_confidence=0.5,  # Seuil de confiance (0.0 à 1.0)
    enable_debug=True       # Génère une image de debug
)

# Accès aux résultats
print(f"Zones détectées: {result['total_zones']}")
for zone in result['zones']:
    print(f"Zone {zone['id']}: {zone['type']} - {zone['content']['text'][:50]}...")
```

### 3. Résultats générés

Le système génère plusieurs fichiers :

- **Document Word structuré** : `output/structured_result_doctr.docx`
- **Résultats JSON détaillés** : `output/detailed_structured_results.json`
- **Image de debug** (si activé) : `output/debug/image_layout_debug.jpg`

## Structure des Résultats JSON

```json
{
  "image_path": "chemin/vers/image.jpg",
  "total_zones": 5,
  "zones": [
    {
      "id": 0,
      "type": "title",
      "bbox": {"x1": 100, "y1": 50, "x2": 500, "y2": 100},
      "layout_confidence": 0.95,
      "content": {
        "text": "Titre du document",
        "lines": ["Titre du document"],
        "confidences": [98.5],
        "avg_confidence": 98.5
      }
    },
    {
      "id": 1,
      "type": "text",
      "bbox": {"x1": 100, "y1": 120, "x2": 500, "y2": 300},
      "layout_confidence": 0.87,
      "content": {
        "text": "Contenu du paragraphe...",
        "lines": ["Ligne 1", "Ligne 2"],
        "confidences": [95.2, 93.8],
        "avg_confidence": 94.5
      }
    }
  ],
  "full_text": "Texte complet reconstruit dans l'ordre logique",
  "stats": {
    "total_zones": 5,
    "text_zones": 3,
    "title_zones": 1,
    "table_zones": 1,
    "figure_zones": 0
  }
}
```

## Mode Fallback

Si LayoutParser n'est pas disponible ou échoue, le système bascule automatiquement en **mode fallback** :

- Une zone unique couvrant toute l'image est créée
- L'OCR classique est appliqué normalement
- Aucune erreur n'est générée, l'utilisateur est informé via les logs

## Optimisation des Performances

### 1. Configuration CPU-only

Le système est configuré pour fonctionner sans GPU :

```python
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Force CPU
```

### 2. Ajustement du seuil de confiance

- **0.3-0.4** : Détection plus sensible (plus de zones, possibles faux positifs)
- **0.5** : Équilibre recommandé (par défaut)
- **0.6-0.8** : Détection plus stricte (moins de zones, plus précises)

### 3. Préprocessing adaptatif

Le système applique un préprocessing différent selon le type de zone :

- **Texte/Titre** : Optimisation pour la lisibilité
- **Tableau** : Préservation de la structure
- **Figure** : Extraction des légendes

## Dépannage

### Problème : "LayoutParser non disponible"

**Solution** : Vérifiez l'installation :
```bash
pip install layoutparser[paddledetection] detectron2
```

### Problème : "Erreur lors de l'initialisation du modèle"

**Solutions** :
1. Vérifiez votre connexion internet (première utilisation)
2. Utilisez le mode fallback (automatique)
3. Réinstallez les dépendances

### Problème : "Aucune zone détectée"

**Solutions** :
1. Réduisez le seuil de confiance (0.3 au lieu de 0.5)
2. Vérifiez la qualité de l'image
3. Le mode fallback s'active automatiquement

### Problème : Performance lente

**Solutions** :
1. Réduisez la résolution des images
2. Augmentez le seuil de confiance
3. Désactivez le mode debug

## Compatibilité

- **Python** : 3.8+
- **Système** : Windows, Linux, macOS
- **GPU** : Optionnel (CPU-only supporté)
- **Mémoire** : 4GB RAM minimum, 8GB recommandé

## Limitations Connues

1. **Première utilisation** : Téléchargement du modèle PubLayNet (~200MB)
2. **Types de documents** : Optimisé pour documents académiques/techniques
3. **Langues** : Détection de mise en page indépendante de la langue, OCR en français/anglais
4. **Résolution** : Meilleures performances avec images haute résolution (300 DPI+)

## Support et Logs

Les logs détaillés sont disponibles dans :
- **Console** : Messages en temps réel
- **Fichier** : `logs/main.log`

Pour activer les logs de debug :
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
