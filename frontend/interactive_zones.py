"""
Module pour l'affichage interactif des zones OCR
Permet le surlignage dynamique en passant la souris
"""

import streamlit as st
import json
import base64
from PIL import Image
import io

def create_interactive_zone_display(annotated_image_path, zones_data, ocr_results=None):
    """
    Crée un affichage interactif des zones avec surlignage au survol
    
    Args:
        annotated_image_path: Chemin vers l'image annotée
        zones_data: Données des zones détectées
        ocr_results: Résultats OCR correspondants (optionnel)
    """
    
    # Convertir l'image en base64 pour l'embedding
    with open(annotated_image_path, "rb") as f:
        img_data = f.read()
        img_base64 = base64.b64encode(img_data).decode()
    
    # Préparer les données des zones pour JavaScript
    zones_js = []
    for i, zone in enumerate(zones_data):
        coords = zone.get("coordinates", {})
        zone_info = {
            "id": f"zone_{zone.get('zone_id', i)}",
            "x": coords.get("x", 0),
            "y": coords.get("y", 0), 
            "width": coords.get("width", 100),
            "height": coords.get("height", 100),
            "type": zone.get("type", "unknown"),
            "content": zone.get("content", ""),
            "confidence": zone.get("confidence", 0)
        }
        zones_js.append(zone_info)
    
    # Préparer les résultats OCR si disponibles
    ocr_js = {}
    if ocr_results:
        for zone_id, result in ocr_results.items():
            if "zone_info" in result:
                zone_info = result["zone_info"]
                ocr_js[f"zone_{zone_id}"] = {
                    "text": result.get("best_text", ""),
                    "confidence": result.get("best_confidence", 0),
                    "method": result.get("best_method", "")
                }
    
    # Générer les HTML des overlays et zones de texte
    overlays_html = generate_zone_overlays(zones_js)
    text_zones_html = generate_text_zones(zones_js, ocr_js)
    
    # Code HTML/CSS/JavaScript pour l'interactivité
    interactive_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .interactive-container {{
                position: relative;
                display: inline-block;
                max-width: 100%;
            }}
            
            .zone-image {{
                max-width: 100%;
                height: auto;
                display: block;
            }}
            
            .zone-overlay {{
                position: absolute;
                border: 3px solid transparent;
                cursor: pointer;
                transition: all 0.3s ease;
                z-index: 10;
            }}
            
            .zone-overlay:hover {{
                border-color: #ff6b6b;
                background-color: rgba(255, 107, 107, 0.2);
                box-shadow: 0 0 15px rgba(255, 107, 107, 0.5);
                transform: scale(1.02);
            }}
            
            .zone-overlay.active {{
                border-color: #4ecdc4;
                background-color: rgba(78, 205, 196, 0.3);
                box-shadow: 0 0 20px rgba(78, 205, 196, 0.7);
            }}
            
            .zone-tooltip {{
                position: absolute;
                background: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                white-space: nowrap;
                z-index: 1000;
                display: none;
                max-width: 300px;
                word-wrap: break-word;
                white-space: normal;
            }}
            
            .text-results {{
                margin-top: 20px;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: #f9f9f9;
            }}
            
            .text-zone {{
                margin: 10px 0;
                padding: 10px;
                border-left: 4px solid #ddd;
                background: white;
                cursor: pointer;
                transition: all 0.3s ease;
                border-radius: 4px;
            }}
            
            .text-zone:hover {{
                border-left-color: #ff6b6b;
                background: #fff5f5;
                transform: translateX(5px);
            }}
            
            .text-zone.active {{
                border-left-color: #4ecdc4;
                background: #f0fffe;
                box-shadow: 0 2px 8px rgba(78, 205, 196, 0.3);
            }}
            
            .zone-type {{
                font-weight: bold;
                color: #333;
                font-size: 14px;
            }}
            
            .zone-text {{
                margin-top: 5px;
                color: #666;
                line-height: 1.4;
            }}
            
            .zone-confidence {{
                font-size: 11px;
                color: #999;
                margin-top: 5px;
            }}
            
            .type-icons {{
                header: '🏷️', price: '💰', date: '📅',
                address: '🏠', reference: '📄', paragraph: '📝',
                signature: '✍️', footer: '📋', unknown: '❓'
            }}
        </style>
    </head>
    <body>
        <div class="interactive-container">
            <img src="data:image/png;base64,{img_base64}" class="zone-image" id="zoneImage" />
            
            <!-- Overlays pour chaque zone -->
            {overlays_html}
            
            <!-- Tooltip -->
            <div class="zone-tooltip" id="tooltip"></div>
        </div>
        
        <div class="text-results">
            <h4>📝 Texte détecté par zones (cliquez pour surligner)</h4>
            {text_zones_html}
        </div>
        
        <script>
            const zones = {json.dumps(zones_js)};
            const ocrResults = {json.dumps(ocr_js)};
            
            // Émojis pour les types
            const typeEmojis = {{
                'header': '🏷️', 'price': '💰', 'date': '📅',
                'address': '🏠', 'reference': '📄', 'paragraph': '📝',
                'signature': '✍️', 'footer': '📋', 'unknown': '❓'
            }};
            
            // Fonction pour afficher/masquer les highlights
            function highlightZone(zoneId, active = true) {{
                // Highlight sur l'image
                const overlay = document.getElementById('overlay_' + zoneId);
                const textZone = document.getElementById('text_' + zoneId);
                
                if (overlay) {{
                    if (active) {{
                        overlay.classList.add('active');
                    }} else {{
                        overlay.classList.remove('active');
                    }}
                }}
                
                if (textZone) {{
                    if (active) {{
                        textZone.classList.add('active');
                    }} else {{
                        textZone.classList.remove('active');
                    }}
                }}
            }}
            
            // Fonction pour afficher le tooltip
            function showTooltip(event, zoneId) {{
                const tooltip = document.getElementById('tooltip');
                const zone = zones.find(z => z.id === zoneId);
                const ocr = ocrResults[zoneId];
                
                if (zone) {{
                    const emoji = typeEmojis[zone.type] || '❓';
                    let content = `${{emoji}} ${{zone.type.toUpperCase()}}\\n`;
                    
                    if (ocr && ocr.text) {{
                        content += `Texte: "${{ocr.text.substring(0, 100)}}${{ocr.text.length > 100 ? '...' : ''}}"\\n`;
                        content += `Confiance: ${{(ocr.confidence * 100).toFixed(1)}}%\\n`;
                        content += `Méthode: ${{ocr.method}}`;
                    }} else if (zone.content) {{
                        content += `Contenu: "${{zone.content.substring(0, 100)}}${{zone.content.length > 100 ? '...' : ''}}"`;
                    }}
                    
                    tooltip.innerHTML = content.replace(/\\n/g, '<br>');
                    tooltip.style.display = 'block';
                    tooltip.style.left = event.pageX + 10 + 'px';
                    tooltip.style.top = event.pageY - 10 + 'px';
                }}
            }}
            
            // Fonction pour masquer le tooltip
            function hideTooltip() {{
                const tooltip = document.getElementById('tooltip');
                tooltip.style.display = 'none';
            }}
            
            // Event listeners pour les overlays
            zones.forEach(zone => {{
                const overlay = document.getElementById('overlay_' + zone.id);
                const textZone = document.getElementById('text_' + zone.id);
                
                if (overlay) {{
                    overlay.addEventListener('mouseenter', (e) => {{
                        highlightZone(zone.id, true);
                        showTooltip(e, zone.id);
                    }});
                    
                    overlay.addEventListener('mouseleave', () => {{
                        highlightZone(zone.id, false);
                        hideTooltip();
                    }});
                    
                    overlay.addEventListener('click', () => {{
                        // Toggle permanent highlight
                        overlay.classList.toggle('active');
                        if (textZone) textZone.classList.toggle('active');
                    }});
                }}
                
                if (textZone) {{
                    textZone.addEventListener('mouseenter', () => {{
                        highlightZone(zone.id, true);
                    }});
                    
                    textZone.addEventListener('mouseleave', () => {{
                        highlightZone(zone.id, false);
                    }});
                    
                    textZone.addEventListener('click', () => {{
                        // Toggle permanent highlight
                        if (overlay) overlay.classList.toggle('active');
                        textZone.classList.toggle('active');
                    }});
                }}
            }});
            
            // Redimensionnement automatique des overlays
            function updateOverlays() {{
                const img = document.getElementById('zoneImage');
                const rect = img.getBoundingClientRect();
                const scaleX = rect.width / img.naturalWidth;
                const scaleY = rect.height / img.naturalHeight;
                
                zones.forEach(zone => {{
                    const overlay = document.getElementById('overlay_' + zone.id);
                    if (overlay) {{
                        overlay.style.left = (zone.x * scaleX) + 'px';
                        overlay.style.top = (zone.y * scaleY) + 'px';
                        overlay.style.width = (zone.width * scaleX) + 'px';
                        overlay.style.height = (zone.height * scaleY) + 'px';
                    }}
                }});
            }}
            
            // Mise à jour au chargement et redimensionnement
            window.addEventListener('load', updateOverlays);
            window.addEventListener('resize', updateOverlays);
            
            // Observer pour les changements de taille de l'image
            const img = document.getElementById('zoneImage');
            img.addEventListener('load', updateOverlays);
        </script>
    </body>
    </html>
    """
    
    return interactive_html

def generate_zone_overlays(zones_js):
    """Génère les overlays HTML pour chaque zone"""
    overlays = ""
    for zone in zones_js:
        overlays += f'''
            <div class="zone-overlay" 
                 id="overlay_{zone['id']}"
                 style="left: {zone['x']}px; top: {zone['y']}px; 
                        width: {zone['width']}px; height: {zone['height']}px;">
            </div>
        '''
    return overlays

def generate_text_zones(zones_js, ocr_js):
    """Génère l'affichage des zones de texte"""
    type_emojis = {
        'header': '🏷️', 'price': '💰', 'date': '📅',
        'address': '🏠', 'reference': '📄', 'paragraph': '📝',
        'signature': '✍️', 'footer': '📋', 'unknown': '❓'
    }
    
    text_zones = ""
    for zone in zones_js:
        emoji = type_emojis.get(zone['type'], '❓')
        zone_id = zone['id']
        
        # Récupérer le texte OCR si disponible
        text_content = ""
        confidence_info = ""
        
        if zone_id in ocr_js:
            ocr = ocr_js[zone_id]
            text_content = ocr.get('text', 'Aucun texte détecté')
            confidence = ocr.get('confidence', 0) * 100
            method = ocr.get('method', 'Unknown')
            confidence_info = f"Confiance: {confidence:.1f}% | Méthode: {method}"
        elif zone.get('content'):
            text_content = zone['content']
            if zone.get('confidence'):
                confidence_info = f"Confiance: {zone['confidence']*100:.1f}%"
        else:
            text_content = "Contenu non disponible"
        
        text_zones += f'''
            <div class="text-zone" id="text_{zone_id}">
                <div class="zone-type">{emoji} Zone {zone_id.replace('zone_', '')} - {zone['type'].upper()}</div>
                <div class="zone-text">{text_content}</div>
                {f'<div class="zone-confidence">{confidence_info}</div>' if confidence_info else ''}
            </div>
        '''
    
    return text_zones

def create_interactive_image_only(annotated_image_path, zones_data, ocr_results=None):
    """
    Crée l'HTML pour l'image interactive seule (côté gauche)
    """
    # Convertir l'image en base64
    with open(annotated_image_path, "rb") as f:
        img_data = f.read()
        img_base64 = base64.b64encode(img_data).decode()
    
    # Préparer les données des zones
    zones_js = []
    for i, zone in enumerate(zones_data):
        coords = zone.get("coordinates", {})
        zone_info = {
            "id": f"zone_{zone.get('zone_id', i)}",
            "x": coords.get("x", 0),
            "y": coords.get("y", 0), 
            "width": coords.get("width", 100),
            "height": coords.get("height", 100),
            "type": zone.get("type", "unknown"),
            "content": zone.get("content", ""),
            "confidence": zone.get("confidence", 0)
        }
        zones_js.append(zone_info)
    
    # Préparer les résultats OCR
    ocr_js = {}
    if ocr_results:
        for zone_id, result in ocr_results.items():
            if "zone_info" in result:
                ocr_js[f"zone_{zone_id}"] = {
                    "text": result.get("best_text", ""),
                    "confidence": result.get("best_confidence", 0),
                    "method": result.get("best_method", "")
                }
    
    overlays_html = generate_zone_overlays(zones_js)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .image-container {{
                position: relative;
                display: inline-block;
                max-width: 100%;
            }}
            
            .zone-image {{
                max-width: 100%;
                height: auto;
                display: block;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
            }}
            
            .zone-overlay {{
                position: absolute;
                border: 3px solid transparent;
                cursor: pointer;
                transition: all 0.3s ease;
                z-index: 10;
            }}
            
            .zone-overlay:hover {{
                border-color: #ff6b6b;
                background-color: rgba(255, 107, 107, 0.2);
                box-shadow: 0 0 15px rgba(255, 107, 107, 0.5);
                transform: scale(1.02);
            }}
            
            .zone-overlay.active {{
                border-color: #4ecdc4;
                background-color: rgba(78, 205, 196, 0.3);
                box-shadow: 0 0 20px rgba(78, 205, 196, 0.7);
            }}
            
            .zone-tooltip {{
                position: absolute;
                background: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                z-index: 1000;
                display: none;
                max-width: 300px;
                word-wrap: break-word;
                white-space: normal;
            }}
        </style>
    </head>
    <body>
        <div class="image-container">
            <img src="data:image/png;base64,{img_base64}" class="zone-image" id="zoneImage" />
            {overlays_html}
            <div class="zone-tooltip" id="tooltip"></div>
        </div>
        
        <script>
            const zones = {json.dumps(zones_js)};
            const ocrResults = {json.dumps(ocr_js)};
            
            const typeEmojis = {{
                'header': '🏷️', 'price': '💰', 'date': '📅',
                'address': '🏠', 'reference': '📄', 'paragraph': '📝',
                'signature': '✍️', 'footer': '📋', 'unknown': '❓'
            }};
            
            function highlightZone(zoneId, active = true) {{
                const overlay = document.getElementById('overlay_' + zoneId);
                if (overlay) {{
                    if (active) {{
                        overlay.classList.add('active');
                    }} else {{
                        overlay.classList.remove('active');
                    }}
                }}
                
                // Notifier le parent (côté texte)
                parent.postMessage({{
                    type: 'zone_highlight',
                    zoneId: zoneId,
                    active: active
                }}, '*');
            }}
            
            function showTooltip(event, zoneId) {{
                const tooltip = document.getElementById('tooltip');
                const zone = zones.find(z => z.id === zoneId);
                const ocr = ocrResults[zoneId];
                
                if (zone) {{
                    const emoji = typeEmojis[zone.type] || '❓';
                    let content = `${{emoji}} ${{zone.type.toUpperCase()}}\\n`;
                    
                    if (ocr && ocr.text) {{
                        content += `Texte: "${{ocr.text.substring(0, 100)}}${{ocr.text.length > 100 ? '...' : ''}}"\\n`;
                        content += `Confiance: ${{(ocr.confidence * 100).toFixed(1)}}%\\n`;
                        content += `Méthode: ${{ocr.method}}`;
                    }} else if (zone.content) {{
                        content += `Contenu: "${{zone.content.substring(0, 100)}}${{zone.content.length > 100 ? '...' : ''}}"`;
                    }}
                    
                    tooltip.innerHTML = content.replace(/\\n/g, '<br>');
                    tooltip.style.display = 'block';
                    tooltip.style.left = event.pageX + 10 + 'px';
                    tooltip.style.top = event.pageY - 10 + 'px';
                }}
            }}
            
            function hideTooltip() {{
                document.getElementById('tooltip').style.display = 'none';
            }}
            
            // Event listeners
            zones.forEach(zone => {{
                const overlay = document.getElementById('overlay_' + zone.id);
                if (overlay) {{
                    overlay.addEventListener('mouseenter', (e) => {{
                        highlightZone(zone.id, true);
                        showTooltip(e, zone.id);
                    }});
                    
                    overlay.addEventListener('mouseleave', () => {{
                        highlightZone(zone.id, false);
                        hideTooltip();
                    }});
                    
                    overlay.addEventListener('click', () => {{
                        overlay.classList.toggle('active');
                    }});
                }}
            }});
            
            // Écouter les messages du côté texte
            window.addEventListener('message', function(event) {{
                if (event.data.type === 'text_zone_hover') {{
                    highlightZone(event.data.zoneId, event.data.active);
                }}
            }});
            
            // Redimensionnement automatique
            function updateOverlays() {{
                const img = document.getElementById('zoneImage');
                const rect = img.getBoundingClientRect();
                const scaleX = rect.width / img.naturalWidth;
                const scaleY = rect.height / img.naturalHeight;
                
                zones.forEach(zone => {{
                    const overlay = document.getElementById('overlay_' + zone.id);
                    if (overlay) {{
                        overlay.style.left = (zone.x * scaleX) + 'px';
                        overlay.style.top = (zone.y * scaleY) + 'px';
                        overlay.style.width = (zone.width * scaleX) + 'px';
                        overlay.style.height = (zone.height * scaleY) + 'px';
                    }}
                }});
            }}
            
            window.addEventListener('load', updateOverlays);
            window.addEventListener('resize', updateOverlays);
            document.getElementById('zoneImage').addEventListener('load', updateOverlays);
        </script>
    </body>
    </html>
    """
    
    return html

def create_interactive_text_list(zones_data, ocr_results=None):
    """
    Crée l'HTML pour la liste de texte interactive (côté droit)
    """
    zones_js = []
    for i, zone in enumerate(zones_data):
        zone_info = {
            "id": f"zone_{zone.get('zone_id', i)}",
            "type": zone.get("type", "unknown"),
            "content": zone.get("content", ""),
            "confidence": zone.get("confidence", 0)
        }
        zones_js.append(zone_info)
    
    ocr_js = {}
    if ocr_results:
        for zone_id, result in ocr_results.items():
            if "zone_info" in result:
                ocr_js[f"zone_{zone_id}"] = {
                    "text": result.get("best_text", ""),
                    "confidence": result.get("best_confidence", 0),
                    "method": result.get("best_method", "")
                }
    
    # Générer les zones de texte
    text_zones_html = ""
    type_emojis = {
        'header': '🏷️', 'price': '💰', 'date': '📅',
        'address': '🏠', 'reference': '📄', 'paragraph': '📝',
        'signature': '✍️', 'footer': '📋', 'unknown': '❓'
    }
    
    for zone in zones_js:
        emoji = type_emojis.get(zone['type'], '❓')
        zone_id = zone['id']
        
        text_content = ""
        confidence_info = ""
        
        if zone_id in ocr_js:
            ocr = ocr_js[zone_id]
            text_content = ocr.get('text', 'Aucun texte détecté')
            confidence = ocr.get('confidence', 0) * 100
            method = ocr.get('method', 'Unknown')
            confidence_info = f"Confiance: {confidence:.1f}% | Méthode: {method}"
        elif zone.get('content'):
            text_content = zone['content']
            if zone.get('confidence'):
                confidence_info = f"Confiance: {zone['confidence']*100:.1f}%"
        else:
            text_content = "Contenu non disponible"
        
        text_zones_html += f'''
            <div class="text-zone" id="text_{zone_id}" data-zone-id="{zone_id}">
                <div class="zone-type">{emoji} Zone {zone_id.replace('zone_', '')} - {zone['type'].upper()}</div>
                <div class="zone-text">{text_content}</div>
                {f'<div class="zone-confidence">{confidence_info}</div>' if confidence_info else ''}
            </div>
        '''
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                padding: 10px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f8f9fa;
            }}
            
            .text-zone {{
                margin: 10px 0;
                padding: 15px;
                border-left: 4px solid #ddd;
                background: white;
                cursor: pointer;
                transition: all 0.3s ease;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .text-zone:hover {{
                border-left-color: #ff6b6b;
                background: #fff5f5;
                transform: translateX(5px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            }}
            
            .text-zone.active {{
                border-left-color: #4ecdc4;
                background: #f0fffe;
                box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
            }}
            
            .zone-type {{
                font-weight: bold;
                color: #333;
                font-size: 14px;
                margin-bottom: 8px;
            }}
            
            .zone-text {{
                color: #666;
                line-height: 1.5;
                margin-bottom: 5px;
            }}
            
            .zone-confidence {{
                font-size: 11px;
                color: #999;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        {text_zones_html}
        
        <script>
            const zones = {json.dumps(zones_js)};
            
            function highlightTextZone(zoneId, active = true) {{
                const textZone = document.getElementById('text_' + zoneId);
                if (textZone) {{
                    if (active) {{
                        textZone.classList.add('active');
                    }} else {{
                        textZone.classList.remove('active');
                    }}
                }}
                
                // Notifier le parent (côté image)
                parent.postMessage({{
                    type: 'text_zone_hover',
                    zoneId: zoneId,
                    active: active
                }}, '*');
            }}
            
            // Event listeners pour les zones de texte
            zones.forEach(zone => {{
                const textZone = document.getElementById('text_' + zone.id);
                if (textZone) {{
                    textZone.addEventListener('mouseenter', () => {{
                        highlightTextZone(zone.id, true);
                    }});
                    
                    textZone.addEventListener('mouseleave', () => {{
                        highlightTextZone(zone.id, false);
                    }});
                    
                    textZone.addEventListener('click', () => {{
                        textZone.classList.toggle('active');
                    }});
                }}
            }});
            
            // Écouter les messages du côté image
            window.addEventListener('message', function(event) {{
                if (event.data.type === 'zone_highlight') {{
                    highlightTextZone(event.data.zoneId, event.data.active);
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    return html

def display_interactive_zones_side_by_side(annotated_image_path, zones_data, ocr_results=None):
    """
    Affiche l'interface interactive côte à côte (image + texte)
    """
    # Colonnes côte à côte
    col_img, col_text = st.columns([1, 1])
    
    with col_img:
        st.markdown("#### 🖼️ Image avec zones interactives")
        st.markdown("*Survolez les zones pour les voir en surbrillance*")
        
        # Afficher l'image interactive
        interactive_html_image = create_interactive_image_only(
            annotated_image_path, 
            zones_data, 
            ocr_results
        )
        st.components.v1.html(interactive_html_image, height=600, scrolling=False)
    
    with col_text:
        st.markdown("#### 📝 Texte détecté par zones")
        st.markdown("*Cliquez sur une zone pour la surligner dans l'image*")
        
        # Afficher la liste interactive des zones
        interactive_html_text = create_interactive_text_list(
            zones_data, 
            ocr_results
        )
        st.components.v1.html(interactive_html_text, height=600, scrolling=True)

def display_interactive_zones(annotated_image_path, zones_data, ocr_results=None):
    """
    Affiche l'interface interactive dans Streamlit (version complète)
    """
    st.markdown("### 🎯 Zones interactives - Passez la souris pour explorer")
    st.markdown("*Survolez les zones dans l'image ou cliquez sur le texte pour voir les correspondances*")
    
    # Générer et afficher le HTML interactif
    interactive_html = create_interactive_zone_display(
        annotated_image_path, 
        zones_data, 
        ocr_results
    )
    
    # Afficher dans Streamlit
    st.components.v1.html(interactive_html, height=800, scrolling=True)
    
    # Instructions d'utilisation
    with st.expander("ℹ️ Comment utiliser l'interface interactive"):
        st.markdown("""
        **🖱️ Interactions disponibles :**
        - **Survol souris** : Surligne temporairement la zone correspondante
        - **Clic sur zone** : Active/désactive le surlignage permanent
        - **Survol texte** : Surligne la zone correspondante dans l'image
        - **Tooltip** : Informations détaillées au survol des zones
        
        **🎨 Code couleur :**
        - 🔴 **Rouge** : Zone survolée temporairement
        - 🔵 **Bleu** : Zone sélectionnée en permanence
        - ⚫ **Gris** : Zone inactive
        
        **📍 Types de zones détectées :**
        - 🏷️ **Header** : En-têtes et titres
        - 💰 **Price** : Prix et montants
        - 📅 **Date** : Dates et timestamps
        - 🏠 **Address** : Adresses et localisations
        - 📄 **Reference** : Numéros de référence
        - 📝 **Paragraph** : Paragraphes de texte
        - ✍️ **Signature** : Signatures et paraphes
        - 📋 **Footer** : Pieds de page
        """)
