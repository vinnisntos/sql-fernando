from db import get_connection


def listar_livros(apenas_disponiveis=False):
    conexao = get_connection()
    try:
        sql = """SELECT l.id_livro, l.titulo, l.ano_publicacao, l.genero,
                         l.qtd_total, l.qtd_disponivel, l.id_autor, a.nome AS nome_autor
                  FROM livros l JOIN autores a ON a.id_autor = l.id_autor"""
        if apenas_disponiveis:
            sql += " WHERE l.qtd_disponivel > 0"
        sql += " ORDER BY l.titulo"

        cursor = conexao.execute(sql)
        lista = []
        for linha in cursor.fetchall():
            lista.append(dict(linha))
        return lista
    finally:
        conexao.close()


def buscar_livro(id_livro):
    conexao = get_connection()
    try:
        cursor = conexao.execute(
            """SELECT l.id_livro, l.titulo, l.ano_publicacao, l.genero,
                      l.qtd_total, l.qtd_disponivel, l.id_autor, a.nome AS nome_autor
               FROM livros l JOIN autores a ON a.id_autor = l.id_autor
               WHERE l.id_livro = ?""",
            (id_livro,),
        )
        linha = cursor.fetchone()
        if linha is None:
            return None
        return dict(linha)
    finally:
        conexao.close()


def criar_livro(titulo, ano_publicacao, genero, qtd_total, id_autor):
    conexao = get_connection()
    try:
        # ao cadastrar, todo mundo comeca disponivel
        cursor = conexao.execute(
            """INSERT INTO livros (titulo, ano_publicacao, genero, qtd_total, qtd_disponivel, id_autor)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (titulo, ano_publicacao, genero, qtd_total, qtd_total, id_autor),
        )
        conexao.commit()
        return cursor.lastrowid
    finally:
        conexao.close()


def atualizar_livro(id_livro, titulo, ano_publicacao, genero, qtd_total, id_autor):
    conexao = get_connection()
    try:
        cursor = conexao.execute("SELECT qtd_total, qtd_disponivel FROM livros WHERE id_livro = ?", (id_livro,))
        atual = cursor.fetchone()
        if atual is None:
            return False

        emprestados = atual["qtd_total"] - atual["qtd_disponivel"]
        nova_disp = qtd_total - emprestados

        if nova_disp < 0:
            raise ValueError(
                "Nao da pra deixar a quantidade total menor que o que ja esta emprestado (%d emprestados)."
                % emprestados
            )

        cursor = conexao.execute(
            """UPDATE livros SET titulo = ?, ano_publicacao = ?, genero = ?, qtd_total = ?,
                                  qtd_disponivel = ?, id_autor = ?
               WHERE id_livro = ?""",
            (titulo, ano_publicacao, genero, qtd_total, nova_disp, id_autor, id_livro),
        )
        conexao.commit()
        return cursor.rowcount > 0
    finally:
        conexao.close()


def excluir_livro(id_livro):
    conexao = get_connection()
    try:
        cursor = conexao.execute("DELETE FROM livros WHERE id_livro = ?", (id_livro,))
        conexao.commit()
        return cursor.rowcount > 0
    finally:
        conexao.close()
