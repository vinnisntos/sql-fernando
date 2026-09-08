import datetime

from db import get_connection


def listar_membros():
    conexao = get_connection()
    try:
        cursor = conexao.execute(
            "SELECT id_membro, nome, email, telefone, data_cadastro FROM membros ORDER BY nome"
        )
        return [dict(l) for l in cursor.fetchall()]
    finally:
        conexao.close()


def buscar_membro(id_membro):
    conexao = get_connection()
    try:
        cursor = conexao.execute(
            "SELECT id_membro, nome, email, telefone, data_cadastro FROM membros WHERE id_membro = ?",
            (id_membro,),
        )
        linha = cursor.fetchone()
        return dict(linha) if linha else None
    finally:
        conexao.close()


def criar_membro(nome, email, telefone):
    conexao = get_connection()
    try:
        hoje = datetime.date.today().isoformat()
        cursor = conexao.execute(
            "INSERT INTO membros (nome, email, telefone, data_cadastro) VALUES (?, ?, ?, ?)",
            (nome, email, telefone, hoje),
        )
        conexao.commit()
        return cursor.lastrowid
    finally:
        conexao.close()


def atualizar_membro(id_membro, nome, email, telefone):
    conexao = get_connection()
    try:
        cursor = conexao.execute(
            "UPDATE membros SET nome = ?, email = ?, telefone = ? WHERE id_membro = ?",
            (nome, email, telefone, id_membro),
        )
        conexao.commit()
        return cursor.rowcount > 0
    finally:
        conexao.close()


def excluir_membro(id_membro):
    conexao = get_connection()
    try:
        cursor = conexao.execute("DELETE FROM membros WHERE id_membro = ?", (id_membro,))
        conexao.commit()
        return cursor.rowcount > 0
    finally:
        conexao.close()
