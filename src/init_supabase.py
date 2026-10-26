"""Inicializa uma instalação nova em um schema privado do Supabase."""
import os

import psycopg
from dotenv import load_dotenv

from init_db import ARQUIVOS, RAIZ

load_dotenv(RAIZ / ".env")


def main():
    url = os.getenv("SUPABASE_DB_URL")
    if not url:
        raise SystemExit("Configure SUPABASE_DB_URL no arquivo .env.")
    with psycopg.connect(url, prepare_threshold=None) as conn:
        with psycopg.ClientCursor(conn) as cur:
            cur.execute("SELECT 1 FROM pg_namespace WHERE nspname = 'aurora'")
            if cur.fetchone():
                raise SystemExit("O schema aurora já existe; inicialização cancelada para preservar os dados.")
            cur.execute("CREATE SCHEMA aurora")
            cur.execute("REVOKE ALL ON SCHEMA aurora FROM PUBLIC")
            cur.execute("SET LOCAL search_path TO aurora, pg_catalog")
            for nome in ARQUIVOS:
                print("Executando", nome)
                cur.execute((RAIZ / "database" / nome).read_text(encoding="utf-8"))
            for tabela in ("clientes", "produtos", "pedidos", "itens_pedido"):
                cur.execute(psycopg.sql.SQL("ALTER TABLE {} ENABLE ROW LEVEL SECURITY").format(psycopg.sql.Identifier(tabela)))
            cur.execute("SELECT COUNT(*) FROM vw_relatorio_vendas")
            print("Vendas de exemplo:", cur.fetchone()[0])
    print("Supabase inicializado com sucesso.")


if __name__ == "__main__":
    main()
