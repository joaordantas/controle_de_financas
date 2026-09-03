from fastapi import APIRouter, HTTPException, Query, status

from backend.schemas.sales import (
    ClientInstallmentsResponse,
    InstallmentCreate,
    InstallmentCreateResponse,
    PaymentResponse,
    SaleCreate,
    SaleResponse,
)
from services.vendas_service import (
    adicionar_parcelas_para_venda,
    criar_venda_service,
    listar_clientes_service,
    listar_parcelas_por_cliente_formatadas,
    listar_vendas_formatadas,
    registrar_pagamento_parcela_service,
)

router = APIRouter(tags=["sales"])


@router.get("/sales", response_model=list[SaleResponse])
def list_sales(usuario_id: int = Query(..., ge=1)) -> list[SaleResponse]:
    return [SaleResponse(**item) for item in listar_vendas_formatadas(usuario_id)]


@router.post("/sales", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(payload: SaleCreate) -> SaleResponse:
    try:
        venda = criar_venda_service(
            payload.cliente,
            payload.tipo,
            payload.valor_total,
            payload.comentario,
            payload.data,
            payload.usuario_id,
        )
        return SaleResponse(**venda)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/sales/clients", response_model=list[str])
def list_clients(usuario_id: int = Query(..., ge=1)) -> list[str]:
    return listar_clientes_service(usuario_id)


@router.get("/installments/by-client", response_model=ClientInstallmentsResponse)
def list_installments_by_client(
    usuario_id: int = Query(..., ge=1),
    cliente: str = Query(..., min_length=1),
) -> ClientInstallmentsResponse:
    dados = listar_parcelas_por_cliente_formatadas(cliente, usuario_id)
    return ClientInstallmentsResponse(**dados)


@router.post("/installments", response_model=InstallmentCreateResponse, status_code=status.HTTP_201_CREATED)
def create_installments(payload: InstallmentCreate) -> InstallmentCreateResponse:
    try:
        resultado = adicionar_parcelas_para_venda(
            payload.venda_id,
            payload.quantidade,
            payload.valor,
            payload.status,
            payload.data,
            payload.usuario_id,
        )
        return InstallmentCreateResponse(**resultado)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/installments/{parcela_id}/pay", response_model=PaymentResponse)
def pay_installment(parcela_id: int, usuario_id: int = Query(..., ge=1)) -> PaymentResponse:
    sucesso = registrar_pagamento_parcela_service(parcela_id, usuario_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Parcela nao encontrada ou ja paga.")
    return PaymentResponse(message="Parcela paga e lancada no financeiro com sucesso.")
