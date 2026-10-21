# ------------------------------------------------------------
# carregar_banco.py
# objetivo: preencher o banco de dados PostgreSQL com os dados tratados.
# o que faz: lê o dados_tratados.csv e grava, nesta ordem, os municípios,
# as escolas e os indicadores anuais de cada escola.
# por que a ordem: cada escola precisa de um município já cadastrado,
# e cada indicador precisa de uma escola já cadastrada.
# pode ser rodado mais de uma vez sem duplicar dados.
# ------------------------------------------------------------

# importa o pandas, que lê e organiza tabelas
import pandas as pd
# importa a função conectar, criada no arquivo conexao.py
from conexao import conectar

dados = pd.read_csv("dados_tratados.csv")  # lê o arquivo CSV tratado e guarda numa tabela

with conectar() as conexao:  # abre a conexão com o banco. ao sair desse bloco sem erro, as gravações são confirmadas
    with conexao.cursor() as cursor: # cria um cursor, que permite enviar comandos SQL para o banco

        # ---- MUNICÍPIOS ----
        # pega a coluna municípios e tira os nomes repetidos, ficando uma vez cada
        municipios = dados["municipio"].drop_duplicates()
        # envia um insert para cada município. o ON CONFLICT DO NOTHING pula os que já existem
        cursor.executemany(
            "INSERT INTO municipios (nome) VALUES (%s) ON CONFLICT (nome) DO NOTHING",
            [(nome,) for nome in municipios],
        )
        # pede ao banco para devolver os IDs e nomes dos municípios cadastrados
        cursor.execute("SELECT nome, id_municipio FROM municipios")
        # guarda em um dicionário: a chave é o nome e o valor é o número do município
        id_municipio = dict(cursor.fetchall())

        # ---- ESCOLAS ----
        # pega as colunas escola e municipio e tira as combinações repetidas
        escolas = dados[["escola", "municipio"]].drop_duplicates()
        # envia um INSERT para cada escola, usando o número do município no lugar do nome.
        cursor.executemany(
            "INSERT INTO escolas (nome, id_municipio) VALUES (%s, %s) ON CONFLICT (nome, id_municipio) DO NOTHING",
            [(linha.escola, id_municipio[linha.municipio]) for linha in escolas.itertuples()],
        )
        # pede ao banco todas as escolas com seus números
        cursor.execute("SELECT nome, id_municipio, id_escola FROM escolas")
        # guarda num dicionário: a chave é (nome da escola, número do município) e o valor é o número da escola
        id_escola = {(nome, mun): numero for nome, mun, numero in cursor.fetchall()}

        # --- INDICADORES ----
        # cria uma lista vazia para guardar os registros que vamos enviar
        registros = []
        # percorre cada linha da tabela de dados
        for linha in dados.itertuples():
            # monta a chave para achar o número da escola no dicionário
            chave = (linha.escola, id_municipio[linha.municipio])
            # acrescenta à lista uma tupla com o número da escola, o ano e os indicadores, na ordem das colunas
            registros.append((
                id_escola[chave],
                int(linha.ano),
                int(linha.matriculas_total),
                int(linha.matricula_inicial),
                int(linha.matricula_apos_censo),
                int(linha.transferidos),
                int(linha.cancelados),
                int(linha.falecidos),
                int(linha.abandono),
                int(linha.aprovados),
                int(linha.reprovados),
                int(linha.cursando),
                int(linha.outras_situacoes),
            ))
        # envia todos os registros ao banco. o ON CONFLICT DO NOTHING pula os que já existem.
        cursor.executemany(
            "INSERT INTO indicadores_anuais (id_escola, ano, matriculas_total, matricula_inicial, "
            "matricula_apos_censo, transferidos, cancelados, falecidos, abandono, aprovados, "
            "reprovados, cursando, outras_situacoes) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            "ON CONFLICT (id_escola, ano) DO NOTHING",
            registros,
        )

        # ---- CONFERÊNCIA ----
        # conta quantas linhas existem em cada tabela e mostra na tela
        for tabela in ["municipios", "escolas", "indicadores_anuais"]:
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            print(tabela, "->", cursor.fetchone()[0], "linhas")