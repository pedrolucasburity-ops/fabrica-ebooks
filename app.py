import streamlit as st
import openai
import markdown
from xhtml2pdf import pisa
import io
import base64
import sqlite3
import json
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Fábrica Enterprise 5.0", layout="wide", page_icon="🏢")

# --- BANCO DE DADOS (SQLITE) ---
def init_db():
    conn = sqlite3.connect('meus_projetos.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projetos
                 (nome TEXT PRIMARY KEY, dados TEXT)''')
    conn.commit()
    conn.close()

def salvar_projeto_db(nome, dados):
    conn = sqlite3.connect('meus_projetos.db')
    c = conn.cursor()
    # Converte o dicionário de sessão em texto JSON para salvar
    dados_json = json.dumps(dados)
    c.execute("INSERT OR REPLACE INTO projetos (nome, dados) VALUES (?, ?)", (nome, dados_json))
    conn.commit()
    conn.close()

def carregar_projeto_db(nome):
    conn = sqlite3.connect('meus_projetos.db')
    c = conn.cursor()
    c.execute("SELECT dados FROM projetos WHERE nome=?", (nome,))
    data = c.fetchone()
    conn.close()
    if data:
        return json.loads(data[0])
    return None

def listar_projetos_db():
    conn = sqlite3.connect('meus_projetos.db')
    c = conn.cursor()
    c.execute("SELECT nome FROM projetos")
    projetos = [row[0] for row in c.fetchall()]
    conn.close()
    return projetos

# Inicializa o DB ao abrir
init_db()

# --- FUNÇÕES DE IA ---
def get_client(api_key):
    return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def gerar_texto(client, prompt, model="llama-3.3-70b-versatile"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return None

def get_image_base64(image_file):
    if image_file is not None:
        return base64.b64encode(image_file.getvalue()).decode()
    return None

# --- GERADOR DE PDF COM TEMPLATES (DESIGN) ---
def converter_markdown_para_pdf(texto_markdown, imagem_capa_base64=None, estilo="Clássico"):
    html_content = markdown.markdown(texto_markdown)
    
    # Cores baseadas no estilo
    cor_titulo = "#2c3e50"
    cor_subtitulo = "#e67e22"
    fonte = "Helvetica, Arial, sans-serif"
    
    if estilo == "Executivo (Azul)":
        cor_titulo = "#003366"
        cor_subtitulo = "#0066cc"
        fonte = "Times New Roman, serif"
    elif estilo == "Criativo (Roxo)":
        cor_titulo = "#4b0082"
        cor_subtitulo = "#8a2be2"
        fonte = "Verdana, sans-serif"

    html_capa = ""
    if imagem_capa_base64:
        html_capa = f"""
        <div style="text-align: center; page-break-after: always; padding-top: 50px;">
            <img src="data:image/jpeg;base64,{imagem_capa_base64}" style="width: 100%; max-height: 700px; object-fit: contain;">
        </div>
        """
    
    html_final = f"""
    <html>
    <head>
    <style>
        @page {{ size: A4; margin: 2.5cm; }}
        body {{ font-family: {fonte}; line-height: 1.6; color: #333; }}
        h1 {{ color: {cor_titulo}; border-bottom: 2px solid #eee; padding-bottom: 10px; text-transform: uppercase; }}
        h2 {{ color: {cor_subtitulo}; margin-top: 30px; border-left: 5px solid {cor_subtitulo}; padding-left: 10px; }}
        p {{ margin-bottom: 15px; text-align: justify; }}
        strong {{ color: {cor_titulo}; }}
    </style>
    </head>
    <body>
        {html_capa}
        {html_content}
    </body>
    </html>
    """
    
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_final, dest=pdf_buffer)
    if pisa_status.err: return None
    return pdf_buffer.getvalue()

# --- INTERFACE ---
st.title("🏭 Fábrica Enterprise 5.0")
st.markdown("---")

# --- SESSION STATE ---
if "dados" not in st.session_state:
    st.session_state.dados = {
        "tema": "", "publico": "", "tom": "Profissional", 
        "sumario": "", "conteudo": "", "prompt_capa": ""
    }

# --- SIDEBAR (CONFIG & DB) ---
with st.sidebar:
    st.header("🔑 Acesso")
    api_key = st.text_input("Chave Groq", type="password")
    
    st.divider()
    st.header("💾 Projetos Salvos")
    
    # Salvar
    nome_projeto = st.text_input("Nome do Projeto para Salvar")
    if st.button("Salvar Projeto"):
        if nome_projeto:
            salvar_projeto_db(nome_projeto, st.session_state.dados)
            st.success(f"Projeto '{nome_projeto}' salvo!")
    
    # Carregar
    lista_projetos = listar_projetos_db()
    projeto_selecionado = st.selectbox("Carregar Projeto", ["Selecione..."] + lista_projetos)
    if st.button("Carregar"):
        if projeto_selecionado != "Selecione...":
            dados_carregados = carregar_projeto_db(projeto_selecionado)
            if dados_carregados:
                st.session_state.dados = dados_carregados
                st.rerun() # Atualiza a tela

    st.divider()
    st.header("🎨 Capa")
    uploaded_file = st.file_uploader("Upload da Imagem (Bing/DALL-E)", type=['jpg', 'png'])

if not api_key:
    st.warning("👈 Insira a Chave API na esquerda para começar.")
    st.stop()

client = get_client(api_key)

# --- TABS DE NAVEGAÇÃO ---
tab1, tab2, tab3 = st.tabs(["1. Planejamento", "2. Produção Automática", "3. Exportação & Design"])

# TAB 1: DEFINIÇÃO
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("O que vamos criar?")
        st.session_state.dados["tema"] = st.text_input("Tema", value=st.session_state.dados["tema"])
        st.session_state.dados["publico"] = st.text_input("Público", value=st.session_state.dados["publico"])
        st.session_state.dados["tom"] = st.selectbox("Tom de Voz", ["Profissional", "Inspirador", "Prático"], index=0)
        
        if st.button("Gerar Sumário"):
            prompt = f"Crie um sumário para e-book sobre '{st.session_state.dados['tema']}'. Público: {st.session_state.dados['publico']}. 6 a 8 capítulos."
            st.session_state.dados["sumario"] = gerar_texto(client, prompt)

    with col2:
        st.subheader("Visual da Capa")
        if st.button("Gerar Ideia de Capa (Prompt)"):
            prompt_img = f"Describe a book cover for '{st.session_state.dados['tema']}'. Minimalist vector art. Max 40 words. Direct visual description."
            st.session_state.dados["prompt_capa"] = gerar_texto(client, prompt_img)
        
        if st.session_state.dados["prompt_capa"]:
            st.info("Copie e cole no Bing Image Creator:")
            st.code(st.session_state.dados["prompt_capa"])

    if st.session_state.dados["sumario"]:
        st.markdown("### 📋 Plano Gerado:")
        st.markdown(st.session_state.dados["sumario"])

# TAB 2: AUTOMAÇÃO
with tab2:
    st.header("🏭 Linha de Montagem")
    st.write("Escolha como você quer escrever seu livro.")
    
    col_a, col_b = st.columns(2)
    
    # MODO MANUAL
    with col_a:
        st.subheader("✍️ Modo Manual")
        cap_manual = st.text_input("Nome do Capítulo Individual")
        if st.button("Escrever este Capítulo"):
            texto = gerar_texto(client, f"Escreva o capítulo '{cap_manual}' do livro '{st.session_state.dados['tema']}'. Detalhado. Use Markdown.")
            if texto:
                st.session_state.dados["conteudo"] += f"\n\n# {cap_manual}\n\n{texto}\n\n---\n"
                st.success("Adicionado!")

    # MODO AUTOMÁTICO
    with col_b:
        st.subheader("⚡ Modo Turbo (Automático)")
        st.warning("Isso vai gerar o livro inteiro baseado no sumário. Pode levar 1 ou 2 minutos.")
        qtd_capitulos = st.slider("Quantos capítulos o livro terá?", 3, 10, 5)
        
        if st.button("🚀 GERAR LIVRO COMPLETO AGORA"):
            if not st.session_state.dados["sumario"]:
                st.error("Gere o sumário primeiro na Aba 1!")
            else:
                barra = st.progress(0)
                st.session_state.dados["conteudo"] = "" # Limpa conteúdo antigo
                
                for i in range(1, qtd_capitulos + 1):
                    with st.spinner(f"Escrevendo Capítulo {i} de {qtd_capitulos}..."):
                        prompt_auto = f"""
                        Estamos escrevendo um livro sobre {st.session_state.dados['tema']}.
                        O sumário é: {st.session_state.dados["sumario"]}.
                        
                        SUA TAREFA: Escreva AGORA SOMENTE o conteúdo do CAPÍTULO NÚMERO {i}.
                        Dê um título criativo para este capítulo.
                        Seja profundo e didático. Mínimo 600 palavras.
                        """
                        texto_cap = gerar_texto(client, prompt_auto)
                        if texto_cap:
                            st.session_state.dados["conteudo"] += f"\n\n{texto_cap}\n\n---\n"
                        barra.progress(i / qtd_capitulos)
                        time.sleep(1) # Pausa para não bloquear a API
                
                st.success("Livro Completo Gerado com Sucesso!")

    # PRÉVIA
    if st.session_state.dados["conteudo"]:
        st.divider()
        with st.expander("Ver Conteúdo do Livro"):
            st.markdown(st.session_state.dados["conteudo"])

# TAB 3: EXPORTAÇÃO
with tab3:
    st.header("🎨 Finalização e Design")
    
    if not st.session_state.dados["conteudo"]:
        st.info("Escreva o conteúdo na aba 2 primeiro.")
    else:
        estilo_escolhido = st.selectbox("Escolha o Design do PDF", ["Clássico", "Executivo (Azul)", "Criativo (Roxo)"])
        
        # Prepara dados
        texto_final = f"# {st.session_state.dados['tema'].upper()}\n\nUm guia exclusivo.\n\n---\n\n{st.session_state.dados['conteudo']}"
        img_b64 = get_image_base64(uploaded_file) if uploaded_file else None
        
        # Gera PDF
        pdf_bytes = converter_markdown_para_pdf(texto_final, img_b64, estilo_escolhido)
        
        if pdf_bytes:
            st.download_button(
                label=f"📕 BAIXAR E-BOOK ({estilo_escolhido})",
                data=pdf_bytes,
                file_name=f"Ebook_{st.session_state.dados['tema']}.pdf",
                mime="application/pdf",
                type="primary"
            )