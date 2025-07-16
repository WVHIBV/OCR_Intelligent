# OCR Intelligent - Clean Project Structure

## 📁 **Production-Ready File Organization**

This document describes the cleaned and optimized project structure for OCR Intelligent.

### **🎯 Core Application Files**

```
OCR_Intelligent/
├── 🚀 main.py                           # Main entry point with port management
├── ⚙️ config.py                         # Centralized configuration
├── 📋 requirements.txt                  # Python dependencies
├── 🔧 port_manager.py                   # Port conflict diagnostic utility
├── 🎨 ocr_icon.ico                      # Application icon
└── 📖 README.md                         # Complete documentation
```

### **🎮 User Interface**

```
frontend/
├── app.py                               # Main Streamlit application
├── custom_style.html                   # Custom CSS styling
└── safran_logo.png                     # Application logo
```

### **🔧 OCR Processing Engine**

```
backend/
├── main.py                              # OCR orchestrator
├── ocr_tesseract.py                    # Tesseract OCR engine
├── ocr_easyocr.py                      # EasyOCR engine
├── ocr_doctr.py                        # DocTR engine (simulation mode)
├── preprocessing.py                    # Image enhancement
├── corrector.py                        # Text correction algorithms
└── export.py                           # Export functionality (Word, Excel)
```

### **🤖 Pre-trained Models**

```
models/
├── tesseract/                          # Tesseract language models
├── easyocr/                            # EasyOCR neural networks
├── doctr/                              # DocTR model files
└── paddleocr/                          # PaddleOCR models (optional)
```

### **📷 Sample Images**

```
images/
├── exemple1.png                        # Sample document 1
├── exemple2.jpg                        # Sample document 2
├── facture1.png                        # Invoice sample
├── FACTURE-ARTFORDPLUS_N1-1.jpg       # Complex invoice sample
└── modele-facture-fr-bande-bleu-750px.png  # French invoice template
```

### **🚀 Launchers and Installers**

```
├── 🎯 Lancer_OCR_Intelligent.bat       # Main application launcher (corrected)
├── 🔨 build_installer.bat              # Windows installer builder (corrected)
├── 🔨 Build_Simple.bat                 # Simplified installer builder
├── ✅ check_installer.bat              # Installer prerequisites checker

└── 📦 OCR_Intelligent_Setup.iss        # Inno Setup script (corrected)
```

### **📁 Working Directories**

```
├── output/                             # Generated OCR results (auto-created)
├── logs/                               # Application logs (auto-created)
└── corrected/                          # Corrected text files (auto-created)
```
