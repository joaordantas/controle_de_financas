from database.connection import get_connection

def criar_banco():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario     TEXT    UNIQUE NOT NULL,
            email       TEXT    UNIQUE NOT NULL,
            senha       TEXT    NOT NULL,
            tipo_perfil TEXT    DEFAULT 'Apenas Financeiro'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nome       TEXT    NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nome          TEXT    NOT NULL,
            tipo          TEXT    NOT NULL DEFAULT 'digital',
            saldo_inicial REAL    NOT NULL DEFAULT 0,
            ativo         INTEGER NOT NULL DEFAULT 1,
            principal     INTEGER NOT NULL DEFAULT 0,
            usuario_id    INTEGER NOT NULL,
            UNIQUE (nome, usuario_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)

    colunas_contas = {
        coluna[1] for coluna in conn.execute("PRAGMA table_info(contas)").fetchall()
    }
    if "principal" not in colunas_contas:
        conn.execute("ALTER TABLE contas ADD COLUMN principal INTEGER NOT NULL DEFAULT 0")

    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_contas_principal_usuario
        ON contas (usuario_id)
        WHERE principal = 1 AND ativo = 1
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            valor        REAL    NOT NULL,
            tipo         TEXT    NOT NULL,
            categoria_id INTEGER,
            conta_id     INTEGER,
            comentario   TEXT,
            data         TEXT    NOT NULL,
            usuario_id   INTEGER NOT NULL,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id),
            FOREIGN KEY (conta_id)     REFERENCES contas     (id),
            FOREIGN KEY (usuario_id)   REFERENCES usuarios   (id)
        )
    """)

    colunas_transacoes = {
        coluna[1] for coluna in conn.execute("PRAGMA table_info(transacoes)").fetchall()
    }
    if "conta_id" not in colunas_transacoes:
        conn.execute("ALTER TABLE transacoes ADD COLUMN conta_id INTEGER REFERENCES contas(id)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transferencias (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            conta_origem_id  INTEGER NOT NULL,
            conta_destino_id INTEGER NOT NULL,
            valor            REAL    NOT NULL,
            descricao        TEXT,
            data             TEXT    NOT NULL,
            usuario_id       INTEGER NOT NULL,
            FOREIGN KEY (conta_origem_id)  REFERENCES contas   (id),
            FOREIGN KEY (conta_destino_id) REFERENCES contas   (id),
            FOREIGN KEY (usuario_id)       REFERENCES usuarios (id),
            CHECK (conta_origem_id <> conta_destino_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS cartoes (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id     INTEGER NOT NULL,
            nome           TEXT    NOT NULL,
            limite_total   REAL    NOT NULL,
            dia_fechamento INTEGER NOT NULL,
            dia_vencimento INTEGER NOT NULL,
            ativo          INTEGER NOT NULL DEFAULT 1,
            criado_em      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            atualizado_em  TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (nome, usuario_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            CHECK (limite_total > 0),
            CHECK (dia_fechamento BETWEEN 1 AND 31),
            CHECK (dia_vencimento BETWEEN 1 AND 31)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS faturas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            cartao_id       INTEGER NOT NULL,
            usuario_id      INTEGER NOT NULL,
            ano_referencia  INTEGER NOT NULL,
            mes_referencia  INTEGER NOT NULL,
            data_inicio     TEXT    NOT NULL,
            data_fechamento TEXT    NOT NULL,
            data_vencimento TEXT    NOT NULL,
            criada_em       TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (cartao_id, ano_referencia, mes_referencia),
            FOREIGN KEY (cartao_id)  REFERENCES cartoes  (id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            CHECK (mes_referencia BETWEEN 1 AND 12)
        )
    """)

    colunas_faturas = {
        coluna[1] for coluna in conn.execute("PRAGMA table_info(faturas)").fetchall()
    }
    if "data_inicio" not in colunas_faturas:
        conn.execute("ALTER TABLE faturas ADD COLUMN data_inicio TEXT NOT NULL DEFAULT '1970-01-01'")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS compras_cartao (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            cartao_id    INTEGER NOT NULL,
            fatura_id    INTEGER NOT NULL,
            usuario_id   INTEGER NOT NULL,
            categoria_id INTEGER,
            valor        REAL    NOT NULL,
            descricao    TEXT    NOT NULL,
            data         TEXT    NOT NULL,
            criada_em    TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            atualizada_em TEXT   NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cartao_id)    REFERENCES cartoes    (id),
            FOREIGN KEY (fatura_id)    REFERENCES faturas    (id),
            FOREIGN KEY (usuario_id)   REFERENCES usuarios   (id),
            FOREIGN KEY (categoria_id) REFERENCES categorias (id),
            CHECK (valor > 0)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos_fatura (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            fatura_id   INTEGER NOT NULL UNIQUE,
            conta_id    INTEGER NOT NULL,
            usuario_id  INTEGER NOT NULL,
            valor       REAL    NOT NULL,
            data        TEXT    NOT NULL,
            criado_em   TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (fatura_id)  REFERENCES faturas (id),
            FOREIGN KEY (conta_id)   REFERENCES contas  (id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            CHECK (valor > 0)
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_compras_cartao_fatura ON compras_cartao (fatura_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_faturas_cartao_periodo ON faturas (cartao_id, ano_referencia DESC, mes_referencia DESC)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente    TEXT    NOT NULL,
            tipo       TEXT    NOT NULL,
            valor_total REAL   NOT NULL,
            comentario TEXT,
            data       TEXT    NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS parcelas (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id   INTEGER NOT NULL,
            valor      REAL    NOT NULL,
            status     TEXT    NOT NULL DEFAULT 'pendente',
            data       TEXT    NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (venda_id)   REFERENCES vendas   (id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS limites (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria_id INTEGER NOT NULL,
            valor        REAL    NOT NULL,
            mes          TEXT    NOT NULL,
            usuario_id   INTEGER NOT NULL,
            UNIQUE (categoria_id, mes, usuario_id),
            FOREIGN KEY (categoria_id) REFERENCES categorias (id),
            FOREIGN KEY (usuario_id)   REFERENCES usuarios   (id)
        )
    """)

    conn.commit()
    conn.close()
