from datetime import date

import matplotlib
import matplotlib.pyplot as plt
import streamlit as st

from categoria import Categoria
from conta import ContaCorrente, ContaPoupanca
from relatorio import ExportadorCSV, ExportadorInterface, ExportadorPDF, NoPeriodo, Relatorio
from sistema import SistemaFinanceiro
from transacao import TransacaoDespesa, TransacaoReceita
from usuario import Usuario

matplotlib.use("Agg")   # backend sem janela — o Streamlit só quer a imagem

st.set_page_config(page_title="SOTF — Organização de Transações Financeiras",
                   page_icon="💳", layout="wide")


# ---- Novo exportador: OCP na prática -----------------------------------------
class ExportadorTela(ExportadorInterface):
    """
    Exporta o relatório para a própria interface.

    Foi acrescentado SEM alterar uma linha de `Relatorio`: como o relatório
    depende da interface `ExportadorInterface` (e não de PDF ou CSV), basta
    implementar o contrato. É o "aberto para extensão, fechado para
    modificação" acontecendo de verdade.
    """

    def exportar(self, conteudo: str) -> None:
        st.success(f"📄 Relatório gerado na tela: **{conteudo}**")


def moeda(valor: float) -> str:
    """Formata no padrão brasileiro: R$ 1.234,56."""
    return f"R$ {valor:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")


# ---- Estado da sessão ---------------------------------------------------------
# O Streamlit re-executa este arquivo inteiro a cada clique. Sem guardar os
# objetos em session_state, todo usuário/conta/transação seria recriado do zero
# a cada interação — e os contadores de classe ficariam malucos.
if "sistema" not in st.session_state:
    st.session_state.sistema = None


def sistema_atual() -> SistemaFinanceiro:
    return st.session_state.sistema


# ---- Barra lateral -------------------------------------------------------------
with st.sidebar:
    st.title("💳 SOTF")
    st.caption("Sistema de Organização de Transações Financeiras")
    st.caption("POO — UFPB · Etapa 3")

    st.divider()

    if sistema_atual() is None:
        st.subheader("Comece por aqui")

        if st.button("🎬 Carregar dados de exemplo", use_container_width=True, type="primary"):
            st.session_state.sistema = SistemaFinanceiro.carregar_exemplo()
            st.rerun()

        st.caption("ou crie um usuário do zero:")
        with st.form("form_usuario"):
            nome = st.text_input("Nome", placeholder="Camila Ferreira")
            email = st.text_input("E-mail", placeholder="camila@email.com")
            senha = st.text_input("Senha", type="password", help="Mínimo de 6 caracteres")

            if st.form_submit_button("Criar usuário", use_container_width=True):
                try:
                    st.session_state.sistema = SistemaFinanceiro(Usuario(nome, email, senha))
                    st.rerun()
                except ValueError as erro:
                    # As validações das properties (Etapa 2) chegam até aqui.
                    st.error(str(erro))
    else:
        sistema = sistema_atual()
        st.subheader(f"👤 {sistema.usuario.nome}")
        st.caption(sistema.usuario.email)
        st.metric("Patrimônio total", moeda(sistema.usuario.patrimonio_total()))
        st.caption(f"{len(sistema.contas)} conta(s) · {len(sistema.transacoes)} transação(ões)")

        if st.button("🔄 Reiniciar sistema", use_container_width=True):
            # Limpa a sessão INTEIRA, não só o sistema: widgets com key guardam
            # objetos (categorias, contas) do sistema antigo, e eles ficariam
            # apontando para algo que não existe mais.
            st.session_state.clear()
            st.rerun()


# ---- Tela inicial ---------------------------------------------------------------
if sistema_atual() is None:
    st.title("💳 SOTF — Sistema de Organização de Transações Financeiras")
    st.info("👈 Carregue os dados de exemplo ou crie um usuário na barra lateral para começar.")

    st.subheader("O que esta interface demonstra")
    coluna_a, coluna_b, coluna_c = st.columns(3)
    with coluna_a:
        st.markdown("**⚡ Tabela hash**\n\nÍndice de transações por categoria com "
                    "busca O(1), colisões tratadas por encadeamento e "
                    "redimensionamento automático.")
    with coluna_b:
        st.markdown("**🕸️ Grafo e busca em largura**\n\nRede Usuário → Contas → "
                    "Transações → Categorias percorrida nível a nível, com "
                    "caminho mais curto.")
    with coluna_c:
        st.markdown("**🌳 Recursão**\n\nConsolidação de gastos por subárvore de "
                    "categorias e por períodos aninhados (ano → semestre → mês).")
    st.stop()


sistema = sistema_atual()

aba_contas, aba_transacoes, aba_hash, aba_grafo, aba_categorias, aba_relatorios = st.tabs([
    "👤 Contas", "💸 Transações", "⚡ Tabela Hash",
    "🕸️ Grafo & BFS", "🌳 Categorias & Recursão", "📊 Relatórios",
])


# ================================================================= ABA 1 — CONTAS
with aba_contas:
    st.header("Contas do usuário")
    st.caption("`ContaCorrente` e `ContaPoupanca` herdam de `Conta` (classe abstrata). "
               "Cada uma implementa `sacar()` à sua maneira — polimorfismo.")

    coluna_lista, coluna_form = st.columns([2, 1])

    with coluna_lista:
        if not sistema.contas:
            st.info("Nenhuma conta ainda. Abra uma ao lado.")
        for conta in sistema.contas:
            with st.container(border=True):
                topo, meio, fim = st.columns(3)
                topo.metric(conta.tipo, moeda(conta.saldo))
                meio.metric("Transações", len(conta.historico))
                # Só a conta corrente tem limite — atributo da subclasse.
                if isinstance(conta, ContaCorrente):
                    fim.metric("Limite", moeda(conta.limite))
                else:
                    fim.metric("Limite", "—")
                st.caption(f"{conta.identificador} · aberta em "
                           f"{conta.data_criacao.strftime('%d/%m/%Y')}")

    with coluna_form:
        st.subheader("Abrir conta")
        with st.form("form_conta"):
            tipo_conta = st.selectbox("Tipo", ["Conta Corrente", "Conta Poupança"])
            saldo_inicial = st.number_input("Saldo inicial", min_value=0.0, value=1000.0, step=100.0)
            limite = st.number_input("Limite (só corrente)", min_value=0.0, value=500.0, step=100.0)

            if st.form_submit_button("Abrir", use_container_width=True):
                try:
                    if tipo_conta == "Conta Corrente":
                        nova = ContaCorrente(limite=limite, saldo_inicial=saldo_inicial)
                    else:
                        nova = ContaPoupanca(saldo_inicial=saldo_inicial)
                    sistema.abrir_conta(nova)
                    st.rerun()
                except ValueError as erro:
                    st.error(str(erro))


# ============================================================= ABA 2 — TRANSAÇÕES
with aba_transacoes:
    st.header("Transações")
    st.caption("`TransacaoReceita` e `TransacaoDespesa` herdam de `Transacao`. "
               "O sistema chama sempre `aplicar(conta)` — cada subclasse decide "
               "se deposita ou saca.")

    if not sistema.contas:
        st.warning("Abra uma conta antes de lançar transações.")
    else:
        coluna_form, coluna_historico = st.columns([1, 2])

        with coluna_form:
            st.subheader("Nova transação")
            with st.form("form_transacao"):
                contas = sistema.contas
                conta_selecionada = st.selectbox(
                    "Conta", contas, format_func=lambda c: c.identificador)
                # Widgets do Streamlit devolvem uma CÓPIA do objeto selecionado
                # (proteção interna contra mutação por fora do session_state).
                # Resolvemos de volta para a instância viva pelo número — sem
                # isso, `conta_escolhida` fica desconectada da árvore do
                # usuário e `registrar_transacao` barra tudo com "a conta não
                # pertence ao usuário".
                conta_escolhida = next(c for c in contas if c.numero == conta_selecionada.numero)

                tipo_transacao = st.radio("Tipo", ["Despesa", "Receita"], horizontal=True)
                valor = st.number_input("Valor", min_value=0.01, value=100.0, step=10.0)
                descricao = st.text_input("Descrição", placeholder="Compras do mês")

                categorias = [c for c in sistema.categorias_da_arvore()
                              if c is not sistema.raiz_categorias]
                if categorias:
                    categoria_selecionada = st.selectbox(
                        "Categoria", categorias,
                        format_func=lambda c: f"{c.icone} {c.nome}")
                    categoria = next(c for c in categorias if c.id == categoria_selecionada.id)
                else:
                    categoria = None
                    st.warning("Cadastre uma categoria na aba 🌳 primeiro.")

                if st.form_submit_button("Registrar", use_container_width=True, type="primary"):
                    try:
                        if categoria is None:
                            raise ValueError("É preciso ter ao menos uma categoria.")
                        classe = TransacaoDespesa if tipo_transacao == "Despesa" else TransacaoReceita
                        # O sistema aplica, registra no histórico e indexa na hash.
                        sistema.registrar_transacao(classe(valor, descricao, categoria),
                                                    conta_escolhida)
                        st.rerun()
                    except ValueError as erro:
                        # Ex.: saque acima do saldo+limite é barrado pela regra
                        # de negócio da própria conta.
                        st.error(str(erro))

        with coluna_historico:
            st.subheader("Histórico")
            transacoes = sistema.transacoes
            if not transacoes:
                st.info("Nenhuma transação registrada.")
            else:
                st.dataframe(
                    [{
                        "ID": t.id,
                        "Tipo": t.tipo.capitalize(),
                        "Descrição": t.descricao,
                        "Categoria": f"{t.categoria.icone} {t.categoria.nome}",
                        "Valor": moeda(t.valor),
                        "Data": t.data.strftime("%d/%m/%Y %H:%M"),
                    } for t in reversed(transacoes)],
                    use_container_width=True, hide_index=True,
                )


# ============================================================= ABA 3 — TABELA HASH
with aba_hash:
    st.header("Tabela hash — índice de transações por categoria")
    st.caption("Implementada do zero em `estruturas/tabela_hash.py`, com colisões "
               "tratadas por encadeamento separado.")

    indice = sistema.indice

    metricas = st.columns(4)
    metricas[0].metric("Buckets", indice.capacidade)
    metricas[1].metric("Chaves", indice.tamanho)
    metricas[2].metric("Fator de carga", f"{indice.fator_carga:.2f}",
                       help=f"Redimensiona acima de {indice.limite_fator_carga}")
    metricas[3].metric("Colisões", indice.colisoes)

    if indice.tamanho == 0:
        st.info("Registre transações para popular o índice.")
    else:
        st.subheader("Distribuição das chaves pelos buckets")
        st.caption("Barras com mais de uma chave = colisão resolvida por encadeamento.")
        st.bar_chart({"chaves no bucket": indice.distribuicao()})

        st.subheader("Busca: hash O(1) × varredura linear O(n)")
        chave = st.selectbox("Categoria indexada", sorted(indice.chaves()))

        via_hash = sistema.buscar_por_categoria(chave)
        via_linear, comparacoes = sistema.buscar_linear(chave)

        esquerda, direita = st.columns(2)
        esquerda.metric("Busca hash", f"{len(via_hash)} encontradas",
                        f"bucket {indice.indice_de(chave)} · 1 cálculo de hash")
        direita.metric("Busca linear", f"{len(via_linear)} encontradas",
                       f"{comparacoes} comparações", delta_color="inverse")

        st.dataframe(
            [{
                "ID": t.id,
                "Descrição": t.descricao,
                "Tipo": t.tipo.capitalize(),
                "Valor": moeda(t.valor),
            } for t in via_hash],
            use_container_width=True, hide_index=True,
        )


# ============================================================== ABA 4 — GRAFO/BFS
with aba_grafo:
    st.header("Grafo da rede financeira e pesquisa em largura")
    st.caption("Vértices: usuário, contas, transações e categorias. "
               "Quando duas contas usam a mesma categoria, a rede ganha um ciclo.")

    grafo = sistema.construir_grafo()

    if len(grafo) <= 1:
        st.info("Registre transações para a rede ganhar forma.")
    else:
        info = st.columns(3)
        info[0].metric("Vértices", len(grafo))
        info[1].metric("Arestas", grafo.total_arestas)
        info[2].metric("Componentes", len(grafo.componentes_conexos()))

        vertices = grafo.vertices
        padrao = f"Usuário: {sistema.usuario.nome}"
        origem = st.selectbox("Vértice de origem do BFS", vertices,
                              index=vertices.index(padrao) if padrao in vertices else 0)

        resultado = grafo.busca_em_largura(origem)
        niveis = resultado["niveis"]

        st.subheader("Visita por níveis")
        st.caption("A fila FIFO garante que todo o nível N seja visitado antes do N+1.")
        for nivel in range(max(niveis.values()) + 1):
            do_nivel = [v for v, n in niveis.items() if n == nivel]
            with st.expander(f"Nível {nivel} — {len(do_nivel)} vértice(s)",
                             expanded=(nivel <= 1)):
                st.write(", ".join(do_nivel))

        nao_alcancados = [v for v in vertices if v not in niveis]
        if nao_alcancados:
            st.warning(f"Inalcançáveis a partir de '{origem}': {', '.join(nao_alcancados)}")

        st.subheader("Caminho mais curto")
        # A lista de opções é a mesma do seletor de origem, de propósito: se ela
        # dependesse da origem, trocar a origem deixaria aqui um destino que não
        # existe mais na lista.
        destino = st.selectbox("Vértice de destino", vertices,
                               index=len(vertices) - 1)

        caminho = grafo.caminho_mais_curto(origem, destino)
        if origem == destino:
            st.info("Origem e destino são o mesmo vértice (0 saltos).")
        elif caminho:
            st.success(" → ".join(caminho) + f"  ({len(caminho) - 1} saltos)")
        else:
            st.error("Não há caminho entre esses dois vértices.")

        # ---- Desenho do grafo -------------------------------------------------
        # O layout usa os NÍVEIS DO PRÓPRIO BFS como coordenada horizontal:
        # o algoritmo que percorre é o mesmo que organiza o desenho.
        st.subheader("Rede desenhada por níveis do BFS")

        posicoes = {}
        for nivel in range(max(niveis.values()) + 1):
            do_nivel = sorted([v for v, n in niveis.items() if n == nivel])
            for ordem, vertice in enumerate(do_nivel):
                # Centraliza verticalmente cada coluna.
                posicoes[vertice] = (nivel, ordem - (len(do_nivel) - 1) / 2)

        figura, eixo = plt.subplots(figsize=(11, max(4, len(niveis) * 0.32)))
        no_caminho = set(zip(caminho, caminho[1:])) if caminho else set()

        for vertice in posicoes:
            for vizinho in grafo.vizinhos(vertice):
                if vizinho not in posicoes:
                    continue
                destaque = (vertice, vizinho) in no_caminho or (vizinho, vertice) in no_caminho
                x1, y1 = posicoes[vertice]
                x2, y2 = posicoes[vizinho]
                eixo.plot([x1, x2], [y1, y2],
                          color="#E74C3C" if destaque else "#CCCCCC",
                          linewidth=2.2 if destaque else 0.8,
                          zorder=2 if destaque else 1)

        cores_por_nivel = ["#8E44AD", "#2980B9", "#16A085", "#E67E22", "#C0392B"]
        for vertice, (x, y) in posicoes.items():
            nivel = niveis[vertice]
            eixo.scatter([x], [y], s=190, zorder=3,
                         color=cores_por_nivel[nivel % len(cores_por_nivel)],
                         edgecolors="white", linewidths=1.5)
            eixo.annotate(vertice, (x, y), fontsize=7, xytext=(0, 9),
                          textcoords="offset points", ha="center")

        eixo.set_xticks(range(max(niveis.values()) + 1))
        eixo.set_xticklabels([f"nível {n}" for n in range(max(niveis.values()) + 1)])
        eixo.set_yticks([])
        for borda in ("top", "right", "left"):
            eixo.spines[borda].set_visible(False)
        eixo.margins(x=0.12, y=0.22)
        figura.tight_layout()
        st.pyplot(figura)
        plt.close(figura)
        st.caption("Em vermelho, o caminho mais curto selecionado acima.")


# ========================================================= ABA 5 — CATEGORIAS
with aba_categorias:
    st.header("Hierarquia de categorias e consolidação recursiva")
    st.caption("Cada categoria pode conter subcategorias. A recursão faz o total "
               "do pai ser a soma do que ele gastou mais o que as filhas devolvem.")

    coluna_arvore, coluna_nova = st.columns([2, 1])

    with coluna_nova:
        st.subheader("Nova categoria")
        with st.form("form_categoria"):
            nome_categoria = st.text_input("Nome", placeholder="Internet")
            icone_categoria = st.text_input("Ícone", value="📦")
            cor_categoria = st.color_picker("Cor", "#4ECDC4")

            possiveis_pais = sistema.categorias_da_arvore()
            pai_selecionado = st.selectbox(
                "Dentro de", possiveis_pais,
                format_func=lambda c: f"{c.icone} {c.nome}")
            # O Streamlit devolve uma CÓPIA do objeto selecionado, não a
            # instância viva da árvore — resolvemos de volta pelo id, senão
            # a categoria nova é encaixada numa cópia órfã, desconectada de
            # `sistema.raiz_categorias`, e nunca aparece na árvore exibida.
            pai_escolhido = next(c for c in possiveis_pais if c.id == pai_selecionado.id)

            if st.form_submit_button("Criar", use_container_width=True):
                try:
                    sistema.registrar_categoria(
                        Categoria(nome_categoria, cor_categoria, icone_categoria),
                        pai_escolhido)
                    st.rerun()
                except ValueError as erro:
                    st.error(str(erro))

    with coluna_arvore:
        raiz = sistema.raiz_categorias
        st.subheader("Árvore")

        resumo = st.columns(3)
        resumo[0].metric("Profundidade", raiz.profundidade())
        resumo[1].metric("Descendentes", raiz.contar_descendentes())
        resumo[2].metric("Folhas", sum(1 for _, c in raiz.listar_arvore() if c.eh_folha()))

        # listar_arvore() já devolve a árvore achatada pela recursão.
        for nivel, categoria in raiz.listar_arvore():
            st.markdown(f"{'&nbsp;' * 6 * nivel}{'└ ' if nivel else ''}"
                        f"{categoria.icone} **{categoria.nome}**",
                        unsafe_allow_html=True)

    st.divider()
    st.subheader("Consolidação recursiva por subárvore")

    hoje = date.today()
    relatorio_categorias = Relatorio("Consolidação por categoria",
                                     date(hoje.year, 1, 1), date(hoje.year, 12, 31))

    # Sem `key`: assim o Streamlit reidentifica o seletor quando a árvore muda,
    # em vez de guardar uma categoria que pode ter saído da lista.
    categorias_consolidacao = sistema.categorias_da_arvore()
    selecionada = st.selectbox(
        "Consolidar a partir de", categorias_consolidacao,
        format_func=lambda c: f"{c.icone} {c.nome}")
    # Mesma ressalva das outras seleções: o widget devolve uma cópia, não a
    # instância viva — resolvemos pelo id antes de percorrer a árvore.
    escolhida = next(c for c in categorias_consolidacao if c.id == selecionada.id)

    consolidado = relatorio_categorias.consolidar_categoria(escolhida, sistema.indice)

    totais = st.columns(2)
    totais[0].metric("Lançado direto nesta categoria", moeda(consolidado["proprio"]))
    totais[1].metric("Total com as subcategorias", moeda(consolidado["total"]))

    def linhas_consolidacao(resultado: dict, nivel: int = 0) -> list:
        """RECURSÃO: achata o resultado da consolidação em linhas de tabela."""
        linhas = [{
            "Categoria": f"{'— ' * nivel}{resultado['icone']} {resultado['nome']}",
            "Próprio": moeda(resultado["proprio"]),
            "Transações": resultado["transacoes"],
            "Total da subárvore": moeda(resultado["total"]),
        }]
        for filho in resultado["filhos"]:
            linhas.extend(linhas_consolidacao(filho, nivel + 1))
        return linhas

    st.dataframe(linhas_consolidacao(consolidado), use_container_width=True, hide_index=True)


# ========================================================== ABA 6 — RELATÓRIOS
with aba_relatorios:
    st.header("Relatórios")
    st.caption("`Relatorio` depende das abstrações `Conta` e `ExportadorInterface` — "
               "nunca das classes concretas (inversão de dependência).")

    hoje = date.today()
    periodo = st.columns(2)
    inicio = periodo[0].date_input("Início do período", date(hoje.year, 1, 1))
    fim = periodo[1].date_input("Fim do período", date(hoje.year, 12, 31))

    try:
        relatorio = Relatorio("Consolidado", inicio, fim)
    except ValueError as erro:
        st.error(str(erro))
        st.stop()

    transacoes = sistema.transacoes
    no_periodo = [t for t in transacoes if relatorio.dentro_do_periodo(t.data)]
    receitas = sum(t.valor for t in no_periodo if t.tipo == "receita")
    despesas = sum(t.valor for t in no_periodo if t.tipo == "despesa")

    indicadores = st.columns(4)
    indicadores[0].metric("Receitas", moeda(receitas))
    indicadores[1].metric("Despesas", moeda(despesas))
    indicadores[2].metric("Saldo do período", moeda(receitas - despesas))
    indicadores[3].metric("Transações", len(no_periodo))

    st.subheader("Consolidação recursiva por período aninhado")
    st.caption("O ano nunca é somado direto: ele recebe o total dos semestres, "
               "que por sua vez recebem o total dos meses.")

    ano = NoPeriodo(f"Ano {hoje.year}")
    for numero_semestre in (1, 2):
        primeiro_mes = 1 if numero_semestre == 1 else 7
        semestre = NoPeriodo(f"{numero_semestre}º semestre")
        for mes in range(primeiro_mes, primeiro_mes + 6):
            ultimo_dia = 31 if mes in (1, 3, 5, 7, 8, 10, 12) else (30 if mes != 2 else 28)
            semestre.adicionar(NoPeriodo(f"Mês {mes:02d}",
                                         date(hoje.year, mes, 1),
                                         date(hoje.year, mes, ultimo_dia)))
        ano.adicionar(semestre)

    consolidado_periodo = relatorio.consolidar_periodo(ano, transacoes)

    def linhas_periodo(resultado: dict, nivel: int = 0) -> list:
        """RECURSÃO: achata a árvore de períodos em linhas de tabela."""
        linhas = [{
            "Período": f"{'— ' * nivel}{resultado['rotulo']}",
            "Transações": resultado["transacoes"],
            "Total": moeda(resultado["total"]),
        }]
        for filho in resultado["filhos"]:
            linhas.extend(linhas_periodo(filho, nivel + 1))
        return linhas

    st.dataframe(linhas_periodo(consolidado_periodo), use_container_width=True, hide_index=True)

    st.subheader("Exportação")
    st.caption("Os três botões chamam o MESMO método `relatorio.exportar()`. "
               "Cada um injeta um exportador diferente — o relatório não sabe qual.")

    botoes = st.columns(3)
    if botoes[0].button("📄 Exportar PDF", use_container_width=True):
        relatorio.exportar(ExportadorPDF())
        st.info("Motor de PDF acionado (a saída vai para o terminal).")
    if botoes[1].button("📊 Exportar CSV", use_container_width=True):
        relatorio.exportar(ExportadorCSV())
        st.info("Motor de CSV acionado (a saída vai para o terminal).")
    if botoes[2].button("🖥️ Exportar na tela", use_container_width=True, type="primary"):
        # ExportadorTela foi criado neste arquivo, sem tocar em Relatorio.
        relatorio.exportar(ExportadorTela())
