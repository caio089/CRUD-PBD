-- Procedure usada na tela Nova venda.
-- Ela faz o processo inteiro: cria o pedido, grava os itens e baixa o estoque.
-- Se der erro no meio, o Python desfaz a transação e nada fica salvo pela metade.
--
-- Parâmetros:
--   id_cliente    quem comprou
--   produtos      ids dos produtos
--   quantidades   quantidades, na mesma ordem dos produtos
--   observacao    texto opcional
--   id_pedido     volta com o número do pedido criado

CREATE OR REPLACE PROCEDURE sp_realizar_venda(
    IN id_cliente INTEGER,
    IN produtos INTEGER[],
    IN quantidades INTEGER[],
    IN observacao VARCHAR(255),
    INOUT id_pedido INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INTEGER;
    id_produto INTEGER;
    qtd INTEGER;
    preco_item NUMERIC(10, 2);
    estoque_atual INTEGER;
    nome_produto VARCHAR(120);
    produto_ativo BOOLEAN;
BEGIN
    IF id_cliente IS NULL OR NOT EXISTS (SELECT 1 FROM clientes WHERE id = id_cliente) THEN
        RAISE EXCEPTION 'Cliente não encontrado.';
    END IF;

    IF produtos IS NULL OR quantidades IS NULL OR array_length(produtos, 1) IS NULL THEN
        RAISE EXCEPTION 'A venda precisa ter pelo menos um item.';
    END IF;

    IF array_length(produtos, 1) <> array_length(quantidades, 1) THEN
        RAISE EXCEPTION 'Produtos e quantidades não batem.';
    END IF;

    INSERT INTO pedidos (cliente_id, observacao)
    VALUES (id_cliente, NULLIF(trim(COALESCE(observacao, '')), ''))
    RETURNING id INTO id_pedido;

    FOR i IN 1 .. array_length(produtos, 1) LOOP
        id_produto := produtos[i];
        qtd := quantidades[i];

        IF qtd IS NULL OR qtd <= 0 THEN
            RAISE EXCEPTION 'A quantidade precisa ser maior que zero.';
        END IF;

        SELECT nome, preco, estoque, ativo
          INTO nome_produto, preco_item, estoque_atual, produto_ativo
          FROM produtos
         WHERE produtos.id = id_produto;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Produto % não encontrado.', id_produto;
        END IF;

        IF NOT produto_ativo THEN
            RAISE EXCEPTION 'O produto % está inativo.', nome_produto;
        END IF;

        IF estoque_atual < qtd THEN
            RAISE EXCEPTION 'Estoque insuficiente de %. Disponível: %.', nome_produto, estoque_atual;
        END IF;

        INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)
        VALUES (id_pedido, id_produto, qtd, preco_item);

        UPDATE produtos
           SET estoque = estoque - qtd
         WHERE id = id_produto;
    END LOOP;
END;
$$;
