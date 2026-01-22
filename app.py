import streamlit as st
import openai
import json
import base64
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Fábrica Final 5.4", layout="wide", page_icon="💎")

# --- FUNÇÕES ---
def get_client(api_key):
    return openai.OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")

def gerar_texto(client, prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
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

def carregar_dados():
    """Função que roda quando clica no botão de restaurar"""
    arquivo = st.session_state.uploader_arquivo
    if arquivo is not None:
        try:
            dados = json.load(arquivo)
            # Força a atualização de cada chave individualmente
            st.session_state['tema'] = dados.get('tema', '')
            st.session_state['publico'] = dados.get('publico', '')
            st.session_state['sumario'] = dados.get('sumario', '')
            st.session_state['conteudo'] = dados.get('conteudo', '')
            st.session_state['prompt_capa'] = dados.get('prompt_capa', '')
            st.toast("Dados restaurados com sucesso!", icon="✅")
        except:
            st.error("Erro ao ler o arquivo.")

def gerar_html_download(tema, conteudo, img_b64, estilo):
    # Lógica de HTML (Mantida da versão anterior)
    if not conteudo: conteudo = "<p>Conteúdo vazio.</p>"
    conteudo_html = conteudo.replace("\n", "<br>").replace("# ", "<h1>").replace("## ", "<h2>").replace("---", "<hr>")
    
    cores = {"Clássico": "#2c3e50", "Executivo": "#003366", "Criativo": "#4b0082"}
    cor_h1 = cores.get(estilo, "#2c3e50")
    
    capa = f"<div style='text-align:center'><img src='data:image/jpeg;base64,{img_b64}' style='max-height:500px'><br><h1>{tema}</h1></div><div style='page-break-after:always'></div>" if img_b64 else ""
    
    return f"<html><body style='font-family:sans-serif; padding:40px'>{capa}{conteudo_html}<script>window.print()</script></body></html>"

# --- INICIALIZAÇÃO DE VARIÁVEIS (OBRIGATÓRIO) ---
# Aqui definimos as chaves que os campos vão usar
chaves_padrao = ['tema', 'publico', 'sumario', 'conteudo', 'prompt_capa']
for chave in chaves_padrao:
    if chave not in st.session_state:
        st.session_state[chave] = ""

# --- INTERFACE ---
st.title("💎 Fábrica Final 5.4 (Vinculada)")

with st.sidebar:
    st.header("1. Configurações")
    api_key = st.text_input("Chave Groq", type="password")
    
    st.divider()
    st.header("2. Backup (Salvar/Carregar)")
    
    # Prepara os dados atuais para salvar
    dados_para_salvar = {
        "tema": st.session_state['tema'],
        "publico": st.session_state['publico'],
        "sumario": st.session_state['sumario'],
        "conteudo": st.session_state['conteudo'],
        "prompt_capa": st.session_state['prompt_capa']
    }
    
    st.download_button(
        label="💾 Baixar Arquivo do Projeto",
        data=json.dumps(dados_para_salvar),
        file_name="meu_projeto.json",
        mime="application/json"
    )
    
    # Upload com "Callback" (O segredo para funcionar)
    st.file_uploader(
        "Carregar Projeto Antigo", 
        type=["json"], 
        key="uploader_arquivo", 
        on_change=carregar_dados # <-- ISSO É A MÁGICA. Roda a função assim que envia o arquivo.
    )

    st.divider()
    st.header("3. Estilo")
    # Agora as opções ficam fora de qualquer "if" para não sumirem
    estilo = st.selectbox("Design do PDF", ["Clássico", "Executivo", "Criativo"])
    capa_upload = st.file_uploader("Capa (Imagem)", type=['jpg','png'])

if not api_key:
    st.warning("Coloque a chave API.")
    st.stop()

client = get_client(api_key)

# --- TABS ---
t1, t2, t3 = st.tabs(["Planejamento", "Produção", "Download"])

with t1:
    col1, col2 = st.columns(2)
    with col1:
        # Repare no key='tema'. Isso liga o campo direto na memória.
        st.text_input("Tema", key="tema") 
        st.text_input("Público", key="publico")
        
        if st.button("Gerar Sumário"):
            prompt = f"Sumário para e-book '{st.session_state.tema}' (Público: {st.session_state.publico}). 5 capítulos."
            st.session_state.sumario = gerar_texto(client, prompt)
            st.rerun() # Atualiza a tela na hora

    with col2:
        if st.button("Gerar Ideia de Capa"):
            st.session_state.prompt_capa = gerar_texto(client, f"Prompt visual curto em inglês para capa: {st.session_state.tema}")
            st.rerun()
        
        if st.session_state.prompt_capa:
            st.code(st.session_state.prompt_capa)

    if st.session_state.sumario:
        st.markdown("---")
        st.markdown(st.session_state.sumario)

with t2:
    if st.button("⚡ Escrever Livro Completo"):
        if not st.session_state.sumario:
            st.error("Sem sumário!")
        else:
            bar = st.progress(0)
            st.session_state.conteudo = ""
            for i in range(1, 6):
                txt = gerar_texto(client, f"Escreva cap {i} do livro {st.session_state.tema}. Use HTML <h2> e <p>.")
                if txt: st.session_state.conteudo += f"<h1>Cap {i}</h1>{txt}<hr>"
                bar.progress(i/5)
            st.success("Pronto!")
            st.rerun()
            
    if st.session_state.conteudo:
        with st.expander("Ver Texto"):
            st.markdown(st.session_state.conteudo, unsafe_allow_html=True)

with t3:
    if st.session_state.conteudo:
        b64 = get_image_base64(capa_upload)
        html = gerar_html_download(st.session_state.tema, st.session_state.conteudo, b64, estilo)
        st.download_button("📄 BAIXAR AGORA", html, f"{st.session_state.tema}.html", "text/html")
    else:
        st.info("Gere o conteúdo na aba anterior primeiro.")
