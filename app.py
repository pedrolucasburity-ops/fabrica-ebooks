import streamlit as st
import openai
import json
import base64
import markdown
import time

# --- 1. CONFIGURAÇÃO VISUAL (TELA) ---
st.set_page_config(page_title="Infinity Factory 7.1 Deluxe", layout="wide", page_icon="💎")

def carregar_css():
    st.markdown("""
    <style>
        /* Fontes Elegantes para a Interface */
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Inter:wght@400;600&display=swap');
        
        .stApp { background-color: #0E1117; font-family: 'Inter', sans-serif; }
        h1, h2, h3 { color: #FFFFFF !important; font-family: 'Cinzel', serif; letter-spacing: 1px; }
        p, label, .stMarkdown, .stTextInput label { color: #E0E0E0 !important; }
        
        .stButton > button { 
            background: linear-gradient(135deg, #d53369 0%, #c7913a 100%); 
            color: white; border: none; padding: 14px; border-radius: 8px; font-weight: bold; letter-spacing: 1px;
            width: 100%; transition: 0.4s; text-transform: uppercase;
        }
        .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(213, 51, 105, 0.4); }
        [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #222; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIN ---
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if st.session_state.authenticated: return True
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><h1 style='text-align: center;'>🔒 Factory Deluxe</h1>", unsafe_allow_html=True)
        senha = st.text_input("Senha Mestra", type="password")
        if st.button("ACESSAR"):
            if senha == "admin": 
                st.session_state.authenticated = True
                st.rerun()
            else: st.error("Negado.")
    return False

# --- 3. IA (ESCRITOR SÊNIOR) ---
def get_client(api_key):
    return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def gerar_texto_rico(client, prompt, contexto=""):
    # Mantivemos o prompt forte para garantir texto denso
    system_prompt = """
    Você é um ESCRITOR SÊNIOR de livros didáticos e técnicos.
    REGRA 1: PROFUNDIDADE. Parágrafos longos e explicativos.
    REGRA 2: Use Markdown (## para subtítulos, **negrito** para destaque).
    REGRA 3: NÃO repita o título do capítulo no início.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": f"CTX: {contexto}. TAREFA: {prompt}. Mínimo 1000 palavras."}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except: return None

def get_image_base64(image_file):
    if image_file: return base64.b64encode(image_file.getvalue()).decode()
    return None

# --- 4. GERADOR DE HTML (DIAGRAMAÇÃO DE LUXO) ---
def gerar_html_download(tema, sumario_md, conteudo_raw, img_b64, estilo):
    if not conteudo_raw: conteudo_raw = "Vazio"
    
    # 1. Prepara o Conteúdo Principal
    html_body = markdown.markdown(conteudo_raw)
    html_body = html_body.replace("<hr />", "<div class='page-break'></div>")

    # 2. Prepara a Página de Sumário (Novo!)
    html_sumario = ""
    if sumario_md:
        html_sumario = f"""
        <div class="toc-page">
            <h1 style="text-align: center; border: none; margin-bottom: 50px;">Sumário</h1>
            <div class="toc-content">
                {markdown.markdown(sumario_md)}
            </div>
        </div>
        <div class='page-break'></div>
        """

    # Estilos e Fontes
    cores = {
        "Clássico": {"h1": "#222", "acc": "#8B0000", "font": "'Merriweather', serif", "bg_capa": "#2c3e50"},
        "Moderno": {"h1": "#2c3e50", "acc": "#0056b3", "font": "'Inter', sans-serif", "bg_capa": "#34495e"},
        "Dark": {"h1": "#111", "acc": "#c0392b", "font": "Arial, sans-serif", "bg_capa": "#1a1a1a"}
    }
    c = cores.get(estilo, cores["Moderno"])
    
    # 3. Capa de Luxo (Banner Overlay)
    bg_style = f"background-image: url('data:image/jpeg;base64,{img_b64}');" if img_b64 else f"background-color: {c['bg_capa']};"
    capa = f"""
    <div class='capa-banner' style="{bg_style}">
        <div class='capa-overlay'>
            <h1 class='titulo-capa'>{tema.upper()}</h1>
            <p style='color: #eee; font-size: 14pt;'>Um guia essencial</p>
        </div>
    </div>
    <div class='page-break'></div>
    """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        /* --- FONTES DE IMPRESSÃO --- */
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;700&family=Inter:wght@400;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap'); /* Fonte da Capa */

        /* --- CONFIGURAÇÃO DA PÁGINA --- */
        @page {{
            size: A4;
            margin: 2.5cm; /* Margem de segurança */
            /* Configuração para rodapé automático do navegador ficar bonito */
            @bottom-center {{ content: counter(page); font-family: sans-serif; font-size: 9pt; color: #999; }}
        }}

        body {{
            font-family: {c['font']}; font-size: 12pt; line-height: 1.8;
            color: #222; background: white; text-align: justify;
        }}

        /* --- TIPOGRAFIA --- */
        h1 {{ font-size: 24pt; color: {c['h1']}; border-bottom: 3px solid {c['acc']}; padding-bottom: 10px; margin-top: 1em; margin-bottom: 30px; page-break-after: avoid; }}
        h2 {{ font-size: 16pt; color: {c['acc']}; margin-top: 35px; margin-bottom: 15px; font-weight: bold; page-break-after: avoid; }}
        h3 {{ font-size: 14pt; font-weight: bold; margin-top: 25px; page-break-after: avoid; }}

        /* --- RECUO DE PARÁGRAFO (O pedido especial!) --- */
        p {{ 
            text-indent: 2em; /* Recuo padrão */
            margin-bottom: 10px; margin-top: 0;
        }}
        /* Regra de ouro: O primeiro parágrafo depois de um título NÃO tem recuo */
        h1 + p, h2 + p, h3 + p {{ text-indent: 0; }}

        /* --- LISTAS (Formatadas para não parecer "bloco") --- */
        ul, ol {{ margin-top: 15px; margin-bottom: 25px; padding-left: 30px; }}
        li {{ margin-bottom: 10px; padding-left: 5px; }}
        li p {{ text-indent: 0; margin-bottom: 0; }} /* Parágrafos dentro de listas não têm recuo */

        /* --- CAPA DE LUXO --- */
        .capa-banner {{
            height: 100%; min-height: 900px; /* Ocupa a folha toda */
            background-size: cover; background-position: center;
            display: flex; align-items: flex-end; /* Texto embaixo */
            page-break-after: always;
             /* Tira a margem da página só para a capa */
            margin-top: -2.5cm; margin-left: -2.5cm; margin-right: -2.5cm;
        }}
        .capa-overlay {{
            background: linear-gradient(to top, rgba(0,0,0,0.9), rgba(0,0,0,0.2));
            width: 100%; padding: 60px 40px; text-align: center; color: white;
        }}
        .titulo-capa {{
            font-family: 'Cinzel', serif; font-size: 42pt; color: white !important;
            border: none !important; margin: 0 !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}

        /* --- PÁGINA DE SUMÁRIO --- */
        .toc-page {{ padding: 20px 0; }}
        .toc-content ul {{ list-style-type: none; padding-left: 0; }}
        .toc-content li {{ 
            border-bottom: 1px dotted #ccc; 
            padding: 10px 0; font-weight: 600; color: {c['acc']};
            font-size: 14pt;
        }}

        /* --- UTILITÁRIOS --- */
        .page-break {{ page-break-after: always; }}
        img {{ max-width: 100%; border-radius: 4px; }}
        
        @media print {{
            body {{ background: white; }}
            h1, h2, h3 {{ page-break-after: avoid; }}
            /* Garante que o navegador imprima as cores de fundo da capa */
            * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
        }}
    </style>
    </head>
    <body>
        {capa}
        {html_sumario}
        {html_body}
        <div style="position: fixed; bottom: 0; width: 100%; text-align: center; font-size: 9pt; color: #aaa; padding-bottom: 10px; background: white;">
            {tema} | Edição Exclusiva
        </div>
    </body>
    </html>
    """

# --- INICIALIZAÇÃO ---
if "dados" not in st.session_state: st.session_state.dados = {"tema": "", "publico": "", "sumario": "", "conteudo": ""}
carregar_css()

# --- APP ---
if check_password():
    st.sidebar.title("💎 Factory 7.1 Deluxe")
    api_key = st.sidebar.text_input("API Key Groq", type="password")
    
    with st.sidebar.expander("💾 Sistema de Backup"):
        st.download_button("BAIXAR PROJETO (.json)", json.dumps(st.session_state.dados), "projeto_deluxe.json")
        f = st.file_uploader("CARREGAR PROJETO", type=["json"])
        if f: 
            st.session_state.dados = json.load(f)
            st.success("Projeto Carregado!"); time.sleep(1); st.rerun()

    if not api_key: st.stop()
    client = get_client(api_key)

    t1, t2, t3 = st.tabs(["1. PLANEJAMENTO", "2. PRODUÇÃO", "3. DIAGRAMAÇÃO"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.dados["tema"] = st.text_input("Tema", value=st.session_state.dados["tema"])
            st.session_state.dados["publico"] = st.text_input("Público", value=st.session_state.dados["publico"])
        with c2:
            if st.button("✨ Gerar Sumário"):
                prompt = f"Crie sumário DETALHADO e criativo para livro '{st.session_state.dados['tema']}' (Público: {st.session_state.dados['publico']}). 5 a 7 capítulos."
                st.session_state.dados["sumario"] = gerar_texto_rico(client, prompt)
                st.rerun()
        if st.session_state.dados["sumario"]: 
            st.markdown("### 📋 Sumário Gerado:")
            st.markdown(st.session_state.dados["sumario"])

    with t2:
        if st.button("🔥 ESCREVER LIVRO COMPLETO (Modo Profundo)"):
            if not st.session_state.dados["sumario"]: st.error("Falta sumário")
            else:
                bar = st.progress(0)
                st.session_state.dados["conteudo"] = ""
                ctx = f"Livro: {st.session_state.dados['tema']}. Público: {st.session_state.dados['publico']}."
                # Dividindo o sumário em linhas para tentar guiar a IA
                capitulos = [line for line in st.session_state.dados["sumario"].split('\n') if line.strip() and any(char.isdigit() for char in line)]
                total_caps = len(capitulos) if capitulos else 5

                for i in range(1, total_caps + 1):
                    prompt = f"Escreva o CAPÍTULO {i}. Baseado no sumário. Explique os conceitos profundamente antes de listar tópicos. Use subtítulos ##."
                    txt = gerar_texto_rico(client, prompt, ctx)
                    if txt: st.session_state.dados["conteudo"] += f"# Capítulo {i}\n\n{txt}\n\n---\n"
                    bar.progress(i/total_caps)
                st.success("Texto Gerado com Sucesso!")
                st.rerun()
        if st.session_state.dados["conteudo"]: 
            with st.expander("Ver Texto Bruto"):
                st.markdown(st.session_state.dados["conteudo"])

    with t3:
        st.header("Finalização")
        c_a, c_b = st.columns(2)
        with c_a: estilo = st.selectbox("Estilo de Diagramação", ["Moderno", "Clássico", "Dark"])
        with c_b: img = st.file_uploader("Imagem da Capa (Alta Resolução)", type=['jpg','png'])
        
        if st.session_state.dados["conteudo"]:
            b64 = get_image_base64(img)
            # Passamos o sumário também para a função de gerar HTML
            html = gerar_html_download(st.session_state.dados["tema"], st.session_state.dados["sumario"], st.session_state.dados["conteudo"], b64, estilo)
            st.download_button("💎 BAIXAR E-BOOK DIAGRAMADO (HTML)", html, "ebook_deluxe.html", "text/html")
            st.info("👆 Dica: Na hora de imprimir (Ctrl+P), ative 'Cabeçalhos e Rodapés' para ver os números das páginas.")
