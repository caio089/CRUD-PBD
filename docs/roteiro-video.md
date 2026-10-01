# Roteiro do vídeo

Grave a tela do sistema e o código. Fale na ordem abaixo. Uns 6 minutos resolvem.

Antes: `python src/init_db.py` e `python src/app.py`. Abra http://127.0.0.1:5000.

## 1. Apresentação

Diga que a Aurora controla clientes, produtos, vendas e estoque de uma mercearia.

O problema é a venda: ela mexe em pedido, itens e estoque ao mesmo tempo. Se isso ficar só no Python, pode baixar estoque sem gravar o pedido.

Mostre o menu: Painel, Clientes, Produtos, Nova venda, Pedidos e Relatório.

## 2. Telas

Passe rápido por clientes e produtos. Depois abra Nova venda, Pedidos e Relatório. Diga em uma frase o que cada uma faz.

## 3. View

Abra `database/views/01_vw_relatorio_vendas.sql`.

- Foi criada para o relatório não repetir o JOIN no Python.
- Usa `pedidos`, `clientes` e `itens_pedido`.
- Devolve uma linha por pedido, com cliente, quantidades e total.

Abra `src/app.py` e mostre o `SELECT` em `vw_relatorio_vendas` nas funções `relatorio` e `painel`.

No navegador, filtre o relatório pelo nome Ana.

## 4. Function

Abra `database/functions/01_fn_calcular_total_pedido.sql`.

- Só calcula, não grava nada.
- Recebe `id_pedido`.
- Devolve a soma de quantidade × preço que foi salvo no item.

Abra `src/app.py` e mostre `fn_calcular_total_pedido` na função `pedidos` e em `detalhe_pedido`.

No navegador, abra o pedido 1. O total é R$ 84,67.

## 5. Procedure

Abra `database/procedures/01_sp_realizar_venda.sql`.

Explique os parâmetros: cliente, lista de produtos, lista de quantidades, observação e o id do pedido.

Ela:

1. Confere o cliente e os itens.
2. Insere o pedido.
3. Para cada item, confere estoque, grava o item com o preço da hora e baixa o estoque.

Abra `src/app.py` e mostre o `CALL sp_realizar_venda` dentro de `registrar_venda`.

## 6. Tudo junto

1. Anote o estoque do café.
2. Em Nova venda, escolha um cliente, o café e a quantidade 1. Confirme.
3. O pedido novo abre com o total da function (R$ 28,90).
4. Em Produtos, o estoque do café caiu 1.
5. O relatório mostra a venda nova, vinda da view.

Depois tente vender 5 unidades de mel. A procedure recusa, o pedido não é criado e o estoque continua 4.
