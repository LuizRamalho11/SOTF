from abc import ABC, abstractmethod
from datetime import date

from conta import Conta
from transacao import Transacao


# ---- Interface (DIP/ISP): Relatorio depende desta abstração, não das
# implementações concretas de exportação abaixo. -----------------------------
class ExportadorInterface(ABC):
    @abstractmethod
    def exportar(self, conteudo: str) -> None:
        pass


class ExportadorPDF(ExportadorInterface):
    def exportar(self, conteudo: str) -> None:
        print(f"[PDF Engine] Documento compilado com sucesso: '{conteudo}.pdf'")


class ExportadorCSV(ExportadorInterface):
    def exportar(self, conteudo: str) -> None:
        print(f"[CSV Engine] Matriz exportada em formato de planilha: '{conteudo}.csv'")


class Relatorio:
    """Analisa um período financeiro para uma conta, apoiado em abstrações."""

    __total_gerados: int = 0

    def __init__(self, tipo: str, periodo_inicio: date, periodo_fim: date) -> None:
        hoje = date.today()
        if periodo_inicio > hoje:
            raise ValueError("A data de início do período não pode ser futura.")
        if periodo_inicio > periodo_fim:
            raise ValueError("A data de início do período não pode ser posterior à data de fim.")

        self.__tipo: str = tipo
        self.__periodo_inicio: date = periodo_inicio
        self.__periodo_fim: date = periodo_fim
        Relatorio.__total_gerados += 1

        # Guarda de segurança: só existe se o construtor terminou sem erro.
        self.__construido: bool = True

    def __del__(self) -> None:
        """Decrementa o contador, só se o objeto chegou a ser construído."""
        if hasattr(self, "_Relatorio__construido"):
            Relatorio.__total_gerados -= 1

    def __str__(self) -> str:
        return f"Relatório do tipo '{self.__tipo}' para o período de {self.__periodo_inicio} a {self.__periodo_fim}."

    # ---- Encapsulamento com properties -------------------------------------
    @property
    def tipo(self) -> str:
        return self.__tipo

    @tipo.setter
    def tipo(self, novo_tipo: str) -> None:
        if not novo_tipo.strip():
            raise ValueError("O tipo do relatório não pode ser vazio.")
        self.__tipo = novo_tipo.strip()

    @property
    def periodo_inicio(self) -> date:
        return self.__periodo_inicio

    @property
    def periodo_fim(self) -> date:
        return self.__periodo_fim

    def set_periodo(self, inicio: date, fim: date) -> None:
        """
        Não vira @property porque depende de dois valores (início e fim) —
        uma property.setter só recebe um único argumento.
        """
        hoje = date.today()
        if inicio > hoje:
            raise ValueError("A data de início do período não pode ser futura.")
        if inicio > fim:
            raise ValueError("A data de início do período não pode ser posterior à data de fim.")
        self.__periodo_inicio = inicio
        self.__periodo_fim = fim
        print(f"Período modificado para {self.__periodo_inicio} até {self.__periodo_fim}.")

    @classmethod
    def get_total_gerados(cls) -> int:
        return cls.__total_gerados

    # ---- DIP: depende da abstração Conta, nunca de ContaCorrente/ContaPoupanca
    def gerar(self, conta: Conta, transacoes: list = None) -> None:
        """
        Gera o relatório para uma conta e, opcionalmente, resume uma lista
        de Transacao — cada uma resolve seu próprio '.tipo' (polimorfismo).
        """
        print(f"\nGerando relatório do tipo '{self.tipo}' para uma conta do tipo '{conta.tipo}'...")
        print(f"Janela temporal: {self.periodo_inicio} a {self.periodo_fim}.")
        print(f"Saldo capturado em tempo real (via property): R$ {conta.saldo:.2f}")

        if transacoes:
            receitas = sum(t.valor for t in transacoes if t.tipo == "receita")
            despesas = sum(t.valor for t in transacoes if t.tipo == "despesa")
            print(f"Receitas no período: R$ {receitas:.2f}")
            print(f"Despesas no período: R$ {despesas:.2f}")

        print("Conteúdo do relatório processado com sucesso.")

    # ---- DIP: depende da interface, não de um exportador concreto -----------
    def exportar(self, exportador: ExportadorInterface) -> None:
        string_relatorio = f"Relatorio_{self.tipo}_Periodo_{self.periodo_inicio}_a_{self.periodo_fim}"
        exportador.exportar(string_relatorio)


# ---- Bloco de demonstração ---------------------------------------------------
if __name__ == "__main__":
    from conta import ContaCorrente
    from categoria import Categoria
    from transacao import TransacaoReceita, TransacaoDespesa

    print("Testando arquitetura SOLID e integração da Etapa 2...\n")

    relatorio1 = Relatorio("Auditoria Mensal", date(2025, 1, 1), date(2025, 1, 31))

    conta_teste = ContaCorrente(limite=500, saldo_inicial=2500)
    alimentacao = Categoria.criar_a_partir_do_padrao(1)
    renda = Categoria.criar_a_partir_do_padrao(7)
    transacoes = [
        TransacaoDespesa(400.0, "Aluguel", alimentacao),
        TransacaoReceita(3000.0, "Salário", renda),
    ]
    for t in transacoes:
        t.aplicar(conta_teste)

    relatorio1.gerar(conta_teste, transacoes)

    print("\nTestando inversão de dependência na exportação...")
    motor_pdf = ExportadorPDF()
    motor_csv = ExportadorCSV()

    # O mesmo relatório pode ser exportado para qualquer mecanismo
    # compatível com a interface, sem o Relatorio conhecer PDF ou CSV.
    relatorio1.exportar(motor_pdf)
    relatorio1.exportar(motor_csv)
    print(f"\nTotal de relatórios ativos no sistema: {Relatorio.get_total_gerados()}")
