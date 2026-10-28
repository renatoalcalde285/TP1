from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
    Enum
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.core.base import Base

import enum


class RolUsuario(str, enum.Enum):
    ADMINISTRADOR = "ADMINISTRADOR"
    REGISTRADOR = "REGISTRADOR"
    AUDITOR = "AUDITOR"


class Usuario(Base):

    __tablename__ = "usuarios"

    id_usuario: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    nombre: Mapped[str] = mapped_column(
        String(100)
    )

    email: Mapped[str] = mapped_column(
        String(150)
    )

    password_hash: Mapped[str] = mapped_column(
        String(255)
    )

    rol: Mapped[RolUsuario] = mapped_column(
        Enum(RolUsuario)
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )