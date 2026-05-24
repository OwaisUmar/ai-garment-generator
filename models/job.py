from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from db.session import Base


class InputType(Enum):
    IMAGE = 'image'
    TEXT = 'text'


class Status(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    

class ImageSize(str, Enum):
    SQUARE = "1024x1024"
    PORTRAIT = "1024x1536"
    LANDSCAPE = "1536x1024"


class ImageQuality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    AUTO = "auto"


class ImageModel(str, Enum):
    GPT_IMAGE_1 = "gpt-image-1"

class GenerationJob(Base):
    __tablename__ = 'generation_jobs'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    garment_input_type: Mapped[InputType]
    color_input_type: Mapped[InputType]
    fabric_input_type: Mapped[InputType]
    
    garment_value: Mapped[str] = mapped_column(nullable=False)
    color_value: Mapped[str] = mapped_column(nullable=False)
    fabric_value: Mapped[str] = mapped_column(nullable=False)
    
    output_image_path: Mapped[str | None]
    image_size: Mapped[ImageSize | None]
    image_quality: Mapped[ImageQuality | None]
    model_name: Mapped[str | None]
    
    satisfaction_rating: Mapped[int | None]
    comment: Mapped[str | None] = mapped_column(Text)
    rating_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    error_message: Mapped[str | None]
    
    status: Mapped[Status] = mapped_column(default=Status.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))    
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    