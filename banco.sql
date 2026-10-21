-- ------------------------------------------------------------
-- banco.sql
-- objetivo: criar a estrutura do banco de dados da educação pública de MS.
-- o que faz: cria três tabelas (municipios, escolas e indicadores_anuais)
-- ligadas entre si, para guardar o histórico das escolas ano a ano.
-- banco usado: PostgreSQL (gerenciado pelo pgAdmin).
-- ------------------------------------------------------------

-- tabela dos municípios.
CREATE TABLE IF NOT EXISTS municipios (
    -- número único de cada município, gerado automaticamente (1, 2, 3...).
    id_municipio INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- nome do município. Não pode ficar vazio nem repetir.
    nome VARCHAR(200) NOT NULL UNIQUE
);

-- tabela das escolas.
CREATE TABLE IF NOT EXISTS escolas (
    -- número único de cada escola, gerado automaticamente.
    id_escola INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- nome da escola. Não pode ficar vazio.
    nome VARCHAR(200) NOT NULL,
    -- número do município ao qual a escola pertence.
    id_municipio INTEGER NOT NULL,
    -- garante que o número do município existe na tabela municipios.
    FOREIGN KEY (id_municipio) REFERENCES municipios (id_municipio),
    -- impede cadastrar duas escolas com o mesmo nome no mesmo município.
    UNIQUE (nome, id_municipio)
);

-- tabela com os números de cada escola em cada ano.
CREATE TABLE IF NOT EXISTS indicadores_anuais (
    -- número único de cada registro, gerado automaticamente.
    id_indicador INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- número da escola a que os dados se referem.
    id_escola INTEGER NOT NULL,
    -- ano de referência dos dados.
    ano INTEGER NOT NULL,
    -- total de matrículas no ano.
    matriculas_total INTEGER,
    -- matrículas no início do ano.
    matricula_inicial INTEGER,
    -- matrículas feitas depois do censo.
    matricula_apos_censo INTEGER,
    -- alunos transferidos.
    transferidos INTEGER,
    -- matrículas canceladas.
    cancelados INTEGER,
    -- alunos falecidos.
    falecidos INTEGER,
    -- alunos que abandonaram os estudos.
    abandono INTEGER,
    -- alunos aprovados.
    aprovados INTEGER,
    -- alunos reprovados.
    reprovados INTEGER,
    -- alunos ainda cursando.
    cursando INTEGER,
    -- alunos em outras situações.
    outras_situacoes INTEGER,
    -- garante que o número da escola existe na tabela escolas.
    FOREIGN KEY (id_escola) REFERENCES escolas (id_escola),
    -- impede cadastrar dois registros da mesma escola no mesmo ano.
    UNIQUE (id_escola, ano)
);