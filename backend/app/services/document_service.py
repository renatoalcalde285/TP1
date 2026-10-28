from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.core.storage import (
    s3_client,
    BUCKET_NAME
)

from app.models.documento import (
    Documento,
    EstadoDocumento
)

from app.models.documento_archivo import DocumentoArchivo


class DocumentService:

    ALLOWED_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".tif",
        ".tiff"
    }

    @staticmethod
    def validate_file(file):

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Archivo inválido"
            )

        extension = Path(file.filename).suffix.lower()

        if extension not in DocumentService.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Formato no permitido. "
                    "Formatos válidos: "
                    "PNG, JPG, JPEG, TIF, TIFF"
                )
            )

    @staticmethod
    async def upload_file(
        db: Session,
        file,
        usuario_id: int
    ):

        DocumentService.validate_file(file)

        # Leer archivo

        content = await file.read()

        if len(content) == 0:
            raise HTTPException(
                status_code=400,
                detail="El archivo está vacío"
            )

        # Crear documento

        documento = Documento(
            titulo=file.filename,
            estado=EstadoDocumento.PENDIENTE,
            id_usuario_carga=usuario_id
        )

        db.add(documento)
        db.commit()
        db.refresh(documento)

        # Generar ruta en RustFS

        extension = Path(file.filename).suffix.lower()

        object_name = (
            f"{documento.id_documento}/"
            f"{uuid4()}{extension}"
        )

        # Subir a RustFS

        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=object_name,
            Body=content
        )

        # Registrar metadata

        archivo = DocumentoArchivo(
            id_documento=documento.id_documento,
            numero_pagina=1,
            ruta_almacenamiento=object_name,
            nombre_original=file.filename,
            formato=file.content_type,
            tamano_bytes=len(content)
        )

        db.add(archivo)
        db.commit()
        db.refresh(archivo)

        return {
            "id_documento": documento.id_documento,
            "id_archivo": archivo.id_archivo,
            "estado": documento.estado.value,
            "ruta_almacenamiento": object_name,
            "nombre_archivo": file.filename
        }

    @staticmethod
    def get_document_status(
        db: Session,
        document_id: int
    ):

        documento = (
            db.query(Documento)
            .filter(
                Documento.id_documento == document_id
            )
            .first()
        )

        if not documento:

            raise HTTPException(
                status_code=404,
                detail="Documento no encontrado"
            )

        return {
            "id_documento": documento.id_documento,
            "titulo": documento.titulo,
            "estado": documento.estado.value,
            "fecha_carga": documento.fecha_carga
        }