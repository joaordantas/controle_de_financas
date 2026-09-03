from typing import Literal

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    valor: float = Field(gt=0)
    tipo: Literal["entrada", "saida"]
    categoria_id: int | None = Field(default=None, ge=1)
    comentario: str | None = Field(default=None, max_length=255)
    data: str
    usuario_id: int = Field(ge=1)


class TransactionListItem(BaseModel):
    id: int
    valor: float
    tipo: str
    categoria: str
    comentario: str | None = None
    data: str


class TransactionSummary(BaseModel):
    entradas: float
    saidas: float
    saldo: float
