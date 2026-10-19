import pandas as pd
from pathlib import Path

pasta = Path("planilhas dos anos")  # pasta onde estão os arquivos csv

tabelas = []  # lista para guardar as tabelas lidas

# repete o bloco para cada csv da pasta, em ordem alfabética
for arquivo in sorted(pasta.glob("*.csv")):
    # tenta ler o arquivo com a codificação mais comum (utf-8-sig)  
    try:
        tabela = pd.read_csv(arquivo, sep=None, engine="python", encoding="utf-8-sig")
    # se der erro de leitura, tenta com outra codificação (latin-1)
    except UnicodeDecodeError:
        tabela = pd.read_csv(arquivo, sep=None, engine="python", encoding="latin-1")
    # adiciona a tabela lida à lista de tabelas
    tabelas.append(tabela)

# empilha todas as tabelas da lista em uma só.
# ignore_index refaz as numerações das linhas 
dados = pd.concat(tabelas, ignore_index=True)

# remove a coluna _id que só numera as linhas dentro de cada arquivo 
dados = dados.drop(columns=["_id"])

# troca os nomes das colunas por nomes curtos, para facilitar a digitação depois
dados = dados.rename(columns={
    "AnoReferencia": "ano",
    "NomeMunicipio": "municipio",
    "NomeUnidadeEscolar": "escola",
    "MatriculasTotal": "matriculas_total",
    "MatriculaInicial": "matricula_inicial",
    "MatriculaAposCenso": "matricula_apos_censo",
    "Transferidos": "transferidos",
    "Cancelados": "cancelados",
    "Falecido": "falecidos",
    "Abandono": "abandono",
    "Aprovados": "aprovados",
    "Reprovados": "reprovados",
    "Cursando": "cursando",
    "OutrasSituacoes": "outras_situacoes",
})

# tira espaços sobrando e deixa em maiúsculas os nomes de município e escola, para não haver diferenças entre anos
dados["municipio"] = dados["municipio"].str.strip().str.upper()
dados["escola"] = dados["escola"].str.strip().str.upper()

# lista as colunas que devem ser números 
colunas_numericas = ["ano", "matriculas_total", "matricula_inicial", "matricula_apos_censo",
                     "transferidos", "cancelados", "falecidos", "abandono",
                     "aprovados", "reprovados", "cursando", "outras_situacoes"]

# converte as colunas para números. o que não for número vira vazio
for coluna in colunas_numericas:
    dados[coluna] = pd.to_numeric(dados[coluna], errors="coerce")

# mostra quantas linhas e colunas a tabela final tem
print("quantidade de linhas e colunas:")
print(dados.shape)
# mostra quantas linhas existem por ano, em ordem de ano
print("quantidade de linhas por ano:")
print(dados["ano"].value_counts().sort_index())
# mostra quantos valores vazios existem em cada coluna 
print("quantidade de valores vazios por coluna:")
print(dados.isna().sum())

# salva a tabela tratada num novo csv, sem a coluna de numeração do pandas 
dados.to_csv("planilhas dos anos/dados_tratados.csv", index=False, encoding="utf-8-sig")