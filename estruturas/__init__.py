"""
Estruturas de dados implementadas do zero para a Etapa 3 do SOTF.

Separadas das classes de domínio (usuario, conta, categoria, transacao,
relatorio) porque resolvem um problema diferente: não modelam o negócio,
apenas organizam os dados para busca e percurso eficientes.
"""

from .grafo import Grafo
from .tabela_hash import TabelaHash

__all__ = ["TabelaHash", "Grafo"]
