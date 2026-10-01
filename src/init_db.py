"""Cria o banco e roda os scripts da pasta database.

    python src/init_db.py

Esse comando apaga os dados da aplicação e carrega os exemplos de novo.
"""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg import sql

RAIZ = Path(__file__).resolve().parents[1]
load_dotenv(RAIZ / ".env")

ARQUIVOS = [
    "tables/01_tabelas.sql",
    "functions/01_fn_calcular_total_pedido.sql",
    "views/01_vw_relatorio_vendas.sql",
    "procedures/01_sp_realizar_venda.sql",
    "inserts/01_dados_iniciais.sql",
]


def conexao(banco):
    return psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "postgres"),
        dbname=banco,
    )


def main():
    nome_banco = os.getenv("PGDATABASE", "aurora_vendas")
    admin = conexao("postgres")
    admin.autocommit = True
    try:
        with admin.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (nome_banco,))
            if cur.fetchone() is None:
                cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(nome_banco)))
                print("Banco criado:", nome_banco)
            else:
                print("Banco já existe:", nome_banco)
    finally:
        admin.close()

    conn = conexao(nome_banco)
    try:
        for nome in ARQUIVOS:
            print("Executando", nome)
            arquivo = RAIZ / "database" / nome
            # ClientCursor roda o arquivo inteiro, inclusive function e procedure.
            with psycopg.ClientCursor(conn) as cur:
                cur.execute(arquivo.read_text(encoding="utf-8"))
            conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT fn_calcular_total_pedido(1)")
            print("Total do pedido 1:", cur.fetchone()[0])
            cur.execute("SELECT COUNT(*) FROM vw_relatorio_vendas")
            print("Linhas da view:", cur.fetchone()[0])
        conn.commit()
    except Exception as erro:
        conn.rollback()
        print("Erro:", erro)
        raise SystemExit(1)
    finally:
        conn.close()

    print("Pronto. Agora rode: python src/app.py")


if __name__ == "__main__":
    main()
