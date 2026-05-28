# 💳 SOTF — Sistema de Organização de Transações Financeiras

> Projeto desenvolvido para a disciplina de **Programação Orientada a Objetos** — UFPB 2026  
> Etapa 1: Classes, Encapsulamento, Atributos de Classe e Instância, Construtores e Destrutores

---

## 📋 Sumário

- [Sobre o Projeto](#-sobre-o-projeto)
- [Objetivos](#-objetivos)
- [Problema que Resolve](#-problema-que-resolve)
- [Estrutura de Arquivos](#-estrutura-de-arquivos)
- [Diagrama de Classes](#-diagrama-de-classes)
- [Descrição de Cada Arquivo](#-descrição-de-cada-arquivo)
  - [usuario.py](#usuariopy)
  - [conta.py](#contapy)
  - [categoria.py](#categoriapy)
  - [transacao.py](#transacaopy)
  - [relatorio.py](#relatoriopy)
- [@classmethods e @staticmethods](#classmethods-e-staticmethods)
- [Conceitos de POO Aplicados](#-conceitos-de-poo-aplicados)
- [Como Executar](#-como-executar)
- [Exemplo de Uso](#-exemplo-de-uso)
- [Erros Encontrados e Soluções](#-erros-encontrados-e-soluções-diário-de-bordo)
- [Próximas Etapas](#-próximas-etapas)
- [Equipe](#-equipe)

---

## 📌 Sobre o Projeto

O **SOTF** é um sistema de gerenciamento financeiro pessoal desenvolvido inteiramente em Python, utilizando os princípios da Programação Orientada a Objetos. O sistema permite que usuários cadastrem contas, registrem transações, categorizem seus gastos e acompanhem o histórico financeiro com total controle sobre os dados.

O projeto foi estruturado com foco em **encapsulamento real**: nenhum dado sensível (como saldo ou senha) pode ser alterado diretamente de fora das classes — toda modificação passa por métodos que aplicam regras de negócio.

---

## 🎯 Objetivos

### Objetivos Acadêmicos (Etapa 1)
- Aplicar **classes e objetos** em um contexto de problema real
- Demonstrar **encapsulamento** com atributos privados (`__atributo`) e acesso exclusivo via `get` e `set`
- Diferenciar e utilizar **atributos de classe** e **atributos de instância**
- Implementar **construtores** (`__init__`) com validação de dados
- Implementar **destrutores** (`__del__`) para limpeza e log
- Construir um **diagrama de classes** com relacionamentos, multiplicidades e tipos de seta

### Objetivos do Produto
- Oferecer controle financeiro simples, transparente e sem dependência de banco de dados externo
- Reduzir erros humanos no registro de transações através de validações automáticas
- Servir como base sólida e expansível para as etapas seguintes do projeto

---

## 🧩 Problema que Resolve

| Problema Real | Solução no SOTF |
|---|---|
| Não saber para onde foi o dinheiro | Histórico detalhado em cada `Conta` |
| Gastos espalhados em anotações avulsas | `Transacao` registrada com data, valor e categoria |
| Risco de alterar saldo por engano | `__saldo` sem setter — só muda por `depositar()` e `sacar()` |
| Senhas expostas no código | `__senha` nunca retornada — apenas verificada internamente |
| Dados inconsistentes entre objetos | Validação no construtor impede criação de objetos inválidos |
| Múltiplos usuários sem banco de dados | `__total_usuarios` como atributo de classe rastreia tudo |

---

## 📁 Estrutura de Arquivos

```
SOTF/
│
├── usuario.py       # Classe Usuario — autenticação e dados do usuário
├── conta.py         # Classe Conta — saldo, limite e histórico de movimentações
├── categoria.py     # Classe Categoria — classificação de transações
├── transacao.py     # Classe Transacao — registro de cada entrada ou saída
├── relatorio.py     # Classe Relatorio — análise de período financeiro
└── README.md        # Este arquivo
```

### Relação entre os arquivos

```
usuario.py
  └── possui N instâncias de → conta.py
        └── possui N instâncias de → transacao.py
                                          └── referencia 1 → categoria.py
  └── possui N instâncias de → relatorio.py
                                    └── usa (dependência) → transacao.py
```

---

## 📊 Diagrama de Classes

```
┌─────────────────────────┐
│        Usuario          │
├─────────────────────────┤
│ - __id: int             │
│ - __nome: str           │
│ - __email: str          │
│ - __senha: str          │
│ - __data_cadastro: str  │
│ @ __total_usuarios: int │
├─────────────────────────┤
│ + get_id()              │
│ + get_nome()            │
│ + get_email()           │
│ + get_data_cadastro()   │
│ + verificar_senha()     │
│ + set_nome()            │
│ + set_email()           │
│ + set_senha()           │
│ + get_total_usuarios()  │
└────────┬────────────────┘
         │ 1                          1
         ├──────────────────────────────────────────┐
         │ N                                        │ N
┌────────┴────────────────┐          ┌──────────────┴──────────┐
│         Conta           │          │        Relatorio        │
├─────────────────────────┤          ├─────────────────────────┤
│ - __numero: int         │          │ - __periodo_inicio: date│
│ - __tipo: str           │          │ - __periodo_fim: date   │
│ - __saldo: float        │          │ - __tipo: str           │
│ - __limite: float       │          │ @ __total_gerados: int  │
│ - __data_abertura: str  │          ├─────────────────────────┤
│ - __historico: list     │          │ + get_tipo()            │
│ @ __total_contas: int   │          │ + set_periodo()         │
├─────────────────────────┤          │ + gerar()               │
│ + get_saldo()           │          │ + exportar()            │
│ + get_limite()          │          │ + get_total_gerados()   │
│ + set_limite()          │          └────────────┬────────────┘
│ + depositar()           │                       │ usa (dependência)
│ + sacar()               │                       │ · · · · · · · · ·
│ + exibir_historico()    │                       ▼
│ + get_total_contas()    │          ┌─────────────────────────┐
└────────┬────────────────┘          │       Transacao         │
         │ 1                         ├─────────────────────────┤
         │ N                         │ - __valor: float        │
         ▼                           │ - __tipo: str           │
┌─────────────────────────┐          │ - __descricao: str      │
│       Transacao         │◄─────────│ - __data: datetime      │
│    (ver à direita)      │ N     1  │ - __categoria: Categoria│
└─────────────────────────┘          ├─────────────────────────┤
                                     │ + get_valor()           │
         ◆────────────────────────── │ + get_tipo()            │
         N                           │ + get_categoria()       │
         1                           └─────────────────────────┘
┌─────────────────────────┐
│       Categoria         │
├─────────────────────────┤
│ - __id: int             │
│ - __nome: str           │
│ - __cor: str            │
│ - __icone: str          │
│ @ __total_categorias    │
│ @ __categorias_padrao   │
├─────────────────────────┤
│ + get_nome()            │
│ + get_cor()             │
│ + set_nome()            │
│ + set_cor()             │
│ + listar_padrao()       │
│ + criar_a_partir_do_padrao() │
│ - __validar_cor()       │
└─────────────────────────┘

Legenda:
  →   associação (tem)
  ◆→  agregação (usa, mas existe independente)
  ··→ dependência (usa temporariamente)
  @   atributo de classe (compartilhado)
  -   atributo privado (name mangling __)
```

---

## 📄 Descrição de Cada Arquivo

---

### `usuario.py`

**Responsabilidade:** Representa quem utiliza o sistema. Armazena credenciais e dados pessoais com total proteção de acesso.

**Por que foi criado assim:**  
A senha nunca deve ser exposta — por isso não existe `get_senha()`. Em vez disso, o método `verificar_senha()` compara internamente sem revelar o valor armazenado. Esse é o padrão usado em sistemas reais de autenticação.

**Atributos de instância (privados):**

| Atributo | Tipo | Descrição |
|---|---|---|
| `__id` | `int` | Identificador único gerado automaticamente |
| `__nome` | `str` | Nome completo do usuário |
| `__email` | `str` | E-mail de acesso |
| `__senha` | `str` | Senha — nunca retornada, apenas verificada |
| `__data_cadastro` | `str` | Data/hora de criação do objeto |

**Atributo de classe:**

| Atributo | Tipo | Descrição |
|---|---|---|
| `__total_usuarios` | `int` | Contador global de usuários ativos — compartilhado por todos os objetos |

**Métodos públicos (get/set):**

| Método | Descrição |
|---|---|
| `get_id()` | Retorna o ID único |
| `get_nome()` | Retorna o nome |
| `get_email()` | Retorna o e-mail |
| `get_data_cadastro()` | Retorna a data de criação |
| `verificar_senha(senha)` | Retorna `True` se a senha confere, sem expor o valor |
| `set_nome(novo)` | Atualiza nome — valida mínimo de 2 caracteres |
| `set_email(novo)` | Atualiza e-mail — valida presença de `@` e `.` |
| `set_senha(atual, nova)` | Troca senha — exige confirmação da senha atual |
| `get_total_usuarios()` *(classmethod)* | Retorna total de usuários no sistema |

**Construtor:** registra `__data_cadastro` automaticamente e incrementa `__total_usuarios`.  
**Destrutor:** decrementa `__total_usuarios` ao remover o objeto da memória.

---

### `conta.py`

**Responsabilidade:** Representa uma conta financeira. Controla saldo, limite e histórico de movimentações.

**Por que foi criado assim:**  
O `__saldo` **não possui** `set_saldo()` — essa é uma decisão deliberada de design. Permitir alteração direta do saldo quebraria toda a lógica de negócio. O saldo só muda através de `depositar()` e `sacar()`, que aplicam validações antes de qualquer alteração. O histórico é retornado como cópia (`.copy()`) para impedir adulteração externa.

**Atributos de instância (privados):**

| Atributo | Tipo | Descrição |
|---|---|---|
| `__numero` | `int` | Número único gerado automaticamente |
| `__tipo` | `str` | Tipo da conta: `'corrente'` ou `'poupança'` |
| `__saldo` | `float` | Saldo atual — **sem setter** |
| `__limite` | `float` | Crédito disponível além do saldo |
| `__data_abertura` | `str` | Data/hora de abertura |
| `__historico` | `list` | Registro de todas as movimentações |

**Atributo de classe:**

| Atributo | Tipo | Descrição |
|---|---|---|
| `__total_contas` | `int` | Total de contas abertas no sistema |

**Métodos públicos:**

| Método | Descrição |
|---|---|
| `get_saldo()` | Retorna o saldo atual |
| `get_limite()` | Retorna o limite |
| `get_saldo_disponivel()` | Retorna `saldo + limite` |
| `get_historico()` | Retorna **cópia** do histórico |
| `set_limite(valor)` | Atualiza limite — valida `>= 0` |
| `set_tipo(tipo)` | Altera tipo da conta com validação |
| `depositar(valor)` | Adiciona ao saldo — valida `> 0` |
| `sacar(valor)` | Subtrai do saldo — valida saldo disponível |
| `exibir_historico()` | Imprime todas as movimentações formatadas |
| `get_total_contas()` *(classmethod)* | Retorna total de contas no sistema |

**Método privado:**

| Método | Descrição |
|---|---|
| `__registrar(desc)` | Adiciona entrada no histórico com timestamp — só chamado internamente |

**Construtor:** valida `tipo`, define `saldo_inicial` e `limite`, inicia `__historico` com registro de abertura.  
**Destrutor:** exibe saldo final, total de movimentações e decrementa `__total_contas`.

---

### `categoria.py`

**Responsabilidade:** Classifica as transações financeiras (Alimentação, Transporte, Saúde etc.). Possui uma lista de categorias padrão compartilhada entre todos os objetos.

**Por que foi criado assim:**  
`__categorias_padrao` é um atributo de classe do tipo `list` — ela existe independente de qualquer instância criada. O método `criar_a_partir_do_padrao()` demonstra o padrão *factory method*: cria um objeto a partir de dados pré-definidos na própria classe. A cor é validada por um método estático privado que não precisa de `self` nem de `cls` — apenas verifica o formato hexadecimal.

**Atributos de instância (privados):**

| Atributo | Tipo | Descrição |
|---|---|---|
| `__id` | `int` | Identificador único |
| `__nome` | `str` | Nome da categoria |
| `__cor` | `str` | Cor em formato hex (`#RRGGBB`) |
| `__icone` | `str` | Emoji representativo |

**Atributos de classe:**

| Atributo | Tipo | Descrição |
|---|---|---|
| `__total_categorias` | `int` | Total de categorias personalizadas criadas |
| `__categorias_padrao` | `list` | Lista de dicionários com categorias padrão do sistema |

**Categorias padrão disponíveis:**

| Ícone | Nome | Cor |
|---|---|---|
| 🍔 | Alimentação | `#FF6B6B` |
| 🚗 | Transporte | `#4ECDC4` |
| 💊 | Saúde | `#45B7D1` |
| 🎮 | Lazer | `#96CEB4` |
| 🏠 | Moradia | `#FFEAA7` |
| 📚 | Educação | `#DDA0DD` |
| 💰 | Renda | `#98FB98` |
| 📦 | Outros | `#D3D3D3` |

**Métodos públicos:**

| Método | Tipo | Descrição |
|---|---|---|
| `get_id()` | instância | Retorna o ID |
| `get_nome()` | instância | Retorna o nome |
| `get_cor()` | instância | Retorna a cor hex |
| `get_icone()` | instância | Retorna o emoji |
| `set_nome(novo)` | instância | Atualiza nome — valida não vazio |
| `set_cor(nova)` | instância | Atualiza cor — valida formato `#RRGGBB` |
| `set_icone(novo)` | instância | Atualiza o emoji |
| `exibir()` | instância | Imprime dados formatados |
| `get_total_categorias()` | `@classmethod` | Total de categorias criadas |
| `get_categorias_padrao()` | `@classmethod` | Retorna **cópia** da lista padrão |
| `listar_padrao()` | `@classmethod` | Imprime todas as categorias padrão |
| `criar_a_partir_do_padrao(i)` | `@classmethod` | Cria objeto a partir do índice da lista padrão |

**Método privado:**

| Método | Tipo | Descrição |
|---|---|---|
| `__validar_cor(cor)` | `@staticmethod` | Verifica se a string é um hex `#RRGGBB` válido |

**Construtor:** valida nome (não vazio) e cor (formato hex) antes de criar. Incrementa `__total_categorias`.  
**Destrutor:** decrementa `__total_categorias`.

---

### `transacao.py`

**Responsabilidade:** Registra cada movimentação financeira individual — entradas e saídas — com data, descrição, valor e categoria vinculada.

**Por que foi criado assim:**  
Uma transação é imutável após criação — não faz sentido alterar o valor ou a data de um lançamento já feito. Por isso, os atributos críticos (`__valor`, `__data`, `__tipo`) têm apenas `get`, sem `set`. A categoria é vinculada no construtor e pode ser consultada, mas não trocada arbitrariamente.

**Atributos de instância (privados):**

| Atributo | Tipo | Descrição |
|---|---|---|
| `__id` | `int` | Identificador único |
| `__valor` | `float` | Valor da transação |
| `__tipo` | `str` | `'entrada'` ou `'saida'` |
| `__descricao` | `str` | Descrição do lançamento |
| `__data` | `datetime` | Data/hora do registro |
| `__categoria` | `Categoria` | Objeto de categoria vinculado |

**Atributo de classe:**

| Atributo | Tipo | Descrição |
|---|---|---|
| `__total_transacoes` | `int` | Total de transações registradas no sistema |

**Métodos públicos:**

| Método | Descrição |
|---|---|
| `get_id()` | Retorna o ID |
| `get_valor()` | Retorna o valor |
| `get_tipo()` | Retorna o tipo (`entrada`/`saida`) |
| `get_descricao()` | Retorna a descrição |
| `get_data()` | Retorna a data formatada |
| `get_categoria()` | Retorna o objeto `Categoria` vinculado |
| `exibir()` | Imprime a transação formatada |
| `get_total_transacoes()` *(classmethod)* | Total de transações no sistema |

**Construtor:** valida `valor > 0`, valida `tipo`, registra `__data` automaticamente e incrementa contador.  
**Destrutor:** decrementa `__total_transacoes`.

---

### `relatorio.py`

**Responsabilidade:** Analisa um conjunto de transações dentro de um período definido, gerando resumos financeiros por categoria e tipo.

**Por que foi criado assim:**  
`Relatorio` tem uma relação de **dependência** com `Transacao` — ele usa as transações para calcular resultados, mas não as possui. O período é definido pelos atributos privados e pode ser ajustado via `set_periodo()`. O método `gerar()` recebe uma lista de transações como parâmetro e processa internamente.

**Atributos de instância (privados):**

| Atributo | Tipo | Descrição |
|---|---|---|
| `__id` | `int` | Identificador único |
| `__periodo_inicio` | `date` | Data de início da análise |
| `__periodo_fim` | `date` | Data de fim da análise |
| `__tipo` | `str` | Tipo: `'mensal'`, `'semanal'` ou `'personalizado'` |
| `__resultado` | `dict` | Dados processados após `gerar()` |

**Atributo de classe:**

| Atributo | Tipo | Descrição |
|---|---|---|
| `__total_gerados` | `int` | Total de relatórios gerados no sistema |

**Métodos públicos:**

| Método | Descrição |
|---|---|
| `get_id()` | Retorna o ID |
| `get_tipo()` | Retorna o tipo do relatório |
| `get_periodo()` | Retorna o período como tupla `(inicio, fim)` |
| `set_periodo(inicio, fim)` | Atualiza o período — valida que início < fim |
| `set_tipo(tipo)` | Atualiza o tipo com validação |
| `gerar(transacoes)` | Processa a lista de transações e preenche `__resultado` |
| `exibir()` | Imprime o relatório gerado |
| `exportar(formato)` | Exporta o resultado (extensível para CSV, PDF) |
| `get_total_gerados()` *(classmethod)* | Total de relatórios gerados no sistema |

**Construtor:** define período e tipo, inicializa `__resultado` vazio e incrementa contador.  
**Destrutor:** decrementa `__total_gerados`.

---

## 🔧 @classmethods e @staticmethods

### O que é `@classmethod`

Um método de classe recebe a **própria classe** (`cls`) como primeiro argumento, em vez de uma instância (`self`). Isso permite acessar e modificar **atributos de classe** sem precisar criar um objeto.

```python
@classmethod
def get_total_contas(cls) -> int:
    return cls.__total_contas

# Uso — sem criar nenhum objeto:
Conta.get_total_contas()   # → 3
```

### Todos os `@classmethod` do projeto

| Classe | Método | O que faz |
|---|---|---|
| `Usuario` | `get_total_usuarios()` | Retorna total de usuários ativos |
| `Conta` | `get_total_contas()` | Retorna total de contas abertas |
| `Categoria` | `get_total_categorias()` | Retorna total de categorias criadas |
| `Categoria` | `get_categorias_padrao()` | Retorna cópia da lista padrão |
| `Categoria` | `listar_padrao()` | Imprime todas as categorias padrão |
| `Categoria` | `criar_a_partir_do_padrao(i)` | Cria objeto a partir do índice da lista padrão (*factory method*) |
| `Transacao` | `get_total_transacoes()` | Retorna total de transações registradas |
| `Relatorio` | `get_total_gerados()` | Retorna total de relatórios gerados |

---

### O que é `@staticmethod`

Um método estático **não recebe nem `self` nem `cls`** — é um utilitário puro que pertence à classe apenas por organização. Não acessa nem modifica nenhum atributo do objeto ou da classe.

```python
@staticmethod
def __validar_cor(cor: str) -> bool:
    if not cor.startswith("#"):
        return False
    if len(cor) != 7:
        return False
    return all(c in "0123456789ABCDEFabcdef" for c in cor[1:])
```

### Todos os `@staticmethod` do projeto

| Classe | Método | Visibilidade | O que faz |
|---|---|---|---|
| `Categoria` | `__validar_cor(cor)` | Privado (`__`) | Valida se a string segue o formato `#RRGGBB` |

> O prefixo `__` torna o método estático **privado** — ele só pode ser chamado dentro da própria classe, pelo construtor e pelo `set_cor()`. Não é acessível de fora.

---

### Diferença prática entre os três tipos

```python
class Categoria:
    __total = 0                    # atributo de CLASSE

    def __init__(self, nome):
        self.__nome = nome         # atributo de INSTÂNCIA
        Categoria.__total += 1

    def get_nome(self):            # método de INSTÂNCIA — usa self
        return self.__nome

    @classmethod
    def get_total(cls):            # método de CLASSE — usa cls, acessa __total
        return cls.__total

    @staticmethod
    def __validar_cor(cor):        # método ESTÁTICO — não usa self nem cls
        return cor.startswith("#") and len(cor) == 7
```

---

## 🧠 Conceitos de POO Aplicados

### Encapsulamento

Todos os atributos do projeto usam `__` (duplo underscore), que ativa o *name mangling* do Python:

```python
self.__saldo   →   internamente vira   _Conta__saldo
```

Isso significa que `objeto.__saldo` de fora da classe levanta `AttributeError`, pois o Python não encontra o nome `__saldo` — apenas `_Conta__saldo`.

```python
c = Conta("corrente", 1000.0)
print(c.__saldo)        # AttributeError: 'Conta' object has no attribute '__saldo'
print(c.get_saldo())    # 1000.0 — acesso correto via getter
```

### Atributo de Classe vs Atributo de Instância

```python
class Conta:
    __total_contas = 0        # de CLASSE — um só valor para todas as contas

    def __init__(self, tipo, saldo):
        self.__tipo = tipo     # de INSTÂNCIA — cada conta tem o seu
        self.__saldo = saldo   # de INSTÂNCIA — cada conta tem o seu
        Conta.__total_contas += 1
```

### Construtor com Validação

```python
def __init__(self, tipo: str, saldo_inicial: float = 0.0):
    if tipo.lower() not in ("corrente", "poupança"):
        raise ValueError(f"Tipo inválido: '{tipo}'")
    # Se chegou aqui, o objeto é válido — nunca existe com dado errado
    self.__tipo = tipo.lower()
    self.__saldo = saldo_inicial
```

### Destrutor com Log

```python
def __del__(self):
    Conta.__total_contas -= 1
    # Chamado automaticamente ao: del objeto, fim do escopo, ou fim do programa
```

### Proteção do Histórico com `.copy()`

```python
def get_historico(self) -> list:
    return self.__historico.copy()   # cópia — alterações externas não afetam o original

# Sem .copy(), isso seria possível (e perigoso):
h = conta.get_historico()
h.append("movimentação falsa")       # com .copy(), só afeta h — histórico original intacto
```

---

## ▶️ Como Executar

**Pré-requisito:** Python 3.8 ou superior.

```bash
# Clonar o repositório
git clone https://github.com/LuizRamalho11/SOTF.git
cd SOTF

# Executar a demonstração de cada módulo individualmente
python usuario.py
python conta.py
python categoria.py
python transacao.py
python relatorio.py
```

Cada arquivo possui um bloco `if __name__ == "__main__"` com uma demonstração completa do módulo.

---

## 💡 Exemplo de Uso

```python
from usuario import Usuario
from conta import Conta
from categoria import Categoria
from transacao import Transacao

# 1. Criar usuário
usuario = Usuario("Pedro Silva", "pedro@email.com", "senha123")

# 2. Abrir conta
conta = Conta("corrente", saldo_inicial=700.0, limite=0.0)

# 3. Registrar categoria
cat_alimentacao = Categoria.criar_a_partir_do_padrao(1)  # Alimentação padrão

# 4. Movimentar
conta.sacar(400.0)    # Aluguel
conta.sacar(35.0)     # Lanche

# 5. Consultar
print(f"Saldo disponível: R$ {conta.get_saldo():.2f}")
conta.exibir_historico()

# 6. Verificar contadores (atributos de classe)
print(f"Total de contas no sistema: {Conta.get_total_contas()}")
print(f"Total de usuários:          {Usuario.get_total_usuarios()}")
```

**Saída esperada:**
```
[+] Usuário 'Pedro Silva' criado em 26/05/2026 09:15.
[+] Conta #1 (corrente) aberta em 26/05/2026 09:15.
[+] Categoria '🍔 Alimentação' criada (id=1).
Saque de R$ 400.00 realizado. Saldo atual: R$ 300.00
Saque de R$ 35.00 realizado. Saldo atual: R$ 265.00

Saldo disponível: R$ 265.00

── Histórico da Conta #1 ──
  [26/05/2026 09:15] Conta aberta com saldo inicial R$ 700.00
  [26/05/2026 09:15] Saque de R$ 400.00 | Saldo: R$ 300.00
  [26/05/2026 09:15] Saque de R$ 35.00  | Saldo: R$ 265.00

Total de contas no sistema: 1
Total de usuários:          1
```

---

## 🪵 Erros Encontrados e Soluções (Diário de Bordo)

### Erro 1 — `AttributeError: _Categoria__categorias_padrao`

**O que aconteceu:**
```
AttributeError: type object 'Categoria' has no attribute '_Categoria__categorias_padrao'.
Did you mean: '_Categoria__categoria_padrao'?
```

**Causa:** O atributo foi declarado como `__categoria_padrao` (sem o `s`) na linha de definição, mas todos os métodos (`listar_padrao`, `get_categorias_padrao`, `criar_a_partir_do_padrao`) acessavam `__categorias_padrao` (com o `s`). Como o `__` ativa o *name mangling*, o Python não encontrou o nome esperado.

**Solução:** Padronizar o nome em toda a classe — escolhemos `__categorias_padrao` (com `s`) por ser mais descritivo.

**Lição:** Atributos com `__` são case e character sensitive de forma ainda mais crítica — um erro de digitação cria um atributo completamente diferente sem nenhum aviso de sintaxe.

---

### Erro 2 — Destrutor imprimindo mensagem inesperada ao fim do programa

**O que aconteceu:** Mesmo sem chamar `del` explicitamente, ao encerrar o script o terminal exibia `"[-] Usuário 'X' removido do sistema."` para todos os objetos.

**Causa:** O Python chama `__del__` automaticamente em **todos os objetos ainda na memória** ao encerrar o programa — não apenas nos destruídos com `del` manual.

**Solução:** Removemos o `print()` do `__del__`, mantendo apenas o decremento do contador. O log explícito fica disponível apenas quando `del` é chamado intencionalmente no código de demonstração.

**Lição:** O destrutor não é equivalente ao `del` — ele é controlado pelo *garbage collector* do Python e não pelo programador.

---

### Erro 3 — `set_saldo()` permitia contornar as regras de negócio

**O que aconteceu:** A primeira versão da classe `Conta` tinha um `set_saldo()` genérico que aceitava qualquer valor.

**Causa:** Isso permitia fazer `conta.set_saldo(99999)` diretamente, ignorando completamente a lógica de `depositar()` e `sacar()` e o registro no histórico.

**Solução:** O `set_saldo()` foi removido. O `__saldo` só pode ser alterado pelos métodos `depositar()` e `sacar()`, que validam o valor, atualizam o histórico e retornam feedback ao chamador.

**Lição:** Encapsulamento não é apenas esconder o atributo — é proteger a **lógica de negócio** que mantém o dado coerente com o restante do sistema.

---

### Erro 4 — Contador de `Relatorio` assumindo valores negativos

**O que aconteceu:** O atributo de classe `__total_gerados` decresc ia incorretamente, chegando a valores negativos mesmo sem nenhum objeto ter sido criado com sucesso.

**Causa:** Quando o construtor rejeitava uma data inválida disparando um `ValueError`, o Python enviava o objeto incompleto para o *garbage collector*, que chamava o `__del__` automaticamente. Como o destrutor decrementava `__total_gerados` sem verificar se o objeto havia sido de fato construído, ele subtraía 1 de um contador que nunca havia sido somado.

**Solução:** Foi implementada uma guarda de segurança com `self.__construido = True` como última linha do construtor — só executada se nenhuma exceção ocorrer antes. O `__del__` foi modificado para usar `hasattr()` antes de decrementar:

```python
def __del__(self):
    if hasattr(self, '_Relatorio__construido') and self.__construido:
        Relatorio.__total_gerados -= 1
```

**Lição:** O destrutor pode ser chamado mesmo para objetos que nunca terminaram de ser construídos. Sempre que o construtor puder lançar exceções, o `__del__` precisa verificar se o objeto realmente chegou a um estado válido antes de desfazer qualquer operação.

---

### Erro 5 — `sacar()` bloqueava saques legítimos com limite disponível

**O que aconteceu:** A validação original `if valor > self.__saldo` impedia saques mesmo quando o usuário ainda possuía limite de crédito disponível. Ao mesmo tempo, remover a validação completamente permitia saques ilimitados, estourando o limite aprovado.

**Causa:** A regra de negócio estava incompleta — ela considerava apenas o saldo isolado, ignorando que o "poder de compra real" do usuário é a soma `saldo + limite`. Uma conta com saldo `R$ 0,00` e limite `R$ 500,00` tem `R$ 500,00` disponíveis para saque, mas a validação antiga bloqueava qualquer valor acima de zero.

**Solução:** A validação foi reestruturada para calcular o saldo disponível real antes de decidir:

```python
if valor > (self.__saldo + self.__limite):
    raise ValueError("Saldo e limite insuficientes para realizar esta operação.")
```

Agora o sistema permite que o saldo fique negativo (utilizando o limite), mas bloqueia o saque no centavo exato em que o limite total é ultrapassado.

**Lição:** Validações financeiras devem refletir a regra de negócio completa, não apenas o estado mais simples do atributo. Um erro de lógica aqui bloquearia operações legítimas ou permitiria fraudes — ambos igualmente problemáticos.

## 🚀 Próximas Etapas

### Etapa 2 — Herança, Polimorfismo, Interfaces e SOLID

- [ ] `ContaCorrente` e `ContaPoupanca` como subclasses de `Conta`
  - `ContaPoupanca` terá método `aplicar_rendimento()` sobrescrito
- [ ] `TransacaoEntrada` e `TransacaoSaida` como subclasses de `Transacao`
- [ ] Substituição dos get/set manuais por `@property` (mais pythônico)
- [ ] Diagrama de classes atualizado com hierarquia de herança
- [ ] Aplicação dos princípios SOLID:
  - **SRP** — cada classe com uma única responsabilidade
  - **OCP** — aberto para extensão, fechado para modificação
  - **LSP** — subclasses substituíveis pelas superclasses

### Etapa 3 — Estruturas Avançadas e Interface Gráfica

- [ ] Interface visual com **Streamlit**
- [ ] Tabela hash para busca rápida de transações por categoria
- [ ] Grafo de categorias com visualização de relacionamentos
- [ ] Pesquisa em largura no histórico financeiro
- [ ] Recursão nos relatórios para consolidação de períodos aninhados
- [ ] Revisão de SOLID no código alterado

### Expansões Futuras (além da disciplina)

- [ ] Exportação de relatórios em PDF e CSV
- [ ] Metas financeiras mensais por categoria com alertas
- [ ] Persistência com banco de dados SQLite
- [ ] Hash de senha com `bcrypt` para segurança real
- [ ] Dashboard com gráficos de pizza e linha por categoria

---

## 👥 Equipe

| Integrante | Responsabilidade na Etapa 1 |
|---|---|
| Luiz Felipe Ramalho Reis  | `usuario.py` + 'categoria.py' |
| Luy Koji Castelo Branco   | `conta.py` + `relatorio.py`   |
| Gabriel José              | `transacao.py`                |

---

## 📚 Disciplina

> **Programação Orientada a Objetos**  
> Universidade Federal da Paraíba — UFPB  
> 2026

---