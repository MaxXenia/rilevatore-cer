import streamlit as st
from google import genai
from PIL import Image

# Configurazione della pagina
st.set_page_config(page_title="Rilevatore CER", page_icon="♻️", layout="centered")

# Inizializza il client in modo sicuro
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("♻️ Rilevatore Codici CER")
st.info("Scatta o carica una foto del rifiuto per ottenere la classificazione e il codice CER.")

tab1, tab2 = st.tabs(["📷 Fotocamera", "📁 Galleria"])

with tab1:
    foto_scattata = st.camera_input("Inquadra il rifiuto")

with tab2:
    foto_caricata = st.file_uploader("Seleziona un'immagine", type=['png', 'jpg', 'jpeg'])

immagine_input = foto_scattata if foto_scattata else foto_caricata

if immagine_input is not None:
    img = Image.open(immagine_input)
    
    # Aggiornato con la nuova sintassi richiesta da Streamlit
    st.image(img, caption="Immagine acquisita", use_container_width=True)
    
    with st.spinner("Analisi del rifiuto in corso..."):
        prompt = """
        Analizza questa immagine. Identifica il tipo di rifiuto. 
        Fornisci il probabile codice CER (Catalogo Europeo dei Rifiuti) corrispondente. 
        Specifica se il codice è potenzialmente pericoloso (asteriscato). Sii conciso ed elenca in modo chiaro.
        """
        
        # Gestione sicura degli errori di rete o di sovraccarico server
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[img, prompt]
            )
            
            st.success("Analisi completata!")
            st.markdown("### Risultato:")
            
            with st.container(border=True):
                st.write(response.text)
                
        except Exception as e:
            st.error(f"Impossibile completare l'analisi a causa di un errore del server IA: {e}")
            st.warning("I server di Google potrebbero essere sovraccarichi. Attendi qualche istante e riprova.")
            
    st.caption("⚠️ **Nota tecnica:** L'assegnazione definitiva del codice CER e la verifica della pericolosità richiedono l'applicazione delle procedure previste dal D.Lgs. 152/2006.")
