import sqlite3
from datetime import date, datetime

from categoria import Categoria
from conta import ContaCorrente, ContaPoupanca
from sistema import SistemaFinanceiro
from transacao import TransacaoDespesa, TransacaoReceita
from usuario import Usuario

"""
Camada de persistência do SOTF — Etapa 4.

É o único módulo do projeto que sabe o que é SQL ou `sqlite3`: assim como
`SistemaFinanceiro` é a fachada que integra o domínio com as estruturas de
dados, `banco.py` é a fachada que integra o domínio com o disco. Nenhuma
classe de `usuario.py`, `conta.py`, `categoria.py` ou `transacao.py` importa
este módulo — a dependência corre só num sentido (DIP).

Estratégia de salvamento: "substituição total". A cada `salvar_estado()`,
todas as contas/categorias/transações do usuário são apagadas e reinseridas
a partir do estado atual em memória. Para o volume de dados de um sistema
financeiro pessoal isso é barato, e evita todo o trabalho de sincronizar
incrementalmente IDs entre os objetos Python e as linhas do banco.
"""

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    hash_senha    TEXT NOT NULL,
    salt          TEXT NOT NULL,
    data_cadastro TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categorias (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    pai_id      INTEGER REFERENCES categorias(id) ON DELETE CASCADE,
    nome        TEXT NOT NULL,
    cor         TEXT NOT NULL,
    icone       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contas (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id    INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    tipo          TEXT NOT NULL CHECK (tipo IN ('corrente', 'poupanca')),
    saldo         REAL NOT NULL,
    limite        REAL NOT NULL DEFAULT 0,
    data_criacao  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS transacoes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    conta_id      INTEGER NOT NULL REFERENCES contas(id) ON DELETE CASCADE,
    categoria_id  INTEGER NOT NULL REFERENCES categorias(id) ON DELETE CASCADE,
    tipo          TEXT NOT NULL CHECK (tipo IN ('receita', 'despesa')),
    valor         REAL NOT NULL,
    descricao     TEXT NOT NULL,
    data          TEXT NOT NULL
);
"""


# ---- Conexão -------------------------------------------------------------
def conectar(caminho: str = "sotf.db") -> sqlite3.Connection:
    """Abre (ou cria) o banco e garante que as tabelas existam."""
    conexao = sqlite3.connect(caminho, check_same_thread=False)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.execute("PRAGMA journal_mode = WAL")
    conexao.executescript(ESQUEMA)
    return conexao


# ---- Cadastro e login -------------------------------------------------------
def cadastrar(conexao: sqlite3.Connection, nome: str, email: str, senha: str) -> tuple:
    """
    Cria um usuário novo: valida os dados (via `Usuario.__init__`, Etapas 1 e
    2) e persiste só o hash da senha, nunca o texto puro.

    Devolve (id_no_banco, Usuario). Levanta ValueError se a validação falhar
    ou se o e-mail já estiver cadastrado.
    """
    usuario = Usuario(nome, email, senha)
    hash_senha, salt_hex = usuario.credenciais

    try:
        with conexao:
            cursor = conexao.execute(
                "INSERT INTO usuarios (nome, email, hash_senha, salt, data_cadastro) "
                "VALUES (?, ?, ?, ?, ?)",
                (usuario.nome, usuario.email, hash_senha, salt_hex, usuario.data_cadastro),
            )
    except sqlite3.IntegrityError:
        raise ValueError(f"Já existe uma conta cadastrada com o e-mail '{usuario.email}'.")

    return cursor.lastrowid, usuario


def autenticar(conexao: sqlite3.Connection, email: str, senha: str):
    """
    Confere e-mail e senha contra o banco.

    Devolve (id_no_banco, Usuario) se a senha confere, ou None se o e-mail
    não existe ou a senha está errada — as duas falhas não se distinguem na
    resposta, para não revelar a quem tenta adivinhar se um e-mail existe.
    """
    linha = conexao.execute(
        "SELECT id, nome, email, hash_senha, salt, data_cadastro FROM usuarios WHERE email = ?",
        (email.strip().lower(),),
    ).fetchone()
    if linha is None:
        return None

    usuario = Usuario.reconstruir(linha["nome"], linha["email"], linha["hash_senha"],
                                   linha["salt"], linha["data_cadastro"])
    if not usuario.verificar_senha(senha):
        return None

    return linha["id"], usuario


# ---- Salvar estado --------------------------------------------------------
def salvar_estado(conexao: sqlite3.Connection, usuario_id: int, sistema: SistemaFinanceiro) -> None:
    """Apaga o que este usuário tinha salvo e regrava tudo a partir do estado atual em memória."""
    with conexao:
        # As linhas de "contas" e "categorias" saem em cascata levando junto
        # as próprias transações (ON DELETE CASCADE).
        conexao.execute("DELETE FROM contas WHERE usuario_id = ?", (usuario_id,))
        conexao.execute("DELETE FROM categorias WHERE usuario_id = ?", (usuario_id,))

        # ---- Categorias: pré-ordem já garante que o pai é gravado antes do
        # filho (mesma travessia usada em `listar_arvore`), então o pai já
        # está no dicionário quando a categoria seguinte precisa dele.
        raiz = sistema.raiz_categorias
        id_db_por_categoria = {}
        for _, categoria in raiz.listar_arvore():
            if categoria is raiz:
                continue
            pai_id_db = None if categoria.pai is raiz else id_db_por_categoria[categoria.pai]
            cursor = conexao.execute(
                "INSERT INTO categorias (usuario_id, pai_id, nome, cor, icone) VALUES (?, ?, ?, ?, ?)",
                (usuario_id, pai_id_db, categoria.nome, categoria.cor, categoria.icone),
            )
            id_db_por_categoria[categoria] = cursor.lastrowid

        # ---- Contas e, para cada uma, seu histórico de transações.
        for conta in sistema.contas:
            eh_corrente = isinstance(conta, ContaCorrente)
            cursor = conexao.execute(
                "INSERT INTO contas (usuario_id, tipo, saldo, limite, data_criacao) "
                "VALUES (?, ?, ?, ?, ?)",
                (usuario_id, "corrente" if eh_corrente else "poupanca", conta.saldo,
                 conta.limite if eh_corrente else 0.0, conta.data_criacao.isoformat()),
            )
            conta_id_db = cursor.lastrowid

            for transacao in conta.historico:
                categoria_id_db = id_db_por_categoria.get(transacao.categoria)
                if categoria_id_db is None:
                    continue  # categoria fora da árvore deste usuário — não deveria acontecer
                conexao.execute(
                    "INSERT INTO transacoes (conta_id, categoria_id, tipo, valor, descricao, data) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (conta_id_db, categoria_id_db, transacao.tipo, transacao.valor,
                     transacao.descricao, transacao.data.isoformat()),
                )


# ---- Carregar estado --------------------------------------------------------
def carregar_estado(conexao: sqlite3.Connection, usuario_id: int, usuario: Usuario) -> SistemaFinanceiro:
    """Reconstrói um SistemaFinanceiro inteiro (categorias, contas e transações) a partir do banco."""
    sistema = SistemaFinanceiro(usuario)

    # ---- Categorias: reconstrói a árvore de cima para baixo, exatamente
    # como o resto do projeto percorre árvores — recursivamente.
    linhas_categorias = conexao.execute(
        "SELECT id, pai_id, nome, cor, icone FROM categorias WHERE usuario_id = ? ORDER BY id",
        (usuario_id,),
    ).fetchall()
    categoria_por_id_db = {}

    def montar_filhas(pai_id_db) -> None:
        """RECURSÃO: monta as categorias cujo pai_id é `pai_id_db`, depois as netas."""
        for linha in linhas_categorias:
            if linha["pai_id"] != pai_id_db:
                continue
            pai_objeto = categoria_por_id_db[pai_id_db] if pai_id_db is not None else None
            categoria = sistema.registrar_categoria(
                Categoria(linha["nome"], linha["cor"], linha["icone"]), pai_objeto)
            categoria_por_id_db[linha["id"]] = categoria
            montar_filhas(linha["id"])

    montar_filhas(None)

    # ---- Contas: saldo_inicial recebe o saldo já salvo — as transações
    # abaixo só entram no histórico, sem mexer no saldo de novo.
    linhas_contas = conexao.execute(
        "SELECT id, tipo, saldo, limite, data_criacao FROM contas WHERE usuario_id = ? ORDER BY id",
        (usuario_id,),
    ).fetchall()
    conta_por_id_db = {}
    for linha in linhas_contas:
        data_criacao = date.fromisoformat(linha["data_criacao"])
        if linha["tipo"] == "corrente":
            conta = ContaCorrente(limite=linha["limite"], saldo_inicial=linha["saldo"],
                                   data_criacao=data_criacao)
        else:
            conta = ContaPoupanca(saldo_inicial=linha["saldo"], data_criacao=data_criacao)
        sistema.abrir_conta(conta)
        conta_por_id_db[linha["id"]] = conta

    # ---- Transações: reidratadas em ordem cronológica, sem reaplicar o
    # efeito no saldo (ver `SistemaFinanceiro.reidratar_transacao`).
    linhas_transacoes = conexao.execute(
        "SELECT conta_id, categoria_id, tipo, valor, descricao, data FROM transacoes "
        "WHERE conta_id IN (SELECT id FROM contas WHERE usuario_id = ?) ORDER BY data",
        (usuario_id,),
    ).fetchall()
    for linha in linhas_transacoes:
        conta = conta_por_id_db[linha["conta_id"]]
        categoria = categoria_por_id_db[linha["categoria_id"]]
        data = datetime.fromisoformat(linha["data"])
        classe = TransacaoReceita if linha["tipo"] == "receita" else TransacaoDespesa
        sistema.reidratar_transacao(classe(linha["valor"], linha["descricao"], categoria, data=data), conta)

    return sistema
