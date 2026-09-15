import streamlit as st
from google import genai
from PIL import Image
import time

# 1. Configurazione della pagina
st.set_page_config(page_title="Rilevatore CER", page_icon="♻️", layout="centered")

# 2. INIEZIONE CSS PER ESTETICA, SFONDO VERDE E TESTO SU MOBILE
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(to bottom, #e8f5e9 0%, #f6fdf8 100%);
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

# Inizializza il client in modo sicuro
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("♻️ Rilevatore Codici CER")
st.info("Scatta o carica una foto del rifiuto in cantiere per ottenere la classificazione, il codice CER e le indicazioni di stoccaggio.")

tab1, tab2 = st.tabs(["📷 Fotocamera", "📁 Galleria"])

with tab1:
    foto_scattata = st.camera_input("Inquadra il rifiuto")

with tab2:
    foto_caricata = st.file_uploader("Seleziona un'immagine", type=['png', 'jpg', 'jpeg'])

immagine_input = foto_scattata if foto_scattata else foto_caricata

# 3. INTERFACCIA DI ANALISI CON LOGICA DI RETRY E PROMPT AGGIORNATO
if immagine_input is not None:
    img = Image.open(immagine_input)
    st.image(img, caption="Immagine acquisita", use_container_width=True)
    
    # Prompt arricchito con le richieste per il deposito temporaneo in cantiere
    prompt = """
    Analizza questa immagine scattata in un cantiere edile/infrastrutturale. 
    Fornisci un output strutturato con i seguenti punti:
    1. **Identificazione Rifiuto:** Descrivi brevemente cosa vedi.
    2. **Codice CER Proposto:** Fornisci il probabile codice CER (Catalogo Europeo dei Rifiuti) corrispondente. Specifica chiaramente se si tratta di un codice pericoloso (asteriscato).
    3. **Prescrizioni per il Deposito Temporaneo:** Indica le corrette modalità di stoccaggio in cantiere in attesa dello smaltimento, nel rispetto del D.Lgs. 152/2006 (Art. 185-bis). Specifica accorgimenti operativi pratici (es. utilizzo di big bags, necessità di coperture per evitare dilavamenti, stoccaggio su basamenti impermeabilizzati, vasche di contenimento, etichettatura di pericolo se necessaria).
    Sii conciso, professionale e usa un elenco puntato chiaro.
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
            st.markdown("### 📋 Esito Controllo Ambientale:")
            
            with st.container(border=True):
                st.write(risultato)

# 4. FOOTER E FIRMA
st.markdown("---")
st.caption("⚠️ **Nota tecnica:** L'assegnazione definitiva del codice CER e la classificazione di pericolosità rimangono in capo al produttore del rifiuto secondo le procedure previste dalla normativa vigente.")

st.markdown(
    "<p style='text-align: center; color: #7f8c8d; font-size: 14px; font-style: italic; margin-top: 20px;'>"
    "Sviluppato da: Massimiliano Pontoriere"
    "</p>", 
    unsafe_allow_html=True
)
