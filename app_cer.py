import streamlit as st
from google import genai
from PIL import Image
import time

# 1. Configurazione della pagina
st.set_page_config(page_title="Rilevatore CER", page_icon="♻️", layout="centered")

# 2. INIEZIONE CSS PER ESTETICA E TESTO PIÙ GRANDE SU MOBILE
st.markdown("""
<style>
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
    }
    
    /* Ingrandisce i titoli delle schede (Fotocamera / Galleria) */
    button[data-baseweb="tab"] > div {
        font-size: 1.2rem !important;
        font-weight: 600;
    }
    
    /* Rende il riquadro del risultato più elegante */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 15px !important;
        background-color: #f8f9fa;
        border: 2px solid #e0e0e0;
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

# 3. INTERFACCIA DI ANALISI CON PULSANTE E LOGICA DI RETRY AUTOMATICA
if immagine_input is not None:
    img = Image.open(immagine_input)
    st.image(img, caption="Immagine acquisita", use_container_width=True)
    
    prompt = """
    Analizza questa immagine. Identifica il tipo di rifiuto. 
    Fornisci il probabile codice CER (Catalogo Europeo dei Rifiuti) corrispondente. 
    Specifica se il codice è potenzialmente pericoloso (asteriscato). Sii conciso ed elenca in modo chiaro.
    """
    
    # Aggiungiamo un pulsante per dare all'utente il controllo (evita chiamate inutili all'API)
    if st.button("🔍 Analizza Rifiuto", type="primary", use_container_width=True):
        
        status_text = st.empty() # Spazio per i messaggi di caricamento
        progress_bar = st.progress(0)
        
        risultato = None
        max_tentativi = 3
        
        # Ciclo di salvataggio: riprova fino a 3 volte in caso di server occupati
        for tentativo in range(max_tentativi):
            try:
                status_text.info(f"⏳ Analisi in corso... (Tentativo {tentativo + 1} di {max_tentativi})")
                progress_bar.progress(33 * (tentativo + 1))
                
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=[img, prompt]
                )
                risultato = response.text
                break # Se l'analisi riesce, interrompe il ciclo e prosegue
                
            except Exception as e:
                # Controlla se l'errore è dovuto a server sovraccarichi (503) o troppe richieste (429)
                if "503" in str(e) or "429" in str(e) or "unavailable" in str(e).lower():
                    if tentativo < max_tentativi - 1:
                        status_text.warning("⚠️ Server momentaneamente occupati. Attendo 3 secondi e riprovo in automatico...")
                        time.sleep(3) # Pausa di 3 secondi prima del prossimo tentativo
                    else:
                        status_text.empty()
                        st.error("I server di Google sono troppo congestionati in questo momento. Riprova tra qualche minuto.")
                else:
                    status_text.empty()
                    st.error(f"Errore imprevisto durante l'analisi: {e}")
                    break
        
        # Pulizia della barra di caricamento
        progress_bar.empty()
        
        # Se l'analisi è andata a buon fine, stampa il risultato
        if risultato:
            status_text.success("✅ Analisi completata con successo!")
            st.markdown("### 📋 Risultato Classificazione:")
            
            with st.container(border=True):
                st.write(risultato)
                
st.markdown("---")
st.caption("⚠️ **Nota tecnica:** L'assegnazione definitiva del codice CER e la verifica della pericolosità richiedono l'applicazione delle procedure previste dal D.Lgs. 152/2006.")
