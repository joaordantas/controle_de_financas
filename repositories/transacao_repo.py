from database.connection import get_connection

def adicionar_transacao(valor: float, tipo: str, categoria_id: int | None,
                        comentario: str | None, data: str, usuario_id: int,
                        conta_id: int | None = None):
    conn = get_connection()
    conn.execute("""
        INSERT INTO transacoes (
            valor, tipo, categoria_id, comentario, data, usuario_id, conta_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (valor, tipo, categoria_id, comentario, data, usuario_id, conta_id))
    conn.commit()
    conn.close()

def listar_transacoes(usuario_id: int) -> list:
    """Retorna transações com o nome da categoria já resolvido via JOIN."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.valor, t.tipo,
               COALESCE(c.nome, '—') AS categoria,
               t.comentario, t.data,
               t.conta_id,
               COALESCE(conta.nome, 'Sem conta') AS conta
        FROM transacoes t
        LEFT JOIN categorias c ON c.id = t.categoria_id
        LEFT JOIN contas conta ON conta.id = t.conta_id
        WHERE t.usuario_id = ?
        ORDER BY t.data DESC, t.id DESC
    """, (usuario_id,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def calcular_resumo(usuario_id: int) -> tuple[float, float, float]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'entrada' AND usuario_id = ?", (usuario_id,))
    entradas = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE tipo = 'saida' AND usuario_id = ?", (usuario_id,))
    saidas = cursor.fetchone()[0] or 0.0
    conn.close()
    return entradas, saidas, entradas - saidas
