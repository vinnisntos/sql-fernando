# servidor do sistema, sem framework nenhum (so http.server + sqlite3)
# pra rodar: cd backend / python server.py / abrir localhost:8000

import json
import mimetypes
import os
import re
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import autores
import livros
import membros
import emprestimos
from db import inicializar_banco

PORTA = 8000

PASTA_BACKEND = os.path.dirname(os.path.abspath(__file__))
PASTA_RAIZ = os.path.dirname(PASTA_BACKEND)
PASTA_FRONTEND = os.path.join(PASTA_RAIZ, "frontend")

# regex das rotas que tem id (autor/1, livro/2, etc)
PADRAO_AUTORES = re.compile(r"^/api/autores/(\d+)$")
PADRAO_LIVROS = re.compile(r"^/api/livros/(\d+)$")
PADRAO_MEMBROS = re.compile(r"^/api/membros/(\d+)$")
PADRAO_EMPRESTIMOS = re.compile(r"^/api/emprestimos/(\d+)$")
PADRAO_DEVOLUCAO = re.compile(r"^/api/emprestimos/(\d+)/devolver$")


class ManipuladorRequisicoes(BaseHTTPRequestHandler):

    # ---------- utilidades ----------

    def enviar_json(self, status, dados):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def ler_corpo_json(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        if tamanho == 0:
            return {}
        corpo = self.rfile.read(tamanho)
        return json.loads(corpo.decode("utf-8"))

    def log_message(self, formato, *args):
        # deixa o log do servidor mais enxuto no terminal
        print("[servidor] " + (formato % args))

    # ---------- arquivos estaticos (frontend) ----------

    def servir_arquivo_estatico(self, caminho_url):
        if caminho_url == "/":
            caminho_url = "/index.html"

        # impede acessar arquivos fora da pasta frontend (ex: ../backend/db.py)
        caminho_relativo = caminho_url.lstrip("/")
        caminho_absoluto = os.path.normpath(os.path.join(PASTA_FRONTEND, caminho_relativo))
        if not caminho_absoluto.startswith(PASTA_FRONTEND):
            self.send_error(403, "Acesso negado")
            return

        if not os.path.isfile(caminho_absoluto):
            self.send_error(404, "Arquivo nao encontrado")
            return

        tipo, _ = mimetypes.guess_type(caminho_absoluto)
        if tipo is None:
            tipo = "application/octet-stream"

        with open(caminho_absoluto, "rb") as arquivo:
            conteudo = arquivo.read()

        self.send_response(200)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(conteudo)))
        self.end_headers()
        self.wfile.write(conteudo)

    # ---------- roteamento ----------

    def do_GET(self):
        url = urlparse(self.path)
        caminho = url.path
        parametros = parse_qs(url.query)

        try:
            if caminho == "/api/autores":
                return self.enviar_json(200, autores.listar_autores())

            m = PADRAO_AUTORES.match(caminho)
            if m:
                autor = autores.buscar_autor(int(m.group(1)))
                if autor is None:
                    return self.enviar_json(404, {"erro": "Autor nao encontrado."})
                return self.enviar_json(200, autor)

            if caminho == "/api/livros":
                apenas_disponiveis = parametros.get("disponivel", ["0"])[0] == "1"
                return self.enviar_json(200, livros.listar_livros(apenas_disponiveis))

            m = PADRAO_LIVROS.match(caminho)
            if m:
                livro = livros.buscar_livro(int(m.group(1)))
                if livro is None:
                    return self.enviar_json(404, {"erro": "Livro nao encontrado."})
                return self.enviar_json(200, livro)

            if caminho == "/api/membros":
                return self.enviar_json(200, membros.listar_membros())

            m = PADRAO_MEMBROS.match(caminho)
            if m:
                membro = membros.buscar_membro(int(m.group(1)))
                if membro is None:
                    return self.enviar_json(404, {"erro": "Membro nao encontrado."})
                return self.enviar_json(200, membro)

            if caminho == "/api/emprestimos":
                return self.enviar_json(200, emprestimos.listar_emprestimos())

            if caminho.startswith("/api/"):
                return self.enviar_json(404, {"erro": "Rota nao encontrada."})

            # se nao e rota de API, tenta servir um arquivo do frontend
            return self.servir_arquivo_estatico(caminho)

        except Exception as erro:
            return self.enviar_json(500, {"erro": str(erro)})

    def do_POST(self):
        caminho = urlparse(self.path).path

        try:
            dados = self.ler_corpo_json()

            if caminho == "/api/autores":
                novo_id = autores.criar_autor(dados.get("nome"), dados.get("nacionalidade"))
                return self.enviar_json(201, {"id_autor": novo_id})

            if caminho == "/api/livros":
                novo_id = livros.criar_livro(
                    dados.get("titulo"),
                    dados.get("ano_publicacao"),
                    dados.get("genero"),
                    dados.get("qtd_total"),
                    dados.get("id_autor"),
                )
                return self.enviar_json(201, {"id_livro": novo_id})

            if caminho == "/api/membros":
                novo_id = membros.criar_membro(
                    dados.get("nome"), dados.get("email"), dados.get("telefone")
                )
                return self.enviar_json(201, {"id_membro": novo_id})

            if caminho == "/api/emprestimos":
                novo_id = emprestimos.registrar_emprestimo(
                    dados.get("id_livro"), dados.get("id_membro")
                )
                return self.enviar_json(201, {"id_emprestimo": novo_id})

            m = PADRAO_DEVOLUCAO.match(caminho)
            if m:
                emprestimos.registrar_devolucao(int(m.group(1)))
                return self.enviar_json(200, {"mensagem": "Devolucao registrada com sucesso."})

            return self.enviar_json(404, {"erro": "Rota nao encontrada."})

        except ValueError as erro:
            return self.enviar_json(400, {"erro": str(erro)})
        except sqlite3.IntegrityError as erro:
            return self.enviar_json(400, {"erro": "Violacao de integridade no banco: " + str(erro)})
        except Exception as erro:
            return self.enviar_json(500, {"erro": str(erro)})

    def do_PUT(self):
        caminho = urlparse(self.path).path

        try:
            dados = self.ler_corpo_json()

            m = PADRAO_AUTORES.match(caminho)
            if m:
                id_autor = int(m.group(1))
                ok = autores.atualizar_autor(id_autor, dados.get("nome"), dados.get("nacionalidade"))
                if not ok:
                    return self.enviar_json(404, {"erro": "Autor nao encontrado."})
                return self.enviar_json(200, {"mensagem": "Autor atualizado."})

            m = PADRAO_LIVROS.match(caminho)
            if m:
                id_livro = int(m.group(1))
                ok = livros.atualizar_livro(
                    id_livro,
                    dados.get("titulo"),
                    dados.get("ano_publicacao"),
                    dados.get("genero"),
                    dados.get("qtd_total"),
                    dados.get("id_autor"),
                )
                if not ok:
                    return self.enviar_json(404, {"erro": "Livro nao encontrado."})
                return self.enviar_json(200, {"mensagem": "Livro atualizado."})

            m = PADRAO_MEMBROS.match(caminho)
            if m:
                id_membro = int(m.group(1))
                ok = membros.atualizar_membro(
                    id_membro, dados.get("nome"), dados.get("email"), dados.get("telefone")
                )
                if not ok:
                    return self.enviar_json(404, {"erro": "Membro nao encontrado."})
                return self.enviar_json(200, {"mensagem": "Membro atualizado."})

            return self.enviar_json(404, {"erro": "Rota nao encontrada."})

        except ValueError as erro:
            return self.enviar_json(400, {"erro": str(erro)})
        except sqlite3.IntegrityError as erro:
            return self.enviar_json(400, {"erro": "Violacao de integridade no banco: " + str(erro)})
        except Exception as erro:
            return self.enviar_json(500, {"erro": str(erro)})

    def do_DELETE(self):
        caminho = urlparse(self.path).path

        try:
            m = PADRAO_AUTORES.match(caminho)
            if m:
                ok = autores.excluir_autor(int(m.group(1)))
                if not ok:
                    return self.enviar_json(404, {"erro": "Autor nao encontrado."})
                return self.enviar_json(200, {"mensagem": "Autor excluido."})

            m = PADRAO_LIVROS.match(caminho)
            if m:
                ok = livros.excluir_livro(int(m.group(1)))
                if not ok:
                    return self.enviar_json(404, {"erro": "Livro nao encontrado."})
                return self.enviar_json(200, {"mensagem": "Livro excluido."})

            m = PADRAO_MEMBROS.match(caminho)
            if m:
                ok = membros.excluir_membro(int(m.group(1)))
                if not ok:
                    return self.enviar_json(404, {"erro": "Membro nao encontrado."})
                return self.enviar_json(200, {"mensagem": "Membro excluido."})

            m = PADRAO_EMPRESTIMOS.match(caminho)
            if m:
                ok = emprestimos.excluir_emprestimo(int(m.group(1)))
                if not ok:
                    return self.enviar_json(404, {"erro": "Emprestimo nao encontrado."})
                return self.enviar_json(200, {"mensagem": "Emprestimo excluido."})

            return self.enviar_json(404, {"erro": "Rota nao encontrada."})

        except sqlite3.IntegrityError as erro:
            return self.enviar_json(
                400,
                {"erro": "Nao e possivel excluir: existem registros que dependem deste ("
                          + str(erro) + ")."},
            )
        except Exception as erro:
            return self.enviar_json(500, {"erro": str(erro)})


def main():
    inicializar_banco()
    servidor = ThreadingHTTPServer(("localhost", PORTA), ManipuladorRequisicoes)
    print("Servidor rodando em http://localhost:{}".format(PORTA))
    print("Pressione Ctrl+C para parar.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        servidor.server_close()


if __name__ == "__main__":
    main()
