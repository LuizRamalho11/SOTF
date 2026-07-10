from abc import ABC, abstractmethod
from datetime import datetime

from categoria import Categoria
from conta import Conta


class Transacao(ABC):
    """
    Classe base abstrata de uma transação financeira.

    Uma transação é imutável após criação (sem setters para valor, data
    ou categoria) e delega para as subclasses COMO ela afeta uma conta —
    'tipo' e 'aplicar' são o contrato que TransacaoReceita e
    TransacaoDespesa implementam de formas diferentes (polimorfismo).
    """

    __total_transacoes: int = 0

    def __init__(self, valor: float, descricao: str, categoria: Categoria) -> None:
        """
        Args:
            valor      (float)    : Valor da transação (deve ser positivo).
            descricao  (str)      : Descrição resumida da transação.
            categoria  (Categoria): Categoria associada à transação.
        """
        if valor <= 0:
            raise ValueError("Erro: o valor da transação deve ser positivo.")

        Transacao.__total_transacoes += 1
        self.__id: int = Transacao.__total_transacoes
        self._valor: float = valor
        self._descricao: str = descricao.strip()
        self._data: datetime = datetime.now()
        self._categoria: Categoria = categoria

        # Guarda de segurança: só existe se o construtor terminou sem erro.
        self.__construido: bool = True

        print(f"[+] Transação #{self.__id} ({self.tipo}) '{self._descricao}' "
              f"criada em {self._data.strftime('%d/%m/%y %H:%M')}.")

    def __del__(self) -> None:
        """Decrementa o contador, só se o objeto chegou a ser construído."""
        if hasattr(self, "_Transacao__construido"):
            Transacao.__total_transacoes -= 1

    def __str__(self) -> str:
        return (
            f"Transacao(id={self.__id}, tipo='{self.tipo}', "
            f"valor=R${self.valor:.2f}, descricao='{self.descricao}', "
            f"categoria='{self.categoria.nome}', "
            f"data='{self.data.strftime('%d/%m/%y %H:%M')}')"
        )

    # ---- Properties somente leitura (transação é imutável) ------------------
    @property
    def id(self) -> int:
        return self.__id

    @property
    def valor(self) -> float:
        return self._valor

    @property
    def descricao(self) -> str:
        return self._descricao

    @property
    def data(self) -> datetime:
        return self._data

    @property
    def categoria(self) -> Categoria:
        return self._categoria

    # ---- Contrato que cada subclasse deve cumprir (polimorfismo) -----------
    @property
    @abstractmethod
    def tipo(self) -> str:
        """Retorna o tipo da transação: 'receita' ou 'despesa'."""

    @abstractmethod
    def aplicar(self, conta: Conta) -> None:
        """Aplica o efeito desta transação sobre o saldo da conta."""

    @classmethod
    def get_total_transacoes(cls) -> int:
        """Retorna o total de transações atualmente no sistema."""
        return cls.__total_transacoes


class TransacaoReceita(Transacao):
    """Transação que aumenta o saldo de uma conta."""

    @property
    def tipo(self) -> str:
        return "receita"

    def aplicar(self, conta: Conta) -> None:
        conta.depositar(self.valor)


class TransacaoDespesa(Transacao):
    """Transação que reduz o saldo de uma conta."""

    @property
    def tipo(self) -> str:
        return "despesa"

    def aplicar(self, conta: Conta) -> None:
        conta.sacar(self.valor)


# ---- Bloco de demonstração --------------------------------------------------
if __name__ == "__main__":
    from conta import ContaCorrente

    print("=== Criando transações (polimorfismo: receita x despesa) ===")

    alimentacao = Categoria.criar_a_partir_do_padrao(1)
    renda = Categoria.criar_a_partir_do_padrao(7)

    t1 = TransacaoDespesa(150.00, "Mercado semanal", alimentacao)
    t2 = TransacaoReceita(3000.00, "Salário mensal", renda)

    print(f"\nTotal de transações: {Transacao.get_total_transacoes()}")

    print("\n=== Acessando atributos via property ===")
    print(t1)
    print(f"ID: {t1.id}")
    print(f"Valor: R${t1.valor:.2f}")
    print(f"Tipo: {t1.tipo}")
    print(f"Categoria: {t1.categoria.nome}")

    print("\n=== Tentando acessar atributo privado diretamente ===")
    try:
        print(t1.__valor)
    except AttributeError as e:
        print(f"Bloqueado pelo encapsulamento: {e}")

    print("\n=== Tentando criar transação com valor inválido (não conta no total) ===")
    try:
        TransacaoDespesa(-50.00, "Valor negativo", alimentacao)
    except ValueError as e:
        print(e)
    print(f"Total após falha de criação: {Transacao.get_total_transacoes()}")

    print("\n=== Aplicando transações a uma conta (mesma chamada, efeitos opostos) ===")
    conta = ContaCorrente(limite=0.0, saldo_inicial=500.0)
    print(f"Saldo inicial: R${conta.saldo:.2f}")
    # despesa saca, receita deposita — cada uma resolve o seu próprio 'aplicar'
    t1.aplicar(conta)
    t2.aplicar(conta)
    print(f"Saldo final: R${conta.saldo:.2f}")

    print("\n=== Removendo uma transação (destrutor) ===")
    del t2
    print(f"Total após remoção: {Transacao.get_total_transacoes()}")
