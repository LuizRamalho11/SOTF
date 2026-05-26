class Categoria:
    """
    Representa uma categoria de transação financeira.
    Exemplos: Alimentação, Transporte, Lazer, Saúde.

    Possui categorias padrão definidas na própria classe (atributo de classe), disponíveis para todos os objetos sem precisar criar instâncias.
    """

    # ---- Atributos de Classe ----------------------------
    # Declarados fora do __init__, pertencem à classe, nâo a objetos específicos.
    # Compartilhado entre todas as instâncias de Categorias.
    # -----------------------------------------------------

    # Contador de categorias criadas. Privado, acessando via @classmethod.
    __total_categorias: int = 0

    # Lista de categorias padrão do sistema.
    # Cada item é um dicionário com nome, cor e emoji.
    # Este é um atributo de classe do tipo lista, compartilhada por todas as instâncias.
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

    # ---- Construtor ------------------------------------
    # Chamado ao instanciar: c = Categoria("Viagens", "#FFD700", "✈️")
    # ----------------------------------------------------
    def __init__(self, nome: str, cor: str = "#D3D3D3", icone: str = "📦") -> None:
        """
        Inicializa uma nova categoria personalizada.

        Args:
            nome    (str): Nome da categoria.
            cor     (str): Cor da categorial pelo padrâo hexadecimal.
            icone   (str): Emoji da categoria.
        """

        # Valida o nome antes de criar, evita categorias com nome vazio.
        if not nome.strip():
            raise ValueError("Erro: o nome da categoria não pode ser vazio.")

        # Valida o formato da cor. Conter # e 7 caracteres.
        if not Categoria.__validar_cor(cor):
            raise ValueError(f"Erro: cor '{cor}' inválida. Use o formato hexadecimal (#AAAAAA)")
        
        # incrementa o contador de classe a cada novo objeto criado.
        Categoria.__total_categorias += 1

        # ----Atributos de instância (privados) ----------
        # Cada objeto Categoria terá seus próprios valores para estes atributos.
        # ------------------------------------------------
        self.__id: int = Categoria.__total_categorias
        self.__nome: str = nome.strip().capitalize()
        self.__cor: str = cor.upper()
        self.__icone: str = icone

        print(f"[+] Categoria '{self.__icone} {self.__nome}' criada (id={self.__id}).")

        # ---- Destrutor ---------------------------------
        # Chamado automaticamente ao remover o objeto.
        # ------------------------------------------------
    def __del__(self) -> None:
        """
        Decrementa o contador ao destruir uma categoria.
        """
        Categoria.__total_categorias -= 1

    # ----Representação do objeto --------------------
    
    def __str__(self) -> str:
        return (
            f"Categoria(id={self.__id}, "
            f"nome='{self.__nome}', "
            f"cor='{self.__cor}', "
            f"icone='{self.__icone}')"
        )
    
    # ---- Métodos Get -------------------------------
    
    def get_id(self) -> int:
        """
        Retorna o ID único da categoria.
        """
        return self.__id

    def get_nome(self) -> str:
        """
        Retorna o nome da categoria.
        """
        return self.__nome

    def get_cor(self) -> str:
        """
        Retorna a cor da categoria em formato hexadecimal.
        """
        return self.__cor

    def get_icone(self) -> str:
        """
        Retorna o emoji associado à categoria.
        """
        return self.__icone

    @classmethod
    def get_total_categorias(cls) -> int:
        """
        Retorna o total de categorias personalizadas criadas.
        'cls' recebe a própria classe, não um objeto específico.
        """
        return cls.__total_categorias

    @classmethod
    def get_categorias_padrao(cls) -> list:
        """
        Retorna uma cópia da lista de categorias padrão do sistema.
        Pode ser chamado sem instância: Categoria.get_categorias_padrao()
        """
        return cls.__categorias_padrao.copy()  # .copy() evita alteração da lista original
        
    # ---- Métodos Set -----------------------------------
    
    def set_nome(self, novo_nome: str) -> None:
        """
        Atualiza o nome da categoria após validação.
 
        Args:
            novo_nome (str): Novo nome (não pode ser vazio).
        """
        if not novo_nome.strip():
            print("Erro: o nome não pode ser vazio.")
            return
 
        # capitalize() garante que a primeira letra seja maiúscula
        self.__nome = novo_nome.strip().capitalize()
        print(f"Nome atualizado para '{self.__nome}'.")
 
    def set_cor(self, nova_cor: str) -> None:
        """
        Atualiza a cor da categoria após validar o formato hexadecimal.
 
        Args:
            nova_cor (str): Nova cor no formato '#AAAAAA'.
        """
        # Chama o método privado de validação antes de aceitar
        if not Categoria.__validar_cor(nova_cor):
            print(f"Erro: '{nova_cor}' não é uma cor hex válida. Use #RRGGBB.")
            return
 
        self.__cor = nova_cor.upper()
        print(f"Cor atualizada para '{self.__cor}'.")
 
    def set_icone(self, novo_icone: str) -> None:
        """
        Atualiza o emoji da categoria.
 
        Args:
            novo_icone (str): Novo emoji.
        """
        if not novo_icone.strip():
            print("Erro: o ícone não pode ser vazio.")
            return
 
        self.__icone = novo_icone.strip()
        print(f"Ícone atualizado para '{self.__icone}'.")

    # ---- Métodos de negócio ----------------------------

    def exibir(self) -> None:
        """
        Exibe os dados da categoria de forma formatada no terminal.
        """
        print(f"\n── Categoria ──────────────────")
        print(f"  ID    : {self.__id}")
        print(f"  Nome  : {self.__icone} {self.__nome}")
        print(f"  Cor   : {self.__cor}")
        print(f"────────────────────────────────")
 
    @classmethod
    def listar_padrao(cls) -> None:
        """
        Exibe todas as categorias padrão do sistema.
        @classmethod -> acessa __categorias_padrao sem precisar de instância.
        Uso: Categoria.listar_padrao()
        """
        print("\n── Categorias padrão do sistema ──")
        for i, categ in enumerate(cls.__categorias_padrao, start=1):
            # Cada 'categ' é um dicionário, acessa chaves 'icone', 'nome', 'cor'
            print(f"  {i}. {categ['icone']} {categ['nome']:<15} | {categ['cor']}")
        print()
 
    @classmethod
    def criar_a_partir_do_padrao(cls, indice: int) -> "Categoria":
        """
        Cria um objeto Categoria a partir de uma categoria padrão pelo índice.
 
        Args:
            indice (int): Posição na lista (começa em 1).
 
        Returns:
            Categoria: Nova instância baseada nos dados padrão.
        """
        # Valida se o índice está dentro do intervalo da lista
        if indice < 1 or indice > len(cls.__categorias_padrao):
            raise IndexError(f"Índice {indice} fora do intervalo. Use 1 a {len(cls.__categorias_padrao)}.")
 
        # Acessa o dicionário da categoria padrão pelo índice (ajustado para base 0)
        padrao = cls.__categorias_padrao[indice - 1]
 
        # Cria e retorna um novo objeto Categoria com os dados padrão
        return cls(padrao["nome"], padrao["cor"], padrao["icone"])
 
    
    # ---- Método estático privado -----------------------
    # @staticmethod -> não recebe self nem cls, é um utilitário da classe.
    # Privado (__) -> só usado internamente, no construtor e no set_cor.
    # ----------------------------------------------------
    @staticmethod
    def __validar_cor(cor: str) -> bool:
        """
        Valida se a string segue o formato hexadecimal #AAAAAA.
 
        Args:
            cor (str): String a validar.
 
        Returns:
            bool: True se válida, False se não.
        """
        if not cor.startswith("#"):       # Deve começar com '#'
            return False
        if len(cor) != 7:                 # Deve ter exatamente 7 caracteres (#AAAAAA)
            return False
        # Verifica se os 6 caracteres após '#' são todos hexadecimais válidos (0-9, A-F)
        hex_valido = all(c in "0123456789ABCDEFabcdef" for c in cor[1:])
        return hex_valido

# ---- Bloco de demonstração -----------------------------

if __name__ == "__main__":
 
    print("=" * 50)
    print("=== Categorias padrão do sistema ===")
    print("=" * 50)
 
    # Acesso ao atributo de classe sem criar nenhum objeto
    Categoria.listar_padrao()
 
    print("=== Criando categoria personalizada ===")
 
    # Construtor chamado com dados personalizados
    c1 = Categoria("Viagens", "#FFD700", "✈️")
    c1.exibir()
 
    print(f"Total de categorias criadas: {Categoria.get_total_categorias()}")
 
    print("\n=== Criando a partir de categoria padrão ===")
 
    # Cria objeto diretamente a partir da lista padrão (índice 1 = Alimentação)
    c2 = Categoria.criar_a_partir_do_padrao(1)
    c2.exibir()
 
    print(f"Total de categorias criadas: {Categoria.get_total_categorias()}")
 
    print("\n=== Acessando atributos via get ===")
    print(f"ID    : {c1.get_id()}")
    print(f"Nome  : {c1.get_nome()}")
    print(f"Cor   : {c1.get_cor()}")
    print(f"Ícone : {c1.get_icone()}")
 
    print("\n=== Tentando acessar atributo privado diretamente ===")
    try:
        print(c1.__nome)
    except AttributeError as e:
        print(f"Bloqueado: {e}")
 
    print("\n=== Alterando atributos via set ===")
    c1.set_nome("viagens internacionais")  # Capitalize aplicado automaticamente
    c1.set_cor("#FF4500")                # Válido -> atualiza
    c1.set_cor("vermelho")                 # Inválido -> sem '#', nãoa aceita
    c1.set_cor("#GGGGGG")                  # Inválido -> caracteres não hex, rejeitado
    c1.set_icone("🌍")                     # Válido -> atualiza
 
    print("\n=== Estado final da categoria ===")
    print(c1)  # Chama __str__
 
    print("\n=== Consultando lista padrão (atributo de classe) ===")
    padrao = Categoria.get_categorias_padrao()
    print(f"Total de categorias padrão: {len(padrao)}")
    print(f"Primeira categoria padrão : {padrao[0]}")