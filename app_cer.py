import streamlit as st
from google import genai
from PIL import Image
import time

# 1. Configurazione della pagina
st.set_page_config(page_title="Rilevatore CER", page_icon="♻️", layout="centered")

# 2. INIEZIONE CSS PER ESTETICA E INGRANDIMENTO FOTOCAMERA
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom, #e8f5e9 0%, #f6fdf8 100%);
    }
    
    /* INGRANDISCE I PULSANTI DELLA FOTOCAMERA */
    [data-testid="stCameraInput"] button {
        transform: scale(1.5) !important;
        margin-bottom: 15px !important;
    }
    
    p, li, .stMarkdown, .stText {
        font-size: 1.2rem !important;
    }
    .stButton > button {
        border-radius: 12px;
        font-weight: bold;
        font-size: 1.2rem !important;
        padding: 0.6rem 1rem;
        background-color: #2e7d32;
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1b5e20;
        color: white;
    }
    button[data-baseweb="tab"] > div {
        font-size: 1.2rem !important;
        font-weight: 600;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 15px !important;
        background-color: #ffffff;
        border: 2px solid #c8e6c9;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ... (il resto del codice rimane esattamente lo stesso) ...
