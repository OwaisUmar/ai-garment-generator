# storage/local_storage.py

from pathlib import Path
from uuid import uuid4
import aiofiles
from fastapi import UploadFile


class LocalStorage:
    def __init__(self, base_dir: str = 'static'):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, upload: UploadFile) -> str:
        """
        Save an uploaded file to disk and return the relative file path.

        Example return value:
            static/uploads/550e8400-e29b-41d4-a716-446655440000.png
        """
        # Preserve original extension
        extension = Path(upload.filename).suffix.lower()
        
        target_dir = self.base_dir / 'uploads'
        target_dir.mkdir(parents=True, exist_ok=True)
        
        file_name = f'{uuid4()}{extension}'
        file_path = target_dir / file_name
        
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await upload.read(65536):
                await f.write(chunk)
                
        return str(file_path)


    # async def save_bytes(
    #     self,
    #     data: bytes,
    #     suffix: str = '.bin',
    #     directory: str | None = None
    # ):
    #     """
    #     Save arbitrary bytes to disk and return the relative path.

    #     Example:
    #         static/generated/550e8400-e29b-41d4-a716-446655440000.png
    #     """
    #     target_dir = self.base_dir / directory if directory else self.base_dir
    #     target_dir.mkdir(parents=True, exist_ok=True)
        
    #     # Unique filename
    #     filename = f'{uuid4()}{suffix}'
    #     file_path = target_dir / filename
        
    #     # Write asynchronously
    #     async with aiofiles.open(file_path, 'wb') as f:
    #         await f.write(data)
            
    #     return str(file_path)