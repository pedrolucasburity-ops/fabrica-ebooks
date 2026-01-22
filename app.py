import streamlit as st
import openai
import json
import base64
import markdown # <--- A BIBLIOTECA MÁGICA VOLTOU

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Infinity Factory 6.4", layout="wide", page_icon="✨")

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

# --- 2. SISTEMA DE LOGIN ---
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

# --- 3. LÓGICA DA IA ---
def get_client(api_key):
    return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def gerar_texto_rico(client, prompt, contexto=""):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Você é um autor de livros. Use Markdown (negrito, listas). NÃO repita 'Capítulo X' no início, vá direto ao título do assunto."},
                {"role": "user", "content": f"CONTEXTO: {contexto}\nTAREFA: {prompt}"}
            ],
            temperature=0.6
        )
        return response.choices[0].message.content
    except: return None

def get_image_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return None

# --- 4. GERADOR DE HTML (CORRIGIDO COM MARKDOWN LIB) ---
def gerar_html_download(tema, conteudo_raw, img_b64, estilo):
    if not conteudo_raw: conteudo_raw = "Vazio"
    
    # CONVERSÃO MÁGICA: Markdown -> HTML Real
    # Isso transforma **texto** em negrito e # Título em Título Grande
    html_body = markdown.markdown(conteudo_raw)
    
    # Tratamento para quebras de página (--- vira quebra)
    html_body = html_body.replace("<hr />", "<div class='page-break'></div>")

    # Estilos
    cores = {
        "Clássico": {"h1": "#000", "acc": "#333", "font": "Georgia, serif"},
        "Moderno": {"h1": "#2c3e50", "acc": "#2980b9", "font": "Arial, sans-serif"},
        "Dark": {"h1": "#000", "acc": "#c0392b", "font": "Arial, sans-serif"}
    }
    c = cores.get(estilo, cores["Moderno"])
    
    capa = f"<div class='capa'><img src='data:image/jpeg;base64,{img_b64}'><h1 style='font-size:32pt; margin-top:30px'>{tema.upper()}</h1></div><div class='page-break'></div>" if img_b64 else ""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @page {{ size: A4; margin: 0; }}
        body {{ margin: 0; padding: 0; background-color: #555; -webkit-print-color-adjust: exact; }}
        
        .folha-a4 {{
            background: white; width: 210mm; min-height: 297mm;
            margin: 40px auto; padding: 2.5cm; box-sizing: border-box;
            font-family: {c['font']}; font-size: 12pt; line-height: 1.6; color: #000; text-align: justify;
            box-shadow: 0 0 15px rgba(0,0,0,0.5);
        }}
        
        /* Formatação Automática do Markdown */
        h1 {{ font-size: 24pt; color: {c['h1']}; border-bottom: 2px solid {c['acc']}; margin-top: 1em; }}
        h2 {{ font-size: 16pt; color: {c['acc']}; margin-top: 1.5em; }}
        strong {{ color: {c['acc']}; font-weight: bold; }} /* Negrito colorido */
        ul, ol {{ margin-bottom: 1em; padding-left: 1.5em; }}
        li {{ margin-bottom: 0.5em; }}
        img {{ max-width: 100%; }}
        
        .capa {{ text-align: center; padding-top: 20%; }}
        .capa h1 {{ border: none; }}
        
        @media print {{
            body {{ background: none; }}
            .folha-a4 {{ margin: 0; box-shadow: none; width: 100%; }}
            .page-break {{ page-break-after: always; }}
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
    st.sidebar.title("🚀 Infinity 6.4")
    api_key = st.sidebar.text_input("API Key Groq", type="password")
    
    with st.sidebar.expander("💾 Backup"):
        st.download_button("Salvar (.json)", json.dumps(st.session_state.dados), "bkp.json")
        f = st.file_uploader("Carregar", type=["json"])
        if f: 
            st.session_state.dados = json.load(f)
            st.success("Ok!"); time.sleep(1); st.rerun()

    if not api_key: st.stop()
    client = get_client(api_key)

    t1, t2, t3 = st.tabs(["1. Planejamento", "2. Produção", "3. Entrega"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            # Campos que tinham sumido voltaram
            st.session_state.dados["tema"] = st.text_input("Tema", value=st.session_state.dados["tema"])
            st.session_state.dados["publico"] = st.text_input("Público", value=st.session_state.dados["publico"])
        with c2:
            if st.button("✨ Gerar Sumário"):
                prompt = f"Crie sumário para e-book '{st.session_state.dados['tema']}' (Público: {st.session_state.dados['publico']}). 5 caps."
                st.session_state.dados["sumario"] = gerar_texto_rico(client, prompt)
                st.rerun()
        if st.session_state.dados["sumario"]: st.markdown(st.session_state.dados["sumario"])

    with t2:
        if st.button("🔥 Escrever Livro Completo"):
            if not st.session_state.dados["sumario"]: st.error("Falta sumário")
            else:
                bar = st.progress(0)
                st.session_state.dados["conteudo"] = ""
                ctx = f"Livro: {st.session_state.dados['tema']}. Público: {st.session_state.dados['publico']}."
                for i in range(1, 6):
                    # IA instruída a não repetir título
                    txt = gerar_texto_rico(client, f"Escreva o conteúdo do CAPÍTULO {i}. Use negrito (**texto**) e listas. NÃO escreva 'Capítulo {i}' no título.", ctx)
                    if txt: 
                        # Nós adicionamos o título manualmente aqui para ficar padronizado
                        st.session_state.dados["conteudo"] += f"# Capítulo {i}\n\n{txt}\n\n---\n"
                    bar.progress(i/5)
                st.success("Pronto!")
                st.rerun()
        if st.session_state.dados["conteudo"]: st.markdown(st.session_state.dados["conteudo"])

    with t3:
        c_a, c_b = st.columns(2)
        with c_a: estilo = st.selectbox("Estilo", ["Moderno", "Clássico", "Dark"])
        with c_b: img = st.file_uploader("Capa", type=['jpg','png']) # Capa voltou
        
        if st.session_state.dados["conteudo"]:
            b64 = get_image_base64(img)
            html = gerar_html_download(st.session_state.dados["tema"], st.session_state.dados["conteudo"], b64, estilo)
            st.download_button("📄 BAIXAR ARQUIVO DE IMPRESSÃO", html, "ebook.html", "text/html")
