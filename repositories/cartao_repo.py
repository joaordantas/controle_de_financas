from database.connection import get_connection


CARD_SELECT = """
    SELECT c.id, c.usuario_id, c.nome, c.limite_total,
           c.dia_fechamento, c.dia_vencimento, c.ativo,
           COALESCE((
               SELECT SUM(cp.valor)
               FROM compras_cartao cp
               JOIN faturas f ON f.id = cp.fatura_id
               LEFT JOIN pagamentos_fatura pf ON pf.fatura_id = f.id
               WHERE cp.cartao_id = c.id AND pf.id IS NULL
           ), 0) AS limite_utilizado
    FROM cartoes c
"""


INVOICE_SELECT = """
    SELECT f.id, f.cartao_id, c.nome, f.ano_referencia, f.mes_referencia,
           f.data_inicio, f.data_fechamento, f.data_vencimento,
           COALESCE(SUM(cp.valor), 0) AS valor_total,
           COALESCE(MAX(pf.valor), 0) AS valor_pago,
           MAX(pf.data) AS data_pagamento,
           MAX(pf.conta_id) AS conta_pagamento_id,
           MAX(conta.nome) AS conta_pagamento,
           COUNT(cp.id) AS quantidade_compras
    FROM faturas f
    JOIN cartoes c ON c.id = f.cartao_id
    LEFT JOIN compras_cartao cp ON cp.fatura_id = f.id
    LEFT JOIN pagamentos_fatura pf ON pf.fatura_id = f.id
    LEFT JOIN contas conta ON conta.id = pf.conta_id
"""


PURCHASE_SELECT = """
    SELECT cp.id, cp.cartao_id, c.nome, cp.fatura_id, cp.valor,
           cp.descricao, cp.categoria_id,
           COALESCE(cat.nome, 'Sem categoria'), cp.data
    FROM compras_cartao cp
    JOIN cartoes c ON c.id = cp.cartao_id
    LEFT JOIN categorias cat ON cat.id = cp.categoria_id
"""


def criar_cartao(
    usuario_id: int,
    nome: str,
    limite_total: float,
    dia_fechamento: int,
    dia_vencimento: int,
) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO cartoes (
                usuario_id, nome, limite_total, dia_fechamento, dia_vencimento
            ) VALUES (?, ?, ?, ?, ?) RETURNING id
            """,
            (usuario_id, nome, limite_total, dia_fechamento, dia_vencimento),
        )
        cartao_id = int(cursor.fetchone()[0])
        conn.commit()
        return cartao_id
    finally:
        conn.close()


def listar_cartoes(usuario_id: int, incluir_inativos: bool = True) -> list[tuple]:
    conn = get_connection()
    try:
        filtro = "" if incluir_inativos else "AND c.ativo = TRUE"
        return conn.execute(
            f"""{CARD_SELECT}
            WHERE c.usuario_id = ? {filtro}
            ORDER BY c.ativo DESC, LOWER(c.nome)
            """,
            (usuario_id,),
        ).fetchall()
    finally:
        conn.close()


def buscar_cartao(cartao_id: int, usuario_id: int, somente_ativo: bool = False) -> tuple | None:
    conn = get_connection()
    try:
        filtro = "AND c.ativo = TRUE" if somente_ativo else ""
        return conn.execute(
            f"""{CARD_SELECT}
            WHERE c.id = ? AND c.usuario_id = ? {filtro}
            """,
            (cartao_id, usuario_id),
        ).fetchone()
    finally:
        conn.close()


def atualizar_cartao(
    cartao_id: int,
    usuario_id: int,
    nome: str,
    limite_total: float,
    dia_fechamento: int,
    dia_vencimento: int,
) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE cartoes
            SET nome = ?, limite_total = ?, dia_fechamento = ?, dia_vencimento = ?,
                atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ? AND usuario_id = ?
            """,
            (nome, limite_total, dia_fechamento, dia_vencimento, cartao_id, usuario_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def alterar_status_cartao(cartao_id: int, usuario_id: int, ativo: bool) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE cartoes SET ativo = ?, atualizado_em = CURRENT_TIMESTAMP
            WHERE id = ? AND usuario_id = ?
            """,
            (ativo, cartao_id, usuario_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def garantir_fatura(
    cartao_id: int,
    usuario_id: int,
    ano_referencia: int,
    mes_referencia: int,
    data_inicio: str,
    data_fechamento: str,
    data_vencimento: str,
) -> int:
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO faturas (
                cartao_id, usuario_id, ano_referencia, mes_referencia,
                data_inicio, data_fechamento, data_vencimento
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (cartao_id, ano_referencia, mes_referencia) DO NOTHING
            """,
            (
                cartao_id,
                usuario_id,
                ano_referencia,
                mes_referencia,
                data_inicio,
                data_fechamento,
                data_vencimento,
            ),
        )
        fatura = conn.execute(
            """
            SELECT id FROM faturas
            WHERE cartao_id = ? AND usuario_id = ?
              AND ano_referencia = ? AND mes_referencia = ?
            """,
            (cartao_id, usuario_id, ano_referencia, mes_referencia),
        ).fetchone()
        conn.commit()
        return int(fatura[0])
    finally:
        conn.close()


def listar_faturas(cartao_id: int, usuario_id: int) -> list[tuple]:
    conn = get_connection()
    try:
        return conn.execute(
            f"""{INVOICE_SELECT}
            WHERE f.cartao_id = ? AND f.usuario_id = ?
            GROUP BY f.id, c.nome
            ORDER BY f.ano_referencia DESC, f.mes_referencia DESC
            """,
            (cartao_id, usuario_id),
        ).fetchall()
    finally:
        conn.close()


def buscar_fatura(fatura_id: int, usuario_id: int) -> tuple | None:
    conn = get_connection()
    try:
        return conn.execute(
            f"""{INVOICE_SELECT}
            WHERE f.id = ? AND f.usuario_id = ?
            GROUP BY f.id, c.nome
            """,
            (fatura_id, usuario_id),
        ).fetchone()
    finally:
        conn.close()


def buscar_fatura_periodo(
    cartao_id: int, usuario_id: int, ano_referencia: int, mes_referencia: int
) -> tuple | None:
    conn = get_connection()
    try:
        return conn.execute(
            f"""{INVOICE_SELECT}
            WHERE f.cartao_id = ? AND f.usuario_id = ?
              AND f.ano_referencia = ? AND f.mes_referencia = ?
            GROUP BY f.id, c.nome
            """,
            (cartao_id, usuario_id, ano_referencia, mes_referencia),
        ).fetchone()
    finally:
        conn.close()


def listar_compras_fatura(fatura_id: int, usuario_id: int) -> list[tuple]:
    conn = get_connection()
    try:
        return conn.execute(
            f"""{PURCHASE_SELECT}
            WHERE cp.fatura_id = ? AND cp.usuario_id = ?
            ORDER BY cp.data DESC, cp.id DESC
            """,
            (fatura_id, usuario_id),
        ).fetchall()
    finally:
        conn.close()


def buscar_compra(compra_id: int, usuario_id: int) -> tuple | None:
    conn = get_connection()
    try:
        return conn.execute(
            f"""{PURCHASE_SELECT}
            WHERE cp.id = ? AND cp.usuario_id = ?
            """,
            (compra_id, usuario_id),
        ).fetchone()
    finally:
        conn.close()


def criar_compra(
    cartao_id: int,
    fatura_id: int,
    usuario_id: int,
    valor: float,
    descricao: str,
    categoria_id: int | None,
    data: str,
) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO compras_cartao (
                cartao_id, fatura_id, usuario_id, valor, descricao, categoria_id, data
            ) VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id
            """,
            (cartao_id, fatura_id, usuario_id, valor, descricao, categoria_id, data),
        )
        compra_id = int(cursor.fetchone()[0])
        conn.commit()
        return compra_id
    finally:
        conn.close()


def atualizar_compra(
    compra_id: int,
    usuario_id: int,
    cartao_id: int,
    fatura_id: int,
    valor: float,
    descricao: str,
    categoria_id: int | None,
    data: str,
) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            UPDATE compras_cartao
            SET cartao_id = ?, fatura_id = ?, valor = ?, descricao = ?,
                categoria_id = ?, data = ?, atualizada_em = CURRENT_TIMESTAMP
            WHERE id = ? AND usuario_id = ?
            """,
            (cartao_id, fatura_id, valor, descricao, categoria_id, data, compra_id, usuario_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def deletar_compra(compra_id: int, usuario_id: int) -> bool:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM compras_cartao WHERE id = ? AND usuario_id = ?",
            (compra_id, usuario_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def pagar_fatura_atomico(
    fatura_id: int,
    conta_id: int,
    usuario_id: int,
    valor: float,
    data: str,
) -> int:
    conn = get_connection()
    try:
        conn.lock_row("faturas", "id", fatura_id)
        fatura = conn.execute(
            "SELECT id FROM faturas WHERE id = ? AND usuario_id = ?",
            (fatura_id, usuario_id),
        ).fetchone()
        conta = conn.execute(
            "SELECT id FROM contas WHERE id = ? AND usuario_id = ? AND ativo = TRUE",
            (conta_id, usuario_id),
        ).fetchone()
        pagamento = conn.execute(
            "SELECT id FROM pagamentos_fatura WHERE fatura_id = ?",
            (fatura_id,),
        ).fetchone()
        if fatura is None or conta is None or pagamento is not None:
            conn.rollback()
            return 0
        cursor = conn.execute(
            """
            INSERT INTO pagamentos_fatura (fatura_id, conta_id, usuario_id, valor, data)
            VALUES (?, ?, ?, ?, ?) RETURNING id
            """,
            (fatura_id, conta_id, usuario_id, valor, data),
        )
        pagamento_id = int(cursor.fetchone()[0])
        conn.commit()
        return pagamento_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
