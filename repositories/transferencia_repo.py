from database.connection import get_connection


def criar_transferencia(
    conta_origem_id: int,
    conta_destino_id: int,
    valor: float,
    descricao: str | None,
    data: str,
    usuario_id: int,
) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO transferencias (
                conta_origem_id, conta_destino_id, valor, descricao, data, usuario_id
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (conta_origem_id, conta_destino_id, valor, descricao, data, usuario_id),
        )
        conn.commit()
        return int(cursor.lastrowid)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def listar_transferencias(usuario_id: int) -> list[tuple]:
    conn = get_connection()
    try:
        return conn.execute(
            """
            SELECT
                tr.id,
                tr.conta_origem_id,
                origem.nome,
                tr.conta_destino_id,
                destino.nome,
                tr.valor,
                tr.descricao,
                tr.data
            FROM transferencias tr
            INNER JOIN contas origem ON origem.id = tr.conta_origem_id
            INNER JOIN contas destino ON destino.id = tr.conta_destino_id
            WHERE tr.usuario_id = ?
            ORDER BY tr.data DESC, tr.id DESC
            """,
            (usuario_id,),
        ).fetchall()
    finally:
        conn.close()
