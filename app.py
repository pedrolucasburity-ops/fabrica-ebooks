import streamlit as st
import openai
import json
import io
import time
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Infinity Factory 8.3 (Deep Word)", layout="wide", page_icon="📘")

def carregar_css():
    st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #fff; }
        .stButton>button { background: linear-gradient(90deg, #d53369 0%, #daae51 100%); color: white; border: none; padding: 12px; width: 100%; font-weight: bold; }
        [data-testid="stSidebar"] { background-color: #111; }
        h1, h2, h3 { color: white !important; }
        .stError { background-color: #500; color: #fcc; }
    </style>""", unsafe_allow_html=True)

# --- 2. LOGIN ---
def check_password():
    if "authenticated" not in st.session_state: st.session_state.authenticated = False
    if st.session_state.authenticated: return True
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔒 Login")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if senha == "admin": st.session_state.authenticated = True; st.rerun()
            else: st.error("Senha incorreta")
    return False

# --- 3. IA (MODO PROFUNDO RESTAURADO) ---
def get_client(api_key): 
    return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def gerar_texto_rico(client, prompt, contexto="", modelo="llama-3.3-70b-versatile"):
    # AQUI ESTÁ O SEGREDO DO TEXTO LONGO
    system_prompt = """
    Você é um ESCRITOR SÊNIOR e Especialista Técnico.
    
    SUAS REGRAS OBRIGATÓRIAS (MODO PROFUNDO):
    1. DENSIDADE: Escreva parágrafos longos e explicativos. Nunca seja superficial.
    2. ESTRUTURA: Comece com conceitos teóricos, desenvolva o raciocínio e dê exemplos práticos.
    3. FORMATO: Use Markdown.
       - Use ## para Subtítulos.
       - Use **Negrito** para destacar termos importantes.
    4. PROIBIDO: Não faça listas de tópicos sem explicar cada um detalhadamente antes.
    5. NÃO repita o título do capítulo no início do texto.
    """
    
    try:
        resp = client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": f"CONTEXTO DO LIVRO: {contexto}\n\nSUA TAREFA AGORA: {prompt}\n\nEscreva no mínimo 1000 palavras."}
            ],
            temperature=0.7 # Temperatura alta para ele escrever mais
        )
        return resp.choices[0].message.content
    except Exception as e:
        st.error(f"Erro na IA ({modelo}): {e}")
        return None

# --- 4. GERADOR DE WORD ---
def criar_word(tema, publico, conteudo_raw, capa_file):
    doc = Document()
    
    # Capa
    if capa_file:
        try:
            doc.add_picture(capa_file, width=Inches(6))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        except: pass
        
    doc.add_paragraph("\n")
    t = doc.add_heading(tema.upper(), 0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Público Alvo: {publico}").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()
    
    # Conteúdo
    if conteudo_raw:
        for linha in conteudo_raw.split('\n'):
            linha = linha.strip()
            if not linha: continue
            
            if linha.startswith('# '): 
                doc.add_heading(linha.replace('# ', ''), 1)
            elif linha.startswith('## '): 
                doc.add_heading(linha.replace('## ', ''), 2)
            elif '---' in linha: 
                doc.add_page_break()
            else: 
                p = doc.add_paragraph()
                # Processa negrito simples
                parts = linha.split('**')
                for i, pt in enumerate(parts):
                    r = p.add_run(pt)
                    if i % 2 == 1: r.bold = True
                p.paragraph_format.space_after = Pt(12)
    
    b = io.BytesIO()
    doc.save(b)
    b.seek(0)
    return b

# --- APP ---
if "dados" not in st.session_state: st.session_state.dados = {"tema": "", "publico": "", "sumario": "", "conteudo": ""}
carregar_css()

if check_password():
    st.sidebar.title("Factory 8.3 (Deep)")
    api_key = st.sidebar.text_input("API Key Groq", type="password")
    
    # Seletor de Modelo (Mantenha o llama-3.3 se possível, ele escreve melhor)
    modelo = st.sidebar.selectbox("Modelo IA", ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "llama3-70b-8192"])

    with st.sidebar.expander("Backup"):
        st.download_button("Salvar", json.dumps(st.session_state.dados), "bkp.json")
        f = st.file_uploader("Carregar", type=["json"])
        if f: st.session_state.dados = json.load(f); st.rerun()

    if not api_key: st.stop()
    client = get_client(api_key)

    t1, t2, t3 = st.tabs(["Planejar", "Escrever", "Baixar Word"])
    
    with t1:
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.dados["tema"] = st.text_input("Tema", value=st.session_state.dados["tema"])
            st.session_state.dados["publico"] = st.text_input("Público", value=st.session_state.dados["publico"])
        with c2:
            if st.button("Gerar Sumário"):
                # Prompt específico para sumário
                res = gerar_texto_rico(client, f"Crie um sumário detalhado (5 caps) para '{st.session_state.dados['tema']}'.", "", modelo)
                if res: 
                    st.session_state.dados["sumario"] = res
                    st.rerun()
        if st.session_state.dados["sumario"]: st.markdown(st.session_state.dados["sumario"])

    with t2:
        if st.button("🔥 ESCREVER LIVRO (MODO PROFUNDO)"):
            bar = st.progress(0)
            st.session_state.dados["conteudo"] = ""
            for i in range(1, 6):
                with st.spinner(f"Escrevendo Capítulo {i} com profundidade..."):
                    # Prompt reforçado
                    p = f"Escreva o CAPÍTULO {i} completo. Aprofunde nos conceitos. Explique o 'porquê' e o 'como'. Use ## para subtítulos."
                    ctx = f"Livro: {st.session_state.dados['tema']}. Público: {st.session_state.dados['publico']}"
                    
                    txt = gerar_texto_rico(client, p, ctx, modelo)
                    
                    if txt: 
                        st.session_state.dados["conteudo"] += f"# Capítulo {i}\n\n{txt}\n\n---\n"
                    else:
                        st.error("Erro na geração. Verifique a chave ou mude o modelo.")
                        break
                bar.progress(i/5)
            st.success("Livro Concluído!")
            
        if st.session_state.dados["conteudo"]: st.markdown(st.session_state.dados["conteudo"])

    with t3:
        st.header("Download Word")
        capa = st.file_uploader("Capa", type=['png', 'jpg'])
        if st.session_state.dados["conteudo"]:
            if st.button("Processar DOCX"):
                docx = criar_word(st.session_state.dados["tema"], st.session_state.dados["publico"], st.session_state.dados["conteudo"], capa)
                st.download_button("BAIXAR ARQUIVO WORD", docx, "SeuLivro.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
