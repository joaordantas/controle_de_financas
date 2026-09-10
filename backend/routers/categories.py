from fastapi import APIRouter, HTTPException, Query, status
from sqlite3 import IntegrityError

from backend.schemas.categories import CategoryCreate, CategoryResponse, CategoryUpdate
from services.categoria_service import (
    criar_categoria_service,
    deletar_categoria_service,
    listar_categorias_formatadas,
    renomear_categoria_service,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
def list_categories(usuario_id: int = Query(..., ge=1)) -> list[CategoryResponse]:
    return [CategoryResponse(**categoria) for categoria in listar_categorias_formatadas(usuario_id)]


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate) -> CategoryResponse:
    try:
        categoria = criar_categoria_service(payload.nome, payload.usuario_id)
        return CategoryResponse(**categoria)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Nao foi possivel criar a categoria.") from exc


@router.put("/{categoria_id}", response_model=CategoryResponse)
def update_category(categoria_id: int, payload: CategoryUpdate) -> CategoryResponse:
    try:
        categoria = renomear_categoria_service(categoria_id, payload.nome, payload.usuario_id)
        return CategoryResponse(**categoria)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(categoria_id: int, usuario_id: int = Query(..., ge=1)) -> None:
    try:
        removido = deletar_categoria_service(categoria_id, usuario_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if not removido:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada.")
