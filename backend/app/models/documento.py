from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    func
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.core.base import Base

import enum


class EstadoDocumento(str, enum.Enum):

    PENDIENTE = "PENDIENTE"
    PROCESANDO = "PROCESANDO"
    PROCESADO = "PROCESADO"
    EN_REVISION = "EN_REVISION"
    VALIDADO = "VALIDADO"
    RECHAZADO = "RECHAZADO"
    ERROR = "ERROR"


class Documento(Base):

    __tablename__ = "documentos"

    id_documento: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    titulo: Mapped[str | None] = mapped_column(
        String(200)
    )

    descripcion: Mapped[str | None] = mapped_column(
        Text
    )

    estado: Mapped[EstadoDocumento] = mapped_column(
        Enum(EstadoDocumento),
        default=EstadoDocumento.PENDIENTE
    )

    id_usuario_carga: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("usuarios.id_usuario")
    )

    id_usuario_valida: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("usuarios.id_usuario"),
        nullable=True
    )

    fecha_carga: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )

    fecha_validacion: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    observaciones: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )