from repositories.categoria_repo import (
    criar_categoria,
    deletar_categoria,
    listar_categorias,
    renomear_categoria,
)


def listar_categorias_formatadas(usuario_id: int) -> list[dict]:
    categorias = listar_categorias(usuario_id)
    return [{"id": categoria_id, "nome": nome} for categoria_id, nome in categorias]


def criar_categoria_service(nome: str, usuario_id: int) -> dict:
    nome_limpo = nome.strip()
    if not nome_limpo:
        raise ValueError("Digite um nome para a categoria.")
    categoria_id = criar_categoria(nome_limpo, usuario_id)
    return {"id": categoria_id, "nome": nome_limpo}


def renomear_categoria_service(categoria_id: int, novo_nome: str, usuario_id: int) -> dict:
    nome_limpo = novo_nome.strip()
    if not nome_limpo:
        raise ValueError("Digite um novo nome para a categoria.")
    atualizado = renomear_categoria(categoria_id, nome_limpo, usuario_id)
    if not atualizado:
        raise ValueError("Categoria nao encontrada.")
    return {"id": categoria_id, "nome": nome_limpo}


def deletar_categoria_service(categoria_id: int, usuario_id: int) -> bool:
    return deletar_categoria(categoria_id, usuario_id)
