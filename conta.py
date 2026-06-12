from abc import ABC, abstractmethod
from datetime import date

class Conta(ABC): # Transforma a classe numa Interface

    # Mantém o controle de quantas contas foram criadas
    __total_contas: int = 0

    # Inicializa os atributos COMUNS da conta
    def __init__(self, saldo_inicial: float = 0.0) -> None:
        Conta.__total_contas += 1
        # Atributos protegidos para que as subclasses possam acessar
        self._saldo: float = saldo_inicial
        self._data_criacao: date = date.today()
        print("Estrutura base da conta inicializada.")

    # Destrutor
    def __del__(self) -> None:
        print("Conta encerrada.")
        Conta.__total_contas -= 1

    # Encapsulamento com PROPERTIES
    @property
    def saldo(self) -> float:
        return self._saldo
        
    @property
    def data_criacao(self) -> date:
        return self._data_criacao

    # Propriedade abstrata
    @property
    @abstractmethod
    def tipo(self) -> str:
        pass

    @classmethod
    def get_total_contas(cls) -> int:
        return cls.__total_contas

    # Regras de negócio
    def depositar(self, valor: float) -> None:
        if valor <= 0:
            print("Valor de depósito deve ser positivo.")
            return
        self._saldo += valor
        print(f"Depósito de R${valor} realizado.")

    # Método abstrato
    @abstractmethod
    def sacar(self, valor: float) -> None:
        pass

    # Representação do objeto
    def __str__(self) -> str:
        return (f"Tipo da conta: {self.tipo}\n"
                f"Saldo: R${self.saldo}\n"
                f"Data de criação: {self.data_criacao.strftime('%d/%m/%Y')}")


# Aplicação de herança
class ContaCorrente(Conta):
    def __init__(self, limite: float = 0.0, saldo_inicial: float = 0.0) -> None:
        super().__init__(saldo_inicial)
        self.__limite: float = limite
        
    @property
    def tipo(self) -> str:
        return "Conta Corrente"
        
    # Property e Setter para o limite
    @property
    def limite(self) -> float:
        return self.__limite
        
    @limite.setter
    def limite(self, novo_limite: float) -> None:
        if novo_limite < 0:
            print("Limite não pode ser negativo.")
            return
        self.__limite = novo_limite
        print(f"Limite atualizado para R${novo_limite}.")

    # POLIMORFISMO
    def sacar(self, valor: float) -> None:
        if valor <= 0:
            print("Valor de saque deve ser positivo.")
            return
        if valor > (self._saldo + self.__limite):
            print("Saldo insuficiente para este saque.")
            return
        self._saldo -= valor
        print(f"Saque de R${valor} realizado.")
        
    def __str__(self) -> str:
        return super().__str__() + f"\nLimite: R${self.limite}"


# Aplicação de herança
class ContaPoupanca(Conta):
    def __init__(self, saldo_inicial: float = 0.0) -> None:
        super().__init__(saldo_inicial)
        
    @property
    def tipo(self) -> str:
        return "Conta Poupança"
    
    # POLIMORFISMO
    def sacar(self, valor: float) -> None:
        if valor <= 0:
            print("Valor de saque deve ser positivo.")
            return
        if valor > self._saldo:
            print("Saldo insuficiente para este saque.")
            return
        self._saldo -= valor
        print(f"Saque de R${valor} realizado.")


# Bloco de demonstração ajustado
if __name__ == "__main__":
    print("Iniciando o sistema bancário...\n")

    # Polimorfismo e Herança em ação
    conta1 = ContaCorrente(limite=500.0, saldo_inicial=1000.0)
    conta2 = ContaPoupanca(saldo_inicial=2000.0)
    
    print(f"\nTotal de contas no sistema: {Conta.get_total_contas()}")
    print("\nDados da Conta 1:")
    print(conta1)
    
    print(f"\nVerificando o saldo da conta 1 via property: R${conta1.saldo}")
    
    print("\nTestando alterações de limite via Setter...")
    conta1.limite = 1000.0
    conta1.limite = -100.0
    
    print("\nTestando polimorfismo com saques...")
    print("Tentando sacar da Conta Corrente tirando do limite...")
    conta1.depositar(200.0)
    conta1.sacar(1500.0)
    
    print("\nTentando sacar da Conta Poupança com saldo insuficiente...")
    conta2.sacar(2500.0)
    
    print("\nRemovendo uma conta...")
    del conta2
    print(f"\nTotal de contas no sistema após remoção: {Conta.get_total_contas()}")

