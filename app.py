import streamlit as st
import openai
import json
import base64
import time

# --- 1. CONFIGURAÇÃO VISUAL (TELA) ---
st.set_page_config(page_title="Infinity Factory 6.3", layout="wide", page_icon="✨")

def carregar_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        /* Visual do App (Dark Mode) */
        .stApp { background-color: #0E1117; font-family: 'Inter', sans-serif; }
        h1, h2, h3 { color: #FFFFFF !important; }
        p, label, .stMarkdown, .stTextInput label { color: #E0E0E0 !important; }
        
        /* Inputs */
        .stTextInput > div > div > input { 
            background-color: #262730; color: white; border: 1px solid #4A4A4A; border-radius: 8px; 
        }
        
        /* Botões */
        .stButton > button { 
            background: linear-gradient(90deg, #FF4B4B 0%, #FF914D 100%); 
            color: white; border: none; padding: 12px; border-radius: 8px; font-weight: 600;
            width: 100%; transition: 0.3s;
        }
        .stButton > button:hover { transform: scale(1.02); }
        
        /* Sidebar */
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
        st.markdown("<p style='text-align: center;'>Digite a senha de administrador.</p>", unsafe_allow_html=True)
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
                {"role": "system", "content": "Você é um autor técnico experiente. Escreva conteúdo denso, detalhado e didático. Use Markdown."},
                {"role": "user", "content": f"CONTEXTO DO PROJETO: {contexto}\n\nSUA TAREFA: {prompt}"}
            ],
            temperature=0.6
        )
        return response.choices[0].message.content
    except: return None

def get_image_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return None

# --- 4. GERADOR DE HTML (CORREÇÃO DE IMPRESSÃO) ---
def gerar_html_download(tema, conteudo, img_b64, estilo):
    if not conteudo: conteudo = "<p>Vazio</p>"
    
    # Prepara o HTML do conteúdo
    conteudo_html = conteudo\
        .replace("# ", "<h1 class='cap-title'>")\
        .replace("## ", "<h2 class='sub-title'>")\
        .replace("---", "<div class='page-break'></div>")\
        .replace("\n", "<br>")

    # Definição de Cores
    cores = {
        "Clássico": {"h1": "#000", "acc": "#333", "font": "Georgia, serif"},
        "Moderno": {"h1": "#2c3e50", "acc": "#2980b9", "font": "Arial, sans-serif"},
        "Dark": {"h1": "#000", "acc": "#c0392b", "font": "Arial, sans-serif"} # Dark imprime em branco
    }
    c = cores.get(estilo, cores["Moderno"])
    
    capa = f"<div class='capa'><img src='data:image/jpeg;base64,{img_b64}'><h1 style='font-size:32pt; margin-top:30px'>{tema.upper()}</h1></div><div class='page-break'></div>" if img_b64 else ""

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @page {{ size: A4; margin: 0; }} /* Tira margem do navegador */
        
        body {{ 
            margin: 0; padding: 0; 
            background-color: #555; 
            -webkit-print-color-adjust: exact; 
        }}
        
        /* A FOLHA A4 TRAVADA */
        .folha-a4 {{
            background: white;
            width: 210mm; /* LARGURA EXATA DO A4 */
            min-height: 297mm;
            margin: 40px auto;
            padding: 2.5cm; /* Margem interna do papel */
            box-sizing: border-box;
            box-shadow: 0 0 15px rgba(0,0,0,0.5);
            
            /* Tipografia */
            font-family: {c['font']};
            font-size: 12pt; 
            line-height: 1.6;
            color: #000;
            text-align: justify;
        }}
        
        h1.cap-title {{ font-size: 24pt; color: {c['h1']}; border-bottom: 2px solid {c['acc']}; margin-top: 0; padding-bottom: 10px; }}
        h2.sub-title {{ font-size: 16pt; color: {c['acc']}; margin-top: 20pt; }}
        p {{ margin-bottom: 12pt; }}
        img {{ max-width: 100%; }}
        .capa {{ text-align: center; padding-top: 20%; }}
        
        /* MODO IMPRESSÃO (CTRL+P) */
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

# --- INICIALIZAÇÃO DE DADOS ---
if "dados" not in st.session_state: 
    st.session_state.dados = {"tema": "", "publico": "", "sumario": "", "conteudo": ""}

carregar_css()

# --- APP PRINCIPAL ---
if check_password():
    st.sidebar.title("🚀 Infinity 6.3")
    api_key = st.sidebar.text_input("API Key Groq", type="password")
    
    # SISTEMA DE BACKUP
    with st.sidebar.expander("💾 Backup do Projeto"):
        st.download_button("Baixar (.json)", json.dumps(st.session_state.dados), "projeto.json")
        f = st.file_uploader("Carregar (.json)", type=["json"])
        if f: 
            st.session_state.dados = json.load(f)
            st.success("Carregado!")
            time.sleep(1)
            st.rerun()

    if not api_key: st.stop()
    client = get_client(api_key)

    # TABS (AGORA COM OS CAMPOS CERTOS)
    t1, t2, t3 = st.tabs(["1. Planejamento", "2. Produção", "3. Entrega"])
    
    with t1:
        col1, col2 = st.columns(2)
        with col1:
            # VOLTOU: Campo Público Alvo
            novo_tema = st.text_input("Tema Principal", value=st.session_state.dados["tema"])
            novo_publico = st.text_input("Público Alvo", value=st.session_state.dados["publico"])
            
            # Atualiza estado
            if novo_tema != st.session_state.dados["tema"]: st.session_state.dados["tema"] = novo_tema
            if novo_publico != st.session_state.dados["publico"]: st.session_state.dados["publico"] = novo_publico

        with col2:
            st.info("Define a base do seu infoproduto.")
            if st.button("✨ Gerar Sumário"):
                prompt = f"Crie um sumário para e-book sobre '{novo_tema}'. Público: {novo_publico}. 6 capítulos."
                st.session_state.dados["sumario"] = gerar_texto_rico(client, prompt)
                st.rerun()
        
        if st.session_state.dados["sumario"]:
            st.markdown("---")
            st.markdown(st.session_state.dados["sumario"])

    with t2:
        st.header("Fábrica de Texto")
        if st.button("🔥 Escrever Livro Completo"):
            if not st.session_state.dados["sumario"]:
                st.error("Gere o sumário antes!")
            else:
                bar = st.progress(0)
                st.session_state.dados["conteudo"] = ""
                contexto = f"Livro: {st.session_state.dados['tema']}. Público: {st.session_state.dados['publico']}."
                
                for i in range(1, 7):
                    prompt_cap = f"Escreva o CAPÍTULO {i} completo. Seja denso, técnico e use Markdown. Mínimo 800 palavras."
                    txt = gerar_texto_rico(client, prompt_cap, contexto)
                    if txt: st.session_state.dados["conteudo"] += f"# Capítulo {i}\n\n{txt}\n\n---\n"
                    bar.progress(i/6)
                st.success("Concluído!")
                st.rerun()
        
        if st.session_state.dados["conteudo"]:
            with st.expander("Ver Texto"): st.markdown(st.session_state.dados["conteudo"])

    with t3:
        st.header("Exportação")
        col_a, col_b = st.columns(2)
        with col_a: 
            estilo = st.selectbox("Estilo Visual", ["Moderno", "Clássico", "Dark"])
        with col_b: 
            # VOLTOU: Upload de Capa
            img = st.file_uploader("Capa do Livro", type=['jpg','png'])
            
        if st.session_state.dados["conteudo"]:
            b64 = get_image_base64(img)
            html = gerar_html_download(st.session_state.dados["tema"], st.session_state.dados["conteudo"], b64, estilo)
            st.download_button("🚀 BAIXAR ARQUIVO DE IMPRESSÃO", html, "ebook.html", "text/html")
            st.caption("Dica: Ao imprimir (Ctrl+P), defina 'Margens' como 'Nenhum'.")
