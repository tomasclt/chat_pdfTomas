<style>
/* =========================
   OVERRIDES DE ARMONÍA VISUAL
   ========================= */

/* 1) Inputs (API key, textos) — altura, radio y foco uniforme */
.stTextInput input, .stTextArea textarea{
  height: 48px;                 /* altura coherente */
  border-radius: 14px !important;
  border: 1px solid #3a4a64 !important;
  background: #0c1324 !important;
  color: #ffffff !important;
  box-shadow: none !important;
  transition: border-color .18s ease, background .18s ease, box-shadow .18s ease;
}
.stTextArea textarea{ height: auto; min-height: 120px; padding-top: .9rem; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder{ color: #c9d3e2 !important; }

.stTextInput input:hover, .stTextArea textarea:hover{
  background: #101935 !important;
  border-color: #4b64ff !important;
}
.stTextInput input:focus, .stTextArea textarea:focus{
  background: #0b1229 !important;
  border-color: #38bdf8 !important;
  box-shadow: 0 0 0 2px rgba(56,189,248,.22) !important;
}

/* 2) File uploader — caja oscura, borde sutil, radio igual y hover suave */
[data-testid="stFileUploader"] section div{
  background: #0f172a !important;
  border: 1px dashed #3a4a64 !important;
  border-radius: 14px !important;
  color: #e7eef9 !important;
  padding: 14px !important;
}
[data-testid="stFileUploader"] section:hover div{
  border-color: #4b64ff !important;
  background: #101c37 !important;
}
[data-testid="stFileUploader"] button{   /* botón “Browse files” */
  background: #111c33 !important;
  color: #e7eef9 !important;
  border: 1px solid #334257 !important;
  border-radius: 999px !important;
  box-shadow: none !important;
}
[data-testid="stFileUploader"] button:hover{
  background: #152242 !important;
  border-color: #4b64ff !important;
}

/* 3) Alertas (success/info/warn) — menos “banda”, más tarjeta */
.stAlert{
  background: #0e1a33 !important;
  border: 1px solid #24324a !important;
  border-left: 4px solid #38bdf8 !important; /* acento */
  border-radius: 14px !important;
  color: #ffffff !important;
  padding: .85rem 1rem !important;
  box-shadow: 0 10px 28px rgba(0,0,0,.35) !important;
}
.stAlert p, .stAlert div, .stAlert span{ color: #ffffff !important; }

/* 4) Títulos de sección (como “Carga el archivo PDF”) — tipografía consistente */
[data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] h4{
  margin-top: .6rem !important;
  margin-bottom: .35rem !important;
  color: #ffffff !important;
  letter-spacing: -0.01em !important;
}

/* 5) Contenedores (espaciado y sombras coherentes) */
.card{
  border-radius: 18px !important;
  border: 1px solid #1e293b !important;
  box-shadow: 0 18px 46px rgba(0,0,0,.45) !important;
}
main .block-container > div:has(.stTextInput), 
main .block-container > div:has([data-testid="stFileUploader"]), 
main .block-container > div:has(.stAlert){
  margin-bottom: .6rem !important;  /* comprime los gaps */
}

/* 6) Tooltip “Press Enter to apply” del input de contraseña — menos invasivo */
[data-testid="stPasswordInput"] ~ div [data-baseweb="tooltip"]{
  opacity: .85 !important;
  color: #e7eef9 !important;
}
</style>

