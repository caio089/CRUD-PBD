-- Function usada na tela de pedidos.
-- Recebe o id do pedido e devolve o total: soma de quantidade * preço gravado no item.

CREATE OR REPLACE FUNCTION fn_calcular_total_pedido(id_pedido INTEGER)
RETURNS NUMERIC(10, 2)
LANGUAGE plpgsql
AS $$
DECLARE
    total NUMERIC(10, 2);
BEGIN
    SELECT COALESCE(SUM(quantidade * preco_unitario), 0)
      INTO total
      FROM itens_pedido
     WHERE pedido_id = id_pedido;

    RETURN total;
END;
$$;
