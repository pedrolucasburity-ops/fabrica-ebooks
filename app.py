import streamlit as st
import openai
import json
import base64
import time

# --- CONFIGURAÇÃO VISUAL (CSS INJETADO) ---
st.set_page_config(page_title="Infinity Factory 6.0", layout="wide", page_icon="✨")

def carregar_css():
    st.markdown("""
    <style>
        /* Importando Fonte Google */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        /* Fundo e Texto Geral */
        .stApp {
            background-color: #0E1117; /* Fundo Escuro Moderno */
            font-family: 'Inter', sans-serif;
        }
        
        h1, h2, h3 {
            color: #FFFFFF !important;
            font-weight: 700;
        }
        
        p, label, .stMarkdown {
            color: #E0E0E0 !important;
        }

        /* Inputs de Texto */
        .stTextInput > div > div > input {
            background-color: #262730;
            color: white;
            border-radius: 10px;
            border: 1px solid #4A4A4A;
        }

        /* Botão Primário (Gerar) */
        .stButton > button {
            background: linear-gradient(90deg, #FF4B4B 0%, #FF914D 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4);
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #1A1C24;
            border-right: 1px solid #333;
        }
        
        /* Containers de Sucesso/Aviso */
        .stSuccess, .stInfo, .stWarning {
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE LÓGICA ---
def check_password():
    """Retorna True se o usuário estiver logado"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # Tela de Login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔒 Acesso Restrito</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Entre com suas credenciais para acessar a Fábrica.</p>", unsafe_allow_html=True)
        senha = st.text_input("Senha de Acesso", type="password")
        
        if st.button("ENTRAR NO SISTEMA"):
            if senha == "admin": # <--- MUDE SUA SENHA AQUI
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    return False

def get_client(api_key):
    return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def gerar_texto_rico(client, prompt, contexto=""):
    """
    Função aprimorada para gerar texto profundo e não superficial.
    """
    prompt_sistema = """
    Você é um Autor Best-Seller e Especialista Técnico de alto nível.
    Seu objetivo é escrever conteúdo denso, rico e extremamente didático.
    NUNCA seja superficial. Use exemplos, analogias, listas e tom de autoridade.
    Formate sempre em Markdown (Use h2 para títulos, negrito para ênfase).
    """
    
    prompt_usuario = f"""
    CONTEXTO DO LIVRO: {contexto}
    
    SUA TAREFA AGORA: {prompt}
    
    REGRAS OBRIGATÓRIAS:
    1. Escreva no mínimo 800 palavras.
    2. Aprofunde nos "porquês" e "comos".
    3. Não faça resumos, escreva o conteúdo final pronto para publicação.
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.6 # Temperatura menor para ser mais focado/menos aleatório
        )
        return response.choices[0].message.content
    except Exception as e:
        return None

def get_image_base64(image_file):
    if image_file is not None:
        return base64.b64encode(image_file.getvalue()).decode()
    return None

def gerar_html_download(tema, conteudo, img_b64, estilo):
    # Lógica de HTML Premium
    if not conteudo: conteudo = "<p>Conteúdo vazio.</p>"
    conteudo_html = conteudo.replace("\n", "<br>").replace("# ", "<h1>").replace("## ", "<h2>").replace("### ", "<h3>").replace("---", "<hr>")
    
    cores = {
        "Clássico": {"h1": "#333", "accent": "#000", "font": "Georgia, serif", "bg": "#fff"},
        "Moderno": {"h1": "#2c3e50", "accent": "#3498db", "font": "'Helvetica Neue', Arial, sans-serif", "bg": "#f9f9f9"},
        "Dark": {"h1": "#ecf0f1", "accent": "#e74c3c", "font": "Verdana, sans-serif", "bg": "#2c3e50"}
    }
    c = cores.get(estilo, cores["Moderno"])
    
    cor_texto = "#ecf0f1" if estilo == "Dark" else "#333"
    
    capa = f"<div class='capa'><img src='data:image/jpeg;base64,{img_b64}'><h1 style='color:{c['h1']}'>{tema.upper()}</h1></div><div class='page-break'></div>" if img_b64 else ""
    
    return f"""
    <html>
    <head>
    <style>
        body {{ font-family: {c['font']}; color: {cor_texto}; background: {c['bg']}; max-width: 800px; margin: 0 auto; padding: 40px; line-height: 1.8; }}
        h1 {{ color: {c['h1']}; border-bottom: 3px solid {c['accent']}; padding-bottom: 10px; }}
        h2 {{ color: {c['accent']}; margin-top: 40px; font-size: 1.5em; }}
        p {{ margin-bottom: 20px; text-align: justify; }}
        .capa {{ text-align: center; margin-bottom: 100px; }}
        .capa img {{ max-width: 100%; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        .page-break {{ page-break-after: always; }}
    </style>
    </head>
    <body>{capa}{conteudo_html}</body></html>
    """

# --- INICIALIZAÇÃO ---
if "dados" not in st.session_state:
    st.session_state.dados = {"tema": "", "publico": "", "sumario": "", "conteudo": "", "prompt_capa": ""}

carregar_css()

# --- FLUXO PRINCIPAL ---
if check_password():
    # Só mostra o app se a senha estiver certa
    st.sidebar.title("🚀 Painel de Controle")
    st.sidebar.markdown("---")
    
    api_key = st.sidebar.text_input("Chave API Groq", type="password")
    
    # Menu de Backup (Ainda necessário até conectarmos Banco de Dados)
    with st.sidebar.expander("💾 Backup & Salvar"):
        st.download_button("Baixar Progresso (.json)", data=json.dumps(st.session_state.dados), file_name="backup.json", mime="application/json")
        uploaded_file = st.file_uploader("Carregar Progresso", type=["json"])
        if uploaded_file:
            st.session_state.dados = json.load(uploaded_file)
            st.success("Carregado!")
            st.rerun()

    if not api_key:
        st.warning("⚠️ Digite a chave API na barra lateral para ativar a IA.")
        st.stop()
    
    client = get_client(api_key)

    # TABS VISUAIS
    t1, t2, t3 = st.tabs(["📝 1. Planejamento", "⚙️ 2. Fábrica de Texto", "📦 3. Entrega"])

    with t1:
        st.header("Definição do Produto")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.dados["tema"] = st.text_input("Tema Principal", value=st.session_state.dados["tema"])
            st.session_state.dados["publico"] = st.text_input("Público Alvo", value=st.session_state.dados["publico"])
        with col2:
            st.info("Dica: Quanto mais específico o público, melhor o texto.")
            if st.button("✨ Criar Estrutura (Sumário)"):
                prompt = f"Crie um sumário matador para um livro sobre '{st.session_state.dados['tema']}'. Foco: {st.session_state.dados['publico']}. 6 Capítulos com nomes criativos."
                st.session_state.dados["sumario"] = gerar_texto_rico(client, prompt)
                st.rerun()
        
        if st.session_state.dados["sumario"]:
            st.markdown("### 📋 Estrutura Aprovada:")
            st.markdown(st.session_state.dados["sumario"])

    with t2:
        st.header("Produção de Conteúdo")
        st.markdown("*A IA agora está configurada para escrever textos profundos e técnicos.*")
        
        if st.button("🔥 Escrever Livro Completo (Modo Profundo)"):
            if not st.session_state.dados["sumario"]:
                st.error("Precisa do sumário antes!")
            else:
                barra = st.progress(0)
                st.session_state.dados["conteudo"] = ""
                contexto = f"Livro: {st.session_state.dados['tema']}. Público: {st.session_state.dados['publico']}. Sumário: {st.session_state.dados['sumario']}"
                
                # Loop para escrever
                for i in range(1, 7):
                    with st.spinner(f"Escrevendo Capítulo {i} com profundidade..."):
                        prompt_cap = f"Escreva o CAPÍTULO {i} completo. Seja extenso, use exemplos, listas e tom profissional. Mínimo 800 palavras."
                        texto = gerar_texto_rico(client, prompt_cap, contexto)
                        if texto:
                            st.session_state.dados["conteudo"] += f"<h1>Capítulo {i}</h1>{texto}<hr>"
                        barra.progress(i/6)
                st.success("Livro finalizado com sucesso!")
                st.rerun()

        if st.session_state.dados["conteudo"]:
            with st.expander("📖 Ler Rascunho"):
                st.markdown(st.session_state.dados["conteudo"], unsafe_allow_html=True)

    with t3:
        st.header("Exportação Final")
        col_a, col_b = st.columns(2)
        with col_a:
            estilo = st.selectbox("Estilo Visual", ["Moderno", "Clássico", "Dark"])
        with col_b:
            capa_img = st.file_uploader("Capa do Livro", type=['jpg', 'png'])
        
        if st.session_state.dados["conteudo"]:
            b64 = get_image_base64(capa_img)
            html = gerar_html_download(st.session_state.dados["tema"], st.session_state.dados["conteudo"], b64, estilo)
            st.download_button(
                label="🚀 BAIXAR E-BOOK PRONTO",
                data=html,
                file_name=f"{st.session_state.dados['tema']}.html",
                mime="text/html"
            )
            st.caption("Abra o arquivo e salve como PDF (Ctrl+P).")
