# biblioteca pandas para ler e organizar tabelas
import pandas as pd 
# path para trabalhar com pastas e nomes de arquivos
from pathlib import Path 

pasta = Path("planilhas dos anos")  # pasta onde estão os arquivos csv

# procura todos os arquivos csv na pasta atual e repete o bloco abaixo para cada um, em ordem alfabética
for arquivo in sorted(pasta.glob("*.csv")):
    try:
        # lê o CSV. sep=None pede ao programa para descobrir sozinho o separador 
        tabela = pd.read_csv(arquivo, sep=None, engine="python", encoding="utf-8-sig")
    # se os acentos derem erro de leitura, cai aqui.
    except UnicodeDecodeError:
        # lê de novo usando outra codificação de texto, comum em arquivos de órgãos públicos.
        tabela = pd.read_csv(arquivo, sep=None, engine="python", encoding="latin-1")
    # mostra na tela o nome do arquivo e quantas linhas ele tem.
    print(arquivo.name, "-", len(tabela), "linhas")
    # mostra a lista com os nomes das colunas do arquivo.
    print(list(tabela.columns))
    # imprime uma linha em branco para separar um arquivo do outro.
    print()

