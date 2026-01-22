import streamlit as st
import openai
import json
import base64
import time

# --- CONFIGURAÇÃO VISUAL (CSS TELA) ---
st.set_page_config(page_title="Infinity Factory 6.1", layout="wide", page_icon="✨")

def carregar_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        .stApp { background-color: #0E1117; font-family: 'Inter', sans-serif; }
        h1, h2, h3 { color: #FFFFFF !important; font-weight: 700; }
        p, label, .stMarkdown { color: #E0E0E0 !important; }
        .stTextInput > div > div > input { background-color: #262730; color: white; border-radius: 10px; border: 1px solid #4A4A4A; }
        .stButton > button { background: linear-gradient(90deg, #FF4B4B 0%, #FF914D 100%); color: white; border: none; padding: 12px 24px; border-radius: 12px; font-weight: 600; width: 100%; transition: all 0.3s ease; }
        .stButton > button:hover { transform: scale(1.02); }
        [data-testid="stSidebar"] { background-color: #1A1C24; border-right: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES ---
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if st.session_state.authenticated: return True
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🔒 Acesso Restrito</h1>", unsafe_allow_html=True)
        st.text_input("Senha", type="password", key="senha_input", on_change=autenticar)
        if st.button("ENTRAR"): autenticar()
    return False

def autenticar():
    if st.session_state.senha_input == "admin": # SENHA AQUI
        st.session_state.authenticated = True
    else: st.error("Senha incorreta.")

def get_client(api_key):
    return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def gerar_texto_rico(client, prompt, contexto=""):
    prompt_sistema = "Você é um Autor Best-Seller e Especialista Técnico. Escreva conteúdo denso, rico e didático. NUNCA superficial. Use exemplos e tom de autoridade. Formate em Markdown (h1, h2, negrito)."
    prompt_usuario = f"CONTEXTO: {contexto}\nTAREFA: {prompt}\nREGRAS: Mínimo 800 palavras. Aprofunde nos porquês. Conteúdo pronto para publicação."
    try:
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": prompt_sistema}, {"role": "user", "content": prompt_usuario}], temperature=0.6)
        return response.choices[0].message.content
    except Exception as e: return None

def get_image_base64(image_file):
    if image_file is not None: return base64.b64encode(image_file.getvalue()).decode()
    return None

# --- CORREÇÃO CRÍTICA: GERADOR DE HTML/PDF ---
def gerar_html_download(tema, conteudo, img_b64, estilo):
    if not conteudo: conteudo = "<p>Conteúdo vazio.</p>"
    
    # Tratamento melhor do Markdown para HTML
    conteudo_html = conteudo\
        .replace("# ", "<h1 class='main-title'>")\
        .replace("## ", "<h2 class='sub-title'>")\
        .replace("### ", "<h3 class='section-title'>")\
        .replace("---", "<hr class='divisor'>")\
        .replace("**", "<strong>")\
        .replace("\n", "<br>")

    # Definição de Cores e Fontes
    cores = {
        "Clássico": {"h1": "#2c3e50", "accent": "#e67e22", "font": "'Merriweather', Georgia, serif"},
        "Moderno": {"h1": "#111", "accent": "#007BFF", "font": "'Inter', Helvetica, Arial, sans-serif"},
        "Dark": {"h1": "#ffffff", "accent": "#FF4B4B", "font": "'Inter', Helvetica, Arial, sans-serif"}
    }
    c = cores.get(estilo, cores["Moderno"])
    cor_titulo_impressao = c['h1'] if estilo != "Dark" else "#222" # Evita título branco no papel branco

    capa = f"<div class='capa_container'><img src='data:image/jpeg;base64,{img_b64}' class='capa_img'><h1 class='titulo_capa' style='color:{c['h1']}'>{tema.upper()}</h1></div><div class='page-break'></div>" if img_b64 else ""

    html_final = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
    <meta charset="UTF-8">
    <title>{tema}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Merriweather:wght@300;700&display=swap" rel="stylesheet">
    <style>
        /* --- ESTILOS GERAIS (Base) --- */
        body {{ font-family: {c['font']}; line-height: 1.8; margin: 0; padding: 0; }}
        
        /* Títulos */
        h1.main-title {{ font-size: 24pt; font-weight: 700; margin-top: 2em; margin-bottom: 1em; padding-bottom: 0.5em; page-break-after: avoid; }}
        h2.sub-title {{ font-size: 18pt; font-weight: 600; margin-top: 1.5em; page-break-after: avoid; }}
        h3.section-title {{ font-size: 14pt; font-weight: 600; margin-top: 1.5em; }}
        
        /* Texto e Listas */
        p, li {{ font-size: 12pt; text-align: justify; margin-bottom: 1.2em; }}
        ul, ol {{ margin-left: 1.5em; margin-bottom: 1.5em; }}
        hr.divisor {{ border: 0; border-top: 1px solid #eee; margin: 3em 0; }}

        /* Capa */
        .capa_container {{ text-align: center; padding: 4cm 2cm; height: 80vh; display: flex; flex-direction: column; justify-content: center; align-items: center; }}
        .capa_img {{ max-width: 80%; max-height: 60vh; box-shadow: 0 10px 20px rgba(0,0,0,0.2); border-radius: 8px; }}
        .titulo_capa {{ font-size: 36pt !important; margin-top: 1em !important; border: none !important; }}
        .page-break {{ page-break-after: always; }}

        /* --- VISUALIZAÇÃO NA TELA (CSS que você vê ao abrir o HTML) --- */
        @media screen {{
            body {{ background-color: #f4f4f9; color: #333; padding: 40px; }}
            .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 50px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border-radius: 12px; }}
            h1.main-title {{ color: {c['h1']}; border-bottom: 3px solid {c['accent']}; }}
            h2.sub-title {{ color: {c['accent']}; }}
            /* Se for Dark mode na tela, inverte as cores do container */
            {f".container {{ background: #1E1E1E; color: #E0E0E0; }}" if estilo == "Dark" else ""}
        }}

        /* --- IMPRESSÃO/PDF (CSS Crítico para ficar bonito no papel) --- */
        @media print {{
            @page {{ margin: 2.5cm; size: A4; }}
            body {{ background-color: white !important; color: black !important; font-size: 12pt !important; padding: 0 !important; margin: 0 !important; }}
            .container {{ width: 100% !important; margin: 0 !important; padding: 0 !important; box-shadow: none !important; border-radius: 0 !important; }}
            /* Cores de impressão (Sempre fundo branco) */
            h1.main-title {{ color: {cor_titulo_impressao} !important; border-bottom: 2px solid {c['accent']} !important; }}
            h2.sub-title {{ color: {c['accent']} !important; }}
            .titulo_capa {{ color: {cor_titulo_impressao} !important; }}
            .capa_container {{ height: auto !important; padding: 2cm 0 !important; display: block; }}
            .capa_img {{ box-shadow: none !important; max-height: 500px; }}
            /* Evita quebras ruins */
            h1, h2, h3 {{ page-break-after: avoid; }}
            p, li {{ page-break-inside: avoid; }}
        }}
    </style>
    </head>
    <body>
        <div class="container">
            {capa}
            {conteudo_html}
        </div>
    </body>
    </html>
    """
    return html_final

# --- INICIALIZAÇÃO ---
if "dados" not in st.session_state: st.session_state.dados = {"tema": "", "publico": "", "sumario": "", "conteudo": "", "prompt_capa": ""}
carregar_css()

# --- FLUXO PRINCIPAL ---
if check_password():
    st.sidebar.title("🚀 Painel de Controle")
    api_key = st.sidebar.text_input("Chave API Groq", type="password")
    with st.sidebar.expander("💾 Backup & Salvar"):
        st.download_button("Baixar Progresso (.json)", data=json.dumps(st.session_state.dados), file_name="backup.json", mime="application/json")
        uploaded_file = st.file_uploader("Carregar Progresso", type=["json"])
        if uploaded_file:
            st.session_state.dados = json.load(uploaded_file)
            st.rerun()
    if not api_key:
        st.warning("⚠️ Digite a chave API na barra lateral.")
        st.stop()
    client = get_client(api_key)

    t1, t2, t3 = st.tabs(["📝 1. Planejamento", "⚙️ 2. Fábrica de Texto", "📦 3. Entrega"])
    with t1:
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.dados["tema"] = st.text_input("Tema Principal", value=st.session_state.dados["tema"])
            st.session_state.dados["publico"] = st.text_input("Público Alvo", value=st.session_state.dados["publico"])
        with col2:
            if st.button("✨ Criar Estrutura (Sumário)"):
                prompt = f"Crie um sumário matador para um livro sobre '{st.session_state.dados['tema']}'. Foco: {st.session_state.dados['publico']}. 6 Capítulos com nomes criativos."
                st.session_state.dados["sumario"] = gerar_texto_rico(client, prompt)
                st.rerun()
        if st.session_state.dados["sumario"]: st.markdown(st.session_state.dados["sumario"])
    with t2:
        st.markdown("*IA configurada para textos profundos.*")
        if st.button("🔥 Escrever Livro Completo (Modo Profundo)"):
            if not st.session_state.dados["sumario"]: st.error("Precisa do sumário antes!")
            else:
                barra = st.progress(0)
                st.session_state.dados["conteudo"] = ""
                contexto = f"Livro: {st.session_state.dados['tema']}. Público: {st.session_state.dados['publico']}. Sumário: {st.session_state.dados['sumario']}"
                for i in range(1, 7):
                    with st.spinner(f"Escrevendo Capítulo {i} com profundidade..."):
                        prompt_cap = f"Escreva o CAPÍTULO {i} completo. Seja extenso, use exemplos, listas e tom profissional. Mínimo 800 palavras. Use Markdown (h1, h2, negrito)."
                        texto = gerar_texto_rico(client, prompt_cap, contexto)
                        if texto: st.session_state.dados["conteudo"] += f"# Capítulo {i}\n\n{texto}\n\n---\n"
                        barra.progress(i/6)
                st.success("Livro finalizado!")
                st.rerun()
        if st.session_state.dados["conteudo"]:
            with st.expander("📖 Ler Rascunho"): st.markdown(st.session_state.dados["conteudo"])
    with t3:
        col_a, col_b = st.columns(2)
        with col_a: estilo = st.selectbox("Estilo Visual", ["Moderno", "Clássico", "Dark"])
        with col_b: capa_img = st.file_uploader("Capa do Livro", type=['jpg', 'png'])
        if st.session_state.dados["conteudo"]:
            b64 = get_image_base64(capa_img)
            html = gerar_html_download(st.session_state.dados["tema"], st.session_state.dados["conteudo"], b64, estilo)
            st.download_button("🚀 BAIXAR E-BOOK PRONTO", data=html, file_name=f"{st.session_state.dados['tema']}.html", mime="text/html")
            st.caption("Abra o arquivo e salve como PDF (Ctrl+P). A formatação estará correta agora.")
