from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    valor: float = Field(gt=0)
    tipo: Literal["entrada", "saida"]
    categoria_id: int | None = Field(default=None, ge=1)
    comentario: str | None = Field(default=None, max_length=255)
    data: str
    conta_id: int | None = Field(default=None, ge=1)


class TransactionUpdate(TransactionCreate):
    pass


class TransactionListItem(BaseModel):
    id: int
    valor: float
    tipo: str
    categoria_id: int | None = None
    categoria: str
    comentario: str | None = None
    data: str
    conta_id: int | None = None
    conta: str = "Sem conta"


class TransactionSummary(BaseModel):
    entradas: float
    saidas: float
    saldo: float
