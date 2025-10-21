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
# ESTILO VISUAL FUTURISTA (sin afectar la lógica)
# ============================================================
st.markdown("""
<style>
:root {
  --bg:#0a0f1e; --bg2:#0e172a; --panel:#111827;
  --border:#1f2937; --text:#f9fafb; --muted:#94a3b8;
  --accent:#22d3ee; --accent2:#6366f1; --ok:#10b981; --warn:#f59e0b;
}
[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(600px 400px at 20% 10%, rgba(34,211,238,.08), transparent 80%),
    radial-gradient(800px 600px at 90% 5%, rgba(99,102,241,.12), transparent 80%),
    linear-gradient(180deg, var(--bg) 0%, var(--bg2) 100%) !important;
  color: var(--text) !important;
  font-family: 'Inter', system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial;
}
main .block-container {padding-top: 2rem; padding-bottom: 2.5rem; max-width: 850px;}

h1, h2, h3 {color: var(--text); letter-spacing:-.02em;}
h1 span.grad {
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

.card {
  background: rgba(17,24,39,0.9);
  border: 1px solid rgba(255,255,255,.05);
  border-radius: 20px;
  padding: 1.5rem 1.8rem;
  box-shadow: 0 12px 40px rgba(0,0,0,.4);
  backdrop-filter: blur(10px);
  animation: fadeIn .5s ease;
}
@keyframes fadeIn {from{opacity:0; transform:translateY(12px);} to{opacity:1; transform:none;}}

.stButton > button {
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  border: 0; color: #fff; font-weight:600;
  border-radius: 999px; padding: .75rem 1.25rem;
  box-shadow: 0 10px 30px rgba(99,102,241,.3);
  transition: all .18s ease;
}
.stButton > button:hover {
  transform: translateY(-1px);
  box-shadow: 0 15px 40px rgba(99,102,241,.45);
}

.stTextInput input, .stTextArea textarea {
  background:#0f172a !important; color:#f8fafc !important;
  border:1px solid #334155 !important; border-radius:12px !important;
  transition: all .2s ease;
}
.stTextInput input:hover, .stTextArea textarea:hover {
  background:#132036 !important; border-color:#3b82f6 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  background:#0d1829 !important; border-color:#22d3ee !important;
  box-shadow:0 0 0 2px rgba(34,211,238,.25);
}

[data-testid="stFileUploader"] section div {
  background: #111827 !important;
  border: 1px dashed #334155 !important;
  border-radius: 14px;
  color: var(--muted);
}
[data-testid="stFileUploader"] section:hover div {border-color: var(--accent2) !important;}

.stAlert {
  background: rgba(17,24,39,0.7) !important;
  border-left: 3px solid var(--accent2) !important;
  border-radius: 10px;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def card_start(): st.markdown('<div class="card">', unsafe_allow_html=True)
def card_end():   st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TITULAR Y CABECERA
# ============================================================
st.markdown("## 💬 <span class='grad'>Generación Aumentada por Recuperación (RAG)</span>", unsafe_allow_html=True)
st.caption(f"Versión de Python: {platform.python_version()}")

# Imagen ilustrativa
card_start()
try:
    image = Image.open('Chat_pdf.png')
    st.image(image, width=340, caption="Agente inteligente RAG — PDF Analyzer")
except Exception as e:
    st.warning(f"No se pudo cargar la imagen: {e}")
card_end()

# ============================================================
# SIDEBAR (informativo)
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Instrucciones")
    st.write("1️⃣ Ingresa tu clave de **OpenAI API**.")
    st.write("2️⃣ Carga un archivo **PDF** para analizarlo.")
    st.write("3️⃣ Escribe tu pregunta y obtén respuestas contextuales.")
    st.write("💡 Ideal para análisis legales, académicos o de investigación.")

# ============================================================
# CLAVE API
# ============================================================
card_start()
ke = st.text_input('🔐 Ingresa tu clave de OpenAI', type="password", placeholder="sk-...")
if ke:
    os.environ['OPENAI_API_KEY'] = ke
    st.success("Clave cargada correctamente ✅")
else:
    st.warning("Por favor ingresa tu clave de API de OpenAI para continuar")
card_end()

# ============================================================
# CARGA DEL PDF
# ============================================================
card_start()
pdf = st.file_uploader("📄 Carga el archivo PDF", type="pdf")
card_end()

# ============================================================
# PROCESAMIENTO RAG
# ============================================================
if pdf is not None and ke:
    try:
        card_start()
        st.markdown("### 🔍 Procesando documento…")

        # 1️⃣ Extraer texto
        pdf_reader = PdfReader(pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""

        st.info(f"Texto extraído: {len(text)} caracteres")

        # 2️⃣ Fragmentar texto
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=500,
            chunk_overlap=20,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        st.success(f"Documento dividido en {len(chunks)} fragmentos")

        # 3️⃣ Embeddings y base de conocimiento
        with st.spinner("Creando base de conocimiento vectorial..."):
            embeddings = OpenAIEmbeddings()
            knowledge_base = FAISS.from_texts(chunks, embeddings)
        st.toast("Base de conocimiento lista 🧠", icon="✅")

        # 4️⃣ Pregunta del usuario
        st.markdown("### 💭 Escribe tu pregunta sobre el documento:")
        user_question = st.text_area(" ", placeholder="Ejemplo: ¿Cuál es el tema principal del documento?")

        if user_question:
            st.markdown("⌛ **Analizando contexto y generando respuesta...**")

            # Buscar fragmentos relevantes
            docs = knowledge_base.similarity_search(user_question)

            # LLM
            llm = OpenAI(temperature=0, model_name="gpt-4o")

            # Cadena QA
            chain = load_qa_chain(llm, chain_type="stuff")

            # Generar respuesta
            response = chain.run(input_documents=docs, question=user_question)

            # Mostrar resultado
            st.markdown("### 🧩 Respuesta generada:")
            st.markdown(f"<div style='background:#0f172a; border-radius:10px; padding:1rem 1.2rem; color:#e2e8f0;'>{response}</div>", unsafe_allow_html=True)

        card_end()

    except Exception as e:
        st.error(f"❌ Error al procesar el PDF: {str(e)}")
        st.error(traceback.format_exc())

elif pdf is not None and not ke:
    st.warning("Por favor ingresa tu clave de API de OpenAI para continuar")
else:
    st.info("Sube un archivo PDF para comenzar el análisis.")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption("🧠 RAG • Streamlit + LangChain + OpenAI — interfaz oscura y futurista 🌌")
