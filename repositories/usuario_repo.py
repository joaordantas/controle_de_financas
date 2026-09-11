from database.connection import get_connection
from utils.security import hash_senha

def cadastrar_usuario(usuario: str, email: str, senha: str, tipo_perfil: str):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO usuarios (usuario, email, senha, tipo_perfil)
            VALUES (?, ?, ?, ?)
        """, (usuario, email, hash_senha(senha), tipo_perfil))
        conn.commit()
    finally:
        conn.close()

def buscar_usuario_por_email(email: str):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM usuarios WHERE LOWER(email) = LOWER(?)", (email,)
        ).fetchone()
    finally:
        conn.close()

def buscar_perfil(usuario_id: int) -> str | None:
    conn = get_connection()
    try:
        resultado = conn.execute(
            "SELECT tipo_perfil FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        return resultado[0] if resultado else None
    finally:
        conn.close()
