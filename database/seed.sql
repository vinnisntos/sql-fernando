-- Dados de exemplo, só para o sistema não começar vazio
-- (esse script só roda automaticamente na primeira vez que o banco é criado)

INSERT INTO autores (nome, nacionalidade) VALUES
('Machado de Assis', 'Brasileira'),
('J.K. Rowling', 'Britanica'),
('George Orwell', 'Britanica');

INSERT INTO livros (titulo, ano_publicacao, genero, qtd_total, qtd_disponivel, id_autor) VALUES
('Dom Casmurro', 1899, 'Romance', 3, 3, 1),
('Harry Potter e a Pedra Filosofal', 1997, 'Fantasia', 2, 2, 2),
('1984', 1949, 'Ficcao', 4, 4, 3);

INSERT INTO membros (nome, email, telefone, data_cadastro) VALUES
('Ana Souza', 'ana.souza@email.com', '11999990000', '2026-09-01'),
('Bruno Lima', 'bruno.lima@email.com', '11999990001', '2026-09-01');
