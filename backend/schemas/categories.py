from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=50)
    usuario_id: int = Field(ge=1)


class CategoryUpdate(BaseModel):
    nome: str = Field(min_length=1, max_length=50)
    usuario_id: int = Field(ge=1)


class CategoryResponse(BaseModel):
    id: int
    nome: str
