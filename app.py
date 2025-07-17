import streamlit as st
import numpy as np
import io
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
# from gradcam import make_gradcam_heatmap, overlay_heatmap

# ---------------------- Configuration Streamlit ----------------------

st.set_page_config(page_title="DiagMind.AI", layout="centered")

# ---------------------- Chargement CSS externe ----------------------

with open("styles/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
# ---------------------- Sidebar Infos ----------------------

with st.sidebar:
    st.image("assets/logo.png", width=200)
    st.title("ℹ️ À propos")
    st.markdown("DiagMind.AI est un outil de détection assistée de tumeurs cérébrales à partir d'images médicales.")
    st.markdown("**Modèle utilisé :** ResNet50 (fine-tuné)")
    st.markdown("**Formats supportés :** JPG, PNG")
    st.markdown("**Développé par Matthieu GRAZIANI**")

# ---------------------- Paramètres ----------------------

IMAGE_SIZE = (128, 128)
CLASS_NAMES = ['Sain', 'Tumeur']

# ---------------------- Chargement modèle ----------------------

@st.cache_resource
def load_best_model():
    return load_model("models/resnet50_phase2.keras")

model = load_best_model()

# ---------------------- Titre de la page ----------------------

st.markdown("### Téléversez une image médicale pour détecter une tumeur")
st.markdown("---")

# ---------------------- Upload de l'image ----------------------

uploaded_file = st.file_uploader("Choisissez une image (JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.toast("Image chargée avec succès ✅", icon="📸")
    img = Image.open(uploaded_file).convert("RGB")
    img_resized = img.resize(IMAGE_SIZE)
    img_array = image.img_to_array(img_resized) / 255.0
    img_batch = np.expand_dims(img_array, axis=0)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(img, caption="🖼️ Image chargée", use_container_width=True)

    with col2:
        with st.spinner("🔍 Analyse de l'image..."):
            prediction = model.predict(img_batch)[0][0]
            predicted_class = CLASS_NAMES[int(prediction > 0.5)]
            confidence = prediction if prediction > 0.5 else 1 - prediction

        st.markdown("### 🔬 Résultat de l'analyse :")
        st.markdown(f"**Prédiction :** `{predicted_class}`")
        st.progress(int(confidence * 100))
        st.markdown(f"**Confiance du modèle :** `{confidence:.2%}`")

        # Message selon la classe
        if predicted_class == 'Tumeur':
            st.error("⚠️ Présence probable d'une tumeur détectée.")
        else:
            st.success("✅ Aucune tumeur détectée.")

        # Téléchargement résultat
        result_text = f"Classe prédite : {predicted_class}\nConfiance : {confidence:.2%}"
        st.download_button("📄 Télécharger le rapport", result_text, file_name="resultat_diagmind.txt")

    # Bouton de réinitialisation
    if st.button("🔄 Réinitialiser"):
        st.rerun()
else:
    st.info("Veuillez téléverser une image médicale pour commencer l’analyse.")