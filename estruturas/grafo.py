from collections import deque


class Grafo:
    """
    Grafo implementado do zero usando LISTA DE ADJACÊNCIA.

    Cada vértice guarda a lista dos vértices ligados a ele:
        {"Usuario:Camila": ["Conta:CC-1", "Conta:CP-2"], ...}

    A lista de adjacência foi escolhida no lugar da matriz porque a rede
    financeira do SOTF é esparsa — cada transação liga só uma conta a uma
    categoria. A matriz gastaria O(V²) de memória para guardar quase só zeros.

    No SOTF os vértices são as próprias entidades do sistema:
        Usuario -> Contas -> Transações -> Categorias
    """

    def __init__(self, direcionado: bool = False) -> None:
        """
        Args:
            direcionado (bool): se False, toda aresta vale nos dois sentidos.
        """
        self.__adjacencia: dict = {}
        self.__direcionado: bool = direcionado

    # ---- Construção do grafo -----------------------------------------------
    def adicionar_vertice(self, vertice) -> None:
        """Cria o vértice se ele ainda não existir (idempotente)."""
        if vertice not in self.__adjacencia:
            self.__adjacencia[vertice] = []

    def adicionar_aresta(self, origem, destino) -> None:
        """
        Liga dois vértices, criando-os se necessário.
        Em grafo não-direcionado a ligação é registrada nos dois sentidos.
        """
        if origem == destino:
            raise ValueError("Laço não faz sentido nesta rede: origem e destino iguais.")

        self.adicionar_vertice(origem)
        self.adicionar_vertice(destino)

        # O teste evita aresta duplicada quando o mesmo par é ligado 2x.
        if destino not in self.__adjacencia[origem]:
            self.__adjacencia[origem].append(destino)

        if not self.__direcionado and origem not in self.__adjacencia[destino]:
            self.__adjacencia[destino].append(origem)

    # ---- Consultas ----------------------------------------------------------
    def vizinhos(self, vertice) -> list:
        """Vértices diretamente ligados — cópia, para não expor a estrutura."""
        if vertice not in self.__adjacencia:
            raise KeyError(f"Vértice '{vertice}' não existe no grafo.")
        return self.__adjacencia[vertice].copy()

    def grau(self, vertice) -> int:
        """Quantas ligações o vértice tem."""
        return len(self.vizinhos(vertice))

    @property
    def vertices(self) -> list:
        return list(self.__adjacencia.keys())

    @property
    def direcionado(self) -> bool:
        return self.__direcionado

    @property
    def total_arestas(self) -> int:
        ligacoes = sum(len(lista) for lista in self.__adjacencia.values())
        # Em grafo não-direcionado cada aresta foi contada duas vezes.
        return ligacoes if self.__direcionado else ligacoes // 2

    # ---- Pesquisa em largura (BFS) -------------------------------------------
    def busca_em_largura(self, origem) -> dict:
        """
        PESQUISA EM LARGURA: visita o grafo em ondas, de nível em nível.

        Visita a origem (nível 0), depois todos os vizinhos dela (nível 1),
        depois os vizinhos dos vizinhos (nível 2), e assim por diante.

        A FILA (FIFO) é o que garante essa ordem: quem entra primeiro sai
        primeiro, então um vértice do nível 2 só é processado depois que
        todos os do nível 1 já saíram. Trocar a fila por uma pilha (LIFO)
        transformaria o algoritmo em busca em PROFUNDIDADE.

        O conjunto 'visitados' impede laço infinito quando o grafo tem ciclos
        — e a rede do SOTF tem: uma categoria usada por duas contas fecha um ciclo.

        Returns:
            dict: 'ordem' (visita), 'niveis' (distância em saltos) e
                  'predecessores' (de onde se chegou a cada vértice).
        """
        if origem not in self.__adjacencia:
            raise KeyError(f"Vértice '{origem}' não existe no grafo.")

        visitados = {origem}
        fila = deque([origem])          # fila FIFO
        ordem = []
        niveis = {origem: 0}
        predecessores = {origem: None}

        while fila:
            atual = fila.popleft()      # popleft = retira do início (FIFO)
            ordem.append(atual)

            for vizinho in self.__adjacencia[atual]:
                if vizinho not in visitados:
                    visitados.add(vizinho)          # marca ANTES de enfileirar,
                    niveis[vizinho] = niveis[atual] + 1   # senão entraria 2x na fila
                    predecessores[vizinho] = atual
                    fila.append(vizinho)

        return {"ordem": ordem, "niveis": niveis, "predecessores": predecessores}

    def caminho_mais_curto(self, origem, destino) -> list:
        """
        Menor caminho em número de saltos, reconstruído de trás para frente
        pelos predecessores do BFS.

        Funciona porque o BFS alcança cada vértice pela primeira vez sempre
        pelo trajeto mais curto — propriedade que a busca em profundidade não tem.
        """
        resultado = self.busca_em_largura(origem)
        predecessores = resultado["predecessores"]

        if destino not in predecessores:
            return []   # destino inalcançável a partir da origem

        caminho = []
        atual = destino
        while atual is not None:
            caminho.append(atual)
            atual = predecessores[atual]

        caminho.reverse()   # foi montado do destino para a origem
        return caminho

    def alcancaveis_em(self, origem, saltos: int) -> list:
        """Vértices exatamente a N saltos da origem (usa os níveis do BFS)."""
        niveis = self.busca_em_largura(origem)["niveis"]
        return [vertice for vertice, nivel in niveis.items() if nivel == saltos]

    def componentes_conexos(self) -> list:
        """
        Agrupa os vértices em ilhas desconexas, repetindo o BFS a partir
        de cada vértice ainda não visitado.
        """
        visitados = set()
        componentes = []

        for vertice in self.__adjacencia:
            if vertice not in visitados:
                alcancados = self.busca_em_largura(vertice)["ordem"]
                visitados.update(alcancados)
                componentes.append(alcancados)

        return componentes

    # ---- Dunders ---------------------------------------------------------------
    def __len__(self) -> int:
        return len(self.__adjacencia)

    def __contains__(self, vertice) -> bool:
        return vertice in self.__adjacencia

    def __str__(self) -> str:
        tipo = "direcionado" if self.__direcionado else "não-direcionado"
        return f"Grafo {tipo}(vértices={len(self)}, arestas={self.total_arestas})"


# ---- Bloco de demonstração ------------------------------------------------------
if __name__ == "__main__":

    print("=== Montando uma rede financeira ===")
    # Usuario -> Contas -> Transações -> Categorias
    rede = Grafo()
    rede.adicionar_aresta("Usuario:Camila", "Conta:CC-1")
    rede.adicionar_aresta("Usuario:Camila", "Conta:CP-2")

    rede.adicionar_aresta("Conta:CC-1", "Trans:#1")
    rede.adicionar_aresta("Conta:CC-1", "Trans:#2")
    rede.adicionar_aresta("Conta:CP-2", "Trans:#3")

    rede.adicionar_aresta("Trans:#1", "Cat:Alimentação")
    rede.adicionar_aresta("Trans:#2", "Cat:Moradia")
    # A mesma categoria usada pela outra conta FECHA UM CICLO na rede.
    rede.adicionar_aresta("Trans:#3", "Cat:Alimentação")

    print(rede)
    print(f"Grau de 'Usuario:Camila': {rede.grau('Usuario:Camila')}")
    print(f"Vizinhos de 'Conta:CC-1': {rede.vizinhos('Conta:CC-1')}")

    print("\n=== Pesquisa em largura a partir do usuário ===")
    resultado = rede.busca_em_largura("Usuario:Camila")

    print("Ordem de visita:")
    for posicao, vertice in enumerate(resultado["ordem"], start=1):
        print(f"  {posicao}. {vertice}")

    print("\nVértices agrupados por nível (distância em saltos):")
    niveis = resultado["niveis"]
    for nivel in range(max(niveis.values()) + 1):
        no_nivel = [v for v, n in niveis.items() if n == nivel]
        print(f"  nível {nivel}: {no_nivel}")

    print("\n=== Caminho mais curto ===")
    caminho = rede.caminho_mais_curto("Usuario:Camila", "Cat:Alimentação")
    print(" -> ".join(caminho))
    print(f"({len(caminho) - 1} saltos)")

    print("\n=== Quem está a 2 saltos do usuário ===")
    print(rede.alcancaveis_em("Usuario:Camila", 2))

    print("\n=== Componentes conexos ===")
    # Uma conta nova, ainda sem transações, forma uma ilha separada.
    rede.adicionar_vertice("Conta:CC-9 (isolada)")
    for numero, componente in enumerate(rede.componentes_conexos(), start=1):
        print(f"  componente {numero}: {len(componente)} vértice(s) -> {componente}")

    print("\n=== Destino inalcançável ===")
    print(f"Caminho até a conta isolada: {rede.caminho_mais_curto('Usuario:Camila', 'Conta:CC-9 (isolada)')}")
