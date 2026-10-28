# ------------------------------------------------------------
# educacao.py
# objetivo: reunir as classes do projeto (orientação a objetos).
# repositorioEscolar: busca os dados no banco PostgreSQL.
# analiseEducacional: filtra os dados e calcula as taxas e o resumo.
# por que existe: separar o acesso ao banco, os cálculos e a interface (app.py),
# deixando cada parte com uma única responsabilidade.
# ------------------------------------------------------------

# importa o pandas, que lê e organiza tabelas
import pandas as pd
# importa a função de conexão que criamos no conexao.py
from conexao import conectar


# classe responsável por buscar os dados no banco de dados
class RepositorioEscolar:
    # atributo da classe: o comando SQL que junta as três tabelas
    CONSULTA = (
        "SELECT m.nome, e.nome, i.ano, i.aprovados, i.reprovados, i.abandono, i.cursando "
        "FROM indicadores_anuais i "
        "JOIN escolas e ON e.id_escola = i.id_escola "
        "JOIN municipios m ON m.id_municipio = e.id_municipio"
    )
    # atributo da classe: nomes das colunas, na mesma ordem do SELECT
    COLUNAS = ["municipio", "escola", "ano", "aprovados", "reprovados", "abandono", "cursando"]

    # método que busca os dados no banco e devolve uma tabela do pandas
    def carregar_dados(self):
        # abre a conexão com o banco
        with conectar() as conexao:
            # cria o cursor, que envia comandos SQL
            with conexao.cursor() as cursor:
                # executa a consulta guardada no atributo CONSULTA
                cursor.execute(self.CONSULTA)
                # guarda todas as linhas devolvidas pelo banco
                linhas = cursor.fetchall()
        # transforma as linhas numa tabela do pandas e devolve
        return pd.DataFrame(linhas, columns=self.COLUNAS)


# classe responsável por filtrar os dados e calcular os indicadores
class AnaliseEducacional:
    # atributo da classe: o texto da opção que representa todos os municípios
    TODOS = "Todos os municípios"

    # construtor: roda quando criamos um objeto da classe e guarda os dados dentro dele
    def __init__(self, dados):
        # guarda a tabela recebida num atributo do objeto
        self.dados = dados

    # método que devolve a lista de opções do filtro de município
    def lista_municipios(self):
        # "Todos" primeiro e depois os municípios em ordem alfabética.
        return [self.TODOS] + sorted(self.dados["municipio"].unique())

    # método que devolve a lista de anos que existem nos dados
    def lista_anos(self):
        # pega os anos sem repetição, converte para inteiro e ordena
        return sorted(int(a) for a in self.dados["ano"].unique())

    # método que aplica os filtros de município e de período
    def filtrar(self, municipio, inicio, fim):
        # mantém só as linhas dos anos escolhidos
        filtrado = self.dados[(self.dados["ano"] >= inicio) & (self.dados["ano"] <= fim)]
        # se foi escolhido um município específico, mantém só as linhas dele
        if municipio != self.TODOS:
            filtrado = filtrado[filtrado["municipio"] == municipio]
        # devolve a tabela já filtrada
        return filtrado

    # método que soma os alunos por ano e calcula as taxas de aprovação e abandono
    def calcular_taxas(self, filtrado):
        # soma os alunos de todas as escolas, ano a ano
        por_ano = filtrado.groupby("ano")[["aprovados", "reprovados", "abandono", "cursando"]].sum()
        # total de alunos com resultado final: aprovados + reprovados, igual para todos os anos
        total = por_ano["aprovados"] + por_ano["reprovados"]
        # se o total for zero, deixa vazio para não dividir por zero
        total = total.where(total > 0)
        # taxa de aprovação: aprovados dividido pelo total, vezes 100
        por_ano["Aprovação (%)"] = por_ano["aprovados"] / total * 100
        # taxa de abandono, como informada nos arquivos
        por_ano["Abandono (%)"] = por_ano["abandono"] / (total + por_ano["abandono"]) * 100
        # anos com mais alunos cursando do que com resultado final ainda estão em andamento: apaga as taxas
        por_ano.loc[por_ano["cursando"] > total, ["Aprovação (%)", "Abandono (%)"]] = float("nan")
        # anos com abandono zerado não têm registro confiável: apaga a taxa de abandono
        por_ano.loc[por_ano["abandono"] == 0, "Abandono (%)"] = float("nan")
        # devolve a tabela com os números e as taxas de cada ano
        return por_ano

    # método que compara o primeiro e o último ano válidos e resume a evolução da aprovação.
    def resumir(self, por_ano):
        # descarta anos sem taxa de aprovação calculada
        validos = por_ano.dropna(subset=["Aprovação (%)"])
        # sem pelo menos dois anos não há o que comparar
        if len(validos) < 2:
            return None
        # pega a primeira e a última linha do período
        primeiro = validos.iloc[0]
        ultimo = validos.iloc[-1]
        # devolve um dicionário com os anos e a variação da aprovação, em pontos percentuais
        return {
            "ano_ini": validos.index[0],
            "ano_fim": validos.index[-1],
            "dif_aprov": ultimo["Aprovação (%)"] - primeiro["Aprovação (%)"],
        }