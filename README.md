# Evolução da educação pública em Mato Grosso do Sul (2018 a 2026)

Projeto acadêmico que analisa dados reais de matrículas por unidade escolar da rede pública de Mato Grosso do Sul e mostra, por município e por período, se a educação está evoluindo, com foco nos indicadores de aprovação e abandono escolar.

## O que o projeto faz

1. Lê os arquivos CSV de cada ano e junta tudo numa tabela única e padronizada.
2. Guarda o histórico das escolas num banco de dados relacional (PostgreSQL), com três tabelas ligadas entre si: municípios, escolas e indicadores anuais.
3. Carrega os dados do banco para a memória e calcula as taxas de aprovação e de abandono.
4. Mostra uma página web com filtros por município e por período, gráficos de evolução e um resumo em texto.

## Demonstração do site 

Na pasta `mostrando o site` estão disponíveis um vídeo de demonstração e capturas de tela da interface web do projeto. Esses materiais permitem visualizar o funcionamento do sistema, os filtros por município e período, os gráficos de evolução e o resumo dos indicadores educacionais.

## Arquivos do projeto

- `carregar.py`: confere os CSVs e mostra o nome das colunas e a quantidade de linhas de cada ano.
- `tratar.py`: junta os CSVs, padroniza nomes e tipos de dados e gera o arquivo `dados_tratados.csv`.
- `verificar.py`: confere se a combinação ano, município e escola se repete nos dados tratados.
- `banco.sql`: cria as três tabelas no PostgreSQL.
- `conexao.py`: abre a conexão com o banco, lendo a senha do arquivo `.env`.
- `carregar_banco.py`: preenche as tabelas com os dados de `dados_tratados.csv`.
- `educacao.py`: classes do projeto. `RepositorioEscolar` busca os dados no banco e `AnaliseEducacional` filtra os dados e calcula as taxas e o resumo.
- `app.py`: interface web feita com Streamlit, que usa as classes de `educacao.py`.
- `.gitignore`: lista o que não deve ir para o GitHub (senha, bancos locais e arquivos temporários).

## Como rodar, caso queira utilizar o site

Requisitos: Python 3, PostgreSQL com pgAdmin e as bibliotecas abaixo.

1. Instale as bibliotecas, abrindo um terminal na pasta do projeto:

```
py -m pip install pandas "psycopg[binary]" python-dotenv streamlit
```

2. Coloque os CSVs de cada ano (arquivos `matriculas-por-unidade-escolar-ANO.csv`) na pasta `planilhas dos anos`, caso eles não venham com o repositório.
3. Rode `tratar.py`. Ele gera o `dados_tratados.csv`, que deve ficar na pasta principal do projeto (e não dentro de `planilhas dos anos`).
4. No pgAdmin, crie um banco chamado `escolas_ms`, abra o Query Tool nele e execute o conteúdo de `banco.sql`.
5. Crie na pasta principal um arquivo chamado `.env` com a senha do seu PostgreSQL, em uma única linha:

```
DB_SENHA=sua_senha_aqui
```

Esse arquivo não vai para o GitHub, porque está listado no `.gitignore`.

6. Rode `carregar_banco.py`. No final ele mostra a contagem de linhas de cada tabela: 79 municípios, 599 escolas e 3703 indicadores anuais.
7. Abra a interface:

```
py -m streamlit run app.py
```

## Decisões e limitações dos dados

- **Taxa de aprovação:** calculada como aprovados dividido por aprovados mais reprovados, com a mesma fórmula em todos os anos, para a comparação ser justa.
- **Abandono:** nos arquivos originais, a coluna de abandono tem valores apenas em 2018 e 2019 (muito baixo em 2019) e vem zerada de 2020 em diante. Por isso a evolução do abandono não é confiável, e a interface mostra a taxa só nos anos com registro e traz um aviso na tela.
- **2024 e 2026:** quase todos os alunos aparecem como "cursando", ou seja, o resultado final não está registrado. A interface apaga as taxas desses anos para não mostrar números enganosos.
- **2025:** não há arquivo desse ano na base utilizada.
- **Validação:** em todos os anos, o total de matrículas é igual à soma de todas as situações dos alunos, e os números exibidos para Campo Grande foram conferidos com uma consulta direta no banco.