from sqlite3 import IntegrityError

from fastapi import APIRouter, HTTPException, Query, status

from backend.schemas.accounts import (
    AccountCreate,
    AccountResponse,
    AccountPrimaryUpdate,
    AccountStatusUpdate,
    AccountUpdate,
    TransferCreate,
    TransferListItem,
    TransferResponse,
    TransferUpdate,
)
from services.conta_service import (
    alterar_status_conta_service,
    atualizar_conta_service,
    criar_conta_service,
    listar_contas_formatadas,
    definir_conta_principal_service,
)
from services.transferencia_service import (
    atualizar_transferencia_service,
    criar_transferencia_service,
    deletar_transferencia_service,
    listar_transferencias_formatadas,
)

router = APIRouter(tags=["accounts"])


@router.get("/accounts", response_model=list[AccountResponse])
def list_accounts(
    usuario_id: int = Query(..., ge=1),
    incluir_inativas: bool = Query(False),
) -> list[AccountResponse]:
    return [
        AccountResponse(**conta)
        for conta in listar_contas_formatadas(usuario_id, incluir_inativas)
    ]


@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate) -> AccountResponse:
    try:
        return AccountResponse(
            **criar_conta_service(
                payload.nome,
                payload.tipo,
                payload.saldo_inicial,
                payload.usuario_id,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Ja existe uma conta com esse nome.") from exc


@router.put("/accounts/{conta_id}", response_model=AccountResponse)
def update_account(conta_id: int, payload: AccountUpdate) -> AccountResponse:
    try:
        return AccountResponse(
            **atualizar_conta_service(
                conta_id,
                payload.nome,
                payload.tipo,
                payload.saldo_inicial,
                payload.usuario_id,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Ja existe uma conta com esse nome.") from exc


@router.patch("/accounts/{conta_id}/status", response_model=AccountResponse)
def update_account_status(conta_id: int, payload: AccountStatusUpdate) -> AccountResponse:
    try:
        return AccountResponse(
            **alterar_status_conta_service(conta_id, payload.ativo, payload.usuario_id)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/accounts/{conta_id}/primary", response_model=AccountResponse)
def update_account_primary(conta_id: int, payload: AccountPrimaryUpdate) -> AccountResponse:
    try:
        return AccountResponse(
            **definir_conta_principal_service(conta_id, payload.usuario_id)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/transfers", response_model=list[TransferListItem])
def list_transfers(usuario_id: int = Query(..., ge=1)) -> list[TransferListItem]:
    return [
        TransferListItem(**transferencia)
        for transferencia in listar_transferencias_formatadas(usuario_id)
    ]


@router.post("/transfers", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def create_transfer(payload: TransferCreate) -> TransferResponse:
    try:
        return TransferResponse(
            **criar_transferencia_service(
                payload.conta_origem_id,
                payload.conta_destino_id,
                payload.valor,
                payload.descricao,
                payload.data,
                payload.usuario_id,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/transfers/{transferencia_id}", response_model=TransferListItem)
def update_transfer(transferencia_id: int, payload: TransferUpdate) -> TransferListItem:
    try:
        return TransferListItem(
            **atualizar_transferencia_service(
                transferencia_id,
                payload.conta_origem_id,
                payload.conta_destino_id,
                payload.valor,
                payload.descricao,
                payload.data,
                payload.usuario_id,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/transfers/{transferencia_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transfer(
    transferencia_id: int,
    usuario_id: int = Query(..., ge=1),
) -> None:
    if not deletar_transferencia_service(transferencia_id, usuario_id):
        raise HTTPException(status_code=404, detail="Transferencia nao encontrada.")
