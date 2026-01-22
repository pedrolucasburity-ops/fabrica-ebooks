import streamlit as st
import openai
import json
import base64
import markdown
import time

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Infinity Factory 7.0", layout="wide", page_icon="📚")

def carregar_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Inter:wght@400;600&display=swap');
        
        /* Visual Tela Escura */
        .stApp { background-color: #0E1117; font-family: 'Inter', sans-serif; }
        h1, h2, h3 { color: #FFFFFF !important; }
        p, label, .stMarkdown, .stTextInput label { color: #E0E0E0 !important; }
        
        .stButton > button { 
            background: linear-gradient(90deg, #d53369 0%, #daae51 100%); 
            color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold;
            width: 100%; transition: 0.3s;
        }
        .stButton > button:hover { transform: scale(1.02); }
        [data-testid="stSidebar"] { background-color: #111; border-right: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIN ---
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if st.session_state.authenticated: return True
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><h1 style='text-align: center;'>🔒 Factory 7.0</h1>", unsafe_allow_html=True)
        senha = st.text_input("Senha", type="password")
        if st.button("ENTRAR"):
            if senha == "admin": 
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Acesso Negado.")
    return False

# --- 3. IA (MODO ESCRITOR SÊNIOR) ---
def get_client(api_key):
    return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def gerar_texto_rico(client, prompt, contexto=""):
    system_prompt = """
    Você é um ESCRITOR SÊNIOR de livros didáticos e técnicos.
    
    SUAS REGRAS INEGOCIÁVEIS:
    1. PROFUNDIDADE: Nunca dê respostas curtas. Cada tópico deve ter parágrafos explicativos longos.
    2. ESTRUTURA: Introduza o conceito, explique o 'porquê', dê exemplos e só depois faça listas.
    3. FORMATO: Use Markdown.
       - Use ## para Títulos de Seção (Não use #, pois # é só para o título do capítulo).
       - Use **Negrito** para destacar termos chave.
    4. NÃO repita o título do capítulo no começo do texto. Comece direto no conteúdo.
    """
    
    user_prompt = f"""
    CONTEXTO DO LIVRO: {contexto}
    
    SUA MISSÃO AGORA: {prompt}
    
    Escreva pelo menos 1000 palavras. Seja denso.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7 # Aumentei um pouco para ele ser mais criativo/longo
        )
        return response.choices[0].message.content
    except: return None

def get_image_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return None

# --- 4. GERADOR DE HTML (MARGENS FORÇADAS) ---
def gerar_html_download(tema, conteudo_raw, img_b64, estilo):
    if not conteudo_raw: conteudo_raw = "Vazio"
    
    # Markdown -> HTML
    html_body = markdown.markdown(conteudo_raw)
    html_body = html_body.replace("<hr />", "<div class='page-break'></div>")

    # Estilos
    cores = {
        "Clássico": {"h1": "#000", "acc": "#000", "font": "'Merriweather', serif"},
        "Moderno": {"h1": "#2c3e50", "acc": "#2980b9", "font": "'Inter', sans-serif"},
        "Dark": {"h1": "#000", "acc": "#c0392b", "font": "Arial, sans-serif"}
    }
    c = cores.get(estilo, cores["Moderno"])
    
    capa = f"""
    <div class='capa-container'>
        <div style='height: 100px;'></div>
        <img src='data:image/jpeg;base64,{img_b64}'>
        <h1 style='font-size: 40pt; margin-top: 50px; text-transform: uppercase;'>{tema}</h1>
    </div>
    <div class='page-break'></div>
    """ if img_b64 else ""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        /* FONTS */
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;700&family=Inter:wght@400;700&display=swap');

        /* --- CONFIGURAÇÃO CRÍTICA DE IMPRESSÃO --- */
        @page {{
            size: A4;
            margin: 2.5cm; /* ISSO GARANTE QUE NÃO COMEÇA NO TETO */
        }}

        body {{
            font-family: {c['font']};
            font-size: 12pt;
            line-height: 1.8;
            color: #111;
            background: white;
            text-align: justify;
        }}

        /* Títulos */
        h1 {{ font-size: 24pt; color: {c['h1']}; border-bottom: 3px solid {c['acc']}; padding-bottom: 10px; margin-top: 0; margin-bottom: 30px; page-break-after: avoid; }}
        h2 {{ font-size: 16pt; color: {c['acc']}; margin-top: 40px; margin-bottom: 15px; font-weight: bold; page-break-after: avoid; }}
        h3 {{ font-size: 14pt; color: #444; margin-top: 30px; margin-bottom: 10px; page-break-after: avoid; }}

        /* Texto */
        p {{ margin-bottom: 15px; }}
        
        /* Listas */
        ul, ol {{ margin-bottom: 20px; padding-left: 20px; }}
        li {{ margin-bottom: 8px; }}

        /* Imagens */
        img {{ max-width: 100%; border-radius: 4px; }}
        
        /* Capa */
        .capa-container {{ text-align: center; page-break-after: always; }}
        .capa-container img {{ max-height: 600px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); }}

        /* Utilitários */
        .page-break {{ page-break-after: always; }}
        
        @media print {{
            body {{ background: white; }}
            /* Forçar quebras limpas */
            p, li {{ page-break-inside: avoid; }}
            h1, h2, h3 {{ page-break-after: avoid; }}
        }}
    </style>
    </head>
    <body>
        {capa}
        {html_body}
    </body>
    </html>
    """

# --- INICIALIZAÇÃO ---
if "dados" not in st.session_state: st.session_state.dados = {"tema": "", "publico": "", "sumario": "", "conteudo": ""}
carregar_css()

# --- APP ---
if check_password():
    st.sidebar.title("🚀 Factory 7.0")
    api_key = st.sidebar.text_input("API Key Groq", type="password")
    
    with st.sidebar.expander("💾 Backup"):
        st.download_button("Salvar JSON", json.dumps(st.session_state.dados), "projeto.json")
        f = st.file_uploader("Carregar JSON", type=["json"])
        if f: 
            st.session_state.dados = json.load(f)
            st.success("Carregado!"); time.sleep(1); st.rerun()

    if not api_key: st.stop()
    client = get_client(api_key)

    t1, t2, t3 = st.tabs(["1. Planejar", "2. Escrever", "3. Exportar"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.dados["tema"] = st.text_input("Tema", value=st.session_state.dados["tema"])
            st.session_state.dados["publico"] = st.text_input("Público", value=st.session_state.dados["publico"])
        with c2:
            if st.button("Gerar Sumário"):
                prompt = f"Crie sumário DETALHADO para livro '{st.session_state.dados['tema']}' (Público: {st.session_state.dados['publico']}). 5 capítulos."
                st.session_state.dados["sumario"] = gerar_texto_rico(client, prompt)
                st.rerun()
        if st.session_state.dados["sumario"]: st.markdown(st.session_state.dados["sumario"])

    with t2:
        if st.button("🔥 Escrever Livro (Modo Profundo)"):
            if not st.session_state.dados["sumario"]: st.error("Falta sumário")
            else:
                bar = st.progress(0)
                st.session_state.dados["conteudo"] = ""
                ctx = f"Livro: {st.session_state.dados['tema']}. Público: {st.session_state.dados['publico']}."
                for i in range(1, 6):
                    # Prompt reforçado para profundidade
                    p = f"Escreva o CAPÍTULO {i}. Explique os conceitos profundamente antes de listar tópicos. Use subtítulos ##."
                    txt = gerar_texto_rico(client, p, ctx)
                    if txt: st.session_state.dados["conteudo"] += f"# Capítulo {i}\n\n{txt}\n\n---\n"
                    bar.progress(i/5)
                st.success("Texto Gerado!")
                st.rerun()
        if st.session_state.dados["conteudo"]: st.markdown(st.session_state.dados["conteudo"])

    with t3:
        c_a, c_b = st.columns(2)
        with c_a: estilo = st.selectbox("Estilo", ["Moderno", "Clássico", "Dark"])
        with c_b: img = st.file_uploader("Capa", type=['jpg','png'])
        
        if st.session_state.dados["conteudo"]:
            b64 = get_image_base64(img)
            html = gerar_html_download(st.session_state.dados["tema"], st.session_state.dados["conteudo"], b64, estilo)
            st.download_button("📄 BAIXAR PDF (HTML)", html, "ebook.html", "text/html")
