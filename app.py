import streamlit as st
import pandas as pd
import urllib.parse

# ==========================
# CONFIG
# ==========================

st.set_page_config(
    page_title="Bolão Homedock 2026",
    page_icon="⚽",
    layout="wide"
)

PALPITES_URL = "https://docs.google.com/spreadsheets/d/1S0ch85t9DDzNJZXp5mZFSdNv4Em6An51MN_tYHRZCN8/export?format=csv&gid=0"

RESULTADOS_URL = "https://docs.google.com/spreadsheets/d/1S0ch85t9DDzNJZXp5mZFSdNv4Em6An51MN_tYHRZCN8/export?format=csv&gid=1201181236"

FORM_ID = "1FAIpQLSe0o0aZx7k8XhGZ0C4C-AENyJU-B7943JDfjJosULfTOlWFww"

ENTRY_NOME = "entry.357942348"
ENTRY_JOGO = "entry.1347005369"
ENTRY_CASA = "entry.1938823404"
ENTRY_FORA = "entry.1888761423"

# ==========================
# ESTILO
# ==========================

st.markdown("""
<style>

.stApp{
    background:#FAF9F6;
}

h1,h2,h3{
    color:#111111;
}

.btn-enviar{
    display:inline-block;
    padding:12px 24px;
    background:#111111;
    color:white !important;
    text-decoration:none;
    border-radius:10px;
    font-weight:600;
}

</style>
""", unsafe_allow_html=True)

# ==========================
# FUNÇÕES
# ==========================

@st.cache_data(ttl=60)
def carregar_palpites():
    return pd.read_csv(PALPITES_URL)

@st.cache_data(ttl=60)
def carregar_resultados():
    return pd.read_csv(RESULTADOS_URL)

def calcular_pontos(
    palpite_casa,
    palpite_fora,
    real_casa,
    real_fora
):

    try:

        palpite_casa = int(palpite_casa)
        palpite_fora = int(palpite_fora)

        real_casa = int(real_casa)
        real_fora = int(real_fora)

    except:
        return 0

    if (
        palpite_casa == real_casa
        and
        palpite_fora == real_fora
    ):
        return 6

    resultado_palpite = (
        "casa"
        if palpite_casa > palpite_fora
        else "fora"
        if palpite_fora > palpite_casa
        else "empate"
    )

    resultado_real = (
        "casa"
        if real_casa > real_fora
        else "fora"
        if real_fora > real_casa
        else "empate"
    )

    if resultado_palpite == resultado_real:
        return 3

    return 0

# ==========================
# DADOS
# ==========================

try:
    palpites = carregar_palpites()
except:
    palpites = pd.DataFrame()

try:
    resultados = carregar_resultados()
except:
    resultados = pd.DataFrame()

# ==========================
# HEADER
# ==========================

st.title("🏆 Bolão Homedock 2026")

st.markdown(
    """
    **Pontuação**

    ✅ 6 pontos = placar exato

    ✅ 3 pontos = vencedor correto

    ✅ 0 ponto = erro
    """
)

# ==========================
# ABAS
# ==========================

aba1, aba2 = st.tabs(
    [
        "📝 Dar Palpite",
        "📊 Classificação"
    ]
)

# ==========================
# PALPITE
# ==========================

with aba1:

    jogos = []

    if not resultados.empty:

        jogos = resultados["Jogo"].tolist()

    else:

        jogos = [
            "Fase de Grupos: Brasil x Marrocos",
            "Fase de Grupos: Brasil x Haiti",
            "Fase de Grupos: Brasil x Escocia"
        ]

    nome = st.text_input(
        "Nome completo"
    )

    jogo = st.selectbox(
        "Escolha a partida",
        jogos
    )

    c1,c2 = st.columns(2)

    with c1:
        gols_brasil = st.number_input(
            "Gols Brasil",
            min_value=0,
            max_value=20,
            value=1
        )

    with c2:
        gols_adv = st.number_input(
            "Gols Adversário",
            min_value=0,
            max_value=20,
            value=0
        )

    if nome:

        duplicado = False

        if not palpites.empty:

            duplicado = (
                (
                    palpites["Nome"]
                    .astype(str)
                    .str.lower()
                    ==
                    nome.lower()
                )
                &
                (
                    palpites["Jogo"]
                    ==
                    jogo
                )
            ).any()

        if duplicado:

            st.error(
                "Você já enviou um palpite para esta partida."
            )

        else:

            params = {

                ENTRY_NOME: nome,

                ENTRY_JOGO: jogo,

                ENTRY_CASA: int(gols_brasil),

                ENTRY_FORA: int(gols_adv)

            }

            url_form = (
                f"https://docs.google.com/forms/d/e/{FORM_ID}/viewform?"
                f"usp=pp_url&{urllib.parse.urlencode(params)}"
            )

            st.markdown(
                f"""
                <a
                    href="{url_form}"
                    target="_blank"
                    class="btn-enviar"
                >
                Confirmar Palpite 🚀
                </a>
                """,
                unsafe_allow_html=True
            )

# ==========================
# RANKING
# ==========================

with aba2:

    if palpites.empty:

        st.warning(
            "Nenhum palpite encontrado."
        )

    else:

        ranking = {}

        mapa_resultados = {}

        if not resultados.empty:

            for _, row in resultados.iterrows():

                mapa_resultados[
                    row["Jogo"]
                ] = (
                    row["Gols_Brasil"],
                    row["Gols_Adversario"]
                )

        for _, row in palpites.iterrows():

            nome = str(
                row["Nome"]
            ).strip()

            jogo = row["Jogo"]

            if jogo not in mapa_resultados:
                continue

            real_casa, real_fora = mapa_resultados[jogo]

            pontos = calcular_pontos(
                row["gols_casa"],
                row["gols_fora"],
                real_casa,
                real_fora
            )

            ranking[nome] = (
                ranking.get(nome,0)
                + pontos
            )

        if ranking:

            df_ranking = pd.DataFrame(
                list(ranking.items()),
                columns=[
                    "Participante",
                    "Pontos"
                ]
            )

            df_ranking = (
                df_ranking
                .sort_values(
                    "Pontos",
                    ascending=False
                )
                .reset_index(drop=True)
            )

            df_ranking.index += 1

            st.dataframe(
                df_ranking,
                use_container_width=True
            )

        else:

            st.info(
                "Ainda não existem resultados oficiais cadastrados."
            )
