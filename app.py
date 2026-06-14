import streamlit as st
import pandas as pd
from PIL import Image
import os
import requests
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACAO DA PAGINA
st.set_page_config(
    page_title="Bolao Homedock - Copa 2026", 
    page_icon="⚽", 
    layout="wide"
)

# Estilizacao customizada com a identidade visual da Homedock
st.markdown("""
    <style>
    .stApp {
        background-color: #FAF9F6;
        color: #111111;
    }
    h1, h2, h3 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #111111 !important;
        font-weight: 700 !important;
    }
    div.stButton > button:first-child {
        background-color: #111111;
        color: #FFFFFF;
        border-radius: 12px;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #333333;
        color: #FFFFFF;
    }
    button[data-baseweb="tab"] {
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #888888 !important;
    }
    button[aria-selected="true"] {
        color: #111111 !important;
        font-weight: 700 !important;
        border-bottom-color: #111111 !important;
    }
    </style>
""", unsafe_allow_html=True)

# CONFIGURAÇÕES DO GOOGLE FORMS EXATAS
ID_FORMULARIO = "1FAIpQLSe0o0aZx7k8XhGZ0C4C-AENyJU-B7943JDfjJosULfTOlWFww" 
ENTRY_NOME = "entry.357942348"
ENTRY_JOGO = "entry.1347005369"
ENTRY_CASA = "entry.1938823404"
ENTRY_FORA = "entry.1888761423"

# 2. TOPO COM LOGO E TITULO ALINHADOS NA MESMA ALTURA
col_logo, col_titulo = st.columns([0.6, 3.4], vertical_alignment="center")

with col_logo:
    if os.path.exists("image_27b81c.png"):
        logo = Image.open("image_27b81c.png")
        st.image(logo, use_container_width=True)
    else:
        st.subheader("HOMEDOCK")

with col_titulo:
    st.markdown("<h2 style='margin: 0; padding: 0; font-size: 28px; line-height: 1;'>🏆 COPA 2026</h2>", unsafe_allow_html=True)

st.markdown("---")

# 3. JOGOS FIXOS DA FASE DE GRUPOS
if "jogos" not in st.session_state:
    st.session_state.jogos = {
        "Fase de Grupos: Brasil x Marrocos": {"real_casa": None, "real_fora": None},
        "Fase de Grupos: Brasil x Haiti": {"real_casa": None, "real_fora": None},
        "Fase de Grupos: Brasil x Escocia": {"real_casa": None, "real_fora": None},
    }

# LEITURA DOS DADOS (Apenas leitura via conexão nativa do Streamlit)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_existente = conn.read(ttl=0)
    
    if df_existente.empty:
        df_existente = pd.DataFrame(columns=["Data_Hora", "Nome", "Jogo", "gols_casa", "gols_fora"])
    else:
        df_existente.columns = ["Data_Hora", "Nome", "Jogo", "gols_casa", "gols_fora"]
except Exception:
    df_existente = pd.DataFrame(columns=["Data_Hora", "Nome", "Jogo", "gols_casa", "gols_fora"])

palpites_lista = df_existente.to_dict(orient="records")

# 4. FUNCAO DE REGRAS DE PONTOS
def calcular_pontos(p_casa, p_fora, r_casa, r_fora):
    if r_casa is None or r_fora is None:
        return 0 
    if p_casa == r_casa and p_fora == r_fora:
        return 6
    vencedor_palpite = "casa" if p_casa > p_fora else ("fora" if p_fora > p_casa else "empate")
    vencedor_real = "casa" if r_casa > r_fora else ("fora" if r_fora > r_casa else "empate")
    if vencedor_palpite == vencedor_real:
        return 3
    return 0

# 5. QUADRO DE REGRAS VISUAL (Onde estava dando o erro de aspas)
st.markdown("### 📋 Regulamento de Pontuacao Homedock:")
col_r1, col_r2, col_r3 = st.columns(3)
with col_r1:
    st.info("**6 PONTOS**\n\nAcerto exato do placar")
with col_r2:
    st.warning("**3 PONTOS**\n\nAcerto do vencedor ou empate")
with col_r3:
    st.error("**0 PONTOS**\n\nErro total do placar")

st.markdown("---")

# 6. CRIACAO DAS ABAS
aba_palpites, aba_ranking, aba_admin = st.tabs(["📝 Dar Palpite", "📊 Classificacao Geral", "⚙️ Painel do Administrador"])

# --- ABA 1: PALPITES ---
with aba_palpites:
    st.subheader("Registre o seu palpite")
    
    st.write("💡 **Orientacao Importante:** Use sempre **exatamente o mesmo nome e sobrenome** em todos os seus palpites!")
    
    nomes_existentes = sorted(list(set(str(p["Nome"]) for p in palpites_lista if pd.notna(p["Nome"]))))
    
    with st.form("form_palpite", clear_on_submit=True):
        nome = st.text_input("Seu Nome Completo:")
        jogo_selecionado = st.selectbox("Escolha a partida:", list(st.session_state.jogos.keys()))
        
        col1, col2 = st.columns(2)
        with col1:
            gols_brasil = st.number_input("Gols do Brasil:", min_value=0, max_value=15, value=1, step=1)
        with col2:
            gols_adversario = st.number_input("Gols do Adversario:", min_value=0, max_value=15, value=0, step=1)
            
        enviar = st.form_submit_button("Salvar Palpite 🚀")
        
        if enviar:
            nome_limpo = nome.strip()
            if nome_limpo == "":
                st.error("Por favor, digite seu nome antes de enviar.")
            else:
                ja_palpitou = any(str(p["Nome"]).lower() == nome_limpo.lower() and str(p["Jogo"]) == jogo_selecionado for p in palpites_lista)
                
                if ja_palpitou:
                    st.error(f"Atencao, {nome_limpo}! Voce ja enviou um palpite para este jogo.")
                else:
                    nome_unificado = nome_limpo
                    for n in nomes_existentes:
                        if n.lower() == nome_limpo.lower():
                            nome_unificado = n
                            break
                    
                    url_form = f"https://docs.google.com/forms/d/e/{ID_FORMULARIO}/formResponse"
                    payload = {
                        ENTRY_NOME: nome_unificado,
                        ENTRY_JOGO: jogo_selecionado,
                        ENTRY_CASA: int(gols_brasil),
                        ENTRY_FORA: int(gols_adversario)
                    }
                    
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    }
                    
                    try:
                        res = requests.post(url_form, data=payload, headers=headers)
                        if res.status_code == 200 or res.status_code == 302:
                            st.success(f"Palpite de {nome_unificado} guardado com sucesso na nuvem!")
                            st.rerun()
                        else:
                            st.error(f"Erro temporário ao enviar dados para o servidor do Google. (Status: {res.status_code})")
                    except Exception as e:
                        st.error(f"Falha de conexão: {e}")

    if nomes_existentes:
        st.markdown("<p style='font-size: 13px; color: #666; margin-bottom: 2px; margin-top: 15px;'>👥 <b>Participantes ja cadastrados:</b></p>", unsafe_allow_html=True)
        st.caption(", ".join(nomes_existentes))

# --- ABA 2: RANKING ---
with aba_ranking:
    st.subheader("Classificacao Atualizada dos Colaboradores")
    
    pontuacao_geral = {}
    for p in palpites_lista:
        nome_func = p["Nome"]
        jogo_func = p["Jogo"]
        
        if pd.isna(nome_func) or pd.isna(jogo_func) or str(nome_func).strip() == "" or str(nome_func) == "Nome":
            continue
            
        resultado_real = st.session_state.jogos.get(jogo_func, {"real_casa": None, "real_fora": None})
        r_c = resultado_real["real_casa"]
        r_f = resultado_real["real_fora"]
        
        try:
            pts = calcular_pontos(int(p["gols_casa"]), int(p["gols_fora"]), r_c, r_f)
            if nome
