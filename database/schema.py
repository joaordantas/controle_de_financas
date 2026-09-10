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
            usuario_id    INTEGER NOT NULL,
            UNIQUE (nome, usuario_id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
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
