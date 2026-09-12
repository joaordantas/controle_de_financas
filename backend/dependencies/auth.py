from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, status

from services.session_service import (
    AuthenticatedUser,
    autenticar_sessao,
    validar_csrf_service,
)


def get_current_user(
    session_token: Annotated[str | None, Cookie(alias="nivra_session")] = None,
) -> AuthenticatedUser:
    current_user = autenticar_sessao(session_token)
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessao ausente, expirada ou revogada.",
        )
    return current_user


def get_current_user_with_csrf(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    csrf_header: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    csrf_cookie: Annotated[str | None, Cookie(alias="nivra_csrf")] = None,
) -> AuthenticatedUser:
    if not validar_csrf_service(current_user, csrf_header, csrf_cookie):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token CSRF ausente ou invalido.",
        )
    return current_user


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]
CurrentUserCsrf = Annotated[AuthenticatedUser, Depends(get_current_user_with_csrf)]
