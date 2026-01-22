import streamlit as st
import openai
import json
import io
import time
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. CONFIG VISUAL ---
st.set_page_config(page_title="Infinity Factory 8.1 (Debug)", layout="wide", page_icon="🛠️")

def carregar_css():
    st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #fff; }
        .stButton>button { background: linear-gradient(90deg, #d53369 0%, #daae51 100%); color: white; border: none; padding: 12px; width: 100%; font-weight: bold; }
        [data-testid="stSidebar"] { background-color: #111; }
        h1, h2, h3 { color: white !important; }
        p, label { color: #ccc !important; }
        .stError { background-color: #500; color: #fcc; padding: 10px; border-radius: 5px; }
    </style>""", unsafe_allow_html=True)

# --- 2. LOGIN ---
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if st.session_state.authenticated: return True
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔒 Login")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if senha == "admin": st.session_state.authenticated = True; st.rerun()
            else: st.error("Senha incorreta")
    return False

# --- 3. IA (COM DIAGNÓSTICO DE ERRO) ---
def get_client(api_key): return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def gerar_texto_rico(client, prompt, contexto=""):
    sys = "Você é um Escritor Profissional. Escreva MUITO. Use Markdown. NÃO repita o título."
    try:
        # Tenta conectar na Groq
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Modelo atual
            messages=[
                {"role": "system", "content": sys}, 
                {"role": "user", "content": f"CTX: {contexto}. TAREFA: {prompt}"}
            ],
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception as e:
        # SE DER ERRO, MOSTRA NA TELA
        st.error(f"❌ ERRO NA IA: {e}")
        return None

# --- 4. GERADOR DE WORD ---
def criar_word(tema, publico, conteudo_raw, capa_file):
    doc = Document()
    
    # Capa
    if capa_file:
        try:
            doc.add_picture(capa_file, width=Inches(6))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        except: pass
    
    doc.add_paragraph("\n")
    t = doc.add_heading(tema.upper(), 0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Guia para {publico}").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    # Conteúdo
    if conteudo_raw:
        for linha in conteudo_raw.split('\n'):
            linha = linha.strip()
            if not linha: continue
            if linha.startswith('# '): doc.add_heading(linha.replace('# ', ''), 1)
            elif linha.startswith('## '): doc.add_heading(linha.replace('## ', ''), 2)
            elif '---' in linha: doc.add_page_break()
            else: 
                p = doc.add_paragraph()
                partes = linha.split('**')
                for i, pt in enumerate(partes):
                    r = p.add_run(pt)
                    if i % 2 == 1: r.bold = True
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- APP ---
if "dados" not in st.session_state: st.session_state.dados = {"tema": "", "publico": "", "sumario": "", "conteudo": ""}
carregar_css()

if check_password():
    st.sidebar.title("Factory 8.1 (Debug)")
    api_key = st.sidebar.text_input("API Key Groq", type="password")
    
    # Backup
    with st.sidebar.expander("Backup"):
        st.download_button("Salvar", json.dumps(st.session_state.dados), "bkp.json")
        f = st.file_uploader("Carregar", type=["json"])
        if f: st.session_state.dados = json.load(f); st.rerun()

    if not api_key: st.warning("⚠️ COLOQUE A CHAVE API NA LATERAL"); st.stop()
    client = get_client(api_key)

    t1, t2, t3 = st.tabs(["Planejar", "Escrever", "Baixar Word"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.dados["tema"] = st.text_input("Tema", value=st.session_state.dados["tema"])
            st.session_state.dados["publico"] = st.text_input("Público", value=st.session_state.dados["publico"])
        with c2:
            if st.button("Gerar Sumário"):
                res = gerar_texto_rico(client, f"Sumário para livro '{st.session_state.dados['tema']}' ({st.session_state.dados['publico']}). 5 caps.", "")
                if res: 
                    st.session_state.dados["sumario"] = res
                    st.rerun()
        if st.session_state.dados["sumario"]: st.markdown(st.session_state.dados["sumario"])

    with t2:
        if st.button("🔥 TENTAR ESCREVER LIVRO"):
            st.info("Iniciando processo...")
            bar = st.progress(0)
            st.session_state.dados["conteudo"] = ""
            
            # Escreve 5 capítulos
            for i in range(1, 6):
                with st.spinner(f"Processando Capítulo {i}... (Fique de olho se aparece erro vermelho)"):
                    p = f"Escreva CAPÍTULO {i}. Use ## para subtítulos."
                    ctx = f"Livro: {st.session_state.dados['tema']}."
                    
                    txt = gerar_texto_rico(client, p, ctx)
                    
                    if txt: 
                        st.session_state.dados["conteudo"] += f"# Capítulo {i}\n\n{txt}\n\n---\n"
                        st.success(f"Capítulo {i} OK!")
                    else:
                        st.error(f"Falha ao gerar Capítulo {i}. Verifique a mensagem de erro acima.")
                        break # Para se der erro
                    
                bar.progress(i/5)
                
            if st.session_state.dados["conteudo"]:
                st.balloons()
            
        if st.session_state.dados["conteudo"]: st.markdown(st.session_state.dados["conteudo"])

    with t3:
        st.header("Download Word")
        capa = st.file_uploader("Capa", type=['png', 'jpg'])
        if st.session_state.dados["conteudo"]:
            if st.button("Processar DOCX"):
                docx = criar_word(st.session_state.dados["tema"], st.session_state.dados["publico"], st.session_state.dados["conteudo"], capa)
                st.download_button("BAIXAR WORD", docx, "livro.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
