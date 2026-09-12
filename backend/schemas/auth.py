from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    senha: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    usuario: str = Field(min_length=2, max_length=50)
    email: EmailStr
    senha: str = Field(min_length=6)
    tipo_perfil: str = Field(default="Apenas Financeiro")


class UserResponse(BaseModel):
    id: int
    usuario: str
    email: EmailStr
    tipo_perfil: str


class CsrfResponse(BaseModel):
    csrf_token: str
