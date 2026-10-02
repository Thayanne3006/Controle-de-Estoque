import streamlit as st
import pandas as pd
import plotly.express as px
from database import (
    inicializar_banco,
    cadastrar_produto,
    listar_produtos,
    registrar_entrada,
    registrar_saida,
    listar_movimentacoes
)

st.set_page_config(
    page_title="Controle de Estoque",
    page_icon="📦",
    layout="wide"
)

inicializar_banco()

st.title("📦 Sistema de Controle de Estoque")
st.write("MVP desenvolvido para o projeto Fábrica de Software.")

(
    aba_cadastro,
    aba_entrada,
    aba_saida,
    aba_consulta,
    aba_historico,
    aba_dashboard
) = st.tabs([
    "Cadastro de Produtos",
    "Entrada de Estoque",
    "Saída de Estoque",
    "Consulta de Estoque",
    "Histórico",
    "Dashboard"
])

with aba_cadastro:
    st.subheader("Cadastro de Produtos")

    with st.form("form_cadastro_produto"):
        nome = st.text_input("Nome do produto")
        quantidade = st.number_input(
            "Quantidade inicial",
            min_value=0,
            step=1
        )

        cadastrar = st.form_submit_button("Cadastrar produto")

        if cadastrar:
            if not nome.strip():
                st.error("Informe o nome do produto.")
            else:
                cadastrar_produto(nome.strip(), int(quantidade))
                st.success("Produto cadastrado com sucesso!")
                st.rerun()

    st.divider()
    st.subheader("Produtos cadastrados")

    produtos = listar_produtos()

    if produtos:
        df = pd.DataFrame(
            produtos,
            columns=["ID", "Produto", "Quantidade"]
        )
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhum produto cadastrado.")

with aba_entrada:
    st.subheader("Entrada de Estoque")

    produtos = listar_produtos()

    if not produtos:
        st.info("Cadastre pelo menos um produto antes de registrar uma entrada.")
    else:
        opcoes = {
            f"{produto[1]} — estoque atual: {produto[2]}": produto[0]
            for produto in produtos
        }

        with st.form("form_entrada_estoque"):
            produto_escolhido = st.selectbox(
                "Produto",
                options=list(opcoes.keys()),
                key="produto_entrada"
            )

            quantidade_entrada = st.number_input(
                "Quantidade de entrada",
                min_value=1,
                step=1
            )

            confirmar_entrada = st.form_submit_button("Registrar entrada")

            if confirmar_entrada:
                produto_id = opcoes[produto_escolhido]
                registrar_entrada(
                    produto_id,
                    int(quantidade_entrada)
                )
                st.success("Entrada registrada com sucesso!")
                st.rerun()

        st.divider()
        st.subheader("Saldo atual")

        produtos_atualizados = listar_produtos()

        df_saldo = pd.DataFrame(
            produtos_atualizados,
            columns=["ID", "Produto", "Quantidade"]
        )

        st.dataframe(
            df_saldo,
            use_container_width=True,
            hide_index=True
        )

with aba_saida:
    st.subheader("Saída de Estoque")

    produtos = listar_produtos()

    if not produtos:
        st.info("Cadastre pelo menos um produto antes de registrar uma saída.")
    else:
        opcoes_saida = {
            f"{produto[1]} — estoque atual: {produto[2]}": produto[0]
            for produto in produtos
        }

        with st.form("form_saida_estoque"):
            produto_escolhido_saida = st.selectbox(
                "Produto",
                options=list(opcoes_saida.keys()),
                key="produto_saida"
            )

            quantidade_saida = st.number_input(
                "Quantidade de saída",
                min_value=1,
                step=1
            )

            confirmar_saida = st.form_submit_button(
                "Registrar saída"
            )

            if confirmar_saida:
                produto_id = opcoes_saida[
                    produto_escolhido_saida
                ]

                sucesso, mensagem = registrar_saida(
                    produto_id,
                    int(quantidade_saida)
                )

                if sucesso:
                    st.success(mensagem)
                    st.rerun()
                else:
                    st.error(mensagem)

        st.divider()
        st.subheader("Saldo atual")

        produtos_atualizados = listar_produtos()

        df_saldo_saida = pd.DataFrame(
            produtos_atualizados,
            columns=["ID", "Produto", "Quantidade"]
        )

        st.dataframe(
            df_saldo_saida,
            use_container_width=True,
            hide_index=True
        )

with aba_consulta:
    st.subheader("Consulta do Saldo Disponível")

    produtos = listar_produtos()

    if produtos:
        df_consulta = pd.DataFrame(
            produtos,
            columns=[
                "ID",
                "Produto",
                "Quantidade disponível"
            ]
        )

        st.dataframe(
            df_consulta,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhum produto cadastrado.")

with aba_historico:
    st.subheader("Histórico de Movimentações")

    movimentacoes = listar_movimentacoes()

    if movimentacoes:
        df_historico = pd.DataFrame(
            movimentacoes,
            columns=[
                "ID",
                "Produto",
                "Tipo",
                "Quantidade",
                "Data/Hora"
            ]
        )

        st.dataframe(
            df_historico,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Nenhuma movimentação registrada.")

with aba_dashboard:
    st.subheader("Indicadores de Estoque")

    produtos = listar_produtos()
    movimentacoes = listar_movimentacoes()

    if produtos:
        df_produtos = pd.DataFrame(
            produtos,
            columns=["ID", "Produto", "Quantidade"]
        )

        total_produtos = len(df_produtos)
        total_unidades = int(df_produtos["Quantidade"].sum())

        total_entradas = 0
        total_saidas = 0

        if movimentacoes:
            df_mov = pd.DataFrame(
                movimentacoes,
                columns=[
                    "ID",
                    "Produto",
                    "Tipo",
                    "Quantidade",
                    "Data/Hora"
                ]
            )

            total_entradas = int(
                df_mov.loc[
                    df_mov["Tipo"] == "ENTRADA",
                    "Quantidade"
                ].sum()
            )

            total_saidas = int(
                df_mov.loc[
                    df_mov["Tipo"] == "SAÍDA",
                    "Quantidade"
                ].sum()
            )

        espaco_esq, col1, col2, col3, col4, espaco_dir = st.columns(
            [1.5, 1, 1, 1, 1, 1.5]
        )

        col1.metric(
            "Produtos cadastrados",
            total_produtos
        )
        col2.metric(
            "Unidades em estoque",
            total_unidades
        )
        col3.metric(
            "Total de entradas",
            total_entradas
        )
        col4.metric(
            "Total de saídas",
            total_saidas
        )

        st.divider()

        st.subheader("Quantidade atual por produto")

        grafico_estoque = px.bar(
            df_produtos,
            x="Produto",
            y="Quantidade",
            labels={
                "Produto": "Produto",
                "Quantidade": "Quantidade disponível"
            }
        )

        grafico_estoque.update_layout(
            bargap=0.90
        )

        st.plotly_chart(
            grafico_estoque,
            use_container_width=True
        )

        if movimentacoes:
            st.subheader("Movimentações por tipo")

            resumo_movimentacoes = (
                df_mov
                .groupby("Tipo", as_index=False)["Quantidade"]
                .sum()
            )

            grafico_movimentacoes = px.bar(
                resumo_movimentacoes,
                x="Tipo",
                y="Quantidade",
                labels={
                    "Tipo": "Tipo de movimentação",
                    "Quantidade": "Quantidade movimentada"
                }
            )

            grafico_movimentacoes.update_layout(
                bargap=0.90
            )

            st.plotly_chart(
                grafico_movimentacoes,
                use_container_width=True
            )
    else:
        st.info(
            "Cadastre produtos para visualizar os indicadores."
        )
