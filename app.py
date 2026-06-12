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

# CONFIGURAÇÕES DO GOOGLE FORMS
ID_FORMULARIO = "1FAIpQLSe0o0aZx7k8XhGZ0C4C-AENyJU-B7943JDfjJosULfTOlWFww" 
ENTRY_NOME = "entry.233513364"
ENTRY_JOGO = "entry.1342686001"
ENTRY_CASA = "entry.2062534064"
ENTRY_FORA = "entry.188899881"

# 2. TOPO COM LOGO E TITULO ALINHADOS NA MESMA ALTURA
# Usamos vertical_alignment="center" para alinhar o meio da imagem com o meio do texto
col_logo, col_titulo = st.columns([0.6, 3.4], vertical_alignment="center")

with col_logo:
    if os.path.exists("image_27b81c.png"):
        logo = Image.open("image_27b81c.png")
        st.image(logo, use_container_width=True)
    else:
        st.subheader("HOMEDOCK")

with col_titulo:
    # Usamos h2 com uma margem zerada e tamanho controlado para casar perfeitamente com a logo
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

# 5. QUADRO DE REGRAS VISUAL
st.markdown("""
<div style='background-color: white; padding: 20px; border-radius: 15px; border: 1px solid #E5E5E5; margin-bottom: 25px;'>
    <h4 style='margin-top:0; color:#111;'>📋 Regulamento de Pontuacao Homedock:</h4>
    <span style='background-color:#111; color:white; padding: 3px 10px; border-radius: 5px; font-weight:bold; font-size:12px; margin-right:10px;'>6 PONTOS</span> Acerto exato do placar<br>
    <span style='background-color:#C5A880; color:white; padding: 3px 10px; border-radius: 5px; font-weight:bold; font-size:12px; margin-right:10px; margin-top:5px; display:inline-block;'>3 PONTOS</span> Acerto do vencedor ou do empate errando o numero de gols<br>
    <span style='background-color:#E5E5E5; color:#555; padding: 3px 10px; border-radius: 5px; font-weight:bold; font-size:12px; margin-right:10px; margin-top:5px; display:inline-block;'>0 PONTOS</span> Erro total do placar e do resultado
</div>
""", unsafe_allow_html=True)

# 6. CRIACAO DAS ABAS
aba_palpites, aba_ranking, aba_admin = st.tabs(["📝 Dar Palpite", "📊 Classificacao Geral", "⚙️ Painel do Administrador"])

# --- ABA 1: PALPITES ---
with aba_palpites:
    st.subheader("Registre o seu palpite")
    
    st.markdown("""
    <div style='background-color: #EBF8FF; padding: 12px; border-radius: 8px; border-left: 4px solid #3182CE; margin-bottom: 15px; font-size: 13px; color: #2B6CB0;'>
        💡 <b>Orientacao Importante:</b> Use sempre <b>exatamente o mesmo nome e sobrenome</b> em todos os seus palpites!
    </div>
    """, unsafe_allow_html=True)
    
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
                    
                    try:
                        res = requests.post(url_form, data=payload)
                        if res.status_code == 200:
                            st.success(f"Palpite de {nome_unificado} guardado com sucesso na nuvem!")
                            st.rerun()
                        else:
                            st.error("Erro temporário ao enviar dados para o servidor do Google.")
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
