from datetime import date

from categoria import Categoria
from conta import Conta, ContaCorrente, ContaPoupanca
from estruturas import Grafo, TabelaHash
from transacao import Transacao, TransacaoDespesa, TransacaoReceita
from usuario import Usuario


class SistemaFinanceiro:
    """
    Fachada que integra as camadas do SOTF.

    Existe para que nenhuma classe de domínio precise conhecer as estruturas
    de dados da Etapa 3: a `Conta` não sabe o que é uma tabela hash, a
    `Categoria` não sabe o que é um grafo. Quem junta tudo é esta classe.

    Responsabilidade única: COORDENAR. Ela não calcula saldo (é da Conta),
    não valida transação (é da Transacao) e não soma relatório (é do Relatorio).
    """

    def __init__(self, usuario: Usuario) -> None:
        self.__usuario: Usuario = usuario

        # Índice de transações por nome de categoria — busca O(1).
        self.__indice: TabelaHash = TabelaHash()

        # Raiz da hierarquia de categorias (árvore percorrida pela recursão).
        self.__raiz_categorias: Categoria = Categoria("Finanças", "#FFFFFF", "💰")

    # ---- Properties ---------------------------------------------------------
    @property
    def usuario(self) -> Usuario:
        return self.__usuario

    @property
    def indice(self) -> TabelaHash:
        return self.__indice

    @property
    def raiz_categorias(self) -> Categoria:
        return self.__raiz_categorias

    @property
    def contas(self) -> list:
        return self.__usuario.contas

    @property
    def transacoes(self) -> list:
        """Todas as transações de todas as contas, em ordem de registro."""
        return [t for conta in self.__usuario.contas for t in conta.historico]

    # ---- Operações principais -----------------------------------------------
    def abrir_conta(self, conta: Conta) -> Conta:
        """Vincula uma conta ao usuário do sistema."""
        self.__usuario.adicionar_conta(conta)
        return conta

    def registrar_transacao(self, transacao: Transacao, conta: Conta) -> None:
        """
        Ponto único por onde toda movimentação passa.

        Os três passos mostram as três etapas do projeto trabalhando juntas:
        polimorfismo (Etapa 2), histórico encapsulado (Etapa 1) e
        indexação em tabela hash (Etapa 3).
        """
        if conta not in self.__usuario.contas:
            raise ValueError("A conta não pertence ao usuário deste sistema.")

        transacao.aplicar(conta)                                    # polimorfismo
        conta.registrar(transacao)                                  # histórico
        self.__indice.inserir(transacao.categoria.nome, transacao)  # tabela hash

    def buscar_por_categoria(self, nome_categoria: str) -> list:
        """Transações de uma categoria em O(1) médio, via tabela hash."""
        return self.__indice.buscar(nome_categoria)

    def buscar_linear(self, nome_categoria: str) -> tuple:
        """
        Mesma busca, porém varrendo tudo — existe só para comparar com a hash
        na interface. Devolve (resultado, número de comparações).
        """
        encontradas = []
        comparacoes = 0
        for transacao in self.transacoes:
            comparacoes += 1
            if transacao.categoria.nome == nome_categoria:
                encontradas.append(transacao)
        return encontradas, comparacoes

    # ---- Grafo da rede financeira --------------------------------------------
    def construir_grafo(self) -> Grafo:
        """
        Monta a rede: Usuário → Contas → Transações → Categorias.

        O grafo tem ciclos de verdade: quando duas contas gastam na mesma
        categoria, ela reconecta os dois ramos. É por isso que o BFS precisa
        do controle de visitados.
        """
        grafo = Grafo()
        rotulo_usuario = f"Usuário: {self.__usuario.nome}"
        grafo.adicionar_vertice(rotulo_usuario)

        for conta in self.__usuario.contas:
            grafo.adicionar_aresta(rotulo_usuario, conta.identificador)

            for transacao in conta.historico:
                rotulo_transacao = f"{transacao.tipo.capitalize()} #{transacao.id}"
                grafo.adicionar_aresta(conta.identificador, rotulo_transacao)
                grafo.adicionar_aresta(rotulo_transacao,
                                       f"Categoria: {transacao.categoria.nome}")

        return grafo

    # ---- Hierarquia de categorias ---------------------------------------------
    def registrar_categoria(self, categoria: Categoria, pai: Categoria = None) -> Categoria:
        """Encaixa a categoria na árvore (na raiz, se nenhum pai for indicado)."""
        (pai or self.__raiz_categorias).adicionar_subcategoria(categoria)
        return categoria

    def categorias_da_arvore(self) -> list:
        """Todas as categorias da hierarquia, achatadas pela recursão."""
        return [categoria for _, categoria in self.__raiz_categorias.listar_arvore()]

    # ---- Cenário de demonstração ------------------------------------------------
    @classmethod
    def carregar_exemplo(cls) -> "SistemaFinanceiro":
        """
        Monta um cenário completo para a apresentação: usuário, duas contas,
        hierarquia de categorias e transações já aplicadas.
        """
        sistema = cls(Usuario("Camila Ferreira", "camila@email.com", "senha123"))

        corrente = sistema.abrir_conta(ContaCorrente(limite=500.0, saldo_inicial=2500.0))
        poupanca = sistema.abrir_conta(ContaPoupanca(saldo_inicial=1200.0))

        # Hierarquia: Finanças -> Moradia -> (Aluguel, Luz) etc.
        moradia = sistema.registrar_categoria(Categoria("Moradia", "#FFEAA7", "🏠"))
        alimentacao = sistema.registrar_categoria(Categoria("Alimentação", "#FF6B6B", "🍔"))
        transporte = sistema.registrar_categoria(Categoria("Transporte", "#4ECDC4", "🚗"))
        renda = sistema.registrar_categoria(Categoria("Renda", "#98FB98", "💰"))

        aluguel = sistema.registrar_categoria(Categoria("Aluguel", "#FFD700", "🔑"), moradia)
        luz = sistema.registrar_categoria(Categoria("Luz", "#FFA500", "💡"), moradia)
        mercado = sistema.registrar_categoria(Categoria("Mercado", "#FF8C69", "🛒"), alimentacao)
        restaurante = sistema.registrar_categoria(Categoria("Restaurante", "#FA8072", "🍽️"), alimentacao)

        movimentacoes = [
            (TransacaoReceita(3200.0, "Salário do mês", renda), corrente),
            (TransacaoDespesa(1200.0, "Aluguel", aluguel), corrente),
            (TransacaoDespesa(180.0, "Conta de luz", luz), corrente),
            (TransacaoDespesa(420.0, "Compras do mês", mercado), corrente),
            (TransacaoDespesa(75.0, "Almoço com colegas", restaurante), corrente),
            (TransacaoDespesa(120.0, "Combustível", transporte), corrente),
            (TransacaoReceita(600.0, "Freelance de pesquisa", renda), poupanca),
            # A poupança gasta na MESMA categoria da corrente: é este par de
            # arestas que fecha um ciclo no grafo da rede financeira.
            (TransacaoDespesa(95.0, "Feira da semana", mercado), poupanca),
            (TransacaoDespesa(60.0, "Padaria", mercado), poupanca),
            (TransacaoDespesa(45.0, "Ônibus do mês", transporte), poupanca),
        ]
        for transacao, conta in movimentacoes:
            sistema.registrar_transacao(transacao, conta)

        return sistema

    def __str__(self) -> str:
        return (f"SistemaFinanceiro(usuário='{self.__usuario.nome}', "
                f"contas={len(self.contas)}, transações={len(self.transacoes)})")


# ---- Bloco de demonstração ---------------------------------------------------
if __name__ == "__main__":

    print("=== Carregando cenário de exemplo ===")
    sistema = SistemaFinanceiro.carregar_exemplo()

    print(f"\n{sistema}")
    print(f"Patrimônio total: R$ {sistema.usuario.patrimonio_total():.2f}")

    print("\n=== Contas do usuário (polimorfismo) ===")
    for conta in sistema.contas:
        print(f"  {conta.identificador:<28} saldo R$ {conta.saldo:>8.2f} "
              f"| {len(conta.historico)} transações")

    print("\n=== Hierarquia de categorias ===")
    sistema.raiz_categorias.exibir_arvore()

    print("\n=== Busca por categoria: hash x linear ===")
    encontradas_hash = sistema.buscar_por_categoria("Mercado")
    encontradas_linear, comparacoes = sistema.buscar_linear("Mercado")
    print(f"Hash  : {len(encontradas_hash)} transações com 1 cálculo de hash")
    print(f"Linear: {len(encontradas_linear)} transações com {comparacoes} comparações")
    for transacao in encontradas_hash:
        print(f"    - {transacao.descricao}: R$ {transacao.valor:.2f}")

    print(f"\n{sistema.indice}")

    print("\n=== Grafo da rede financeira ===")
    grafo = sistema.construir_grafo()
    print(grafo)

    resultado = grafo.busca_em_largura(f"Usuário: {sistema.usuario.nome}")
    niveis = resultado["niveis"]
    print("\nBFS a partir do usuário:")
    for nivel in range(max(niveis.values()) + 1):
        no_nivel = [v for v, n in niveis.items() if n == nivel]
        print(f"  nível {nivel}: {len(no_nivel)} vértice(s)")

    caminho = grafo.caminho_mais_curto(f"Usuário: {sistema.usuario.nome}", "Categoria: Mercado")
    print(f"\nCaminho mais curto até 'Categoria: Mercado' ({len(caminho) - 1} saltos):")
    print("  " + "\n   -> ".join(caminho))
