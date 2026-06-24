from abc import ABC, abstractmethod
from datetime import date
from conta import Conta

# Criaçãp de Interface Abstrata para desacoplar a Exportação
class ExportadorInterface(ABC):
    @abstractmethod
    def exportar(self, conteudo: str) -> None:
        pass

# Classes concretas extensíveis que herdam da Interface de Exportação
class ExportadorPDF(ExportadorInterface):
    def exportar(self, conteudo: str) -> None:
        print(f"[PDF Engine] Documento compilado com sucesso: '{conteudo}.pdf'")
class ExportadorCSV(ExportadorInterface):
    def exportar(self, conteudo: str) -> None:
        print(f"[CSV Engine] Matriz exportada em formato de planilha: '{conteudo}.csv'")
class Relatorio:

    # Atributo de classe
    __total_gerados: int = 0

    # Construtor
    def __init__(self, tipo: str, periodo_inicio: date, periodo_fim: date) -> None:
        hoje = date.today()

        # Validações estruturais mantidas por segurança
        if periodo_inicio > hoje:
            raise ValueError("A data de início do período não pode ser futura.")
        if periodo_inicio > periodo_fim:
            raise ValueError("A data de início do período não pode ser posterior à data de fim.")
        
        # Atributos privados
        self.__tipo: str = tipo
        self.__periodo_inicio: date = periodo_inicio
        self.__periodo_fim: date = periodo_fim
        Relatorio.__total_gerados += 1

        # Guarda de segurança
        self.__construido: bool = True
        print("Relatório criado com sucesso.")

    # Destrutor
    def __del__(self) -> None:
        if hasattr(self, '_Relatorio__construido'):
            print("Relatório removido.")
            Relatorio.__total_gerados -= 1
        else:
            print("Tentativa inválida de relatório descartada sem alterar o contador.")
    def __str__(self) -> str:
        return f"Relatório do tipo '{self.__tipo}' para o período de {self.__periodo_inicio} a {self.__periodo_fim}."
    
    # Encapsulamento com PROPERTIES
    @property
    def tipo(self) -> str:
        return self.__tipo
    @tipo.setter
    def tipo(self, novo_tipo: str) -> None:
        if not novo_tipo.strip():
            print("Erro. O tipo do relatório não pode ser vazio.")
            return
        self.__tipo = novo_tipo.strip()
    @property
    def periodo_inicio(self) -> date:
        return self.__periodo_inicio
    @property
    def periodo_fim(self) -> date: 
        return self.__periodo_fim
    
    # Setter estruturado em método para validação de consistência lógica temporal
    def set_periodo(self, inicio: date, fim: date) -> None:
        hoje = date.today()
        if inicio > hoje:
            print("Erro. A data de início do período não pode ser futura.")
            return
        if inicio > fim:
            print("Erro. A data de início do período não pode ser posterior à data de fim.")
            return
        self.__periodo_inicio = inicio
        self.__periodo_fim = fim
        print(f"Período modificado para {self.__periodo_inicio} até {self.__periodo_fim}.")
    @classmethod
    def get_total_gerados(cls) -> int:
        return cls.__total_gerados

    # Aplicação prática do SOLID
    # O método 'gerar' agora consome a Interface abstrata Conta de forma agnóstica
    def gerar(self, conta: Conta) -> None:
        print(f"\nGerando relatório do tipo '{self.tipo}' para uma conta do tipo '{conta.tipo}'...")
        print(f"Janela temporal: {self.periodo_inicio} a {self.periodo_fim}.")
        print(f"Saldo capturado em tempo real (via Property): R$ {conta.saldo}")
        print("Conteúdo do relatório processado com sucesso.")

    # O método 'exportar' agora recebe um comportamento genérico via injeção
    def exportar(self, exportador: ExportadorInterface) -> None:
        string_relatorio = f"Relatorio_{self.tipo}_Periodo_{self.periodo_inicio}_a_{self.periodo_fim}"
        exportador.exportar(string_relatorio)

# Bloco de demonstração do ecossistema integrado
if __name__ == "__main__":
    from conta import ContaCorrente 
    print("Testando Arquitetura SOLID e Integração da Etapa 2... \n")
    data_valida_inicio = date(2025, 1, 1)
    data_valida_fim = date(2025, 1, 31)
    relatorio1 = Relatorio("Auditoria Mensal", data_valida_inicio, data_valida_fim)

    # Criação de um objeto concreto herdeiro de Conta
    conta_teste = ContaCorrente(limite=500, saldo_inicial=2500)

    # Executa a geração injetando a conta
    relatorio1.gerar(conta_teste)
    print("\nTestando Inversão de Dependência na Exportação...")
    motor_pdf = ExportadorPDF()
    motor_csv = ExportadorCSV()

    # O mesmo relatório pode ser exportado para qualquer mecanismo compatível com a interface
    relatorio1.exportar(motor_pdf)
    relatorio1.exportar(motor_csv)
    print(f"\nTotal de relatórios ativos no sistema: {Relatorio.get_total_gerados()}")           