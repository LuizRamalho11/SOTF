from datetime import datetime
from categoria import Categoria  # Importa a classe Categoria (relação N:1 no diagrama)


class Transacao:
    """
    Representa uma transação financeira do sistema.

    Uma transação possui valor, tipo (receita/despesa), descrição,
    data de criação e uma categoria associada — todos privados.
    O acesso é feito exclusivamente via get.
    """

    # ---- Atributo de Classe ----------------------------------------
    # Contador compartilhado entre todas as instâncias.
    # ----------------------------------------------------------------
    __total_transacoes: int = 0

    # ---- Construtor ------------------------------------------------
    def __init__(self, valor: float, tipo: str, descricao: str, categoria: Categoria) -> None:
        """
        Inicializa uma nova transação e incrementa o contador global.

        Args:
            valor      (float)    : Valor da transação (deve ser positivo).
            tipo       (str)      : Tipo da transação — 'receita' ou 'despesa'.
            descricao  (str)      : Descrição resumida da transação.
            categoria  (Categoria): Categoria associada à transação.
        """

        # Valida o valor antes de aceitar
        if valor <= 0:
            raise ValueError("Erro: o valor da transação deve ser positivo.")

        # Valida o tipo antes de aceitar
        tipo_normalizado = tipo.strip().lower()
        if tipo_normalizado not in ("receita", "despesa"):
            raise ValueError("Erro: tipo deve ser 'receita' ou 'despesa'.")

        Transacao.__total_transacoes += 1

        # ---- Atributos de instância (privados) ----------------------
        self.__id: int = Transacao.__total_transacoes   # ID único gerado automaticamente
        self.__valor: float = valor                     # Valor da transação
        self.__tipo: str = tipo_normalizado             # 'receita' ou 'despesa'
        self.__descricao: str = descricao.strip()       # Descrição da transação
        self.__data: datetime = datetime.now()          # Data/hora exata de criação
        self.__categoria: Categoria = categoria         # Categoria associada (objeto)

        print(f"[+] Transação #{self.__id} '{self.__descricao}' criada em {self.__data.strftime('%d/%m/%y %H:%M')}.")

    # ---- Destrutor --------------------------------------------------
    def __del__(self) -> None:
        """
        Executado automaticamente quando o objeto é destruído.
        """

        print(f"[-] Transação #{self.__id} '{self.__descricao}' removida do sistema.")

        Transacao.__total_transacoes -= 1

    # ---- Representação do Objeto -----------------------------------
    def __str__(self) -> str:
        """
        Retorna uma descrição textual do objeto com print().
        """

        return (
            f"Transacao(id={self.__id}, "
            f"valor=R${self.__valor:.2f}, "
            f"tipo='{self.__tipo}', "
            f"descricao='{self.__descricao}', "
            f"categoria='{self.__categoria.get_nome()}', "
            f"data='{self.__data.strftime('%d/%m/%y %H:%M')}')"
        )

    # ---- Métodos GET — somente leitura -----------------------------

    def get_id(self) -> int:
        """
        Retorna o ID único da transação.
        """

        return self.__id

    def get_valor(self) -> float:
        """
        Retorna o valor da transação.
        """

        return self.__valor

    def get_tipo(self) -> str:
        """
        Retorna o tipo da transação: 'receita' ou 'despesa'.
        """

        return self.__tipo

    def get_descricao(self) -> str:
        """
        Retorna a descrição da transação.
        """

        return self.__descricao

    def get_data(self) -> datetime:
        """
        Retorna o objeto datetime com a data/hora de criação da transação.
        """

        return self.__data

    def get_categoria(self) -> Categoria:
        """
        Retorna o objeto Categoria associado à transação.
        """

        return self.__categoria

    @classmethod
    def get_total_transacoes(cls) -> int:
        """
        Retorna o total de transações atualmente no sistema.

        @classmethod recebe 'cls' (a classe) em vez de 'self' (instância),
        permitindo acessar __total_transacoes sem precisar de um objeto criado.
        """

        return cls.__total_transacoes

    # ---- Não há SETs -----------------------------------------------
    # Transações são imutáveis por design: uma vez registrada,
    # nenhum dado deve ser alterado — para corrigir, deleta e recria.
    # ----------------------------------------------------------------


# ---- Bloco de demonstração ----------------------------------------
# Só executa quando o arquivo é rodado diretamente.
# -------------------------------------------------------------------

if __name__ == "__main__":

    # Simula uma Categoria simples para o teste (sem importar o módulo real)
    class CategoriaFake:
        def get_nome(self): return "Alimentação"

    cat = CategoriaFake()

    print("=" * 50)
    print("=== Criando transações ===")
    print("=" * 50)

    t1 = Transacao(150.00, "despesa", "Mercado semanal", cat)
    t2 = Transacao(3000.00, "receita", "Salário mensal", cat)

    print(f"\nTotal de transações: {Transacao.get_total_transacoes()}")

    print("\n=== Acessando atributos via get ===")
    print(t1)
    print(f"ID: {t1.get_id()}")
    print(f"Valor: R${t1.get_valor():.2f}")
    print(f"Tipo: {t1.get_tipo()}")
    print(f"Data: {t1.get_data().strftime('%d/%m/%Y às %H:%M')}")
    print(f"Categoria: {t1.get_categoria().get_nome()}")

    print("\n=== Tentando acessar atributo privado diretamente ===")
    try:
        print(t1.__valor)
    except AttributeError as e:
        print(f"Bloqueado pelo encapsulamento: {e}")

    print("\n=== Tentando criar transação com valor inválido ===")
    try:
        t3 = Transacao(-50.00, "despesa", "Valor negativo", cat)
    except ValueError as e:
        print(e)

    print("\n=== Tentando criar transação com tipo inválido ===")
    try:
        t4 = Transacao(100.00, "outro", "Tipo errado", cat)
    except ValueError as e:
        print(e)

    print("\n=== Removendo uma transação (destrutor) ===")
    del t2
    print(f"Total após remoção: {Transacao.get_total_transacoes()}")
