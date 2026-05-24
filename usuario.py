from datetime import datetime

class Usuario:
    """
    Representa um usuário do sistema de organização financeira.

    Um usuário possui nome, e-mail e senha - todos privados.
    O acesso a esses dados é feito exclusivamente via get e set.
    """

    # ---- Atributo de Classe ----------------------------------------
    # Definido fora do __init__, pertence à classe, não sendo uma instância especifíca.
    # Compartilhado entre todos os objetos criados.
    # __ -> Torna privado.
    # ----------------------------------------------------------------
    __total_usuarios: int = 0

    # ---- Construtor ------------------------------------------------
    # É chamado automaticamente ao fazer: u = Usuario("Ana", ...)
    # Inicialização de todos os atributos de instância.
    # ----------------------------------------------------------------

    def __init__(self, nome: str, email: str, senha: str) -> None:
        """
        Inicializa um novo usuário e incrementa o contador global.

        Args:
            nome    (str): Nome completo do usuário.
            email   (str): E-mail de login.
            senha   (str): Senha de acesso.
        """

        # Incrementa o contador de classe antes de usar seu valor como ID.
        Usuario.__total_usuarios += 1

        # ---- Atributos de instância (privados) -------------------
        # __id vira _Usuario__id internamente.
        # ----------------------------------------------------------

        self.__id: int = Usuario.__total_usuarios   # ID único
        self.__nome: str = nome                     # Nome Fornecido pelo usuário
        self.__email: str = email                   # E-mail fornecido pelo usuário
        self.__senha: str = senha                   # Senha - nunca vai ser retornada por get

        # Registra o momento exato da criação do obejto.
        self.__data_cadastro: str = datetime.now().strftime("%d/%m/%y %H:%M")

        # Informa no console que o objeto foi criado
        print(f"[+] Usuário '{self.__nome}' criado em {self.__data_cadastro}.")

    # ---- Destrutor -------------------------------------------
    # __del__ é chamdao automaticamente quando o objeto é removido
    # ----------------------------------------------------------
    def __del__(self) -> None:
        """
        Executado automaticamente quando o objeto é destruído.
        """

        print(f"[-] Usuário '{self.__nome}' removido do sistema.")

        Usuario.__total_usuarios -= 1

    # ---- Representação do Objeto ---------------------------------
    # __str__ define o que aparece quando fazemos print(objeto).
    # Retorna uma string apresentável com os dados públicos do usuário.
    # --------------------------------------------------------------
    def __str__(self) -> str:
        """
        Retorna uma descrição textual do objeto com o print.
        """

        return (
            f"Usuário (id= {self.__id}, "
            f"nome='{self.__nome}', "
            f"email='{self.__email}')"
        )
    
    # ---- Métodos GET - somente leitura ---------------------------
    # Cada get retorna uma cópia do atributo privado, sem permitir alteração direta.
    # Regra etapa 1: apenas get e set devem ser públicos.
    # --------------------------------------------------------------

    def get_id(self) -> int:
        """
        Retorna o ID único do usuário (gerado autoamticamente no construtor).
        """

        return self.__id
    
    def get_nome(self) -> str:
        """
        Retorna o nome atual do usuário.
        """

        return self.__nome
    
    def get_email(self) -> str:
        """
        Retorna o e-mail atual do usuário.
        """

        return self.__email
    
    def get_data_cadastro(self) -> str:
        """
        Retorna a data e hora de criação do objeto.
        """

        return self.__data_cadastro
    
    def verificar_senha(self, senha: str) -> bool:
        """
        Verifica se a senha fornecida confere com a armazenada.
        A senha nunca é retornada - apenas comparada internamente.

        Args:
            senha (str): senha a verificar.

        returns:
            bool: True se correta, False se errada.
        """

        return self.__senha == senha # Compara diretamente sem expor __senha.
    
    @classmethod    # Decorador: indica que o método pertence à classe, não a uma instância.
    def get_total_usuarios(cls) -> int:
        """
        Retorna o total de usuários atualmente no sistema.

        @ classmethod recebe 'cls' (a classe em si) em vez de 'self' (instância), permitindo acessar __total_usuarios sem precisar de um objeto criado.
        """

        return cls.__total_usuarios # cls aqui equivale a escrever Usuario.__total_usuarios.

    # ---- Métodos SET - escrita com validação ---------------------
    # Permitem alterar atributos privados, mas com regras de negócio.
    # __atributo nunca é alterado diretamente de fora - sempre pelo set.
    # --------------------------------------------------------------

    def set_nome(self, novo_nome: str) -> None:
        """
        Atualiza o nome do usuário após validação mínima.
 
        Args:
            novo_nome (str): Novo nome a ser definido.
        """

        # strip() remove espaços extras nas bordas antes de checar o tamanho
        if len(novo_nome.strip()) < 2:
            # Se inválido, informa e interrompe — não altera nada
            print("Erro: nome deve ter ao menos 2 caracteres.")
            return  # Sai do método sem modificar self.__nome
 
        self.__nome = novo_nome.strip()  # Atribui o nome limpo (sem espaços extras)
 
    def set_email(self, novo_email: str) -> None:
        """
        Atualiza o e-mail do usuário com validação básica de formato.
 
        Args:
            novo_email (str): Novo e-mail a ser definido.
        """
        # Valida se o texto tem ao menos um '@' e um '.' (formato mínimo de e-mail)

        if "@" not in novo_email or "." not in novo_email:
            print("Erro: e-mail inválido.")
            return  # Interrompe sem alterar o atributo
 
        # lower() converte para minúsculas — padroniza o armazenamento
        self.__email = novo_email.strip().lower()
 
    def set_senha(self, senha_atual: str, nova_senha: str) -> None:
        """
        Altera a senha do usuário, exigindo confirmação da senha atual.
 
        Segurança: não é possível trocar a senha sem saber a atual.
 
        Args:
            senha_atual (str): Senha que o usuário já possui.
            nova_senha  (str): Nova senha desejada.
        """
        
        # Reutiliza o método verificar_senha para checar a senha atual
        if not self.verificar_senha(senha_atual):
            print("Erro: senha atual incorreta.")
            return  # Bloqueia a troca sem revelar qual dado está errado
 
        # Exige tamanho mínimo para a nova senha
        if len(nova_senha) < 6:
            print("Erro: a nova senha deve ter ao menos 6 caracteres.")
            return
 
        self.__senha = nova_senha  # Somente aqui o atributo privado é de fato alterado
        print("Senha alterada com sucesso.")
 
# ---- Bloco de demonstração ---------------------------------------
# Este bloco só executa quando o arquivo é rodado diretamente.
# Se importado como módulo em outro arquivo, este trecho é ignorado.
# ------------------------------------------------------------------
 
if __name__ == "__main__":
 
    print("=" * 50)
    print("=== Criando usuários ===")
    print("=" * 50)
 
    # Construtor chamado duas vezes → dois objetos distintos na memória
    u1 = Usuario("Ana Lima", "ana@email.com", "senha123")
    u2 = Usuario("Carlos Souza", "carlos@email.com", "abc456")
 
    # Acesso ao atributo de classe sem precisar de instância
    print(f"\nTotal de usuários: {Usuario.get_total_usuarios()}")
 
    print("\n=== Acessando atributos via get ===")
    print(u1)           # Chama __str__ automaticamente
    print(f"ID: {u1.get_id()}")
    print(f"Cadastro: {u1.get_data_cadastro()}")
 
    print("\n=== Tentando acessar atributo privado diretamente ===")
    try:
        # Python transforma __nome em _Usuario__nome internamente.
        # Tentar acessar u1.__nome de fora levanta AttributeError — encapsulamento ok.
        print(u1.__nome)
    except AttributeError as e:
        print(f"Bloqueado pelo encapsulamento: {e}")
 
    print("\n=== Alterando dados via set ===")
    u1.set_nome("Ana Costa")                # Válido → altera
    u1.set_email("ana.costa@email.com")     # Válido → altera
    u1.set_nome("A")                        # Inválido → mensagem de erro, sem alteração
    u1.set_email("invalido")                # Inválido → mensagem de erro, sem alteração
 
    print(f"Nome atualizado: {u1.get_nome()}")
    print(f"Email atualizado: {u1.get_email()}")
 
    print("\n=== Verificando e alterando senha ===")
    print(f"Senha correta? {u1.verificar_senha('senha123')}")       # True
    u1.set_senha("errada", "nova999")                               # Falha — senha atual errada
    u1.set_senha("senha123", "nova999")                             # Sucesso — senha atual correta
    print(f"Nova senha confere? {u1.verificar_senha('nova999')}")   # True
 
    print("\n=== Removendo um usuário (destrutor) ===")
    del u2  # Força destruição de u2 → __del__ é chamado automaticamente
    print(f"Total após remoção: {Usuario.get_total_usuarios()}")