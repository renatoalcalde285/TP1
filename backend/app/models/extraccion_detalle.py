from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    Numeric,
    Boolean,
    ForeignKey,
    DateTime,
    func
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.core.base import Base


class ExtraccionDetalle(Base):

    __tablename__ = "extraccion_detalle"

    id_detalle: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    id_extraccion: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "extraccion_documentos.id_extraccion"
        )
    )

    campo: Mapped[str] = mapped_column(
        String(150)
    )

    valor_extraido: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    valor_corregido: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    confianza: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )

    revisado: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    observacion: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now()
    )