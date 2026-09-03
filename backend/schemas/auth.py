from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    usuario: str = Field(min_length=2, max_length=50)
    email: EmailStr
    senha: str = Field(min_length=6)
    tipo_perfil: str = Field(default="Apenas Financeiro")


class UserResponse(BaseModel):
    id: int
    usuario: str
    email: EmailStr
    tipo_perfil: str
