from typing import Literal

from pydantic import BaseModel, Field


AccountType = Literal["corrente", "poupanca", "digital", "dinheiro", "outro"]


class AccountCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=60)
    tipo: AccountType = "digital"
    saldo_inicial: float = 0
    usuario_id: int = Field(ge=1)


class AccountResponse(BaseModel):
    id: int
    nome: str
    tipo: AccountType
    saldo_inicial: float
    saldo_atual: float
    ativo: bool


class TransferCreate(BaseModel):
    conta_origem_id: int = Field(ge=1)
    conta_destino_id: int = Field(ge=1)
    valor: float = Field(gt=0)
    descricao: str | None = Field(default=None, max_length=255)
    data: str
    usuario_id: int = Field(ge=1)


class TransferResponse(BaseModel):
    id: int
    conta_origem_id: int
    conta_destino_id: int
    valor: float
    descricao: str | None = None
    data: str


class TransferListItem(TransferResponse):
    conta_origem: str
    conta_destino: str
