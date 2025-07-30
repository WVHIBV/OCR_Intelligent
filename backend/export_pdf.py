"""
Module d'export PDF avec préservation de la mise en page
"""
import os
import fitz  # PyMuPDF
from PIL import Image
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import black, red, orange, yellow, gray


def create_pdf_with_layout(zone_results, reading_order, original_image_path, output_path):
    """
    Crée un PDF avec la mise en page préservée
    
    Args:
        zone_results (dict): Résultats des zones avec coordonnées
        reading_order (list): Ordre de lecture intelligent
        original_image_path (str): Chemin vers l'image originale
        output_path (str): Chemin de sortie du PDF
    """
    try:
        # Créer le document PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Style pour le titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # Style pour le texte normal
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_LEFT
        )
        
        # Ajouter le titre
        story.append(Paragraph("📄 DOCUMENT AVEC MISE EN PAGE PRÉSERVÉE", title_style))
        story.append(Spacer(1, 20))
        
        # Ajouter l'image originale en arrière-plan (optionnel)
        if os.path.exists(original_image_path):
            try:
                # Redimensionner l'image pour s'adapter à la page
                img = Image.open(original_image_path)
                img_width, img_height = img.size
                
                # Calculer les dimensions pour s'adapter à A4
                page_width, page_height = A4
                scale = min(page_width / img_width, page_height / img_height) * 0.8
                
                new_width = img_width * scale
                new_height = img_height * scale
                
                # Centrer l'image
                x_offset = (page_width - new_width) / 2
                y_offset = (page_height - new_height) / 2
                
                # Ajouter l'image (sera en arrière-plan)
                story.append(Paragraph(f'<img src="{original_image_path}" width="{new_width}" height="{new_height}"/>', normal_style))
                story.append(Spacer(1, 10))
            except Exception as e:
                print(f"[WARNING] Impossible d'ajouter l'image: {e}")
        
        # Ajouter le texte dans l'ordre de lecture avec positionnement
        for zone_id in reading_order:
            if zone_id in zone_results:
                zone_data = zone_results[zone_id]
                best_text = zone_data.get("best_text", "").strip()
                confidence = zone_data.get("confidence", 0)
                zone_type = zone_data.get("type", "unknown")
                
                if best_text:
                    # Style selon le type de zone
                    if zone_type == "header":
                        text_style = ParagraphStyle(
                            'Header',
                            parent=normal_style,
                            fontSize=14,
                            fontName='Helvetica-Bold',
                            spaceAfter=8
                        )
                    elif zone_type == "price":
                        text_style = ParagraphStyle(
                            'Price',
                            parent=normal_style,
                            fontSize=12,
                            fontName='Helvetica-Bold',
                            textColor=red,
                            spaceAfter=6
                        )
                    elif zone_type == "signature":
                        text_style = ParagraphStyle(
                            'Signature',
                            parent=normal_style,
                            fontSize=10,
                            fontName='Helvetica-Oblique',
                            spaceAfter=6
                        )
                    else:
                        text_style = normal_style
                    
                    # Ajouter le texte avec sa position relative
                    story.append(Paragraph(best_text, text_style))
        
        # Construire le PDF
        doc.build(story)
        print(f"[OK] PDF avec mise en page créé: {output_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la création du PDF: {e}")
        return False


def create_structured_pdf(zone_results, reading_order, output_path):
    """
    Crée un PDF structuré avec sections organisées
    
    Args:
        zone_results (dict): Résultats des zones
        reading_order (list): Ordre de lecture
        output_path (str): Chemin de sortie
    """
    try:
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        
        # Style pour les sections
        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=black
        )
        
        # Style pour le contenu
        content_style = ParagraphStyle(
            'Content',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20
        )
        
        # Grouper par type de zone
        zones_by_type = {}
        for zone_id in reading_order:
            if zone_id in zone_results:
                zone_data = zone_results[zone_id]
                zone_type = zone_data.get("type", "unknown")
                best_text = zone_data.get("best_text", "").strip()
                
                if best_text:
                    if zone_type not in zones_by_type:
                        zones_by_type[zone_type] = []
                    zones_by_type[zone_type].append(best_text)
        
        # Titre principal
        story.append(Paragraph("📄 DOCUMENT STRUCTURÉ", section_style))
        story.append(Spacer(1, 20))
        
        # Ajouter chaque section par type
        type_names = {
            "header": "🏷️ EN-TÊTE",
            "price": "💰 PRIX ET MONTANTS",
            "reference": "📄 RÉFÉRENCES",
            "signature": "✍️ SIGNATURE",
            "address": "🏠 ADRESSES",
            "paragraph": "📝 PARAGRAPHES",
            "unknown": "📋 AUTRES ÉLÉMENTS"
        }
        
        for zone_type, texts in zones_by_type.items():
            type_name = type_names.get(zone_type, f"📋 {zone_type.upper()}")
            story.append(Paragraph(type_name, section_style))
            
            for text in texts:
                story.append(Paragraph(text, content_style))
            
            story.append(Spacer(1, 10))
        
        # Construire le PDF
        doc.build(story)
        print(f"[OK] PDF structuré créé: {output_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la création du PDF structuré: {e}")
        return False


def create_html_with_layout(zone_results, reading_order, original_image_path, output_path):
    """
    Crée un fichier HTML avec mise en page préservée
    
    Args:
        zone_results (dict): Résultats des zones
        reading_order (list): Ordre de lecture
        original_image_path (str): Image originale
        output_path (str): Chemin de sortie HTML
    """
    try:
        html_content = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document OCR avec mise en page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        .header {
            text-align: center;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }
        .original-image {
            text-align: center;
            margin: 20px 0;
        }
        .original-image img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .content {
            line-height: 1.6;
            color: #333;
        }
        .zone {
            margin: 10px 0;
            padding: 8px;
            border-left: 3px solid #3498db;
            background-color: #f8f9fa;
        }
        .zone-header {
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .zone-text {
            margin: 0;
        }
        .confidence {
            font-size: 0.8em;
            color: #7f8c8d;
            font-style: italic;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 DOCUMENT OCR AVEC MISE EN PAGE</h1>
            <p>Texte extrait et organisé selon l'ordre de lecture intelligent</p>
        </div>
"""
        
        # Ajouter l'image originale si disponible
        if os.path.exists(original_image_path):
            html_content += f"""
        <div class="original-image">
            <h3>🖼️ Image originale</h3>
            <img src="{original_image_path}" alt="Document original">
        </div>
"""
        
        html_content += """
        <div class="content">
"""
        
        # Ajouter le texte dans l'ordre de lecture
        for zone_id in reading_order:
            if zone_id in zone_results:
                zone_data = zone_results[zone_id]
                best_text = zone_data.get("best_text", "").strip()
                confidence = zone_data.get("confidence", 0)
                zone_type = zone_data.get("type", "unknown")
                
                if best_text:
                    html_content += f"""
            <div class="zone">
                <div class="zone-header">Zone {zone_id} - {zone_type.upper()}</div>
                <p class="zone-text">{best_text}</p>
                <div class="confidence">Confiance: {confidence:.1f}%</div>
            </div>
"""
        
        html_content += """
        </div>
        <div class="footer">
            <p>Généré automatiquement par l'outil OCR Intelligent</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Sauvegarder le fichier HTML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[OK] HTML avec mise en page créé: {output_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la création du HTML: {e}")
        return False 