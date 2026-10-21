# ------------------------------------------------------------
# verificar.py
# objetivo: checar se a combinação ano + município + escola se repete
# no arquivo dados_tratados.csv.
# o que faz: procura linhas duplicadas e mostra algumas no terminal.
# por que existe: os CSVs não têm código único de escola, então
# precisamos saber se o nome basta para identificar cada registro
# antes de montar as tabelas do banco de dados.
# ------------------------------------------------------------

import pandas as pd 

dados = pd.read_csv("dados_tratados.csv")  # lê o arquivo gerado pelo tratar.py

# marca as linhas em que a combinação ano + município + escola aparece mais de uma vez
# o keep=False faz o pandas mostrar todas as repetidas, e não só as extras
repetidas = dados[dados.duplicated(subset=["ano", "municipio", "escola"], keep=False)]

# mostra quantas linhas repetidas foram encontradas
print("linhas repetidas:", len(repetidas))
# mostra algumas delas, em ordem, só com as colunas principais para ficar legível.
print(repetidas.sort_values(["ano", "municipio", "escola"])[["ano", "municipio", "escola", "matriculas_total"]].head(20))

