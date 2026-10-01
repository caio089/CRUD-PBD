-- Apaga e cria as tabelas de novo.
-- Rode este arquivo antes da function, da view e da procedure.

DROP VIEW IF EXISTS vw_relatorio_vendas;
DROP PROCEDURE IF EXISTS sp_realizar_venda(INTEGER, INTEGER[], INTEGER[], VARCHAR, INTEGER);
DROP FUNCTION IF EXISTS fn_calcular_total_pedido(INTEGER);

DROP TABLE IF EXISTS itens_pedido CASCADE;
DROP TABLE IF EXISTS pedidos CASCADE;
DROP TABLE IF EXISTS produtos CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;

CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    telefone VARCHAR(20)
);

CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    preco NUMERIC(10, 2) NOT NULL CHECK (preco >= 0),
    estoque INTEGER NOT NULL CHECK (estoque >= 0),
    ativo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clientes (id),
    data_pedido TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    observacao VARCHAR(255)
);

-- preco_unitario guarda o preço da hora da venda.
-- Se o produto mudar de preço depois, o pedido antigo não muda.
CREATE TABLE itens_pedido (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES pedidos (id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES produtos (id),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario NUMERIC(10, 2) NOT NULL CHECK (preco_unitario >= 0)
);
