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
# ESTILO (MISMO QUE LOS ANTERIORES)
# ============================================================
st.markdown("""
<style>
:root{
  --bg:#0b1120; --bg2:#0f172a;
  --panel:#111827; --border:#1f2937;
  --text:#f8fafc; --muted:#cbd5e1;
  --accent:#22d3ee; --accent2:#6366f1;
}
[data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg, var(--bg) 0%, var(--bg2) 100%) !important;
  color: var(--text) !important;
  font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial;
}
main .block-container{ padding-top: 1.8rem; padding-bottom: 2.2rem; }

h1,h2,h3{ color:#f9fafb !important; letter-spacing:-.02em; }
h1 span.grad{
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text; background-clip: text; color: transparent;
}

/* Tarjetas */
.card{
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1.1rem 1.3rem;
  box-shadow: 0 18px 48px rgba(0,0,0,.45);
  animation: fadeIn .5s ease;
}
@keyframes fadeIn{ from{opacity:0; transform: translateY(10px);} to{opacity:1; transform:none;} }

/* Inputs */
.stTextInput input, .stTextArea textarea{
  background:#0f172a !important; color:#f8fafc !important;
  border:1px solid #334155 !important; border-radius:12px !important;
  transition: all .2s ease;
}
.stTextInput input:hover, .stTextArea textarea:hover{
  background:#132036 !important; border-color:#3b82f6 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus{
  background:#0d1829 !important; color:#f8fafc !important;
  border-color:#22d3ee !important; box-shadow:0 0 0 2px rgba(34,211,238,.25);
}

/* Botones */
.stButton > button{
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  border:0; color:#fff; font-weight:600;
  border-radius:999px; padding:.72rem 1.15rem;
  box-shadow:0 12px 36px rgba(99,102,241,.35);
  transition: all .18s ease;
}
.stButton > button:hover{
  transform: translateY(-1px);
  box-shadow:0 16px 46px rgba(99,102,241,.45);
}

/* Uploader */
[data-testid="stFileUploader"] section div{
  background:#0f172a !important; border:1px dashed #334155 !important; border-radius:14px;
}
[data-testid="stFileUploader"] section:hover div{ border-color: var(--accent2) !important; }

footer{ visibility:hidden; }
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
    st.image(image, width=340, caption="Analizador de PDFs con inteligencia artificial")
except Exception as e:
    st.warning(f"No se pudo cargar la imagen: {e}")
card_end()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.subheader("Instrucciones")
    st.write("1️⃣ Ingresa tu clave de **OpenAI**.")
    st.write("2️⃣ Carga un archivo **PDF**.")
    st.write("3️⃣ Escribe una pregunta sobre su contenido.")
    st.write("Ideal para informes, contratos o papers.")

# ============================================================
# API KEY
# ============================================================
card_start()
ke = st.text_input('🔐 Clave de API de OpenAI', type="password", placeholder="sk-...")
if ke:
    os.environ['OPENAI_API_KEY'] = ke
    st.success("Clave cargada correctamente ✅")
else:
    st.warning("Por favor ingresa tu clave de API para continuar")
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

        # 2️⃣ Dividir texto en fragmentos
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=500,
            chunk_overlap=20,
            length_function=len
        )
        chunks = text_splitter.split_text(text)
        st.success(f"Documento dividido en {len(chunks)} fragmentos")

        # 3️⃣ Crear embeddings y base de conocimiento
        with st.spinner("Generando base de conocimiento..."):
            embeddings = OpenAIEmbeddings()
            knowledge_base = FAISS.from_texts(chunks, embeddings)
        st.toast("Base de conocimiento lista 🧠", icon="✅")

        # 4️⃣ Pregunta del usuario
        st.subheader("💭 Escribe tu pregunta sobre el documento:")
        user_question = st.text_area("", placeholder="Ejemplo: ¿Cuál es el tema principal del documento?")

        if user_question:
            st.info("Analizando contexto y generando respuesta...")

            docs = knowledge_base.similarity_search(user_question)
            llm = OpenAI(temperature=0, model_name="gpt-4o")
            chain = load_qa_chain(llm, chain_type="stuff")
            response = chain.run(input_documents=docs, question=user_question)

            st.markdown("### 🧩 Respuesta:")
            st.markdown(
                f"<div style='background:#0f172a; border-radius:10px; padding:1rem 1.2rem; color:#e2e8f0;'>{response}</div>",
                unsafe_allow_html=True
            )
        card_end()

    except Exception as e:
        st.error(f"❌ Error al procesar el PDF: {str(e)}")
        st.error(traceback.format_exc())

elif pdf is not None and not ke:
    st.warning("Por favor ingresa tu clave de API para continuar")
else:
    st.info("Sube un archivo PDF para comenzar el análisis.")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption("💬 RAG PDF Analyzer • Streamlit + LangChain + OpenAI — estética uniforme y profesional")


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption("🧠 RAG • Streamlit + LangChain + OpenAI — interfaz oscura y futurista 🌌")
