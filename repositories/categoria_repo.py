from database.connection import get_connection

def criar_categoria(nome: str, usuario_id: int) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO categorias (nome, usuario_id)
        VALUES (?, ?)
    """, (nome.strip(), usuario_id))
    categoria_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return categoria_id

def listar_categorias(usuario_id: int) -> list[tuple]:
    """Retorna lista de (id, nome)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome FROM categorias
        WHERE usuario_id = ?
        ORDER BY nome
    """, (usuario_id,))
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def deletar_categoria(categoria_id: int, usuario_id: int):
    conn = get_connection()
    cursor = conn.execute("""
        DELETE FROM categorias
        WHERE id = ? AND usuario_id = ?
    """, (categoria_id, usuario_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def renomear_categoria(categoria_id: int, novo_nome: str, usuario_id: int):
    conn = get_connection()
    cursor = conn.execute("""
        UPDATE categorias SET nome = ?
        WHERE id = ? AND usuario_id = ?
    """, (novo_nome.strip(), categoria_id, usuario_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0
