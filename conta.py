from abc import ABC, abstractmethod
from datetime import date
from typing import TYPE_CHECKING

# Importado só para a checagem de tipos. Em tempo de execução este bloco não
# roda, o que evita import circular: transacao.py já importa conta.py.
if TYPE_CHECKING:
    from transacao import Transacao


class Conta(ABC):
    """
    Classe base abstrata (interface parcial) para contas financeiras.

    Define o que toda conta TEM (saldo, data de criação) e o que toda
    conta FAZ (depositar), deixando 'tipo' e 'sacar' como contrato
    obrigatório para as subclasses — cada tipo de conta saca de um jeito.
    """

    # Contas VIVAS: sobe no construtor, desce no destrutor.
    __total_contas: int = 0

    # Gerador de números de conta: só sobe, nunca desce. É o que identifica
    # a conta como vértice do grafo, então precisa ser único de verdade.
    __ultimo_numero: int = 0

    def __init__(self, saldo_inicial: float = 0.0, data_criacao: date = None) -> None:
        if saldo_inicial < 0:
            raise ValueError("O saldo inicial não pode ser negativo.")

        Conta.__total_contas += 1
        Conta.__ultimo_numero += 1

        # Atributos protegidos (_) para que as subclasses possam acessá-los.
        self._numero: int = Conta.__ultimo_numero
        self._saldo: float = saldo_inicial
        # `data_criacao` só é passada por `banco.carregar_estado()`, para a
        # conta recarregada do banco manter a data original em vez de "hoje".
        self._data_criacao: date = data_criacao or date.today()

        # Histórico de transações (Etapa 3): sem ele não há o que indexar
        # na tabela hash nem o que percorrer no grafo.
        self._historico: list = []

        # Guarda de segurança: só existe se o construtor terminou sem erro.
        self.__construido: bool = True

    def __del__(self) -> None:
        """Decrementa o contador, só se o objeto chegou a ser construído."""
        if hasattr(self, "_Conta__construido"):
            Conta.__total_contas -= 1

    # ---- Encapsulamento com properties -----------------------------------
    @property
    def numero(self) -> int:
        return self._numero

    @property
    def saldo(self) -> float:
        return self._saldo

    @property
    def data_criacao(self) -> date:
        return self._data_criacao

    @property
    def historico(self) -> list:
        """
        Transações já registradas — CÓPIA, para que ninguém insira ou apague
        movimentações por fora das regras de negócio (lição da Etapa 1).
        """
        return self._historico.copy()

    @property
    def identificador(self) -> str:
        """Rótulo curto usado como vértice do grafo. Ex.: 'Conta:#1 Corrente'."""
        return f"Conta:#{self._numero} {self.tipo.replace('Conta ', '')}"

    def registrar(self, transacao: "Transacao") -> None:
        """Guarda a transação no histórico desta conta."""
        self._historico.append(transacao)

    @property
    @abstractmethod
    def tipo(self) -> str:
        """Identifica o tipo concreto da conta — cada subclasse define o seu."""

    @classmethod
    def get_total_contas(cls) -> int:
        return cls.__total_contas

    # ---- Regra de negócio comum ------------------------------------------
    def depositar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("Valor de depósito deve ser positivo.")
        self._saldo += valor
        print(f"Depósito de R${valor:.2f} realizado.")

    # ---- Contrato que cada subclasse deve cumprir (polimorfismo) -----------
    @abstractmethod
    def sacar(self, valor: float) -> None:
        """Regra de saque específica de cada tipo de conta."""

    def __str__(self) -> str:
        return (f"Tipo da conta: {self.tipo} (nº {self._numero})\n"
                f"Saldo: R${self.saldo:.2f}\n"
                f"Transações registradas: {len(self._historico)}\n"
                f"Data de criação: {self.data_criacao.strftime('%d/%m/%Y')}")


class ContaCorrente(Conta):
    """Conta com limite de cheque especial além do saldo."""

    def __init__(self, limite: float = 0.0, saldo_inicial: float = 0.0,
                 data_criacao: date = None) -> None:
        super().__init__(saldo_inicial, data_criacao)
        # Passa pela property abaixo — garante a mesma validação usada
        # em qualquer alteração posterior do limite.
        self.limite = limite

    @property
    def tipo(self) -> str:
        return "Conta Corrente"

    @property
    def limite(self) -> float:
        return self.__limite

    @limite.setter
    def limite(self, novo_limite: float) -> None:
        if novo_limite < 0:
            raise ValueError("Limite não pode ser negativo.")
        self.__limite = novo_limite

    # ---- Polimorfismo: saque considera saldo + limite ----------------------
    def sacar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("Valor de saque deve ser positivo.")
        if valor > (self._saldo + self.__limite):
            raise ValueError("Saldo e limite insuficientes para este saque.")
        self._saldo -= valor
        print(f"Saque de R${valor:.2f} realizado.")

    def __str__(self) -> str:
        return super().__str__() + f"\nLimite: R${self.limite:.2f}"


class ContaPoupanca(Conta):
    """Conta sem limite de crédito — só pode sacar o que tem de saldo."""

    def __init__(self, saldo_inicial: float = 0.0, data_criacao: date = None) -> None:
        super().__init__(saldo_inicial, data_criacao)

    @property
    def tipo(self) -> str:
        return "Conta Poupança"

    # ---- Polimorfismo: saque considera apenas o saldo -----------------------
    def sacar(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("Valor de saque deve ser positivo.")
        if valor > self._saldo:
            raise ValueError("Saldo insuficiente para este saque.")
        self._saldo -= valor
        print(f"Saque de R${valor:.2f} realizado.")


# ---- Bloco de demonstração ----------------------------------------------
if __name__ == "__main__":
    print("Iniciando o sistema bancário...\n")

    conta1 = ContaCorrente(limite=500.0, saldo_inicial=1000.0)
    conta2 = ContaPoupanca(saldo_inicial=2000.0)

    print(f"\nTotal de contas no sistema: {Conta.get_total_contas()}")
    print("\nDados da Conta 1:")
    print(conta1)

    print(f"\nVerificando o saldo da conta 1 via property: R${conta1.saldo:.2f}")

    print("\nTestando alterações de limite via setter...")
    conta1.limite = 1000.0
    try:
        conta1.limite = -100.0
    except ValueError as e:
        print(e)

    print("\nTestando polimorfismo com saques...")
    print("Tentando sacar da Conta Corrente usando o limite...")
    conta1.depositar(200.0)
    conta1.sacar(1500.0)

    print("\nTentando sacar da Conta Poupança com saldo insuficiente...")
    try:
        conta2.sacar(2500.0)
    except ValueError as e:
        print(e)

    print("\nRemovendo uma conta...")
    del conta2
    print(f"\nTotal de contas no sistema após remoção: {Conta.get_total_contas()}")
