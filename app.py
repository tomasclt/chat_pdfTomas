# -*- coding: utf-8 -*-
import os
import platform
import traceback
import streamlit as st
from PIL import Image
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain

# ============================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(page_title="RAG PDF Analyzer", page_icon="💬", layout="centered")

# ============================================================
# ESTILO CLARO Y LEGIBLE (ajustado al feedback)
# ============================================================
st.markdown("""
<style>
:root{
  --bg:#060b18; --bg2:#0a1224;
  --panel:#0f172a; --border:#1e293b;
  --text:#ffffff; --muted:#d1d5db;
  --accent:#38bdf8; --accent2:#818cf8;
  --highlight:#1e40af;
}
[data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg, var(--bg) 0%, var(--bg2) 100%) !important;
  color: var(--text) !important;
  font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial;
}
main .block-container{ padding-top: 1.8rem; padding-bottom: 2.2rem; max-width:850px; }

h1,h2,h3, label, p, span, div, textarea, input, .stMarkdown {
  color: var(--text) !important;
}

h1 span.grad{
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text; background-clip: text; color: transparent;
}

/* Tarjetas */
.card{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1.2rem 1.4rem;
  box-shadow: 0 18px 48px rgba(0,0,0,.55);
  animation: fadeIn .5s ease;
}
@keyframes fadeIn{ from{opacity:0; transform: translateY(10px);} to{opacity:1; transform:none;} }

/* Inputs */
.stTextInput input, .stTextArea textarea{
  background:#0c1324 !important; color:#f9fafb !important;
  border:1px solid #475569 !important; border-radius:12px !important;
  transition: all .2s ease;
}
.stTextInput input:hover, .stTextArea textarea:hover{
  background:#101a34 !important; border-color:#3b82f6 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus{
  background:#0b1228 !important; border-color:#38bdf8 !important;
  box-shadow:0 0 0 2px rgba(56,189,248,.25);
}

/* Botones */
.stButton > button{
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  border:0; color:#ffffff; font-weight:600;
  border-radius:999px; padding:.75rem 1.2rem;
  box-shadow:0 10px 30px rgba(99,102,241,.4);
  transition: all .18s ease;
}
.stButton > button:hover{
  transform: translateY(-1px);
  box-shadow:0 16px 50px rgba(99,102,241,.55);
}

/* File uploader */
[data-testid="stFileUploader"] section div{
  background:#0c1324 !important;
  border:1px dashed #475569 !important;
  border-radius:14px; color:#e2e8f0 !important;
}
[data-testid="stFileUploader"] section:hover div{
  border-color: var(--accent2) !important;
}

/* Scroll y alertas */
.stAlert {
  background:#101a33 !important; border-left: 4px solid var(--accent2);
  border-radius: 12px;
}
footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

def card_start(): st.markdown('<div class="card">', unsafe_allow_html=True)
def card_end():   st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# ENCABEZADO
# ============================================================
st.markdown("## 💬 <span class='grad'>Generación Aumentada por Recuperación (RAG)</span>", unsafe_allow_html=True)
st.caption(f"Versión de Python: {platform.python_version()}")

# Imagen principal
card_start()
try:
    image = Image.open('Chat_pdf.png')
    st.image(image, width=340, caption="Analizador de PDFs con IA")
except Exception as e:
    st.warning(f"No se pudo cargar la imagen: {e}")
card_end()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.subheader("🧭 Instrucciones")
    st.write("1️⃣ Ingresa tu clave de **OpenAI API**.")
    st.write("2️⃣ Carga un archivo **PDF**.")
    st.write("3️⃣ Escribe tu pregunta para analizar el contenido.")
    st.write("🧠 Ideal para contratos, reportes o investigación académica.")

# ============================================================
# CLAVE API
# ============================================================
card_start()
ke = st.text_input('🔐 Clave de API de OpenAI', type="password", placeholder="sk-...")
if ke:
    os.environ['OPENAI_API_KEY'] = ke
    st.success("✅ Clave cargada correctamente")
else:
    st.warning("Por favor ingresa tu clave para continuar")
card_end()

# ============================================================
# CARGA DEL PDF
# ============================================================
card_start()
pdf = st.file_uploader("📄 Carga el archivo PDF", type="pdf")
card_end()

# ============================================================
# PROCESAMIENTO PRINCIPAL
# ============================================================
if pdf is not None and ke:
    try:
        card_start()
        st.subheader("🔎 Procesando documento...")

        # 1️⃣ Extraer texto
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        st.info(f"Texto extraído: {len(text)} caracteres")

        # 2️⃣ Dividir texto
        text_splitter = CharacterTextSplitter(
            separator="\n", chunk_size=500, chunk_overlap=20, length_function=len
        )
        chunks = text_splitter.split_text(text)
        st.success(f"Documento dividido en {len(chunks)} fragmentos")

        # 3️⃣ Crear embeddings
        with st.spinner("Generando base de conocimiento..."):
            embeddings = OpenAIEmbeddings()
            knowledge_base = FAISS.from_texts(chunks, embeddings)
        st.toast("Base de conocimiento lista 🧠", icon="✅")

        # 4️⃣ Pregunta del usuario
        st.subheader("💭 Escribe tu pregunta:")
        user_question = st.text_area("", placeholder="Ejemplo: ¿Cuál es el objetivo principal del documento?")

        if user_question:
            st.info("Analizando contexto y generando respuesta...")
            docs = knowledge_base.similarity_search(user_question)
            llm = OpenAI(temperature=0, model_name="gpt-4o")
            chain = load_qa_chain(llm, chain_type="stuff")
            response = chain.run(input_documents=docs, question=user_question)

            st.markdown("### 🧩 Respuesta:")
            st.markdown(
                f"<div style='background:#101a33; border-radius:12px; padding:1.2rem; font-size:1rem; color:#ffffff;'>{response}</div>",
                unsafe_allow_html=True
            )
        card_end()

    except Exception as e:
        st.error(f"❌ Error al procesar el PDF: {str(e)}")
        st.error(traceback.format_exc())

elif pdf is not None and not ke:
    st.warning("Por favor ingresa tu clave de API antes de continuar")
else:
    st.info("Carga un archivo PDF para comenzar el análisis.")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption("💬 RAG PDF Analyzer • Streamlit + LangChain + OpenAI — contraste optimizado y coherencia visual total ⚡️")
