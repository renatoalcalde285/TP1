from io import BytesIO

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends,
    HTTPException
)

from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.models.usuario import Usuario

from app.models.documento_archivo import (
    DocumentoArchivo
)

from app.services.document_service import (
    DocumentService
)

from app.security.dependencies import (
    require_role
)

from app.tasks.document_tasks import (
    process_document_task
)

from app.schemas.document_validation import (
    DocumentValidationRequest
)

from app.core.storage import (
    s3_client,
    BUCKET_NAME
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload")
async def upload_document(
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_role(
            "REGISTRADOR"
        )
    )
):

    results = []

    for file in files:

        result = await DocumentService.upload_file(
            db=db,
            file=file,
            usuario_id=current_user.id_usuario
        )

        process_document_task.delay(
            result["id_documento"]
        )

        results.append(result)

    return results


@router.get("/{document_id}")
def get_document_status(
    document_id: int,
    db: Session = Depends(get_db)
):

    return DocumentService.get_document_status(
        db=db,
        document_id=document_id
    )


@router.get("/{document_id}/review")
def get_document_review(
    document_id: int,
    db: Session = Depends(get_db)
):

    return DocumentService.get_document_review(
        db=db,
        document_id=document_id
    )


@router.get("/{document_id}/image")
def get_document_image(
    document_id: int,
    db: Session = Depends(get_db)
):

    archivo = (
        db.query(DocumentoArchivo)
        .filter(
            DocumentoArchivo.id_documento
            == document_id
        )
        .first()
    )

    if not archivo:

        raise HTTPException(
            status_code=404,
            detail="Imagen no encontrada"
        )

    objeto = s3_client.get_object(
        Bucket=BUCKET_NAME,
        Key=archivo.ruta_almacenamiento
    )

    contenido = objeto["Body"].read()

    return StreamingResponse(
        BytesIO(contenido),
        media_type=archivo.formato
    )


@router.put("/{document_id}/validate")
def validate_document(
    document_id: int,
    payload: DocumentValidationRequest,
    db: Session = Depends(get_db)
):

    return DocumentService.validate_document(
        db=db,
        document_id=document_id,
        transcripcion=payload.transcripcion
    )


@router.get("")
def get_documents(
    nombre: str | None = None,
    tipo: str | None = None,
    estado: str | None = None,
    db: Session = Depends(get_db)
):

    return DocumentService.validate_document(
    db=db,
    document_id=document_id,
    datos_estructurados=
        payload.datos_estructurados
)