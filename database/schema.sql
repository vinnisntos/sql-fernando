-- Script de criação do banco de dados da Biblioteca
-- SGBD: SQLite

-- Ativa a checagem de chaves estrangeiras (no SQLite isso vem desligado por padrão)
PRAGMA foreign_keys = ON;

-- Tabela de Autores
CREATE TABLE IF NOT EXISTS autores (
    id_autor      INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT NOT NULL,
    nacionalidade TEXT
);

-- Tabela de Livros
-- qtd_disponivel nunca pode ser maior que qtd_total (CHECK garante isso no banco)
CREATE TABLE IF NOT EXISTS livros (
    id_livro       INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo         TEXT NOT NULL,
    ano_publicacao INTEGER,
    genero         TEXT,
    qtd_total      INTEGER NOT NULL CONSTRAINT chk_qtd_total CHECK (qtd_total >= 0),
    qtd_disponivel INTEGER NOT NULL CONSTRAINT chk_qtd_disponivel CHECK (qtd_disponivel >= 0),
    id_autor       INTEGER NOT NULL,
    CONSTRAINT chk_disponivel_menor_total CHECK (qtd_disponivel <= qtd_total),
    FOREIGN KEY (id_autor) REFERENCES autores (id_autor) ON DELETE RESTRICT
);

-- Tabela de Membros (usuários cadastrados na biblioteca)
CREATE TABLE IF NOT EXISTS membros (
    id_membro     INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    telefone      TEXT,
    data_cadastro TEXT NOT NULL
);

-- Tabela de Empréstimos (relaciona um livro com um membro)
CREATE TABLE IF NOT EXISTS emprestimos (
    id_emprestimo          INTEGER PRIMARY KEY AUTOINCREMENT,
    id_livro                INTEGER NOT NULL,
    id_membro                INTEGER NOT NULL,
    data_emprestimo          TEXT NOT NULL,
    data_devolucao_prevista  TEXT NOT NULL,
    data_devolucao_real      TEXT,
    status                   TEXT NOT NULL DEFAULT 'emprestado'
                             CONSTRAINT chk_status CHECK (status IN ('emprestado', 'devolvido')),
    FOREIGN KEY (id_livro) REFERENCES livros (id_livro) ON DELETE RESTRICT,
    FOREIGN KEY (id_membro) REFERENCES membros (id_membro) ON DELETE RESTRICT
);
