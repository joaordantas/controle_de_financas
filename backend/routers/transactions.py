from fastapi import APIRouter, HTTPException, Query, status

from backend.schemas.transactions import (
    TransactionCreate,
    TransactionListItem,
    TransactionSummary,
    TransactionUpdate,
)
from services.transacao_service import (
    atualizar_transacao_service,
    criar_transacao_service,
    deletar_transacao_service,
    listar_transacoes_formatadas,
    obter_resumo_financeiro,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionListItem])
def list_transactions(usuario_id: int = Query(..., ge=1)) -> list[TransactionListItem]:
    dados = listar_transacoes_formatadas(usuario_id)
    return [TransactionListItem(**item) for item in dados]


@router.post("", response_model=TransactionListItem, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate) -> TransactionListItem:
    try:
        transacao = criar_transacao_service(
            payload.valor,
            payload.tipo,
            payload.categoria_id,
            payload.comentario,
            payload.data,
            payload.usuario_id,
            payload.conta_id,
        )
        return TransactionListItem(**transacao)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{transacao_id}", response_model=TransactionListItem)
def update_transaction(
    transacao_id: int,
    payload: TransactionUpdate,
) -> TransactionListItem:
    try:
        transacao = atualizar_transacao_service(
            transacao_id,
            payload.valor,
            payload.tipo,
            payload.categoria_id,
            payload.comentario,
            payload.data,
            payload.usuario_id,
            payload.conta_id,
        )
        return TransactionListItem(**transacao)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{transacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transacao_id: int,
    usuario_id: int = Query(..., ge=1),
) -> None:
    if not deletar_transacao_service(transacao_id, usuario_id):
        raise HTTPException(status_code=404, detail="Transacao nao encontrada.")


@router.get("/summary", response_model=TransactionSummary)
def get_summary(usuario_id: int = Query(..., ge=1)) -> TransactionSummary:
    return TransactionSummary(**obter_resumo_financeiro(usuario_id))
