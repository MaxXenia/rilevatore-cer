import streamlit as st
from google import genai
from PIL import Image

# Configurazione della pagina (deve essere il primo comando)
st.set_page_config(page_title="Rilevatore CER", page_icon="♻️", layout="centered")

# Inizializza il client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Intestazione stilizzata
st.title("♻️ Rilevatore Codici CER")
st.info("Scatta o carica una foto del rifiuto in cantiere per ottenere la classificazione e il codice CER.")

# Schede di caricamento
tab1, tab2 = st.tabs(["📷 Fotocamera", "📁 Galleria"])

with tab1:
    foto_scattata = st.camera_input("Inquadra il rifiuto")

with tab2:
    foto_caricata = st.file_uploader("Seleziona un'immagine", type=['png', 'jpg', 'jpeg'])

immagine_input = foto_scattata if foto_scattata else foto_caricata

if immagine_input is not None:
    img = Image.open(immagine_input)
    st.image(img, caption="Immagine acquisita", use_container_width=True)
    
    with st.spinner("Analisi del rifiuto in corso..."):
        prompt = """
        Analizza questa immagine. Identifica il tipo di rifiuto. 
        Fornisci il probabile codice CER (Catalogo Europeo dei Rifiuti) corrispondente. 
        Specifica se il codice è potenzialmente pericoloso (asteriscato). Sii conciso ed elenca in modo chiaro.
        """
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=[img, prompt]
        )
        
    st.success("Analisi completata!")
    st.markdown("### Risultato:")
    
    # Riquadro per contenere il testo dell'IA in modo ordinato
    with st.container(border=True):
        st.write(response.text)
        
    # Disclaimer tecnico per uso sul campo
    st.caption("⚠️ **Nota tecnica:** L'assegnazione definitiva del codice CER e la verifica della pericolosità richiedono l'applicazione delle procedure previste dal D.Lgs. 152/2006, supportate da eventuali analisi chimiche di laboratorio.")