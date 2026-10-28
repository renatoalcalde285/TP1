from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Depends
)

from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.models.usuario import Usuario

from app.services.document_service import (
    DocumentService
)

from app.security.dependencies import (
    require_role
)

from app.tasks.document_tasks import (
    process_document_task
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