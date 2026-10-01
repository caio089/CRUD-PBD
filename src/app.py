"""Sistema de vendas da mercearia Aurora.

Telas que usam o banco de um jeito especial:
- Painel e Relatório leem a view vw_relatorio_vendas
- Pedidos chamam a function fn_calcular_total_pedido
- Nova venda chama a procedure sp_realizar_venda
"""

from decimal import Decimal, InvalidOperation

import psycopg
from flask import Flask, flash, redirect, render_template, request, url_for

from banco import buscar_todos, buscar_um, conectar, executar, mensagem_banco

app = Flask(__name__)
app.secret_key = "aurora123"


def moeda(valor):
    if valor is None:
        valor = 0
    return "R$ " + f"{valor:.2f}".replace(".", ",")


def data_br(valor):
    if valor is None:
        return ""
    return valor.strftime("%d/%m/%Y %H:%M")


app.jinja_env.filters["moeda"] = moeda
app.jinja_env.filters["datahora"] = data_br


def ler_preco(texto):
    texto = (texto or "").strip().replace(",", ".")
    if texto == "":
        return None
    return Decimal(texto).quantize(Decimal("0.01"))


def registrar_venda(id_cliente, produtos, quantidades, observacao):
    """Chama a procedure e pega o id do pedido criado na mesma conexão."""
    conn = conectar()
    try:
        cur = conn.cursor()
        cur.execute(
            "CALL sp_realizar_venda(%s, %s, %s, %s, %s)",
            (id_cliente, produtos, quantidades, observacao, 0),
        )
        if cur.description:
            cur.fetchall()
        # currval é o id que o INSERT da procedure acabou de gerar nesta conexão
        cur.execute("SELECT currval(pg_get_serial_sequence('pedidos', 'id')) AS id")
        id_pedido = cur.fetchone()["id"]
        conn.commit()
        return id_pedido
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def separar_itens(ids_form, qtds_form):
    ids = []
    qtds = []
    for id_produto, qtd_texto in zip(ids_form, qtds_form):
        id_produto = (id_produto or "").strip()
        qtd_texto = (qtd_texto or "").strip()
        if id_produto == "" and qtd_texto == "":
            continue
        if id_produto == "" or qtd_texto == "":
            raise ValueError("Preencha produto e quantidade no mesmo item.")
        try:
            qtd = int(qtd_texto)
            id_num = int(id_produto)
        except ValueError as erro:
            raise ValueError("Produto ou quantidade inválidos.") from erro
        if qtd <= 0:
            raise ValueError("A quantidade precisa ser maior que zero.")
        ids.append(id_num)
        qtds.append(qtd)
    return ids, qtds


def itens_do_formulario():
    ids = request.form.getlist("produto_id")
    qtds = request.form.getlist("quantidade")
    itens = []
    for i in range(3):
        itens.append({
            "produto_id": ids[i] if i < len(ids) else "",
            "quantidade": qtds[i] if i < len(qtds) else "",
        })
    return itens


# --- Painel: usa a view ---

@app.route("/")
def painel():
    resumo = buscar_um(
        """
        SELECT COUNT(*) AS qtd_vendas,
               COALESCE(SUM(valor_total), 0) AS faturamento
        FROM vw_relatorio_vendas
        """
    )
    vendas = buscar_todos(
        """
        SELECT id_pedido, data_pedido, cliente, valor_total
        FROM vw_relatorio_vendas
        ORDER BY data_pedido DESC
        LIMIT 5
        """
    )
    qtd_clientes = buscar_um("SELECT COUNT(*) AS total FROM clientes")
    qtd_produtos = buscar_um("SELECT COUNT(*) AS total FROM produtos WHERE ativo = TRUE")
    estoque_baixo = buscar_todos(
        """
        SELECT id, nome, estoque
        FROM produtos
        WHERE ativo = TRUE AND estoque <= 5
        ORDER BY estoque, nome
        """
    )
    return render_template(
        "painel.html",
        resumo=resumo,
        vendas=vendas,
        qtd_clientes=qtd_clientes["total"],
        qtd_produtos=qtd_produtos["total"],
        estoque_baixo=estoque_baixo,
    )


# --- Clientes ---

@app.route("/clientes")
def clientes():
    busca = request.args.get("q", "").strip()
    if busca:
        lista = buscar_todos(
            """
            SELECT id, nome, email, telefone
            FROM clientes
            WHERE nome ILIKE %s OR email ILIKE %s
            ORDER BY nome
            """,
            (f"%{busca}%", f"%{busca}%"),
        )
    else:
        lista = buscar_todos(
            "SELECT id, nome, email, telefone FROM clientes ORDER BY nome"
        )
    return render_template("clientes/lista.html", clientes=lista, q=busca)


@app.route("/clientes/novo", methods=["GET", "POST"])
def novo_cliente():
    nome = ""
    email = ""
    telefone = ""
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefone = request.form.get("telefone", "").strip()
        if nome == "" or "@" not in email:
            flash("Preencha o nome e um e-mail válido.", "erro")
        else:
            try:
                executar(
                    "INSERT INTO clientes (nome, email, telefone) VALUES (%s, %s, %s)",
                    (nome, email, telefone or None),
                )
            except psycopg.Error as erro:
                if erro.sqlstate == "23505":
                    flash("Já existe um cliente com esse e-mail.", "erro")
                else:
                    flash(mensagem_banco(erro), "erro")
            else:
                flash("Cliente cadastrado.", "ok")
                return redirect(url_for("clientes"))
    return render_template(
        "clientes/form.html",
        titulo="Novo cliente",
        id_cliente=None,
        nome=nome,
        email=email,
        telefone=telefone,
    )


@app.route("/clientes/<int:id_cliente>/editar", methods=["GET", "POST"])
def editar_cliente(id_cliente):
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefone = request.form.get("telefone", "").strip()
        if nome == "" or "@" not in email:
            flash("Preencha o nome e um e-mail válido.", "erro")
        else:
            try:
                executar(
                    """
                    UPDATE clientes
                       SET nome = %s, email = %s, telefone = %s
                     WHERE id = %s
                    """,
                    (nome, email, telefone or None, id_cliente),
                )
            except psycopg.Error as erro:
                if erro.sqlstate == "23505":
                    flash("Já existe um cliente com esse e-mail.", "erro")
                else:
                    flash(mensagem_banco(erro), "erro")
            else:
                flash("Cliente atualizado.", "ok")
                return redirect(url_for("clientes"))
        return render_template(
            "clientes/form.html",
            titulo="Editar cliente",
            id_cliente=id_cliente,
            nome=nome,
            email=email,
            telefone=telefone,
        )

    cliente = buscar_um(
        "SELECT id, nome, email, telefone FROM clientes WHERE id = %s",
        (id_cliente,),
    )
    if cliente is None:
        flash("Cliente não encontrado.", "erro")
        return redirect(url_for("clientes"))
    return render_template(
        "clientes/form.html",
        titulo="Editar cliente",
        id_cliente=id_cliente,
        nome=cliente["nome"],
        email=cliente["email"],
        telefone=cliente["telefone"] or "",
    )


@app.route("/clientes/<int:id_cliente>/excluir", methods=["POST"])
def excluir_cliente(id_cliente):
    try:
        executar("DELETE FROM clientes WHERE id = %s", (id_cliente,))
    except psycopg.Error as erro:
        if erro.sqlstate == "23503":
            flash("Esse cliente tem pedidos e não pode ser excluído.", "erro")
        else:
            flash(mensagem_banco(erro), "erro")
    else:
        flash("Cliente excluído.", "ok")
    return redirect(url_for("clientes"))


# --- Produtos ---

@app.route("/produtos")
def produtos():
    busca = request.args.get("q", "").strip()
    if busca:
        lista = buscar_todos(
            """
            SELECT id, nome, preco, estoque, ativo
            FROM produtos
            WHERE nome ILIKE %s
            ORDER BY nome
            """,
            (f"%{busca}%",),
        )
    else:
        lista = buscar_todos(
            "SELECT id, nome, preco, estoque, ativo FROM produtos ORDER BY nome"
        )
    return render_template("produtos/lista.html", produtos=lista, q=busca)


@app.route("/produtos/novo", methods=["GET", "POST"])
def novo_produto():
    nome = ""
    preco = ""
    estoque = ""
    ativo = True
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        preco = request.form.get("preco", "").strip()
        estoque = request.form.get("estoque", "").strip()
        ativo = request.form.get("ativo") == "on"
        try:
            preco_num = ler_preco(preco)
            estoque_num = int(estoque)
            if nome == "" or preco_num is None or preco_num < 0 or estoque_num < 0:
                raise ValueError
        except (ValueError, InvalidOperation):
            flash("Preencha nome, preço e estoque com valores válidos.", "erro")
        else:
            try:
                executar(
                    """
                    INSERT INTO produtos (nome, preco, estoque, ativo)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (nome, preco_num, estoque_num, ativo),
                )
            except psycopg.Error as erro:
                flash(mensagem_banco(erro), "erro")
            else:
                flash("Produto cadastrado.", "ok")
                return redirect(url_for("produtos"))
    return render_template(
        "produtos/form.html",
        titulo="Novo produto",
        id_produto=None,
        nome=nome,
        preco=preco,
        estoque=estoque,
        ativo=ativo,
    )


@app.route("/produtos/<int:id_produto>/editar", methods=["GET", "POST"])
def editar_produto(id_produto):
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        preco = request.form.get("preco", "").strip()
        estoque = request.form.get("estoque", "").strip()
        ativo = request.form.get("ativo") == "on"
        try:
            preco_num = ler_preco(preco)
            estoque_num = int(estoque)
            if nome == "" or preco_num is None or preco_num < 0 or estoque_num < 0:
                raise ValueError
        except (ValueError, InvalidOperation):
            flash("Preencha nome, preço e estoque com valores válidos.", "erro")
        else:
            try:
                executar(
                    """
                    UPDATE produtos
                       SET nome = %s, preco = %s, estoque = %s, ativo = %s
                     WHERE id = %s
                    """,
                    (nome, preco_num, estoque_num, ativo, id_produto),
                )
            except psycopg.Error as erro:
                flash(mensagem_banco(erro), "erro")
            else:
                flash("Produto atualizado.", "ok")
                return redirect(url_for("produtos"))
        return render_template(
            "produtos/form.html",
            titulo="Editar produto",
            id_produto=id_produto,
            nome=nome,
            preco=preco,
            estoque=estoque,
            ativo=ativo,
        )

    produto = buscar_um(
        "SELECT id, nome, preco, estoque, ativo FROM produtos WHERE id = %s",
        (id_produto,),
    )
    if produto is None:
        flash("Produto não encontrado.", "erro")
        return redirect(url_for("produtos"))
    return render_template(
        "produtos/form.html",
        titulo="Editar produto",
        id_produto=id_produto,
        nome=produto["nome"],
        preco=str(produto["preco"]).replace(".", ","),
        estoque=produto["estoque"],
        ativo=produto["ativo"],
    )


@app.route("/produtos/<int:id_produto>/excluir", methods=["POST"])
def excluir_produto(id_produto):
    try:
        executar("DELETE FROM produtos WHERE id = %s", (id_produto,))
    except psycopg.Error as erro:
        if erro.sqlstate == "23503":
            flash("Esse produto já foi vendido. Você pode desmarcar Ativo.", "erro")
        else:
            flash(mensagem_banco(erro), "erro")
    else:
        flash("Produto excluído.", "ok")
    return redirect(url_for("produtos"))


# --- Nova venda: chama a procedure ---

@app.route("/vendas/nova", methods=["GET", "POST"])
def nova_venda():
    lista_clientes = buscar_todos("SELECT id, nome FROM clientes ORDER BY nome")
    lista_produtos = buscar_todos(
        """
        SELECT id, nome, preco, estoque
        FROM produtos
        WHERE ativo = TRUE AND estoque > 0
        ORDER BY nome
        """
    )
    itens = [{"produto_id": "", "quantidade": ""} for _ in range(3)]
    id_cliente = ""
    observacao = ""

    if request.method == "POST":
        id_cliente = request.form.get("id_cliente", "")
        observacao = request.form.get("observacao", "").strip()
        itens = itens_do_formulario()
        try:
            produtos, quantidades = separar_itens(
                request.form.getlist("produto_id"),
                request.form.getlist("quantidade"),
            )
            if id_cliente == "" or not produtos:
                raise ValueError("Escolha o cliente e pelo menos um item.")
            try:
                id_num = int(id_cliente)
            except ValueError as erro:
                raise ValueError("Escolha o cliente.") from erro
            id_pedido = registrar_venda(
                id_num,
                produtos,
                quantidades,
                observacao or None,
            )
        except ValueError as erro:
            flash(str(erro), "erro")
        except psycopg.Error as erro:
            flash(mensagem_banco(erro), "erro")
        else:
            flash("Venda registrada.", "ok")
            return redirect(url_for("detalhe_pedido", id_pedido=id_pedido))

    return render_template(
        "vendas/nova.html",
        clientes=lista_clientes,
        produtos=lista_produtos,
        itens=itens,
        id_cliente=id_cliente,
        observacao=observacao,
    )


# --- Pedidos: o total vem da function ---

@app.route("/pedidos")
def pedidos():
    lista = buscar_todos(
        """
        SELECT p.id,
               p.data_pedido,
               c.nome AS cliente,
               fn_calcular_total_pedido(p.id) AS valor_total
        FROM pedidos p
        INNER JOIN clientes c ON c.id = p.cliente_id
        ORDER BY p.data_pedido DESC, p.id DESC
        """
    )
    return render_template("pedidos/lista.html", pedidos=lista)


@app.route("/pedidos/<int:id_pedido>")
def detalhe_pedido(id_pedido):
    pedido = buscar_um(
        """
        SELECT p.id,
               p.data_pedido,
               p.observacao,
               c.nome AS cliente,
               c.email,
               c.telefone,
               fn_calcular_total_pedido(p.id) AS valor_total
        FROM pedidos p
        INNER JOIN clientes c ON c.id = p.cliente_id
        WHERE p.id = %s
        """,
        (id_pedido,),
    )
    if pedido is None:
        flash("Pedido não encontrado.", "erro")
        return redirect(url_for("pedidos"))
    itens = buscar_todos(
        """
        SELECT pr.nome,
               i.quantidade,
               i.preco_unitario,
               (i.quantidade * i.preco_unitario) AS subtotal
        FROM itens_pedido i
        INNER JOIN produtos pr ON pr.id = i.produto_id
        WHERE i.pedido_id = %s
        ORDER BY i.id
        """,
        (id_pedido,),
    )
    return render_template("pedidos/detalhe.html", pedido=pedido, itens=itens)


# --- Relatório: lê a view ---

@app.route("/relatorio")
def relatorio():
    cliente = request.args.get("cliente", "").strip()
    inicio = request.args.get("inicio", "").strip()
    fim = request.args.get("fim", "").strip()

    # O WHERE é montado com pedaços fixos. O que a pessoa digitou vai em params.
    sql = "SELECT * FROM vw_relatorio_vendas WHERE 1 = 1"
    params = []
    if cliente:
        sql += " AND cliente ILIKE %s"
        params.append(f"%{cliente}%")
    if inicio:
        sql += " AND data_pedido::date >= %s"
        params.append(inicio)
    if fim:
        sql += " AND data_pedido::date <= %s"
        params.append(fim)
    sql += " ORDER BY data_pedido DESC, id_pedido DESC"

    try:
        linhas = buscar_todos(sql, params)
    except psycopg.Error:
        flash("Data inválida no filtro.", "erro")
        linhas = []

    faturamento = 0
    for linha in linhas:
        faturamento += linha["valor_total"]
    qtd = len(linhas)
    if qtd:
        ticket = faturamento / qtd
    else:
        ticket = 0

    return render_template(
        "relatorio/lista.html",
        linhas=linhas,
        qtd=qtd,
        faturamento=faturamento,
        ticket=ticket,
        cliente=cliente,
        inicio=inicio,
        fim=fim,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
