from datetime import datetime
from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.job import GenerationJob, InputType, Status
from schemas.feedback import FeedbackRequest
from schemas.generate import GenerateRequest
from storage.dependencies import get_storage
from storage.local_storage import LocalStorage
from tasks.generation_task import process_generation

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

@app.post('/generate')
async def generate(
    garment_text: str | None = Form(None),
    color_text: str | None = Form(None),
    fabric_text: str | None = Form(None),
    
    garment_image: UploadFile | None = File(None),
    color_image: UploadFile | None = File(None),
    fabric_image: UploadFile | None = File(None),
    
    storage: LocalStorage = Depends(get_storage),
    db: AsyncSession = Depends(get_db),
):
    try:
        # 1. Validate
        request = GenerateRequest(
            garment_text=garment_text,
            color_text=color_text,
            fabric_text=fabric_text,

            garment_filename=garment_image.filename if garment_image else None,
            color_filename=color_image.filename if color_image else None,
            fabric_filename=fabric_image.filename if fabric_image else None,
        )
        
        
        # 2. Specify input type and upload files (if available)
        garment_input_type = InputType.IMAGE if garment_image else InputType.TEXT
        color_input_type = InputType.IMAGE if color_image else InputType.TEXT
        fabric_input_type = InputType.IMAGE if fabric_image else InputType.TEXT
        
        garment_value = await storage.save_upload(garment_image) if garment_image else garment_text
        color_value = await storage.save_upload(color_image) if color_image else color_text
        fabric_value = await storage.save_upload(fabric_image) if fabric_image else fabric_text
        
        # 3. Create DB job
        job = GenerationJob(
            garment_input_type=garment_input_type,
            color_input_type=color_input_type,
            fabric_input_type=fabric_input_type,
            
            garment_value=garment_value,
            color_value=color_value,
            fabric_value=fabric_value,
        )
        
        # 4. Save to DB
        db.add(job)
        await db.commit()
        await db.refresh(job)
        
        # 5. Start background processing (Celery)
        process_generation.delay(str(job.id))
        
        # 6. Return immediately
        return {
            'message': 'Generation job created successfully.',
            'job_id': str(job.id),
            'status': job.status.value,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Database error while creating generation job.',
        )

    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unexpected error while creating generation job.',
        )

        
@app.get('/jobs/{job_id}')
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(GenerationJob).where(GenerationJob.id == job_id))

    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=404,
            detail='Job not found.',
        )
    resp = {
        'job_id': str(job.id),
        'status': job.status.value,
        'error_message': job.error_message,
    }
    
    if job.status.value == 'completed':
        resp['generation_details'] = {
        'garment_input': (
            'Image'
            if job.garment_input_type == InputType.IMAGE
            else f'Text - {job.garment_value}'
        ),

        'color': (
            'Image'
            if job.color_input_type == InputType.IMAGE
            else job.color_value
        ),

        'fabric_input': (
            'Image'
            if job.fabric_input_type == InputType.IMAGE
            else f'Text - {job.fabric_value}'
        ),
        
        'image_path': job.output_image_path,
        

        'image_size': (
            job.image_size.value.replace('x', ' × ')
            if job.image_size
            else None
        ),

        'quality': (
            job.image_quality.value.capitalize()
            if job.image_quality
            else None
        ),

        'generated_at': (
            job.completed_at.strftime('%d %b %Y, %H:%M:%S')
            if job.completed_at
            else None
        ),

        'model_name': job.model_name,
    }

    return resp


@app.post('/jobs/{job_id}/feedback')
async def submit_feedback(
    job_id: UUID,
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(GenerationJob).where(GenerationJob.id == job_id))

    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=404,
            detail='Generation job not found.',
        )

    if job.status != Status.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail='Feedback allowed only for completed jobs.',
        )

    job.satisfaction_rating = request.rating
    job.comment = request.comment
    job.rating_timestamp = datetime.utcnow()

    await db.commit()

    return {'message': 'Feedback submitted successfully.'}