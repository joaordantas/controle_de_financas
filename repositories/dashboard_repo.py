from database.connection import get_connection

def lucro_por_periodo(data_inicio: str, data_fim: str, usuario_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tipo, SUM(valor)
        FROM transacoes
        WHERE usuario_id = ?
            AND data BETWEEN ? AND ?
        GROUP BY tipo
    """, (usuario_id, data_inicio, data_fim))

    resultado = {"entrada": 0.0, "saida": 0.0}
    for tipo, total in cursor.fetchall():
        resultado[tipo] = total or 0.0

    cursor.execute("""
        SELECT COALESCE(SUM(valor), 0)
        FROM compras_cartao
        WHERE usuario_id = ? AND data BETWEEN ? AND ?
    """, (usuario_id, data_inicio, data_fim))
    resultado["saida"] += cursor.fetchone()[0] or 0.0

    conn.close()
    resultado["lucro"] = resultado["entrada"] - resultado["saida"]
    return resultado

def total_a_receber(usuario_id: int) -> float:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(valor)
        FROM parcelas
        WHERE usuario_id = ? AND status = 'pendente'
    """, (usuario_id,))

    resultado = cursor.fetchone()[0]
    conn.close()
    return resultado or 0.0


def a_receber_por_cliente(usuario_id: int) -> list:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT vendas.cliente, SUM(parcelas.valor) AS pendente
        FROM parcelas
        JOIN vendas ON parcelas.venda_id = vendas.id
        WHERE parcelas.usuario_id = ? AND parcelas.status = 'pendente'
        GROUP BY vendas.cliente
        ORDER BY pendente DESC
    """, (usuario_id,))

    resultado = cursor.fetchall()
    conn.close()
    return resultado
