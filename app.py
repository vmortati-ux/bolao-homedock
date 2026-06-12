import streamlit as st
import pandas as pd
from PIL import Image
import os
from datetime import datetime, timedelta, timezone
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

# 2. TOPO COM LOGO RESTRITO E TITULO DIRETO
col_logo, col_titulo = st.columns([0.5, 3.5])
with col_logo:
    if os.path.exists("image_27b81c.png"):
        logo = Image.open("image_27b81c.png")
        st.image(logo, use_container_width=True)
    else:
        st.subheader("HOMEDOCK")

with col_titulo:
    st.markdown("<h1 style='margin-bottom: 0; padding-top: 10px;'>🏆 COPA 2026</h1>", unsafe_allow_html=True)

st.markdown("---")

# 3. JOGOS FIXOS DA FASE DE GRUPOS
if "jogos" not in st.session_state:
    st.session_state.jogos = {
        "Fase de Grupos: Brasil x Marrocos": {"real_casa": None, "real_fora": None},
        "Fase de Grupos: Brasil x Haiti": {"real_casa": None, "real_fora": None},
        "Fase de Grupos: Brasil x Escocia": {"real_casa": None, "real_fora": None},
    }

# LIGAÇÃO AO GOOGLE SHEETS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_existente = conn.read(ttl=0)
    if df_existente.empty or "Nome" not in df_existente.columns:
        df_existente = pd.DataFrame(columns=["Nome", "Jogo", "gols_casa", "gols_fora", "Data_Hora"])
except Exception:
    df_existente = pd.DataFrame(columns=["Nome", "Jogo", "gols_casa", "gols_fora", "Data_Hora"])

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
                    
                    # 🕒 CAPTURA E CONFIGURAÇÃO DO FUSO HORÁRIO DE SÃO PAULO (UTC -3)
                    fuso_sp = timezone(timedelta(hours=-3))
                    agora_sp = datetime.now(fuso_sp)
                    data_hora_formatada = agora_sp.strftime("%d/%m/%Y %H:%M:%S")
                    
                    novo_palpite = {
                        "Nome": nome_unificado,
                        "Jogo": jogo_selecionado,
                        "gols_casa": int(gols_brasil),
                        "gols_fora": int(gols_adversario),
                        "Data_Hora": data_hora_formatada
                    }
                    
                    df_novo = pd.DataFrame([novo_palpite])
                    df_atualizado = pd.concat([df_existente, df_novo], ignore_index=True)
                    
                    try:
                        conn.update(data=df_atualizado)
                        st.success(f"Palpite de {nome_unificado} guardado com sucesso às {data_hora_formatada}!")
                        st.rerun()
                    except Exception as e:
                        st.error("Erro ao conectar com o banco de dados. Tente novamente.")

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
        
        if pd.isna(nome_func) or pd.isna(jogo_func):
            continue
            
        resultado_real = st.session_state.jogos.get(jogo_func, {"real_casa": None, "real_fora": None})
        r_c = resultado_real["real_casa"]
        r_f = resultado_real["real_fora"]
        
        pts = calcular_pontos(int(p["gols_casa"]), int(p["gols_fora"]), r_c, r_f)
        
        if nome_func not in pontuacao_geral:
            pontuacao_geral[nome_func] = 0
        pontuacao_geral[nome_func] += pts

    if pontuacao_geral:
        df_ranking = pd.DataFrame(list(pontuacao_geral.items()), columns=["Colaborador Homedock", "Pontuacao Total"])
        df_ranking = df_ranking.sort_values(by="Pontuacao Total", ascending=False).reset_index(drop=True)
        df_ranking.index = df_ranking.index + 1
        st.dataframe(df_ranking, use_container_width=True)
        
        # 📊 TABELA EXTRA: Histórico completo de palpites em tempo real com data e hora
        st.markdown("### 📋 Histórico Detalhado de Envio")
        if not df_existente.empty:
            # Reorganiza o dataframe existente para exibição elegante
            df_display = df_existente.copy()
            df_display.columns = ["Colaborador", "Partida", "Gols Casa", "Gols Fora", "Momento do Palpite (Fuso SP)"]
            st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Nenhum palpite enviado ate o momento.")

# --- ABA 3: ADMINISTRADOR ---
with aba_admin:
    st.subheader("Painel de Controle Exclusivo")
    senha_admin = st.text_input("Digite a senha master:", type="password")
    
    if senha_admin == "hmdk":
        st.success("Acesso Liberado!")
        for jogo, resultados in st.session_state.jogos.items():
            st.markdown(f"**{jogo}**")
            col1, col2, col3 = st.columns([2, 2, 1])
            val_casa = resultados["real_casa"] if resultados["real_casa"] is not None else 0
            val_fora = resultados["real_fora"] if resultados["real_fora"] is not None else 0
            
            with col1:
                res_casa = st.number_input("Placar Real Brasil:", min_value=0, value=val_casa, key=f"rc_{jogo}")
            with col2:
                res_fora = st.number_input("Placar Real Adversario:", min_value=0, value=val_fora, key=f"rf_{jogo}")
            with col3:
                st.write("")
                st.write("")
                if st.button("Confirmar", key=f"btn_{jogo}"):
                    st.session_state.jogos[jogo]["real_casa"] = res_casa
                    st.session_state.jogos[jogo]["real_fora"] = res_fora
                    st.success("Placar updated!")
                    st.rerun()
            st.markdown("---")

        st.subheader("➕ Adicionar Jogo do Brasil")
        novo_jogo = st.text_input("Exemplo: Oitavas de Final: Brasil x Alemanha")
        if st.button("Inserir Nova Partida"):
            if novo_jogo:
                st.session_state.jogos[novo_jogo] = {"real_casa": None, "real_fora": None}
                st.success("Jogo adicionado!")
                st.rerun()
