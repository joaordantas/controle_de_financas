from fastapi import APIRouter, Query

from backend.dependencies.auth import CurrentUser
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
    current_user: CurrentUser,
    data_inicio: str = Query(...),
    data_fim: str = Query(...),
) -> ProfitSummary:
    return ProfitSummary(**obter_lucro_por_periodo(data_inicio, data_fim, current_user.id))


@router.get("/receivables/total", response_model=ReceivableTotal)
def get_receivables_total(current_user: CurrentUser) -> ReceivableTotal:
    return ReceivableTotal(total=obter_total_a_receber(current_user.id))


@router.get("/receivables/by-client", response_model=list[ClientReceivable])
def get_receivables_by_client(current_user: CurrentUser) -> list[ClientReceivable]:
    dados = obter_a_receber_por_cliente(current_user.id)
    return [ClientReceivable(**item) for item in dados]
