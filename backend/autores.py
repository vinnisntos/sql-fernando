from db import get_connection


def listar_autores():
    conexao = get_connection()
    try:
        cursor = conexao.execute("SELECT id_autor, nome, nacionalidade FROM autores ORDER BY nome")
        return [dict(linha) for linha in cursor.fetchall()]
    finally:
        conexao.close()


def buscar_autor(id_autor):
    conexao = get_connection()
    try:
        cursor = conexao.execute(
            "SELECT id_autor, nome, nacionalidade FROM autores WHERE id_autor = ?",
            (id_autor,),
        )
        linha = cursor.fetchone()
        if linha is None:
            return None
        return dict(linha)
    finally:
        conexao.close()


def criar_autor(nome, nacionalidade):
    conexao = get_connection()
    try:
        cursor = conexao.execute(
            "INSERT INTO autores (nome, nacionalidade) VALUES (?, ?)",
            (nome, nacionalidade),
        )
        conexao.commit()
        return cursor.lastrowid
    finally:
        conexao.close()


def atualizar_autor(id_autor, nome, nacionalidade):
    conexao = get_connection()
    try:
        cursor = conexao.execute(
            "UPDATE autores SET nome = ?, nacionalidade = ? WHERE id_autor = ?",
            (nome, nacionalidade, id_autor),
        )
        conexao.commit()
        return cursor.rowcount > 0
    finally:
        conexao.close()


def excluir_autor(id_autor):
    conexao = get_connection()
    try:
        cursor = conexao.execute("DELETE FROM autores WHERE id_autor = ?", (id_autor,))
        conexao.commit()
        return cursor.rowcount > 0
    finally:
        conexao.close()
