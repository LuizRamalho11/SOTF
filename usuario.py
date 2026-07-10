from datetime import datetime


class Usuario:
    """
    Representa um usuário do sistema de organização financeira.

    Etapa 2: nome, email e data_cadastro são expostos via @property.
    A senha nunca é exposta - apenas verificada internamente.
    """

    # ---- Atributo de Classe ------------------------------------------
    __total_usuarios: int = 0

    # ---- Construtor ----------------------------------------------------
    def __init__(self, nome: str, email: str, senha: str) -> None:
        """
        Inicializa um novo usuário e incrementa o contador global.

        Args:
            nome    (str): Nome completo do usuário.
            email   (str): E-mail de login.
            senha   (str): Senha de acesso (mínimo 6 caracteres).
        """

        # As properties abaixo já validam nome e email — se algum for
        # inválido, a exceção interrompe o construtor ANTES de qualquer
        # contador ser incrementado (evita objetos "meio-criados").
        self.nome = nome
        self.email = email

        if len(senha) < 6:
            raise ValueError("Erro: a senha deve ter ao menos 6 caracteres.")
        self.__senha: str = senha

        Usuario.__total_usuarios += 1
        self.__id: int = Usuario.__total_usuarios
        self.__data_cadastro: str = datetime.now().strftime("%d/%m/%Y %H:%M")

        # Guarda de segurança: só existe se o construtor terminou com sucesso.
        # Usada pelo __del__ para nunca decrementar um objeto que nunca chegou
        # a ser contado (ver "Erro 4" no README).
        self.__construido: bool = True

        print(f"[+] Usuário '{self.__nome}' criado em {self.__data_cadastro}.")

    # ---- Destrutor -------------------------------------------------------
    def __del__(self) -> None:
        """Decrementa o contador global, só se o objeto chegou a ser construído."""
        if hasattr(self, "_Usuario__construido"):
            Usuario.__total_usuarios -= 1

    # ---- Representação do Objeto -----------------------------------------
    def __str__(self) -> str:
        return f"Usuário(id={self.__id}, nome='{self.__nome}', email='{self.__email}')"

    # ---- Properties somente leitura ---------------------------------------
    @property
    def id(self) -> int:
        return self.__id

    @property
    def data_cadastro(self) -> str:
        return self.__data_cadastro

    # ---- Properties com validação (encapsulamento) -------------------------
    @property
    def nome(self) -> str:
        return self.__nome

    @nome.setter
    def nome(self, novo_nome: str) -> None:
        if len(novo_nome.strip()) < 2:
            raise ValueError("Erro: nome deve ter ao menos 2 caracteres.")
        self.__nome = novo_nome.strip()

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, novo_email: str) -> None:
        if "@" not in novo_email or "." not in novo_email:
            raise ValueError("Erro: e-mail inválido.")
        self.__email = novo_email.strip().lower()

    # ---- Senha: sem getter, só verificação e troca controlada --------------
    def verificar_senha(self, senha: str) -> bool:
        """Retorna True se a senha fornecida confere com a armazenada."""
        return self.__senha == senha

    def set_senha(self, senha_atual: str, nova_senha: str) -> None:
        """
        Troca a senha, exigindo confirmação da senha atual.

        Não vira @property porque depende de dois valores (atual e nova) —
        uma property.setter só recebe um único argumento.
        """
        if not self.verificar_senha(senha_atual):
            raise ValueError("Erro: senha atual incorreta.")
        if len(nova_senha) < 6:
            raise ValueError("Erro: a nova senha deve ter ao menos 6 caracteres.")
        self.__senha = nova_senha
        print("Senha alterada com sucesso.")

    @classmethod
    def get_total_usuarios(cls) -> int:
        """Retorna o total de usuários atualmente no sistema."""
        return cls.__total_usuarios


# ---- Bloco de demonstração -------------------------------------------------
if __name__ == "__main__":

    print("=== Criando usuários ===")
    u1 = Usuario("Ana Lima", "ana@email.com", "senha123")
    u2 = Usuario("Carlos Souza", "carlos@email.com", "abc456")

    print(f"\nTotal de usuários: {Usuario.get_total_usuarios()}")

    print("\n=== Acessando dados via property ===")
    print(u1)
    print(f"ID: {u1.id}")
    print(f"Cadastro: {u1.data_cadastro}")

    print("\n=== Tentando acessar atributo privado diretamente ===")
    try:
        print(u1.__nome)
    except AttributeError as e:
        print(f"Bloqueado pelo encapsulamento: {e}")

    print("\n=== Alterando dados via property ===")
    u1.nome = "Ana Costa"
    u1.email = "ana.costa@email.com"
    try:
        u1.nome = "A"
    except ValueError as e:
        print(e)
    try:
        u1.email = "invalido"
    except ValueError as e:
        print(e)

    print(f"Nome atualizado: {u1.nome}")
    print(f"Email atualizado: {u1.email}")

    print("\n=== Verificando e alterando senha ===")
    print(f"Senha correta? {u1.verificar_senha('senha123')}")
    try:
        u1.set_senha("errada", "nova999")
    except ValueError as e:
        print(e)
    u1.set_senha("senha123", "nova999")
    print(f"Nova senha confere? {u1.verificar_senha('nova999')}")

    print("\n=== Criando usuário com dado inválido (não conta no total) ===")
    try:
        Usuario("Zé", "email-invalido", "123456")
    except ValueError as e:
        print(e)
    print(f"Total após falha de criação: {Usuario.get_total_usuarios()}")

    print("\n=== Removendo um usuário (destrutor) ===")
    del u2
    print(f"Total após remoção: {Usuario.get_total_usuarios()}")
