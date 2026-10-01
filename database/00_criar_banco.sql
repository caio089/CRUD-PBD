-- Cria o banco da aplicação.
-- Execute conectado ao banco de manutenção postgres, por exemplo:
--   psql -U postgres -f database/00_criar_banco.sql
--
-- O script Python src/init_db.py faz este passo automaticamente.

CREATE DATABASE aurora_vendas
    WITH ENCODING 'UTF8'
         TEMPLATE template0;
