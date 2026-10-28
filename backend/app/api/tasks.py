from fastapi import APIRouter

from app.tasks.document_tasks import (
    test_task,
    process_document_task
)

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post("/test")
def enqueue_test_task():

    task = test_task.delay()

    return {
        "task_id": task.id,
        "message": "Task enviada a Redis"
    }


@router.post("/process/{document_id}")
def process_document(
    document_id: int
):

    task = process_document_task.delay(
        document_id
    )

    return {
        "task_id": task.id,
        "message": (
            f"Documento {document_id} "
            "enviado a procesamiento"
        )
    }