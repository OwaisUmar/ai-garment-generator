from datetime import datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4
import base64

from openai import APIConnectionError, APITimeoutError, RateLimitError

from exceptions.generation import ImageGenerationError, RetryableGenerationError


class Demo:

    def __init__(self) -> None:
        self.model = "gpt-image-1"

    def generate(
        self,
        prompt: str,
        garment_image_path: str | None = None,
        color_image_path: str | None = None,
        fabric_image_path: str | None = None,
        size: Literal["1024x1024", "1024x1536", "1536x1024"] = "1024x1024",
        quality: Literal["low", "medium", "high", "auto"] = "high",
    ) -> str:

        image_paths = [path for path in (
            garment_image_path,
            color_image_path,
            fabric_image_path
        ) if path]

        try:
            image_files = [open(path, 'rb') for path in image_paths]

        except (APIConnectionError, APITimeoutError, RateLimitError) as e:
            raise RetryableGenerationError(str(e)) from e
        
        try:    
            with open("static/demo/generated.png", "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
            
            if not image_base64:
                raise ImageGenerationError("No image returned from OpenAI.")

            image_bytes = base64.b64decode(image_base64)

        except Exception as e:

            raise ImageGenerationError(f"Failed to decode generated image: {e}") from e

        try:
            today = datetime.utcnow()
            target_dir = Path(f"static/outputs/{today.year}/{today.month:02d}/{today.day:02d}")
            target_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{uuid4()}.png"
            file_path = target_dir / filename

            with open(file_path, "wb") as f:
                f.write(image_bytes)

            return str(file_path)
        
        except Exception as e:

            raise ImageGenerationError(f"Failed to save generated image: {e}") from e