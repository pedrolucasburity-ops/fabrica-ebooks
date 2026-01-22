import streamlit as st
import openai
import json
import base64
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Fábrica Enterprise 5.3", layout="wide", page_icon="🏢")

# --- FUNÇÕES ---
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

def gerar_html_download(tema, conteudo_markdown, imagem_capa_base64=None, estilo="Clássico"):
    # Cores e Estilos
    cores = {
        "Clássico": {"h1": "#2c3e50", "h2": "#e67e22", "bg": "#ffffff", "font": "Helvetica, Arial"},
        "Executivo": {"h1": "#003366", "h2": "#0066cc", "bg": "#f4f7f6", "font": "Georgia, serif"},
        "Criativo": {"h1": "#4b0082", "h2": "#8a2be2", "bg": "#faf0e6", "font": "Verdana, sans-serif"}
    }
    c = cores.get(estilo, cores["Clássico"])

    # Conversão Texto -> HTML
    if conteudo_markdown:
        conteudo_html = conteudo_markdown.replace("\n", "<br>").replace("# ", "<h1>").replace("## ", "<h2>").replace("---", "<hr>")
    else:
        conteudo_html = "<p>O conteúdo está vazio.</p>"
    
    capa_html = ""
    if imagem_capa_base64:
        capa_html = f"""<div class='capa'><img src='data:image/jpeg;base64,{imagem_capa_base64}'><h1 class='titulo-capa'>{tema.upper()}</h1></div><div class='page-break'></div>"""

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{tema}</title>
        <style>
            body {{ font-family: {c['font']}; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background: {c['bg']}; }}
            .capa {{ text-align: center; margin-top: 50px; margin-bottom: 100px; }}
            .capa img {{ max-width: 100%; max-height: 500px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); border-radius: 10px; }}
            .titulo-capa {{ font-size: 3em; margin-top: 20px; color: {c['h1']}; }}
            h1 {{ color: {c['h1']}; border-bottom: 2px solid #ccc; padding-bottom: 10px; margin-top: 50px; }}
            h2 {{ color: {c['h2']}; margin-top: 30px; }}
            p {{ margin-bottom: 15px; text-align: justify; }}
            .page-break {{ page-break-after: always; }}
            @media print {{ body {{ max-width: 100%; background: white; }} .page-break {{ page-break-after: always; }} }}
        </style>
    </head>
    <body>{capa_html}<div class='conteudo'>{conteudo_html}</div>
    <script>window.onload = function() {{ window.print(); }}</script>
    </body></html>
    """
    return html_template

# --- SESSION STATE (MEMÓRIA) ---
# Inicializa as variáveis se elas não existirem
if "dados" not in st.session_state:
    st.session_state.dados = {"tema": "", "publico": "", "sumario": "", "conteudo": "", "prompt_capa": ""}

# --- INTERFACE ---
st.title("🏭 Fábrica Enterprise 5.3 (Corrigida)")
st.markdown("---")

# --- SIDEBAR (TUDO IMPORTANTE FICA AQUI) ---
with st.sidebar:
    st.header("🔑 1. Acesso")
    api_key = st.text_input("Chave Groq", type="password")
    
    st.divider()
    
    st.header("💾 2. Salvar e Carregar")
    
    # BOTÃO SALVAR
    dados_json = json.dumps(st.session_state.dados)
    st.download_button(
        label="📥 Baixar Projeto (Salvar no PC)",
        data=dados_json,
        file_name=f"Backup_{st.session_state.dados['tema'] if st.session_state.dados['tema'] else 'Projeto'}.json",
        mime="application/json"
    )
    
    # BOTÃO CARREGAR
    arquivo_carregado = st.file_uploader("📂 Carregar Backup", type=["json"])
    if arquivo_carregado is not None:
        if st.button("♻️ Restaurar Dados"):
            try:
                dados_lidos = json.load(arquivo_carregado)
                # Atualiza a memória
                st.session_state.dados = dados_lidos
                st.success("Dados restaurados! A página vai recarregar...")
                time.sleep(1)
                st.rerun() # Força atualização da tela
            except:
                st.error("Erro ao ler arquivo. Tem certeza que é um JSON válido?")

    st.divider()
    
    # --- AQUI ESTAVAM AS OPÇÕES QUE SUMIRAM ---
    # Agora estão fixas na lateral para nunca sumirem
    st.header("🎨 3. Design e Capa")
    estilo_escolhido = st.selectbox("Estilo do PDF", ["Clássico", "Executivo", "Criativo"])
    uploaded_file = st.file_uploader("Upload Capa (Bing/DALL-E)", type=['jpg', 'png'])

if not api_key:
    st.warning("👈 Insira a Chave API na esquerda.")
    st.stop()

client = get_client(api_key)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["1. Planejamento", "2. Produção", "3. Download"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        # O valor do campo sempre lê da memória (st.session_state)
        novo_tema = st.text_input("Tema", value=st.session_state.dados["tema"])
        if novo_tema != st.session_state.dados["tema"]:
            st.session_state.dados["tema"] = novo_tema

        novo_publico = st.text_input("Público", value=st.session_state.dados["publico"])
        if novo_publico != st.session_state.dados["publico"]:
             st.session_state.dados["publico"] = novo_publico

        if st.button("Gerar Sumário"):
            prompt = f"Crie um sumário para e-book sobre '{st.session_state.dados['tema']}'. Público: {st.session_state.dados['publico']}. 5 capítulos."
            st.session_state.dados["sumario"] = gerar_texto(client, prompt)
    
    with col2:
        if st.button("Gerar Prompt de Capa"):
            st.session_state.dados["prompt_capa"] = gerar_texto(client, f"Prompt visual curto em inglês para capa de livro sobre {st.session_state.dados['tema']}.")
        
        if st.session_state.dados["prompt_capa"]:
            st.code(st.session_state.dados["prompt_capa"])

    st.markdown("### Sumário Atual:")
    if st.session_state.dados["sumario"]:
        st.markdown(st.session_state.dados["sumario"])
    else:
        st.info("Ainda não há sumário gerado.")

with tab2:
    st.info("Gera o conteúdo automaticamente baseado no sumário.")
    if st.button("⚡ Gerar Livro Completo (Turbo)"):
        if not st.session_state.dados["sumario"]:
            st.error("Gere o sumário primeiro!")
        else:
            barra = st.progress(0)
            st.session_state.dados["conteudo"] = ""
            for i in range(1, 6):
                with st.spinner(f"Escrevendo capítulo {i}..."):
                    texto = gerar_texto(client, f"Escreva o capítulo {i} do livro {st.session_state.dados['tema']}. Use HTML <h2> e <p>.")
                    if texto: st.session_state.dados["conteudo"] += f"<br><h1>Capítulo {i}</h1><br>{texto}<br><hr>"
                    barra.progress(i/5)
            st.success("Concluído! Vá para a aba 3.")
    
    # Mostra prévia se tiver conteúdo
    if st.session_state.dados["conteudo"]:
        with st.expander("Ver texto gerado"):
            st.markdown(st.session_state.dados["conteudo"], unsafe_allow_html=True)

with tab3:
    st.header("Produto Final")
    
    if st.session_state.dados["conteudo"]:
        # Prepara o HTML usando o estilo selecionado na Sidebar
        img_b64 = get_image_base64(uploaded_file) if uploaded_file else None
        html_data = gerar_html_download(st.session_state.dados["tema"], st.session_state.dados["conteudo"], img_b64, estilo_escolhido)
        
        st.download_button(
            label=f"📄 BAIXAR E-BOOK ({estilo_escolhido})",
            data=html_data,
            file_name=f"Ebook_{st.session_state.dados['tema']}.html",
            mime="text/html",
            type="primary"
        )
        st.caption("Instrução: Abra o arquivo baixado e salve como PDF (Ctrl+P).")
    else:
        st.warning("Gere o conteúdo na Aba 2 primeiro para liberar o download.")
