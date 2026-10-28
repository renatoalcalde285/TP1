from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    ForeignKey
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.core.base import Base


class DocumentoArchivo(Base):
    __tablename__ = "documento_archivos"

    id_archivo: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True
    )

    id_documento: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("documentos.id_documento")
    )

    numero_pagina: Mapped[int] = mapped_column(
        Integer
    )

    ruta_almacenamiento: Mapped[str] = mapped_column(
        String(500)
    )

    nombre_original: Mapped[str] = mapped_column(
        String(255)
    )

    formato: Mapped[str | None] = mapped_column(
        String(25)
    )

    tamano_bytes: Mapped[int | None] = mapped_column(
        BigInteger
    )

    hash_archivo: Mapped[str | None] = mapped_column(
        String(255)
    )