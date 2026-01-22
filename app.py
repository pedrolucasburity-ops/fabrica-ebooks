import streamlit as st
import openai
import json
import base64
import markdown
import time
import re # Biblioteca para encontrar os titulos no texto

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Infinity Factory 7.2", layout="wide", page_icon="💎")

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
        st.markdown("<br><h1 style='text-align: center;'>🔒 Factory 7.2</h1>", unsafe_allow_html=True)
        senha = st.text_input("Senha", type="password")
        if st.button("ACESSAR"):
            if senha == "admin": 
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Erro.")
    return False

# --- 3. IA ---
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

# --- 4. FUNÇÃO NOVA: EXTRAIR SUMÁRIO DO TEXTO ---
def extrair_topicos(conteudo_markdown):
    """Lê o texto inteiro e encontra # Titulos e ## Subtitulos"""
    linhas = conteudo_markdown.split('\n')
    sumario = []
    
    capitulo_num = 1
    
    for linha in linhas:
        # Encontra Títulos Principais (#)
        if linha.startswith('# '):
            titulo_limpo = linha.replace('# ', '').replace('*', '').strip()
            # Adiciona na lista: (Nivel 1, Texto)
            sumario.append((1, f"Capítulo {capitulo_num}: {titulo_limpo}"))
            capitulo_num += 1
            
        # Encontra Subtítulos (##)
        elif linha.startswith('## '):
            subtitulo_limpo = linha.replace('## ', '').replace('*', '').strip()
            # Adiciona na lista: (Nivel 2, Texto)
            sumario.append((2, subtitulo_limpo))
            
    return sumario

# --- 5. GERADOR DE HTML ---
def gerar_html_download(tema, conteudo_raw, img_b64, estilo):
    if not conteudo_raw: conteudo_raw = "Vazio"
    
    # GERA O SUMÁRIO AUTOMÁTICO HTML
    lista_topicos = extrair_topicos(conteudo_raw)
    html_sumario_itens = ""
    
    for nivel, texto in lista_topicos:
        if nivel == 1:
            # Título Principal (Negrito, margem maior)
            html_sumario_itens += f"""
            <div class="toc-item main">
                <span class="toc-text">{texto}</span>
                <span class="toc-dots"></span>
            </div>"""
        else:
            # Subtítulo (Indentado)
            html_sumario_itens += f"""
            <div class="toc-item sub">
                <span class="toc-text">{texto}</span>
                <span class="toc-dots"></span>
            </div>"""

    # HTML DO CONTEÚDO
    html_body = markdown.markdown(conteudo_raw)
    html_body = html_body.replace("<hr />", "<div class='page-break'></div>")

    # CORES E ESTILOS
    cores = {
        "Clássico": {"h1": "#000", "acc": "#800000", "font": "'Merriweather', serif", "bg": "#fff"},
        "Moderno": {"h1": "#2c3e50", "acc": "#2980b9", "font": "'Inter', sans-serif", "bg": "#fff"},
        "Dark": {"h1": "#111", "acc": "#c0392b", "font": "Arial, sans-serif", "bg": "#fff"}
    }
    c = cores.get(estilo, cores["Moderno"])
    
    # CAPA CORRIGIDA (Sem margens negativas que cortam texto)
    capa = ""
    if img_b64:
        capa = f"""
        <div class='capa-page'>
            <div class='capa-img-container' style="background-image: url('data:image/jpeg;base64,{img_b64}');">
                <div class='capa-overlay'>
                    <h1 class='titulo-capa'>{tema.upper()}</h1>
                </div>
            </div>
        </div>
        <div class='page-break'></div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;700&family=Inter:wght@400;600&family=Cinzel:wght@700&display=swap');

        @page {{
            size: A4;
            margin: 2.5cm; /* Margem segura para não cortar texto */
            @bottom-center {{ 
                content: counter(page); 
                font-family: sans-serif; font-size: 9pt; color: #555;
            }}
        }}

        body {{
            font-family: {c['font']}; font-size: 12pt; line-height: 1.6;
            color: #222; background: white; text-align: justify;
            margin: 0; padding: 0;
        }}

        /* CAPA NOVA (Mais segura para impressão) */
        .capa-page {{
            /* Hack para ocupar a página toda removendo a margem do @page só aqui */
            margin: -2.5cm; 
            width: 210mm; height: 297mm; 
            overflow: hidden;
            page-break-after: always;
        }}
        .capa-img-container {{
            width: 100%; height: 100%;
            background-size: cover; background-position: center;
            display: flex; align-items: flex-end;
        }}
        .capa-overlay {{
            background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
            width: 100%; padding: 3cm 1cm 2cm 1cm;
            text-align: center;
        }}
        .titulo-capa {{
            font-family: 'Cinzel', serif; font-size: 36pt; color: white !important;
            margin: 0; padding: 0; border: none !important;
            text-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }}

        /* SUMÁRIO ESTILO LIVRO */
        .toc-page {{ margin-top: 2cm; margin-bottom: 2cm; }}
        .toc-title {{ text-align: center; font-family: 'Cinzel', serif; margin-bottom: 40px; border-bottom: 2px solid #ccc; padding-bottom: 10px; }}
        
        .toc-item {{ display: flex; align-items: baseline; margin-bottom: 8px; }}
        .toc-item.main {{ font-weight: bold; margin-top: 15px; font-size: 13pt; color: {c['acc']}; }}
        .toc-item.sub {{ margin-left: 20px; font-size: 11pt; color: #555; }}
        
        .toc-text {{ flex-shrink: 0; max-width: 80%; }}
        .toc-dots {{ 
            flex-grow: 1; 
            border-bottom: 1px dotted #999; 
            margin: 0 5px; 
            position: relative; top: -5px; 
        }}

        /* CONTEÚDO */
        h1 {{ font-size: 22pt; color: {c['h1']}; border-bottom: 3px solid {c['acc']}; margin-top: 0; padding-bottom: 10px; page-break-after: avoid; }}
        h2 {{ font-size: 16pt; color: {c['acc']}; margin-top: 30px; margin-bottom: 15px; font-weight: bold; page-break-after: avoid; }}
        
        /* RECUO DE PARÁGRAFO (Lógica Inteligente) */
        p {{ text-indent: 1.5cm; margin-bottom: 10px; margin-top: 0; }}
        h1 + p, h2 + p {{ text-indent: 0; }}
        li p {{ text-indent: 0; }}

        /* LISTAS */
        ul, ol {{ margin-left: 0; padding-left: 1.5cm; margin-bottom: 20px; }}
        li {{ margin-bottom: 5px; }}

        @media print {{
            body {{ background: white; }}
            .capa-page {{ -webkit-print-color-adjust: exact; }}
        }}
    </style>
    </head>
    <body>
        {capa}
        
        <div class="toc-page">
            <h1 class="toc-title">SUMÁRIO</h1>
            {html_sumario_itens}
        </div>
        <div class="page-break"></div>

        {html_body}
    </body>
    </html>
    """

# --- APP ---
if check_password():
    st.sidebar.title("💎 Factory 7.2")
    api_key = st.sidebar.text_input("API Key Groq", type="password")
    if "dados" not in st.session_state: st.session_state.dados = {"tema": "", "sumario": "", "conteudo": ""}
    
    with st.sidebar.expander("💾 Backup"):
        st.download_button("Salvar", json.dumps(st.session_state.dados), "backup.json")
        f = st.file_uploader("Carregar", type=["json"])
        if f: st.session_state.dados = json.load(f); st.rerun()

    if not api_key: st.stop()
    client = get_client(api_key)

    t1, t2, t3 = st.tabs(["1. Planejar", "2. Escrever", "3. Diagramar"])
    
    with t1:
        tema = st.text_input("Tema", value=st.session_state.dados["tema"])
        st.session_state.dados["tema"] = tema
        if st.button("Gerar Plano"):
            # AQUI PEDIMOS PARA A IA APENAS CRIAR A LISTA, O SUMÁRIO FINAL É GERADO NA EXPORTAÇÃO
            st.session_state.dados["sumario"] = gerar_texto_rico(client, f"Crie um plano de tópicos para livro sobre {tema}. Liste 5 capítulos.", "")
            st.rerun()
        if st.session_state.dados["sumario"]: st.write(st.session_state.dados["sumario"])

    with t2:
        if st.button("🔥 Escrever Livro"):
            bar = st.progress(0)
            st.session_state.dados["conteudo"] = ""
            for i in range(1, 6):
                # Prompt instruindo IA a usar ## para subtopicos que aparecerão no sumario
                prompt = f"Escreva o CAPÍTULO {i}. Use ## para subtítulos importantes. Não repita o titulo do capitulo."
                txt = gerar_texto_rico(client, prompt, f"Livro: {st.session_state.dados['tema']}")
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
