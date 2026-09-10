from database.connection import get_connection


SALDO_ATUAL_SQL = """
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
    ), 0)
"""


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


def listar_contas_com_saldo(usuario_id: int, incluir_inativas: bool = False) -> list[tuple]:
    conn = get_connection()
    try:
        filtro_ativo = "" if incluir_inativas else "AND c.ativo = 1"
        return conn.execute(
            f"""
            SELECT c.id, c.nome, c.tipo, c.saldo_inicial, c.ativo,
                   {SALDO_ATUAL_SQL} AS saldo_atual
            FROM contas c
            WHERE c.usuario_id = ? {filtro_ativo}
            ORDER BY c.ativo DESC, c.nome COLLATE NOCASE
            """,
            (usuario_id,),
        ).fetchall()
    finally:
        conn.close()


def buscar_conta_por_id(
    conta_id: int, usuario_id: int, somente_ativa: bool = True
) -> tuple | None:
    conn = get_connection()
    try:
        filtro_ativo = "AND c.ativo = 1" if somente_ativa else ""
        return conn.execute(
            f"""
            SELECT c.id, c.nome, c.tipo, c.saldo_inicial, c.ativo,
                   {SALDO_ATUAL_SQL} AS saldo_atual
            FROM contas c
            WHERE c.id = ? AND c.usuario_id = ? {filtro_ativo}
            """,
            (conta_id, usuario_id),
        ).fetchone()
    finally:
        conn.close()


def atualizar_conta(
    conta_id: int,
    nome: str,
    tipo: str,
    saldo_inicial: float,
    usuario_id: int,
) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE contas
            SET nome = ?, tipo = ?, saldo_inicial = ?
            WHERE id = ? AND usuario_id = ?
            """,
            (nome, tipo, saldo_inicial, conta_id, usuario_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def alterar_status_conta(conta_id: int, ativo: bool, usuario_id: int) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE contas SET ativo = ? WHERE id = ? AND usuario_id = ?",
            (int(ativo), conta_id, usuario_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
