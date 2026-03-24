import streamlit as st
import streamlit.components.v1 as components
import subprocess
import socket
import sys

# Démarrer le vrai backend FastAPI en arrière-plan s'il ne tourne pas déjà
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

if not is_port_in_use(8000):
    # Lancement silencieux du serveur responsable de l'intelligence artificielle
    subprocess.Popen([sys.executable, "-m", "uvicorn", "api:app", "--port", "8000"])

# Configuration Streamlit "Invisible" pour laisser la place au HTML
st.set_page_config(layout="wide", page_title="AI Code Reviewer")

st.markdown("""
<style>
    /* Supprimer tout le rembourrage par défaut de Streamlit */
    .stApp {
        background-color: #080c14 !important;
    }
    .block-container {
        padding: 0rem !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    /* Cacher les headers, footers et menus internes de Streamlit */
    header { display: none !important; }
    footer { display: none !important; }
    #MainMenu { display: none !important; }
    
    /* Gérer l'iframe proprement */
    iframe {
        border: none !important;
        width: 100vw !important;
        margin: 0 !important;
        padding: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Lire exactement le code HTML de l'utilisateur
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Injecter le HTML parfait à l'intérieur de la fenêtre Streamlit native !
components.html(html_content, height=1200, scrolling=True)
