from typing import Literal

from pydantic import BaseModel, Field


class SaleCreate(BaseModel):
    cliente: str = Field(min_length=1, max_length=100)
    tipo: str = Field(min_length=1, max_length=50)
    valor_total: float = Field(gt=0)
    comentario: str | None = Field(default=None, max_length=255)
    data: str
    usuario_id: int = Field(ge=1)


class SaleResponse(BaseModel):
    id: int
    cliente: str
    tipo: str
    valor_total: float
    comentario: str | None = None
    data: str


class InstallmentCreate(BaseModel):
    venda_id: int = Field(ge=1)
    quantidade: int = Field(gt=0)
    valor: float = Field(gt=0)
    status: Literal["pendente", "pago"]
    data: str
    usuario_id: int = Field(ge=1)


class InstallmentItem(BaseModel):
    id: int
    venda_id: int
    valor: float
    status: str
    data: str


class ClientInstallmentsSummary(BaseModel):
    total_pago: float
    valor_total_vendas: float
    ainda_falta: float


class ClientInstallmentsResponse(BaseModel):
    cliente: str
    parcelas: list[InstallmentItem]
    resumo: ClientInstallmentsSummary


class InstallmentCreateResponse(BaseModel):
    venda_id: int
    quantidade: int
    valor_parcela: float
    status: str
    data: str
    valor_total_venda: float
    valor_ja_parcelado: float


class PaymentResponse(BaseModel):
    message: str
