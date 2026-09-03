from fastapi import APIRouter, Query

from backend.schemas.dashboard import (
    ClientReceivable,
    ProfitSummary,
    ReceivableTotal,
)
from services.dashboard_service import (
    obter_a_receber_por_cliente,
    obter_lucro_por_periodo,
    obter_total_a_receber,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/profit", response_model=ProfitSummary)
def get_profit(
    usuario_id: int = Query(..., ge=1),
    data_inicio: str = Query(...),
    data_fim: str = Query(...),
) -> ProfitSummary:
    return ProfitSummary(**obter_lucro_por_periodo(data_inicio, data_fim, usuario_id))


@router.get("/receivables/total", response_model=ReceivableTotal)
def get_receivables_total(usuario_id: int = Query(..., ge=1)) -> ReceivableTotal:
    return ReceivableTotal(total=obter_total_a_receber(usuario_id))


@router.get("/receivables/by-client", response_model=list[ClientReceivable])
def get_receivables_by_client(usuario_id: int = Query(..., ge=1)) -> list[ClientReceivable]:
    dados = obter_a_receber_por_cliente(usuario_id)
    return [ClientReceivable(**item) for item in dados]
