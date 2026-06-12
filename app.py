import streamlit as st
import pandas as pd
from PIL import Image
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Bolão Homedock - Jogos do Brasil", 
    page_icon="⚽", 
    layout="wide"
)

# Estilização customizada com a identidade visual da Homedock
st.markdown("""
    <style>
    /* Fundo Off-white e fontes mais limpas */
    .stApp {
        background-color: #FAF9F6;
        color: #111111;
    }
    /* Estilo dos títulos principais */
    h1, h2, h3 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #111111 !important;
        font-weight: 700 !important;
    }
    /* Botão principal com a cor preta da Homedock */
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
    /* Abas customizadas */
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

# 2. TOPO COM LOGO DA HOMEDOCK
col_logo, col_titulo = st.columns([1, 3])
with col_logo:
    # Tenta carregar a imagem do logo enviada
    if os.path.exists("image_27b81c.png"):
        logo = Image.open("image_27b81c.png")
        st.image(logo, use_container_width=True)
    else:
        st.subheader("HOMEDOCK")

with col_titulo:
    st.markdown("<h1 style='margin-bottom: 0; padding-top: 5px;'>🏆 BOLÃO DOS FUNCIONÁRIOS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #C5A880; font-weight: 600; tracking: 2px; font-size: 13px; text-transform: uppercase; margin-top: 0;'>Arena de Integração Corporativa - Brasil rumo ao topo</p>", unsafe_allow_html=True)

st.markdown("---")

# 3. BANCO DE DADOS EM MEMÓRIA (Sessão do Streamlit)
if "jogos" not in st.session_state:
    st.session_state.jogos = {
        "Fase de Grupos: Brasil 🇧🇷 x 🇷🇸 Sérvia": {"real_casa": None, "real_fora": None},
        "Fase de Grupos: Brasil 🇧🇷 x 🇨🇭 Suíça": {"real_casa": None, "real_fora": None},
        "Fase de Grupos: Brasil 🇧🇷 x 🇨🇲 Camarões": {"real_casa": None, "real_fora": None},
    }

if "palpites" not in st.session_state:
    # Exemplos iniciais
    st.session_state.palpites = [
        {"Nome": "Daniela (CEO)", "Jogo": "Fase de Grupos: Brasil 🇧🇷 x 🇷🇸 Sérvia", "gols_casa": 3, "gols_fora": 1},
        {"Nome": "Lucas Medeiros", "Jogo": "Fase de Grupos: Brasil 🇧🇷 x 🇷🇸 Sérvia", "gols_casa": 2, "gols_fora": 0},
    ]

# 4. FUNÇÃO DE REGRAS DE PONTOS (6 para cheio, 3 para vencedor/empate)
def calcular_pontos(p_casa, p_fora, r_casa, r_fora):
    if r_casa is None or r_fora is None:
        return 0 
    
    # Acerto do Placar Exato -> 6 pontos
    if p_casa == r_casa and p_fora == r_fora:
        return 6
        
    # Verificação de quem ganhou/empatou -> 3 pontos
    vencedor_palpite = "casa" if p_casa > p_fora else ("fora" if p_fora > p_casa else "empate")
    vencedor_real = "casa" if r_casa > r_fora else ("fora" if r_fora > r_casa else "empate")
    
    if vencedor_palpite == vencedor_real:
        return 3
        
    return 0

# 5. QUADRO DE REGRAS VISUAL
st.markdown("""
<div style='background-color: #white; padding: 20px; border-radius: 15px; border: 1px solid #E5E5E5; margin-bottom: 25px;'>
    <h4 style='margin-top:0; color:#111;'>📋 Regulamento de Pontuação Homedock:</h4>
    <span style='background-color:#111; color:white; padding: 3px 10px; border-radius: 5px; font-weight:bold; font-size:12px; margin-right:10px;'>6 PONTOS</span> Acerto exato do placar (Ex: Palpite 2x1 | Resultado 2x1)<br>
    <span style='background-color:#C5A880; color:white; padding: 3px 10px; border-radius: 5px; font-weight:bold; font-size:12px; margin-right:10px; margin-top:5px; display:inline-block;'>3 PONTOS</span> Acerto do vencedor ou do empate errando o placar (Ex: Palpite 1x0 | Resultado 3x1)
</div>
""", unsafe_allow_html=True)

# 6. CRIAÇÃO DAS ABAS DO APP
aba_palpites, aba_ranking, aba_admin = st.tabs(["📝 Dar Palpite", "📊 Classificação Geral", "⚙️ Painel do Administrador"])

# --- ABA 1: PALPITES ---
with aba_palpites:
    st.subheader("Registre o seu palpite")
    with st.form("form_palpite", clear_on_submit=True):
        nome = st.text_input("Seu Nome Completo:")
        jogo_selecionado = st.selectbox("Escolha a partida:", list(st.session_state.jogos.keys()))
        
        col1, col2 = st.columns(2)
        with col1:
            gols_brasil = st.number_input("Gols do Brasil:", min_value=0, max_value=15, value=1, step=1)
        with col2:
            gols_adversario = st.number_input("Gols do Adversário:", min_value=0, max_value=15, value=0, step=1)
            
        enviar = st.form_submit_button("Salvar Palpite 🚀")
        
        if enviar:
            if nome.strip() == "":
                st.error("Por favor, digite seu nome antes de enviar o palpite.")
            else:
                # Substitui palpite anterior se o mesmo usuário mandar pro mesmo jogo
                st.session_state.palpites = [p for p in st.session_state.palpites if not (p["Nome"].lower() == nome.strip().lower() and p["Jogo"] == jogo_selecionado)]
                st.session_state.palpites.append({
                    "Nome": nome.strip(),
                    "Jogo": jogo_selecionado,
                    "gols_casa": gols_brasil,
                    "gols_fora": gols_adversario
                })
                st.success(f"Palpite de {nome} para '{jogo_selecionado}' registrado com sucesso!")

# --- ABA 2: RANKING ---
with aba_ranking:
    st.subheader("Classificação Atualizada dos Colaboradores")
    
    pontuacao_geral = {}
    for p in st.session_state.palpites:
        nome_func = p["Nome"]
        jogo_func = p["Jogo"]
        
        resultado_real = st.session_state.jogos.get(jogo_func, {"real_casa": None, "real_fora": None})
        r_c = resultado_real["real_casa"]
        r_f = resultado_real["real_fora"]
        
        pts = calcular_pontos(p["gols_casa"], p["gols_fora"], r_c, r_f)
        
        if nome_func not in pontuacao_geral:
            pontuacao_geral[nome_func] = 0
        pontuacao_geral[nome_func] += pts

    if pontuacao_geral:
        df_ranking = pd.DataFrame(list(pontuacao_geral.items()), columns=["Colaborador Homedock", "Pontuação Total"])
        df_ranking = df_ranking.sort_values(by="Pontuação Total", ascending=False).reset_index(drop=True)
        df_ranking.index = df_ranking.index + 1
        st.dataframe(df_ranking, use_container_width=True)
    else:
        st.info("Nenhum palpite enviado ou processado até o momento.")

# --- ABA 3: ADMINISTRADOR ---
with aba_admin:
    st.subheader("Painel de Controle Exclusivo")
    st.write("Atualize os resultados reais abaixo para que o sistema mude o ranking na hora.")
    
    for jogo, resultados in st.session_state.jogos.items():
        st.markdown(f"**{jogo}**")
        col1, col2, col3 = st.columns([2, 2, 1])
        
        val_casa = resultados["real_casa"] if resultados["real_casa"] is not None else 0
        val_fora = resultados["real_fora"] if resultados["real_fora"] is not None else 0
        
        with col1:
            res_casa = st.number_input("Placar Real Brasil:", min_value=0, value=val_casa, key=f"rc_{jogo}")
        with col2:
            res_fora = st.number_input("Placar Real Adversário:", min_value=0, value=val_fora, key=f"rf_{jogo}")
        with col3:
            st.write("")
            st.write("")
            if st.button("Confirmar", key=f"btn_{jogo}"):
                st.session_state.jogos[jogo]["real_casa"] = res_casa
                st.session_state.jogos[jogo]["real_fora"] = res_fora
                st.success("Placar atualizado!")
                st.rerun()
        st.markdown("---")

    # MATA-MATA (Adicionar novas fases)
    st.subheader("➕ Adicionar Jogo do Brasil (Próximas Fases)")
    novo_jogo = st.text_input("Exemplo: Oitavas de Final: Brasil 🇧🇷 x 🇩🇪 Alemanha")
    if st.button("Inserir Nova Partida no Sistema"):
        if novo_jogo:
            st.session_state.jogos[novo_jogo] = {"real_casa": None, "real_fora": None}
            st.success(f"'{novo_jogo}' adicionado com sucesso nas opções de palpites!")
            st.rerun()