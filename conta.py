from datetime import date

class Conta:

# Mantém o controle de quantas contas foram criadas
    __total_contas: int = 0

# Inicializa os atributos da conta
    def __init__(self, tipo: str, limite: float = 0.0, saldo_inicial: float = 0.0) -> None:

# Incrementa o contador da classe
        Conta.__total_contas += 1

# Atributos de instância
        self.__saldo: float = saldo_inicial
        self.__limite: float = limite
        self.__tipo: str = tipo
        self.__data_criacao: date = date.today()

# Informa a criação da conta
        print(f"Conta do tipo '{self.__tipo}' criada com sucesso.")

# Destrutor
    def __del__(self) -> None:
        print(f"Conta encerrada.")
        Conta.__total_contas -= 1

# Representação do objeto
    def __str__(self) -> str:
        return (f"Tipo da conta: {self.__tipo}\n" +
                f"Saldo: R$ {self.__saldo}\n" +
                f"Limite: R$ {self.__limite}\n" +
                f"Data de criação: {self.__data_criacao.strftime('%d/%m/%Y')}")
    
# Métodos GET
    def get_saldo(self) -> float:
        return self.__saldo
    def get_limite(self) -> float:
        return self.__limite
    def get_tipo(self) -> str:
        return self.__tipo
    def get_data_criacao(self) -> date:
        return self.__data_criacao
    @classmethod
    def get_total_contas(cls) -> int:
        return cls.__total_contas
    

# Métodos SET
    def set_limite(self, novo_limite: float) -> None:
        if novo_limite < 0:
            print("Erro: O limite não pode ser negativo.")
            return
        self.__limite = novo_limite
        print(f"Limite atualizado para R$ {self.__limite}.")
    def set_tipo(self, novo_tipo: str) -> None:
        if not novo_tipo.strip():
            print("Erro: O tipo da conta não pode ser vazio.")
            return
        self.__tipo = novo_tipo.strip()

# Métodos de Regra de Negócio
    def depositar(self, valor: float) -> None:
        if valor <= 0:
            print("Erro: O valor do depósito deve ser maior que zero.")
            return
        self.__saldo += valor
        print(f"Depósito de R$ {valor} realizado. Novo saldo: R$ {self.__saldo}.")
    def sacar(self, valor: float) -> None:
        if valor <= 0:
            print("Erro: O valor do saque deve ser maior que zero.")
            return
        if valor > (self.__saldo + self.__limite):
            print("Erro: Saldo e limite insuficiente para realizar o saque.")
            return
        self.__saldo -= valor
        print(f"Saque de R$ {valor} realizado. Novo saldo: R$ {self.__saldo}.")
    def transferir(self, valor: float, conta_destino: 'Conta') -> None:
        if valor <= 0:
            print("Erro: O valor da transferência deve ser maior que zero.")
            return
        if valor > (self.__saldo + self.__limite):
            print("Erro: Saldo e limite insuficiente para realizar a transferência.")
            return
        self.__saldo -= valor
        conta_destino.depositar(valor)
        print(f"Transferência de R$ {valor} realizada para a conta do tipo '{conta_destino.get_tipo()}.' Novo saldo: R$ {self.__saldo}.")

# Blocos de demonstração
if __name__ == "__main__":
    print("Iniciando o sistema de contas...\n")
    conta1 = Conta("Corrente", limite=400, saldo_inicial=40)
    conta2 = Conta("Poupança", limite=0, saldo_inicial=10000)
print(f"\nTotal de contas no sistema: {Conta.get_total_contas()}")
print("\nDados da conta 1:")
print(conta1)
print("\nVerificando o saldo da conta 1... R$")
print(f"O saldo da conta 1 é: R$ {conta1.get_saldo()}")
print("\nTestando Encapsulamento Direto...")
try:
    print(conta1.__saldo)
except AttributeError as e:
    print(f"Bloqueado com sucesso pelo encapsulamento: {e}")
print("\nTestando alterações de limite...")
conta1.set_limite(-500)
conta1.set_limite(500)
print("\nTestando operações...")
conta1.depositar(200)
conta1.sacar(500)
conta1.sacar(1000)
conta1.transferir(300, conta2)
print("\nDados da conta 1 após operações:")
print(conta1)
print(f"\nDados da conta 2 após receber transferência:")
print(conta2)
print("\nRemovendo uma conta...")
del conta2
print(f"Total de contas no sistema após remoção: {Conta.get_total_contas()}")
