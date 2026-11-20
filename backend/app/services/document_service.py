from pathlib import Path
from uuid import uuid4
import hashlib

from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.documento_archivo import DocumentoArchivo

from app.core.storage import (
    s3_client,
    BUCKET_NAME
)

from app.models.documento import (  
    Documento,
    EstadoDocumento
)

from app.models.extraccion_documento import (
    ExtraccionDocumento
)

from app.schemas.document_validation import (
    DocumentValidationRequest
)

from app.models.documento_archivo import DocumentoArchivo

from app.models.extraccion_detalle import (
    ExtraccionDetalle
)


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

        hash_archivo = hashlib.sha256(
            content
        ).hexdigest()

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
            tamano_bytes=len(content),
            hash_archivo=hash_archivo
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

    @staticmethod
    def get_document_review(
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

        extraccion = (
            db.query(ExtraccionDocumento)
            .filter(
                ExtraccionDocumento.id_documento
                == document_id
            )
            .order_by(
                ExtraccionDocumento.id_extraccion.desc()
            )
            .first()
        )

        if not extraccion:
            raise HTTPException(
                status_code=404,
                detail="No existe extracción asociada"
            )

        archivo = (
            db.query(DocumentoArchivo)
            .filter(
                DocumentoArchivo.id_documento
                == document_id
            )
            .first()
        )

        return {
            "id_documento":
                documento.id_documento,

            "titulo":
                documento.titulo,

            "estado":
                documento.estado.value,

            "estado_validacion":
                extraccion.estado_validacion,

            "transcripcion":
                extraccion.json_resultado.get(
                    "texto_completo",
                    ""
                ),

            "datos_estructurados":
                extraccion.json_resultado.get(
                    "datos",
                    {}
                ),

            "procesamiento":
                extraccion.json_resultado.get(
                    "procesamiento",
                    {}
                ),

            "tiempo_procesamiento_ms":
                extraccion.tiempo_procesamiento_ms,

            "ruta_imagen":
                archivo.ruta_almacenamiento
                if archivo
                else None,

            "nombre_original":
                archivo.nombre_original
                if archivo
                else None
        }

    @staticmethod
    def flatten_dict(
        data: dict,
        parent_key: str = ""
    ):
        items = {}

        for key, value in data.items():

            new_key = (
                f"{parent_key}.{key}"
                if parent_key
                else key
            )

            if isinstance(value, dict):

                items.update(
                    DocumentService.flatten_dict(
                        value,
                        new_key
                    )
                )

            else:

                items[new_key] = value

        return items

    @staticmethod
    def validate_document(
        db: Session,
        document_id: int,
        datos_estructurados: dict,
        usuario_validador_id: int
    ):

        extraccion = (
            db.query(ExtraccionDocumento)
            .filter(
                ExtraccionDocumento.id_documento
                == document_id
            )
            .order_by(
                ExtraccionDocumento.id_extraccion.desc()
            )
            .first()
        )

        if not extraccion:

            raise HTTPException(
                status_code=404,
                detail="Extracción no encontrada"
            )

        datos_originales = (
            extraccion.json_resultado.get(
                "datos",
                {}
            )
        )

        campos_originales = (
            DocumentService.flatten_dict(
                datos_originales
            )
        )

        campos_corregidos = (
            DocumentService.flatten_dict(
                datos_estructurados
            )
        )

        nuevo_resultado = {
            **extraccion.json_resultado
        }

        nuevo_resultado[
            "datos"
        ] = datos_estructurados

        extraccion.json_resultado = nuevo_resultado

        extraccion.estado_validacion = (
            "VALIDADO"
        )

        documento = (
            db.query(Documento)
            .filter(
                Documento.id_documento
                == document_id
            )
            .first()
        )

        if documento:

            documento.id_usuario_valida = (
                usuario_validador_id
            )

            documento.fecha_validacion = (
                datetime.utcnow()
            )

            documento.estado = (
                EstadoDocumento.VALIDADO
            )

        for campo in set(
            list(campos_originales.keys()) +
            list(campos_corregidos.keys())
        ):

            detalle = ExtraccionDetalle(
                id_extraccion=
                    extraccion.id_extraccion,

                campo=campo,

                valor_extraido=str(
                    campos_originales.get(
                        campo,
                        ""
                    )
                ),

                valor_corregido=str(
                    campos_corregidos.get(
                        campo,
                        ""
                    )
                ),

                revisado=True
            )

            db.add(detalle)

        db.commit()

        db.refresh(extraccion)

        return {
            "message":
                "Documento validado correctamente",

            "estado_validacion":
                extraccion.estado_validacion,

            "texto":
                extraccion.json_resultado.get(
                    "texto_completo"
                )
        }

    @staticmethod
    def get_documents(
        db: Session,
        nombre: str | None = None,
        tipo: str | None = None,
        estado: str | None = None
    ):


        documentos = (
            db.query(
                Documento,
                ExtraccionDocumento
            )
            .join(
                ExtraccionDocumento,
                Documento.id_documento
                == ExtraccionDocumento.id_documento
            )
            .order_by(
                Documento.id_documento.desc()
            )
            .all()
        )

        resultado = []

        for documento, extraccion in documentos:

            datos = (
                extraccion.json_resultado
                .get(
                    "datos",
                    {}
                )
            )

            resultado.append(
                {
                    "id_documento":
                        documento.id_documento,

                    "titulo":
                        documento.titulo,

                    "estado":
                        documento.estado.value,

                    "estado_validacion":
                        extraccion.estado_validacion,

                    "tipo_documento":
                        datos.get(
                            "tipo_documento",
                            ""
                        ),

                    "nombre":
                        datos.get(
                            "paciente",
                            {}
                        ).get(
                            "nombre",
                            ""
                        )
                }
            )

        if nombre:

            resultado = [
                doc
                for doc in resultado
                if nombre.lower()
                in doc["nombre"].lower()
            ]

        if tipo:

            resultado = [
                doc
                for doc in resultado
                if tipo.lower()
                in doc["tipo_documento"].lower()
            ]

        if estado:

            resultado = [
                doc
                for doc in resultado
                if estado.lower()
                == doc["estado_validacion"].lower()
            ]

        return resultado

    @staticmethod
    def export_document_json(
        db: Session,
        document_id: int
    ):
        extraccion = (
            db.query(ExtraccionDocumento)
            .filter(
                ExtraccionDocumento.id_documento
                == document_id
            )
            .order_by(
                ExtraccionDocumento.id_extraccion.desc()
            )
            .first()
        )

        if not extraccion:
            raise HTTPException(
                status_code=404,
                detail="Extracción no encontrada"
            )

        return extraccion.json_resultado.get(
            "datos",
            {}
        )