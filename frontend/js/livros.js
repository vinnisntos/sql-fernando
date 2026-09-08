var URL_API = "/api/livros";
var URL_API_AUTORES = "/api/autores";

$(document).ready(function () {
    carregarAutoresNoSelect();
    carregarLivros();

    $("#form-livro").on("submit", function (evento) {
        evento.preventDefault();
        salvarLivro();
    });

    $("#btn-cancelar").on("click", function () {
        limparFormulario();
    });
});

function mostrarMensagem(texto, tipo) {
    var classe = tipo === "erro" ? "alert-danger" : "alert-success";
    $("#area-mensagem").html(
        '<div class="alert ' + classe + '" role="alert">' + texto + "</div>"
    );
}

function carregarAutoresNoSelect() {
    $.getJSON(URL_API_AUTORES, function (autores) {
        var opcoes = '<option value="">Selecione...</option>';
        $.each(autores, function (i, a) {
            opcoes += '<option value="' + a.id_autor + '">' + a.nome + "</option>";
        });
        $("#id_autor").html(opcoes);
    });
}

function carregarLivros() {
    $.getJSON(URL_API, function (livros) {
        var linhas = "";
        for (var i = 0; i < livros.length; i++) {
            var l = livros[i];
            linhas +=
                "<tr>" +
                "<td>" + l.id_livro + "</td>" +
                "<td>" + l.titulo + "</td>" +
                "<td>" + l.nome_autor + "</td>" +
                "<td>" + (l.ano_publicacao || "") + "</td>" +
                "<td>" + (l.genero || "") + "</td>" +
                "<td>" + l.qtd_total + "</td>" +
                "<td>" + l.qtd_disponivel + "</td>" +
                "<td>" +
                '<button class="btn btn-sm btn-warning me-1" onclick="editarLivro(' + l.id_livro + ')">Editar</button>' +
                '<button class="btn btn-sm btn-danger" onclick="excluirLivro(' + l.id_livro + ')">Excluir</button>' +
                "</td>" +
                "</tr>";
        }
        $("#tabela-livros").html(linhas);
    }).fail(function () {
        mostrarMensagem("Erro ao carregar a lista de livros.", "erro");
    });
}

function salvarLivro() {
    var idLivro = $("#id_livro").val();
    var dados = {
        titulo: $("#titulo").val(),
        ano_publicacao: $("#ano_publicacao").val() ? parseInt($("#ano_publicacao").val(), 10) : null,
        genero: $("#genero").val(),
        qtd_total: parseInt($("#qtd_total").val(), 10),
        id_autor: parseInt($("#id_autor").val(), 10),
    };

    var ehEdicao = idLivro !== "";
    var url = ehEdicao ? URL_API + "/" + idLivro : URL_API;
    var metodo = ehEdicao ? "PUT" : "POST";

    $.ajax({
        url: url,
        type: metodo,
        contentType: "application/json",
        data: JSON.stringify(dados),
        success: function () {
            mostrarMensagem(ehEdicao ? "Livro atualizado com sucesso." : "Livro cadastrado com sucesso.", "ok");
            limparFormulario();
            carregarLivros();
        },
        error: function (resposta) {
            var erro = resposta.responseJSON ? resposta.responseJSON.erro : "Erro ao salvar livro.";
            mostrarMensagem(erro, "erro");
        },
    });
}

function editarLivro(id) {
    $.getJSON(URL_API + "/" + id, function (livro) {
        $("#id_livro").val(livro.id_livro);
        $("#titulo").val(livro.titulo);
        $("#ano_publicacao").val(livro.ano_publicacao);
        $("#genero").val(livro.genero);
        $("#id_autor").val(livro.id_autor);
        $("#qtd_total").val(livro.qtd_total);
        $("#titulo-formulario").text("Editar livro #" + livro.id_livro);
        $("#btn-cancelar").show();
        window.scrollTo(0, 0);
    });
}

function excluirLivro(id) {
    if (!confirm("Tem certeza que deseja excluir este livro?")) {
        return;
    }
    $.ajax({
        url: URL_API + "/" + id,
        type: "DELETE",
        success: function () {
            mostrarMensagem("Livro excluido com sucesso.", "ok");
            carregarLivros();
        },
        error: function (resposta) {
            var erro = resposta.responseJSON ? resposta.responseJSON.erro : "Erro ao excluir livro.";
            mostrarMensagem(erro, "erro");
        },
    });
}

function limparFormulario() {
    $("#id_livro").val("");
    $("#form-livro")[0].reset();
    $("#titulo-formulario").text("Novo livro");
    $("#btn-cancelar").hide();
}
