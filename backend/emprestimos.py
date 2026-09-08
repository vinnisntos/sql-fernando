import datetime

from db import get_connection

PRAZO_PADRAO_DIAS = 7


def listar_emprestimos():
    conexao = get_connection()
    try:
        cursor = conexao.execute(
            """SELECT e.id_emprestimo, e.data_emprestimo, e.data_devolucao_prevista,
                      e.data_devolucao_real, e.status,
                      e.id_livro, l.titulo AS titulo_livro,
                      e.id_membro, m.nome AS nome_membro
               FROM emprestimos e
               JOIN livros l ON l.id_livro = e.id_livro
               JOIN membros m ON m.id_membro = e.id_membro
               ORDER BY e.data_emprestimo DESC, e.id_emprestimo DESC"""
        )
        return [dict(l) for l in cursor.fetchall()]
    finally:
        conexao.close()


def registrar_emprestimo(id_livro, id_membro, dias_prazo=PRAZO_PADRAO_DIAS):
    conexao = get_connection()
    try:
        cursor = conexao.execute("SELECT qtd_disponivel FROM livros WHERE id_livro = ?", (id_livro,))
        livro = cursor.fetchone()
        if livro is None:
            raise ValueError("Livro nao encontrado.")
        if livro["qtd_disponivel"] <= 0:
            raise ValueError("Nao ha exemplares disponiveis deste livro no momento.")

        cursor = conexao.execute("SELECT id_membro FROM membros WHERE id_membro = ?", (id_membro,))
        if cursor.fetchone() is None:
            raise ValueError("Membro nao encontrado.")

        hoje = datetime.date.today()
        prevista = hoje + datetime.timedelta(days=dias_prazo)

        conexao.execute("UPDATE livros SET qtd_disponivel = qtd_disponivel - 1 WHERE id_livro = ?", (id_livro,))

        cursor = conexao.execute(
            """INSERT INTO emprestimos (id_livro, id_membro, data_emprestimo, data_devolucao_prevista,
                                         data_devolucao_real, status)
               VALUES (?, ?, ?, ?, NULL, 'emprestado')""",
            (id_livro, id_membro, hoje.isoformat(), prevista.isoformat()),
        )
        conexao.commit()
        return cursor.lastrowid
    finally:
        conexao.close()


def registrar_devolucao(id_emprestimo):
    conexao = get_connection()
    try:
        cursor = conexao.execute(
            "SELECT id_livro, status FROM emprestimos WHERE id_emprestimo = ?", (id_emprestimo,)
        )
        emp = cursor.fetchone()
        if emp is None:
            raise ValueError("Emprestimo nao encontrado.")
        if emp["status"] == "devolvido":
            raise ValueError("Este emprestimo ja foi devolvido.")

        hoje = datetime.date.today().isoformat()
        conexao.execute(
            "UPDATE emprestimos SET data_devolucao_real = ?, status = 'devolvido' WHERE id_emprestimo = ?",
            (hoje, id_emprestimo),
        )
        conexao.execute(
            "UPDATE livros SET qtd_disponivel = qtd_disponivel + 1 WHERE id_livro = ?", (emp["id_livro"],)
        )
        conexao.commit()
    finally:
        conexao.close()


def excluir_emprestimo(id_emprestimo):
    conexao = get_connection()
    try:
        cursor = conexao.execute(
            "SELECT id_livro, status FROM emprestimos WHERE id_emprestimo = ?", (id_emprestimo,)
        )
        emp = cursor.fetchone()
        if emp is None:
            return False

        if emp["status"] == "emprestado":
            # devolve o exemplar pro estoque antes de apagar o registro
            conexao.execute(
                "UPDATE livros SET qtd_disponivel = qtd_disponivel + 1 WHERE id_livro = ?", (emp["id_livro"],)
            )

        conexao.execute("DELETE FROM emprestimos WHERE id_emprestimo = ?", (id_emprestimo,))
        conexao.commit()
        return True
    finally:
        conexao.close()
