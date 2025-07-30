# 🎨 Guide d'utilisation - Mise en page préservée

## 📋 Fonctionnalités disponibles

Votre OCR Tool propose maintenant **4 types d'export** pour préserver la mise en page :

### 1. 📄 **Export Word classique**
- **Format** : Document Word (.docx)
- **Contenu** : Texte extrait avec coloration selon la confiance
- **Avantages** : Éditable, compatible avec tous les logiciels
- **Utilisation** : Pour la correction et l'édition manuelle

### 2. 📄 **PDF Structuré**
- **Format** : PDF (.pdf)
- **Contenu** : Document organisé par sections (En-tête, Prix, Adresses, etc.)
- **Avantages** : Structure claire, facile à lire
- **Utilisation** : Pour la lecture et l'archivage

### 3. 🌐 **HTML avec mise en page**
- **Format** : Page web (.html)
- **Contenu** : Document interactif avec image originale
- **Avantages** : Visuel, peut être ouvert dans n'importe quel navigateur
- **Utilisation** : Pour le partage et la consultation

### 4. 📄 **PDF avec mise en page**
- **Format** : PDF (.pdf)
- **Contenu** : Document avec image originale et texte superposé
- **Avantages** : Préservation maximale de la mise en page
- **Utilisation** : Pour l'archivage fidèle

## 🚀 Installation

### Étape 1 : Installer les dépendances
```bash
python install_dependencies.py
```

### Étape 2 : Lancer l'application
```bash
python -m streamlit run frontend/app.py
```

## 📖 Utilisation

### 1. **Mode Intelligent (Recommandé)**
1. Sélectionnez **"Facture"** ou **"Autre"** dans le type de document
2. Uploadez votre image
3. Laissez l'IA détecter les zones intelligemment
4. Choisissez votre format d'export préféré

### 2. **Export avec mise en page**
Après le traitement, vous verrez une nouvelle section **"🎨 Export avec mise en page préservée"** avec 3 boutons :

- **📄 Générer PDF structuré** : Document organisé par sections
- **🌐 Générer HTML** : Page web interactive
- **📄 Générer PDF avec layout** : Document avec image originale

### 3. **Téléchargement**
Cliquez sur le bouton correspondant à votre format préféré, puis sur **"Télécharger"**.

## 🎯 Recommandations par usage

### 📊 **Pour l'analyse de documents**
- **PDF Structuré** : Meilleur pour l'analyse et la lecture
- **HTML** : Pour la consultation rapide

### 💼 **Pour l'archivage**
- **PDF avec mise en page** : Fidélité maximale
- **PDF Structuré** : Organisation claire

### ✏️ **Pour l'édition**
- **Word classique** : Édition facile
- **HTML** : Copier-coller simple

### 📤 **Pour le partage**
- **HTML** : Ouverture universelle
- **PDF Structuré** : Compatibilité maximale

## 🔧 Fonctionnalités avancées

### **Ordre de lecture intelligent**
- L'IA détermine automatiquement l'ordre logique de lecture
- Le texte est réorganisé selon cet ordre
- Respect de la hiérarchie visuelle du document

### **Classification automatique**
- **En-tête** : Titres et informations principales
- **Prix** : Montants et calculs
- **Références** : Numéros et codes
- **Adresses** : Coordonnées postales
- **Signature** : Espaces de signature
- **Paragraphes** : Texte de contenu

### **Confiance et qualité**
- Chaque zone a un score de confiance
- Coloration automatique selon la qualité
- Sélection du meilleur moteur OCR par zone

## 🛠️ Dépannage

### **Erreur d'installation**
```bash
# Réinstaller les dépendances
pip install --upgrade pip
python install_dependencies.py
```

### **Erreur de génération PDF**
- Vérifiez que ReportLab est installé : `pip install reportlab`
- Assurez-vous d'avoir les permissions d'écriture dans le dossier `output`

### **Erreur de génération HTML**
- Vérifiez que PyMuPDF est installé : `pip install PyMuPDF`
- L'image originale doit être accessible

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez que toutes les dépendances sont installées
2. Consultez les logs dans la console
3. Redémarrez l'application

---

**🎉 Profitez de votre OCR Tool avec mise en page préservée !** 