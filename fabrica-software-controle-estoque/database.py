import sqlite3
from datetime import datetime

DB_NAME = "estoque.db"


def conectar():
    return sqlite3.connect(DB_NAME)


def inicializar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            data_hora TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)

    conexao.commit()
    conexao.close()


def cadastrar_produto(nome, quantidade):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "INSERT INTO produtos (nome, quantidade) VALUES (?, ?)",
        (nome, quantidade)
    )

    conexao.commit()
    conexao.close()


def listar_produtos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT id, nome, quantidade FROM produtos ORDER BY id DESC"
    )

    produtos = cursor.fetchall()
    conexao.close()

    return produtos


def registrar_entrada(produto_id, quantidade):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE produtos
        SET quantidade = quantidade + ?
        WHERE id = ?
        """,
        (quantidade, produto_id)
    )

    cursor.execute(
        """
        INSERT INTO movimentacoes (
            produto_id,
            tipo,
            quantidade,
            data_hora
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            produto_id,
            "ENTRADA",
            quantidade,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conexao.commit()
    conexao.close()


def registrar_saida(produto_id, quantidade):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT quantidade FROM produtos WHERE id = ?",
        (produto_id,)
    )

    resultado = cursor.fetchone()

    if resultado is None:
        conexao.close()
        return False, "Produto não encontrado."

    estoque_atual = resultado[0]

    if quantidade > estoque_atual:
        conexao.close()
        return False, "Quantidade de saída maior que o estoque disponível."

    cursor.execute(
        """
        UPDATE produtos
        SET quantidade = quantidade - ?
        WHERE id = ?
        """,
        (quantidade, produto_id)
    )

    cursor.execute(
        """
        INSERT INTO movimentacoes (
            produto_id,
            tipo,
            quantidade,
            data_hora
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            produto_id,
            "SAÍDA",
            quantidade,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conexao.commit()
    conexao.close()

    return True, "Saída registrada com sucesso!"


def listar_movimentacoes():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT
            movimentacoes.id,
            produtos.nome,
            movimentacoes.tipo,
            movimentacoes.quantidade,
            movimentacoes.data_hora
        FROM movimentacoes
        INNER JOIN produtos
            ON produtos.id = movimentacoes.produto_id
        ORDER BY movimentacoes.id DESC
        """
    )

    movimentacoes = cursor.fetchall()
    conexao.close()

    return movimentacoes
