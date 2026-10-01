-- Recria os objetos e os dados de exemplo em uma única transação.
-- O banco aurora_vendas já precisa existir.
--
--   psql -U postgres -d aurora_vendas -f database/setup.sql
--
-- A forma recomendada no Windows é:
--   python src/init_db.py

\set ON_ERROR_STOP on
SET client_encoding = 'UTF8';

BEGIN;
\ir tables/01_tabelas.sql
\ir functions/01_fn_calcular_total_pedido.sql
\ir views/01_vw_relatorio_vendas.sql
\ir procedures/01_sp_realizar_venda.sql
\ir inserts/01_dados_iniciais.sql
COMMIT;
