import os
from datetime import datetime

from fastapi import UploadFile

from config import media_dir


async def save_file(file: UploadFile) -> str:
    file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file_path = os.path.join(media_dir, file_name)
    with open(file_path, "wb") as a:
        a.write(await file.read())
    return file_name
