"""
Interface Streamlit pour l'application OCR Intelligent
"""
import os
import sys
import glob
import shutil
from pathlib import Path

# Configuration de l'environnement
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import fitz
from PIL import Image
from streamlit.components.v1 import html
import docx

# Configuration du chemin backend
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

from backend.main import run_all_ocr_methods
from backend.export import export_to_word


def clear_output_directory():
    """
    Nettoie le dossier output à chaque relancement de l'application
    Supprime tous les fichiers .docx générés précédemment
    """
    output_dir = Path("output")

    if output_dir.exists():
        try:
            # Compter les fichiers avant nettoyage
            files_before = list(output_dir.glob("*.docx"))
            files_count = len(files_before)

            if files_count > 0:
                # Supprimer tous les fichiers .docx
                cleaned_count = 0
                for file_path in files_before:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                    except Exception as e:
                        st.warning(f"Impossible de supprimer {file_path}: {e}")

                if cleaned_count > 0:
                    st.info(f"Dossier output nettoyé: {cleaned_count} fichier(s) supprimé(s)")
            else:
                st.info("Dossier output déjà propre")

        except Exception as e:
            st.error(f"Erreur lors du nettoyage du dossier output: {e}")
    else:
        # Créer le dossier s'il n'existe pas
        output_dir.mkdir(exist_ok=True)
        st.info("Dossier output créé")


# [CLEAN] Nettoyage automatique du dossier output au démarrage
if 'output_cleaned' not in st.session_state:
    clear_output_directory()
    st.session_state.output_cleaned = True

st.set_page_config(page_title="OCR Intelligent", layout="wide")
st.image("frontend/safran_logo.png", width=250)
with open("frontend/custom_style.html") as f:
    html(f.read(), height=0)
st.markdown("<h1> OCR Intelligent </h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(" Téléversez une image ou un PDF", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file:
    os.makedirs("images", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    file_path = os.path.join("images", uploaded_file.name)

    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        st.warning(f"PDF détecté, traitement de {len(doc)} pages.")
        image_paths = []
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image_path = os.path.join("images", f"page_{i+1}.png")
            pix.save(image_path)
            image_paths.append(image_path)
    else:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        image_paths = [file_path]

    # --- OCR multiple
    with st.spinner(" Analyse en cours, merci de patienter..."):
        results, best_method, word_file = run_all_ocr_methods(image_paths)
    st.success(" Analyse terminée !")

    # --- Affichage
    col_img, col_text = st.columns([1, 3])
    with col_img:
        st.image(image_paths[0], caption=" Image analysée")

    with col_text:
        cols = st.columns(len(results))
        for i, (method, data) in enumerate(results.items()):
            with cols[i]:
                st.markdown(f"###  {method.upper()} ({data['avg_conf']:.2f}%)")
                st.text_area("Texte extrait", "\n".join(data['lines']), height=250, key=f"text_{method}")

    st.success(f" Meilleure méthode : {best_method.upper()}")
    with open(word_file, "rb") as f:
        st.download_button(" Télécharger le Word", f, file_name=os.path.basename(word_file))

# --- Upload d'un Word corrigé ---
st.markdown("---")
st.markdown("### Uploader un Word corrigé")
corrected_file = st.file_uploader("Déposez ici votre Word corrigé", type=["docx"], key="corrected")
if corrected_file is not None:
    os.makedirs("corrected", exist_ok=True)
    # Extraire le texte du Word corrigé
    doc = docx.Document(corrected_file)
    corrected_text = "\n".join([p.text for p in doc.paragraphs])
    
    # Sauvegarder la correction
    base_name = uploaded_file.name if uploaded_file else "unknown"
    txt_name = os.path.splitext(base_name)[0] + "_corrige.txt"
    corrected_path = os.path.join("corrected", txt_name)
    os.makedirs("corrected", exist_ok=True)

    with open(corrected_path, "w", encoding="utf-8") as f:
        f.write(corrected_text)
    st.success(f"Texte corrigé enregistré dans {corrected_path}")
