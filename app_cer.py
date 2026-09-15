import streamlit as st
from google import genai
from PIL import Image
import time

# 1. Configurazione della pagina
st.set_page_config(page_title="Rilevatore CER", page_icon="♻️", layout="centered")

# 2. INIEZIONE CSS PER ESTETICA, SFONDO VERDE E TESTO SU MOBILE
st.markdown("""
<style>
    /* Colore di sfondo verde sfumato per l'intera app */
    .stApp {
        background: linear-gradient(to bottom, #e8f5e9 0%, #f6fdf8 100%);
    }

    /* Ingrandisce il testo generale per una migliore lettura sul cellulare */
    p, li, .stMarkdown, .stText {
        font-size: 1.2rem !important;
    }
    
    /* Arrotonda, colora e ingrandisce i pulsanti */
    .stButton > button {
        border-radius: 12px;
        font-weight: bold;
        font-size: 1.2rem !important;
        padding: 0.6rem 1rem;
        background-color: #2e7d32; /* Verde scuro per il pulsante */
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #1b5e20; /* Verde ancora più scuro al passaggio del dito/mouse */
        color: white;
    }
    
    /* Ingrandisce i titoli delle schede (Fotocamera / Galleria) */
    button[data-baseweb="tab"] > div {
        font-size: 1.2rem !important;
        font-weight: 600;
    }
    
    /* Rende il riquadro del risultato bianco, con bordi arrotondati e ombra */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 15px !important;
        background-color: #ffffff; /* Sfondo bianco per staccare dal verde */
        border: 2px solid #c8e6c9; /* Bordo verdino */
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); /* Leggera ombra 3D */
    }
</style>
""", unsafe_allow_html=True)

# Inizializza il client in modo sicuro
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("♻️ Rilevatore Codici CER")
st.info("Scatta o carica una foto del rifiuto in cantiere per ottenere la classificazione e il codice CER.")

tab1, tab2 = st.tabs(["📷 Fotocamera", "📁 Galleria"])

with tab1:
    foto_scattata = st.camera_input("Inquadra il rifiuto")

with tab2:
    foto_caricata = st.file_uploader("Seleziona un'immagine", type=['png', 'jpg', 'jpeg'])

immagine_input = foto_scattata if foto_scattata else foto_caricata

# 3. INTERFACCIA DI ANALISI CON LOGICA DI RETRY AUTOMATICA
if immagine_input is not None:
    img = Image.open(immagine_input)
    st.image(img, caption="Immagine acquisita", use_container_width=True)
    
    prompt = """
    Analizza questa immagine. Identifica il tipo di rifiuto. 
    Fornisci il probabile codice CER (Catalogo Europeo dei Rifiuti) corrispondente. 
    Specifica se il codice è potenzialmente pericoloso (asteriscato). Sii conciso ed elenca in modo chiaro.
    """
    
    if st.button("🔍 Analizza Rifiuto", type="primary", use_container_width=True):
        
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        risultato = None
        max_tentativi = 3
        
        for tentativo in range(max_tentativi):
            try:
                status_text.info(f"⏳ Analisi in corso... (Tentativo {tentativo + 1} di {max_tentativi})")
                progress_bar.progress(33 * (tentativo + 1))
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=[img, prompt]
                )
                risultato = response.text
                break
                
            except Exception as e:
                if "503" in str(e) or "429" in str(e) or "unavailable" in str(e).lower():
                    if tentativo < max_tentativi - 1:
                        status_text.warning("⚠️ Server momentaneamente occupati. Attendo 3 secondi e riprovo in automatico...")
                        time.sleep(3)
                    else:
                        status_text.empty()
                        st.error("I server di Google sono troppo congestionati in questo momento. Riprova tra qualche minuto.")
                else:
                    status_text.empty()
                    st.error(f"Errore imprevisto durante l'analisi: {e}")
                    break
        
        progress_bar.empty()
        
        if risultato:
            status_text.success("✅ Analisi completata con successo!")
            st.markdown("### 📋 Risultato Classificazione:")
            
            with st.container(border=True):
                st.write(risultato)

# 4. FOOTER E FIRMA
st.markdown("---")
st.caption("⚠️ **Nota tecnica:** L'assegnazione definitiva del codice CER e la verifica della pericolosità richiedono l'applicazione delle procedure previste dal D.Lgs. 152/2006.")

st.markdown(
    "<p style='text-align: center; color: #7f8c8d; font-size: 14px; font-style: italic; margin-top: 20px;'>"
    "Sviluppato da: Massimiliano Pontoriere"
    "</p>", 
    unsafe_allow_html=True
)
