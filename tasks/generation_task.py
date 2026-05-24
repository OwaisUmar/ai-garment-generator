import asyncio
from uuid import UUID

from db.session import SessionLocal
from exceptions.generation import RetryableGenerationError
from services.generation_service import GenerationService
from tasks.celery_app import celery_app

@celery_app.task(
    bind=True, 
    max_retries=1, 
    retry_backoff=True, 
    retry_jitter=True, 
    autoretry_for=(RetryableGenerationError,)
)
def process_generation(self, job_id: str):
    with SessionLocal() as db:
        service = GenerationService(db)
        service.process_job(UUID(job_id))