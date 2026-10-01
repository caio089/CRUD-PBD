# Aurora Vendas

Sistema de vendas de uma mercearia. Eu cadastro clientes e produtos, registro a venda, consulto os pedidos e vejo o relatório. O estoque só baixa quando a venda inteira é gravada.

**Vídeo da apresentação:** https://youtu.be/DNc1sK8VqmE

Nesse vídeo eu mostro as telas e, no código, onde entram a view, a function e a procedure.

- **Repositório:** [caio089/CRUD-PBD](https://github.com/caio089/CRUD-PBD)
- **Integrante:** [seu nome completo]
- **Disciplina:** [nome da disciplina]
- **Professor:** [nome do professor]

## O que o sistema faz

A loja precisa vender sem deixar o estoque errado e sem recalcular o total na mão em cada tela.

Uma venda mexe em três lugares ao mesmo tempo: o pedido, os itens e o estoque. Se isso ficasse espalhado só no Python, dava para baixar o estoque e falhar na hora de gravar o pedido. Por isso a venda inteira está numa procedure do PostgreSQL. Se alguma conferência falha, nada fica salvo pela metade.

O que dá para fazer nas telas:

| Tela | Endereço | O que eu faço nela |
| --- | --- | --- |
| Painel | `/` | Vejo quantas vendas existem, o faturamento, clientes, produtos ativos, as últimas vendas e o estoque baixo (5 unidades ou menos). |
| Clientes | `/clientes` | Listo, busco, cadastro, edito e excluo clientes. Quem já tem pedido não pode ser excluído. |
| Produtos | `/produtos` | Listo, busco, cadastro, edito e excluo produtos. Produto que já foi vendido não apaga; eu desmarco **Ativo**. |
| Nova venda | `/vendas/nova` | Escolho o cliente e até três itens. Ao confirmar, o sistema chama a procedure. |
| Pedidos | `/pedidos` | Listo os pedidos. O total de cada um vem da function. |
| Detalhe do pedido | `/pedidos/<id>` | Vejo cliente, observação, itens, preço da hora e o total da function. |
| Relatório | `/relatorio` | Filtro por cliente e por período. Os números vêm da view. |

O menu dessas telas está em `src/templates/base.html`. Cada página fica em `src/templates/` e o visual em `src/static/css/estilo.css`.

## Onde está o banco e onde os dados ficam guardados

O banco **não fica dentro da pasta do projeto**. A pasta `database/` só tem os scripts SQL: o desenho das tabelas, a view, a function, a procedure e os dados de exemplo. Esses arquivos vão para o GitHub. Os registros de verdade não.

Os dados ficam no **PostgreSQL**, instalado na máquina, no banco chamado `aurora_vendas`.

A aplicação descobre como conectar lendo o arquivo `.env` na raiz do projeto (a partir de `.env.example`):

| Variável | O que significa | Valor de exemplo |
| --- | --- | --- |
| `PGHOST` | Em qual computador o PostgreSQL está | `localhost` |
| `PGPORT` | Porta do servidor | `5432` |
| `PGUSER` | Usuário | `postgres` |
| `PGPASSWORD` | Senha desse usuário | a senha da instalação |
| `PGDATABASE` | Nome do banco da aplicação | `aurora_vendas` |

O arquivo `.env` não entra no Git (`/.gitignore`). Quem clonar o projeto copia o exemplo e coloca a própria senha.

Quem guarda as linhas no disco é o PostgreSQL, no diretório de dados do servidor (no Windows, a pasta `data` da instalação; no Linux deste ambiente, o cluster fica em `/var/lib/postgresql/16/main`). Eu não abro esses arquivos na mão. Eu falo com o banco pelo `psycopg`, e o servidor é quem grava em disco.

Dentro de `aurora_vendas`, a informação fica nestas tabelas:

| Tabela | O que guarda |
| --- | --- |
| `clientes` | Nome, e-mail (único) e telefone. |
| `produtos` | Nome, preço atual, estoque e se está ativo. Preço e estoque não podem ser negativos. |
| `pedidos` | Qual cliente comprou, a data (preenchida sozinha se eu não informar) e uma observação opcional. |
| `itens_pedido` | Cada produto do pedido, a quantidade e o `preco_unitario` da hora da venda. |

O `preco_unitario` é de propósito. Se o café mudar de preço amanhã, o pedido antigo continua com o preço que foi cobrado. O preço novo fica só na tabela `produtos`.

Ligações:

- `pedidos.cliente_id` aponta para `clientes.id`.
- `itens_pedido.pedido_id` aponta para `pedidos.id`. Se o pedido some, os itens somem junto (`ON DELETE CASCADE`).
- `itens_pedido.produto_id` aponta para `produtos.id`.

O script das tabelas está em `database/tables/01_tabelas.sql`.

## Como eu usei o banco no código

As telas não montam o relatório, o total nem a venda só em Python. Elas chamam objetos do PostgreSQL. A conexão está em `src/banco.py`: `conectar`, `buscar_todos`, `buscar_um` e `executar`. As consultas usam `%s` no lugar dos valores digitados, para não concatenar texto do usuário dentro do SQL.

### View `vw_relatorio_vendas`

Arquivo: `database/views/01_vw_relatorio_vendas.sql`.

Ela junta `pedidos`, `clientes` e `itens_pedido` e devolve **uma linha por pedido**, com data, nome, e-mail, quantidade de itens, quantidade de produtos e valor total.

Eu uso essa view em dois lugares de `src/app.py`:

- `painel()` lê a quantidade de vendas, o faturamento e as cinco vendas mais recentes.
- `relatorio()` faz `SELECT * FROM vw_relatorio_vendas` e acrescenta filtro de cliente e de data quando eu preencho o formulário.

Com os dados de exemplo, a view tem 3 linhas e o faturamento é **R$ 215,47**.

### Function `fn_calcular_total_pedido`

Arquivo: `database/functions/01_fn_calcular_total_pedido.sql`.

Ela só calcula. Não grava nada. Recebe o id do pedido e devolve a soma de `quantidade * preco_unitario` dos itens. Se o pedido não tiver item, devolve zero.

Eu chamo essa function em `src/app.py`:

- `pedidos()`, na lista.
- `detalhe_pedido()`, no pedido aberto.

O pedido 1 (Ana Lima) fecha em **R$ 84,67**: dois cafés a R$ 28,90, um pão a R$ 9,50 e três leites a R$ 5,79.

### Procedure `sp_realizar_venda`

Arquivo: `database/procedures/01_sp_realizar_venda.sql`.

A tela Nova venda chama essa procedure pela função `registrar_venda` em `src/app.py`:

```sql
CALL sp_realizar_venda(%s, %s, %s, %s, %s)
```

Parâmetros, nesta ordem: id do cliente, lista de ids dos produtos, lista de quantidades, observação e o id do pedido (a procedure devolve o número gerado).

O que ela faz, em ordem:

1. Confere se o cliente existe.
2. Confere se há pelo menos um item e se as duas listas têm o mesmo tamanho.
3. Insere o pedido.
4. Para cada item, confere se a quantidade é maior que zero, se o produto existe, se está ativo e se há estoque.
5. Grava o item com o preço daquela hora.
6. Baixa o estoque.

Se algo falha, ela dispara `RAISE EXCEPTION` com uma frase clara (por exemplo, estoque insuficiente). O Python desfaz a transação em `registrar_venda` e mostra essa frase na tela, pela função `mensagem_banco` em `src/banco.py`.

O mel silvestre começa com **4** unidades. Se eu tentar vender 5, a procedure recusa, o pedido não é criado e o estoque continua 4.

## O que cada arquivo do código faz

```
CRUD-PBD/
├── .env.example          # modelo da conexão (eu copio para .env)
├── requirements.txt      # Flask, psycopg e python-dotenv
├── database/
│   ├── 00_criar_banco.sql
│   ├── setup.sql         # junta os scripts, para quem usa o psql
│   ├── tables/           # tabelas
│   ├── functions/        # fn_calcular_total_pedido
│   ├── views/            # vw_relatorio_vendas
│   ├── procedures/       # sp_realizar_venda
│   └── inserts/          # clientes, produtos e 3 pedidos de exemplo
├── src/
│   ├── init_db.py        # cria o banco e roda os scripts
│   ├── banco.py          # abre a conexão e executa SQL
│   ├── app.py            # rotas das telas
│   ├── templates/        # HTML de cada tela
│   └── static/css/       # estilo
└── docs/roteiro-video.md # o que eu falei no vídeo
```

`src/app.py` é o Flask. As rotas estão agrupadas por tela: painel, clientes, produtos, nova venda, pedidos e relatório. Valores de dinheiro passam pelo filtro `moeda` (formato `R$ 84,67`) e as datas pelo filtro `datahora`.

`src/init_db.py` conecta no banco `postgres`, cria `aurora_vendas` se ele ainda não existir e executa os scripts nesta ordem: tabelas, function, view, procedure e inserts. Esse comando **apaga os dados da aplicação e carrega o exemplo de novo**. No final ele imprime o total do pedido 1 e a quantidade de linhas da view, para eu saber que o banco subiu certo.

Os dados iniciais estão em `database/inserts/01_dados_iniciais.sql`:

| Pedido | Cliente | Conta | Total |
| --- | --- | --- | --- |
| 1 | Ana Lima | 2×28,90 + 1×9,50 + 3×5,79 | R$ 84,67 |
| 2 | Bruno Costa | 22,00 + 24,90 | R$ 46,90 |
| 3 | Carla Mendes | 34,50 + 2×16,40 + 2×8,30 | R$ 83,90 |

84,67 + 46,90 + 83,90 = **215,47**, que é o faturamento do painel e do relatório.

Também entram Diego Alves e Elena Rocha, sem pedido, e o biscoito cream cracker inativo, com estoque zero. Ele não aparece na nova venda.

## Como executar

1. Instalar o PostgreSQL e anotar a senha do usuário `postgres`.
2. Na pasta do projeto:

```powershell
cd "D:\CRUD PBD"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

3. Colocar a senha no arquivo `.env`.
4. Criar o banco, carregar o exemplo e subir as telas:

```powershell
python src/init_db.py
python src/app.py
```

5. Abrir http://127.0.0.1:5000

No Linux o caminho do ambiente virtual é `source .venv/bin/activate`. O resto é igual.

Quem preferir o `psql` pode rodar `database/00_criar_banco.sql` conectado ao banco `postgres` e, em seguida, `database/setup.sql` conectado em `aurora_vendas`. O caminho que eu uso no dia a dia é o `python src/init_db.py`.

## O que conferir para saber que está certo

- O pedido 1 aparece como **R$ 84,67** na lista e no detalhe. Esse valor sai da function.
- O painel e o relatório mostram **3 vendas** e faturamento **R$ 215,47**. Esse valor sai da view.
- Uma venda nova (por exemplo, 1 café) abre o pedido com o total da function, o estoque do produto cai e a venda aparece no relatório.
- Vender 5 unidades de mel mostra a mensagem da procedure e não grava a venda.

O roteiro que eu segui na gravação está em [docs/roteiro-video.md](docs/roteiro-video.md). O vídeo publicado é este: https://youtu.be/DNc1sK8VqmE
