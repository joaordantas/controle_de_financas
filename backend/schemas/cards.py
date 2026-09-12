from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


InvoiceStatus = Literal["aberta", "fechada", "paga", "vencida"]


class InvoiceSummary(BaseModel):
    id: int
    cartao_id: int
    cartao: str
    ano_referencia: int
    mes_referencia: int
    data_inicio: str
    data_fechamento: str
    data_vencimento: str
    valor_total: float
    valor_pago: float
    status: InvoiceStatus
    data_pagamento: str | None = None
    conta_pagamento_id: int | None = None
    conta_pagamento: str | None = None
    quantidade_compras: int


class CardCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nome: str = Field(min_length=1, max_length=60)
    limite_total: float = Field(gt=0)
    dia_fechamento: int = Field(ge=1, le=31)
    dia_vencimento: int = Field(ge=1, le=31)


class CardUpdate(CardCreate):
    pass


class CardStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ativo: bool


class CardResponse(BaseModel):
    id: int
    nome: str
    limite_total: float
    limite_utilizado: float
    limite_disponivel: float
    percentual_utilizado: float
    dia_fechamento: int
    dia_vencimento: int
    ativo: bool
    fatura_atual: InvoiceSummary | None = None


class CardPurchaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cartao_id: int = Field(ge=1)
    valor: float = Field(gt=0)
    descricao: str = Field(min_length=1, max_length=255)
    categoria_id: int = Field(ge=1)
    data: str


class CardPurchaseUpdate(CardPurchaseCreate):
    pass


class CardPurchaseResponse(BaseModel):
    id: int
    cartao_id: int
    cartao: str
    fatura_id: int
    valor: float
    descricao: str
    categoria_id: int | None = None
    categoria: str
    data: str


class InvoiceDetail(InvoiceSummary):
    compras: list[CardPurchaseResponse]


class InvoicePaymentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    conta_id: int = Field(ge=1)
    data: str
