import os
from datetime import datetime

from fastapi import UploadFile

from config import media_dir


async def save_image(image_file: UploadFile) -> str:
    file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image_file.filename}"
    file_path = os.path.join(media_dir, file_name)
    async with open(file_path, "wb") as file:
        file.write(await image_file.read())
    return file_name
