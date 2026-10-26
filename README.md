# Aurora Vendas

O Aurora Vendas é um sistema de gestão para uma mercearia, desenvolvido para a disciplina Projeto de Banco de Dados. Ele reúne o cadastro de clientes e produtos, o controle de estoque e o registro de vendas em uma interface acessível pelo navegador.

O objetivo do projeto é demonstrar a integração entre uma interface gráfica, o **Supabase**, responsável por armazenar os dados, e o **Redis**, utilizado como cache para reduzir consultas repetidas ao banco.

**Autor:** Caio Campos · **Professor:** Anderson Soares · **Repositório:** [caio089/CRUD-PBD](https://github.com/caio089/CRUD-PBD)

## Vídeo demonstrativo

Assista à [demonstração do Aurora Vendas](https://youtu.be/zgXDQB_bnu8).

## Funcionalidades

- Painel com faturamento, quantidade de vendas, últimas vendas e estoque baixo.
- Cadastro, busca, edição e exclusão de clientes e produtos.
- Registro de vendas, consulta de pedidos e relatório filtrado.
- No painel, indicação da origem do resumo: banco de dados ou cache Redis.

## Tecnologias utilizadas

| Tecnologia | Papel no projeto |
| --- | --- |
| Python e Flask | Processamento das requisições e regras da aplicação. |
| HTML e CSS | Construção das telas acessadas pelo navegador. |
| Supabase e PostgreSQL | Armazenamento de clientes, produtos, pedidos e itens das vendas. |
| Redis | Armazenamento temporário do resumo de vendas do painel. |
| psycopg e redis-py | Conexão do backend ao PostgreSQL e ao Redis. |
| python-dotenv | Carregamento das configurações do arquivo `.env`. |

## Configuração e execução

Pré-requisitos: Python 3, Git, um projeto Supabase de teste, a senha do banco desse projeto e um servidor Redis acessível. A inicialização cria dados de exemplo.

1. Crie e ative um ambiente virtual, instale as dependências e copie o arquivo de configuração:

```bash
git clone https://github.com/caio089/CRUD-PBD.git
cd CRUD-PBD
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

No Windows, ative com `.venv\Scripts\Activate.ps1` e copie com `Copy-Item .env.example .env`.

2. No painel do Supabase, abra **Connect** e copie a string de conexão PostgreSQL do **Session pooler** (ou conexão direta, se sua rede suportar IPv6). Coloque-a em `SUPABASE_DB_URL` no `.env`, substituindo a senha e adicionando `?sslmode=require` caso a URL ainda não contenha parâmetros. Caracteres especiais da senha precisam ser codificados para URL. Não use a chave de API no lugar da URL do banco. Veja a [documentação oficial de conexões](https://supabase.com/docs/guides/database/connecting-to-postgres).

3. Inicie o Redis. Por exemplo, com Docker:

```bash
docker run --name aurora-redis -p 127.0.0.1:6379:6379 -d redis:7
```

Configure `REDIS_URL=redis://localhost:6379/0`. Para um serviço remoto, use a URL e o TLS fornecidos pelo provedor. Use uma instância ou banco Redis dedicado ao projeto. Defina também uma `FLASK_SECRET_KEY` aleatória no `.env`. Nunca envie `.env`, URLs com senha ou chaves ao GitHub.

4. Crie os objetos e dados de exemplo no Supabase e inicie a aplicação:

```bash
python src/init_supabase.py
python src/app.py
```

Abra <http://127.0.0.1:5001>. O inicializador cria o schema `aurora` em uma transação e recusa executá-lo se o schema já existir, para preservar os dados. Ele não deve ser usado para atualizar instalações existentes. `src/init_db.py` continua disponível apenas para PostgreSQL local e **apaga os dados da aplicação local** ao recriar as tabelas.

## Como o Supabase é utilizado

O Supabase fornece o banco PostgreSQL que armazena os dados do sistema. Ao cadastrar um produto ou registrar uma venda, por exemplo, a aplicação grava as informações no banco; quando as páginas são abertas, elas consultam os dados armazenados.

As principais operações de banco são:

- A **procedure `sp_realizar_venda`** verifica o estoque, registra o pedido e seus itens e desconta as unidades vendidas. Tudo acontece em uma transação: se ocorrer um erro, a venda não fica salva pela metade.
- A **function `fn_calcular_total_pedido`** calcula o valor total de um pedido a partir dos seus itens.
- A **view `vw_relatorio_vendas`** reúne informações usadas pelo painel e pelo relatório.

O Flask conecta diretamente ao PostgreSQL do Supabase pelo backend, usando `SUPABASE_DB_URL`; as telas não recebem a senha. As tabelas, view, function, procedure e dados de exemplo ficam no schema `aurora`, que não é exposto pela Data API na configuração padrão. O acesso público ao schema é revogado e as tabelas têm RLS habilitada sem políticas públicas. Não adicione `aurora` aos schemas expostos sem configurar permissões e políticas adequadas.

A aplicação usa uma conexão privilegiada no servidor e não implementa autenticação de usuários. Ela foi preparada para execução local e demonstração acadêmica: não a exponha na internet ou use dados reais sem implementar autenticação, autorização e medidas adicionais de segurança. A integração é por conexão PostgreSQL, sem necessidade da biblioteca ou chave de API do Supabase.

## Como o Redis é utilizado

O painel consulta a view para calcular a quantidade de vendas e o faturamento. Como esses totais podem ser lidos várias vezes sem mudar, o backend guarda o resultado no Redis por **60 segundos**. Quando não há cache válido, consulta o banco; nas leituras seguintes, pode reutilizar o valor em cache, reduzindo consultas repetidas. O restante do painel continua consultando o banco diretamente.

Após gravações feitas pela aplicação, o cache é invalidado depois do commit; a próxima leitura consulta o banco novamente. Uma versão no Redis impede que uma consulta anterior a uma gravação substitua o cache depois dela. Alterações realizadas diretamente no banco ou durante indisponibilidade do Redis podem deixar o resumo antigo até o TTL expirar. Se o Redis estiver indisponível, a aplicação consulta o banco e informa isso no painel; o banco continua sendo a fonte de dados.

## Como demonstrar as integrações

As próprias telas ajudam a identificar o papel de cada tecnologia. Para demonstrar:

1. Abra o painel e observe a origem do resumo. Quando o cache estiver vazio ou expirado, a leitura vem de **Supabase/banco (consulta)**; atualize dentro de 60 segundos para ver **Redis (cache)**. Se já houver um resumo válido no cache, a primeira abertura poderá mostrar Redis.
2. No Supabase, abra o Table Editor ou SQL Editor e mostre os dados no schema `aurora`. Crie uma venda pela interface e mostre o pedido e a baixa do estoque no banco.
3. Volte ao painel: depois da venda, o resumo vem novamente do banco; atualize outra vez para ver a leitura do Redis.
4. Opcionalmente, em outro terminal, execute `docker exec aurora-redis redis-cli GET aurora:painel:resumo` e `docker exec aurora-redis redis-cli TTL aurora:painel:resumo` para mostrar o valor e sua expiração. O texto do painel é a fonte usada naquela requisição; se a chave já tiver expirado, atualize o painel antes de consultar o Redis.
5. Explique que o cache reduz consultas repetidas e que sua invalidação e TTL limitam dados desatualizados. Mostre também o cadastro e o relatório na interface.

## Dados de exemplo

A instalação nova inclui três pedidos, totalizando R$ 215,47. O pedido 1 totaliza R$ 84,67. O mel começa com quatro unidades: tentar vender cinco deve retornar erro sem gravar uma venda parcial.

## Organização

- `src/app.py`: rotas e telas; `src/banco.py`: conexão e consultas.
- `src/cache.py`: leitura, gravação e invalidação do cache Redis.
- `src/init_supabase.py`: instalação inicial no Supabase.
- `database/`: tabelas, function, view, procedure e dados de exemplo.
- `src/templates/` e `src/static/`: interface HTML e CSS.
