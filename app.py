import streamlit as st
import openai
import json
import base64
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Fábrica Enterprise 5.1", layout="wide", page_icon="🏢")

# --- FUNÇÕES DE CONNEXÃO ---
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

# --- GERADOR DE ARQUIVO HTML (SUBSTITUI O PDF) ---
def gerar_html_download(tema, conteudo_markdown, imagem_capa_base64=None, estilo="Clássico"):
    # Define cores baseadas no estilo
    cores = {
        "Clássico": {"h1": "#2c3e50", "h2": "#e67e22", "bg": "#ffffff", "font": "Helvetica, Arial"},
        "Executivo (Azul)": {"h1": "#003366", "h2": "#0066cc", "bg": "#f4f7f6", "font": "Georgia, serif"},
        "Criativo (Roxo)": {"h1": "#4b0082", "h2": "#8a2be2", "bg": "#faf0e6", "font": "Verdana, sans-serif"}
    }
    c = cores.get(estilo, cores["Clássico"])

    # Converte Markdown para HTML básico (simples conversão de texto)
    # Nota: Estamos fazendo manual para não depender de libs externas pesadas
    conteudo_html = conteudo_markdown.replace("\n", "<br>").replace("# ", "<h1>").replace("## ", "<h2>").replace("---", "<hr>")
    
    # HTML da Capa
    capa_html = ""
    if imagem_capa_base64:
        capa_html = f"""
        <div class="capa">
            <img src="data:image/jpeg;base64,{imagem_capa_base64}">
            <h1 class="titulo-capa">{tema.upper()}</h1>
        </div>
        <div class="page-break"></div>
        """

    # Estrutura Final do Arquivo
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{tema}</title>
        <style>
            body {{ font-family: {c['font']}; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background: {c['bg']}; }}
            .capa {{ text-align: center; margin-top: 50px; margin-bottom: 100px; }}
            .capa img {{ max-width: 100%; max-height: 600px; box-shadow: 0 10px 20px rgba(0,0,0,0.2); }}
            .titulo-capa {{ font-size: 3em; margin-top: 20px; color: {c['h1']}; }}
            h1 {{ color: {c['h1']}; border-bottom: 2px solid #ccc; padding-bottom: 10px; margin-top: 50px; }}
            h2 {{ color: {c['h2']}; margin-top: 30px; }}
            p {{ margin-bottom: 15px; text-align: justify; }}
            .page-break {{ page-break-after: always; }}
            @media print {{ body {{ max-width: 100%; }} .page-break {{ page-break-after: always; }} }}
        </style>
    </head>
    <body>
        {capa_html}
        <div class="conteudo">
            {conteudo_html}
        </div>
        <script>
            window.onload = function() {{ window.print(); }}
        </script>
    </body>
    </html>
    """
    return html_template

# --- INTERFACE ---
st.title("🏭 Fábrica Enterprise 5.1 (Versão Nuvem)")
st.info("💡 Dica: Ao baixar o arquivo, ele abrirá para impressão. Selecione 'Salvar como PDF' no destino.")
st.markdown("---")

# --- SESSION STATE ---
if "dados" not in st.session_state:
    st.session_state.dados = {"tema": "", "publico": "", "sumario": "", "conteudo": "", "prompt_capa": ""}

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔑 Acesso")
    api_key = st.text_input("Chave Groq", type="password")
    st.divider()
    st.header("🎨 Capa")
    uploaded_file = st.file_uploader("Upload da Imagem", type=['jpg', 'png'])

if not api_key:
    st.warning("👈 Insira a Chave API na esquerda.")
    st.stop()

client = get_client(api_key)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["1. Planejamento", "2. Produção", "3. Exportação"])

with tab1:
    st.session_state.dados["tema"] = st.text_input("Tema", value=st.session_state.dados["tema"])
    st.session_state.dados["publico"] = st.text_input("Público", value=st.session_state.dados["publico"])
    
    if st.button("Gerar Sumário"):
        prompt = f"Crie um sumário para e-book sobre '{st.session_state.dados['tema']}'. Público: {st.session_state.dados['publico']}. 5 capítulos."
        st.session_state.dados["sumario"] = gerar_texto(client, prompt)
    
    if st.session_state.dados["sumario"]:
        st.markdown(st.session_state.dados["sumario"])

    st.divider()
    if st.button("Gerar Prompt de Capa"):
        st.session_state.dados["prompt_capa"] = gerar_texto(client, f"Prompt visual curto em inglês para capa de livro sobre {st.session_state.dados['tema']}.")
    if st.session_state.dados["prompt_capa"]:
        st.code(st.session_state.dados["prompt_capa"])

with tab2:
    if st.button("⚡ Gerar Livro Completo (Turbo)"):
        if not st.session_state.dados["sumario"]:
            st.error("Gere o sumário antes!")
        else:
            barra = st.progress(0)
            st.session_state.dados["conteudo"] = ""
            # Simulação de geração rápida para teste
            for i in range(1, 6):
                with st.spinner(f"Escrevendo cap {i}..."):
                    texto = gerar_texto(client, f"Escreva o capítulo {i} do livro {st.session_state.dados['tema']}. Mínimo 400 palavras. Use tags HTML como <h2> para subtitulos e <p> para parágrafos.")
                    if texto: st.session_state.dados["conteudo"] += f"<br><h1>Capítulo {i}</h1><br>{texto}<br><hr>"
                    barra.progress(i/5)
                    time.sleep(1)
            st.success("Concluído!")

with tab3:
    if st.session_state.dados["conteudo"]:
        estilo = st.selectbox("Estilo", ["Clássico", "Executivo (Azul)", "Criativo (Roxo)"])
        img_b64 = get_image_base64(uploaded_file) if uploaded_file else None
        
        # Gera HTML
        html_data = gerar_html_download(st.session_state.dados["tema"], st.session_state.dados["conteudo"], img_b64, estilo)
        
        st.download_button(
            label="📄 BAIXAR E-BOOK (Versão Web/PDF)",
            data=html_data,
            file_name=f"Ebook_{st.session_state.dados['tema']}.html",
            mime="text/html"
        )
        st.caption("Ao abrir o arquivo baixado, use Ctrl+P e escolha 'Salvar como PDF'.")
