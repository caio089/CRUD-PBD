"""Cache do resumo do painel; o banco continua sendo a fonte dos dados."""
import json
import logging
import os
import uuid

import redis

log = logging.getLogger(__name__)
CHAVE = "aurora:painel:resumo"
VERSAO = "aurora:painel:versao"
TTL = 60


def cliente():
    url = os.getenv("REDIS_URL", "")
    if not url:
        return None
    return redis.Redis.from_url(url, decode_responses=True, socket_connect_timeout=1, socket_timeout=1)


def resumo_painel(consultar):
    r = cliente()
    if r is None:
        return consultar(), "Redis não configurado"
    try:
        versao = r.get(VERSAO)
        valor = r.get(CHAVE)
        if valor:
            dados = json.loads(valor)
            if dados["versao"] == versao:
                from decimal import Decimal
                return {"qtd_vendas": dados["qtd_vendas"], "faturamento": Decimal(dados["faturamento"])}, "Redis (cache)"
    except (redis.RedisError, ValueError, KeyError, TypeError):
        log.warning("Cache Redis indisponível ou inválido", exc_info=True)
        return consultar(), "Supabase/banco (Redis indisponível)"

    resumo = consultar()
    dados = json.dumps({"versao": versao, "qtd_vendas": resumo["qtd_vendas"], "faturamento": str(resumo["faturamento"])})
    try:
        # Não publica um resultado antigo se uma gravação ocorreu durante a consulta.
        r.eval("if redis.call('GET', KEYS[1]) == ARGV[1] or (not redis.call('GET', KEYS[1]) and ARGV[1] == '') then return redis.call('SET', KEYS[2], ARGV[2], 'EX', ARGV[3]) end", 2, VERSAO, CHAVE, versao or "", dados, TTL)
    except redis.RedisError:
        log.warning("Não foi possível gravar no Redis", exc_info=True)
    return resumo, "Supabase/banco (consulta)"


def invalidar():
    r = cliente()
    if r is None:
        return
    try:
        with r.pipeline(transaction=True) as pipe:
            pipe.set(VERSAO, uuid.uuid4().hex)
            pipe.delete(CHAVE)
            pipe.execute()
    except redis.RedisError:
        # O TTL limita a duração de um resultado antigo caso o Redis volte.
        log.warning("Não foi possível invalidar o cache Redis", exc_info=True)
