from abc import ABC, abstractmethod
from datetime import date, datetime

from categoria import Categoria
from conta import Conta
from estruturas import TabelaHash
from transacao import Transacao


class NoPeriodo:
    """
    Nó de uma árvore de períodos: Ano → Trimestres → Meses.

    Só os nós-folha têm datas; os intermediários existem para agrupar.
    É essa estrutura aninhada que a consolidação recursiva percorre.
    """

    def __init__(self, rotulo: str, inicio: date = None, fim: date = None) -> None:
        self.__rotulo: str = rotulo
        self.__inicio: date = inicio
        self.__fim: date = fim
        self.__filhos: list = []

    def adicionar(self, filho: "NoPeriodo") -> "NoPeriodo":
        """Encaixa um subperíodo e devolve self, permitindo encadear chamadas."""
        self.__filhos.append(filho)
        return self

    @property
    def rotulo(self) -> str:
        return self.__rotulo

    @property
    def filhos(self) -> list:
        return self.__filhos.copy()

    def eh_folha(self) -> bool:
        return len(self.__filhos) == 0

    def contem(self, momento) -> bool:
        """True se a data cai dentro deste período (nós-folha)."""
        if self.__inicio is None or self.__fim is None:
            return False
        dia = momento.date() if isinstance(momento, datetime) else momento
        return self.__inicio <= dia <= self.__fim

    def __str__(self) -> str:
        return f"NoPeriodo('{self.__rotulo}', subperíodos={len(self.__filhos)})"


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

    # ---- Consolidação recursiva (Etapa 3) -----------------------------------
    def dentro_do_periodo(self, momento) -> bool:
        """True se a data está na janela deste relatório."""
        dia = momento.date() if isinstance(momento, datetime) else momento
        return self.__periodo_inicio <= dia <= self.__periodo_fim

    def consolidar_categoria(self, categoria: Categoria, indice: TabelaHash) -> dict:
        """
        RECURSÃO sobre a árvore de categorias.

        Devolve quanto foi gasto NA categoria e quanto foi gasto nela somada a
        todas as descendentes — 'Moradia' passa a valer Aluguel + Luz + Internet.

        Caso base    : uma folha não tem filhas, o laço não roda e o total é o próprio.
        Caso recursivo: cada filha resolve a própria subárvore e devolve o total dela.

        As transações vêm da TABELA HASH: buscar por nome de categoria custa
        O(1), então a recursão não precisa varrer a lista inteira em cada nó.

        SRP: quem soma dinheiro é o Relatório (análise); a Categoria só conhece
        a própria estrutura de árvore.
        """
        proprias = [t for t in indice.buscar(categoria.nome) if self.dentro_do_periodo(t.data)]
        total_proprio = sum(t.valor for t in proprias)

        filhos = [self.consolidar_categoria(sub, indice) for sub in categoria.subcategorias]

        return {
            "nome": categoria.nome,
            "icone": categoria.icone,
            "proprio": total_proprio,
            "transacoes": len(proprias),
            "total": total_proprio + sum(filho["total"] for filho in filhos),
            "filhos": filhos,
        }

    def consolidar_periodo(self, no: NoPeriodo, transacoes: list) -> dict:
        """
        RECURSÃO sobre a árvore de períodos (Ano → Trimestres → Meses).

        Caso base    : nó-folha (um mês) — soma as transações que caem nele.
        Caso recursivo: nó intermediário — soma o que as filhas devolverem.

        O ano nunca é calculado direto: ele é a soma dos trimestres, que por sua
        vez são a soma dos meses. É a recursão que faz o valor subir pela árvore.
        """
        if no.eh_folha():
            no_periodo = [t for t in transacoes if no.contem(t.data)]
            return {
                "rotulo": no.rotulo,
                "total": sum(t.valor for t in no_periodo),
                "transacoes": len(no_periodo),
                "filhos": [],
            }

        filhos = [self.consolidar_periodo(filho, transacoes) for filho in no.filhos]
        return {
            "rotulo": no.rotulo,
            "total": sum(filho["total"] for filho in filhos),
            "transacoes": sum(filho["transacoes"] for filho in filhos),
            "filhos": filhos,
        }

    @staticmethod
    def exibir_consolidacao(resultado: dict, nivel: int = 0) -> None:
        """RECURSÃO: imprime o resultado de uma consolidação de forma indentada."""
        rotulo = resultado.get("rotulo") or f"{resultado['icone']} {resultado['nome']}"
        print(f"{'    ' * nivel}{rotulo:<28} R$ {resultado['total']:>10.2f}")
        for filho in resultado["filhos"]:
            Relatorio.exibir_consolidacao(filho, nivel + 1)

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

    # Período que cobre o ano corrente — as transações da demo nascem com a
    # data de hoje, então precisam cair dentro da janela do relatório.
    hoje = date.today()
    relatorio1 = Relatorio("Auditoria Anual", date(hoje.year, 1, 1), date(hoje.year, 12, 31))

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

    # ---- Consolidação recursiva (Etapa 3) -----------------------------------
    print("\n" + "=" * 60)
    print("=== Recursão 1: consolidação por árvore de CATEGORIAS ===")

    # Hierarquia: Moradia contém Aluguel e Luz.
    moradia = Categoria("Moradia", "#FFEAA7", "🏠")
    aluguel = Categoria("Aluguel", "#FFD700", "🔑")
    luz = Categoria("Luz", "#FFA500", "💡")
    moradia.adicionar_subcategoria(aluguel)
    moradia.adicionar_subcategoria(luz)

    gastos = [
        TransacaoDespesa(1200.0, "Aluguel de julho", aluguel),
        TransacaoDespesa(180.0, "Conta de luz", luz),
        TransacaoDespesa(90.0, "Reparo na porta", moradia),
    ]

    # A tabela hash indexa por nome de categoria: busca O(1) dentro da recursão.
    indice = TabelaHash()
    for gasto in gastos:
        indice.inserir(gasto.categoria.nome, gasto)

    consolidado = relatorio1.consolidar_categoria(moradia, indice)
    print("\nTotal por subárvore (o pai soma o que as filhas devolvem):")
    Relatorio.exibir_consolidacao(consolidado)
    print(f"\nGasto lançado direto em 'Moradia' : R$ {consolidado['proprio']:.2f}")
    print(f"Gasto de 'Moradia' + descendentes : R$ {consolidado['total']:.2f}")

    print("\n=== Recursão 2: consolidação por árvore de PERÍODOS ===")

    # Ano -> Semestres -> Meses.
    ano = NoPeriodo(f"Ano {hoje.year}")
    for numero_semestre in (1, 2):
        inicio_mes = 1 if numero_semestre == 1 else 7
        semestre = NoPeriodo(f"{numero_semestre}º semestre")
        for mes in range(inicio_mes, inicio_mes + 6):
            ultimo_dia = 31 if mes in (1, 3, 5, 7, 8, 10, 12) else (30 if mes != 2 else 28)
            semestre.adicionar(NoPeriodo(f"Mês {mes:02d}",
                                         date(hoje.year, mes, 1),
                                         date(hoje.year, mes, ultimo_dia)))
        ano.adicionar(semestre)

    resultado_periodo = relatorio1.consolidar_periodo(ano, gastos)
    print("\nO ano é a soma dos semestres, que é a soma dos meses:")
    Relatorio.exibir_consolidacao(resultado_periodo)
