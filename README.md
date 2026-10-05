# Aurora Vendas

Sistema de vendas de uma mercearia desenvolvido para a disciplina **Projeto de Banco de Dados**.

O sistema permite cadastrar clientes e produtos, registrar vendas com baixa de estoque, consultar pedidos e gerar relatório de faturamento. A regra de negócio principal fica no PostgreSQL: a venda usa **procedure**, o total do pedido usa **function** e o relatório usa **view**.

| | |
| --- | --- |
| **Integrante** | Caio Campos |
| **Disciplina** | Projeto de Banco de Dados |
| **Professor** | Anderson Soares |
| **Vídeo** | [Assistir no YouTube](https://youtu.be/DNc1sK8VqmE) |
| **Repositório** | [caio089/CRUD-PBD](https://github.com/caio089/CRUD-PBD) |

---

## Tecnologias

- Python 3
- Flask
- PostgreSQL
- HTML e CSS
- psycopg (conexão e SQL direto nas telas)

---

## O que o sistema faz

A mercearia precisa vender sem deixar o estoque inconsistente e sem remontar a mesma consulta de relatório em várias telas.

Uma venda altera pedido, itens e estoque ao mesmo tempo. Se isso ficasse só no Python, dava para baixar estoque e falhar na hora de gravar o pedido. Por isso a venda completa está na procedure `sp_realizar_venda`. Se algo falha no meio, nada fica salvo pela metade.

### Telas

| Tela | Rota | Descrição |
| --- | --- | --- |
| Painel | `/` | Resumo de vendas, faturamento, clientes, produtos e estoque baixo |
| Clientes | `/clientes` | Cadastro, busca, edição e exclusão de clientes |
| Produtos | `/produtos` | Cadastro, busca, edição e exclusão de produtos |
| Nova venda | `/vendas/nova` | Registra a venda chamando a procedure |
| Pedidos | `/pedidos` | Lista os pedidos; o total vem da function |
| Detalhe | `/pedidos/<id>` | Mostra itens, preços e total do pedido |
| Relatório | `/relatorio` | Filtra vendas pela view (cliente e período) |

---

## Banco de dados

### Onde os dados ficam

Os dados **não** ficam na pasta do projeto. A pasta `database/` contém apenas os scripts SQL (estrutura, view, function, procedure e inserts de exemplo).

Os registros ficam no PostgreSQL local, no banco `aurora_vendas`. A aplicação conecta usando o arquivo `.env` (copiado de `.env.example`):

```env
PGHOST=localhost
PGPORT=5432
PGUSER=postgres
PGPASSWORD=sua_senha
PGDATABASE=aurora_vendas
```

O arquivo `.env` não sobe para o GitHub. Quem grava no disco é o PostgreSQL; a aplicação envia SQL através do `psycopg`.

### Tabelas

| Tabela | Conteúdo |
| --- | --- |
| `clientes` | Nome, e-mail (único) e telefone |
| `produtos` | Nome, preço, estoque e se está ativo |
| `pedidos` | Cliente, data e observação |
| `itens_pedido` | Produto, quantidade e `preco_unitario` da hora da venda |

O preço fica gravado no item de propósito: se o produto mudar de preço depois, o pedido antigo não muda.

Script das tabelas: `database/tables/01_tabelas.sql`

---

## View, function e procedure

### View — `vw_relatorio_vendas`

- **Arquivo:** `database/views/01_vw_relatorio_vendas.sql`
- **O que faz:** junta pedido, cliente e itens e devolve uma linha por pedido, com total
- **Onde usa:** `src/app.py` → funções `painel` e `relatorio`
- **Exemplo:** 3 vendas e faturamento de **R$ 215,47**

### Function — `fn_calcular_total_pedido`

- **Arquivo:** `database/functions/01_fn_calcular_total_pedido.sql`
- **O que faz:** recebe o id do pedido e devolve a soma de quantidade × preço do item (não grava nada)
- **Onde usa:** `src/app.py` → funções `pedidos` e `detalhe_pedido`
- **Exemplo:** pedido 1 (Ana Lima) = **R$ 84,67**

### Procedure — `sp_realizar_venda`

- **Arquivo:** `database/procedures/01_sp_realizar_venda.sql`
- **O que faz:** confere cliente e itens, cria o pedido, grava os itens com o preço da hora e baixa o estoque
- **Onde usa:** tela Nova venda → função `registrar_venda` em `src/app.py`

```sql
CALL sp_realizar_venda(%s, %s, %s, %s, %s)
```

Se não houver estoque suficiente, a procedure recusa e não grava a venda.  
Exemplo: o mel começa com 4 unidades; tentar vender 5 mostra o erro e o estoque continua 4.

---

## Estrutura do projeto

```
CRUD-PBD/
├── .env.example
├── requirements.txt
├── README.md
├── database/
│   ├── 00_criar_banco.sql
│   ├── setup.sql
│   ├── tables/          # tabelas
│   ├── functions/       # fn_calcular_total_pedido
│   ├── views/           # vw_relatorio_vendas
│   ├── procedures/      # sp_realizar_venda
│   └── inserts/         # dados de exemplo
└── src/
    ├── init_db.py       # cria o banco e carrega os scripts
    ├── banco.py         # conexão e consultas
    ├── app.py           # rotas das telas (Flask)
    ├── templates/       # HTML
    └── static/css/      # estilo
```

O comando `python src/init_db.py` cria o banco se precisar e roda os scripts de novo. Isso apaga os dados da aplicação e recarrega o exemplo.

---

## Como executar

1. Instale o PostgreSQL e anote a senha do usuário `postgres`.
2. Na pasta do projeto:

```powershell
cd "D:\CRUD PBD"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

3. Coloque a senha no arquivo `.env`.
4. Crie o banco e suba as telas:

```powershell
python src/init_db.py
python src/app.py
```

5. Abra http://127.0.0.1:5000

Também é possível usar o `psql` com `database/00_criar_banco.sql` e `database/setup.sql`. O caminho mais simples é o `init_db.py`.

---

## Dados de exemplo

| Pedido | Cliente | Total |
| --- | --- | --- |
| 1 | Ana Lima | R$ 84,67 |
| 2 | Bruno Costa | R$ 46,90 |
| 3 | Carla Mendes | R$ 83,90 |
| **Total (view)** | | **R$ 215,47** |

---

## Como testar

- Pedido 1 aparece como **R$ 84,67** (valor da function)
- Painel e relatório mostram **3 vendas** e faturamento **R$ 215,47** (valor da view)
- Uma venda nova baixa o estoque e aparece no relatório
- Vender 5 unidades de mel mostra o erro da procedure e não grava a venda

---

## Vídeo

Demonstração completa do sistema (telas, view, function e procedure):

**https://youtu.be/DNc1sK8VqmE**
