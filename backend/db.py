import os
import sqlite3

PASTA_BACKEND = os.path.dirname(os.path.abspath(__file__))
PASTA_RAIZ = os.path.dirname(PASTA_BACKEND)

CAMINHO_BANCO = os.path.join(PASTA_RAIZ, "database", "biblioteca.db")
CAMINHO_SCHEMA = os.path.join(PASTA_RAIZ, "database", "schema.sql")
CAMINHO_SEED = os.path.join(PASTA_RAIZ, "database", "seed.sql")


def get_connection():
    # timeout=10 pra nao dar "database is locked" quando duas requisicoes
    # chegam quase junto
    conexao = sqlite3.connect(CAMINHO_BANCO, timeout=10)
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar_banco():
    banco_e_novo = not os.path.exists(CAMINHO_BANCO)

    conexao = get_connection()
    conexao.execute("PRAGMA journal_mode = WAL")  # ajuda a nao travar o banco

    with open(CAMINHO_SCHEMA, "r", encoding="utf-8") as arquivo:
        conexao.executescript(arquivo.read())

    if banco_e_novo:
        with open(CAMINHO_SEED, "r", encoding="utf-8") as arquivo:
            conexao.executescript(arquivo.read())
        conexao.commit()
        print("Banco de dados criado e populado com dados de exemplo.")

    conexao.close()
