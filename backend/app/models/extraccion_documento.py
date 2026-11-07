from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Integer,
    Numeric,
    ForeignKey,
    DateTime,
    String,
    func
)

from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.core.base import Base


class ExtraccionDocumento(Base):

    __tablename__ = "extraccion_documentos"

    id_extraccion: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    id_documento: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("documentos.id_documento")
    )

    id_archivo: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("documento_archivos.id_archivo")
    )

    id_modelo: Mapped[int] = mapped_column(
        BigInteger
    )

    json_resultado: Mapped[dict] = mapped_column(
        JSONB
    )

    estado_validacion: Mapped[str] = mapped_column(
        String(50)
    )

    metrica_confianza: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )

    tiempo_procesamiento_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )