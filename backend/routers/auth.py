import secrets
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError

from backend.dependencies.auth import CurrentUser, CurrentUserCsrf
from backend.schemas.auth import CsrfResponse, LoginRequest, RegisterRequest, UserResponse
from services.auth_service import login, registrar
from services.session_service import (
    CSRF_COOKIE,
    SESSION_COOKIE,
    criar_sessao_service,
    cookie_is_secure,
    revogar_sessao_service,
    rotacionar_csrf_service,
    session_duration_seconds,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_csrf_cookie(response: Response, csrf_token: str) -> None:
    response.set_cookie(
        CSRF_COOKIE,
        csrf_token,
        max_age=session_duration_seconds(),
        httponly=False,
        secure=cookie_is_secure(),
        samesite="lax",
        path="/",
    )


def _set_session_cookies(response: Response, session_token: str, csrf_token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        session_token,
        max_age=session_duration_seconds(),
        httponly=True,
        secure=cookie_is_secure(),
        samesite="lax",
        path="/",
    )
    _set_csrf_cookie(response, csrf_token)


def _clear_session_cookies(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/", secure=cookie_is_secure(), samesite="lax")
    response.delete_cookie(CSRF_COOKIE, path="/", secure=cookie_is_secure(), samesite="lax")


def _require_public_csrf(
    csrf_header: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    csrf_cookie: Annotated[str | None, Cookie(alias=CSRF_COOKIE)] = None,
) -> None:
    if not csrf_header or not csrf_cookie or not secrets.compare_digest(csrf_header, csrf_cookie):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token CSRF ausente ou invalido.")


@router.get("/csrf", response_model=CsrfResponse)
def get_csrf_token(request: Request, response: Response) -> CsrfResponse:
    csrf_token = rotacionar_csrf_service(
        request.cookies.get(SESSION_COOKIE),
        request.cookies.get(CSRF_COOKIE),
    )
    _set_csrf_cookie(response, csrf_token)
    return CsrfResponse(csrf_token=csrf_token)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(_require_public_csrf)],
)
def register_user(
    payload: RegisterRequest,
    response: Response,
    csrf_token: Annotated[str, Cookie(alias=CSRF_COOKIE)],
) -> UserResponse:
    try:
        registrar(payload.usuario, payload.email, payload.senha, payload.tipo_perfil)
        resultado = login(payload.email, payload.senha)
        if resultado is None:
            raise HTTPException(status_code=500, detail="Nao foi possivel carregar o usuario criado.")
        session_token = criar_sessao_service(int(resultado[0]), csrf_token)
        _set_session_cookies(response, session_token, csrf_token)
        return _user_from_tuple(resultado)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Usuario ou e-mail ja cadastrado.") from exc


@router.post(
    "/login",
    response_model=UserResponse,
    dependencies=[Depends(_require_public_csrf)],
)
def login_user(
    payload: LoginRequest,
    response: Response,
    csrf_token: Annotated[str, Cookie(alias=CSRF_COOKIE)],
) -> UserResponse:
    resultado = login(payload.email, payload.senha)
    if resultado is None:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos.")
    session_token = criar_sessao_service(int(resultado[0]), csrf_token)
    _set_session_cookies(response, session_token, csrf_token)
    return _user_from_tuple(resultado)


@router.get("/me", response_model=UserResponse)
def current_user(current_user: CurrentUser) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        usuario=current_user.usuario,
        email=current_user.email,
        tipo_perfil=current_user.tipo_perfil,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(request: Request, response: Response, current_user: CurrentUserCsrf) -> None:
    del current_user
    revogar_sessao_service(request.cookies.get(SESSION_COOKIE))
    _clear_session_cookies(response)


def _user_from_tuple(usuario: tuple) -> UserResponse:
    return UserResponse(
        id=usuario[0],
        usuario=usuario[1],
        email=usuario[2],
        tipo_perfil=usuario[4],
    )
