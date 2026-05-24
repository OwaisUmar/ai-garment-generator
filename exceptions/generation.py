class ImageGenerationError(Exception):
    """Base image generation error."""
    pass


class RetryableGenerationError(ImageGenerationError):
    """Transient/retryable AI provider failure."""
    pass