# Aurora Vendas

Sistema simples de vendas de uma mercearia: cadastro de clientes e produtos, registro de venda, consulta de pedidos e relatório.

> Antes de entregar, preencha os campos abaixo.

- **Integrante:** [seu nome completo]
- **Disciplina:** [nome da disciplina]
- **Professor:** [nome do professor]

## Sobre o projeto

A loja precisa vender sem deixar o estoque errado e ver o total das vendas sem remontar a consulta na tela.

- A **procedure** grava a venda inteira (pedido, itens e baixa de estoque).
- A **function** calcula o total de um pedido com o preço que foi gravado na hora.
- A **view** junta pedido, cliente e itens para o relatório.

## Tecnologias utilizadas

- Python
- Flask
- PostgreSQL
- HTML e CSS

As telas chamam o SQL direto, com `psycopg`. Assim dá para ver a view, a function e a procedure no código.

## Banco de dados

- **SGBD:** PostgreSQL

**Tabelas:** `clientes`, `produtos`, `pedidos`, `itens_pedido`

**View:** `vw_relatorio_vendas`  
Usada no painel e na tela Relatório. O `SELECT` está em `src/app.py`, nas funções `painel` e `relatorio`.

**Function:** `fn_calcular_total_pedido(id_pedido)`  
Devolve o total do pedido. Usada na lista e no detalhe de pedidos (`src/app.py`).

**Procedure:** `sp_realizar_venda(id_cliente, produtos, quantidades, observacao, id_pedido)`  
Cria o pedido, grava os itens com o preço da hora e baixa o estoque. A tela Nova venda faz o `CALL` em `registrar_venda`, no `src/app.py`.

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
4. Crie o banco e os dados de exemplo (isso apaga o que já existir na aplicação):

```powershell
python src/init_db.py
python src/app.py
```

5. Abra http://127.0.0.1:5000

O pedido 1 fica em R$ 84,67. O faturamento da view fica em R$ 215,47. O mel tem 4 unidades: vender 5 mostra a mensagem da procedure e não grava a venda.

Quem for usar o `psql` pode rodar `database/00_criar_banco.sql` e depois `database/setup.sql`.

## Vídeo

O roteiro está em [docs/roteiro-video.md](docs/roteiro-video.md). O vídeo precisa ser gravado por você.

## Antes de entregar

- [ ] Preencher nome, disciplina e professor
- [ ] Rodar o projeto
- [ ] Mostrar relatório, total do pedido e uma venda
- [ ] Publicar no GitHub
- [ ] Gravar o vídeo
