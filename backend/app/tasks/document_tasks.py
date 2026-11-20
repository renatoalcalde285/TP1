import io
import time
from wsgiref import headers
import requests

from PIL import Image

from app.core.celery_app import celery_app
from app.core.database import SessionLocal

from app.core.settings import (
    QWEN_URL,
    QWEN_API_KEY
)

from app.core.storage import (
    s3_client,
    BUCKET_NAME
)

from app.models.documento import (
    Documento,
    EstadoDocumento
)

from app.models.documento_archivo import (
    DocumentoArchivo
)

from app.models.extraccion_documento import (
    ExtraccionDocumento
)

from app.services.image_processing import (
    preprocess_document
)

from app.models.extraccion_detalle import (
    ExtraccionDetalle
)


@celery_app.task
def test_task():

    print("✅ Celery funcionando correctamente")

    return {
        "status": "completed"
    }


@celery_app.task
def process_document_task(document_id: int):

    db = SessionLocal()

    documento = None

    try:

        documento = (
            db.query(Documento)
            .filter(
                Documento.id_documento == document_id
            )
            .first()
        )

        if not documento:

            print(
                f"Documento {document_id} no encontrado"
            )

            return

        documento.estado = (
            EstadoDocumento.PROCESANDO
        )

        db.commit()

        print(
            f"Procesando documento {document_id}"
        )

        archivo = (
            db.query(DocumentoArchivo)
            .filter(
                DocumentoArchivo.id_documento == document_id
            )
            .first()
        )

        if not archivo:

            raise Exception(
                "No existe archivo asociado al documento"
            )

        print(
            f"Descargando archivo: "
            f"{archivo.ruta_almacenamiento}"
        )

        objeto = s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key=archivo.ruta_almacenamiento
        )

        contenido = objeto["Body"].read()

        imagen = Image.open(
            io.BytesIO(contenido)
        ).convert("RGB")

        print(
            f"Imagen cargada correctamente: "
            f"{archivo.nombre_original}"
        )

        imagen_procesada = preprocess_document(
            imagen
        )

        print(
            "✅ Filtros aplicados correctamente"
        )

        # ==========================================
        # ENVIAR A QWEN
        # ==========================================

        buffer = io.BytesIO()

        imagen_procesada.save(
            buffer,
            format="JPEG"
        )

        buffer.seek(0)

        inicio = time.perf_counter()

        headers = {
         "X-API-Key": QWEN_API_KEY
        }
        respuesta = requests.post(
            f"{QWEN_URL}/ocr",
            files={
                "file": (
                    archivo.nombre_original,
                    buffer,
                    "image/jpeg"
                )
            },
            headers=headers,
            timeout=900
        )

        respuesta.raise_for_status()

        resultado = respuesta.json()

        print("RESPUESTA OCR")
        print(resultado)

        buffer.seek(0)

        respuesta_estructura = requests.post(
            f"{QWEN_URL}/extraer",
            files={
                "file": (
                    archivo.nombre_original,
                    buffer,
                    "image/jpeg"
                )
            },
            headers=headers,
            timeout=300
        )

        respuesta_estructura.raise_for_status()

        resultado_completo = respuesta_estructura.json()
        
        fin = time.perf_counter()

        tiempo_ms = int(
            resultado_completo["procesamiento"]["tiempo_total_s"]
            * 1000
        )

        print(
            "✅ Respuesta recibida desde Qwen"
        )

        extraccion = ExtraccionDocumento(
            id_documento=documento.id_documento,
            id_archivo=archivo.id_archivo,
            id_modelo=1,
            json_resultado=resultado_completo,
            estado_validacion="SIN_REVISAR",
            metrica_confianza=None,
            tiempo_procesamiento_ms=tiempo_ms
        )

        db.add(extraccion)

        documento.estado = (
            EstadoDocumento.PROCESADO
        )

        db.commit()
        db.refresh(extraccion)

        campos = flatten(
            resultado_completo["datos"]
        )

        for campo, valor in campos.items():

            detalle = ExtraccionDetalle(
                id_extraccion=extraccion.id_extraccion,
                campo=campo,
                valor_extraido=str(valor)
                    if valor is not None
                    else "",
                revisado=False
            )

            db.add(detalle)

        db.commit()


        print(
            f"Documento {document_id} "
            f"procesado correctamente"
        )

        return {
            "documento": document_id,
            "estado": "PROCESADO"
        }

    except Exception as e:

        print(
            f"ERROR procesando documento "
            f"{document_id}: {str(e)}"
        )

        if documento:

            documento.estado = (
                EstadoDocumento.ERROR
            )

            db.commit() 

        raise

    finally:

        db.close()


def flatten(data, parent=""):
    items = {}

    if isinstance(data, dict):
        for key, value in data.items():
            nuevo = (
                f"{parent}.{key}"
                if parent
                else key
            )

            items.update(
                flatten(value, nuevo)
            )

    elif isinstance(data, list):
        for i, value in enumerate(data):

            nuevo = (
                f"{parent}.{i}"
            )

            items.update(
                flatten(value, nuevo)
            )

    else:

        items[parent] = data

    return items