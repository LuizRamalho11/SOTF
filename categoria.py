class Categoria:
    """
    Representa uma categoria de transação financeira.
    Exemplos: Alimentação, Transporte, Lazer, Saúde.

    Possui categorias padrão definidas na própria classe (atributo de
    classe), disponíveis para todos os objetos sem precisar criar instâncias.

    Etapa 2: nome, cor e icone são expostos via @property com validação.
    """

    # ---- Atributos de Classe ------------------------------------------
    __total_categorias: int = 0

    __categorias_padrao: list = [
        {"nome": "Alimentação",  "cor": "#FF6B6B", "icone": "🍔"},
        {"nome": "Transporte",   "cor": "#4ECDC4", "icone": "🚗"},
        {"nome": "Saúde",        "cor": "#45B7D1", "icone": "💊"},
        {"nome": "Lazer",        "cor": "#96CEB4", "icone": "🎮"},
        {"nome": "Moradia",      "cor": "#FFEAA7", "icone": "🏠"},
        {"nome": "Educação",     "cor": "#DDA0DD", "icone": "📚"},
        {"nome": "Renda",        "cor": "#98FB98", "icone": "💰"},
        {"nome": "Outros",       "cor": "#D3D3D3", "icone": "📦"},
    ]

    # ---- Construtor -----------------------------------------------------
    def __init__(self, nome: str, cor: str = "#D3D3D3", icone: str = "📦") -> None:
        """
        Inicializa uma nova categoria personalizada.

        Args:
            nome    (str): Nome da categoria.
            cor     (str): Cor no padrão hexadecimal (#RRGGBB).
            icone   (str): Emoji da categoria.
        """

        # As properties abaixo já validam — se alguma falhar, o construtor é
        # interrompido ANTES do contador de classe ser incrementado.
        self.nome = nome
        self.cor = cor
        self.icone = icone

        Categoria.__total_categorias += 1
        self.__id: int = Categoria.__total_categorias

        # Guarda de segurança: só existe se o construtor terminou com sucesso.
        # Sem ela, um __init__ que falhasse na validação ainda acionaria o
        # __del__ (o objeto já existe em memória antes do __init__ rodar) e
        # decrementaria um contador que nunca chegou a ser incrementado.
        self.__construido: bool = True

        print(f"[+] Categoria '{self.__icone} {self.__nome}' criada (id={self.__id}).")

    # ---- Destrutor --------------------------------------------------------
    def __del__(self) -> None:
        """Decrementa o contador, só se o objeto chegou a ser construído."""
        if hasattr(self, "_Categoria__construido"):
            Categoria.__total_categorias -= 1

    # ---- Representação do objeto -------------------------------------------
    def __str__(self) -> str:
        return (
            f"Categoria(id={self.__id}, "
            f"nome='{self.__nome}', "
            f"cor='{self.__cor}', "
            f"icone='{self.__icone}')"
        )

    # ---- Properties somente leitura -----------------------------------------
    @property
    def id(self) -> int:
        return self.__id

    # ---- Properties com validação (encapsulamento) ---------------------------
    @property
    def nome(self) -> str:
        return self.__nome

    @nome.setter
    def nome(self, novo_nome: str) -> None:
        if not novo_nome.strip():
            raise ValueError("Erro: o nome não pode ser vazio.")
        self.__nome = novo_nome.strip().capitalize()

    @property
    def cor(self) -> str:
        return self.__cor

    @cor.setter
    def cor(self, nova_cor: str) -> None:
        if not Categoria.__validar_cor(nova_cor):
            raise ValueError(f"Erro: cor '{nova_cor}' inválida. Use o formato hexadecimal (#RRGGBB).")
        self.__cor = nova_cor.upper()

    @property
    def icone(self) -> str:
        return self.__icone

    @icone.setter
    def icone(self, novo_icone: str) -> None:
        if not novo_icone.strip():
            raise ValueError("Erro: o ícone não pode ser vazio.")
        self.__icone = novo_icone.strip()

    # ---- Métodos de negócio -------------------------------------------------
    def exibir(self) -> None:
        """Exibe os dados da categoria de forma formatada no terminal."""
        print("\n── Categoria ──────────────────")
        print(f"  ID    : {self.__id}")
        print(f"  Nome  : {self.__icone} {self.__nome}")
        print(f"  Cor   : {self.__cor}")
        print("────────────────────────────────")

    @classmethod
    def get_total_categorias(cls) -> int:
        """Retorna o total de categorias personalizadas criadas."""
        return cls.__total_categorias

    @classmethod
    def get_categorias_padrao(cls) -> list:
        """Retorna uma cópia da lista de categorias padrão do sistema."""
        return cls.__categorias_padrao.copy()  # .copy() evita alteração da lista original

    @classmethod
    def listar_padrao(cls) -> None:
        """Exibe todas as categorias padrão do sistema, sem precisar de instância."""
        print("\n── Categorias padrão do sistema ──")
        for i, categ in enumerate(cls.__categorias_padrao, start=1):
            print(f"  {i}. {categ['icone']} {categ['nome']:<15} | {categ['cor']}")
        print()

    @classmethod
    def criar_a_partir_do_padrao(cls, indice: int) -> "Categoria":
        """
        Cria um objeto Categoria a partir de uma categoria padrão pelo índice.
        Factory method: constrói o objeto usando dados já validados da classe.

        Args:
            indice (int): Posição na lista (começa em 1).
        """
        if indice < 1 or indice > len(cls.__categorias_padrao):
            raise IndexError(f"Índice {indice} fora do intervalo. Use 1 a {len(cls.__categorias_padrao)}.")

        padrao = cls.__categorias_padrao[indice - 1]
        return cls(padrao["nome"], padrao["cor"], padrao["icone"])

    # ---- Método estático privado ----------------------------------------
    @staticmethod
    def __validar_cor(cor: str) -> bool:
        """Valida se a string segue o formato hexadecimal #RRGGBB."""
        if not cor.startswith("#"):
            return False
        if len(cor) != 7:
            return False
        return all(c in "0123456789ABCDEFabcdef" for c in cor[1:])


# ---- Bloco de demonstração --------------------------------------------------
if __name__ == "__main__":

    print("=== Categorias padrão do sistema ===")
    Categoria.listar_padrao()

    print("=== Criando categoria personalizada ===")
    c1 = Categoria("Viagens", "#FFD700", "✈️")
    c1.exibir()

    print(f"Total de categorias criadas: {Categoria.get_total_categorias()}")

    print("\n=== Criando a partir de categoria padrão ===")
    c2 = Categoria.criar_a_partir_do_padrao(1)
    c2.exibir()

    print(f"Total de categorias criadas: {Categoria.get_total_categorias()}")

    print("\n=== Acessando atributos via property ===")
    print(f"ID    : {c1.id}")
    print(f"Nome  : {c1.nome}")
    print(f"Cor   : {c1.cor}")
    print(f"Ícone : {c1.icone}")

    print("\n=== Tentando acessar atributo privado diretamente ===")
    try:
        print(c1.__nome)
    except AttributeError as e:
        print(f"Bloqueado: {e}")

    print("\n=== Alterando atributos via property ===")
    c1.nome = "viagens internacionais"
    c1.cor = "#FF4500"
    try:
        c1.cor = "vermelho"
    except ValueError as e:
        print(e)
    try:
        c1.cor = "#GGGGGG"
    except ValueError as e:
        print(e)
    c1.icone = "🌍"

    print("\n=== Estado final da categoria ===")
    print(c1)

    print("\n=== Criando categoria inválida (não conta no total) ===")
    try:
        Categoria("", "#000000")
    except ValueError as e:
        print(e)
    print(f"Total após falha de criação: {Categoria.get_total_categorias()}")

    print("\n=== Consultando lista padrão (atributo de classe) ===")
    padrao = Categoria.get_categorias_padrao()
    print(f"Total de categorias padrão: {len(padrao)}")
    print(f"Primeira categoria padrão : {padrao[0]}")
