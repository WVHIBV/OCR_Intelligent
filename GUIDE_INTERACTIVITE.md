# 🎯 Guide d'utilisation du Surlignage Interactif

## Vue d'ensemble

La nouvelle fonctionnalité de **surlignage interactif** transforme l'analyse des documents OCR en une expérience visuelle et intuitive. Plus besoin de deviner quelles zones correspondent à quel texte !

## 🚀 Fonctionnalités

### **Surlignage au survol**
- **Survolez une zone** dans l'image → Elle se surligne en **rouge**
- **Survolez le texte** en bas → La zone correspondante se surligne
- **Synchronisation bidirectionnelle** automatique

### **Sélection permanente**
- **Cliquez sur une zone** → Surlignage **bleu permanent**
- **Cliquez sur le texte** → Même effet
- **Re-cliquez** pour désélectionner

### **Tooltips informatifs**
Au survol d'une zone, découvrez :
- 🏷️ **Type de zone** (header, price, date, etc.)
- 📝 **Texte détecté** par l'OCR
- 📊 **Niveau de confiance** (%)
- 🔧 **Méthode utilisée** (Tesseract, EasyOCR, DocTR)

## 🎨 Code couleur

| Couleur | Signification |
|---------|---------------|
| 🔴 **Rouge** | Zone survolée temporairement |
| 🔵 **Bleu** | Zone sélectionnée en permanence |
| ⚫ **Gris** | Zone inactive |

## 🖱️ Interactions disponibles

### **Sur l'image :**
- **Hover** : Surlignage temporaire + tooltip
- **Clic** : Sélection permanente
- **Redimensionnement** : Adaptation automatique des zones

### **Sur le texte :**
- **Hover** : Surlignage de la zone correspondante
- **Clic** : Sélection permanente bidirectionnelle

## 📍 Types de zones détectées

| Emoji | Type | Description |
|-------|------|-------------|
| 🏷️ | **Header** | Titres et en-têtes |
| 💰 | **Price** | Prix et montants |
| 📅 | **Date** | Dates et timestamps |
| 🏠 | **Address** | Adresses et localisations |
| 📄 | **Reference** | Numéros de référence |
| 📝 | **Paragraph** | Paragraphes de texte |
| ✍️ | **Signature** | Signatures et paraphes |
| 📋 | **Footer** | Pieds de page |
| ❓ | **Unknown** | Type non identifié |

## 🔧 Comment activer

1. **Uploadez votre document** (image ou PDF)
2. **Sélectionnez un type** autre que "Standard"
3. **Activez la détection intelligente** (recommandé)
4. **Choisissez "🎯 Interactif"** dans le mode d'affichage
5. **Explorez** en survolant les zones !

## 💡 Conseils d'utilisation

### **Pour l'analyse de documents :**
- Utilisez le **survol** pour explorer rapidement
- **Sélectionnez les zones importantes** pour comparaison
- Vérifiez les **niveaux de confiance** dans les tooltips

### **Pour la validation OCR :**
- **Comparez** le texte affiché avec l'image
- **Identifiez** les zones de faible confiance
- **Vérifiez** la cohérence type/contenu

### **Pour la correction :**
- **Repérez** les erreurs de classification
- **Notez** les zones mal détectées
- **Corrigez** le document Word exporté

## 🆚 Modes d'affichage

### **🎯 Mode Interactif**
- Interface complète avec surlignage
- Tooltips détaillés
- Synchronisation image ↔ texte
- Idéal pour l'exploration et la validation

### **📊 Mode Compact**
- Affichage traditionnel statique
- Liste des zones avec métadonnées
- Plus compact, moins interactif
- Idéal pour un aperçu rapide

## 🔮 Évolutions futures

- **Édition en ligne** des zones
- **Annotation manuelle** des types
- **Comparaison multi-moteurs** visuelle
- **Export des annotations** au format JSON

---

**✨ Cette fonctionnalité rend l'OCR Intelligent encore plus intuitif et puissant pour analyser vos documents !**
