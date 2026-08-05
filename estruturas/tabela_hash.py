class TabelaHash:
    """
    Tabela hash implementada do zero, com tratamento de colisões por
    ENCADEAMENTO SEPARADO (separate chaining).

    Cada posição do vetor interno (bucket) guarda uma lista de entradas
    no formato [chave, [valores]]. Quando duas chaves diferentes caem no
    mesmo bucket (colisão), as duas convivem na mesma lista.

    No SOTF ela indexa transações por nome de categoria:
        "Alimentação" -> [Transacao#1, Transacao#4, Transacao#7]

    Sem a tabela, achar as transações de uma categoria custaria O(n) —
    varrer todas. Com ela, custa O(1) em média: calcula o hash, vai
    direto no bucket.
    """

    # Acima deste fator de carga a tabela dobra de tamanho para continuar rápida.
    __LIMITE_PADRAO: float = 0.7

    def __init__(self, capacidade: int = 8, limite_fator_carga: float = __LIMITE_PADRAO) -> None:
        """
        Args:
            capacidade         (int)  : quantidade inicial de buckets.
            limite_fator_carga (float): fator de carga que dispara o
                redimensionamento. Um valor alto praticamente desliga o
                redimensionamento — útil para observar as colisões.
        """
        if capacidade < 1:
            raise ValueError("A capacidade da tabela deve ser no mínimo 1.")
        if limite_fator_carga <= 0:
            raise ValueError("O limite do fator de carga deve ser positivo.")

        self.__capacidade: int = capacidade
        self.__limite_fator_carga: float = limite_fator_carga
        self.__buckets: list = [[] for _ in range(capacidade)]
        self.__tamanho: int = 0    # chaves distintas armazenadas
        self.__colisoes: int = 0   # vezes que uma chave nova caiu em bucket ocupado

    # ---- Função hash ------------------------------------------------------
    def __funcao_hash(self, chave) -> int:
        """
        Hash polinomial de base 31: h = (h * 31 + código do caractere) % capacidade.

        O 31 é primo e ímpar — espalha bem as chaves e evita que textos
        parecidos ("Lazer"/"Lazer ") caiam sempre no mesmo bucket, o que
        aconteceria com uma soma simples dos caracteres.
        """
        codigo = 0
        for caractere in str(chave):
            codigo = (codigo * 31 + ord(caractere)) % self.__capacidade
        return codigo

    def indice_de(self, chave) -> int:
        """Expõe em qual bucket a chave cai — usado na visualização do app."""
        return self.__funcao_hash(chave)

    # ---- Operações principais ----------------------------------------------
    def inserir(self, chave, valor) -> None:
        """
        Insere um valor sob uma chave. Chaves repetidas acumulam valores
        na mesma lista (uma categoria tem várias transações).
        """
        indice = self.__funcao_hash(chave)
        bucket = self.__buckets[indice]

        # A chave já existe neste bucket? Só acrescenta o valor.
        for entrada in bucket:
            if entrada[0] == chave:
                entrada[1].append(valor)
                return

        # Chave nova caindo em bucket já ocupado = colisão.
        if bucket:
            self.__colisoes += 1

        bucket.append([chave, [valor]])
        self.__tamanho += 1

        if self.fator_carga > self.__limite_fator_carga:
            self.__redimensionar()

    def buscar(self, chave) -> list:
        """
        Retorna a lista de valores da chave — O(1) em média.
        Devolve uma CÓPIA: alterar o resultado não corrompe a tabela.
        """
        indice = self.__funcao_hash(chave)
        for entrada in self.__buckets[indice]:
            if entrada[0] == chave:
                return entrada[1].copy()
        return []

    def remover(self, chave) -> bool:
        """Remove a chave e todos os seus valores. True se removeu."""
        bucket = self.__buckets[self.__funcao_hash(chave)]
        for posicao, entrada in enumerate(bucket):
            if entrada[0] == chave:
                bucket.pop(posicao)
                self.__tamanho -= 1
                return True
        return False

    def __redimensionar(self) -> None:
        """
        Dobra a capacidade e reinsere tudo.

        É obrigatório reinserir (e não só copiar): a função hash usa a
        capacidade no cálculo, então toda chave muda de bucket quando a
        capacidade muda.
        """
        entradas_antigas = self.__buckets

        self.__capacidade *= 2
        self.__buckets = [[] for _ in range(self.__capacidade)]
        self.__tamanho = 0
        self.__colisoes = 0   # recontadas para a nova capacidade

        for bucket in entradas_antigas:
            for chave, valores in bucket:
                for valor in valores:
                    self.inserir(chave, valor)

    # ---- Properties de inspeção ---------------------------------------------
    @property
    def capacidade(self) -> int:
        return self.__capacidade

    @property
    def tamanho(self) -> int:
        """Quantidade de chaves distintas."""
        return self.__tamanho

    @property
    def colisoes(self) -> int:
        return self.__colisoes

    @property
    def fator_carga(self) -> float:
        """Chaves ÷ buckets. Quanto maior, mais colisões tendem a aparecer."""
        return self.__tamanho / self.__capacidade

    @property
    def limite_fator_carga(self) -> float:
        """Fator de carga a partir do qual a tabela dobra de tamanho."""
        return self.__limite_fator_carga

    # ---- Consultas auxiliares (alimentam a interface Streamlit) --------------
    def chaves(self) -> list:
        return [entrada[0] for bucket in self.__buckets for entrada in bucket]

    def distribuicao(self) -> list:
        """Quantas chaves há em cada bucket — vira o gráfico de barras do app."""
        return [len(bucket) for bucket in self.__buckets]

    def total_valores(self) -> int:
        """Total de valores guardados somando todas as chaves."""
        return sum(len(entrada[1]) for bucket in self.__buckets for entrada in bucket)

    def itens(self) -> list:
        """Lista de tuplas (chave, valores) de toda a tabela."""
        return [(entrada[0], entrada[1].copy())
                for bucket in self.__buckets for entrada in bucket]

    # ---- Dunders -------------------------------------------------------------
    def __len__(self) -> int:
        return self.__tamanho

    def __contains__(self, chave) -> bool:
        indice = self.__funcao_hash(chave)
        return any(entrada[0] == chave for entrada in self.__buckets[indice])

    def __str__(self) -> str:
        return (f"TabelaHash(chaves={self.__tamanho}, capacidade={self.__capacidade}, "
                f"fator_carga={self.fator_carga:.2f}, colisões={self.__colisoes})")


# ---- Bloco de demonstração ----------------------------------------------------
if __name__ == "__main__":

    dados = [
        ("Alimentação", "Mercado"), ("Alimentação", "Restaurante"),
        ("Transporte", "Uber"),     ("Moradia", "Aluguel"),
        ("Lazer", "Cinema"),        ("Saúde", "Farmácia"),
    ]

    print("=== 1) Colisões e encadeamento separado ===")
    # Capacidade 4 para 5 categorias: pelo menos duas TÊM que dividir bucket.
    # O limite alto desliga o redimensionamento, senão a tabela cresceria
    # e desfaria justamente as colisões que queremos observar.
    tabela = TabelaHash(capacidade=4, limite_fator_carga=10.0)
    for categoria, descricao in dados:
        tabela.inserir(categoria, descricao)

    print(tabela)
    print(f"Valores guardados: {tabela.total_valores()}")

    print("\nOnde cada chave caiu:")
    for chave in tabela.chaves():
        print(f"  {chave:<14} -> bucket {tabela.indice_de(chave)}")

    print("\nDistribuição dos buckets (barras = chaves encadeadas):")
    for indice, quantidade in enumerate(tabela.distribuicao()):
        print(f"  bucket {indice}: {'█' * quantidade} ({quantidade})")

    print("\n=== 2) Busca O(1) por chave ===")
    print(f"Alimentação -> {tabela.buscar('Alimentação')}")
    print(f"Inexistente -> {tabela.buscar('Viagens')}")
    print(f"'Lazer' está na tabela? {'Lazer' in tabela}")

    print("\n=== 3) Redimensionamento automático (limite padrão de 0.7) ===")
    crescente = TabelaHash(capacidade=4)
    for categoria, descricao in dados:
        crescente.inserir(categoria, descricao)
        print(f"  após inserir {categoria:<14} "
              f"capacidade={crescente.capacidade:<3} "
              f"fator de carga={crescente.fator_carga:.2f}")
    print(f"\nA tabela cresceu sozinha de 4 para {crescente.capacidade} buckets.")
    print(f"As chaves continuam acessíveis: {crescente.buscar('Alimentação')}")

    print("\n=== Busca linear O(n) x busca hash O(1) ===")
    # Mesma pergunta respondida das duas formas, contando comparações.
    todas = [(c, d) for c, valores in tabela.itens() for d in valores]

    comparacoes = 0
    encontrados_linear = []
    for categoria, descricao in todas:          # varre TUDO
        comparacoes += 1
        if categoria == "Alimentação":
            encontrados_linear.append(descricao)

    print(f"Linear: {comparacoes} comparações -> {encontrados_linear}")
    print(f"Hash  : 1 cálculo de hash        -> {tabela.buscar('Alimentação')}")
