from app.core.celery_app import celery_app

from app.core.database import SessionLocal

from app.models.documento import (
    Documento,
    EstadoDocumento
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

    try:

        documento = (
            db.query(Documento)
            .filter(
                Documento.id_documento == document_id
            )
            .first()
        )

        if not documento:
            return

        documento.estado = (
            EstadoDocumento.PROCESANDO
        )

        db.commit()

        # Aquí irán:
        # Lanczos
        # Bilateral
        # CLAHE
        # Sharp
        # Qwen

        documento.estado = (
            EstadoDocumento.PROCESADO
        )

        db.commit()

    except Exception:

        if documento:

            documento.estado = (
                EstadoDocumento.ERROR
            )

            db.commit()

        raise

    finally:

        db.close()