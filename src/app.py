from typing import Dict
from fastapi import FastAPI

app = FastAPI()


@app.get("/items/{item_id}")
async def get_item(item_id: int) -> Dict[str, int]:
    return {"item": item_id}
