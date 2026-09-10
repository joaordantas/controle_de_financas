from database.connection import get_connection


def criar_conta(nome: str, tipo: str, saldo_inicial: float, usuario_id: int) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO contas (nome, tipo, saldo_inicial, usuario_id)
            VALUES (?, ?, ?, ?)
            """,
            (nome, tipo, saldo_inicial, usuario_id),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def listar_contas_com_saldo(usuario_id: int) -> list[tuple]:
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT
                c.id,
                c.nome,
                c.tipo,
                c.saldo_inicial,
                c.ativo,
                c.saldo_inicial
                    + COALESCE((
                        SELECT SUM(CASE WHEN t.tipo = 'entrada' THEN t.valor ELSE -t.valor END)
                        FROM transacoes t
                        WHERE t.conta_id = c.id AND t.usuario_id = c.usuario_id
                    ), 0)
                    + COALESCE((
                        SELECT SUM(tr.valor)
                        FROM transferencias tr
                        WHERE tr.conta_destino_id = c.id AND tr.usuario_id = c.usuario_id
                    ), 0)
                    - COALESCE((
                        SELECT SUM(tr.valor)
                        FROM transferencias tr
                        WHERE tr.conta_origem_id = c.id AND tr.usuario_id = c.usuario_id
                    ), 0) AS saldo_atual
            FROM contas c
            WHERE c.usuario_id = ? AND c.ativo = 1
            ORDER BY c.nome COLLATE NOCASE
            """,
            (usuario_id,),
        ).fetchall()
    finally:
        conn.close()


def buscar_conta_por_id(conta_id: int, usuario_id: int) -> tuple | None:
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT id, nome, tipo, saldo_inicial, ativo
            FROM contas
            WHERE id = ? AND usuario_id = ? AND ativo = 1
            """,
            (conta_id, usuario_id),
        ).fetchone()
    finally:
        conn.close()
