from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.security.dependencies import (
    get_current_user
)

from app.schemas.auth import (
    LoginRequest,
    TokenResponse
)

from app.models.usuario import Usuario

from app.security.jwt import (
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    usuario = (
        db.query(Usuario)
        .filter(
            Usuario.email == request.email
        )
        .first()
    )

    if not usuario:

        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    token = create_access_token(
        {
            "sub": str(
                usuario.id_usuario
            )
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
def me(
    current_user: Usuario = Depends(
        get_current_user
    )
):

    return {
        "id_usuario": current_user.id_usuario,
        "nombre": current_user.nombre,
        "email": current_user.email,
        "rol": current_user.rol
    }