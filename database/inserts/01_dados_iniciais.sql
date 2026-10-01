-- Dados para testar.
-- Pedido 1 (Ana): 2x28,90 + 1x9,50 + 3x5,79 = 84,67
-- Pedido 2 (Bruno): 22,00 + 24,90 = 46,90
-- Pedido 3 (Carla): 34,50 + 2x16,40 + 2x8,30 = 83,90
-- Soma da view: 215,47
-- O mel começa com 4 unidades. Vender 5 mostra o erro da procedure.

TRUNCATE TABLE itens_pedido, pedidos, produtos, clientes RESTART IDENTITY CASCADE;

INSERT INTO clientes (nome, email, telefone) VALUES
    ('Ana Lima', 'ana.lima@email.com', '(11) 98888-1001'),
    ('Bruno Costa', 'bruno.costa@email.com', '(11) 98888-1002'),
    ('Carla Mendes', 'carla.mendes@email.com', '(21) 97777-2003'),
    ('Diego Alves', 'diego.alves@email.com', '(31) 96666-3004'),
    ('Elena Rocha', 'elena.rocha@email.com', '(41) 95555-4005');

INSERT INTO produtos (nome, preco, estoque, ativo) VALUES
    ('Café especial 250g', 28.90, 40, TRUE),
    ('Pão integral 500g', 9.50, 25, TRUE),
    ('Leite integral 1L', 5.79, 60, TRUE),
    ('Queijo minas 300g', 22.00, 18, TRUE),
    ('Granola 400g', 16.40, 12, TRUE),
    ('Mel silvestre 300g', 24.90, 4, TRUE),
    ('Suco de laranja 1L', 8.30, 30, TRUE),
    ('Azeite 500ml', 34.50, 15, TRUE),
    ('Biscoito cream cracker', 6.20, 0, FALSE);

INSERT INTO pedidos (cliente_id, data_pedido, observacao) VALUES
    (1, TIMESTAMP '2026-09-18 09:30:00', 'Compra da manhã'),
    (2, TIMESTAMP '2026-09-22 14:10:00', 'Retirada no balcão'),
    (3, TIMESTAMP '2026-09-28 11:05:00', NULL);

INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES
    (1, 1, 2, 28.90),
    (1, 2, 1, 9.50),
    (1, 3, 3, 5.79),
    (2, 4, 1, 22.00),
    (2, 6, 1, 24.90),
    (3, 8, 1, 34.50),
    (3, 5, 2, 16.40),
    (3, 7, 2, 8.30);
