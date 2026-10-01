"""Conexão com o PostgreSQL e funções simples de consulta."""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def conectar():
    return psycopg.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "postgres"),
        dbname=os.getenv("PGDATABASE", "aurora_vendas"),
        row_factory=dict_row,
    )


def buscar_todos(sql, params=()):
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


def buscar_um(sql, params=()):
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchone()
    finally:
        conn.close()


def executar(sql, params=()):
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def mensagem_banco(erro):
    # A procedure manda o texto do RAISE EXCEPTION nesse campo.
    if getattr(erro, "diag", None) and erro.diag.message_primary:
        return erro.diag.message_primary
    return "Não foi possível concluir a operação."
