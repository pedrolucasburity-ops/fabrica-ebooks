import streamlit as st
import openai
import json
import base64
import markdown
import time

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Infinity Factory 6.5", layout="wide", page_icon="✨")

def carregar_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        .stApp { background-color: #0E1117; font-family: 'Inter', sans-serif; }
        h1, h2, h3 { color: #FFFFFF !important; }
        p, label, .stMarkdown, .stTextInput label { color: #E0E0E0 !important; }
        .stButton > button { background: linear-gradient(90deg, #FF4B4B 0%, #FF914D 100%); color: white; border: none; padding: 12px; border-radius: 8px; width: 100%; transition: 0.3s; }
        .stButton > button:hover { transform: scale(1.02); }
        [data-testid="stSidebar"] { background-color: #1A1C24; border-right: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIN ---
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if st.session_state.authenticated: return True
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><h1 style='text-align: center;'>🔒 Acesso Restrito</h1>", unsafe_allow_html=True)
        senha = st.text_input("Senha", type="password")
        if st.button("ENTRAR"):
            if senha == "admin": 
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Senha incorreta.")
    return False

# --- 3. LÓGICA IA ---
def get_client(api_key):
    return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def gerar_texto_rico(client, prompt, contexto=""):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": """
                Você é um diagramador de livros.
                REGRAS DE FORMATAÇÃO:
                1. Use Títulos (##) para separar seções importantes.
                2. NUNCA faça listas longas com títulos em negrito na mesma linha (Ex: NÃO faça '**Titulo**: texto').
                3. Ao invés disso, quebre em parágrafos ou use subtítulos.
                4. Use Markdown padrão.
                """},
                {"role": "user", "content": f"CONTEXTO: {contexto}\nTAREFA: {prompt}"}
            ],
            temperature=0.6
        )
        return response.choices[0].message.content
    except: return None

def get_image_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return None

# --- 4. GERADOR DE HTML (CORREÇÃO DE MARGENS E ESPAÇAMENTO) ---
def gerar_html_download(tema, conteudo_raw, img_b64, estilo):
    if not conteudo_raw: conteudo_raw = "Vazio"
    
    # Converte Markdown para HTML
    html_body = markdown.markdown(conteudo_raw)
    
    # Tratamento de quebras
    html_body = html_body.replace("<hr />", "<div class='page-break'></div>")

    # Cores
    cores = {
        "Clássico": {"h1": "#000", "acc": "#333", "font": "'Times New Roman', serif", "bg": "#fff"},
        "Moderno": {"h1": "#1a1a1a", "acc": "#0056b3", "font": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", "bg": "#fff"},
        "Clean": {"h1": "#333", "acc": "#e67e22", "font": "'Helvetica Neue', Helvetica, Arial, sans-serif", "bg": "#fff"}
    }
    c = cores.get(estilo, cores["Moderno"])
    
    capa = f"""
    <div class='capa'>
        <div style='margin-bottom: 50px;'></div>
        <img src='data:image/jpeg;base64,{img_b64}'>
        <h1 style='font-size:36pt; margin-top:40px; text-transform: uppercase;'>{tema}</h1>
    </div>
    <div class='page-break'></div>
    """ if img_b64 else ""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        /* CONFIGURAÇÃO DA FOLHA */
        @page {{ size: A4; margin: 0; }}
        
        body {{ 
            margin: 0; padding: 0; 
            background-color: #555; 
            -webkit-print-color-adjust: exact; 
        }}
        
        .folha-a4 {{
            background: white;
            width: 210mm;
            min-height: 297mm;
            margin: 40px auto;
            /* AQUI ESTÁ O SEGREDO DAS MARGENS: */
            padding-top: 3cm;
            padding-bottom: 3cm;
            padding-left: 2.5cm;
            padding-right: 2.5cm;
            box-sizing: border-box;
            
            /* Tipografia */
            font-family: {c['font']};
            font-size: 12pt; 
            line-height: 1.8; /* Espaçamento entre linhas maior */
            color: #222;
            text-align: justify;
            box-shadow: 0 0 15px rgba(0,0,0,0.5);
        }}
        
        /* FORMATAÇÃO DO TEXTO */
        h1 {{ font-size: 26pt; color: {c['h1']}; margin-bottom: 0.5em; page-break-after: avoid; }}
        
        h2 {{ 
            font-size: 18pt; 
            color: {c['acc']}; 
            margin-top: 2em; /* Mais espaço antes do título */
            margin-bottom: 0.8em; 
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
            page-break-after: avoid;
        }}
        
        h3 {{ font-size: 14pt; color: #444; margin-top: 1.5em; font-weight: bold; }}
        
        p {{ margin-bottom: 1.5em; }} /* Espaço entre parágrafos */
        
        /* LISTAS MAIS BONITAS (Corrige o texto grudado) */
        ul, ol {{ margin-bottom: 1.5em; padding-left: 20px; }}
        li {{ 
            margin-bottom: 10px; /* Espaço entre itens da lista */
            padding-left: 5px;
        }}
        strong {{ color: {c['acc']}; font-weight: 700; }}
        
        /* CAPA */
        .capa {{ text-align: center; display: flex; flex-direction: column; justify-content: center; height: 80%; }}
        .capa img {{ max-width: 90%; max-height: 500px; border-radius: 5px; box-shadow: 0 5px 15px rgba(0,0,0,0.15); }}
        
        /* IMPRESSÃO */
        @media print {{
            body {{ background: none; }}
            .folha-a4 {{ margin: 0; box-shadow: none; width: 100%; height: auto; }}
            .page-break {{ page-break-after: always; }}
            h1, h2, h3 {{ page-break-after: avoid; }}
            img {{ page-break-inside: avoid; }}
            li {{ page-break-inside: avoid; }}
        }}
    </style>
    </head>
    <body><div class="folha-a4">{capa}{html_body}</div></body>
    </html>
    """

# --- INICIALIZAÇÃO ---
if "dados" not in st.session_state: 
    st.session_state.dados = {"tema": "", "publico": "", "sumario": "", "conteudo": ""}
carregar_css()

# --- APP ---
if check_password():
    st.sidebar.title("🚀 Infinity 6.5")
    api_key = st.sidebar.text_input("API Key Groq", type="password")
    
    with st.sidebar.expander("💾 Backup"):
        st.download_button("Salvar", json.dumps(st.session_state.dados), "backup.json")
        f = st.file_uploader("Carregar", type=["json"])
        if f: 
            st.session_state.dados = json.load(f)
            st.success("Carregado!"); time.sleep(1); st.rerun()

    if not api_key: st.stop()
    client = get_client(api_key)

    t1, t2, t3 = st.tabs(["Planejamento", "Produção", "Entrega"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.dados["tema"] = st.text_input("Tema", value=st.session_state.dados["tema"])
            st.session_state.dados["publico"] = st.text_input("Público", value=st.session_state.dados["publico"])
        with c2:
            if st.button("✨ Gerar Sumário"):
                prompt = f"Crie um sumário para e-book sobre '{st.session_state.dados['tema']}' (Público: {st.session_state.dados['publico']}). 5 capítulos."
                st.session_state.dados["sumario"] = gerar_texto_rico(client, prompt)
                st.rerun()
        if st.session_state.dados["sumario"]: st.markdown(st.session_state.dados["sumario"])

    with t2:
        if st.button("🔥 Escrever Livro Completo"):
            if not st.session_state.dados["sumario"]: st.error("Falta sumário")
            else:
                bar = st.progress(0)
                st.session_state.dados["conteudo"] = ""
                ctx = f"Livro: {st.session_state.dados['tema']}."
                for i in range(1, 6):
                    # Prompt ajustado para evitar formatação ruim
                    txt = gerar_texto_rico(client, f"Escreva o CAPÍTULO {i}. Use subtítulos (##) em vez de negrito para separar ideias. Use parágrafos curtos.", ctx)
                    if txt: st.session_state.dados["conteudo"] += f"# Capítulo {i}\n\n{txt}\n\n---\n"
                    bar.progress(i/5)
                st.success("Pronto!")
                st.rerun()
        if st.session_state.dados["conteudo"]: st.markdown(st.session_state.dados["conteudo"])

    with t3:
        c_a, c_b = st.columns(2)
        with c_a: estilo = st.selectbox("Estilo", ["Moderno", "Clássico", "Clean"])
        with c_b: img = st.file_uploader("Capa", type=['jpg','png'])
        
        if st.session_state.dados["conteudo"]:
            b64 = get_image_base64(img)
            html = gerar_html_download(st.session_state.dados["tema"], st.session_state.dados["conteudo"], b64, estilo)
            st.download_button("📄 BAIXAR PDF (HTML)", html, "ebook.html", "text/html")
