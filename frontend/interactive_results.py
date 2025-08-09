"""
Module pour l'affichage interactif des résultats OCR finaux
Permet l'interaction avec le document analysé et le texte extrait
"""

import streamlit as st
import json
import base64
from PIL import Image
import io
import os

# Import du module de correction des coordonnées
try:
    from frontend.coordinate_fixer import validate_and_fix_coordinates, check_zone_text_correspondence, debug_zone_positions
except ImportError:
    # Fallback si le module n'est pas disponible
    def validate_and_fix_coordinates(zone_ocr_results, image_path):
        return zone_ocr_results
    def check_zone_text_correspondence(zone_ocr_results):
        return []
    def debug_zone_positions(zone_ocr_results, image_path):
        pass

def create_interactive_results_display(image_path, zone_ocr_results, original_image=None):
    """
    Crée un affichage interactif des résultats finaux OCR
    
    Args:
        image_path: Chemin vers l'image analysée
        zone_ocr_results: Résultats OCR par zones
        original_image: Image originale (optionnel)
    """
    
    # Convertir l'image en base64
    with open(image_path, "rb") as f:
        img_data = f.read()
        img_base64 = base64.b64encode(img_data).decode()
    
    # Préparer les données des zones pour JavaScript
    zones_data = []
    reorganized_text = []
    
    if zone_ocr_results:
        # Récupérer l'ordre de lecture s'il existe
        reading_order = zone_ocr_results.get("reading_order", [])
        
        # Zones réussies
        successful_zones = [z for z in zone_ocr_results.values() 
                           if isinstance(z, dict) and "error" not in z and "zone_info" in z]
        
        # Organiser selon l'ordre de lecture ou ordre naturel
        if reading_order:
            ordered_zones = []
            used_zone_ids = set()
            
            # D'abord, ajouter les zones dans l'ordre de lecture
            for zone_id in reading_order:
                for zone_data in successful_zones:
                    current_zone_id = zone_data["zone_info"]["zone_id"]
                    if current_zone_id == zone_id and current_zone_id not in used_zone_ids:
                        ordered_zones.append(zone_data)
                        used_zone_ids.add(current_zone_id)
                        break
            
            # Puis ajouter les zones non trouvées dans l'ordre de lecture
            for zone_data in successful_zones:
                current_zone_id = zone_data["zone_info"]["zone_id"]
                if current_zone_id not in used_zone_ids:
                    ordered_zones.append(zone_data)
                    used_zone_ids.add(current_zone_id)
            
            successful_zones = ordered_zones
        else:
            # Si pas d'ordre de lecture, trier par position (haut-bas, gauche-droite)
            successful_zones = sorted(successful_zones, key=lambda z: (
                z["zone_info"]["coordinates"]["y"],  # Trier d'abord par Y (haut en bas)
                z["zone_info"]["coordinates"]["x"]   # Puis par X (gauche à droite)
            ))
        
        for i, zone_data in enumerate(successful_zones):
            zone_info = zone_data["zone_info"]
            coords = zone_info.get("coordinates", {})
            
            zone_item = {
                "id": f"zone_{zone_info['zone_id']}",
                "x": coords.get("x", 0),
                "y": coords.get("y", 0),
                "width": coords.get("width", 100),
                "height": coords.get("height", 100),
                "type": zone_info.get("type", "unknown"),
                "text": zone_data.get("best_text", ""),
                "confidence": zone_data.get("confidence", 0),
                "method": zone_data.get("best_method", ""),
                "order": i + 1
            }
            zones_data.append(zone_item)
            reorganized_text.append(zone_data.get("best_text", "").strip())
    
    # Texte réorganisé complet
    full_text = "\n\n".join(filter(None, reorganized_text))
    
    # Calculer les statistiques
    total_zones = len(zones_data)
    avg_confidence = sum(z["confidence"] for z in zones_data) / total_zones if total_zones > 0 else 0
    
    # HTML interactif
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .results-container {{
                display: flex;
                gap: 20px;
                height: 600px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            
            .image-panel {{
                flex: 1;
                position: relative;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                overflow: hidden;
            }}
            
            .text-panel {{
                flex: 1;
                display: flex;
                flex-direction: column;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: #f8f9fa;
            }}
            
            .stats-header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                border-radius: 6px 6px 0 0;
            }}
            
            .stats-row {{
                display: flex;
                justify-content: space-between;
                margin: 5px 0;
            }}
            
            .text-content {{
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                background: white;
                margin: 10px;
                border-radius: 6px;
                border: 1px solid #ddd;
            }}
            
            .zone-image {{
                width: 100%;
                height: 100%;
                object-fit: contain;
                display: block;
            }}
            
                        .zone-overlay {{
                 position: absolute;
                 border: 3px solid rgba(255, 107, 107, 0.7);
                 background-color: rgba(255, 107, 107, 0.1);
                 cursor: pointer;
                 transition: all 0.3s ease;
                 z-index: 10;
                 opacity: 0.8;
             }}
             
             .zone-overlay:hover {{
                 border-color: #ff6b6b;
                 background-color: rgba(255, 107, 107, 0.3);
                 box-shadow: 0 0 15px rgba(255, 107, 107, 0.8);
                 transform: scale(1.02);
                 opacity: 1;
             }}
             
             .zone-overlay.active {{
                 border-color: #4ecdc4;
                 background-color: rgba(78, 205, 196, 0.4);
                 box-shadow: 0 0 20px rgba(78, 205, 196, 0.9);
                 opacity: 1;
             }}
            
            .text-segment {{
                margin: 10px 0;
                padding: 12px;
                border-left: 4px solid #ddd;
                background: #f8f9fa;
                cursor: pointer;
                transition: all 0.3s ease;
                border-radius: 6px;
                position: relative;
            }}
            
            .text-segment:hover {{
                border-left-color: #ff6b6b;
                background: #fff5f5;
                transform: translateX(5px);
                box-shadow: 0 3px 10px rgba(0,0,0,0.1);
            }}
            
            .text-segment.active {{
                border-left-color: #4ecdc4;
                background: #f0fffe;
                box-shadow: 0 3px 15px rgba(78, 205, 196, 0.3);
            }}
            
            .segment-header {{
                font-size: 12px;
                color: #666;
                margin-bottom: 8px;
                font-weight: 500;
            }}
            
            .segment-text {{
                color: #333;
                line-height: 1.5;
                font-size: 14px;
            }}
            
            .confidence-bar {{
                position: absolute;
                top: 8px;
                right: 8px;
                width: 60px;
                height: 4px;
                background: #eee;
                border-radius: 2px;
                overflow: hidden;
            }}
            
            .confidence-fill {{
                height: 100%;
                transition: width 0.3s ease;
            }}
            
            .confidence-high {{ background: #28a745; }}
            .confidence-medium {{ background: #ffc107; }}
            .confidence-low {{ background: #dc3545; }}
            
            .zone-tooltip {{
                position: absolute;
                background: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 10px 15px;
                border-radius: 8px;
                font-size: 12px;
                z-index: 1000;
                display: none;
                max-width: 250px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }}
            
                         .reading-order {{
                 position: absolute;
                 top: 5px;
                 left: 5px;
                 background: rgba(0, 123, 255, 0.9);
                 color: white;
                 border-radius: 50%;
                 width: 24px;
                 height: 24px;
                 display: flex;
                 align-items: center;
                 justify-content: center;
                 font-size: 12px;
                 font-weight: bold;
                 opacity: 0.8;
                 transition: opacity 0.3s ease;
                 box-shadow: 0 2px 4px rgba(0,0,0,0.3);
             }}
             
             .zone-overlay:hover .reading-order {{
                 opacity: 1;
                 transform: scale(1.1);
             }}
        </style>
    </head>
    <body>
        <div class="results-container">
            <!-- Panel image -->
            <div class="image-panel">
                <img src="data:image/png;base64,{img_base64}" class="zone-image" id="resultImage" />
                {generate_result_overlays(zones_data)}
                <div class="zone-tooltip" id="tooltip"></div>
            </div>
            
            <!-- Panel texte -->
            <div class="text-panel">
                <div class="stats-header">
                    <h4 style="margin: 0 0 10px 0;">📊 Résultats de l'analyse</h4>
                    <div class="stats-row">
                        <span>🎯 Zones traitées :</span>
                        <strong>{total_zones}</strong>
                    </div>
                    <div class="stats-row">
                        <span>📈 Confiance moyenne :</span>
                        <strong>{avg_confidence:.1f}% ({get_confidence_label(avg_confidence)})</strong>
                    </div>
                </div>
                
                <div class="text-content">
                    <h4>📝 Texte extrait (ordre de lecture intelligent)</h4>
                    <p style="color: #666; font-style: italic; margin-bottom: 15px;">
                        Le texte est organisé selon l'ordre logique de lecture du document
                    </p>
                    <div id="textSegments">
                        {generate_text_segments(zones_data)}
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            const zones = {json.dumps(zones_data)};
            
            const typeEmojis = {{
                'header': '🏷️', 'price': '💰', 'date': '📅',
                'address': '🏠', 'reference': '📄', 'paragraph': '📝',
                'signature': '✍️', 'footer': '📋', 'unknown': '❓'
            }};
            
            function highlightZone(zoneId, active = true) {{
                const overlay = document.getElementById('overlay_' + zoneId);
                const segment = document.getElementById('segment_' + zoneId);
                
                if (overlay) {{
                    if (active) {{
                        overlay.classList.add('active');
                    }} else {{
                        overlay.classList.remove('active');
                    }}
                }}
                
                if (segment) {{
                    if (active) {{
                        segment.classList.add('active');
                    }} else {{
                        segment.classList.remove('active');
                    }}
                }}
            }}
            
            function showTooltip(event, zoneId) {{
                const tooltip = document.getElementById('tooltip');
                const zone = zones.find(z => z.id === zoneId);
                
                if (zone) {{
                    const emoji = typeEmojis[zone.type] || '❓';
                    const confidence = (zone.confidence * 100).toFixed(1);
                    const textPreview = zone.text.substring(0, 80) + (zone.text.length > 80 ? '...' : '');
                    
                    tooltip.innerHTML = `
                        <div><strong>${{emoji}} Zone ${{zone.order}} - ${{zone.type.toUpperCase()}}</strong></div>
                        <div style="margin: 5px 0;">Confiance: ${{confidence}}%</div>
                        <div style="margin: 5px 0;">Méthode: ${{zone.method.toUpperCase()}}</div>
                        <div style="margin-top: 8px; font-style: italic;">"${{textPreview}}"</div>
                    `;
                    tooltip.style.display = 'block';
                    tooltip.style.left = event.pageX + 10 + 'px';
                    tooltip.style.top = event.pageY - 10 + 'px';
                }}
            }}
            
            function hideTooltip() {{
                document.getElementById('tooltip').style.display = 'none';
            }}
            
            // Event listeners pour les overlays
            zones.forEach(zone => {{
                const overlay = document.getElementById('overlay_' + zone.id);
                const segment = document.getElementById('segment_' + zone.id);
                
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
                        if (segment) segment.classList.toggle('active');
                    }});
                }}
                
                if (segment) {{
                    segment.addEventListener('mouseenter', () => {{
                        highlightZone(zone.id, true);
                    }});
                    
                    segment.addEventListener('mouseleave', () => {{
                        highlightZone(zone.id, false);
                    }});
                    
                    segment.addEventListener('click', () => {{
                        segment.classList.toggle('active');
                        if (overlay) overlay.classList.toggle('active');
                        
                        // Scroll vers la zone dans l'image
                        segment.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }});
                }}
            }});
            
            // Redimensionnement automatique des overlays avec debug
            function updateOverlays() {{
                const img = document.getElementById('resultImage');
                if (!img || !img.naturalWidth || !img.naturalHeight) {{
                    // Image pas encore chargée, on réessaie plus tard
                    setTimeout(updateOverlays, 100);
                    return;
                }}
                
                const rect = img.getBoundingClientRect();
                const scaleX = rect.width / img.naturalWidth;
                const scaleY = rect.height / img.naturalHeight;
                
                // Debug info
                console.log('Image dimensions:', {{
                    natural: {{w: img.naturalWidth, h: img.naturalHeight}},
                    displayed: {{w: rect.width, h: rect.height}},
                    scale: {{x: scaleX, y: scaleY}}
                }});
                
                zones.forEach(zone => {{
                    const overlay = document.getElementById('overlay_' + zone.id);
                    if (overlay) {{
                        const scaledX = zone.x * scaleX;
                        const scaledY = zone.y * scaleY;
                        const scaledW = zone.width * scaleX;
                        const scaledH = zone.height * scaleY;
                        
                        overlay.style.left = scaledX + 'px';
                        overlay.style.top = scaledY + 'px';
                        overlay.style.width = scaledW + 'px';
                        overlay.style.height = scaledH + 'px';
                        
                        // Debug pour la première zone
                        if (zone.order === 1) {{
                            console.log('Zone 1 positioning:', {{
                                original: {{x: zone.x, y: zone.y, w: zone.width, h: zone.height}},
                                scaled: {{x: scaledX, y: scaledY, w: scaledW, h: scaledH}}
                            }});
                        }}
                    }}
                }});
            }}
            
            window.addEventListener('load', updateOverlays);
            window.addEventListener('resize', updateOverlays);
            document.getElementById('resultImage').addEventListener('load', updateOverlays);
        </script>
    </body>
    </html>
    """
    
    return html

def generate_result_overlays(zones_data):
    """Génère les overlays pour les zones dans l'image des résultats"""
    overlays = ""
    for zone in zones_data:
        overlays += f'''
            <div class="zone-overlay" 
                 id="overlay_{zone['id']}"
                 style="left: {zone['x']}px; top: {zone['y']}px; 
                        width: {zone['width']}px; height: {zone['height']}px;">
                <div class="reading-order">{zone['order']}</div>
            </div>
        '''
    return overlays

def generate_text_segments(zones_data):
    """Génère les segments de texte interactifs"""
    segments = ""
    type_emojis = {
        'header': '🏷️', 'price': '💰', 'date': '📅',
        'address': '🏠', 'reference': '📄', 'paragraph': '📝',
        'signature': '✍️', 'footer': '📋', 'unknown': '❓'
    }
    
    for zone in zones_data:
        emoji = type_emojis.get(zone['type'], '❓')
        confidence = zone['confidence'] * 100
        
        # Classe CSS pour la barre de confiance
        if confidence >= 80:
            conf_class = "confidence-high"
        elif confidence >= 60:
            conf_class = "confidence-medium"
        else:
            conf_class = "confidence-low"
        
        segments += f'''
            <div class="text-segment" id="segment_{zone['id']}">
                <div class="segment-header">
                    {emoji} Zone {zone['order']} - {zone['type'].upper()} | {zone['method'].upper()}
                </div>
                <div class="segment-text">{zone['text']}</div>
                <div class="confidence-bar">
                    <div class="confidence-fill {conf_class}" style="width: {confidence}%"></div>
                </div>
            </div>
        '''
    
    return segments

def get_confidence_label(confidence):
    """Retourne le label de confiance"""
    if confidence >= 85:
        return "Excellente"
    elif confidence >= 70:
        return "Bonne"
    elif confidence >= 50:
        return "Moyenne"
    else:
        return "Faible"

def display_interactive_results(image_path, zone_ocr_results):
    """
    Affiche les résultats interactifs dans Streamlit avec validation des coordonnées
    """
    st.markdown("### 📊 Résultats de l'analyse - Vue interactive")
    st.markdown("*Explorez les résultats en survolant les zones et le texte*")
    
    # Utiliser les résultats directement pour l'instant (debug)
    corrected_results = zone_ocr_results
    
    # Vérifications supplémentaires
    issues = check_zone_text_correspondence(corrected_results)
    
    # Debug et diagnostics
    with st.expander("🔧 Debug et diagnostics", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 Statistiques des zones**")
            if corrected_results:
                successful_zones = [z for z in corrected_results.values() 
                                   if isinstance(z, dict) and "error" not in z and "zone_info" in z]
                
                st.write(f"Zones réussies: {len(successful_zones)}")
                
                # Afficher quelques zones pour debug
                for i, zone_data in enumerate(successful_zones[:3]):
                    zone_info = zone_data["zone_info"]
                    coords = zone_info.get("coordinates", {})
                    st.write(f"**Zone {zone_info['zone_id']}:**")
                    st.write(f"- Pos: ({coords.get('x', 0)}, {coords.get('y', 0)})")
                    st.write(f"- Taille: {coords.get('width', 0)}×{coords.get('height', 0)}")
                    st.write(f"- Type: {zone_info.get('type', 'unknown')}")
                    st.write(f"- Texte: {zone_data.get('best_text', '')[:30]}...")
                    st.write("---")
        
        with col2:
            st.write("**⚠️ Problèmes détectés**")
            if issues:
                for issue in issues:
                    icon = "🔴" if issue["type"] == "empty_text" else "🟡"
                    st.write(f"{icon} {issue['message']}")
            else:
                st.write("✅ Aucun problème détecté")
        
        # Debug console info
        if st.button("🖨️ Afficher debug console"):
            debug_zone_positions(corrected_results, image_path)
            st.success("Informations de debug affichées dans la console Python")
    
    # Générer et afficher le HTML interactif avec les coordonnées corrigées
    interactive_html = create_interactive_results_display(
        image_path, 
        corrected_results
    )
    
    # Afficher dans Streamlit
    st.components.v1.html(interactive_html, height=650, scrolling=False)
    


def display_standard_interactive_results(image_path, results, best_method):
    """
    Affiche les résultats interactifs pour le mode standard (sans zones)
    """
    if not results or not best_method:
        return
        
    best_data = results[best_method]
    confidence = best_data['avg_conf']
    text = "\n".join(best_data['lines'])
    
    # HTML simplifié pour le mode standard
    with open(image_path, "rb") as f:
        img_data = f.read()
        img_base64 = base64.b64encode(img_data).decode()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .standard-container {{
                display: flex;
                gap: 20px;
                height: 500px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }}
            
            .image-panel {{
                flex: 1;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                overflow: hidden;
            }}
            
            .text-panel {{
                flex: 1;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: #f8f9fa;
                display: flex;
                flex-direction: column;
            }}
            
            .stats-header {{
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 15px;
                border-radius: 6px 6px 0 0;
            }}
            
            .text-content {{
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                background: white;
                margin: 10px;
                border-radius: 6px;
                border: 1px solid #ddd;
            }}
            
            .result-image {{
                width: 100%;
                height: 100%;
                object-fit: contain;
            }}
            
            .extracted-text {{
                background: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 15px;
                line-height: 1.6;
                white-space: pre-wrap;
                font-family: 'Courier New', monospace;
                color: #333;
            }}
        </style>
    </head>
    <body>
        <div class="standard-container">
            <div class="image-panel">
                <img src="data:image/png;base64,{img_base64}" class="result-image" />
            </div>
            
            <div class="text-panel">
                <div class="stats-header">
                    <h4 style="margin: 0 0 10px 0;">🏆 Meilleur résultat : {best_method.upper()}</h4>
                    <div style="display: flex; justify-content: space-between;">
                        <span>📈 Confiance :</span>
                        <strong>{confidence:.1f}% ({get_confidence_label(confidence)})</strong>
                    </div>
                </div>
                
                <div class="text-content">
                    <h4>📝 Texte extrait</h4>
                    <div class="extracted-text">{text}</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    st.markdown("### 📊 Résultats de l'analyse - Mode standard")
    st.components.v1.html(html, height=550, scrolling=False)
