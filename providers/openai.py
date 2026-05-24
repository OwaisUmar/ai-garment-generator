from datetime import datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4
import base64

from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
)

from config.settings import settings
from exceptions.generation import (
    ImageGenerationError,
    RetryableGenerationError,
)


class OpenAIProvider:

    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-image-1"

    def generate(
        self,
        prompt: str,
        garment_image_path: str | None = None,
        color_image_path: str | None = None,
        fabric_image_path: str | None = None,
        size: Literal[
            "1024x1024",
            "1024x1536",
            "1536x1024",
        ] = "1024x1024",
        quality: Literal[
            "low",
            "medium",
            "high",
            "auto",
        ] = "high",
    ) -> str:

        image_paths = [
            path
            for path in (
                garment_image_path,
                color_image_path,
                fabric_image_path,
            )
            if path
        ]

        try:

            image_files = [open(path, "rb") for path in image_paths]

            try:

                # Use image edit endpoint when references are provided
                if image_files:
                    response = self.client.images.edit(
                        model=self.model,
                        image=image_files,
                        prompt=prompt,
                        size=size,
                        quality=quality,
                    )

                # Otherwise use text-to-image generation
                else:
                    response = self.client.images.generate(
                        model=self.model,
                        prompt=prompt,
                        size=size,
                        quality=quality,
                    )

            finally:

                # Always close opened files
                for f in image_files:
                    f.close()

        except (
            APIConnectionError,
            APITimeoutError,
            RateLimitError,
        ) as e:

            raise RetryableGenerationError(str(e)) from e

        try:

            image_base64 = response.data[0].b64_json

            if not image_base64:
                raise ImageGenerationError("No image returned from OpenAI.")

            image_bytes = base64.b64decode(image_base64)

        except Exception as e:
            raise ImageGenerationError(f"Failed to decode generated image: {e}") from e

        try:
            today = datetime.utcnow()

            target_dir = Path(
                f"static/outputs/"
                f"{today.year}/"
                f"{today.month:02d}/"
                f"{today.day:02d}"
            )

            target_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            filename = f"{uuid4()}.png"

            file_path = target_dir / filename

            with open(file_path, "wb") as f:
                f.write(image_bytes)

            return str(file_path)

        except Exception as e:
            raise ImageGenerationError(f"Failed to save generated image: {e}") from e
