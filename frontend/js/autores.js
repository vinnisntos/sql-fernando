var URL_API = "/api/autores";

$(document).ready(function () {
    carregarAutores();

    $("#form-autor").on("submit", function (evento) {
        evento.preventDefault();
        salvarAutor();
    });

    $("#btn-cancelar").on("click", function () {
        limparFormulario();
    });
});

function escapeHtml(texto) {
    if (texto === null || texto === undefined) {
        return "";
    }
    return String(texto)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function mostrarMensagem(texto, tipo) {
    var classe = tipo === "erro" ? "alert-danger" : "alert-success";
    $("#area-mensagem").html(
        '<div class="alert ' + classe + '" role="alert">' + texto + "</div>"
    );
}

function carregarAutores() {
    $.getJSON(URL_API, function (autores) {
        var linhas = "";
        for (var i = 0; i < autores.length; i++) {
            var a = autores[i];
            linhas +=
                "<tr>" +
                "<td>" + a.id_autor + "</td>" +
                "<td>" + escapeHtml(a.nome) + "</td>" +
                "<td>" + escapeHtml(a.nacionalidade) + "</td>" +
                "<td>" +
                '<button class="btn btn-sm btn-warning me-1" onclick="editarAutor(' + a.id_autor + ')">Editar</button>' +
                '<button class="btn btn-sm btn-danger" onclick="excluirAutor(' + a.id_autor + ')">Excluir</button>' +
                "</td>" +
                "</tr>";
        }
        $("#tabela-autores").html(linhas);
    }).fail(function () {
        mostrarMensagem("Erro ao carregar a lista de autores.", "erro");
    });
}

function salvarAutor() {
    var idAutor = $("#id_autor").val();
    var dados = {
        nome: $("#nome").val(),
        nacionalidade: $("#nacionalidade").val(),
    };

    var ehEdicao = idAutor !== "";
    var url = ehEdicao ? URL_API + "/" + idAutor : URL_API;
    var metodo = ehEdicao ? "PUT" : "POST";

    $.ajax({
        url: url,
        type: metodo,
        contentType: "application/json",
        data: JSON.stringify(dados),
        success: function () {
            mostrarMensagem(ehEdicao ? "Autor atualizado com sucesso." : "Autor cadastrado com sucesso.", "ok");
            limparFormulario();
            carregarAutores();
        },
        error: function (resposta) {
            var erro = resposta.responseJSON ? resposta.responseJSON.erro : "Erro ao salvar autor.";
            mostrarMensagem(erro, "erro");
        },
    });
}

function editarAutor(id) {
    $.getJSON(URL_API + "/" + id, function (autor) {
        $("#id_autor").val(autor.id_autor);
        $("#nome").val(autor.nome);
        $("#nacionalidade").val(autor.nacionalidade);
        $("#titulo-formulario").text("Editar autor #" + autor.id_autor);
        $("#btn-cancelar").show();
        window.scrollTo(0, 0);
    });
}

function excluirAutor(id) {
    if (!confirm("Tem certeza que deseja excluir este autor?")) {
        return;
    }
    $.ajax({
        url: URL_API + "/" + id,
        type: "DELETE",
        success: function () {
            mostrarMensagem("Autor excluido com sucesso.", "ok");
            carregarAutores();
        },
        error: function (resposta) {
            var erro = resposta.responseJSON ? resposta.responseJSON.erro : "Erro ao excluir autor.";
            mostrarMensagem(erro, "erro");
        },
    });
}

function limparFormulario() {
    $("#id_autor").val("");
    $("#form-autor")[0].reset();
    $("#titulo-formulario").text("Novo autor");
    $("#btn-cancelar").hide();
}
