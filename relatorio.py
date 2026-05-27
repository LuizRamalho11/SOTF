from datetime import date

class Relatorio:

# Atributo de classe
    __total_relatorios: int = 0

# Construtor
    def __init__(self, tipo: str, periodo_inicio:date, periodo_fim:date):

# Validação inicial de consistência
        if periodo_inicio > periodo_fim:
            raise ValueError("A data de início do período não pode ser posterior à data de fim.")

# Incrementa o contador de classe
        Relatorio.__total_relatorios += 1

# Atributos de instância
        self.__tipo = tipo
        self.__periodo_inicio: date = periodo_inicio
        self.__periodo_fim: date = periodo_fim
        print(f"Relatório criado.")

# Destrutor
def __del__(self) -> None:
    Relatorio.__total_relatorios -= 1
    print("Relatório removido.")

# Representação do objeto
def __str__(self) -> str:
    return (f"Relatório do tipo '{self.__tipo}' para o período de {self.__periodo_inicio} a {self.__periodo_fim}.")

# Métodos GET
def get_tipo(self) -> str:
    return self.__tipo
def get_periodo_inicio(self) -> date:
    return self.__periodo_inicio
def get_periodo_fim(self) -> date:
    return self.__periodo_fim
@classmethod
def get_total_relatorios(cls) -> int:
    return cls.__total_relatorios

# Métodos SET
def set_tipo(self, novo_tipo: str) -> None:
    if not novo_tipo.strip():
        print("Erro. O tipo do relatório não pode ser vazio.")
        return
    self.__tipo = novo_tipo.strip()
def set_periodo(self, inicio: date, fim: date) -> None:
    if inicio > fim:
        print("Erro. A data de início do período não pode ser posterior à data de fim.")
        return
    self.__periodo_inicio = inicio
    self.__periodo_fim = fim
    print(f"Período do relatório atualizado para {self.__periodo_inicio} a {self.__periodo_fim}.")

# Metódos de regra de negócio
def gerar(self, conta) -> None:
    print(f"\nGerando relatório do tipo '{self.__tipo}' para a conta do tipo '{conta.get_tipo()}...")
    print(f"\nPeríodo do relatório: {self.__periodo_inicio} a {self.__periodo_fim}.")
    print(f"\nConteúdo do relatório gerado com sucesso.")
def exportar(self, formato: str) -> None:
    formato_limpo = formato.strip().lower()
    if formato_limpo not in ['pdf', 'csv', 'xlsx']:
        print("Erro. Formato de exportação não suportado. Use 'PDF', 'CSV' ou 'XLSX'.")
        return
    print(f"Exportando relatório gerado e salvo.")
    

