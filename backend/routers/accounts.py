from sqlite3 import IntegrityError

from fastapi import APIRouter, HTTPException, Query, status

from backend.schemas.accounts import (
    AccountCreate,
    AccountResponse,
    TransferCreate,
    TransferListItem,
    TransferResponse,
)
from services.conta_service import criar_conta_service, listar_contas_formatadas
from services.transferencia_service import (
    criar_transferencia_service,
    listar_transferencias_formatadas,
)

router = APIRouter(tags=["accounts"])


@router.get("/accounts", response_model=list[AccountResponse])
def list_accounts(usuario_id: int = Query(..., ge=1)) -> list[AccountResponse]:
    return [AccountResponse(**conta) for conta in listar_contas_formatadas(usuario_id)]


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
