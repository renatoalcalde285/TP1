from fastapi import Depends
from fastapi import HTTPException

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from jose import JWTError
from jose import jwt

from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.core.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM
)

from app.models.usuario import Usuario


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:

            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.id_usuario == int(user_id)
        )
        .first()
    )

    if usuario is None:

        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )

    return usuario


def require_role(*allowed_roles):

    def role_checker(
        current_user: Usuario = Depends(
            get_current_user
        )
    ):

        user_role = current_user.rol

        if hasattr(user_role, "value"):
            user_role = user_role.value

        if user_role not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail="No tiene permisos para acceder a este recurso"
            )

        return current_user

    return role_checker