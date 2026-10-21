# ------------------------------------------------------------
# conexao.py
# objetivo: abrir a conexão com o banco de dados PostgreSQL (escolas_ms).
# por que existe: vários arquivos do projeto (carga dos dados e interface)
# vão precisar se conectar ao banco, então a conexão fica num lugar só.
# segurança: a senha vem do arquivo .env, que não vai para o GitHub.
# ------------------------------------------------------------

# importa o os, que permite ler informações do computador, como variáveis de ambiente
import os
# importa o psycopg, que permite ao Python falar com o PostgreSQL
import psycopg
# importa a função que lê o arquivo .env
from dotenv import load_dotenv

load_dotenv()  # lê o arquivo .env e deixa a senha disponível para o programa

# criacão da função conectar, que abre e devolve a conexão com o banco de dados
def conectar():
    # abre a conexão com os dados abaixo e devolve o resultado
    return psycopg.connect(
        host = "localhost",    # o banco está neste computador
        port = 5432,           # porta padrão do PostgreSQL
        dbname = "escolas_ms", # nome do banco de dados
        user = "postgres",     # usuário do banco
        password = os.getenv("DB_SENHA")  # senha do banco, vinda do arquivo .env
    )

# esse bloco só roda quando o arquivo é executado diretamente, não quando outro arquivo usa
if __name__ == "__main__":
    # abre a conexão e fecha sozinho quando terminar
    with conectar() as conexao:
        # cria um cursor, que permite enviar comandos SQL para o banco
        with conexao.cursor() as cursor:
            # pede ao banco para listar as tabelas do esquema public
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            # mostra na tela o que o banco respondeu
            print(cursor.fetchall())