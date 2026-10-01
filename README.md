# Aurora Vendas

Sistema de vendas de uma mercearia: cadastro de clientes e produtos, registro de venda, consulta de pedidos e relatório.

**Vídeo:** https://youtu.be/DNc1sK8VqmE

- **Integrante:** Caio Campos
- **Disciplina:** Projeto de Banco de Dados
- **Professor:** Anderson Soares

## O que o sistema faz

A ideia é a loja vender sem bagunçar o estoque e sem montar a mesma consulta de relatório em várias telas.

Uma venda mexe em pedido, itens e estoque ao mesmo tempo. Se isso ficasse só no Python, dava para baixar o estoque e falhar na hora de gravar o pedido. Por isso a venda inteira está numa procedure do PostgreSQL. Se der erro no meio, nada fica salvo pela metade.

Telas:

| Tela | Rota | Função |
| --- | --- | --- |
| Painel | `/` | Resumo de vendas, faturamento, clientes, produtos e estoque baixo |
| Clientes | `/clientes` | CRUD de clientes (com busca) |
| Produtos | `/produtos` | CRUD de produtos (com busca) |
| Nova venda | `/vendas/nova` | Registra venda pela procedure |
| Pedidos | `/pedidos` | Lista pedidos; total pela function |
| Detalhe | `/pedidos/<id>` | Itens e total do pedido |
| Relatório | `/relatorio` | Vendas filtradas pela view |

## Tecnologias

- Python + Flask
- PostgreSQL
- HTML e CSS
- `psycopg` para conectar e rodar o SQL direto nas telas

## Onde fica o banco

Os dados **não** ficam na pasta do projeto. A pasta `database/` só tem os scripts SQL (tabelas, view, function, procedure e inserts de exemplo). Esses arquivos vão pro GitHub.

Os registros ficam no PostgreSQL local, no banco `aurora_vendas`. A conexão vem do arquivo `.env` (copiado de `.env.example`):

```
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=sua_senha
PGDATABASE=aurora_vendas
```

O `.env` não sobe pro Git. Quem grava no disco é o PostgreSQL; a aplicação só manda SQL por cima do `psycopg`.

### Tabelas

- `clientes` — nome, e-mail (único), telefone
- `produtos` — nome, preço, estoque, ativo
- `pedidos` — cliente, data, observação
- `itens_pedido` — produto, quantidade e `preco_unitario` da hora da venda

O preço fica gravado no item de propósito: se o produto mudar de preço depois, o pedido antigo não muda.

Script: `database/tables/01_tabelas.sql`.

## View, function e procedure

### View `vw_relatorio_vendas`

Arquivo: `database/views/01_vw_relatorio_vendas.sql`

Junta pedido, cliente e itens e devolve uma linha por pedido, com total.

Usada em `src/app.py` nas funções `painel` e `relatorio`.

Com os dados de exemplo: 3 vendas e faturamento **R$ 215,47**.

### Function `fn_calcular_total_pedido`

Arquivo: `database/functions/01_fn_calcular_total_pedido.sql`

Recebe o id do pedido e devolve a soma de quantidade × preço do item. Não grava nada.

Usada em `src/app.py` nas funções `pedidos` e `detalhe_pedido`.

Pedido 1 (Ana Lima): **R$ 84,67**.

### Procedure `sp_realizar_venda`

Arquivo: `database/procedures/01_sp_realizar_venda.sql`

Chamada pela tela Nova venda, na função `registrar_venda` de `src/app.py`:

```sql
CALL sp_realizar_venda(%s, %s, %s, %s, %s)
```

Ela confere cliente e itens, cria o pedido, grava os itens com o preço da hora e baixa o estoque. Se não tiver estoque, recusa e não grava.

Exemplo: o mel começa com 4 unidades; vender 5 mostra o erro da procedure e o estoque continua 4.

## Estrutura do projeto

```
├── .env.example
├── requirements.txt
├── database/
│   ├── 00_criar_banco.sql
│   ├── setup.sql
│   ├── tables/
│   ├── functions/
│   ├── views/
│   ├── procedures/
│   └── inserts/
└── src/
    ├── init_db.py      # cria o banco e carrega os scripts
    ├── banco.py        # conexão e consultas
    ├── app.py          # telas (Flask)
    ├── templates/
    └── static/css/
```

`src/init_db.py` cria o banco se precisar e roda os scripts de novo. Isso apaga os dados da aplicação e coloca o exemplo outra vez.

## Como executar

```powershell
cd "D:\CRUD PBD"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Coloque a senha no `.env` e rode:

```powershell
python src/init_db.py
python src/app.py
```

Abra http://127.0.0.1:5000

Também dá para usar o `psql` com `database/00_criar_banco.sql` e `database/setup.sql`, mas o caminho mais simples é o `init_db.py`.

## Conferência rápida

- Pedido 1 = R$ 84,67 (function)
- Faturamento da view = R$ 215,47
- Nova venda baixa estoque e aparece no relatório
- Vender 5 de mel não grava a venda
