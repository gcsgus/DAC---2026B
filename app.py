# ------------------------------------------------------------
# app.py
# objetivo: interface do projeto, que mostra se a educação pública de MS está evoluindo.
# o que faz: busca os dados no banco PostgreSQL, deixa escolher município e período
# e mostra gráficos das taxas de aprovação e abandono, com um resumo da evolução.
# como abrir: py -m streamlit run app.py
# ------------------------------------------------------------

# importa o pandas, que lê e organiza tabelas
import pandas as pd
# importa o streamlit, que monta a página web
import streamlit as st
# importa a função de conexão criada no conexao.py
from conexao import conectar

# define o título da aba do navegador e deixa a página mais larga
st.set_page_config(page_title="Educação pública de MS", layout="wide")

# O @st.cache_data guarda o resultado da função abaixo, para não consultar o banco a cada clique.
@st.cache_data
def carregar_dados():
    # abre a conexão com o banco
    with conectar() as conexao:
        # cria o cursor, que envia comandos SQL
        with conexao.cursor() as cursor:
            # junta as três tabelas: cada indicador vem com o nome da escola e do município
            cursor.execute(
                "SELECT m.nome, e.nome, i.ano, i.aprovados, i.reprovados, i.abandono, i.cursando "
                "FROM indicadores_anuais i "
                "JOIN escolas e ON e.id_escola = i.id_escola "
                "JOIN municipios m ON m.id_municipio = e.id_municipio"
            )
            # guarda todas as linhas devolvidas pelo banco
            linhas = cursor.fetchall()
    # define os nomes das colunas, na mesma ordem do SELECT
    colunas = ["municipio", "escola", "ano", "aprovados", "reprovados", "abandono", "cursando"]
    # transforma as linhas numa tabela do pandas e devolve
    return pd.DataFrame(linhas, columns=colunas)

# carrega os dados do banco para a memória.
dados = carregar_dados()

# escreve o título e uma frase explicativa na página.
st.title("Evolução da educação pública em Mato Grosso do Sul")
st.write("Taxas de aprovação e de abandono escolar nas escolas da rede pública, por ano.")

# ---- FILTROS ----
# monta a lista de opções: "Todos" primeiro e depois os municípios em ordem alfabética
lista_municipios = ["Todos os municípios"] + sorted(dados["municipio"].unique())
# cria a caixa de seleção do município
municipio = st.selectbox("Município", lista_municipios)

# monta a lista dos anos que existem nos dados, em ordem
anos = sorted(int(a) for a in dados["ano"].unique())
# cria a barra de período, começando em 2018 e terminando em 2023 (anos com resultado final registrado)
inicio, fim = st.select_slider("Período", options=anos, value=(anos[0], 2023))

# mantém só as linhas dos anos escolhidos
filtrado = dados[(dados["ano"] >= inicio) & (dados["ano"] <= fim)]
# se o usuário escolheu um município específico, mantém só as linhas dele
if municipio != "Todos os municípios":
    filtrado = filtrado[filtrado["municipio"] == municipio]

# ---- CÁLCULOS ----
# soma os alunos de todas as escolas, ano a ano
por_ano = filtrado.groupby("ano")[["aprovados", "reprovados", "abandono", "cursando"]].sum()

# total de alunos com resultado final: aprovados + reprovados, igual para todos os anos
total = por_ano["aprovados"] + por_ano["reprovados"]
# se o total for zero, deixa vazio para não dividir por zero
total = total.where(total > 0)

# taxa de aprovação: aprovados dividido pelo total, vezes 100
por_ano["Aprovação (%)"] = por_ano["aprovados"] / total * 100
# taxa de abandono, como informada nos arquivos, sobre quem teve resultado final ou abandonou
por_ano["Abandono (%)"] = por_ano["abandono"] / (total + por_ano["abandono"]) * 100

# anos em que há mais alunos cursando do que alunos com resultado final ainda estão em andamento
# nesses anos, apaga as duas taxas para não mostrar números enganosos
por_ano.loc[por_ano["cursando"] > total, ["Aprovação (%)", "Abandono (%)"]] = float("nan")
# anos em que o abandono somado é zero não têm registro confiável desse dado, então apaga a taxa de abandono deles
por_ano.loc[por_ano["abandono"] == 0, "Abandono (%)"] = float("nan")

# ---- GRÁFICOS ----
# separa só as duas taxas e transforma os anos em texto, para o gráfico não escrever "2,018"
grafico = por_ano[["Aprovação (%)", "Abandono (%)"]].copy()
grafico.index = grafico.index.astype(str)

# divide a página em duas colunas lado a lado
col1, col2 = st.columns(2)
# na primeira coluna, mostra o gráfico de aprovação
with col1:
    st.subheader("Taxa de aprovação (%)")
    st.line_chart(grafico["Aprovação (%)"])
# na segunda coluna, mostra o gráfico de abandono
with col2:
    st.subheader("Taxa de abandono (%)")
    st.line_chart(grafico["Abandono (%)"])

# ---------- RESUMO DA EVOLUÇÃO ----------
# aviso fixo sobre o abandono, porque os arquivos não trazem esse dado de forma confiável
st.warning(
    "Atenção sobre o abandono: nos arquivos originais, essa coluna só tem valores em 2018 e 2019 "
    "e vem zerada de 2020 em diante. Por isso a evolução do abandono não é confiável, "
    "e o resumo abaixo trata apenas da aprovação."
)
# descarta anos sem taxa de aprovação calculada (olhando só a coluna de aprovação)
validos = por_ano.dropna(subset=["Aprovação (%)"])
# só faz o resumo se houver pelo menos dois anos para comparar
if len(validos) >= 2:
    # pega a primeira e a última linha do período e seus anos
    primeiro = validos.iloc[0]
    ultimo = validos.iloc[-1]
    ano_ini = validos.index[0]
    ano_fim = validos.index[-1]
    # calcula quanto a aprovação mudou, em pontos percentuais.
    dif_aprov = ultimo["Aprovação (%)"] - primeiro["Aprovação (%)"]
    # escreve a frase com o resultado.
    st.write(
        f"Entre {ano_ini} e {ano_fim}, a taxa de aprovação {'subiu' if dif_aprov > 0 else 'caiu'} "
        f"{abs(dif_aprov):.1f} pontos percentuais."
    )
    # mostra uma caixa verde se subiu e vermelha se caiu.
    if dif_aprov > 0:
        st.success("Sinal de melhora na aprovação no período.")
    else:
        st.error("Sinal de queda na aprovação no período.")
else:
    st.info("Escolha um período com pelo menos dois anos com resultado final para ver a evolução.")

# avisa sobre 2026 quando ele estiver incluído no período
if fim == 2026:
    st.caption("Atenção: 2026 pode estar em andamento, então parte dos alunos ainda aparece como cursando e os resultados finais podem estar incompletos.")

# ---- TABELA ----
# mostra os números de cada ano, com duas casas decimais
st.subheader("Números por ano")
st.dataframe(por_ano.round(2))