from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from db.session import SessionLocal
from exceptions.generation import RetryableGenerationError
from models.job import GenerationJob, ImageQuality, ImageSize, InputType, Status
from providers.openai import OpenAI
from providers.demo import Demo


class GenerationService:
    def __init__(self, db: Session):
        self.db = db
        # self.provider = OpenAI()
        self.provider = Demo() # using Demo for testing
        self.size = ImageSize.SQUARE
        self.quality = ImageQuality.HIGH
        
    def process_job(self, job_id: UUID):
        result = self.db.execute(select(GenerationJob).where(GenerationJob.id == job_id))
        job = result.scalar_one()
        
        try:
            # Mark as processing
            job.status = Status.PROCESSING
            job.started_at = datetime.utcnow()
            self.db.commit()
            
            prompt = self._build_prompt(job)
            
            garment_image_path=job.garment_value if job.garment_input_type == InputType.IMAGE else None
            color_image_path=job.color_value if job.color_input_type == InputType.IMAGE else None
            fabric_image_path=job.fabric_value if job.fabric_input_type == InputType.IMAGE else None
            
            # Generate image using AI provider
            output_image_path = self.provider.generate(
                prompt=prompt,
                garment_image_path=garment_image_path,
                color_image_path=color_image_path,
                fabric_image_path=fabric_image_path,
                size=self.size,
                quality=self.quality
            )
        
            job.output_image_path = output_image_path
            job.image_size = self.size
            job.image_quality = self.quality
            job.model_name = self.provider.model
            job.status = Status.COMPLETED
            job.completed_at = datetime.utcnow()
            job.error_message = None
            
            self.db.commit()
        except RetryableGenerationError:
            self.db.rollback()
            # Let celery retry
            raise    
        
        except Exception as e:
            self.db.rollback()
            
            job.status = Status.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            
            raise
        
        
    def _build_prompt(self, job: GenerationJob):
        parts = []

        if job.garment_input_type == InputType.TEXT:
            parts.append(f'Garment design: {job.garment_value}')

        if job.color_input_type == InputType.TEXT:
            parts.append(f'Primary color: {job.color_value}')

        if job.fabric_input_type == InputType.TEXT:
            parts.append(f'Fabric: {job.fabric_value}')

        parts.append(
            'Generate a high-resolution, photorealistic studio product image of the garment. '
            'Accurately preserve the provided design, colors, and fabric texture. '
            'Display the garment centered on a pure white background with professional lighting, '
            'natural shadows, and no models, props, text, or watermarks.'
        )

        return '. '.join(parts)