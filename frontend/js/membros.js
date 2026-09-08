var URL_API = "/api/membros";

$(document).ready(function () {
    carregarMembros();

    $("#form-membro").on("submit", function (evento) {
        evento.preventDefault();
        salvarMembro();
    });

    $("#btn-cancelar").on("click", function () {
        limparFormulario();
    });
});

function mostrarMensagem(texto, tipo) {
    var classe = "alert-success";
    if (tipo === "erro") {
        classe = "alert-danger";
    }
    $("#area-mensagem").html('<div class="alert ' + classe + '">' + texto + "</div>");
}

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

function carregarMembros() {
    $.getJSON(URL_API, function (membros) {
        var linhas = "";
        for (var i = 0; i < membros.length; i++) {
            var m = membros[i];
            linhas +=
                "<tr>" +
                "<td>" + m.id_membro + "</td>" +
                "<td>" + escapeHtml(m.nome) + "</td>" +
                "<td>" + escapeHtml(m.email) + "</td>" +
                "<td>" + escapeHtml(m.telefone) + "</td>" +
                "<td>" + m.data_cadastro + "</td>" +
                "<td>" +
                '<button class="btn btn-sm btn-warning me-1" onclick="editarMembro(' + m.id_membro + ')">Editar</button>' +
                '<button class="btn btn-sm btn-danger" onclick="excluirMembro(' + m.id_membro + ')">Excluir</button>' +
                "</td>" +
                "</tr>";
        }
        $("#tabela-membros").html(linhas);
    }).fail(function () {
        mostrarMensagem("Erro ao carregar a lista de membros.", "erro");
    });
}

function salvarMembro() {
    var idMembro = $("#id_membro").val();
    var dados = {
        nome: $("#nome").val(),
        email: $("#email").val(),
        telefone: $("#telefone").val(),
    };

    var ehEdicao = idMembro !== "";
    var url = ehEdicao ? URL_API + "/" + idMembro : URL_API;
    var metodo = ehEdicao ? "PUT" : "POST";

    $.ajax({
        url: url,
        type: metodo,
        contentType: "application/json",
        data: JSON.stringify(dados),
        success: function () {
            mostrarMensagem(ehEdicao ? "Membro atualizado com sucesso." : "Membro cadastrado com sucesso.", "ok");
            limparFormulario();
            carregarMembros();
        },
        error: function (resposta) {
            var erro = resposta.responseJSON ? resposta.responseJSON.erro : "Erro ao salvar membro.";
            mostrarMensagem(erro, "erro");
        },
    });
}

function editarMembro(id) {
    $.getJSON(URL_API + "/" + id, function (membro) {
        $("#id_membro").val(membro.id_membro);
        $("#nome").val(membro.nome);
        $("#email").val(membro.email);
        $("#telefone").val(membro.telefone);
        $("#titulo-formulario").text("Editar membro #" + membro.id_membro);
        $("#btn-cancelar").show();
        window.scrollTo(0, 0);
    });
}

function excluirMembro(id) {
    if (!confirm("Tem certeza que deseja excluir este membro?")) {
        return;
    }
    $.ajax({
        url: URL_API + "/" + id,
        type: "DELETE",
        success: function () {
            mostrarMensagem("Membro excluido com sucesso.", "ok");
            carregarMembros();
        },
        error: function (resposta) {
            var erro = resposta.responseJSON ? resposta.responseJSON.erro : "Erro ao excluir membro.";
            mostrarMensagem(erro, "erro");
        },
    });
}

function limparFormulario() {
    $("#id_membro").val("");
    $("#form-membro")[0].reset();
    $("#titulo-formulario").text("Novo membro");
    $("#btn-cancelar").hide();
}
