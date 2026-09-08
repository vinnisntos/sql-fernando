var URL_API = "/api/emprestimos";
var URL_API_LIVROS = "/api/livros";
var URL_API_MEMBROS = "/api/membros";

$(document).ready(function () {
    carregarSelects();
    carregarEmprestimos();

    $("#form-emprestimo").on("submit", function (evento) {
        evento.preventDefault();
        registrarEmprestimo();
    });
});

function mostrarMensagem(texto, tipo) {
    var classe = tipo === "erro" ? "alert-danger" : "alert-success";
    $("#area-mensagem").html(
        '<div class="alert ' + classe + '" role="alert">' + texto + "</div>"
    );
}

function carregarSelects() {
    // disponivel=1 pra so trazer livro que da pra emprestar
    $.getJSON(URL_API_LIVROS + "?disponivel=1", function (livros) {
        var opcoes = '<option value="">Selecione...</option>';
        for (var i = 0; i < livros.length; i++) {
            opcoes += '<option value="' + livros[i].id_livro + '">' +
                livros[i].titulo + " (disponiveis: " + livros[i].qtd_disponivel + ")" +
                "</option>";
        }
        $("#id_livro").html(opcoes);
    });

    $.getJSON(URL_API_MEMBROS, function (membros) {
        var opcoes = '<option value="">Selecione...</option>';
        for (var i = 0; i < membros.length; i++) {
            opcoes += '<option value="' + membros[i].id_membro + '">' + membros[i].nome + "</option>";
        }
        $("#id_membro").html(opcoes);
    });
}

function carregarEmprestimos() {
    $.getJSON(URL_API, function (emprestimos) {
        var linhas = "";
        for (var i = 0; i < emprestimos.length; i++) {
            var e = emprestimos[i];

            var botoes = "";
            if (e.status === "emprestado") {
                botoes += '<button class="btn btn-sm btn-success me-1" onclick="devolverEmprestimo(' + e.id_emprestimo + ')">Devolver</button>';
            }
            botoes += '<button class="btn btn-sm btn-danger" onclick="excluirEmprestimo(' + e.id_emprestimo + ')">Excluir</button>';

            var rotuloStatus = e.status === "devolvido"
                ? '<span class="badge bg-secondary">Devolvido</span>'
                : '<span class="badge bg-warning text-dark">Emprestado</span>';

            linhas +=
                "<tr>" +
                "<td>" + e.id_emprestimo + "</td>" +
                "<td>" + e.titulo_livro + "</td>" +
                "<td>" + e.nome_membro + "</td>" +
                "<td>" + e.data_emprestimo + "</td>" +
                "<td>" + e.data_devolucao_prevista + "</td>" +
                "<td>" + (e.data_devolucao_real || "-") + "</td>" +
                "<td>" + rotuloStatus + "</td>" +
                "<td>" + botoes + "</td>" +
                "</tr>";
        }
        $("#tabela-emprestimos").html(linhas);
    }).fail(function () {
        mostrarMensagem("Erro ao carregar a lista de emprestimos.", "erro");
    });
}

function registrarEmprestimo() {
    var dados = {
        id_livro: parseInt($("#id_livro").val(), 10),
        id_membro: parseInt($("#id_membro").val(), 10),
    };

    $.ajax({
        url: URL_API,
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify(dados),
        success: function () {
            mostrarMensagem("Emprestimo registrado com sucesso.", "ok");
            $("#form-emprestimo")[0].reset();
            carregarSelects();
            carregarEmprestimos();
        },
        error: function (resposta) {
            var erro = resposta.responseJSON ? resposta.responseJSON.erro : "Erro ao registrar emprestimo.";
            mostrarMensagem(erro, "erro");
        },
    });
}

function devolverEmprestimo(id) {
    if (!confirm("Confirmar a devolucao deste livro?")) {
        return;
    }
    $.ajax({
        url: URL_API + "/" + id + "/devolver",
        type: "POST",
        success: function () {
            mostrarMensagem("Devolucao registrada com sucesso.", "ok");
            carregarSelects();
            carregarEmprestimos();
        },
        error: function (resposta) {
            var erro = resposta.responseJSON ? resposta.responseJSON.erro : "Erro ao registrar devolucao.";
            mostrarMensagem(erro, "erro");
        },
    });
}

function excluirEmprestimo(id) {
    if (!confirm("Tem certeza que deseja excluir este registro de emprestimo?")) {
        return;
    }
    $.ajax({
        url: URL_API + "/" + id,
        type: "DELETE",
        success: function () {
            mostrarMensagem("Registro excluido com sucesso.", "ok");
            carregarSelects();
            carregarEmprestimos();
        },
        error: function (resposta) {
            var erro = resposta.responseJSON ? resposta.responseJSON.erro : "Erro ao excluir registro.";
            mostrarMensagem(erro, "erro");
        },
    });
}
