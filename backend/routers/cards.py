from sqlalchemy.exc import IntegrityError

from fastapi import APIRouter, HTTPException, Query, status

from backend.schemas.cards import (
    CardCreate,
    CardPurchaseCreate,
    CardPurchaseResponse,
    CardPurchaseUpdate,
    CardResponse,
    CardStatusUpdate,
    CardUpdate,
    InvoiceDetail,
    InvoicePaymentCreate,
    InvoiceSummary,
)
from backend.dependencies.auth import CurrentUser, CurrentUserCsrf
from services.cartao_service import (
    alterar_status_cartao_service,
    atualizar_cartao_service,
    atualizar_compra_service,
    criar_cartao_service,
    criar_compra_service,
    deletar_compra_service,
    listar_cartoes_formatados,
    listar_faturas_service,
    obter_fatura_atual_service,
    obter_fatura_service,
    pagar_fatura_service,
)

router = APIRouter(tags=["cards"])


@router.get("/cards", response_model=list[CardResponse])
def list_cards(
    current_user: CurrentUser, incluir_inativos: bool = Query(True)
) -> list[CardResponse]:
    return [
        CardResponse(**cartao)
        for cartao in listar_cartoes_formatados(current_user.id, incluir_inativos)
    ]


@router.post("/cards", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
def create_card(payload: CardCreate, current_user: CurrentUserCsrf) -> CardResponse:
    try:
        return CardResponse(
            **criar_cartao_service(
                current_user.id,
                payload.nome,
                payload.limite_total,
                payload.dia_fechamento,
                payload.dia_vencimento,
            )
        )
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Ja existe um cartao com esse nome.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/cards/{cartao_id}", response_model=CardResponse)
def update_card(cartao_id: int, payload: CardUpdate, current_user: CurrentUserCsrf) -> CardResponse:
    try:
        return CardResponse(
            **atualizar_cartao_service(
                cartao_id,
                current_user.id,
                payload.nome,
                payload.limite_total,
                payload.dia_fechamento,
                payload.dia_vencimento,
            )
        )
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Ja existe um cartao com esse nome.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/cards/{cartao_id}/status", response_model=CardResponse)
def update_card_status(cartao_id: int, payload: CardStatusUpdate, current_user: CurrentUserCsrf) -> CardResponse:
    try:
        return CardResponse(
            **alterar_status_cartao_service(cartao_id, current_user.id, payload.ativo)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/cards/{cartao_id}/invoices", response_model=list[InvoiceSummary])
def list_card_invoices(
    cartao_id: int, current_user: CurrentUser
) -> list[InvoiceSummary]:
    try:
        return [
            InvoiceSummary(**fatura)
            for fatura in listar_faturas_service(cartao_id, current_user.id)
        ]
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/cards/{cartao_id}/invoices/current", response_model=InvoiceSummary)
def get_current_invoice(
    cartao_id: int, current_user: CurrentUser
) -> InvoiceSummary:
    try:
        return InvoiceSummary(**obter_fatura_atual_service(cartao_id, current_user.id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/invoices/{fatura_id}", response_model=InvoiceDetail)
def get_invoice(fatura_id: int, current_user: CurrentUser) -> InvoiceDetail:
    try:
        return InvoiceDetail(**obter_fatura_service(fatura_id, current_user.id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/card-purchases",
    response_model=CardPurchaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_card_purchase(payload: CardPurchaseCreate, current_user: CurrentUserCsrf) -> CardPurchaseResponse:
    try:
        return CardPurchaseResponse(
            **criar_compra_service(
                payload.cartao_id,
                current_user.id,
                payload.valor,
                payload.descricao,
                payload.categoria_id,
                payload.data,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/card-purchases/{compra_id}", response_model=CardPurchaseResponse)
def update_card_purchase(
    compra_id: int, payload: CardPurchaseUpdate, current_user: CurrentUserCsrf
) -> CardPurchaseResponse:
    try:
        return CardPurchaseResponse(
            **atualizar_compra_service(
                compra_id,
                payload.cartao_id,
                current_user.id,
                payload.valor,
                payload.descricao,
                payload.categoria_id,
                payload.data,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/card-purchases/{compra_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_card_purchase(
    compra_id: int, current_user: CurrentUserCsrf
) -> None:
    try:
        if not deletar_compra_service(compra_id, current_user.id):
            raise HTTPException(status_code=404, detail="Compra nao encontrada.")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/invoices/{fatura_id}/pay", response_model=InvoiceDetail)
def pay_invoice(fatura_id: int, payload: InvoicePaymentCreate, current_user: CurrentUserCsrf) -> InvoiceDetail:
    try:
        return InvoiceDetail(
            **pagar_fatura_service(
                fatura_id, payload.conta_id, current_user.id, payload.data
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
