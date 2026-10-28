# ------------------------------------------------------------
# app.py
# objetivo: interface do projeto, que mostra se a educação pública de ms está evoluindo
# o que faz: usa as classes de educacao.py para buscar os dados no banco, filtrar por
# município e período e calcular as taxas, e mostra gráficos, resumo e tabela
# como abrir: py -m streamlit run app.py
# ------------------------------------------------------------

# importa o streamlit, que monta a página web ("st" é o apelido curto)
import streamlit as st
# importa as duas classes do arquivo educacao.py
from educacao import RepositorioEscolar, AnaliseEducacional

# define o título da aba do navegador e deixa a página mais larga
st.set_page_config(page_title="Educação pública de MS", layout="wide")


# o @st.cache_data guarda o resultado da função abaixo, para não consultar o banco a cada clique
@st.cache_data
def carregar_dados():
    # cria um objeto da classe RepositorioEscolar
    repositorio = RepositorioEscolar()
    # pede ao objeto que busque os dados no banco e devolve o resultado
    return repositorio.carregar_dados()


# carrega os dados do banco para a memória
dados = carregar_dados()
# cria um objeto da classe AnaliseEducacional, entregando a ele os dados
analise = AnaliseEducacional(dados)

# escreve o título e uma frase explicativa na página
st.title("Evolução da educação pública em Mato Grosso do Sul")
st.write("Taxas de aprovação e de abandono escolar nas escolas da rede pública, por ano.")

# ---------- filtros ----------
# cria a caixa de seleção do município, com as opções que o objeto fornece
municipio = st.selectbox("Município", analise.lista_municipios())
# pede ao objeto a lista de anos disponíveis
anos = analise.lista_anos()
# cria a barra de período, começando em 2018 e terminando em 2023 (anos com resultado final registrado)
inicio, fim = st.select_slider("Período", options=anos, value=(anos[0], 2023))

# ---------- cálculos ----------
# pede ao objeto os dados já filtrados por município e período
filtrado = analise.filtrar(municipio, inicio, fim)
# pede ao objeto as somas e as taxas de cada ano
por_ano = analise.calcular_taxas(filtrado)

# ---------- gráficos ----------
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

# ---------- resumo da evolução ----------
# aviso fixo sobre o abandono, porque os arquivos não trazem esse dado de forma confiável
st.warning(
    "Atenção sobre o abandono: nos arquivos originais, essa coluna só tem valores em 2018 e 2019 "
    "e vem zerada de 2020 em diante. Por isso a evolução do abandono não é confiável, "
    "e o resumo abaixo trata apenas da aprovação."
)
# pede ao objeto o resumo da evolução da aprovação
resumo = analise.resumir(por_ano)
# se o resumo existe (há pelo menos dois anos válidos), mostra o texto
if resumo is not None:
    # guarda a variação da aprovação numa variável mais curta
    dif_aprov = resumo["dif_aprov"]
    # escreve a frase com o resultado
    st.write(
        f"Entre {resumo['ano_ini']} e {resumo['ano_fim']}, a taxa de aprovação "
        f"{'subiu' if dif_aprov > 0 else 'caiu'} {abs(dif_aprov):.1f} pontos percentuais."
    )
    # mostra uma caixa verde se subiu e vermelha se caiu
    if dif_aprov > 0:
        st.success("Sinal de melhora na aprovação no período.")
    else:
        st.error("Sinal de queda na aprovação no período.")
else:
    st.info("Escolha um período com pelo menos dois anos com resultado final para ver a evolução.")

# avisa sobre 2026 quando ele estiver incluído no período
if fim == 2026:
    st.caption("Atenção: 2026 pode estar em andamento, então parte dos alunos ainda aparece como cursando e os resultados finais podem estar incompletos.")

# ---------- tabela ----------
# mostra os números de cada ano, com duas casas decimais
st.subheader("Números por ano")
st.dataframe(por_ano.round(2))