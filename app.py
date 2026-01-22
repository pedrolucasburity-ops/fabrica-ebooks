import streamlit as st
import openai
import json
import base64
import markdown
import time
import re

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Infinity Factory 7.3", layout="wide", page_icon="💎")

def carregar_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Inter:wght@400;600&display=swap');
        .stApp { background-color: #0E1117; font-family: 'Inter', sans-serif; }
        h1, h2, h3 { color: #FFFFFF !important; font-family: 'Cinzel', serif; }
        p, label, .stMarkdown { color: #E0E0E0 !important; }
        .stButton > button { background: linear-gradient(135deg, #d53369 0%, #c7913a 100%); color: white; border: none; padding: 14px; border-radius: 8px; width: 100%; font-weight: bold; text-transform: uppercase; }
        [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #222; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIN ---
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if st.session_state.authenticated: return True
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><h1 style='text-align: center;'>🔒 Factory 7.3</h1>", unsafe_allow_html=True)
        senha = st.text_input("Senha", type="password")
        if st.button("ACESSAR"):
            if senha == "admin": 
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Erro.")
    return False

# --- 3. IA (MODO PROFUNDO) ---
def get_client(api_key):
    return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def gerar_texto_rico(client, prompt, contexto=""):
    system_prompt = """
    Você é um ESCRITOR SÊNIOR.
    1. Escreva MUITO. Parágrafos longos, detalhados e explicativos.
    2. Use Markdown: # para Título do Capítulo, ## para Subtítulos.
    3. NÃO coloque 'Capítulo X' no título. Apenas o nome do assunto.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": f"CTX: {contexto}. TAREFA: {prompt}. +1000 palavras."}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except: return None

def get_image_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return None

# --- 4. EXTRAIR SUMÁRIO DO TEXTO (AUTOMÁTICO) ---
def extrair_topicos(conteudo_markdown):
    linhas = conteudo_markdown.split('\n')
    sumario = []
    capitulo_num = 1
    for linha in linhas:
        if linha.startswith('# '):
            titulo = linha.replace('# ', '').replace('*', '').strip()
            sumario.append((1, f"Capítulo {capitulo_num}: {titulo}"))
            capitulo_num += 1
        elif linha.startswith('## '):
            titulo = linha.replace('## ', '').replace('*', '').strip()
            sumario.append((2, titulo))
    return sumario

# --- 5. GERADOR DE HTML ---
def gerar_html_download(tema, conteudo_raw, img_b64, estilo):
    if not conteudo_raw: conteudo_raw = "Vazio"
    
    # Gera Sumário Automático
    lista = extrair_topicos(conteudo_raw)
    html_sumario = ""
    for nivel, txt in lista:
        classe = "main" if nivel == 1 else "sub"
        html_sumario += f"<div class='toc-item {classe}'><span class='toc-text'>{txt}</span><span class='toc-dots'></span></div>"

    # HTML Corpo
    html_body = markdown.markdown(conteudo_raw).replace("<hr />", "<div class='page-break'></div>")

    # Estilos
    cores = {
        "Clássico": {"h1": "#000", "acc": "#800000", "font": "'Merriweather', serif"},
        "Moderno": {"h1": "#2c3e50", "acc": "#2980b9", "font": "'Inter', sans-serif"},
        "Dark": {"h1": "#111", "acc": "#c0392b", "font": "Arial, sans-serif"}
    }
    c = cores.get(estilo, cores["Moderno"])
    
    # Capa
    capa = ""
    if img_b64:
        capa = f"""
        <div class='capa-page'>
            <div class='capa-img' style="background-image: url('data:image/jpeg;base64,{img_b64}');">
                <div class='capa-overlay'><h1 class='titulo-capa'>{tema.upper()}</h1></div>
            </div>
        </div><div class='page-break'></div>"""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:300,700|Inter:400,600|Cinzel:700');
        @page {{ size: A4; margin: 2.5cm; @bottom-center {{ content: counter(page); font-size: 9pt; color: #555; }} }}
        
        body {{ font-family: {c['font']}; font-size: 12pt; line-height: 1.6; color: #222; margin: 0; text-align: justify; }}
        
        /* Capa Full Screen */
        .capa-page {{ margin: -2.5cm; width: 210mm; height: 297mm; overflow: hidden; page-break-after: always; }}
        .capa-img {{ width: 100%; height: 100%; background-size: cover; display: flex; align-items: flex-end; }}
        .capa-overlay {{ background: linear-gradient(to top, rgba(0,0,0,0.9), transparent); width: 100%; padding: 3cm 1cm 2cm; text-align: center; }}
        .titulo-capa {{ font-family: 'Cinzel', serif; font-size: 36pt; color: white !important; margin: 0; text-shadow: 0 4px 10px rgba(0,0,0,0.5); border: none !important; }}

        /* Sumário */
        .toc-page {{ margin: 2cm 0; }}
        .toc-title {{ text-align: center; font-family: 'Cinzel', serif; border-bottom: 2px solid #ccc; padding-bottom: 10px; margin-bottom: 30px; }}
        .toc-item {{ display: flex; align-items: baseline; margin-bottom: 8px; }}
        .toc-item.main {{ font-weight: bold; font-size: 13pt; color: {c['acc']}; margin-top: 15px; }}
        .toc-item.sub {{ margin-left: 20px; font-size: 11pt; color: #555; }}
        .toc-text {{ flex-shrink: 0; }}
        .toc-dots {{ flex-grow: 1; border-bottom: 1px dotted #999; margin: 0 5px; }}

        /* Texto */
        h1 {{ font-size: 22pt; color: {c['h1']}; border-bottom: 3px solid {c['acc']}; padding-bottom: 10px; page-break-after: avoid; }}
        h2 {{ font-size: 16pt; color: {c['acc']}; margin-top: 30px; font-weight: bold; page-break-after: avoid; }}
        p {{ text-indent: 1.5cm; margin-bottom: 10px; }}
        h1 + p, h2 + p {{ text-indent: 0; }} /* Sem recuo após título */
        ul, ol {{ padding-left: 1.5cm; }}
        
        @media print {{ body {{ background: white; }} .capa-page {{ -webkit-print-color-adjust: exact; }} }}
    </style>
    </head>
    <body>
        {capa}
        <div class="toc-page"><h1 class="toc-title">SUMÁRIO</h1>{html_sumario}</div>
        <div class="page-break"></div>
        {html_body}
    </body>
    </html>
    """

# --- INICIALIZAÇÃO CORRIGIDA ---
if "dados" not in st.session_state: 
    st.session_state.dados = {"tema": "", "publico": "", "sumario": "", "conteudo": ""}
carregar_css()

# --- APP ---
if check_password():
    st.sidebar.title("💎 Factory 7.3")
    api_key = st.sidebar.text_input("API Key Groq", type="password")
    
    with st.sidebar.expander("💾 Backup"):
        st.download_button("Salvar JSON", json.dumps(st.session_state.dados), "projeto.json")
        f = st.file_uploader("Carregar JSON", type=["json"])
        if f: st.session_state.dados = json.load(f); st.rerun()

    if not api_key: st.stop()
    client = get_client(api_key)

    t1, t2, t3 = st.tabs(["1. Planejar", "2. Escrever", "3. Exportar"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            # VOLTOU AQUI O INPUT \/
            st.session_state.dados["tema"] = st.text_input("Tema", value=st.session_state.dados["tema"])
            st.session_state.dados["publico"] = st.text_input("Público Alvo", value=st.session_state.dados["publico"])
        with c2:
            if st.button("Gerar Plano"):
                st.session_state.dados["sumario"] = gerar_texto_rico(client, f"Crie plano de tópicos para livro '{st.session_state.dados['tema']}' (Público: {st.session_state.dados['publico']}). 5 caps.", "")
                st.rerun()
        if st.session_state.dados["sumario"]: st.markdown(st.session_state.dados["sumario"])

    with t2:
        if st.button("🔥 Escrever Livro"):
            bar = st.progress(0)
            st.session_state.dados["conteudo"] = ""
            for i in range(1, 6):
                # Inclui PUBLICO no contexto
                prompt = f"Escreva CAPÍTULO {i}. Use ## para subtítulos. Não repita título do cap."
                ctx = f"Livro: {st.session_state.dados['tema']}. Público: {st.session_state.dados['publico']}."
                txt = gerar_texto_rico(client, prompt, ctx)
                if txt: st.session_state.dados["conteudo"] += f"# Capítulo {i}\n\n{txt}\n\n---\n"
                bar.progress(i/5)
            st.success("Pronto!")
            st.rerun()
        if st.session_state.dados["conteudo"]: st.markdown(st.session_state.dados["conteudo"])

    with t3:
        estilo = st.selectbox("Estilo", ["Clássico", "Moderno", "Dark"])
        img = st.file_uploader("Capa", type=['jpg','png'])
        if st.session_state.dados["conteudo"]:
            b64 = get_image_base64(img)
            html = gerar_html_download(st.session_state.dados["tema"], st.session_state.dados["conteudo"], b64, estilo)
            st.download_button("BAIXAR EBOOK (HTML)", html, "ebook.html", "text/html")
