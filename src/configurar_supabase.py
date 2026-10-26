"""Configura a conexão local sem exibir a senha no terminal."""
from getpass import getpass
from pathlib import Path
from urllib.parse import quote

arquivo = Path(__file__).resolve().parents[1] / '.env'
senha = getpass('Senha do banco de dados do Supabase: ')
if not senha:
    raise SystemExit('Nenhuma senha informada; configuração cancelada.')
url = ('postgresql://postgres.nhuxypjjvlqwdwogphdh:' + quote(senha, safe='')
       + '@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require')
linhas = arquivo.read_text(encoding='utf-8').splitlines()
linhas = [('SUPABASE_DB_URL=' + url) if linha.startswith('SUPABASE_DB_URL=') else linha for linha in linhas]
arquivo.write_text('\n'.join(linhas) + '\n', encoding='utf-8')
arquivo.chmod(0o600)
print('Conexão salva em .env. A senha não foi exibida.')
