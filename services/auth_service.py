import re
from repositories.usuario_repo import cadastrar_usuario, buscar_usuario_por_email, buscar_perfil
from utils.security import verificar_senha

def _validar_email(email: str) -> bool:
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email))

def registrar(usuario: str, email: str, senha: str, tipo_perfil: str):
    email_normalizado = email.strip().lower()
    if not _validar_email(email_normalizado):
        raise ValueError("E-mail inválido. Use o formato: nome@exemplo.com")
    if len(senha) < 6:
        raise ValueError("A senha deve ter pelo menos 6 caracteres.")
    cadastrar_usuario(usuario.strip(), email_normalizado, senha, tipo_perfil)

def login(email: str, senha: str):
    """Retorna a tupla do usuário se credenciais válidas, ou None."""
    usuario = buscar_usuario_por_email(email.strip().lower())
    if usuario is None:
        return None
    senha_hash = usuario[3]
    if verificar_senha(senha, senha_hash):
        return usuario
    return None

def obter_perfil(usuario_id: int) -> str | None:
    return buscar_perfil(usuario_id)
