from pydantic import BaseModel


class ProfitSummary(BaseModel):
    entrada: float
    saida: float
    lucro: float


class ReceivableTotal(BaseModel):
    total: float


class ClientReceivable(BaseModel):
    cliente: str
    valor_pendente: float
