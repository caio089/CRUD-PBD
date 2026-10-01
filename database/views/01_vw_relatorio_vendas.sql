-- View usada no relatório e no painel.
-- Junta pedido, cliente e itens. A tela só faz SELECT nessa view.

DROP VIEW IF EXISTS vw_relatorio_vendas;

CREATE VIEW vw_relatorio_vendas AS
SELECT
    p.id AS id_pedido,
    p.data_pedido,
    c.nome AS cliente,
    c.email,
    COUNT(i.id) AS qtd_itens,
    SUM(i.quantidade) AS qtd_produtos,
    SUM(i.quantidade * i.preco_unitario) AS valor_total
FROM pedidos p
INNER JOIN clientes c ON c.id = p.cliente_id
INNER JOIN itens_pedido i ON i.pedido_id = p.id
GROUP BY p.id, p.data_pedido, c.nome, c.email;
