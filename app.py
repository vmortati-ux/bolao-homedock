import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACAO DA PAGINA
st.set_page_config(
    page_title="Bolao Homedock - Copa 2026", 
    page_icon="⚽", 
    layout="wide"
)

st.markdown("""
    <style>
    .stApp { background-color: #FAF9F6; color: #111111; }
    h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif !important; color: #111111 !important; font-weight: 700 !important; }
    div.stButton > button:first-child { background-color: #111111; color: #FFFFFF; border-radius: 12px; border: none; padding: 0.6rem 2rem; font-weight: 600; }
    .btn-enviar { display: inline-block; padding: 0.6rem 2rem; background-color: #111111; color: white !important; text-decoration: none; border-radius: 12px; font-weight: 600; text-align: center; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

ID_FORMULARIO = "1FAIpQLSe0o0aZx7k8XhGZ0C4C-AENyJU-B7943JDfjJosULfTOlWFww" 
ENTRY_NOME = "entry.357942348"
ENTRY_JOGO = "entry.1347005369"
ENTRY_CASA = "entry.1938823404"
ENTRY_FORA = "entry.1888761423"

st.markdown("<h2>🏆 COPA 2026 - HOMEDOCK</h2>", unsafe_allow_html=True)
st.markdown("---")

if "jogos" not in st.session_state:
    st.session_state.jogos = {
        "Fase de Grupos: Brasil x Marrocos": {"real_casa": None, "real_fora": None},
        "Fase de Grupos: Brasil x Haiti": {"real_casa": None, "real_fora": None},
        "Fase de Grupos: Brasil x Escocia": {"real_casa": None, "real_fora": None},
    }

# Método alternativo que lê o HTML público da planilha sem precisar "Publicar na Web"
try:
    url_html = "https://docs.google.com/spreadsheets/d/1S0ch85t9DDzNJZXp5mZFSdNv4Em6An51MN_tYHRZCN8/preview?gid=1829076272"
    tabelas = pd.read_html(url_html, header=1)
    df_existente = tabelas[0]
    
    # Limpa colunas extras que o preview do Google gera
    df_existente = df_existente.iloc[:, 1:6]
    df_existente.columns = ["Data_Hora", "Nome", "Jogo", "gols_casa", "gols_fora"]
    df_existente = df_existente.dropna(subset=["Nome"])
except Exception:
    df_existente = pd.DataFrame(columns=["Data_Hora", "Nome", "Jogo", "gols_casa", "gols_fora"])

palpites_lista = df_existente.to_dict(orient="records")

def calcular_pontos(p_casa, p_fora, r_casa, r_fora):
    if r_casa is None or r_fora is None: return 0 
    if int(p_casa) == int(r_casa) and int(p_fora) == int(r_fora): return 6
    v_p = "casa" if int(p_casa) > int(p_fora) else ("fora" if int(p_fora) > int(p_casa) else "empate")
    v_r = "casa" if int(r_casa) > int(r_fora) else ("fora" if int(r_fora) > int(r_casa) else "empate")
    return 3 if v_p == v_r else 0

st.markdown("### 📋 Regulamento: **6 PTS** placar exato | **3 PTS** vencedor/empate")
st.markdown("---")

aba_palpites, aba_ranking, aba_admin = st.tabs(["📝 Dar Palpite", "📊 Classificacao Geral", "⚙️ Painel do Administrador"])

with aba_palpites:
    st.subheader("Prepare o seu palpite")
    nomes_existentes = sorted(list(set(str(p["Nome"]) for p in palpites_lista if pd.notna(p["Nome"]))))
    
    nome = st.text_input("Seu Nome Completo:", key="input_nome")
    jogo_selecionado = st.selectbox("Escolha a partida:", list(st.session_state.jogos.keys()), key="select_jogo")
    
    col1, col2 = st.columns(2)
    with col1: gols_brasil = st.number_input("Gols do Brasil:", min_value=0, max_value=15, value=1, step=1, key="g_casa")
    with col2: gols_adversario = st.number_input("Gols do Adversario:", min_value=0, max_value=15, value=0, step=1, key="g_fora")
        
    nome_limpo = nome.strip()
    if nome_limpo != "":
        ja_palpitou = any(str(p["Nome"]).lower() == nome_limpo.lower() and str(p["Jogo"]) == jogo_selecionado for p in palpites_lista)
        if ja_palpitou:
            st.error(f"Atencao! Voce ja enviou um palpite para este jogo.")
        else:
            params = {ENTRY_NOME: nome_limpo, ENTRY_JOGO: jogo_selecionado, ENTRY_CASA: str(int(gols_brasil)), ENTRY_FORA: str(int(gols_adversario))}
            url_preenchida = f"https://docs.google.com/forms/d/e/{ID_FORMULARIO}/viewform?usp=pp_url&{urllib.parse.urlencode(params)}"
            st.markdown(f'<a href="{url_preenchida}" target="_blank" class="btn-enviar">Confirmar e Enviar no Google Forms 🚀</a>', unsafe_allow_html=True)
    else:
        st.warning("Por favor, digite seu nome completo para habilitar o envio.")

with aba_ranking:
    st.subheader("Classificacao Geral")
    pontuacao_geral = {}
    for p in palpites_lista:
        n_func = str(p.get("Nome", "")).strip()
        j_func = str(p.get("Jogo", "")).strip()
        if not n_func or not j_func or n_func.lower() in ["nome", "nan", "timestamp"]: continue
        res_real = st.session_state.jogos.get(j_func, {"real_casa": None, "real_fora": None})
        try:
            pts = calcular_pontos(p["gols_casa"], p["gols_fora"], res_real["real_casa"], res_real["real_fora"])
            pontuacao_geral[n_func] = pontuacao_geral.get(n_func, 0) + pts
        except: continue

    if pontuacao_geral:
        df_ranking = pd.DataFrame(list(pontuacao_geral.items()), columns=["Colaborador", "Pontuacao"]).sort_values(by="Pontuacao", ascending=False).reset_index(drop=True)
        df_ranking.index = df_ranking.index + 1
        st.dataframe(df_ranking, use_container_width=True)
    else:
        st.info("Nenhum palpite computado ainda.")

with aba_admin:
    senha_admin = st.text_input("Senha master:", type="password")
    if senha_admin == "hmdk":
        for jogo, resultados in st.session_state.jogos.items():
            st.write(f"**{jogo}**")
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1: rc = st.number_input("Brasil:", min_value=0, value=resultados["real_casa"] or 0, key=f"rc_{jogo}")
            with c2: rf = st.number_input("Adversario:", min_value=0, value=resultados["real_fora"] or 0, key=f"rf_{jogo}")
            with c3:
                if st.button("Salvar", key=f"b_{jogo}"):
                    st.session_state.jogos[jogo]["real_casa"] = rc
                    st.session_state.jogos[jogo]["real_fora"] = rf
                    st.rerun()
