from datetime import date

class Relatorio:

    # Atributo de classe
    __total_gerados: int = 0

    # Construtor
    def __init__(self, tipo: str, periodo_inicio: date, periodo_fim: date) -> None:
        hoje = date.today()
        
        # Validação inicial de consistência        
        if periodo_inicio > hoje:
            raise ValueError("A data de início do período não pode ser futura.")
        if periodo_inicio > periodo_fim:
            raise ValueError("A data de início do período não pode ser posterior à data de fim.")

        # Atributos de instância
        self.__tipo: str = tipo
        self.__periodo_inicio: date = periodo_inicio
        self.__periodo_fim: date = periodo_fim
        Relatorio.__total_gerados += 1
        
        # Guarda de segurança
        self.__construido: bool = True
        print(f"Relatório criado com sucesso.")

    # Destrutor protegido
    def __del__(self) -> None:
        if hasattr(self, '_Relatorio__construido'):
            print("Relatório válido removido.")
            Relatorio.__total_gerados -= 1
        else:
            print("Tentativa inválida de relatório descartada sem alterar o contador.")

    # Representação do objeto
    def __str__(self) -> str:
        return f"Relatório do tipo '{self.__tipo}' para o período de {self.__periodo_inicio} a {self.__periodo_fim}."

    # Métodos GET
    def get_tipo(self) -> str:
        return self.__tipo
    def get_periodo_inicio(self) -> date:
        return self.__periodo_inicio
    def get_periodo_fim(self) -> date:
        return self.__periodo_fim
    @classmethod
    def get_total_gerados(cls) -> int:
        return cls.__total_gerados

    # Métodos SET
    def set_tipo(self, novo_tipo: str) -> None:
        if not novo_tipo.strip():
            print("Erro. O tipo do relatório não pode ser vazio.")
            return
        self.__tipo = novo_tipo.strip()
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
        print(f"Período do relatório atualizado para {self.__periodo_inicio} a {self.__periodo_fim}.")

    # Métodos de regra de negócio
    def gerar(self, conta) -> None:
        print(f"\nGerando relatório do tipo '{self.__tipo}' para a conta do tipo '{conta.get_tipo()}'...")
        print(f"Período do relatório: {self.__periodo_inicio} a {self.__periodo_fim}.")
        print(f"Conteúdo do relatório gerado com sucesso.")
    def exportar(self, formato: str) -> None:
        formato_limpo = formato.strip().lower()
        if formato_limpo not in ['pdf', 'csv', 'xlsx']:
            print("Erro. Formato de exportação não suportado. Use 'PDF', 'CSV' ou 'XLSX'.")
            return
        print(f"Exportando relatório gerado e salvo...")

# Bloco de demonstração
if __name__ == "__main__":
    print("Testando Segurança do Contador... ")

    #  Criando um relatório VÁLIDO primeiro para testar o fluxo
    data_valida_inicio = date(2025, 1, 1)
    data_valida_fim = date(2025, 1, 31)
    relatorio1 = Relatorio("Mensal OK", data_valida_inicio, data_valida_fim)
    print(f"Total de relatórios: {Relatorio.get_total_gerados()}")

    # Tentando criar um relatório INVÁLIDO (Data Futura)
    data_futura = date(2027, 11, 5)
    data_fim = date(2027, 11, 30)
    try:
        relatorio_invalido = Relatorio("Mensal Errado", data_futura, data_fim)
    except ValueError as e:
        print(f"\n[Bloqueado pelo Construtor]: {e}")

    # 3. Verificando o contador
    print(f"\nTotal de relatórios após a falha: {Relatorio.get_total_gerados()}") 