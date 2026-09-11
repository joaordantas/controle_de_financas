from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from backend.schemas.auth import LoginRequest, RegisterRequest, UserResponse
from services.auth_service import login, registrar

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest) -> UserResponse:
    try:
        registrar(payload.usuario, payload.email, payload.senha, payload.tipo_perfil)
        resultado = login(payload.email, payload.senha)
        if resultado is None:
            raise HTTPException(status_code=500, detail="Nao foi possivel carregar o usuario criado.")
        return _user_from_tuple(resultado)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Usuario ou e-mail ja cadastrado.") from exc


@router.post("/login", response_model=UserResponse)
def login_user(payload: LoginRequest) -> UserResponse:
    resultado = login(payload.email, payload.senha)
    if resultado is None:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos.")
    return _user_from_tuple(resultado)


def _user_from_tuple(usuario: tuple) -> UserResponse:
    return UserResponse(
        id=usuario[0],
        usuario=usuario[1],
        email=usuario[2],
        tipo_perfil=usuario[4],
    )
