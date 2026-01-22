import streamlit as st
import openai
import json
import base64
import time

# --- CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Infinity Factory 6.2", layout="wide", page_icon="✨")

def carregar_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        .stApp { background-color: #0E1117; font-family: 'Inter', sans-serif; }
        h1, h2, h3 { color: #FFFFFF !important; }
        p, label, .stMarkdown { color: #E0E0E0 !important; }
        .stButton > button { background: linear-gradient(90deg, #FF4B4B 0%, #FF914D 100%); color: white; border: none; padding: 12px; border-radius: 8px; }
        [data-testid="stSidebar"] { background-color: #1A1C24; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if st.session_state.authenticated: return True
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔒 Login</h1>", unsafe_allow_html=True)
        senha = st.text_input("Senha", type="password")
        if st.button("ENTRAR"):
            if senha == "admin": 
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Senha errada.")
    return False

def get_client(api_key):
    return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def gerar_texto_rico(client, prompt, contexto=""):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": "Escreva conteúdo denso, técnico e profundo. Use Markdown. Mínimo 800 palavras."}, 
                {"role": "user", "content": f"CONTEXTO: {contexto}\nTAREFA: {prompt}"}
            ], 
            temperature=0.6
        )
        return response.choices[0].message.content
    except: return None

def get_image_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return None

def gerar_html_download(tema, conteudo, img_b64, estilo):
    if not conteudo: conteudo = "<p>Vazio</p>"
    
    # Conversão Markdown -> HTML com classes
    conteudo_html = conteudo\
        .replace("# ", "<h1 class='cap-title'>")\
        .replace("## ", "<h2 class='sub-title'>")\
        .replace("---", "<div class='page-break'></div>")\
        .replace("\n", "<br>")

    # Cores
    cores = {
        "Clássico": {"h1": "#000", "acc": "#333", "bg": "#fff", "font": "Georgia, serif"},
        "Moderno": {"h1": "#2c3e50", "acc": "#2980b9", "bg": "#fff", "font": "Arial, sans-serif"},
        "Dark": {"h1": "#000", "acc": "#c0392b", "bg": "#fff", "font": "Arial, sans-serif"} # Dark imprime branco
    }
    c = cores.get(estilo, cores["Moderno"])
    
    capa = f"<div class='capa'><img src='data:image/jpeg;base64,{img_b64}'><h1 style='font-size:36pt; margin-top:20px'>{tema.upper()}</h1></div><div class='page-break'></div>" if img_b64 else ""

    # HTML BLINDADO PARA A4
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @page {{ size: A4; margin: 2cm; }}
        body {{ 
            margin: 0; padding: 0; 
            background-color: #555; /* Fundo cinza só na tela pra ver a folha */
            -webkit-print-color-adjust: exact; 
        }}
        .folha-a4 {{
            background: white;
            width: 210mm; /* TRAVA A LARGURA */
            min-height: 297mm;
            margin: 20px auto;
            padding: 2cm;
            box-sizing: border-box;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
            
            /* Tipografia Travada */
            font-family: {c['font']};
            font-size: 12pt; 
            line-height: 1.6;
            color: #000;
            text-align: justify;
        }}
        
        h1.cap-title {{ font-size: 24pt; color: {c['h1']}; border-bottom: 2px solid {c['acc']}; padding-bottom: 10px; margin-top: 0; }}
        h2.sub-title {{ font-size: 16pt; color: {c['acc']}; margin-top: 25pt; }}
        p {{ margin-bottom: 12pt; }}
        img {{ max-width: 100%; }}
        .capa {{ text-align: center; padding-top: 30%; }}
        
        @media print {{
            body {{ background: none; }}
            .folha-a4 {{ margin: 0; box-shadow: none; width: 100%; }}
            .page-break {{ page-break-after: always; }}
        }}
    </style>
    </head>
    <body>
        <div class="folha-a4">
            {capa}
            {conteudo_html}
        </div>
    </body>
    </html>
    """

# --- APP ---
if "dados" not in st.session_state: st.session_state.dados = {"tema": "", "sumario": "", "conteudo": ""}
carregar_css()

if check_password():
    st.sidebar.header("Painel 6.2")
    api_key = st.sidebar.text_input("API Key Groq", type="password")
    
    # BACKUP SIMPLES
    with st.sidebar.expander("Backup"):
        st.download_button("Salvar (.json)", json.dumps(st.session_state.dados), "bkp.json")
        f = st.file_uploader("Carregar", type=["json"])
        if f: 
            st.session_state.dados = json.load(f)
            st.rerun()

    if not api_key: st.stop()
    client = get_client(api_key)

    t1, t2, t3 = st.tabs(["Planejar", "Produzir", "Baixar"])
    
    with t1:
        tema = st.text_input("Tema", value=st.session_state.dados["tema"])
        if st.button("Gerar Sumário"):
            st.session_state.dados["tema"] = tema
            st.session_state.dados["sumario"] = gerar_texto_rico(client, f"Sumário para e-book: {tema}. 5 Caps.")
            st.rerun()
        if st.session_state.dados["sumario"]: st.write(st.session_state.dados["sumario"])

    with t2:
        if st.button("Gerar Livro Completo"):
            bar = st.progress(0)
            st.session_state.dados["conteudo"] = ""
            for i in range(1, 6):
                txt = gerar_texto_rico(client, f"Escreva Cap {i} do livro {st.session_state.dados['tema']}. Markdown.")
                if txt: st.session_state.dados["conteudo"] += f"# Capítulo {i}\n\n{txt}\n\n---\n"
                bar.progress(i/5)
            st.success("Feito!")

    with t3:
        estilo = st.selectbox("Estilo", ["Moderno", "Clássico", "Dark"])
        img = st.file_uploader("Capa", type=['jpg','png'])
        if st.session_state.dados["conteudo"]:
            b64 = get_image_base64(img)
            html = gerar_html_download(st.session_state.dados["tema"], st.session_state.dados["conteudo"], b64, estilo)
            st.download_button("BAIXAR HTML PARA PDF", html, "ebook.html", "text/html")
