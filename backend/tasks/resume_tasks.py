import logging

from backend.core.celery_app import celery_app
from backend.services.resume_ingestion_service import ResumeIngestionService


logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="backend.tasks.resume_tasks.process_resume_task"
)
def process_resume_task(
    self,
    file_path: str,
    category: str = "uploaded",
    metadata_overrides: dict | None = None
):
    task_id = self.request.id

    logger.info(
        "Starting resume processing task task_id=%s file_path=%s category=%s",
        task_id,
        file_path,
        category
    )

    service = None

    try:
        service = ResumeIngestionService()

        candidate = service.process_resume(
            file_path=file_path,
            category=category,
            metadata_overrides=metadata_overrides
        )

        if candidate is None:
            raise RuntimeError(
                f"Resume processing returned no candidate for {file_path}"
            )

        logger.info(
            "Completed resume processing task task_id=%s candidate_id=%s file_name=%s",
            task_id,
            candidate.id,
            candidate.file_name
        )

        return {
            "status": "completed",
            "candidate_id": candidate.id,
            "file_name": candidate.file_name
        }

    except Exception:
        logger.exception(
            "Resume processing task failed task_id=%s file_path=%s",
            task_id,
            file_path
        )

        raise

    finally:
        if service is not None:
            service.close()


def process_resume_background(
    file_path: str,
    category: str = "uploaded",
    metadata_overrides: dict | None = None
):
    import uuid
    task_id = f"bg_{uuid.uuid4().hex[:8]}"

    logger.info(
        "Starting background resume processing task task_id=%s file_path=%s category=%s",
        task_id,
        file_path,
        category,
    )

    service = None

    try:
        service = ResumeIngestionService()

        candidate = service.process_resume(
            file_path=file_path,
            category=category,
            metadata_overrides=metadata_overrides,
        )

        if candidate is None:
            raise RuntimeError(
                f"Resume processing returned no candidate for {file_path}"
            )

        logger.info(
            "Completed background resume processing task task_id=%s candidate_id=%s file_name=%s",
            task_id,
            candidate.id,
            candidate.file_name,
        )

        return {
            "status": "completed",
            "candidate_id": candidate.id,
            "file_name": candidate.file_name,
        }

    except Exception:
        logger.exception(
            "Background resume processing task failed task_id=%s file_path=%s",
            task_id,
            file_path,
        )
        raise

    finally:
        if service is not None:
            service.close()

