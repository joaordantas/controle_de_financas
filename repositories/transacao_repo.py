from database.connection import get_connection


TRANSACTION_SELECT = """
    SELECT t.id, t.valor, t.tipo, t.categoria_id,
           COALESCE(c.nome, 'Sem categoria') AS categoria,
           t.comentario, t.data, t.conta_id,
           COALESCE(conta.nome, 'Sem conta') AS conta
    FROM transacoes t
    LEFT JOIN categorias c ON c.id = t.categoria_id
    LEFT JOIN contas conta ON conta.id = t.conta_id
"""


def adicionar_transacao(
    valor: float,
    tipo: str,
    categoria_id: int | None,
    comentario: str | None,
    data: str,
    usuario_id: int,
    conta_id: int | None = None,
) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO transacoes (
                valor, tipo, categoria_id, comentario, data, usuario_id, conta_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id
            """,
            (valor, tipo, categoria_id, comentario, data, usuario_id, conta_id),
        )
        transacao_id = int(cursor.fetchone()[0])
        conn.commit()
        return transacao_id
    finally:
        conn.close()


def listar_transacoes(usuario_id: int) -> list[tuple]:
    conn = get_connection()
    try:
        return conn.execute(
            f"""
            {TRANSACTION_SELECT}
            WHERE t.usuario_id = ?
            ORDER BY t.data DESC, t.id DESC
            """,
            (usuario_id,),
        ).fetchall()
    finally:
        conn.close()


def buscar_transacao_por_id(transacao_id: int, usuario_id: int) -> tuple | None:
    conn = get_connection()
    try:
        return conn.execute(
            f"""{TRANSACTION_SELECT}
            WHERE t.id = ? AND t.usuario_id = ?
            """,
            (transacao_id, usuario_id),
        ).fetchone()
    finally:
        conn.close()


def atualizar_transacao(
    transacao_id: int,
    valor: float,
    tipo: str,
    categoria_id: int | None,
    comentario: str | None,
    data: str,
    conta_id: int | None,
    usuario_id: int,
) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE transacoes
            SET valor = ?, tipo = ?, categoria_id = ?, comentario = ?, data = ?, conta_id = ?
            WHERE id = ? AND usuario_id = ?
            """,
            (
                valor,
                tipo,
                categoria_id,
                comentario,
                data,
                conta_id,
                transacao_id,
                usuario_id,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def deletar_transacao(transacao_id: int, usuario_id: int) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM transacoes WHERE id = ? AND usuario_id = ?",
            (transacao_id, usuario_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def calcular_resumo(usuario_id: int) -> tuple[float, float, float]:
    conn = get_connection()
    try:
        entradas, saidas_transacoes = conn.execute(
            """
            SELECT
                COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END), 0),
                COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END), 0)
            FROM transacoes
            WHERE usuario_id = ?
            """,
            (usuario_id,),
        ).fetchone()
        saidas_cartao = conn.execute(
            "SELECT COALESCE(SUM(valor), 0) FROM compras_cartao WHERE usuario_id = ?",
            (usuario_id,),
        ).fetchone()[0]
        saidas = float(saidas_transacoes) + float(saidas_cartao)
        return float(entradas), float(saidas), float(entradas - saidas)
    finally:
        conn.close()
