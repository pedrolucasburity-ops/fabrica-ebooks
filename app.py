import streamlit as st
import openai
import json
import io
import time
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. CONFIG VISUAL ---
st.set_page_config(page_title="Infinity Factory 8.0 (Word Edition)", layout="wide", page_icon="📘")

def carregar_css():
    st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #fff; }
        .stButton>button { background: linear-gradient(90deg, #2b5876 0%, #4e4376 100%); color: white; border: none; padding: 12px; width: 100%; font-weight: bold; }
        [data-testid="stSidebar"] { background-color: #111; }
        h1, h2, h3 { color: white !important; }
        p, label { color: #ccc !important; }
    </style>""", unsafe_allow_html=True)

# --- 2. LOGIN ---
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if st.session_state.authenticated: return True
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔒 Login Factory 8.0")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if senha == "admin": st.session_state.authenticated = True; st.rerun()
            else: st.error("Senha incorreta")
    return False

# --- 3. IA ---
def get_client(api_key): return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def gerar_texto_rico(client, prompt, contexto=""):
    sys = "Você é um Escritor Profissional. Escreva MUITO. Use Markdown (# Titulo, ## Subtitulo, **Negrito**). NÃO repita 'Capítulo X' no título."
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": sys}, {"role": "user", "content": f"CTX: {contexto}. TAREFA: {prompt}"}],
            temperature=0.7
        )
        return resp.choices[0].message.content
    except: return None

# --- 4. GERADOR DE WORD (.DOCX) ---
def criar_word(tema, publico, conteudo_raw, capa_file):
    doc = Document()
    
    # --- CAPA ---
    if capa_file:
        doc.add_picture(capa_file, width=Inches(6))
        last_paragraph = doc.paragraphs[-1] 
        last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph("\n\n") # Espaço
    titulo_capa = doc.add_heading(tema.upper(), 0)
    titulo_capa.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    sub = doc.add_paragraph(f"Um guia para {publico}")
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    # --- SUMÁRIO (Manual) ---
    doc.add_heading('SUMÁRIO', level=1)
    # Extrai tópicos do texto
    for linha in conteudo_raw.split('\n'):
        if linha.startswith('# '):
            t = linha.replace('# ', '').replace('*', '').strip()
            p = doc.add_paragraph(t)
            p.paragraph_format.left_indent = Inches(0.2)
    doc.add_page_break()

    # --- CONTEÚDO ---
    linhas = conteudo_raw.split('\n')
    for linha in linhas:
        linha = linha.strip()
        if not linha: continue
        
        # Título 1 (#)
        if linha.startswith('# '):
            doc.add_heading(linha.replace('# ', '').replace('*', ''), level=1)
        
        # Título 2 (##)
        elif linha.startswith('## '):
            doc.add_heading(linha.replace('## ', '').replace('*', ''), level=2)
            
        # Quebra de Página (---)
        elif '---' in linha:
            doc.add_page_break()
            
        # Parágrafo Comum (com suporte a Negrito simples)
        else:
            p = doc.add_paragraph()
            # Lógica simples para negrito: **texto**
            partes = linha.split('**')
            for i, parte in enumerate(partes):
                runner = p.add_run(parte)
                if i % 2 == 1: # Partes impares estavam entre **
                    runner.bold = True
            p.paragraph_format.space_after = Pt(12) # Espaço após parágrafo

    # Salva na memória
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- APP ---
if "dados" not in st.session_state: st.session_state.dados = {"tema": "", "publico": "", "sumario": "", "conteudo": ""}
carregar_css()

if check_password():
    st.sidebar.title("Factory 8.0 (Word)")
    api_key = st.sidebar.text_input("API Key Groq", type="password")
    
    with st.sidebar.expander("Backup"):
        st.download_button("Salvar JSON", json.dumps(st.session_state.dados), "bkp.json")
        f = st.file_uploader("Carregar JSON", type=["json"])
        if f: st.session_state.dados = json.load(f); st.rerun()

    if not api_key: st.stop()
    client = get_client(api_key)

    t1, t2, t3 = st.tabs(["Planejar", "Escrever", "Baixar Word"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.dados["tema"] = st.text_input("Tema", value=st.session_state.dados["tema"])
            st.session_state.dados["publico"] = st.text_input("Público", value=st.session_state.dados["publico"])
        with c2:
            if st.button("Gerar Sumário"):
                p = f"Crie sumário para livro '{st.session_state.dados['tema']}' ({st.session_state.dados['publico']}). 5 caps."
                st.session_state.dados["sumario"] = gerar_texto_rico(client, p)
                st.rerun()
        if st.session_state.dados["sumario"]: st.markdown(st.session_state.dados["sumario"])

    with t2:
        if st.button("Escrever Livro"):
            bar = st.progress(0)
            st.session_state.dados["conteudo"] = ""
            for i in range(1, 6):
                p = f"Escreva CAPÍTULO {i}. Use ## para subtítulos. Use **negrito**."
                ctx = f"Livro: {st.session_state.dados['tema']}. Público: {st.session_state.dados['publico']}"
                txt = gerar_texto_rico(client, p, ctx)
                if txt: st.session_state.dados["conteudo"] += f"# Capítulo {i}\n\n{txt}\n\n---\n"
                bar.progress(i/5)
            st.success("Pronto!")
            st.rerun()
        if st.session_state.dados["conteudo"]: st.markdown(st.session_state.dados["conteudo"])

    with t3:
        st.header("Download Editável")
        capa = st.file_uploader("Capa (Imagem)", type=['png', 'jpg'])
        
        if st.session_state.dados["conteudo"]:
            # Botão para gerar DOCX
            if st.button("🛠️ Processar Arquivo Word"):
                docx_file = criar_word(
                    st.session_state.dados["tema"],
                    st.session_state.dados["publico"],
                    st.session_state.dados["conteudo"],
                    capa
                )
                
                st.download_button(
                    label="📥 BAIXAR WORD (.DOCX)",
                    data=docx_file,
                    file_name=f"{st.session_state.dados['tema']}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
