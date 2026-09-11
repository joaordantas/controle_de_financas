from database.connection import get_connection


def lucro_por_periodo(data_inicio: str, data_fim: str, usuario_id: int) -> dict:
    conn = get_connection()
    try:
        transacoes = conn.execute("""
            SELECT tipo, SUM(valor)
            FROM transacoes
            WHERE usuario_id = ?
                AND data BETWEEN ? AND ?
            GROUP BY tipo
        """, (usuario_id, data_inicio, data_fim)).fetchall()

        resultado = {"entrada": 0.0, "saida": 0.0}
        for tipo, total in transacoes:
            resultado[tipo] = float(total or 0)

        compras_cartao = conn.execute("""
            SELECT COALESCE(SUM(valor), 0)
            FROM compras_cartao
            WHERE usuario_id = ? AND data BETWEEN ? AND ?
        """, (usuario_id, data_inicio, data_fim)).fetchone()
        resultado["saida"] += float(compras_cartao[0] if compras_cartao else 0)
        resultado["lucro"] = resultado["entrada"] - resultado["saida"]
        return resultado
    finally:
        conn.close()


def total_a_receber(usuario_id: int) -> float:
    conn = get_connection()
    try:
        resultado = conn.execute("""
            SELECT SUM(valor)
            FROM parcelas
            WHERE usuario_id = ? AND status = 'pendente'
        """, (usuario_id,)).fetchone()
        return float(resultado[0] if resultado and resultado[0] is not None else 0)
    finally:
        conn.close()


def a_receber_por_cliente(usuario_id: int) -> list:
    conn = get_connection()
    try:
        return conn.execute("""
            SELECT vendas.cliente, SUM(parcelas.valor) AS pendente
            FROM parcelas
            JOIN vendas ON parcelas.venda_id = vendas.id
            WHERE parcelas.usuario_id = ? AND parcelas.status = 'pendente'
            GROUP BY vendas.cliente
            ORDER BY pendente DESC
        """, (usuario_id,)).fetchall()
    finally:
        conn.close()
